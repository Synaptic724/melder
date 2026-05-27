from threading import RLock
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Optional,
    Tuple,
    TYPE_CHECKING,
    ClassVar,
)

# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlAdmissionResult,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
    ChangeControlStagedMutation,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
        ChangeControlTransactionRequest,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
        ChangeControlTransactionManager,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.conflict_manager.conflict_manager import (
        ChangeControlConflictManager,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
        ChangeControlEmbargoManager,
    )


class ChangeControlOrchestrator(Cleanable):
    """
    Serialized control-plane coordinator for change-control requests.

    Purpose:
        Centralize admission, staging, and commit/abort cleanup under one lock
        so concurrent mutation requests cannot observe inconsistent in-flight or
        embargo state.
    Contract:
        - Admission decisions are serialized under the orchestrator lock.
        - Accepted requests are staged and registered as in-flight before the
          lock is released.
        - Rejected requests return explicit conflict/embargo evidence and do
          not mutate in-flight state.
        - Commit and abort both unwind the same admission-state resources, with
          optional hooks running outside the lock.
    Threading:
        Uses an internal RLock to serialize admission/commit/abort paths.
    Lifecycle:
        cleanup() is idempotent and clears only orchestrator-owned staged state
        and hook references.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_staged",
        "_commit_validator",
        "_commit_hook",
        "_abort_hook",
    ]

    def __init__(self) -> None:
        """
        Initialize the orchestrator.

        Purpose:
            Allocate the lock and staged-request registry used for serialized
            admission and cleanup.
        Contract:
            - Starts with no staged requests and no hooks.
            - Safe to publish immediately after construction.
        """
        super().__init__()
        self._lock: RLock = RLock()
        self._staged: Dict[str, ChangeControlStagedMutation] = {}
        self._commit_validator: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        self._commit_hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        self._abort_hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None

    def cleanup(self) -> None:
        """
        Idempotent cleanup for the orchestrator.

        Purpose:
            Clear staged request bookkeeping and hook references owned by this
            orchestrator.
        Contract:
            - Safe to call multiple times.
            - Does not attempt to finalize external transaction or embargo
              state; callers must not use cleanup as a lifecycle substitute for
              `commit_request(...)` or `abort_request(...)`.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._staged is not None:
                self._staged.clear()
            del self._staged

            del self._commit_validator
            del self._commit_hook
            del self._abort_hook
        del self._lock

    def set_commit_validator(
            self,
            fn: Optional[Callable[[ChangeControlStagedMutation], None]],
    ) -> None:
        """
        Register a commit validator hook.

        Purpose:
            Provide a pre-commit validation hook (e.g., structural phase checks).
        Contract:
            - Passing None disables validation.
            - Hook is invoked outside the orchestrator lock.
        Args:
            fn:
                Callable that validates the staged mutation.
        Returns:
            None.
        Raises:
            RuntimeError: If the orchestrator has been cleaned.
        Threading:
            Acquires the internal lock while updating the hook reference.
        """
        
        with self._lock:
            self._commit_validator = fn

    def set_commit_hook(
            self,
            fn: Optional[Callable[[ChangeControlStagedMutation], None]],
    ) -> None:
        """
        Register a commit hook.

        Purpose:
            Provide a post-validation hook for commit-time side effects.
        Contract:
            - Passing None disables the hook.
            - Hook is invoked outside the orchestrator lock.
        Args:
            fn:
                Callable invoked before commit finalization.
        Returns:
            None.
        Raises:
            RuntimeError: If the orchestrator has been cleaned.
        Threading:
            Acquires the internal lock while updating the hook reference.
        """
        
        with self._lock:
            self._commit_hook = fn

    def set_abort_hook(
            self,
            fn: Optional[Callable[[ChangeControlStagedMutation], None]],
    ) -> None:
        """
        Register an abort hook.

        Purpose:
            Provide a hook for abort-time cleanup side effects.
        Contract:
            - Passing None disables the hook.
            - Hook is invoked outside the orchestrator lock.
        Args:
            fn:
                Callable invoked before abort finalization.
        Returns:
            None.
        Raises:
            RuntimeError: If the orchestrator has been cleaned.
        Threading:
            Acquires the internal lock while updating the hook reference.
        """
        
        with self._lock:
            self._abort_hook = fn

    def get_staged(self, request_id: str) -> Optional[ChangeControlStagedMutation]:
        """
        Return a staged mutation record for a request id.

        Purpose:
            Provide access to staged metadata for diagnostics and tests.
        Contract:
            - Returns None if no staged record exists.
        Args:
            request_id:
                Request identifier to look up.
        Returns:
            Optional[ChangeControlStagedMutation]:
                Staged record if present.
        Raises:
            RuntimeError: If the orchestrator has been cleaned.
        Threading:
            Acquires the internal lock while reading state.
        """
        
        if not request_id:
            return None
        with self._lock:
            return self._staged.get(request_id)

    def list_staged(self) -> Tuple[ChangeControlStagedMutation, ...]:
        """
        Return a snapshot of staged mutation records.

        Purpose:
            Provide a stable snapshot of staged requests for diagnostics.
        Contract:
            - Returns a tuple snapshot (may be empty).
        Returns:
            Tuple[ChangeControlStagedMutation, ...]:
                Snapshot of staged mutation records.
        Raises:
            RuntimeError: If the orchestrator has been cleaned.
        Threading:
            Acquires the internal lock while copying state.
        """
        
        with self._lock:
            return tuple(self._staged.values())

    def update_staged(
            self,
            request_id: str,
            *,
            scope_keys: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update staged mutation metadata for an admitted request.

        Purpose:
            Allow callers to refresh staged metadata discovered after admission
            (e.g., binding keys or contract keys discovered during a transaction).
        Contract:
            - Returns False when no staged record exists for the request id.
            - Updates only the supplied fields; None keeps existing values.
            - Metadata is merged into the staged record when provided.
        Args:
            request_id:
                Request identifier to update.
            scope_keys:
                Optional updated scope keys for the staged mutation.
            binding_keys:
                Optional updated binding keys for the staged mutation.
            contract_keys:
                Optional updated contract keys for the staged mutation.
            metadata:
                Optional metadata to merge into the staged record.
        Returns:
            bool:
                True if the staged record was updated, False otherwise.
        Raises:
            RuntimeError: If the orchestrator has been cleaned.
        Threading:
            Acquires the admission lock while updating staged metadata.
        """
        
        if not request_id:
            return False
        normalized_scope_keys = (
            tuple(scope_keys) if scope_keys is not None else None
        )
        normalized_binding_keys = (
            tuple(binding_keys) if binding_keys is not None else None
        )
        normalized_contract_keys = (
            tuple(contract_keys) if contract_keys is not None else None
        )
        with self._lock:
            staged = self._staged.get(request_id) if self._staged is not None else None
            if staged is None:
                return False
            self._staged[request_id] = staged.with_updates(
                scope_keys=normalized_scope_keys,
                binding_keys=normalized_binding_keys,
                contract_keys=normalized_contract_keys,
                metadata=metadata,
            )
            return True

    def _stage_request(
            self,
            request: ChangeControlTransactionRequest,
            scope_keys: Tuple[str, ...],
    ) -> None:
        """
        Internal

        Stage a mutation record for the admitted request.

        Purpose:
            Capture staged metadata for later commit/abort cleanup.
        Contract:
            - Overwrites any existing staged record for the request id.
        Args:
            request:
                Admitted transaction request.
            scope_keys:
                Normalized scope keys for staging/embargo checks.
        Returns:
            None.
        Raises:
            RuntimeError: If the orchestrator has been cleaned.
        Threading:
            Caller must hold the orchestrator lock.
        """
        
        self._staged[request.request_id] = ChangeControlStagedMutation.from_request(
            request_id=request.request_id,
            request_type=request.request_type,
            initiator_conduit_id=request.initiator_conduit_id,
            spellbook_id=request.spellbook_id,
            conduit_ids=request.conduit_ids,
            scope_keys=scope_keys,
            binding_keys=request.binding_keys,
            contract_keys=request.contract_keys,
            metadata=request.metadata,
        )

    def admit_request(
            self,
            request: ChangeControlTransactionRequest,
            *,
            transaction_manager: ChangeControlTransactionManager,
            conflict_manager: ChangeControlConflictManager,
            embargo_manager: ChangeControlEmbargoManager,
    ) -> ChangeControlAdmissionResult:
        """
        Serialize admission and return a decision for the supplied request.

        Purpose:
            Decide whether a request can enter execution based on current
            conflicts and embargoes, then stage the accepted request for later
            commit or abort.
        Contract:
            - Admission is serialized under the orchestrator lock.
            - Rejected requests return explicit rejection evidence and leave the
              transaction manager untouched.
            - Successful admission registers the request as in-flight, applies
              implicit embargoes, and stages the request before returning.
        Args:
            request:
                Transaction request to admit.
            transaction_manager:
                In-flight registry manager.
            conflict_manager:
                Scope-overlap evaluator.
            embargo_manager:
                Embargo registry for gating.
        Returns:
            ChangeControlAdmissionResult:
                Admission decision with evidence for rejection.
        Raises:
            RuntimeError: If the orchestrator has been cleaned.
        Threading:
            Acquires the admission lock for the entire decision path.
        """
        
        with self._lock:
            conflicts = conflict_manager.find_conflicts(
                request,
                transaction_manager.list_in_flight(),
            )
            embargo_scope_keys = embargo_manager.collect_scope_keys(request)
            embargoes = embargo_manager.find_embargoes(embargo_scope_keys)
            if conflicts or embargoes:
                reasons = []
                if conflicts:
                    reasons.append("conflict")
                if embargoes:
                    reasons.append("embargo")
                return ChangeControlAdmissionResult(
                    admitted=False,
                    reasons=tuple(reasons),
                    conflicts=tuple(conflicts),
                    embargoes=tuple(embargoes),
                )

            transaction_manager.add_in_flight(request)
            embargo_manager.apply_implicit_embargoes(request)
            self._stage_request(request, embargo_scope_keys)
            return ChangeControlAdmissionResult(admitted=True)

    def commit_request(
            self,
            request_id: str,
            *,
            transaction_manager: ChangeControlTransactionManager,
            embargo_manager: ChangeControlEmbargoManager,
    ) -> None:
        """
        Finalize a successfully executed admitted request.

        Purpose:
            Run commit-time validation/hooks, then release the admission state
            created by `admit_request(...)`.
        Contract:
            - No effect if `request_id` is not currently in flight.
            - Commit validation and commit hooks run outside the lock.
            - On hook failure, the abort hook is attempted and the same
              in-flight/embargo cleanup still runs before the exception
              propagates.
        Args:
            request_id:
                Request id to finalize.
            transaction_manager:
                In-flight registry manager.
            embargo_manager:
                Embargo registry for implicit release.
        Returns:
            None.
        Raises:
            RuntimeError: If the orchestrator has been cleaned.
        Threading:
            Acquires the admission lock while finalizing.
        """
        
        request: Optional[ChangeControlTransactionRequest] = None
        cleanup_request: Optional[ChangeControlTransactionRequest] = None
        staged: Optional[ChangeControlStagedMutation] = None
        commit_validator: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        commit_hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        abort_hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        with self._lock:
            request = transaction_manager.get_in_flight(request_id)
            if request is None:
                return
            cleanup_request = request
            staged = self._staged.get(request_id) if self._staged is not None else None
            commit_validator = self._commit_validator
            commit_hook = self._commit_hook
            abort_hook = self._abort_hook

        try:
            if staged is not None and commit_validator is not None:
                commit_validator(staged)
            if staged is not None and commit_hook is not None:
                commit_hook(staged)
        except Exception:
            if staged is not None and abort_hook is not None:
                try:
                    abort_hook(staged)
                except Exception:
                    pass
            with self._lock:
                request = transaction_manager.get_in_flight(request_id)
                if request is not None:
                    cleanup_request = request
                embargo_manager.release_implicit_embargoes(cleanup_request)
                transaction_manager.remove_in_flight(request_id)
                if self._staged is not None:
                    self._staged.pop(request_id, None)
            raise

        with self._lock:
            request = transaction_manager.get_in_flight(request_id)
            if request is not None:
                cleanup_request = request
            embargo_manager.release_implicit_embargoes(cleanup_request)
            transaction_manager.remove_in_flight(request_id)
            if self._staged is not None:
                self._staged.pop(request_id, None)

    def abort_request(
            self,
            request_id: str,
            *,
            transaction_manager: ChangeControlTransactionManager,
            embargo_manager: ChangeControlEmbargoManager,
    ) -> None:
        """
        Abort an admitted request and unwind its admission state.

        Purpose:
            Ensure aborted requests release staged, embargo, and in-flight state
            even when the mutation never reaches successful commit.
        Contract:
            - Attempts the abort hook outside the lock when staged data exists.
            - Releases implicit embargoes and removes the request from the
              in-flight registry.
            - Uses the same resource-unwind path as commit, but without running
              commit validation or commit hooks.
        Args:
            request_id:
                Request id to abort.
            transaction_manager:
                In-flight registry manager.
            embargo_manager:
                Embargo registry for implicit release.
        Returns:
            None.
        Raises:
            RuntimeError: If the orchestrator has been cleaned.
        Threading:
            Acquires the admission lock while finalizing.
        """
        
        request_snapshot: Optional[ChangeControlTransactionRequest] = None
        staged: Optional[ChangeControlStagedMutation] = None
        abort_hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        with self._lock:
            if self._staged is not None:
                staged = self._staged.get(request_id)
            abort_hook = self._abort_hook
            request_snapshot = transaction_manager.get_in_flight(request_id)
        if staged is not None and abort_hook is not None:
            try:
                abort_hook(staged)
            except Exception:
                pass
        with self._lock:
            request = transaction_manager.get_in_flight(request_id)
            cleanup_request = request if request is not None else request_snapshot
            if cleanup_request is None:
                return
            embargo_manager.release_implicit_embargoes(cleanup_request)
            transaction_manager.remove_in_flight(request_id)
            if self._staged is not None:
                self._staged.pop(request_id, None)
