import threading
from typing import (
    Callable,
    Iterable,
    List,
    Optional,
    Set,
    TYPE_CHECKING,
    ClassVar,
)

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
        ChangeControlStagedMutation,
    )
    from melder.aether.aetheric_frame.dev_ops.devops_identity import (
        DevopsIdentity,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
        ChangeControlTransactionRequest,
    )


class TransactionSession(Cleanable):
    """
    Live transaction session rooted at one admitted change-control request.

    Purpose:
        Represent the mutable runtime ownership state that begins only after a
        request has already been admitted and staged by change-control. The
        request and staged mutation objects remain immutable snapshots; this
        session is the layer that tracks same-thread recursion, abort-only
        poisoning, and local commit/abort callback registration while work is
        actually executing.

    Contract:
        - One session is owned by one root admitted request.
        - One session has exactly one owner thread.
        - Nested same-thread recursion increments local depth instead of
          creating a second root session.
        - Session status moves through:
          `open -> committing -> committed`
          or
          `open -> abort_only -> aborted`.
        - Commit validators run before commit hooks.
        - Abort hooks run before rollback actions, and rollback actions unwind
          in reverse registration order.

    Threading:
        - Internal state mutation is protected by an `RLock`.
        - Same-thread ownership checks are explicit; cross-thread join is
          rejected.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Live transaction session rooted at one admitted change-control "
        "request. Melder kernel machinery: read it to understand the runtime, do not drive it "
        "directly."
    )

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    STATUS_OPEN: ClassVar[str] = "open"
    STATUS_ABORT_ONLY: ClassVar[str] = "abort_only"
    STATUS_COMMITTING: ClassVar[str] = "committing"
    STATUS_COMMITTED: ClassVar[str] = "committed"
    STATUS_ABORTED: ClassVar[str] = "aborted"

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_request",
        "_staged",
        "_submitter_identity",
        "_owner_thread_id",
        "_capabilities",
        "_depth",
        "_status",
        "_failure_reason",
        "_failure_error",
        "_commit_validators",
        "_commit_hooks",
        "_abort_hooks",
        "_rollback_actions",
    ]

    def __init__(
            self,
            *,
            request: "ChangeControlTransactionRequest",
            staged: "ChangeControlStagedMutation",
            submitter_identity: Optional["DevopsIdentity"] = None,
            owner_thread_id: int,
            capabilities: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Initialize one live transaction session.

        Args:
            request:
                Admitted immutable transaction request.
            staged:
                Admitted immutable staged mutation payload.
            submitter_identity:
                Optional identity surface that originated the root session.
            owner_thread_id:
                Thread identifier that owns the root transaction.
            capabilities:
                Optional granted capabilities for nested work performed inside
                this session.

        Raises:
            ValueError: If request or staged is missing, or thread id is invalid.

        Returns:
            None.
        """
        super().__init__()
        if request is None:
            raise ValueError("request must not be None.")
        if staged is None:
            raise ValueError("staged must not be None.")
        if not isinstance(owner_thread_id, int) or owner_thread_id <= 0:
            raise ValueError("owner_thread_id must be a positive integer.")

        self._lock: threading.RLock = threading.RLock()
        self._request: ChangeControlTransactionRequest = request
        self._staged: ChangeControlStagedMutation = staged
        self._submitter_identity: Optional[DevopsIdentity] = submitter_identity
        self._owner_thread_id: int = owner_thread_id
        self._capabilities: Set[str] = set(capabilities or ())
        self._depth: int = 1
        self._status: str = self.STATUS_OPEN
        self._failure_reason: Optional[str] = None
        self._failure_error: Optional[BaseException] = None
        self._commit_validators: List[Callable[[ChangeControlStagedMutation], None]] = []
        self._commit_hooks: List[Callable[[ChangeControlStagedMutation], None]] = []
        self._abort_hooks: List[Callable[[ChangeControlStagedMutation], None]] = []
        self._rollback_actions: List[Callable[[], object]] = []

    def cleanup(self) -> None:
        """
        Idempotently clear local session state.

        Contract:
            - Safe to call multiple times.
            - Does not commit or abort the root request by itself.
            - Drops local callback lists and references after the session is
              already finished or discarded by the caller.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._capabilities.clear()
            self._commit_validators.clear()
            self._commit_hooks.clear()
            self._abort_hooks.clear()
            self._rollback_actions.clear()
            del self._request
            del self._staged
            del self._submitter_identity
            del self._owner_thread_id
            del self._capabilities
            del self._depth
            del self._status
            del self._failure_reason
            del self._failure_error
            del self._commit_validators
            del self._commit_hooks
            del self._abort_hooks
            del self._rollback_actions
        del self._lock

    @property
    def request(self) -> "ChangeControlTransactionRequest":
        """
        Return the immutable root request for this session.
        """
        
        return self._request

    @property
    def staged(self) -> "ChangeControlStagedMutation":
        """
        Return the immutable staged payload for this session.
        """
        
        return self._staged

    @property
    def owner_thread_id(self) -> int:
        """
        Return the owning root thread id for this session.
        """
        
        return self._owner_thread_id

    @property
    def submitter_identity(self) -> Optional["DevopsIdentity"]:
        """
        Return the identity surface that originated this root session.
        """
        
        return self._submitter_identity

    @property
    def depth(self) -> int:
        """
        Return the current same-thread nesting depth for this session.
        """
        
        with self._lock:
            return self._depth

    @property
    def status(self) -> str:
        """
        Return the current session status.
        """
        
        with self._lock:
            return self._status

    @property
    def failure_reason(self) -> Optional[str]:
        """
        Return the current abort-only failure reason, if any.
        """
        
        with self._lock:
            return self._failure_reason

    def grant_capabilities(self, capabilities: Iterable[str]) -> None:
        """
        Add granted capabilities to this session.

        Args:
            capabilities:
                Capability names to add.

        Returns:
            None.
        """
        
        with self._lock:
            self._capabilities.update(capabilities)

    def supports_capabilities(self, required_capabilities: Iterable[str]) -> bool:
        """
        Return whether the session grants the requested capabilities.

        Args:
            required_capabilities:
                Capability names required by the nested operation.

        Returns:
            bool: True when all required capabilities are granted.
        """
        
        required = set(required_capabilities)
        with self._lock:
            return required.issubset(self._capabilities)

    def join(
            self,
            *,
            thread_id: int,
            required_capabilities: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Join this root session from a nested same-thread execution frame.

        Args:
            thread_id:
                Current caller thread id.
            required_capabilities:
                Optional required capabilities for the nested work.

        Raises:
            RuntimeError: If another thread attempts to join or status is closed.
            RuntimeError: If the session lacks required capabilities.

        Returns:
            None.
        """
        
        with self._lock:
            if thread_id != self._owner_thread_id:
                raise RuntimeError(
                    "Only the owner thread may join an active transaction session."
                )
            if self._status not in (self.STATUS_OPEN, self.STATUS_ABORT_ONLY):
                raise RuntimeError(
                    "Cannot join a transaction session that is no longer active."
                )
            if required_capabilities is not None:
                required = set(required_capabilities)
                if not required.issubset(self._capabilities):
                    raise RuntimeError(
                        "Active transaction session does not grant the required capabilities."
                    )
            self._depth += 1

    def leave(self) -> int:
        """
        Leave one nested execution frame and return the remaining depth.

        Returns:
            int: Remaining depth after the current frame exits.

        Raises:
            RuntimeError: If the depth would underflow.
        """
        
        with self._lock:
            if self._depth <= 0:
                raise RuntimeError("Transaction session depth underflow.")
            self._depth -= 1
            return self._depth

    def mark_abort_only(
            self,
            reason: str,
            error: Optional[BaseException] = None,
    ) -> None:
        """
        Poison the session so the root exit must abort instead of commit.

        Args:
            reason:
                Human-readable reason for the abort-only transition.
            error:
                Optional triggering exception to retain for diagnostics.

        Returns:
            None.
        """
        
        with self._lock:
            self._status = self.STATUS_ABORT_ONLY
            self._failure_reason = reason
            self._failure_error = error

    def mark_committing(self) -> None:
        """
        Mark the session as entering the root commit path.

        Returns:
            None.
        """
        
        with self._lock:
            self._status = self.STATUS_COMMITTING

    def mark_committed(self) -> None:
        """
        Mark the session as successfully committed.

        Returns:
            None.
        """
        
        with self._lock:
            self._status = self.STATUS_COMMITTED

    def mark_aborted(self) -> None:
        """
        Mark the session as fully aborted.

        Returns:
            None.
        """
        
        with self._lock:
            self._status = self.STATUS_ABORTED

    def register_commit_validator(
            self,
            fn: Callable[["ChangeControlStagedMutation"], None],
    ) -> None:
        """
        Register one session-local commit validator.

        Args:
            fn:
                Callable invoked before commit hooks.

        Returns:
            None.
        """
        
        with self._lock:
            self._commit_validators.append(fn)

    def register_commit_hook(
            self,
            fn: Callable[["ChangeControlStagedMutation"], None],
    ) -> None:
        """
        Register one session-local commit hook.

        Args:
            fn:
                Callable invoked after successful validators.

        Returns:
            None.
        """
        
        with self._lock:
            self._commit_hooks.append(fn)

    def register_abort_hook(
            self,
            fn: Callable[["ChangeControlStagedMutation"], None],
    ) -> None:
        """
        Register one session-local abort hook.

        Args:
            fn:
                Callable invoked during abort finalization.

        Returns:
            None.
        """
        
        with self._lock:
            self._abort_hooks.append(fn)

    def register_rollback_action(
            self,
            fn: Callable[[], object],
    ) -> None:
        """
        Register one best-effort rollback action for this session.

        Args:
            fn:
                Callable invoked in reverse order during abort cleanup.

        Returns:
            None.
        """
        
        with self._lock:
            self._rollback_actions.append(fn)

    def run_commit_pipeline(self) -> None:
        """
        Run session-local validators and commit hooks in stable order.

        Raises:
            Exception: Propagates the first validator/hook failure.

        Returns:
            None.
        """
        
        validators: List[Callable[[ChangeControlStagedMutation], None]]
        hooks: List[Callable[[ChangeControlStagedMutation], None]]
        with self._lock:
            validators = list(self._commit_validators)
            hooks = list(self._commit_hooks)
        for validator in validators:
            validator(self._staged)
        for hook in hooks:
            hook(self._staged)

    def run_abort_pipeline(self) -> List[BaseException]:
        """
        Run session-local abort hooks and rollback actions.

        Returns:
            List[BaseException]: Exceptions raised by local abort/rollback work.
        """
        
        hooks: List[Callable[[ChangeControlStagedMutation], None]]
        rollbacks: List[Callable[[], object]]
        with self._lock:
            hooks = list(self._abort_hooks)
            rollbacks = list(self._rollback_actions)
        failures: List[BaseException] = []
        for hook in hooks:
            try:
                hook(self._staged)
            except BaseException as exc:
                failures.append(exc)
        for rollback in reversed(rollbacks):
            try:
                rollback()
            except BaseException as exc:
                failures.append(exc)
        return failures

    def describe(self) -> dict:
        """
        Return a detached diagnostic snapshot of the session state.
        """
        
        with self._lock:
            return {
                "request_id": self._request.request_id,
                "request_type": self._request.request_type,
                "owner_thread_id": self._owner_thread_id,
                "submitter_identity": (
                    None
                    if self._submitter_identity is None
                    else self._submitter_identity.describe()
                ),
                "depth": self._depth,
                "status": self._status,
                "capabilities": tuple(sorted(self._capabilities)),
                "failure_reason": self._failure_reason,
            }
