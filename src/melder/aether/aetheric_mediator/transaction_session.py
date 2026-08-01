"""
The live transaction span for the mediator plane.

Dependency rule: standard library plus `melder.utilities` only.

Mirrors `TransactionSession` in the DevOps plane - root ownership, same-thread
joins, rollback actions, and an abort pipeline - and adds the OUTCOME POLICY the
owner specified: on failure a transaction either UNWINDS and raises, or is LEFT
BROKEN ON PURPOSE so an agent can repair it.
"""

import threading
from enum import StrEnum
from typing import Callable, Dict, List, Optional, Tuple

from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.staged_transaction import StagedTransaction
from melder.aether.aetheric_mediator.transaction_request import TransactionRequest
from melder.utilities.general_base.cleanable import Cleanable


class OutcomePolicy(StrEnum):
    """
    What a transaction does to the world when it fails.

    Purpose:
        Make the failure posture an EXPLICIT, per-transaction choice rather
        than an accident of whichever code path happened to raise.

    Contract:
        - `UNWIND`: run registered rollback actions newest-first, then raise.
          The world is returned toward its prior shape.
        - `LEAVE_BROKEN`: do NOT run rollback actions. Record precisely what
          was left in place and mark the session BROKEN. The half-built world
          is a WORK SURFACE for a repairing agent, not debris.

    Why LEAVE_BROKEN is first-class and not a degraded fallback:
        A structural rebuild that dies partway leaves objects that are often
        individually valid and expensive to recreate. Destroying them to reach
        a clean slate can cost more than mending them. This policy makes
        "leave it for an agent" a decision with a ledger attached, instead of
        the silent partial state that arises when nobody chose anything.

    Threading:
        Stateless enum; safe to share across threads.

    Registration:
        MELDER KERNEL - guarded. Policy vocabulary; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Per-transaction failure posture - unwind and raise,
        or leave the world broken with a ledger for agent repair.
    """

    UNWIND = "unwind"
    LEAVE_BROKEN = "leave_broken"


class SessionStatus(StrEnum):
    """
    The lifecycle state of one transaction session.

    Contract:
        `BROKEN` is a DISTINCT TERMINAL STATE, deliberately not a flavour of
        `ABORTED`. Aborted means the world was returned toward its prior
        shape; broken means it was knowingly left mid-flight for repair.
        Collapsing the two would erase exactly the distinction an agent needs
        to know whether there is anything to go and fix.

    Registration:
        MELDER KERNEL - guarded. Status vocabulary; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Session lifecycle state. BROKEN is terminal and
        distinct from ABORTED - it means repairable residue exists.
    """

    OPEN = "open"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ABORTING = "aborting"
    ABORTED = "aborted"
    BROKEN = "broken"


