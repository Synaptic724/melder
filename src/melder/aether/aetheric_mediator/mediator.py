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
    ]

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

    def cleanup(self) -> None:
        """
        Idempotently tear down the plane and its children.

        Contract:
            Children are cleaned in REVERSE dependency order, and the claim
            table LAST, because its cleanup is what wakes any thread still
            parked waiting for passage. Cleaning it first would leave waiters
            parked against a half-dead plane.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            self._cleaned = True
            sessions = list(self._sessions_by_request_id.values())
            self._sessions_by_request_id.clear()
        for session in sessions:
            if not session.cleaned:
                session.cleanup()
        self._strategy_builder.cleanup()
        self._information_registry.cleanup()
        self._orchestrator.cleanup()
        self._claim_table.cleanup()
        del self._sessions_by_request_id
        del self._thread_local
        del self._max_wait_seconds
        del self._strategy_builder
        del self._information_registry
        del self._orchestrator
        del self._claim_table
        del self._lock

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
        claims = strategy.build_start_plan(
            submitter=submitter,
            metadata=dict(metadata or {}),
        )
        request = TransactionRequest.build(
            request_id=uuid.uuid4().hex,
            transaction_type=transaction_type,
            submitter=submitter,
            scope_claims=claims,
            metadata=dict(metadata or {}),
        )
        verdict = self._admit_with_wait(request=request, holder=submitter)
        if not verdict.admitted:
            raise RuntimeError(
                "transaction {0} was refused: {1}".format(
                    request.describe(), verdict.describe()
                )
            )
        staged = StagedTransaction.from_request(
            request=request, admitted_at=time.time()
        )
        session = TransactionSession(
            request=request,
            holder=submitter,
            outcome_policy=outcome_policy,
        )
        with self._lock:
            self._sessions_by_request_id[request.request_id] = session
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
            self._finalize(
                request=request, holder=submitter, session=session
            )
            if not session.cleaned:
                session.cleanup()
            raise
        return session

    def commit(self, session: TransactionSession) -> None:
        """
        Commit one session, stamping reporting and releasing its claims.

        Contract:
            Order matters and is deliberate: `apply_commit_delta` runs BEFORE
            the claims are released, so the freshness stamp it writes is
            race-free against overlapping writers. Releasing first would open
            a window where another transaction could mutate the region
            between the stamp and the release.

        Args:
            session: The session to commit. Must be at join depth zero.

        Returns:
            None.

        Raises:
            RuntimeError: If the plane is cleaned, or the session is not
                finalisable.
        """
        self.check_cleaned()
        if session.depth > 0:
            raise RuntimeError(
                "cannot commit a session at join depth {0}; inner scopes must "
                "leave first.".format(session.depth)
            )
        request = session.request
        holder = session.holder
        staged = StagedTransaction.from_request(
            request=request, admitted_at=time.time()
        )
        strategy = self._strategy_builder.resolve(request.transaction_type)
        session.mark_committed()
        try:
            strategy.apply_commit_delta(
                information_registry=self._information_registry,
                submitter=holder,
                staged=staged,
            )
            strategy.on_end(submitter=holder, staged=staged)
        finally:
            # CLEANUP RUNS EVEN WHEN A HOOK RAISES, matching the DevOps
            # contract: a failing commit hook must still release the
            # in-flight registration and the claims. The exception
            # propagates - the caller learns the commit failed - but the
            # plane is not left holding scopes for a transaction nobody
            # will ever finalise.
            self._finalize(request=request, holder=holder, session=session)

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
        request = session.request
        holder = session.holder
        staged = StagedTransaction.from_request(
            request=request, admitted_at=time.time()
        )
        status, records = session.fail(reason)
        strategy = self._strategy_builder.resolve(request.transaction_type)
        try:
            strategy.on_end(submitter=holder, staged=staged)
        finally:
            # Same guarantee as commit: the failure path must release claims
            # even when the family's own end hook also fails. A transaction
            # that failed twice is still a transaction whose scopes must be
            # freed.
            self._finalize(request=request, holder=holder, session=session)
        return status, records

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
                return AdmissionResult.refused(
                    reasons=(
                        AdmissionReason.SCOPE_CONTENDED,
                        AdmissionReason.WAIT_TIMEOUT,
                    ),
                    blocked_scopes=verdict.blocked_scopes,
                    evidence=verdict.evidence,
                )
            self._claim_table.wait_for_change(timeout_seconds=remaining)

    def _finalize(
            self,
            *,
            request: TransactionRequest,
            holder: Identity,
            session: TransactionSession,
    ) -> None:
        """
        Release claims and drop all live bookkeeping for one session.

        Args:
            request: The request being finalised.
            holder: The claiming identity.
            session: The session being finalised.

        Returns:
            None.
        """
        self._orchestrator.release(
            request_id=request.request_id,
            holder=holder,
            claim_table=self._claim_table,
        )
        self._information_registry.unregister_activity(request.request_id)
        with self._lock:
            self._sessions_by_request_id.pop(request.request_id, None)
        self._forget_session(holder)

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
        session = sessions.get(submitter)
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
        sessions[submitter] = session

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
            sessions.pop(submitter, None)
