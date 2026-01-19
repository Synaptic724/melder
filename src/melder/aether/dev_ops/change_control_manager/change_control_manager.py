from threading import RLock
from typing import Any, Callable, Dict, Optional, Set, Union

from melder.aether.dev_ops.change_control_manager.conflict_manager.conflict_manager import (
    ChangeControlConflictManager,
)
from melder.aether.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
    ChangeControlEmbargoManager,
    ChangeControlEmbargoRecord,
)
from melder.aether.dev_ops.change_control_manager.orchestrator.orchestrator import (
    ChangeControlOrchestrator,
)
from melder.aether.dev_ops.change_control_manager.orchestrator.staged_mutation import (
    ChangeControlStagedMutation,
)
from melder.aether.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlAdmissionResult,
    ChangeControlTransactionRequest,
    ChangeTransactionType,
)
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import IChangeControlManager, ISpellIndex
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

__all__ = [
    "ChangeTransactionType",
    "ChangeControlTransactionRequest",
    "ChangeControlAdmissionResult",
    "ChangeControlEmbargoRecord",
    "ChangeControlTransactionManager",
    "ChangeControlConflictManager",
    "ChangeControlEmbargoManager",
    "ChangeControlOrchestrator",
    "ChangeControlManager",
]

class ChangeControlManager(Cleanable, IChangeControlManager):
    """
    Change-control registry for an Aetheric Frame.

    Purpose:
        Provide DevOps-facing bookkeeping for spell lineages, dirty roots, and
        change-control admission helpers. This is not a hot-path resolver.
    Contract:
        - Tracks pending change metadata by SpellIndex id.
        - Tracks component-of and dirty root state for targeted revalidation.
        - Provides accessors for change-control scaffolding managers.
        - Does not own SpellSystemStates lifecycle.
    Args:
        spell_system_states:
            Spell system state container for this frame.
    Returns:
        None.
    Raises:
        ValueError: If spell_system_states is None.
    Ownership:
        Owns internal registries and the change-control manager instances.
    Threading:
        All state mutations are guarded by an internal RLock.
    Lifecycle:
        cleanup() is idempotent and nulls internal references.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_system_states",
        "_pending_changes",
        "_component_of",
        "_dirty_spells",
        "_dirty_roots",
        "_monitor_active",
        "_revalidate_fn",
        "_change_control_enabled",
        "_transaction_manager",
        "_conflict_manager",
        "_embargo_manager",
        "_orchestrator",
        "_commit_validator",
        "_commit_hook",
        "_abort_hook",
        "_structural_validator",
        "_dirty_marker",
    ]

    def __init__(self, spell_system_states: "SpellSystemStates") -> None:
        """
        Initialize a ChangeControlManager.

        Purpose:
            Seed change-control registries for the supplied spell system state.
        Contract:
            - Requires a non-null SpellSystemStates reference.
            - Creates per-manager scaffolding components.
        Args:
            spell_system_states:
                Spell system state container for this frame.
        Raises:
            ValueError: If spell_system_states is None.
        Threading:
            Safe to publish after initialization; internal lock guards state.
        """
        if spell_system_states is None:
            raise ValueError("spell_system_states cannot be None")

        Cleanable.__init__(self)

        self._lock: RLock = RLock()
        self._spell_system_states: "SpellSystemStates" = spell_system_states

        # spell_index_id -> Dict[str, Any]
        self._pending_changes: Dict[str, Dict[str, Any]] = {}
        # spell_id (version) -> set[root_id]
        self._component_of: Dict[str, Set[str]] = {}
        self._dirty_spells: Set[str] = set()
        self._dirty_roots: Set[str] = set()
        self._monitor_active: bool = False
        self._revalidate_fn: Optional[Callable[[Set[str], Optional[CancellationEvent]], None]] = None
        self._change_control_enabled: bool = True
        self._transaction_manager: ChangeControlTransactionManager = ChangeControlTransactionManager()
        self._conflict_manager: ChangeControlConflictManager = ChangeControlConflictManager()
        self._embargo_manager: ChangeControlEmbargoManager = ChangeControlEmbargoManager()
        self._orchestrator: ChangeControlOrchestrator = ChangeControlOrchestrator()
        self._commit_validator: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        self._commit_hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        self._abort_hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        self._structural_validator: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        self._dirty_marker: Optional[Callable[[ChangeControlStagedMutation], None]] = (
            self._default_dirty_marker
        )
        self._orchestrator.set_commit_validator(self._dispatch_commit_validator)
        self._orchestrator.set_commit_hook(self._dispatch_commit_hook)
        self._orchestrator.set_abort_hook(self._dispatch_abort_hook)
    # ----------------------------------------------------------------------
    # Cleanup
    # ----------------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Idempotent cleanup for change-control state.

        Purpose:
            Release registries and manager references held by this instance.
        Contract:
            - Safe to call multiple times.
            - After cleanup, check_cleaned() raises on use.
        Returns:
            None.
        Threading:
            Acquires the internal lock while mutating state.
        Lifecycle:
            Does not own SpellSystemStates; drops its reference only.
        """
        if self._cleaned:
            return

        # Normal pattern: lock while mutating internal fields.
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True

            if self._pending_changes is not None:
                self._pending_changes.clear()
                self._pending_changes = None

            if self._component_of is not None:
                for roots in self._component_of.values():
                    roots.clear()
                self._component_of.clear()
                self._component_of = None

            if self._dirty_spells is not None:
                self._dirty_spells.clear()
                self._dirty_spells = None

            if self._dirty_roots is not None:
                self._dirty_roots.clear()
                self._dirty_roots = None

            self._monitor_active = False
            self._revalidate_fn = None
            self._change_control_enabled = None

            if self._transaction_manager is not None:
                self._transaction_manager.cleanup()
                self._transaction_manager = None

            if self._conflict_manager is not None:
                self._conflict_manager.cleanup()
                self._conflict_manager = None

            if self._embargo_manager is not None:
                self._embargo_manager.cleanup()
                self._embargo_manager = None

            if self._orchestrator is not None:
                self._orchestrator.cleanup()
                self._orchestrator = None
            self._commit_validator = None
            self._commit_hook = None
            self._abort_hook = None
            self._structural_validator = None
            self._dirty_marker = None

            # We do *not* own spell_system_states' lifecycle here; that will
            # be cleaned by the Aetheric Frame / DevOpsManager. We only drop
            # our reference so GC can do its job.
            self._spell_system_states = None

        # Drop the lock last.
        self._lock = None

    # ----------------------------------------------------------------------
    # Accessors
    # ----------------------------------------------------------------------
    def enable_change_control(self) -> None:
        """
        Enable change-control admission for this frame.

        Purpose:
            Allow the orchestrator admission gate to evaluate requests.
        Contract:
            - When enabled, admission checks apply conflict/embargo rules.
            - Calling enable while already enabled is a no-op.
        Returns:
            None.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while mutating state.
        """
        self.check_cleaned()
        with self._lock:
            self._change_control_enabled = True

    def disable_change_control(self) -> None:
        """
        Disable change-control admission for this frame.

        Purpose:
            Allow transactions to proceed without conflict/embargo gating.
        Contract:
            - When disabled, admission returns accepted without conflict checks.
            - Calling disable while already disabled is a no-op.
        Returns:
            None.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while mutating state.
        """
        self.check_cleaned()
        with self._lock:
            self._change_control_enabled = False

    def is_change_control_enabled(self) -> bool:
        """
        Return whether change-control admission is enabled.

        Purpose:
            Expose admission gating state for callers and diagnostics.
        Contract:
            - Returns True when admission gating is enabled.
        Returns:
            bool: True if change-control admission is enabled.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while reading state.
        """
        self.check_cleaned()
        with self._lock:
            return bool(self._change_control_enabled)

    def set_audit_logger(
            self,
            fn: Optional[Callable[[ChangeControlTransactionRequest], None]],
    ) -> None:
        """
        Register an audit logger for admitted change-control requests.

        Purpose:
            Forward audit logging callbacks to the transaction manager.
        Contract:
            - Passing None disables audit logging.
            - Callback is invoked outside internal locks by the transaction manager.
        Args:
            fn:
                Callable that receives the admitted request, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while updating the callback.
        """
        self.check_cleaned()
        with self._lock:
            self._transaction_manager.set_audit_logger(fn)

    def set_commit_validator(
            self,
            fn: Optional[Callable[[ChangeControlStagedMutation], None]],
    ) -> None:
        """
        Register a commit validator hook for admitted requests.

        Purpose:
            Provide a hook for pre-commit structural validation.
        Contract:
            - Passing None disables validation.
            - Hook is invoked outside the orchestrator lock.
        Args:
            fn:
                Callable that validates a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while updating the hook reference.
        """
        self.check_cleaned()
        with self._lock:
            self._commit_validator = fn

    def set_structural_validator(
            self,
            fn: Optional[Callable[[ChangeControlStagedMutation], None]],
    ) -> None:
        """
        Register a structural validation hook for admitted requests.

        Purpose:
            Provide a placeholder hook for running structural phases before commit.
        Contract:
            - Passing None disables the hook.
        Args:
            fn:
                Callable that validates a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while updating the hook reference.
        """
        self.check_cleaned()
        with self._lock:
            self._structural_validator = fn

    def set_commit_hook(
            self,
            fn: Optional[Callable[[ChangeControlStagedMutation], None]],
    ) -> None:
        """
        Register a commit hook for admitted requests.

        Purpose:
            Provide a hook for commit-time side effects (dirty marking, etc.).
        Contract:
            - Passing None disables the hook.
            - Hook is invoked outside the orchestrator lock.
        Args:
            fn:
                Callable invoked with a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while updating the hook reference.
        """
        self.check_cleaned()
        with self._lock:
            self._commit_hook = fn

    def set_dirty_marker(
            self,
            fn: Optional[Callable[[ChangeControlStagedMutation], None]],
    ) -> None:
        """
        Register a commit-time dirty-marking hook.

        Purpose:
            Provide a hook for marking dependency state dirty on commit.
        Contract:
            - Passing None disables dirty marking.
        Args:
            fn:
                Callable invoked with a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while updating the hook reference.
        """
        self.check_cleaned()
        with self._lock:
            self._dirty_marker = fn

    def set_abort_hook(
            self,
            fn: Optional[Callable[[ChangeControlStagedMutation], None]],
    ) -> None:
        """
        Register an abort hook for admitted requests.

        Purpose:
            Provide a hook for abort-time cleanup side effects.
        Contract:
            - Passing None disables the hook.
            - Hook is invoked outside the orchestrator lock.
        Args:
            fn:
                Callable invoked with a staged mutation, or None.
        Returns:
            None.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while updating the hook reference.
        """
        self.check_cleaned()
        with self._lock:
            self._abort_hook = fn

    def _dispatch_commit_validator(self, staged: ChangeControlStagedMutation) -> None:
        """
        Internal

        Dispatch commit validators in a stable order.

        Purpose:
            Sequence structural validation ahead of the general commit validator.
        Contract:
            - Structural validator runs before the commit validator.
            - Hook references are captured under the lock, then executed
              without holding the lock to avoid deadlocks.
            - No-op if both hooks are None.
        Args:
            staged:
                Staged mutation metadata to validate.
        Returns:
            None.
        Raises:
            Exception: Propagates any exception raised by the validators.
        Threading:
            Uses the internal lock to snapshot hook references.
        """
        validator: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        structural: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        with self._lock:
            validator = self._commit_validator
            structural = self._structural_validator
        if structural is not None:
            structural(staged)
        if validator is not None:
            validator(staged)

    def _dispatch_commit_hook(self, staged: ChangeControlStagedMutation) -> None:
        """
        Internal

        Dispatch commit hooks in a stable order.

        Purpose:
            Sequence dirty marking ahead of the user-supplied commit hook.
        Contract:
            - Dirty marker runs before the commit hook.
            - Hook references are captured under the lock, then executed
              without holding the lock to avoid deadlocks.
            - No-op if both hooks are None.
        Args:
            staged:
                Staged mutation metadata to process.
        Returns:
            None.
        Raises:
            Exception: Propagates any exception raised by hooks.
        Threading:
            Uses the internal lock to snapshot hook references.
        """
        marker: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        with self._lock:
            marker = self._dirty_marker
            hook = self._commit_hook
        if marker is not None:
            marker(staged)
        if hook is not None:
            hook(staged)

    def _dispatch_abort_hook(self, staged: ChangeControlStagedMutation) -> None:
        """
        Internal

        Dispatch abort hooks.

        Purpose:
            Invoke the abort hook for staged mutations when a commit fails.
        Contract:
            - Hook reference is captured under the lock and invoked without
              holding the lock.
            - No-op if no hook is registered.
        Args:
            staged:
                Staged mutation metadata to process.
        Returns:
            None.
        Raises:
            Exception: Propagates any exception raised by the abort hook.
        Threading:
            Uses the internal lock to snapshot hook references.
        """
        hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        with self._lock:
            hook = self._abort_hook
        if hook is not None:
            hook(staged)

    def _default_dirty_marker(self, staged: ChangeControlStagedMutation) -> None:
        """
        Internal

        Default dirty-marker for commit events.

        Purpose:
            Mark list[Frame] consumers dirty for the owning Spellbook when
            bindings change as part of a transaction commit.
        Contract:
            - No-op if the staged mutation has no spellbook id.
            - No-op if no binding keys are present or frame keys are empty.
            - Delegates to SpellSystemStates for scoped dirty marking.
        Args:
            staged:
                Staged mutation metadata containing binding keys.
        Returns:
            None.
        Raises:
            Exception: Propagates exceptions raised by SpellSystemStates.
        Threading:
            Uses SpellSystemStates internal locking; does not hold the manager lock.
        """
        if staged.spellbook_id is None:
            return
        if not staged.binding_keys:
            return
        frame_keys = {frame_key for frame_key, _ in staged.binding_keys if frame_key}
        if not frame_keys:
            return
        self._spell_system_states.mark_collection_dependents_dirty(
            spellbook_id=staged.spellbook_id,
            frame_keys=frame_keys,
        )

    def transaction_manager(self) -> ChangeControlTransactionManager:
        """
        Return the transaction manager (admission facade).

        Purpose:
            Provide access to the transaction manager used for admission logging.
        Contract:
            - Returned reference is owned by this ChangeControlManager.
        Returns:
            ChangeControlTransactionManager:
                The manager instance.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Thread-safe; no state mutation beyond check_cleaned().
        """
        self.check_cleaned()
        return self._transaction_manager

    def conflict_manager(self) -> ChangeControlConflictManager:
        """
        Return the conflict manager (scope overlap rules).

        Purpose:
            Provide access to the conflict manager used for overlap checks.
        Contract:
            - Returned reference is owned by this ChangeControlManager.
        Returns:
            ChangeControlConflictManager:
                The manager instance.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Thread-safe; no state mutation beyond check_cleaned().
        """
        self.check_cleaned()
        return self._conflict_manager

    def embargo_manager(self) -> ChangeControlEmbargoManager:
        """
        Return the embargo manager (scope gating + hints).

        Purpose:
            Provide access to the embargo manager used for scope gating.
        Contract:
            - Returned reference is owned by this ChangeControlManager.
        Returns:
            ChangeControlEmbargoManager:
                The manager instance.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Thread-safe; no state mutation beyond check_cleaned().
        """
        self.check_cleaned()
        return self._embargo_manager

    def orchestrator(self) -> ChangeControlOrchestrator:
        """
        Return the orchestrator (single admission gate).

        Purpose:
            Provide access to the orchestrator used for admission sequencing.
        Contract:
            - Returned reference is owned by this ChangeControlManager.
        Returns:
            ChangeControlOrchestrator:
                The manager instance.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Thread-safe; no state mutation beyond check_cleaned().
        """
        self.check_cleaned()
        return self._orchestrator

    # ----------------------------------------------------------------------
    # Admission facade
    # ----------------------------------------------------------------------
    def admit_request(
            self,
            request: ChangeControlTransactionRequest,
    ) -> ChangeControlAdmissionResult:
        """
        Admit a transaction request through the change-control gate.

        Purpose:
            Centralize admission logic and enable/disable gating behavior.
        Contract:
            - When enabled, admission is serialized by the orchestrator and
              conflict/embargo checks are enforced.
            - When disabled, the request is accepted and tracked as in-flight.
        Args:
            request:
                Transaction request to admit.
        Returns:
            ChangeControlAdmissionResult:
                Admission decision with evidence for rejection.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Uses the internal lock for enable/disable reads and in-flight updates.
        """
        self.check_cleaned()
        enabled = True
        with self._lock:
            enabled = bool(self._change_control_enabled)
        if not enabled:
            self._transaction_manager.add_in_flight(request)
            return ChangeControlAdmissionResult(admitted=True)
        return self._orchestrator.admit_request(
            request,
            transaction_manager=self._transaction_manager,
            conflict_manager=self._conflict_manager,
            embargo_manager=self._embargo_manager,
        )

    def commit_request(self, request_id: str) -> None:
        """
        Commit an in-flight request and release implicit embargoes.

        Purpose:
            Provide a single commit hook for callers after mutation succeeds.
        Contract:
            - When enabled, delegates to the orchestrator to release embargoes
              and remove in-flight state.
            - When disabled, removes the in-flight entry directly.
        Args:
            request_id:
                Request id to finalize.
        Returns:
            None.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Uses the internal lock to read enable state.
        """
        self.check_cleaned()
        enabled = True
        with self._lock:
            enabled = bool(self._change_control_enabled)
        if not enabled:
            self._transaction_manager.remove_in_flight(request_id)
            return
        self._orchestrator.commit_request(
            request_id,
            transaction_manager=self._transaction_manager,
            embargo_manager=self._embargo_manager,
        )

    def abort_request(self, request_id: str) -> None:
        """
        Abort an in-flight request and release implicit embargoes.

        Purpose:
            Provide a single abort hook for callers when mutation fails.
        Contract:
            - When enabled, delegates to the orchestrator to release embargoes
              and remove in-flight state.
            - When disabled, removes the in-flight entry directly.
        Args:
            request_id:
                Request id to abort.
        Returns:
            None.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Uses the internal lock to read enable state.
        """
        self.check_cleaned()
        enabled = True
        with self._lock:
            enabled = bool(self._change_control_enabled)
        if not enabled:
            self._transaction_manager.remove_in_flight(request_id)
            return
        self._orchestrator.abort_request(
            request_id,
            transaction_manager=self._transaction_manager,
            embargo_manager=self._embargo_manager,
        )

    # ----------------------------------------------------------------------
    # Registration / updates
    # ----------------------------------------------------------------------
    def register_pending_change(
            self,
            spell_index: ISpellIndex,
            reason: str,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record a pending change for a spell lineage.

        Purpose:
            Track DevOps/AI-visible metadata for a SpellIndex lineage.
        Contract:
            - Stores metadata keyed by spell_index.id.
            - Last-write-wins for duplicate lineage ids.
        Args:
            spell_index:
                The SpellIndex for the lineage being tracked.
            reason:
                Short reason code (e.g. "mutation_candidate").
            metadata:
                Optional free-form metadata stored alongside the reason.
        Returns:
            None.
        Raises:
            ValueError: If spell_index is None or reason is empty.
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while updating state.
        """
        self.check_cleaned()
        if spell_index is None:
            raise ValueError("spell_index cannot be None")
        if not reason:
            raise ValueError("reason cannot be empty")

        index_id = spell_index.id
        details = dict(metadata) if metadata is not None else {}
        details["reason"] = reason

        with self._lock:
            # Last-write-wins semantics; we don't try to merge old/new metadata.
            self._pending_changes[index_id] = details

    # ----------------------------------------------------------------------
    # Introspection
    # ----------------------------------------------------------------------
    def get_pending_change(
            self,
            spell_index_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Return a snapshot of pending change metadata for a lineage.

        Purpose:
            Provide tooling with a stable view of pending change metadata.
        Contract:
            - Returns a shallow copy; callers cannot mutate internal state.
        Args:
            spell_index_id:
                SpellIndex id of the lineage to query.
        Returns:
            Optional[Dict[str, Any]]:
                Snapshot metadata if present, otherwise None.
        Raises:
            ValueError: If spell_index_id is empty.
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while copying state.
        """
        self.check_cleaned()
        if not spell_index_id:
            raise ValueError("spell_index_id cannot be empty")

        with self._lock:
            entry = self._pending_changes.get(spell_index_id)
            if entry is None:
                return None
            # Snapshot to plain dict for external consumption; this is
            # DevOps-side, not hot path.
            return dict(entry)

    def list_pending_changes(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a snapshot of all pending changes.

        Purpose:
            Provide a tooling-friendly snapshot of all pending lineage changes.
        Contract:
            - Returns a new mapping; callers cannot mutate internal state.
        Returns:
            Dict[str, Dict[str, Any]]:
                Mapping of SpellIndex id to metadata snapshots.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while copying state.
        """
        self.check_cleaned()
        snapshot: Dict[str, Dict[str, Any]] = {}
        with self._lock:
            for index_id, meta in self._pending_changes.items():
                snapshot[index_id] = dict(meta)
        return snapshot

    # ----------------------------------------------------------------------
    # Clearing
    # ----------------------------------------------------------------------
    def clear_pending_change(self, spell_index_id: str) -> None:
        """
        Clear pending-change metadata for a lineage.

        Purpose:
            Remove stale pending-change metadata after completion or cancelation.
        Contract:
            - No error if no pending entry exists.
        Args:
            spell_index_id:
                SpellIndex id to clear.
        Returns:
            None.
        Raises:
            ValueError: If spell_index_id is empty.
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while mutating state.
        """
        self.check_cleaned()
        if not spell_index_id:
            raise ValueError("spell_index_id cannot be empty")

        with self._lock:
            if spell_index_id in self._pending_changes:
                del self._pending_changes[spell_index_id]

    # ----------------------------------------------------------------------
    # Change-control (component-of / dirty tracking)
    # ----------------------------------------------------------------------
    def set_revalidator(
            self,
            fn: Callable[[Set[str], Optional[CancellationEvent]], None],
    ) -> None:
        """
        Register a callable that performs revalidation for dirty roots.

        Purpose:
            Provide a hook to revalidate roots after change detection.
        Contract:
            - Stored callable is invoked by revalidate_dirty_roots().
            - Callable signature: fn(dirty_roots, cancel_event) -> None.
        Args:
            fn:
                Callable that performs revalidation on supplied root ids.
        Returns:
            None.
        Raises:
            ValueError: If fn is None.
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while updating state.
        """
        self.check_cleaned()
        if fn is None:
            raise ValueError("revalidator fn must not be None.")
        with self._lock:
            self._revalidate_fn = fn

    def rebuild_component_of(
            self,
            root_blueprints: Dict[str, RootResolutionBlueprint],
    ) -> None:
        """
        Rebuild the component-of index from root blueprints.

        Purpose:
            Recompute root dependencies used for targeted revalidation.
        Contract:
            - Clears existing component-of mappings.
            - Resets dirty tracking and monitoring flags.
        Args:
            root_blueprints:
                Mapping of root spell_id to root resolution blueprint.
        Returns:
            None.
        Raises:
            ValueError: If root_blueprints is None.
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while rebuilding mappings.
        """
        self.check_cleaned()
        if root_blueprints is None:
            raise ValueError("root_blueprints must not be None.")

        with self._lock:
            self._component_of.clear()
            for root_id, blueprint in root_blueprints.items():
                dag = blueprint.dag
                for node_id in dag.nodes.keys():
                    self._component_of.setdefault(node_id, set()).add(root_id)
                # Ensure root is present in its own set.
                self._component_of.setdefault(root_id, set()).add(root_id)

            self._dirty_spells.clear()
            self._dirty_roots.clear()
            self._monitor_active = False

    def notify_spell_changed(self, spell_id: str) -> None:
        """
        Mark a spell as changed and flag dependent roots as dirty.

        Purpose:
            Record change signals that may require root revalidation.
        Contract:
            - Marks the spell id dirty.
            - Marks dependent roots dirty and enables monitoring.
        Args:
            spell_id:
                Versioned spell id that changed.
        Returns:
            None.
        Raises:
            ValueError: If spell_id is empty.
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while updating dirty flags.
        """
        self.check_cleaned()
        if not spell_id:
            raise ValueError("spell_id cannot be empty")

        with self._lock:
            self._dirty_spells.add(spell_id)
            affected_roots = self._component_of.get(spell_id, ())
            self._dirty_roots.update(affected_roots)
            self._monitor_active = True

    def notify_provider_changed(self, spell_id: str) -> None:
        """
        Alias for provider changes.

        Purpose:
            Maintain a stable API for provider-driven change signals.
        Contract:
            - Delegates to notify_spell_changed().
        Args:
            spell_id:
                Versioned spell id that changed.
        Returns:
            None.
        Raises:
            ValueError: If spell_id is empty.
            RuntimeError: If this manager has been cleaned.
        Threading:
            Delegates to notify_spell_changed() which is lock-protected.
        """
        self.notify_spell_changed(spell_id)

    def revalidate_dirty_roots(self, cancel_event: Optional["CancellationEvent"] = None) -> None:
        """
        Invoke the registered revalidator for current dirty roots.

        Purpose:
            Execute the revalidator callback on the current dirty root set.
        Contract:
            - Uses a snapshot of dirty roots.
            - Calls the revalidator outside the lock.
            - Clears dirty flags only for roots that were validated.
        Args:
            cancel_event:
                Optional cancellation signal to abort validation.
        Returns:
            None.
        Raises:
            RuntimeError: If this manager has been cleaned.
            OperationCancelledError: If the cancel_event is set.
        Threading:
            Copies state under lock and executes revalidation without the lock.
        """
        self.check_cleaned()
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()
        with self._lock:
            if not self._dirty_roots or self._revalidate_fn is None:
                return
            dirty_roots = set(self._dirty_roots)
        # Call outside the lock to avoid deadlocks.
        self._revalidate_fn(dirty_roots, cancel_event)
        with self._lock:
            self._dirty_roots.difference_update(dirty_roots)
            if not self._dirty_roots:
                self._dirty_spells.clear()
                self._monitor_active = False

    # ----------------------------------------------------------------------
    # Introspection helpers
    # ----------------------------------------------------------------------
    def is_root_dirty(self, root_id: str) -> bool:
        """
        Return True if the supplied root id is marked dirty.

        Purpose:
            Allow callers to check if a root requires revalidation.
        Contract:
            - Returns False if monitoring is inactive.
        Args:
            root_id:
                Versioned root spell id to check.
        Returns:
            bool:
                True if the root is dirty and monitoring is active.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while reading state.
        """
        self.check_cleaned()
        if not root_id:
            return False
        with self._lock:
            if not self._monitor_active:
                return False
            return root_id in self._dirty_roots

    def describe(self) -> Dict[str, Any]:
        """
        Diagnostic snapshot of change-control state.

        Purpose:
            Provide a tooling-friendly snapshot of change-control registries.
        Contract:
            - Returns a new mapping containing copies of internal state.
        Returns:
            Dict[str, Any]:
                Snapshot of change-control state for diagnostics.
        Raises:
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while copying state.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "pending_changes": dict(self._pending_changes),
                "dirty_spells": set(self._dirty_spells),
                "dirty_roots": set(self._dirty_roots),
                "component_of": {k: set(v) for k, v in self._component_of.items()},
                "monitor_active": self._monitor_active,
                "revalidator_registered": self._revalidate_fn is not None,
                "transaction_manager": (
                    self._transaction_manager.describe()
                    if self._transaction_manager is not None
                    else None
                ),
                "embargo_manager": (
                    self._embargo_manager.describe()
                    if self._embargo_manager is not None
                    else None
                ),
            }
