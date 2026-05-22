import threading
import time
import warnings
from typing import (
    Iterable,
    Optional,
    Dict,
    List,
    TYPE_CHECKING,
    ClassVar,
)

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_session import (
    TransactionSession,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
        ChangeControlEmbargoManager,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.orchestrator import (
        ChangeControlOrchestrator,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
        ChangeControlStagedMutation,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
        ChangeControlTransactionManager,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
        ChangeControlTransactionRequest,
    )


class TransactionMediator(Cleanable):
    """
    Frame-local live transaction session mediator.

    Purpose:
        Own the runtime session layer that sits above immutable request/staged
        payloads. This mediator tracks same-thread recursion, root-session
        ownership, and root commit/abort finalization without replacing the
        existing request builder, embargo manager, or orchestrator.

    Contract:
        - Root sessions are keyed by admitted request id.
        - Same-thread nested work joins the active root session.
        - Cross-thread root starts may be rejected depending on mode and
          `allow_multiple_root_transactions`.
        - Only the outermost frame finalizes commit or abort through the
          existing orchestrator path.
        - `warn` mode allows additional root sessions but emits a warning.

    Threading:
        - Shared mediator state is guarded by an internal `RLock`.
        - Active execution frame stacks are stored in `threading.local()`.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    AVAILABLE_MODES: ClassVar[frozenset[str]] = frozenset(
        ("strict", "warn", "disabled")
    )
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_wait_condition",
        "_transaction_manager",
        "_embargo_manager",
        "_orchestrator",
        "_change_control_mode",
        "_allow_multiple_root_transactions",
        "_queue_competing_root_transactions",
        "_max_transaction_wait_time_in_seconds",
        "_sessions_by_request_id",
        "_pending_root_starts",
        "_thread_local",
    ]

    def __init__(
            self,
            *,
            transaction_manager: "ChangeControlTransactionManager",
            embargo_manager: "ChangeControlEmbargoManager",
            orchestrator: "ChangeControlOrchestrator",
            change_control_mode: str = "strict",
            allow_multiple_root_transactions: bool = False,
            queue_competing_root_transactions: bool = False,
            max_transaction_wait_time_in_seconds: float = 30.0,
    ) -> None:
        """
        Initialize the live transaction mediator.

        Args:
            transaction_manager:
                In-flight request registry helper.
            embargo_manager:
                Embargo helper used by orchestrator commit/abort paths.
            orchestrator:
                Admission/commit/abort orchestration helper.
            change_control_mode:
                `strict`, `warn`, or `disabled`.
            allow_multiple_root_transactions:
                Whether multiple root sessions may coexist in the frame.
            queue_competing_root_transactions:
                Whether competing root starts should wait in FIFO order.
            max_transaction_wait_time_in_seconds:
                Maximum seconds a competing root start may wait for the slot.

        Raises:
            ValueError: If required collaborators are missing or mode is invalid.
            TypeError: If `allow_multiple_root_transactions` is not a bool.
        """
        super().__init__()
        if transaction_manager is None:
            raise ValueError("transaction_manager must not be None.")
        if embargo_manager is None:
            raise ValueError("embargo_manager must not be None.")
        if orchestrator is None:
            raise ValueError("orchestrator must not be None.")
        if not isinstance(allow_multiple_root_transactions, bool):
            raise TypeError("allow_multiple_root_transactions must be a bool.")
        if not isinstance(queue_competing_root_transactions, bool):
            raise TypeError("queue_competing_root_transactions must be a bool.")
        if (
            not isinstance(max_transaction_wait_time_in_seconds, (int, float))
            or isinstance(max_transaction_wait_time_in_seconds, bool)
        ):
            raise TypeError(
                "max_transaction_wait_time_in_seconds must be a float or int."
            )
        if max_transaction_wait_time_in_seconds <= 0:
            raise ValueError(
                "max_transaction_wait_time_in_seconds must be greater than 0."
            )

        self._lock: threading.RLock = threading.RLock()
        self._wait_condition: threading.Condition = threading.Condition(self._lock)
        self._transaction_manager: ChangeControlTransactionManager = transaction_manager
        self._embargo_manager: ChangeControlEmbargoManager = embargo_manager
        self._orchestrator: ChangeControlOrchestrator = orchestrator
        self._change_control_mode: str = self._normalize_mode(
            change_control_mode
        )
        self._allow_multiple_root_transactions: bool = (
            allow_multiple_root_transactions
        )
        self._queue_competing_root_transactions: bool = (
            queue_competing_root_transactions
        )
        self._max_transaction_wait_time_in_seconds: float = float(
            max_transaction_wait_time_in_seconds
        )
        self._sessions_by_request_id: Dict[str, TransactionSession] = {}
        self._pending_root_starts: List[int] = []
        self._thread_local: threading.local = threading.local()

    def cleanup(self) -> None:
        """
        Idempotently clear mediator-owned live session state.

        Contract:
            - Does not commit or abort in-flight requests implicitly.
            - Drops local session references and thread-local stacks only.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._sessions_by_request_id is not None:
                for session in list(self._sessions_by_request_id.values()):
                    try:
                        session.cleanup()
                    except Exception:
                        pass
                self._sessions_by_request_id.clear()
            if self._pending_root_starts is not None:
                self._pending_root_starts.clear()
            del self._sessions_by_request_id
            del self._pending_root_starts
            del self._transaction_manager
            del self._embargo_manager
            del self._orchestrator
            del self._change_control_mode
            del self._allow_multiple_root_transactions
            del self._queue_competing_root_transactions
            del self._max_transaction_wait_time_in_seconds
            del self._thread_local
            del self._wait_condition
        del self._lock

    def configure(
            self,
            *,
            change_control_mode: str,
            allow_multiple_root_transactions: bool,
            queue_competing_root_transactions: bool,
            max_transaction_wait_time_in_seconds: float,
    ) -> None:
        """
        Update mediator root-session policy.

        Args:
            change_control_mode:
                `strict`, `warn`, or `disabled`.
            allow_multiple_root_transactions:
                Whether multiple root sessions may coexist.
            queue_competing_root_transactions:
                Whether competing root starts queue for their turn.
            max_transaction_wait_time_in_seconds:
                Maximum seconds a queued root start may wait.
        """
        self.check_cleaned()
        normalized_mode = self._normalize_mode(change_control_mode)
        if not isinstance(allow_multiple_root_transactions, bool):
            raise TypeError("allow_multiple_root_transactions must be a bool.")
        if not isinstance(queue_competing_root_transactions, bool):
            raise TypeError("queue_competing_root_transactions must be a bool.")
        if (
            not isinstance(max_transaction_wait_time_in_seconds, (int, float))
            or isinstance(max_transaction_wait_time_in_seconds, bool)
        ):
            raise TypeError(
                "max_transaction_wait_time_in_seconds must be a float or int."
            )
        if max_transaction_wait_time_in_seconds <= 0:
            raise ValueError(
                "max_transaction_wait_time_in_seconds must be greater than 0."
            )
        with self._lock:
            self._change_control_mode = normalized_mode
            self._allow_multiple_root_transactions = (
                allow_multiple_root_transactions
            )
            self._queue_competing_root_transactions = (
                queue_competing_root_transactions
            )
            self._max_transaction_wait_time_in_seconds = float(
                max_transaction_wait_time_in_seconds
            )

    def begin_frame(
            self,
            *,
            request: Optional["ChangeControlTransactionRequest"] = None,
            staged: Optional["ChangeControlStagedMutation"] = None,
            capabilities: Optional[Iterable[str]] = None,
            required_capabilities: Optional[Iterable[str]] = None,
    ) -> TransactionSession:
        """
        Begin one root session or join the active root session on the current thread.

        Args:
            request:
                Root admitted request for a new root session.
            staged:
                Root staged payload for a new root session.
            capabilities:
                Granted capabilities for a new root session or required
                capabilities for a nested join.
            required_capabilities:
                Explicit nested-join capability requirement. When provided, this
                is used for same-thread join checks instead of `capabilities`.

        Returns:
            TransactionSession: The active root session for this frame.

        Raises:
            RuntimeError: If nested different-root start is attempted.
            RuntimeError: If strict mode rejects a cross-thread root collision.
        """
        self.check_cleaned()
        current_thread_id = threading.get_ident()
        active = self.get_active_session()
        if active is not None:
            if request is not None and request.request_id != active.request.request_id:
                raise RuntimeError(
                    "Nested root transaction is not allowed while a session is already active on this thread."
                )
            join_requirements = required_capabilities
            if join_requirements is None:
                join_requirements = capabilities
            active.join(
                thread_id=current_thread_id,
                required_capabilities=join_requirements,
            )
            self._get_stack().append(active.request.request_id)
            return active

        if request is None:
            raise ValueError(
                "request must be supplied when starting a new root transaction session."
            )
        if staged is None:
            raise ValueError(
                "staged must be supplied when starting a new root transaction session."
            )

        with self._lock:
            self._wait_for_turn_locked(current_thread_id)
            session = TransactionSession(
                request=request,
                staged=staged,
                owner_thread_id=current_thread_id,
                capabilities=capabilities,
            )
            self._sessions_by_request_id[request.request_id] = session
        self._get_stack().append(request.request_id)
        return session

    def end_frame(self, *, success: bool = True) -> TransactionSession:
        """
        End the current execution frame and finalize the root session if outermost.

        Args:
            success:
                Whether the current frame exited successfully.

        Returns:
            TransactionSession: The session that owned the exiting frame.

        Raises:
            RuntimeError: If no active session exists on the current thread.
            Exception: Propagates commit pipeline failures after abort cleanup.
        """
        self.check_cleaned()
        stack = self._get_stack()
        if not stack:
            raise RuntimeError("No active transaction session exists on this thread.")
        request_id = stack.pop()
        session = self._get_session_or_raise(request_id)
        if not success:
            session.mark_abort_only("Nested transaction frame exited with failure.")
        remaining_depth = session.leave()
        if remaining_depth > 0:
            return session
        try:
            self._finalize_root_session(session)
        finally:
            with self._lock:
                self._sessions_by_request_id.pop(request_id, None)
                self._wait_condition.notify_all()
        return session

    def mark_active_session_abort_only(
            self,
            *,
            reason: str,
            error: Optional[BaseException] = None,
    ) -> None:
        """
        Mark the current active session abort-only on the current thread.
        """
        self.check_cleaned()
        session = self.get_active_session()
        if session is None:
            raise RuntimeError("No active transaction session exists on this thread.")
        session.mark_abort_only(reason, error)

    def get_active_session(self) -> Optional[TransactionSession]:
        """
        Return the active session for the current thread, if any.
        """
        self.check_cleaned()
        stack = self._get_stack()
        if not stack:
            return None
        request_id = stack[-1]
        with self._lock:
            return self._sessions_by_request_id.get(request_id)

    def has_active_session(self) -> bool:
        """
        Return whether the current thread has an active session frame.
        """
        self.check_cleaned()
        return self.get_active_session() is not None

    def describe(self) -> dict:
        """
        Return a detached diagnostic snapshot of mediator state.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "change_control_mode": self._change_control_mode,
                "allow_multiple_root_transactions": (
                    self._allow_multiple_root_transactions
                ),
                "queue_competing_root_transactions": (
                    self._queue_competing_root_transactions
                ),
                "max_transaction_wait_time_in_seconds": (
                    self._max_transaction_wait_time_in_seconds
                ),
                "active_session_count": len(self._sessions_by_request_id),
                "request_ids": tuple(sorted(self._sessions_by_request_id.keys())),
            }

    def _finalize_root_session(self, session: TransactionSession) -> None:
        """
        Commit or abort one root session through the existing orchestrator path.
        """
        if session.status == TransactionSession.STATUS_ABORT_ONLY:
            session.run_abort_pipeline()
            session.mark_aborted()
            self._orchestrator.abort_request(
                session.request.request_id,
                transaction_manager=self._transaction_manager,
                embargo_manager=self._embargo_manager,
            )
            return

        session.mark_committing()
        try:
            session.run_commit_pipeline()
            self._orchestrator.commit_request(
                session.request.request_id,
                transaction_manager=self._transaction_manager,
                embargo_manager=self._embargo_manager,
            )
        except Exception as exc:
            session.mark_abort_only("Commit pipeline failed.", exc)
            session.run_abort_pipeline()
            session.mark_aborted()
            self._orchestrator.abort_request(
                session.request.request_id,
                transaction_manager=self._transaction_manager,
                embargo_manager=self._embargo_manager,
            )
            raise
        else:
            session.mark_committed()

    def _get_stack(self) -> List[str]:
        """
        Return the thread-local request-id stack for the current thread.
        """
        stack = getattr(self._thread_local, "request_stack", None)
        if stack is None:
            stack = []
            self._thread_local.request_stack = stack
        return stack

    def _wait_for_turn_locked(self, thread_id: int) -> None:
        """
        Wait in FIFO order for a root-session slot when queueing is enabled.

        Contract:
            - Returns immediately when no root session is active.
            - Returns immediately when multiple roots are allowed.
            - Preserves strict/warn behavior when queueing is disabled.
            - When queueing is enabled, waits until this thread is the queue
              head and no root sessions remain active.
        """
        if self._allow_multiple_root_transactions or not self._sessions_by_request_id:
            return
        if not self._queue_competing_root_transactions:
            if self._change_control_mode == "strict":
                raise RuntimeError(
                    "Another root transaction session is already active in this frame."
                )
            if self._change_control_mode == "warn":
                warnings.warn(
                    "Another root transaction session is already active in this frame.",
                    RuntimeWarning,
                    stacklevel=2,
                )
            return

        self._pending_root_starts.append(thread_id)
        deadline = time.monotonic() + self._max_transaction_wait_time_in_seconds
        try:
            while True:
                is_head = bool(self._pending_root_starts) and self._pending_root_starts[0] == thread_id
                if is_head and not self._sessions_by_request_id:
                    self._pending_root_starts.pop(0)
                    return
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    self._pending_root_starts = [
                        pending_id
                        for pending_id in self._pending_root_starts
                        if pending_id != thread_id
                    ]
                    raise RuntimeError(
                        "Timed out waiting for the active root transaction session to finish."
                    )
                self._wait_condition.wait(timeout=remaining)
        except Exception:
            self._wait_condition.notify_all()
            raise

    def _get_session_or_raise(self, request_id: str) -> TransactionSession:
        """
        Resolve one session by request id or raise if missing.
        """
        with self._lock:
            session = self._sessions_by_request_id.get(request_id)
        if session is None:
            raise RuntimeError("Active transaction session could not be resolved.")
        return session

    @classmethod
    def _normalize_mode(cls, mode: str) -> str:
        """
        Normalize and validate one mediator mode string.
        """
        if not isinstance(mode, str):
            raise TypeError("change_control_mode must be a string.")
        normalized_mode = mode.strip().lower()
        if normalized_mode not in cls.AVAILABLE_MODES:
            raise ValueError(
                "change_control_mode must be one of "
                f"{sorted(cls.AVAILABLE_MODES)}."
            )
        return normalized_mode
