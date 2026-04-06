from threading import RLock
from typing import Any, Callable, Dict, Iterable, Optional, Tuple

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
    Serialized admission and lifecycle gate for change-control requests.

    This object is the narrow coordination point between:
    - admission checks
    - staged mutation state
    - in-flight transaction bookkeeping
    - implicit embargo open/release
    - commit/abort callback ordering

    Contract:
    - Admission, commit, and abort sequencing are serialized under the
      orchestrator lock.
    - Accepted requests become staged and in-flight before the call returns.
    - Rejected requests return explicit conflict/embargo evidence.
    - Validator and commit/abort hooks are snapshotted under lock and run
      outside it.
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

        Contract:
        - Starts with an empty staged-request registry.
        - Owns one admission lock and three optional lifecycle hooks.
        """
        super().__init__()
        self._lock: RLock = RLock()
        self._staged: Dict[str, ChangeControlStagedMutation] = {}
        self._commit_validator: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        self._commit_hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        self._abort_hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None

    def cleanup(self) -> None:
        """
        Finalize the orchestrator and clear staged request state.

        Contract:
        - Idempotent cleanup.
        - Clears staged request state and drops registered hook references
          before releasing the lock.
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
        Register the pre-commit validator hook.

        Passing `None` disables the validator. When present, the hook runs
        before the commit hook during `commit_request()`.
        """
        self.check_cleaned()
        with self._lock:
            self._commit_validator = fn

    def set_commit_hook(
            self,
            fn: Optional[Callable[[ChangeControlStagedMutation], None]],
    ) -> None:
        """
        Register the commit-side effect hook.

        Passing `None` disables the hook. When present, it runs after the
        commit validator and before final in-flight/embargo cleanup.
        """
        self.check_cleaned()
        with self._lock:
            self._commit_hook = fn

    def set_abort_hook(
            self,
            fn: Optional[Callable[[ChangeControlStagedMutation], None]],
    ) -> None:
        """
        Register the abort-side effect hook.

        Passing `None` disables the hook. When present, it runs during
        `abort_request()` and on commit failure before staged state is cleaned
        up.
        """
        self.check_cleaned()
        with self._lock:
            self._abort_hook = fn

    def get_staged(self, request_id: str) -> Optional[ChangeControlStagedMutation]:
        """
        Return the staged mutation record for one request id.

        Returns `None` when no staged record exists for that id.
        """
        self.check_cleaned()
        if not request_id:
            return None
        with self._lock:
            return self._staged.get(request_id)

    def list_staged(self) -> Tuple[ChangeControlStagedMutation, ...]:
        """
        Return a snapshot of all staged mutation records.
        """
        self.check_cleaned()
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

        This is the staged-state refresh path for metadata discovered after
        admission. Only supplied fields are updated; `None` means "leave the
        existing value alone."

        Returns:
            bool: `True` when the staged record existed and was updated,
            otherwise `False`.
        """
        self.check_cleaned()
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
        Create or replace the staged mutation record for one admitted request.

        Caller contract:
        - the orchestrator lock must already be held
        - staging happens only after admission succeeds
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

        This is the serialized admission gate:
        - detect conflicts against in-flight requests
        - detect active embargoes against the incoming scope
        - if clear, register the request as in-flight, apply implicit embargoes,
          and stage its mutation metadata

        Returns:
            ChangeControlAdmissionResult: Admission decision plus any
            conflict/embargo evidence when rejected.
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
        Finalize a successfully executed request.

        Commit sequencing:
        - snapshot staged request + hooks
        - run validator, then commit hook, outside the lock
        - if either fails, run abort hook best-effort and still clean up staged,
          embargo, and in-flight state
        - otherwise release embargoes and remove the request from staged and
          in-flight registries
        """
        self.check_cleaned()
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
        Abort an admitted request and release its staged admission state.

        The cleanup path mirrors commit in the parts that matter for registry
        hygiene: staged state, in-flight tracking, and implicit embargoes are
        all released before the method returns.
        """
        self.check_cleaned()
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
