from threading import RLock
from typing import Callable, Dict, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlAdmissionResult,
    ChangeControlTransactionRequest,
)
from melder.aether.dev_ops.change_control_manager.orchestrator.staged_mutation import (
    ChangeControlStagedMutation,
)
from melder.aether.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.dev_ops.change_control_manager.conflict_manager.conflict_manager import (
    ChangeControlConflictManager,
)
from melder.aether.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
    ChangeControlEmbargoManager,
)


class ChangeControlOrchestrator(Cleanable):
    """
    Serialized admission gate for change-control requests.

    Purpose:
        Centralize admission decisions under a single lock to prevent race
        conditions between concurrent mutation requests.
    Contract:
        - Admission is serialized under the orchestrator lock.
        - Accepted requests are registered as in-flight.
        - Rejected requests return evidence (conflict/embargo).
        - Optional commit/abort hooks are invoked outside the lock.
    Args:
        None.
    Returns:
        None.
    Raises:
        None.
    Threading:
        Uses an internal RLock to serialize admission/commit/abort paths.
    Lifecycle:
        cleanup() is idempotent and nulls internal references.
    """
    __melder_internal__ = _mrg.sentinel
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
            Allocate the admission lock used for serialized decisions.
        Contract:
            - No mutable state beyond the lock.
        Returns:
            None.
        Threading:
            Safe to publish after initialization.
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
            Mark the orchestrator as cleaned and drop the lock reference.
        Contract:
            - Safe to call multiple times.
        Returns:
            None.
        Threading:
            Acquires the internal lock while mutating state.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._staged is not None:
                self._staged.clear()
                self._staged = None
            self._commit_validator = None
            self._commit_hook = None
            self._abort_hook = None
        self._lock = None

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
        self.check_cleaned()
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
        self.check_cleaned()
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
        self.check_cleaned()
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
        self.check_cleaned()
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
        self.check_cleaned()
        with self._lock:
            return tuple(self._staged.values())

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
        self.check_cleaned()
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
            Decide whether a request can proceed based on conflicts/embargoes.
        Contract:
            - Admission is serialized under the orchestrator lock.
            - Successful admission registers the request as in-flight.
            - Implicit embargo hooks are invoked on admission.
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
        self.check_cleaned()
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
        Release implicit embargoes and remove request from in-flight registry.

        Purpose:
            Finalize a request's admission lifecycle after successful execution.
        Contract:
            - No effect if request_id is not in-flight.
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
        self.check_cleaned()
        request: Optional[ChangeControlTransactionRequest] = None
        staged: Optional[ChangeControlStagedMutation] = None
        commit_validator: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        commit_hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        abort_hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        with self._lock:
            request = transaction_manager.get_in_flight(request_id)
            if request is None:
                return
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
                if request is None:
                    return
                embargo_manager.release_implicit_embargoes(request)
                transaction_manager.remove_in_flight(request_id)
                if self._staged is not None and request_id in self._staged:
                    del self._staged[request_id]
            raise

        with self._lock:
            request = transaction_manager.get_in_flight(request_id)
            if request is None:
                return
            embargo_manager.release_implicit_embargoes(request)
            transaction_manager.remove_in_flight(request_id)
            if self._staged is not None and request_id in self._staged:
                del self._staged[request_id]

    def abort_request(
            self,
            request_id: str,
            *,
            transaction_manager: ChangeControlTransactionManager,
            embargo_manager: ChangeControlEmbargoManager,
    ) -> None:
        """
        Abort a request (same cleanup as commit for now).

        Purpose:
            Ensure aborted requests release implicit embargoes and in-flight state.
        Contract:
            - Uses the same cleanup path as commit for scaffolding.
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
        self.check_cleaned()
        staged: Optional[ChangeControlStagedMutation] = None
        abort_hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        with self._lock:
            if self._staged is not None:
                staged = self._staged.get(request_id)
            abort_hook = self._abort_hook
        if staged is not None and abort_hook is not None:
            try:
                abort_hook(staged)
            except Exception:
                pass
        with self._lock:
            request = transaction_manager.get_in_flight(request_id)
            if request is None:
                return
            embargo_manager.release_implicit_embargoes(request)
            transaction_manager.remove_in_flight(request_id)
            if self._staged is not None and request_id in self._staged:
                del self._staged[request_id]
