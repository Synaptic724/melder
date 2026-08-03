"""
The mediator plane root - the object Aether holds.

Dependency rule (epic constraint 4, the one that matters): standard library
plus `melder.utilities` ONLY. This module must never import `melder.aether`.
Aether knows about the plane; the plane knows nothing about Aether. That is
what lets it be constructed before any frame can exist and tested in isolation.

Collapses the roles DevOps splits across `ChangeControlManager` (owning root)
and `TransactionMediator` (front door) into one class, because the DevOps root
carries frame-specific duties - dirty roots, revalidation, risk - that have no
counterpart here. Splitting them would produce a root whose only job is to
forward.
"""

import threading
import time
import uuid
from typing import Any, Dict, Mapping, Optional, Tuple

from melder.aether.aetheric_mediator.admission_orchestrator import (
    AdmissionOrchestrator,
)
from melder.aether.aetheric_mediator.admission_result import (
    AdmissionReason,
    AdmissionResult,
)
from melder.aether.aetheric_mediator.claim_table import ClaimTable
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.information_registry import (
    InformationRegistry,
)
from melder.aether.aetheric_mediator.staged_transaction import StagedTransaction
from melder.aether.aetheric_mediator.strategy_builder import StrategyBuilder
from melder.aether.aetheric_mediator.transaction_request import TransactionRequest
from melder.aether.aetheric_mediator.transaction_session import (
    OutcomePolicy,
    SessionStatus,
    TransactionSession,
)
from melder.aether.aetheric_mediator.transaction_type import TransactionType
from melder.utilities.general_base.cleanable import Cleanable


