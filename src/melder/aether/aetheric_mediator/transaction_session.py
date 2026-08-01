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


class _RollbackAction:
    """
    One registered inverse, paired with a description of what it undoes.

    Contract:
        The DESCRIPTION IS NOT OPTIONAL and is the reason this is a class
        rather than a bare callable. Under `LEAVE_BROKEN` the action is never
        invoked, so the description becomes the ONLY record of what was left
        in place. An undescribed rollback action is invisible residue.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. A registered inverse plus the description that
        survives when the inverse is deliberately not run.
    """

    __slots__ = ["action", "description"]

    def __init__(self, *, action: Callable[[], None], description: str) -> None:
        """
        Build one described rollback action.

        Args:
            action: The zero-argument inverse to invoke on unwind.
            description: What this action undoes, in plain language.

        Returns:
            None.
        """
        self.action: Callable[[], None] = action
        self.description: str = description


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
        "_holder",
        "_owner_thread_id",
        "_depth",
        "_status",
        "_failure_reason",
        "_outcome_policy",
        "_rollback_actions",
        "_unwind_failures",
    ]

    def __init__(
            self,
            *,
            request: TransactionRequest,
            holder: Identity,
            outcome_policy: OutcomePolicy = OutcomePolicy.UNWIND,
    ) -> None:
        """
        Open one session owned by the calling thread.

        Args:
            request: The admitted frozen request.
            holder: The claiming identity.
            outcome_policy: What to do to the world if this transaction fails.
                Defaults to `UNWIND`, the conservative posture.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._request: TransactionRequest = request
        self._holder: Identity = holder
        self._owner_thread_id: int = threading.get_ident()
        self._depth: int = 1
        self._status: SessionStatus = SessionStatus.OPEN
        self._failure_reason: Optional[str] = None
        self._outcome_policy: OutcomePolicy = outcome_policy
        self._rollback_actions: List[_RollbackAction] = []
        self._unwind_failures: List[str] = []

    def cleanup(self) -> None:
        """
        Idempotently drop session state WITHOUT running rollback actions.

        Contract:
            Cleaning is not aborting. Firing inverses here would mutate the
            world during teardown with nothing recording that it happened.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            self._cleaned = True
            self._rollback_actions.clear()
            self._unwind_failures.clear()
        del self._request
        del self._holder
        del self._owner_thread_id
        del self._depth
        del self._status
        del self._failure_reason
        del self._outcome_policy
        del self._rollback_actions
        del self._unwind_failures
        del self._lock

    @property
    def request(self) -> TransactionRequest:
        """Return the frozen request this session was opened for."""
        self.check_cleaned()
        return self._request

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

    def mark_committed(self) -> None:
        """
        Mark this session successfully committed.

        Returns:
            None.

        Raises:
            RuntimeError: If cleaned, not open, or still joined above the root.
        """
        self.check_cleaned()
        with self._lock:
            if self._status is not SessionStatus.OPEN:
                raise RuntimeError(
                    "cannot commit a session in status {0}.".format(
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
            self._status = SessionStatus.COMMITTED

    def fail(self, reason: str) -> Tuple[SessionStatus, Tuple[str, ...]]:
        """
        Terminate this session according to its outcome policy.

        Contract:
            - `UNWIND`: runs every registered inverse NEWEST FIRST, outside
              the lock, best-effort per action. Terminal status `ABORTED`.
            - `LEAVE_BROKEN`: runs NOTHING. Terminal status `BROKEN`, and the
              returned residue lists what was deliberately left in place.
            - Either way the reason is recorded and the session is terminal.

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
            if self._status is not SessionStatus.OPEN:
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
                self._status = SessionStatus.BROKEN
                return SessionStatus.BROKEN, residue
            self._status = SessionStatus.ABORTING
            pending = list(reversed(self._rollback_actions))
        failures = self._run_inverses(pending)
        with self._lock:
            self._unwind_failures.extend(failures)
            self._status = SessionStatus.ABORTED
            return SessionStatus.ABORTED, tuple(failures)

    def _run_inverses(self, pending: List[_RollbackAction]) -> List[str]:
        """
        Invoke inverses outside the lock, collecting failures.

        Contract:
            Best-effort PER ACTION: one failure never prevents the remaining
            inverses from running. Runs outside the session lock because these
            are foreign callables that may block or re-enter.

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
        return failures

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
            }