class _RollbackAction(Cleanable):
    """
    One registered inverse, paired with a description of what it undoes.

    Purpose:
        Own the single most dangerous reference in this package - a
        caller-supplied closure - and give the owning session a way to release
        it at an exact, chosen moment.

    Contract:
        - The DESCRIPTION IS NOT OPTIONAL and is the reason this is a class
          rather than a bare callable. Under `LEAVE_BROKEN` the action is never
          invoked, so the description becomes the ONLY record of what was left
          in place. An undescribed rollback action is invisible residue.
        - CLEANABLE BECAUSE `action` IS A COMPLEX TYPE. A closure captures
          whatever its defining scope held - the session, a frame, a conduit,
          a spellbook - so this small record can transitively pin a large live
          graph. `Callable` is exactly the field the repo's value-only
          dataclass rule exists to keep out of plain records, and DevOps
          treats its own hooks the same way: `ChangeControlManager.cleanup`
          explicitly `del`s `_commit_hook`, `_abort_hook`, and the rest rather
          than trusting them to fall away.
        - RELYING ON `list.clear()` ALONE IS NOT ENOUGH. Clearing the owning
          list drops these records by refcount only if nothing else is holding
          one. During unwind `_run_inverses` holds them in a local list, and a
          raising inverse attaches a traceback that keeps that frame - and so
          every remaining closure - alive for as long as the exception is
          referenced. An explicit release closes that path.

    Owned State:
        - `action`: the inverse. Released by `cleanup`.
        - `description`: plain-language record of what the inverse undoes.

    Threading:
        NO INTERNAL LOCK, deliberately. Each record is owned by exactly one
        `TransactionSession` and is only ever built or cleaned while that
        session's lock is held, so a lock here would be pure overhead on an
        object created several times per transaction.

    Registration:
        MELDER KERNEL - guarded. Session-internal; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. A registered inverse plus the description that
        survives when the inverse is deliberately not run. Cleanable so the
        captured closure is released deterministically.
    """

    __slots__ = Cleanable.__slots__ + ["action", "description"]

    def __init__(self, *, action: Callable[[], None], description: str) -> None:
        """
        Build one described rollback action.

        Args:
            action: The zero-argument inverse to invoke on unwind.
            description: What this action undoes, in plain language.

        Returns:
            None.
        """
        super().__init__()
        self.action: Callable[[], None] = action
        self.description: str = description

    def cleanup(self) -> None:
        """
        Idempotently release the captured closure.

        Contract:
            Callers that need the description must read it BEFORE cleaning;
            `discard_inverses` and `fail` both snapshot it first. Dropping it
            here rather than keeping it is the honest choice: a cleaned record
            owns nothing.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self.action
        del self.description


class TransactionSession(Cleanable):
    """
    One live transaction span, owned by exactly one root thread.

    Purpose:
        Hold everything true about a transaction between admission and its
        terminal state: who owns it, how deep the joins go, what inverses are
        registered, how it ends, and what it left behind if it ended badly.

    Contract:
        - ONE ROOT OWNER. The creating thread owns the session. A join from a
          FOREIGN thread FAILS FAST NAMING THE OWNING THREAD rather than
          waiting, matching DevOps: a cross-thread re-begin is a caller bug,
          and blocking on it would convert that bug into a hang.
        - JOINS ARE DEPTH-COUNTED. Same-thread re-entry increments depth;
          `leave` decrements. The session only becomes finalisable at depth
          zero, so an inner scope cannot terminate an outer one.
        - ROLLBACK ACTIONS ARE DESCRIBED. Registration requires a description
          so `LEAVE_BROKEN` can report what was left undone.
        - UNWIND IS NEWEST-FIRST AND BEST-EFFORT PER ACTION. One failing
          inverse must not prevent the rest from running - a partial unwind
          that stops at the first error is strictly worse than one that
          reaches the bottom. Failures are COLLECTED AND RECORDED, never
          silently dropped.
        - FAILURES DURING UNWIND ARE VISIBLE. They are retained on the session
          as rendered strings and surface through `describe()`. DevOps returns
          them from `run_abort_pipeline` as a list, which is only safe if a
          caller reads it; recording them here means they are reportable even
          when nobody does.

    Owned State:
        The request, holder, owner thread id, depth, status, failure reason,
        outcome policy, described rollback actions, and unwind-failure
        records. The claim table is NOT owned and is not referenced here;
        releasing claims belongs to the orchestrator.

    Lifecycle / Cleanup:
        Idempotent. Cleanup drops the action list WITHOUT running it - a
        session being cleaned is not a session being aborted, and quietly
        firing inverses during teardown would be an invisible mutation.

    Threading:
        One `RLock` guards state. Rollback actions are invoked OUTSIDE the
        lock: they are foreign code and may take arbitrary time or re-enter,
        which is exactly the shape that deadlocks a lock-holding pipeline.

    Registration:
        MELDER KERNEL - guarded. Created by the mediator; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. One live transaction span with depth-counted joins,
        described inverses, and an explicit unwind-or-leave-broken outcome.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_request",
        "_staged",
        "_holder",
        "_owner_thread_id",
        "_depth",
        "_status",
        "_failure_reason",
        "_outcome_policy",
        "_rollback_actions",
        "_unwind_failures",
        "_leave_broken_residue",
    ]

    def __init__(
            self,
            *,
            request: TransactionRequest,
            staged: "StagedTransaction",
            holder: Identity,
            outcome_policy: OutcomePolicy = OutcomePolicy.UNWIND,
    ) -> None:
        """
        Open one session owned by the calling thread.

        Args:
            request: The admitted frozen request.
            staged: The post-admission record, built ONCE at admission and
                carried here. It is not rebuilt at commit or failure: doing so
                allocated a fresh copy of the metadata on every terminal path
                AND stamped `admitted_at` with the COMMIT time, which made the
                field lie about when admission happened.
            holder: The claiming identity.
            outcome_policy: What to do to the world if this transaction fails.
                Defaults to `UNWIND`, the conservative posture.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._request: TransactionRequest = request
        self._staged: "StagedTransaction" = staged
        self._holder: Identity = holder
        self._owner_thread_id: int = threading.get_ident()
        self._depth: int = 1
        self._status: SessionStatus = SessionStatus.OPEN
        self._outcome_policy: OutcomePolicy = outcome_policy
        self._failure_reason: Optional[str] = None
        self._rollback_actions: List[_RollbackAction] = []
        self._unwind_failures: List[str] = []
        # THE LEDGER `LEAVE_BROKEN` PROMISES. `fail` returns the residue to its
        # caller, but finalisation then discards the inverses, so a caller that
        # did not capture the return - or a transaction that broke during
        # COMMIT, where nobody is holding a return value at all - would lose the
        # only record of what was left in the world. Retaining it here makes the
        # ledger a property of the session rather than of whoever happened to
        # call which method, which is what "left for an agent to repair" needs
        # in order to mean anything.
        self._leave_broken_residue: Tuple[str, ...] = ()

    def cleanup(self) -> None:
        """
        Idempotently drop session state WITHOUT running rollback actions.

        Contract:
            - Cleaning is not aborting. Firing inverses here would mutate the
              world during teardown with nothing recording that it happened.
            - CLEARING `_rollback_actions` IS REFERENCE-CYCLE BREAKING, NOT
              JUST TIDINESS. A rollback closure almost always captures the
              session it was registered on, forming
              `session -> _rollback_actions -> _RollbackAction -> closure ->
              session`. Reference counting CANNOT collect that; only the cycle
              collector can, on its own schedule. Clearing the list here breaks
              the cycle so the finishing thread frees the graph immediately
              rather than deferring it to a GC pass.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            # Re-check under the lock; the outer check is a fast path only.
            # Without this, two concurrent cleanups both reach the deletions
            # below and the loser raises AttributeError.
            if self._cleaned:
                return
            self._cleaned = True
            # Order matters: break the closure cycle FIRST, so nothing keeps
            # this session alive while the remaining fields are dropped.
            # Release each record before clearing the list - the closure is
            # the complex reference, and `clear()` only drops it if nothing
            # else happens to be holding the record.
            for entry in self._rollback_actions:
                entry.cleanup()
            self._rollback_actions.clear()
            self._unwind_failures.clear()
            # THIS SESSION IS THE OWNER OF BOTH RECORDS, so this is where
            # they die. `del` alone would only drop THIS reference; the
            # orchestrator's `_in_flight` and the information registry's
            # `_active` borrow the same two objects, and a borrowed reference
            # outliving the owner is exactly the deferred teardown this repo
            # exists to avoid. Cleaning them here means the thread tearing
            # down the session releases their fields deterministically.
            #
            # SAFE BECAUSE THE BORROWERS ARE ALREADY GONE by the time any
            # normal path reaches here: `Mediator._finalize` unregisters both
            # borrows, and `Mediator.cleanup` tears the borrowers down BEFORE
            # the sessions for the same reason.
            self._request.cleanup()
            self._staged.cleanup()
        del self._request
        del self._staged
        del self._holder
        del self._owner_thread_id
        del self._depth
        del self._status
        del self._failure_reason
        del self._outcome_policy
        del self._rollback_actions
        del self._unwind_failures
        del self._leave_broken_residue
        del self._lock

    @property
    def request(self) -> TransactionRequest:
        """Return the frozen request this session was opened for."""
        self.check_cleaned()
        return self._request

    @property
    def staged(self) -> "StagedTransaction":
        """
        Return the post-admission record, built once at admission.

        Contract:
            The SAME object for the life of the session. Callers must not
            rebuild it; `admitted_at` means admission time and rebuilding
            would silently restamp it.

        Returns:
            StagedTransaction: The immutable post-admission record.
        """
        self.check_cleaned()
        return self._staged

    @property
    def holder(self) -> Identity:
        """Return the claiming identity that owns this session."""
        self.check_cleaned()
        return self._holder

    @property
    def status(self) -> SessionStatus:
        """Return the current lifecycle status."""
        self.check_cleaned()
        with self._lock:
            return self._status

    @property
    def depth(self) -> int:
        """Return the current join depth; 1 is the root scope."""
        self.check_cleaned()
        with self._lock:
            return self._depth

    @property
    def outcome_policy(self) -> OutcomePolicy:
        """Return the failure posture configured for this transaction."""
        self.check_cleaned()
        return self._outcome_policy

    @property
    def failure_reason(self) -> Optional[str]:
        """Return why this session failed, or None when it has not."""
        self.check_cleaned()
        with self._lock:
            return self._failure_reason

    @property
    def leave_broken_residue(self) -> Tuple[str, ...]:
        """
        Return what this session deliberately left in the world, if anything.

        Contract:
            Non-empty ONLY for a session that ended `BROKEN` under
            `OutcomePolicy.LEAVE_BROKEN`. Each entry is the description of an
            inverse that was registered and deliberately NOT run, so this is
            the work list for whoever repairs the half-built world.

            Survives finalisation on purpose. `discard_inverses` empties
            `registered_inverses` as soon as the transaction is terminal, so
            without this the ledger would exist only in the return value of
            `fail(...)` - lost entirely when a commit pipeline broke the
            session and no caller was holding that return.

        Returns:
            Tuple[str, ...]: Residue descriptions, empty for every other
                terminal status.

        Raises:
            RuntimeError: If cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._leave_broken_residue

    def join(self) -> int:
        """
        Re-enter this session from its owning thread.

        Contract:
            Same-thread only. A foreign thread FAILS FAST naming the owner
            rather than blocking, because a cross-thread re-begin is a caller
            bug and waiting would turn it into a hang.

        Returns:
            int: The new join depth.

        Raises:
            RuntimeError: If cleaned, if the session is already terminal, or
                if called from a thread other than the owner.
        """
        self.check_cleaned()
        current_thread_id = threading.get_ident()
        with self._lock:
            if current_thread_id != self._owner_thread_id:
                raise RuntimeError(
                    "session for request {0!r} is owned by thread {1}; thread "
                    "{2} cannot join it. A cross-thread re-begin is a caller "
                    "bug, not a wait.".format(
                        self._request.request_id,
                        self._owner_thread_id,
                        current_thread_id,
                    )
                )
            if self._status is not SessionStatus.OPEN:
                raise RuntimeError(
                    "cannot join session for request {0!r} in status "
                    "{1}.".format(self._request.request_id, self._status.value)
                )
            self._depth += 1
            return self._depth

    def leave(self) -> int:
        """
        Exit one join scope.

        Returns:
            int: The remaining depth. Zero means the root scope has exited and
                the session is finalisable.

        Raises:
            RuntimeError: If cleaned or already at depth zero.
        """
        self.check_cleaned()
        with self._lock:
            if self._depth <= 0:
                raise RuntimeError(
                    "session for request {0!r} is already at depth 0.".format(
                        self._request.request_id
                    )
                )
            self._depth -= 1
            return self._depth

    def register_rollback_action(
            self,
            *,
            action: Callable[[], None],
            description: str,
    ) -> None:
        """
        Register one inverse together with what it undoes.

        Contract:
            The description is REQUIRED. Under `LEAVE_BROKEN` the action never
            runs, and the description becomes the only record that the effect
            exists at all.

        Args:
            action: Zero-argument inverse invoked on unwind, newest first.
            description: What this action undoes, in plain language.

        Returns:
            None.

        Raises:
            RuntimeError: If cleaned or the session is already terminal.
            ValueError: If `description` is empty.
        """
        self.check_cleaned()
        if not description or not description.strip():
            raise ValueError(
                "register_rollback_action requires a non-empty description; "
                "an undescribed inverse becomes invisible residue under the "
                "leave_broken outcome."
            )
        with self._lock:
            if self._status is not SessionStatus.OPEN:
                raise RuntimeError(
                    "cannot register a rollback action on a session in status "
                    "{0}.".format(self._status.value)
                )
            self._rollback_actions.append(
                _RollbackAction(action=action, description=description)
            )

    def mark_committing(self) -> None:
        """
        Enter the COMMITTING state before the commit pipeline runs.

        Purpose:
            Make "the commit is in progress" a real, observable state rather
            than an instant, so a transaction that dies inside its own commit
            pipeline does not report itself as having succeeded.

        Contract:
            - OPEN -> COMMITTING, at join depth zero only.
            - This is the state `fail(...)` accepts alongside OPEN, which is
              what lets a failed commit unwind instead of being discarded.
            - Ported from DevOps, where `_finalize_root_session` marks
              committing, runs the pipeline, and only then marks committed. The
              earlier shape here marked COMMITTED up front, so a raising hook
              left a session claiming success - and `SessionStatus.COMMITTING`
              existed in the vocabulary while nothing ever assigned it.

        Returns:
            None.

        Raises:
            RuntimeError: If cleaned, not open, or still joined above the root.
        """
        self.check_cleaned()
        with self._lock:
            if self._status is not SessionStatus.OPEN:
                raise RuntimeError(
                    "cannot begin committing a session in status {0}.".format(
                        self._status.value
                    )
                )
            if self._depth > 0:
                raise RuntimeError(
                    "cannot commit session for request {0!r} at join depth "
                    "{1}; inner scopes must leave first.".format(
                        self._request.request_id, self._depth
                    )
                )
            self._status = SessionStatus.COMMITTING

    def mark_committed(self) -> None:
        """
        Mark this session successfully committed.

        Contract:
            COMMITTING -> COMMITTED, and only that transition. Reaching
            COMMITTED now REQUIRES having passed through COMMITTING, which is
            what makes the state honest: a session can only claim success after
            its commit pipeline has actually returned. A session that was
            failed, broken, or never entered commit still refuses here.

        Returns:
            None.

        Raises:
            RuntimeError: If cleaned, or not currently COMMITTING.
        """
        self.check_cleaned()
        with self._lock:
            if self._status is not SessionStatus.COMMITTING:
                raise RuntimeError(
                    "cannot mark a session committed from status {0}; it must "
                    "be COMMITTING, which means its commit pipeline ran.".format(
                        self._status.value
                    )
                )
            self._status = SessionStatus.COMMITTED

    def fail(self, reason: str) -> Tuple[SessionStatus, Tuple[str, ...]]:
        """
        Terminate this session according to its outcome policy.

        Contract:
            - `UNWIND`: runs every registered inverse NEWEST FIRST, outside
              the lock, best-effort per action. Terminal status `ABORTED`.
            - `LEAVE_BROKEN`: runs NOTHING. Terminal status `BROKEN`, and the
              returned residue lists what was deliberately left in place. The
              residue is ALSO retained on the session and surfaced through
              `describe()`, so the ledger survives a caller that ignores the
              return value - and survives the commit-failure path, where there
              is no caller holding one.
            - Either way the reason is recorded and the session is terminal.
            - ACCEPTS `OPEN` OR `COMMITTING`. Committing is not a safe harbour:
              a transaction that dies inside its own commit pipeline is exactly
              the case that most needs to unwind, and refusing it here is what
              previously forced the mediator to discard the inverses instead of
              running them.

        Args:
            reason: Why the transaction failed.

        Returns:
            Tuple[SessionStatus, Tuple[str, ...]]:
                The terminal status, and either the unwind failures (UNWIND)
                or the residue descriptions left in place (LEAVE_BROKEN).

        Raises:
            RuntimeError: If cleaned or the session is already terminal.
        """
        self.check_cleaned()
        with self._lock:
            if self._status not in (
                SessionStatus.OPEN,
                SessionStatus.COMMITTING,
            ):
                raise RuntimeError(
                    "cannot fail a session already in status {0}.".format(
                        self._status.value
                    )
                )
            self._failure_reason = reason
            policy = self._outcome_policy
            if policy is OutcomePolicy.LEAVE_BROKEN:
                residue = tuple(
                    entry.description for entry in self._rollback_actions
                )
                # Retained, not just returned - finalisation discards the
                # inverses immediately afterwards, so this is the only place
                # the ledger can survive.
                self._leave_broken_residue = residue
                self._status = SessionStatus.BROKEN
                return SessionStatus.BROKEN, residue
            self._status = SessionStatus.ABORTING
            # OWNERSHIP TRANSFERS to `pending`. Emptying the list here means
            # exactly one place is responsible for releasing these records -
            # `_run_inverses`, as each one finishes - instead of leaving a
            # second reference behind for `discard_inverses` to trip over.
            pending = list(reversed(self._rollback_actions))
            self._rollback_actions.clear()
        failures = self._run_inverses(pending)
        with self._lock:
            self._unwind_failures.extend(failures)
            self._status = SessionStatus.ABORTED
            return SessionStatus.ABORTED, tuple(failures)

    def _run_inverses(self, pending: List[_RollbackAction]) -> List[str]:
        """
        Invoke inverses outside the lock, collecting failures.

        Contract:
            - Best-effort PER ACTION: one failure never prevents the remaining
              inverses from running. Runs outside the session lock because
              these are foreign callables that may block or re-enter.
            - EACH RECORD IS RELEASED THE MOMENT IT HAS RUN. This is not
              tidiness. A failing inverse raises, and the caught exception
              carries a traceback that references THIS frame - including
              `pending`, and therefore every closure still in it, and
              everything those closures captured. Releasing as we go bounds
              that to the one record currently in hand rather than letting a
              single early failure pin the whole unwind set for as long as the
              exception lives.
            - `pending` is owned here: `fail` emptied the session's list when
              it handed the records over.

        Args:
            pending: Inverses in the order they should run (newest first).

        Returns:
            List[str]: Rendered failure records, empty when all succeeded.
        """
        failures: List[str] = []
        for entry in pending:
            try:
                entry.action()
            except Exception as error:
                failures.append(
                    "{0} -> {1}: {2}".format(
                        entry.description, type(error).__name__, error
                    )
                )
            finally:
                entry.cleanup()
        pending.clear()
        return failures

    def discard_inverses(self) -> Tuple[str, ...]:
        """
        Drop the registered inverses once this session is terminal.

        Purpose:
            BREAK THE ONE REFERENCE CYCLE THIS OBJECT CAN FORM, on the thread
            that finished the transaction, at the moment it finishes.

        Why this exists:
            A rollback inverse is a closure, and a useful one almost always
            captures the session it will roll back:

                session.register_inverse(
                    "detach conduit", lambda: frame.detach(conduit)
                )

            That gives `session -> _rollback_actions -> _RollbackAction ->
            action closure -> session`. A cycle is invisible to reference
            counting: when the caller drops its last handle the refcount does
            NOT reach zero, so the whole graph - session, request, staged
            record, metadata, and everything the closures captured - survives
            until a cycle-collector pass runs on some later, unrelated
            schedule. That is precisely the deferred, non-deterministic
            teardown this repo is built to avoid.

        Contract:
            - TERMINAL ONLY. Refuses while the session is still OPEN, because
              an open session may still need to unwind. By the time this runs
              the inverses are dead weight in every case: UNWIND already ran
              them, LEAVE_BROKEN already copied their descriptions into the
              residue it returned, and COMMITTED will never need them.
            - Returns the discarded descriptions so a caller that wants a
              post-mortem gets one without retaining the closures.
            - IDEMPOTENT: a second call returns an empty tuple.
            - Does NOT clean the session. Status, request, staged record, and
              failure reason all stay readable, so the caller can still
              inspect the outcome of its own transaction. Only the closures -
              the sole cyclic edge - are released here.

        Returns:
            Tuple[str, ...]: Descriptions of the inverses that were discarded.

        Raises:
            RuntimeError: If cleaned, or if the session is still OPEN.
        """
        self.check_cleaned()
        with self._lock:
            if self._status is SessionStatus.OPEN:
                raise RuntimeError(
                    "cannot discard inverses for request {0!r} while the "
                    "session is still OPEN; it may still need to unwind."
                    .format(self._request.request_id)
                )
            # Snapshot the descriptions BEFORE releasing, then release each
            # record explicitly rather than trusting `clear()` to be the only
            # thing holding them. Deepest-first, matching how DevOps tears
            # down its own nested state.
            discarded = tuple(
                entry.description for entry in self._rollback_actions
            )
            for entry in self._rollback_actions:
                entry.cleanup()
            self._rollback_actions.clear()
            return discarded

    def describe(self) -> Dict[str, object]:
        """
        Return a detached snapshot of this session.

        Contract:
            Values only - safe to log or ship. Includes unwind failures so
            they are visible even when no caller inspected the `fail` return.

        Returns:
            Dict[str, object]: Status, policy, depth, reason, and residue.

        Raises:
            RuntimeError: If cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "request_id": self._request.request_id,
                "transaction_type": self._request.transaction_type.value,
                "holder": self._holder.describe(),
                "owner_thread_id": self._owner_thread_id,
                "status": self._status.value,
                "outcome_policy": self._outcome_policy.value,
                "depth": self._depth,
                "failure_reason": self._failure_reason,
                "registered_inverses": [
                    entry.description for entry in self._rollback_actions
                ],
                "unwind_failures": list(self._unwind_failures),
                # Empty unless this session ended BROKEN. It is the durable
                # answer to "what is still out there for someone to repair",
                # and it deliberately outlives `discard_inverses`, which
                # empties `registered_inverses` moments later.
                "leave_broken_residue": list(self._leave_broken_residue),
            }