class Mediator(Cleanable):
    """
    The plane root: admission, sessions, strategies, and reporting.

    Purpose:
        Be the single front door through which every top-level structural
        transaction passes, so isolation, outcome policy, and reporting have
        one implementation rather than one per subsystem.

    Contract:
        - SESSIONS ARE PER IDENTITY, PER THREAD. A thread re-entering with the
          SAME identity JOINS its existing session (depth increments) rather
          than opening a second root. A DIFFERENT identity on the same thread
          opens its own root session. This mirrors DevOps exactly and is what
          makes nested work by one actor safe without deadlocking it against
          itself.
        - ADMISSION IS BOUNDED, AND WAITING NEVER HOLDS THE ADMISSION LOCK.
          `begin` retries against the orchestrator, parking on the claim
          table's own condition between attempts. Holding the admission lock
          while parked would block every unrelated admission behind one
          contended request.
        - ONE KNOB. `max_wait_seconds` is the entire admission policy surface,
          matching DevOps after `queue_competing_root_transactions` was
          removed. Resist adding a second.
        - AN UNREGISTERED TRANSACTION TYPE REFUSES. There is no default
          strategy and therefore no guessed claim set.
        - READERS NEVER ENTER THIS PLANE. Nothing on a read path calls
          `begin`. The plane exists for structural mutation only.
        - CLAIMS ARE RELEASED ON EVERY TERMINAL PATH, including when the
          outcome policy is LEAVE_BROKEN. Leaving the WORLD broken is a
          deliberate product decision; leaving the CLAIM TABLE broken would
          just be a leak that wedges the plane forever. The two are not the
          same thing and must not be conflated.

    Owned State:
        The claim table, admission orchestrator, information registry, and
        strategy builder - all constructed here and cleaned here, in reverse
        dependency order. Plus thread-local session bookkeeping.

    Lifecycle / Cleanup:
        Idempotent. Children are cleaned in reverse order of construction so
        nothing is torn down while something that borrows it is still live.
        The claim table is cleaned LAST because its cleanup is what wakes any
        thread still parked in `wait_for_change`.

    Threading:
        The plane is designed for free-threaded 3.14t. Foreign code -
        strategy hooks and rollback actions - is never invoked while holding
        a plane lock.

    Registration:
        MELDER KERNEL - guarded. Constructed and held by Aether; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Top-level transaction plane root. Admission, per
        identity sessions, strategy dispatch, outcome policy, and reporting.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_claim_table",
        "_orchestrator",
        "_information_registry",
        "_strategy_builder",
        "_max_wait_seconds",
        "_thread_local",
        "_sessions_by_request_id",
        "_participants",
    ]

    # Longest single park in the admission retry loop, and therefore the worst
    # case for a release notification missed in the window between a refused
    # admission and the park that follows it. A CLASS attribute, not a module
    # constant, per the repo's module-scope rule. Matched to the DevOps plane's
    # one-second slice; see `_admit_with_wait` for why the window exists at all
    # and cannot be closed by restructuring this loop.
    _WAIT_SLICE_SECONDS: float = 1.0

    def __init__(self, *, max_wait_seconds: float = 30.0) -> None:
        """
        Build one plane root with its owned children.

        Args:
            max_wait_seconds:
                How long `begin` waits for contended scopes before refusing.
                The single admission policy knob.

        Returns:
            None.

        Raises:
            ValueError: If `max_wait_seconds` is negative.
        """
        super().__init__()
        if max_wait_seconds < 0:
            raise ValueError(
                "max_wait_seconds must be non-negative; got {0!r}.".format(
                    max_wait_seconds
                )
            )
        self._lock: threading.RLock = threading.RLock()
        self._claim_table: ClaimTable = ClaimTable()
        self._orchestrator: AdmissionOrchestrator = AdmissionOrchestrator()
        self._information_registry: InformationRegistry = InformationRegistry()
        self._strategy_builder: StrategyBuilder = StrategyBuilder()
        self._max_wait_seconds: float = max_wait_seconds
        self._thread_local: threading.local = threading.local()
        self._sessions_by_request_id: Dict[str, TransactionSession] = {}
        self._participants: Dict[str, float] = {}

    def cleanup(self) -> None:
        """
        Idempotently tear down the plane and its children.

        Contract:
            Children are cleaned in REVERSE dependency order, with two rules
            that are load-bearing rather than stylistic:

            BORROWERS BEFORE OWNERS. `AdmissionOrchestrator._in_flight` and
            `InformationRegistry._active` BORROW the `TransactionRequest` and
            `StagedTransaction` records that the SESSIONS own and clean.
            Tearing the sessions down first would leave both borrowers holding
            cleaned records, so a concurrent `describe()` landing mid-teardown
            would raise from inside reporting instead of reporting an empty
            plane. Dropping the borrowed references first makes that window
            impossible rather than unlikely.

            THE CLAIM TABLE IS LAST, because its cleanup is what wakes any
            thread still parked in `wait_for_change`. Cleaning it first would
            leave waiters parked against a half-dead plane.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            # Re-check under the lock; the outer check is a fast path only.
            # Critical here specifically: without it two concurrent cleanups
            # would BOTH tear down the owned children, so the loser would
            # call cleanup() on already-deleted slots AND could double-clean
            # sessions it did not own.
            if self._cleaned:
                return
            self._cleaned = True
            sessions = list(self._sessions_by_request_id.values())
            self._sessions_by_request_id.clear()
            # Names and floats only - nothing here owns a subsystem, so this
            # is a clear, not a teardown cascade.
            self._participants.clear()
        # Borrowers first - see the contract above.
        self._strategy_builder.cleanup()
        self._information_registry.cleanup()
        self._orchestrator.cleanup()
        # Then the owners: each session cleans the request and staged records
        # it owns.
        for session in sessions:
            if not session.cleaned:
                session.cleanup()
        # Then the table, so anything still parked wakes against a plane that
        # has finished dying rather than one mid-teardown.
        self._claim_table.cleanup()
        del self._sessions_by_request_id
        del self._participants
        del self._thread_local
        del self._max_wait_seconds
        del self._strategy_builder
        del self._information_registry
        del self._orchestrator
        del self._claim_table
        del self._lock

    def register_participant(self, participant: str) -> bool:
        """
        Record that one subsystem exists and may submit transactions.

        Purpose:
            Let the plane answer "which subsystems are live" without ever
            importing, referencing, or reaching into any of them.

        Contract:
            - THE SUBSYSTEM ANNOUNCES ITSELF; THE PLANE NEVER REACHES OUT.
              This direction is what keeps epic constraint 4 intact. Aether
              pushes this plane into Crystallizer, MutationResearch, and Nexus
              from above, and each announces itself here on activation. If the
              plane instead had to discover them, it would need to import
              `melder.aether` and the whole isolation property collapses.
            - A NAME IS ALL THAT IS STORED. No handle, no reference, no
              callback - just the participant's stable name and when it
              announced. The plane holds nothing it could accidentally keep
              alive, and there is nothing here to clean up beyond a dict of
              strings.
            - IDEMPOTENT. Re-announcing refreshes the timestamp and returns
              False, so an activate/deactivate/activate cycle is safe and a
              subsystem never needs to check first.
            - THIS IS NOT ADMISSION. Registering grants no claim and gates
              nothing. It is a roster, not a permission.

        Args:
            participant:
                Stable lowercase subsystem name, matching the name used to
                build its `ScopeKey.subsystem(...)` key.

        Returns:
            bool: True on first registration, False when already present.

        Raises:
            RuntimeError: If the plane has been cleaned.
            ValueError: If `participant` is empty or whitespace-only.
        """
        self.check_cleaned()
        if not participant or not participant.strip():
            raise ValueError(
                "register_participant requires a non-empty subsystem name; it "
                "must match the name used for ScopeKey.subsystem(...)."
            )
        with self._lock:
            first = participant not in self._participants
            self._participants[participant] = time.time()
            return first

    def unregister_participant(self, participant: str) -> bool:
        """
        Record that one subsystem is no longer live.

        Contract:
            Idempotent: unregistering an absent participant returns False, so
            a teardown path may call this unconditionally. Does NOT release
            any claims that subsystem holds - claims belong to transactions
            and are released by finalising those, never by roster changes.

        Args:
            participant: The subsystem name to drop.

        Returns:
            bool: True when a live participant was removed.

        Raises:
            RuntimeError: If the plane has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._participants.pop(participant, None) is not None

    def has_participant(self, participant: str) -> bool:
        """
        Report whether one subsystem has announced itself.

        Args:
            participant: The subsystem name to test.

        Returns:
            bool: True when the subsystem is registered.

        Raises:
            RuntimeError: If the plane has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return participant in self._participants

    def participants(self) -> Tuple[str, ...]:
        """
        Return every registered subsystem name, sorted.

        Returns:
            Tuple[str, ...]: Sorted participant names, empty when none.

        Raises:
            RuntimeError: If the plane has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(sorted(self._participants))

    @property
    def strategies(self) -> StrategyBuilder:
        """
        Return the strategy registry, for subsystems to register into.

        Returns:
            StrategyBuilder: The owned registry.
        """
        self.check_cleaned()
        return self._strategy_builder

    @property
    def reporting(self) -> InformationRegistry:
        """
        Return the information registry, for callers asking what is happening.

        Returns:
            InformationRegistry: The owned registry.
        """
        self.check_cleaned()
        return self._information_registry

    def begin(
            self,
            *,
            transaction_type: TransactionType,
            submitter: Identity,
            metadata: Optional[Mapping[str, Any]] = None,
            outcome_policy: OutcomePolicy = OutcomePolicy.UNWIND,
    ) -> TransactionSession:
        """
        Open or join a transaction session for one structural operation.

        Contract:
            Same identity on the same thread JOINS the live session. Otherwise
            resolves the strategy, computes the claim plan, admits with
            bounded waiting, and opens a root session with claims held.

        Args:
            transaction_type: The vocabulary member being performed.
            submitter: The claiming identity.
            metadata: Strategy inputs.
            outcome_policy: What happens to the world if this fails.

        Returns:
            TransactionSession: A joined or newly opened session.

        Raises:
            RuntimeError: If the plane is cleaned, or admission is refused.
                The refusal message carries the blocking evidence.
            KeyError: If no strategy is registered for `transaction_type`.
        """
        self.check_cleaned()
        existing = self._current_session(submitter)
        if existing is not None:
            existing.join()
            return existing
        strategy = self._strategy_builder.resolve(transaction_type)
        # ONE defensive copy, used for both the planning call and the record.
        # This previously built two independent dicts from the same input,
        # which cost an extra allocation per transaction and - more subtly -
        # meant the strategy planned against a DIFFERENT object than the one
        # the frozen request went on to carry. `TransactionRequest.build`
        # freezes this into the deeply immutable mapping that the request and
        # its staged record then SHARE, so one transaction owns exactly one
        # metadata structure from here to teardown.
        supplied = dict(metadata or {})
        claims = strategy.build_start_plan(
            submitter=submitter,
            metadata=supplied,
        )
        request = TransactionRequest.build(
            request_id=uuid.uuid4().hex,
            transaction_type=transaction_type,
            submitter=submitter,
            scope_claims=claims,
            metadata=supplied,
        )
        verdict = self._admit_with_wait(request=request, holder=submitter)
        if not verdict.admitted:
            # Render the refusal, THEN release the verdict. The message is the
            # last thing anybody needs from it, and the exception carries a
            # string rather than the object by design.
            refusal = "transaction {0} was refused: {1}".format(
                request.describe(), verdict.describe()
            )
            verdict.cleanup()
            raise RuntimeError(refusal)
        # Admitted. The verdict carried one bit, it has been read, and nothing
        # downstream takes a reference to it.
        verdict.cleanup()
        staged = StagedTransaction.from_request(
            request=request, admitted_at=time.time()
        )
        # Held as a PLAIN STRING for the rest of this method. The session is
        # about to take ownership of `request`, and the failure path below
        # cleans it - so every later use of the id must not depend on the
        # record still being readable.
        request_id = request.request_id
        session = TransactionSession(
            request=request,
            staged=staged,
            holder=submitter,
            outcome_policy=outcome_policy,
        )
        with self._lock:
            self._sessions_by_request_id[request_id] = session
        self._remember_session(submitter, session)
        try:
            self._information_registry.register_activity(staged)
            strategy.on_start(submitter=submitter, staged=staged)
        except BaseException:
            # POST-ADMISSION FAILURE MUST NOT WEDGE THE SCOPE. Claims are
            # already held at this point, so a raising `on_start` would
            # otherwise leave them held forever by a session no caller ever
            # received and therefore can never finalise. Release everything
            # and re-raise the original cause.
            #
            # ORDER REVERSED, and the reversal is required rather than
            # cosmetic. `_finalize` FIRST, `session.cleanup()` SECOND.
            #
            # The session owns the request and staged records and now CLEANS
            # them, while `_finalize` still has to drop the borrowed
            # references the orchestrator and the information registry are
            # holding. Cleaning first would leave both borrowers pointing at
            # cleaned records for the window between the two calls, and
            # `register_activity` may well have succeeded before `on_start`
            # raised - so a concurrent `reporting.describe()` would raise from
            # inside reporting. Finalising first drops the borrows while the
            # records are still whole.
            #
            # The previous order relied on the `cleaned` guard in `_finalize`
            # to skip a discard on a session still nominally OPEN. That guard
            # is now an explicit status check, so this ordering no longer has
            # to encode a second meaning.
            #
            # FULL cleanup here, not the discard `_finalize` performs. This
            # session never escaped: `begin` raises instead of returning it,
            # so no caller can hold a handle and none can ever inspect its
            # outcome. Nothing is owed to anybody, and this thread is the last
            # one that will ever see the object - so it frees it now rather
            # than leaving it to a later collector pass.
            try:
                # A FAILED `on_start` STILL OWES ITS `on_end`. DevOps routes
                # exactly this case through `end_transaction_by_request_id(
                # success=False)` so `_finalize_root_session`'s finally fires
                # the end hook - because a strategy that froze a runtime gate
                # part-way through `on_start` has no other path to its reopen.
                # This plane previously had no dispatch here at all, so that
                # freeze leaked and the only symptom would be a gate nobody
                # could reopen.
                #
                # The session is NOT failed first: `on_start` never receives
                # the session, so no inverses can have been registered, and
                # unwinding an empty set to reach a status nothing will
                # observe - the object is cleaned two lines later - is
                # ceremony rather than truth.
                strategy.on_end(submitter=submitter, staged=staged)
            finally:
                self._finalize(
                    request_id=request_id, holder=submitter, session=session
                )
                session.cleanup()
            raise
        return session

    def commit(self, session: TransactionSession) -> None:
        """
        Commit one session, stamping reporting and releasing its claims.

        Contract:
            THE PIPELINE, ported from `TransactionMediator._finalize_root_
            session` rather than re-derived:

                COMMITTING -> apply_commit_delta -> COMMITTED
                             -> on failure: fail(...) per outcome policy
                on_end (always, exactly once)
                _finalize (always, even if on_end raises)

            `apply_commit_delta` runs BEFORE the claims are released, so the
            freshness stamp it writes is race-free against overlapping
            writers. Releasing first would open a window where another
            transaction could mutate the region between the stamp and the
            release.

            A FAILED COMMIT UNWINDS. If the delta raises, the session is
            FAILED through its own outcome policy - inverses run under
            `UNWIND`, or the residue is recorded under `LEAVE_BROKEN` - and
            the original exception is re-raised. The previous shape marked the
            session COMMITTED up front and let finalisation DISCARD the
            inverses without running them, so a transaction that died inside
            its commit left the world half-mutated with its rollback thrown
            away and no ledger. That was neither of the two outcomes this
            plane offers.

            `on_end` FIRES EXACTLY ONCE, ON EVERY PATH, from the outer
            `finally`. This is the reliability law DevOps records explicitly:
            a strategy that froze a runtime gate in `on_start` is guaranteed
            its reopen. Dispatching it inside the success path - as this
            method did - means a raising delta silently skips it and the
            freeze leaks. If `on_end` itself raises while another exception is
            in flight, it chains over it with the original preserved as
            context; a gate left closed must never be silent.

            `_finalize` RUNS EVEN IF `on_end` RAISES. A failing end hook must
            still release the in-flight registration and the claims, or the
            plane holds scopes for a transaction nobody will ever finalise.

        Args:
            session: The session to commit. Must be at join depth zero.

        Returns:
            None.

        Raises:
            RuntimeError: If the plane is cleaned, or the session is not
                finalisable.
            BaseException: Whatever the commit delta or the end hook raised,
                after the session has been failed and the claims released.
        """
        self.check_cleaned()
        if session.depth > 0:
            raise RuntimeError(
                "cannot commit a session at join depth {0}; inner scopes must "
                "leave first.".format(session.depth)
            )
        holder = session.holder
        # The staged record was built ONCE at admission and lives on the
        # session. Rebuilding it here allocated a fresh deep copy of the
        # metadata on every commit AND restamped `admitted_at` with the commit
        # time, which made the field lie.
        staged = session.staged
        # Plain string, for the same lifetime reason as in `begin`: the
        # session owns and cleans these records, so finalisation must not
        # depend on one still being readable. The staged record carries both
        # values, so reading `session.request` here would only add a second
        # record to keep alive for no additional information.
        request_id = staged.request_id
        strategy = self._strategy_builder.resolve(staged.transaction_type)
        # COMMITTING first, so a pipeline that dies mid-flight is observably
        # mid-flight rather than observably successful.
        session.mark_committing()
        try:
            try:
                strategy.apply_commit_delta(
                    information_registry=self._information_registry,
                    submitter=holder,
                    staged=staged,
                )
            except BaseException as error:
                # THE TRANSACTION FAILS THROUGH ITS OWN POLICY. Under UNWIND
                # the inverses actually run; under LEAVE_BROKEN the residue is
                # recorded on the session. Either way the session reaches a
                # truthful terminal state before `_finalize` discards the
                # inverses - which is what makes the discard safe rather than
                # destructive.
                #
                # `fail` is given the cause because a bare "commit failed"
                # reason strands whoever reads the session afterwards.
                session.fail(
                    "commit pipeline failed: {0}: {1}".format(
                        type(error).__name__, error
                    )
                )
                raise
            else:
                session.mark_committed()
        finally:
            try:
                # EXACTLY ONCE, ON EVERY PATH - see the contract. This is
                # outside the success branch on purpose.
                strategy.on_end(submitter=holder, staged=staged)
            finally:
                self._finalize(
                    request_id=request_id, holder=holder, session=session
                )

    def fail(
            self,
            session: TransactionSession,
            reason: str,
    ) -> Tuple[SessionStatus, Tuple[str, ...]]:
        """
        Terminate one session per its outcome policy, releasing its claims.

        Contract:
            CLAIMS ARE RELEASED EVEN UNDER `LEAVE_BROKEN`. Leaving the world
            broken is the product decision; holding the claims forever would
            wedge the plane, which is a different and purely harmful failure.

            `on_end` FIRES EXACTLY ONCE and `_finalize` runs even if it
            raises - the same law `commit` states at length. Both terminal
            entrypoints owe a strategy its end hook, or a gate frozen in
            `on_start` leaks depending on which way the transaction happened
            to end.

            UNDER `LEAVE_BROKEN` THE RESIDUE IS ALSO RETAINED on the session
            and readable through `leave_broken_residue` / `describe()`, not
            only returned here. Finalisation discards the inverses moments
            later, so a caller that ignores this return value would otherwise
            have no record of what was left in the world.

        Args:
            session: The session to terminate.
            reason: Why the transaction failed.

        Returns:
            Tuple[SessionStatus, Tuple[str, ...]]:
                Terminal status, and either unwind failures (UNWIND) or the
                residue left in place (LEAVE_BROKEN).

        Raises:
            RuntimeError: If the plane has been cleaned.
        """
        self.check_cleaned()
        holder = session.holder
        staged = session.staged
        # Plain string; see `commit` for why finalisation never holds the
        # record itself.
        request_id = staged.request_id
        status, records = session.fail(reason)
        strategy = self._strategy_builder.resolve(staged.transaction_type)
        try:
            strategy.on_end(submitter=holder, staged=staged)
        finally:
            # Same guarantee as commit: the failure path must release claims
            # even when the family's own end hook also fails. A transaction
            # that failed twice is still a transaction whose scopes must be
            # freed.
            self._finalize(
                request_id=request_id, holder=holder, session=session
            )
        return status, records

    def get_session_for_identity(
            self,
            submitter: Identity,
    ) -> Optional[TransactionSession]:
        """
        Return the OPEN session this identity holds on the calling thread.

        Purpose:
            Let a participant that did not open the transaction discover whether
            it is already inside one, without opening a second root by calling
            `begin` speculatively.

        Contract:
            - Reads the CALLING THREAD's session map. Sessions are per identity
              PER THREAD, so this deliberately cannot see a session the same
              identity holds on another thread - reporting one would invite a
              caller to act on a session it may not touch.
            - Returns None when there is no session, when the session has been
              cleaned, or when it is no longer OPEN. A terminal session is not
              an active one and handing it back would read as "you are still in
              a transaction".
            - Read-only. Does not join, does not extend, does not mutate depth.

        Args:
            submitter:
                The identity whose session is being looked up.

        Returns:
            Optional[TransactionSession]: The open session, or None.

        Raises:
            RuntimeError: If the plane has been cleaned.
        """
        self.check_cleaned()
        return self._current_session(submitter)

    def has_any_active_session(self) -> bool:
        """
        Report whether the CALLING THREAD is inside any plane session at all.

        Purpose:
            Let a low-level seam that many callers reach - `Aether._ensure_frame`
            is the one this was built for - decide whether it needs to open a
            transaction of its own, without knowing WHICH identity is above it.

        WHY THIS IS IDENTITY-AGNOSTIC AND `has_active_session` IS NOT:
            The question being asked is different. `has_active_session(who)` asks
            "does THIS actor hold a session", which is what a caller managing its
            own transaction needs. This asks "is this thread already inside
            SOMEBODY's transaction", which is what a shared seam needs in order
            not to open a nested root underneath a caller it cannot see.

            That distinction is load-bearing rather than stylistic. The
            crystallizer restore engine calls `_ensure_frame` mid-replay while
            its load holds `world` EXCLUSIVE. If the frame seam opened a
            `FRAME_CREATE` root under its own identity, that root would request
            `frame:<name>` and block on a claim its OWN CALLER is holding - a
            self-deadlock, not a refusal, because the holder is never coming back
            to release it. Asking per-identity cannot detect this: the identities
            genuinely differ.

        Contract:
            - Reads the CALLING THREAD's session map only, like every other
              per-thread lookup here. A session held by this identity on another
              thread is correctly invisible.
            - Counts a session in ANY status the thread-local map still holds; a
              terminal session is removed by `_forget_session` at finalisation,
              so a live hit means a transaction genuinely has not ended.
            - Read-only. Opens nothing, joins nothing, mutates no depth.

        Returns:
            bool: True when at least one session is open on the calling thread.

        Raises:
            RuntimeError: If the plane has been cleaned.
        """
        self.check_cleaned()
        sessions = getattr(self._thread_local, "sessions", None)
        if not sessions:
            return False
        for session in sessions.values():
            if session is None or session.cleaned:
                continue
            if session.status is SessionStatus.OPEN:
                return True
        return False

    def has_active_session(self, submitter: Identity) -> bool:
        """
        Report whether this identity holds an OPEN session on this thread.

        Contract:
            Exactly `get_session_for_identity(...) is not None`, offered
            separately because the boolean question is the common one and a
            caller asking it should not have to hold a session reference to get
            an answer.

        Args:
            submitter:
                The identity being asked about.

        Returns:
            bool: True when an open session exists on the calling thread.

        Raises:
            RuntimeError: If the plane has been cleaned.
        """
        return self.get_session_for_identity(submitter) is not None

    def get_active_request(
            self,
            submitter: Identity,
    ) -> Optional[TransactionRequest]:
        """
        Return the frozen request behind this identity's open session.

        Contract:
            - None when there is no open session on the calling thread.
            - The request is the PRE-ADMISSION record, frozen before admission
              and owned by the session. Callers read it; they must not clean it,
              because `TransactionSession.cleanup` owns that.

        Args:
            submitter:
                The identity whose in-flight request is wanted.

        Returns:
            Optional[TransactionRequest]: The frozen request, or None.

        Raises:
            RuntimeError: If the plane has been cleaned.
        """
        session = self.get_session_for_identity(submitter)
        if session is None:
            return None
        return session.request

    def get_session_by_request_id(
            self,
            request_id: str,
    ) -> Optional[TransactionSession]:
        """
        Return the live session for one request id, from any thread.

        Purpose:
            Answer "who is holding these claims" when all the caller has is an
            id out of admission evidence - which is exactly what a refused
            transaction gets back.

        Contract:
            - CROSS-THREAD by design, unlike `get_session_for_identity`. A
              blocked caller needs to identify the holder, and the holder is on
              another thread by definition.
            - Returns None for an unknown id and for a session already cleaned.
              A finalised transaction is removed from this map by `_finalize`,
              so a live hit means the transaction genuinely has not ended.
            - READ-ONLY BY INTENT. The returned session belongs to its owning
              thread; a caller that ends or commits someone else's session
              through this handle is doing something the session's own
              one-root-owner rule exists to prevent, and the session will
              refuse a foreign-thread join for that reason.

        Args:
            request_id:
                The request id to look up.

        Returns:
            Optional[TransactionSession]: The live session, or None.

        Raises:
            RuntimeError: If the plane has been cleaned.
            ValueError: If `request_id` is not a non-empty string.
        """
        self.check_cleaned()
        if not isinstance(request_id, str) or not request_id:
            raise ValueError("request_id must be a non-empty string.")
        with self._lock:
            session = self._sessions_by_request_id.get(request_id)
        if session is None or session.cleaned:
            return None
        return session

    def mark_active_session_abort_only(
            self,
            *,
            submitter: Identity,
            reason: str,
    ) -> None:
        """
        Poison this identity's open session so its root can only roll back.

        Purpose:
            Mirror the DevOps plane's abort-only verb: let a caller that detects
            a failure it wants to survive to finalisation record it, instead of
            raising through every intervening frame and losing the chance to
            unwind deliberately.

        Contract:
            - Targets the OPEN session for `submitter` on the CALLING THREAD;
              raises when there is none, because silently doing nothing would
              let a caller believe it had poisoned a transaction it had not.
            - Delegates to `TransactionSession.mark_abort_only`, which is sticky
              and first-writer-wins - the first detected failure is the reason
              that survives.
            - Does NOT end the session, run inverses, or change its status. The
              session stays OPEN and joinable so inner scopes leave cleanly; the
              bar applies at `commit`.

        Args:
            submitter:
                The identity holding the session.
            reason:
                Human-readable justification, recorded on the session.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the plane is cleaned, or no open session exists for this
                identity on the calling thread.
            ValueError:
                If `reason` is not a non-empty string.
        """
        self.check_cleaned()
        session = self._current_session(submitter)
        if session is None:
            raise RuntimeError(
                "no open session for identity {0!r} on this thread; there is "
                "nothing to mark abort-only.".format(submitter.identity_key())
            )
        session.mark_abort_only(reason)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached snapshot of the whole plane.

        Returns:
            Dict[str, object]: Claims, admission, reporting, and strategy
                coverage - everything needed to answer "what is happening".

        Raises:
            RuntimeError: If the plane has been cleaned.
        """
        self.check_cleaned()
        return {
            "max_wait_seconds": self._max_wait_seconds,
            "claims": self._claim_table.describe(),
            "admission": self._orchestrator.describe(),
            "reporting": self._information_registry.describe(),
            "strategies": self._strategy_builder.describe(),
            "participants": self.participants(),
        }

    def _admit_with_wait(
            self,
            *,
            request: TransactionRequest,
            holder: Identity,
    ) -> AdmissionResult:
        """
        Admit with bounded retry, parking on the table between attempts.

        Contract:
            The admission lock is NOT held while waiting - the orchestrator
            releases it on every refused attempt and this loop parks on the
            claim table's condition instead.

            THE CHECK AND THE WAIT ARE TWO SEPARATE ACQUISITIONS, and that is
            forced rather than sloppy. Admission runs THROUGH the orchestrator,
            which owns its own lock, the in-flight registry, and the identity
            check. Holding the table's condition across that call would nest
            the table lock under the admission lock in the opposite order from
            `admit`, which is the AB-BA this design exists to avoid. So the
            window between "refused" and "parked" is real and cannot be closed
            here. `ClaimTable.acquire` closes it by doing check-and-wait under
            one acquisition, but it can only do that because it bypasses
            admission entirely - which would lose the in-flight registry, the
            identity check, and any admission policy.

            SLICED WAITING IS THE ANSWER, taken from the working DevOps plane
            (`TransactionMediator._admit_with_scope_wait`). A release
            notification landing inside that window is MISSED, because this
            thread is not parked yet and nothing notifies again until the next
            release. Waiting the full remaining time would leave a transaction
            asleep for up to `max_wait_seconds` with its scope already free.
            Capping each park at one second bounds that worst case to one
            second per retry, at the cost of an extra wakeup per second while
            genuinely contended.

            DO NOT DELETE THE `min(...)` AS REDUNDANT. It looks redundant - the
            deadline is already enforced above - and it is not.

        Args:
            request: The frozen request.
            holder: The claiming identity.

        Returns:
            AdmissionResult: Granted, or the last refusal with a timeout
                reason appended.
        """
        deadline = time.monotonic() + self._max_wait_seconds
        while True:
            verdict = self._orchestrator.admit(
                request=request,
                holder=holder,
                claim_table=self._claim_table,
            )
            if verdict.admitted:
                return verdict
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                # Carry the last refusal's evidence forward into the timeout
                # verdict FIRST, then release the verdict it came from.
                timed_out = AdmissionResult.refused(
                    reasons=(
                        AdmissionReason.SCOPE_CONTENDED,
                        AdmissionReason.WAIT_TIMEOUT,
                    ),
                    blocked_scopes=verdict.blocked_scopes,
                    evidence=verdict.evidence,
                )
                verdict.cleanup()
                return timed_out
            # THIS ATTEMPT IS SUPERSEDED. Nothing further will read this
            # verdict - the next pass allocates its own - so this loop is
            # where it ends, and under contention this loop is exactly where
            # discarded verdicts would otherwise pile up.
            verdict.cleanup()
            self._claim_table.wait_for_change(
                timeout_seconds=min(remaining, self._WAIT_SLICE_SECONDS)
            )

    def _finalize(
            self,
            *,
            request_id: str,
            holder: Identity,
            session: TransactionSession,
    ) -> None:
        """
        Release claims and drop all live bookkeeping for one session.

        Contract:
            TAKES THE REQUEST ID, NOT THE REQUEST. That is deliberate and it
            is a lifetime decision, not a style one. `TransactionRequest` is
            now `Cleanable` and is cleaned by the session that owns it, so a
            finaliser that read `request.request_id` would be reaching into a
            record whose owner may already have torn it down - which is
            exactly what the `begin` failure path does. Holding the plain
            string decouples finalisation from the record's lifetime
            completely, so the ordering of these two teardowns stops mattering.

        Args:
            request_id: The id of the request being finalised.
            holder: The claiming identity.
            session: The session being finalised.

        Returns:
            None.
        """
        self._orchestrator.release(
            request_id=request_id,
            holder=holder,
            claim_table=self._claim_table,
        )
        self._information_registry.unregister_activity(request_id)
        with self._lock:
            self._sessions_by_request_id.pop(request_id, None)
        self._forget_session(holder)
        # THE FINISHING THREAD OWNS THE TEARDOWN. A rollback inverse is a
        # closure that normally captures the session, so an unfinalised
        # session holds the cycle `session -> _rollback_actions -> closure ->
        # session`, which reference counting cannot free. Discarding the
        # inverses here means the thread that just finished the transaction
        # releases that graph immediately rather than leaving it for a
        # cycle-collector pass on some later schedule.
        #
        # NOT a full `cleanup()`: the caller must still be able to read the
        # outcome of its own transaction, and every guarded accessor raises
        # once cleaned. Ownership of the session object itself stays with
        # whoever called `begin`; only the cyclic edge is the plane's to cut.
        #
        # BOTH GUARDS ARE REQUIRED. `discard_inverses` refuses on a session
        # that is still OPEN, because an open session may still need to
        # unwind - and the `begin` failure path finalises a session that never
        # left OPEN, since `strategy.on_start` raised before any caller could
        # commit or fail it. Checking the status explicitly says that out
        # loud. It previously worked only as a side effect of that path
        # cleaning the session first, which made a correct outcome depend on
        # an ordering nothing stated.
        if not session.cleaned and session.status is not SessionStatus.OPEN:
            session.discard_inverses()

    def _current_session(
            self,
            submitter: Identity,
    ) -> Optional[TransactionSession]:
        """
        Return this thread's live session for `submitter`, if any.

        Args:
            submitter: The identity to look up.

        Returns:
            Optional[TransactionSession]: The live session, or None.
        """
        sessions = getattr(self._thread_local, "sessions", None)
        if not sessions:
            return None
        # KEYED ON THE STRING, NOT THE OBJECT. `Identity` is `Cleanable` and
        # CALLER-OWNED, so a subsystem may clean its own identity at any time.
        # A cleaned identity refuses `__hash__`, and a map keyed on the object
        # would be permanently corrupt the moment that happened - lookups miss
        # and the entry can never be removed. The string key is captured at
        # insertion and is immune.
        session = sessions.get(submitter.identity_key())
        if session is None or session.cleaned:
            return None
        if session.status is not SessionStatus.OPEN:
            return None
        return session

    def _remember_session(
            self,
            submitter: Identity,
            session: TransactionSession,
    ) -> None:
        """
        Record this thread's session for `submitter`.

        Args:
            submitter: The owning identity.
            session: The session to remember.

        Returns:
            None.
        """
        sessions = getattr(self._thread_local, "sessions", None)
        if sessions is None:
            sessions = {}
            self._thread_local.sessions = sessions
        # See `_current_session` for why this is a string key.
        sessions[submitter.identity_key()] = session

    def _forget_session(self, submitter: Identity) -> None:
        """
        Drop this thread's session record for `submitter`.

        Args:
            submitter: The identity to forget.

        Returns:
            None.
        """
        sessions = getattr(self._thread_local, "sessions", None)
        if sessions is not None:
            # See `_current_session` for why this is a string key.
            sessions.pop(submitter.identity_key(), None)
