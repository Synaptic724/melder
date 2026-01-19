from threading import RLock

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlAdmissionResult,
    ChangeControlTransactionRequest,
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
        self._lock = None

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
            embargoes = embargo_manager.find_embargoes(request.scope_keys)
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
        with self._lock:
            request = transaction_manager.get_in_flight(request_id)
            if request is None:
                return
            embargo_manager.release_implicit_embargoes(request)
            transaction_manager.remove_in_flight(request_id)

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
        self.commit_request(
            request_id,
            transaction_manager=transaction_manager,
            embargo_manager=embargo_manager,
        )
