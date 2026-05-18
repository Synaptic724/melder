from typing import Any, Callable, Dict, Iterable, Optional, Protocol, Tuple, Union, runtime_checkable
from threading import RLock
from melder.aether.dev_ops.change_control_manager.orchestrator.staged_mutation import ChangeControlStagedMutation
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlAdmissionResult,
    ChangeControlTransactionRequest,
)
from melder.utilities.interfaces.ichangecontrolorchestrator import IChangeControlOrchestrator
from melder.utilities.interfaces.ichangecontroltransactionmanager import IChangeControlTransactionManager
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.ispellindex import ISpellIndex
from melder.utilities.interfaces.ispellsystemstates import ISpellSystemStates

@runtime_checkable
class IChangeControlManager(ICleanable, Protocol):
    """
    Protocol for the High-level change/release tracker for an Aetheric Frame.

    This is *not* the hot-path resolution guard. It is the DevOps-facing layer
    that knows about:
      - which spell lineages (SpellIndex.id) have pending changes or promotions,
      - lightweight, structured metadata about those changes.

    It does not apply changes or run policies itself; it's a registry that
    higher-level tools (AI agents, DevOps flows, IncidentManager) can inspect
    and update.
    """
    _lock: RLock
    _spell_system_states: ISpellSystemStates

    # spell_index_id -> Dict[str, Any]
    _pending_changes: 'Dict[str, Dict[str, Any]]'
    _change_control_enabled: bool

    # ----------------------------------------------------------------------
    # Change-control admission controls
    # ----------------------------------------------------------------------
    def enable_change_control(self) -> None:
        """
        Public API

        Enable change-control admission for this frame.

        Purpose:
            Allow the orchestrator admission gate to evaluate requests.
        Contract:
            - When enabled, admission checks apply conflict/embargo rules.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def disable_change_control(self) -> None:
        """
        Public API

        Disable change-control admission for this frame.

        Purpose:
            Allow transactions to proceed without conflict/embargo gating.
        Contract:
            - When disabled, admission returns accepted without conflict checks.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def is_change_control_enabled(self) -> bool:
        """
        Public API

        Return whether change-control admission is enabled.

        Returns:
            bool: True if admission gating is enabled.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def set_audit_logger(
            self,
            fn: Optional[Callable[[ChangeControlTransactionRequest], None]],
    ) -> None:
        """
        Public API

        Register an audit logger for admitted change-control requests.

        Args:
            fn:
                Callable that receives the admitted request, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def set_commit_validator(
            self,
            fn: Optional[Callable[[ChangeControlStagedMutation], None]],
    ) -> None:
        """
        Public API

        Register a commit validator hook for admitted requests.

        Args:
            fn:
                Callable that validates a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def set_structural_validator(
            self,
            fn: Optional[Callable[[ChangeControlStagedMutation], None]],
    ) -> None:
        """
        Public API

        Register a structural validation hook for admitted requests.

        Purpose:
            Provide a hook for running structural phase validation before commit.
        Contract:
            - Passing None disables the hook.
            - Hook is invoked before the commit validator.
        Args:
            fn:
                Callable that validates a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def set_commit_hook(
            self,
            fn: Optional[Callable[[ChangeControlStagedMutation], None]],
    ) -> None:
        """
        Public API

        Register a commit hook for admitted requests.

        Args:
            fn:
                Callable invoked with a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def set_dirty_marker(
            self,
            fn: Optional[Callable[[ChangeControlStagedMutation], None]],
    ) -> None:
        """
        Public API

        Register a commit-time dirty-marker hook.

        Purpose:
            Provide a hook for marking dependency state dirty after commit.
        Contract:
            - Passing None disables dirty marking.
            - Hook is invoked before the commit hook.
        Args:
            fn:
                Callable invoked with a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def set_abort_hook(
            self,
            fn: Optional[Callable[['ChangeControlStagedMutation'], None]],
    ) -> None:
        """
        Public API

        Register an abort hook for admitted requests.

        Args:
            fn:
                Callable invoked with a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def admit_request(
            self,
            request: ChangeControlTransactionRequest,
    ) -> ChangeControlAdmissionResult:
        """
        Public API

        Admit a transaction request through the change-control gate.

        Args:
            request:
                Transaction request to admit.
        Returns:
            ChangeControlAdmissionResult:
                Admission decision with evidence for rejection.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def update_staged_request(
            self,
            request_id: str,
            *,
            scope_keys: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Public API

        Update staged mutation metadata for an admitted request.

        Purpose:
            Allow callers to refresh staged metadata discovered after admission.
        Contract:
            - Returns False if the request is not staged.
            - Updates only supplied fields; None keeps existing values.
            - Metadata merges into the staged record when provided.
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
            bool: True if the staged record was updated.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def commit_request(self, request_id: str) -> None:
        """
        Public API

        Commit an in-flight request and release implicit embargoes.

        Args:
            request_id:
                Request id to finalize.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...

    def abort_request(self, request_id: str) -> None:
        """
        Public API

        Abort an in-flight request and release implicit embargoes.

        Args:
            request_id:
                Request id to abort.
        Returns:
            None.
        Raises:
            RuntimeError: If the manager has been cleaned.
        """
        ...
    # ----------------------------------------------------------------------
    # Registration / updates
    # ----------------------------------------------------------------------
    def register_pending_change(
            self,
            spell_index: ISpellIndex,
            reason: str,
            metadata: Optional[
                Union[Dict[str, Any], 'Dict[str, Any]']
            ] = None,
    ) -> None:
        """
        Record that a given lineage has a pending change (mutation candidate,
        promotion proposal, config swap, etc.).

        This is *bookkeeping only* - it does not apply the change, it just
        surfaces it for DevOps / AI tooling.

        Args:
            spell_index:
                The SpellIndex for the lineage we're tracking.
            reason:
                Short, machine-/human-readable reason code
                (e.g. "mutation_candidate", "rebinding", "config_change").
            metadata:
                Optional free-form metadata.
        """
        ...

    # ----------------------------------------------------------------------
    # Introspection
    # ----------------------------------------------------------------------
    def get_pending_change(
            self,
            spell_index_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a *snapshot* of the pending-change metadata for a specific lineage.

        Returns:
            A plain dict copy of the inner Dict metadata if present,
            or None if no pending change exists for that lineage.
        """
        ...

    def list_pending_changes(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a snapshot of all pending changes:

            {
              spell_index_id: { ...metadata... },
              ...
            }

        This is intended for DevOps / AI tooling - not for hot-path use.
        """
        ...

    # ----------------------------------------------------------------------
    # Clearing
    # ----------------------------------------------------------------------
    def clear_pending_change(self, spell_index_id: str) -> None:
        """
        Remove the pending-change entry for the given lineage, if any.

        This is typically called after a release is either:
          - successfully applied, or
          - explicitly cancelled/abandoned.
        """
        ...

    def is_root_dirty(self, conduit_id: str, root_id: str) -> bool:
        """
        Return whether the supplied root is currently marked dirty for a conduit.

        Args:
            conduit_id: Conduit whose dirty-root state is being queried.
            root_id: Root spell id being checked.

        Returns:
            bool: True when the root is currently dirty for the conduit.
        """
        ...

    def transaction_manager(self) -> IChangeControlTransactionManager:
        """
        Return the owned transaction-manager surface.
        """
        ...

    def orchestrator(self) -> IChangeControlOrchestrator:
        """
        Return the owned staged-mutation orchestrator surface.
        """
        ...

    def has_registered_revalidators(self) -> bool:
        """
        Return whether any conduit revalidator is currently registered.

        Returns:
            bool: True when at least one conduit has a registered revalidator.
        """
        ...
