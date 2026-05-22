from threading import RLock
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    TYPE_CHECKING,
    ClassVar,
)



from melder.aether.aetheric_frame.dev_ops.change_control_manager.conflict_manager.conflict_manager import (
    ChangeControlConflictManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
    ChangeControlEmbargoManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.orchestrator import (
    ChangeControlOrchestrator,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_mediator import (
    TransactionMediator,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlAdmissionResult,
    ChangeTransactionType,
)
from melder.aether.aetheric_frame.aetheric_frame_configuration import (
    AethericFrameConfiguration,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.bind.spell_index import SpellIndex
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
        ChangeControlStagedMutation,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
        ChangeControlTransactionRequest,
    )
    from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


class ChangeControlManager(Cleanable):
    """
    Change-control registry for an Aetheric Frame.

    Purpose:
        Provide DevOps-facing bookkeeping for spell lineages, dirty roots, and
        change-control admission helpers. This is the frame-level control-plane
        owner for admission, embargo, conflict, staging, and targeted
        revalidation bookkeeping; it is not the hot-path resolver itself.
    Contract:
        - Tracks pending change metadata by SpellIndex id.
        - Tracks per-conduit component-of and dirty root state for targeted revalidation.
        - Owns and coordinates the transaction/conflict/embargo/orchestrator
          helper managers used by change-control flows.
        - Exposes hook-registration seams for commit, abort, structural
          validation, and dirty-marking behavior.
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
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_system_states",
        "_pending_changes",
        "_component_of_by_conduit",
        "_dirty_spells_by_conduit",
        "_dirty_roots_by_conduit",
        "_monitor_active_by_conduit",
        "_revalidate_fn_by_conduit",
        "_change_control_enabled",
        "_transaction_manager",
        "_transaction_mediator",
        "_conflict_manager",
        "_embargo_manager",
        "_orchestrator",
        "_commit_validator",
        "_commit_hook",
        "_abort_hook",
        "_structural_validator",
        "_dirty_marker",
    ]

    def __init__(self, spell_system_states: SpellSystemStates) -> None:
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
        self._spell_system_states: SpellSystemStates = spell_system_states

        # spell_index_id -> Dict[str, Any]
        self._pending_changes: Dict[str, Dict[str, Any]] = {}
        # conduit_id -> (spell_id -> set[root_id])
        self._component_of_by_conduit: Dict[str, Dict[str, Set[str]]] = {}
        self._dirty_spells_by_conduit: Dict[str, Set[str]] = {}
        self._dirty_roots_by_conduit: Dict[str, Set[str]] = {}
        self._monitor_active_by_conduit: Dict[str, bool] = {}
        self._revalidate_fn_by_conduit: Dict[
            str,
            Callable[[Set[str], Optional[CancellationEvent]], Optional[Set[str]]],
        ] = {}
        self._change_control_enabled: bool = True
        self._transaction_manager: ChangeControlTransactionManager = ChangeControlTransactionManager()
        self._conflict_manager: ChangeControlConflictManager = ChangeControlConflictManager()
        self._embargo_manager: ChangeControlEmbargoManager = ChangeControlEmbargoManager()
        self._orchestrator: ChangeControlOrchestrator = ChangeControlOrchestrator()
        frame_configuration = None
        try:
            frame = spell_system_states._frame
            if frame is not None:
                frame_configuration = frame.frame_configuration
        except Exception:
            frame_configuration = None
        change_control_mode = "strict"
        allow_multiple_root_transactions = False
        queue_competing_root_transactions = False
        max_transaction_wait_time_in_seconds = 30.0
        if isinstance(frame_configuration, AethericFrameConfiguration):
            change_control_mode = frame_configuration.change_control_mode
            allow_multiple_root_transactions = (
                frame_configuration.allow_multiple_root_transactions
            )
            queue_competing_root_transactions = (
                frame_configuration.queue_competing_root_transactions
            )
            max_transaction_wait_time_in_seconds = (
                frame_configuration.max_transaction_wait_time_in_seconds
            )
        self._transaction_mediator: TransactionMediator = TransactionMediator(
            transaction_manager=self._transaction_manager,
            embargo_manager=self._embargo_manager,
            orchestrator=self._orchestrator,
            change_control_mode=change_control_mode,
            allow_multiple_root_transactions=allow_multiple_root_transactions,
            queue_competing_root_transactions=queue_competing_root_transactions,
            max_transaction_wait_time_in_seconds=(
                max_transaction_wait_time_in_seconds
            ),
        )
        self._commit_validator: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        self._commit_hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        self._abort_hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        self._structural_validator: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        self._dirty_marker: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        self._orchestrator.set_commit_validator(self._dispatch_commit_validator)
        self._orchestrator.set_commit_hook(self._dispatch_commit_hook)
        self._orchestrator.set_abort_hook(self._dispatch_abort_hook)
        self.set_structural_validator(self._default_structural_validator)
        self.set_dirty_marker(self._default_dirty_marker)
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

            if self._component_of_by_conduit is not None:
                for component_of in self._component_of_by_conduit.values():
                    for roots in component_of.values():
                        roots.clear()
                    component_of.clear()
                self._component_of_by_conduit.clear()

            if self._dirty_spells_by_conduit is not None:
                for dirty_spells in self._dirty_spells_by_conduit.values():
                    dirty_spells.clear()
                self._dirty_spells_by_conduit.clear()

            if self._dirty_roots_by_conduit is not None:
                for dirty_roots in self._dirty_roots_by_conduit.values():
                    dirty_roots.clear()
                self._dirty_roots_by_conduit.clear()

            if self._monitor_active_by_conduit is not None:
                self._monitor_active_by_conduit.clear()

            if self._revalidate_fn_by_conduit is not None:
                self._revalidate_fn_by_conduit.clear()

            if self._transaction_manager is not None:
                self._transaction_manager.cleanup()

            if self._transaction_mediator is not None:
                self._transaction_mediator.cleanup()

            if self._conflict_manager is not None:
                self._conflict_manager.cleanup()

            if self._embargo_manager is not None:
                self._embargo_manager.cleanup()

            if self._orchestrator is not None:
                self._orchestrator.cleanup()

            del self._pending_changes
            del self._component_of_by_conduit
            del self._dirty_spells_by_conduit
            del self._dirty_roots_by_conduit
            del self._monitor_active_by_conduit
            del self._revalidate_fn_by_conduit
            del self._change_control_enabled
            del self._transaction_manager
            del self._transaction_mediator
            del self._conflict_manager
            del self._embargo_manager
            del self._orchestrator
            del self._commit_validator
            del self._commit_hook
            del self._abort_hook
            del self._structural_validator
            del self._dirty_marker

            # We do *not* own spell_system_states' lifecycle here; that will
            # be cleaned by the Aetheric Frame / DevOpsManager. We only drop
            # our reference so GC can do its job.
            del self._spell_system_states

        # Drop the lock last.
        del self._lock

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

        Returns:
            bool: `True` when admission should pass through the normal
            conflict/embargo gate and `False` when the manager is operating in
            bypass mode.
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
            Wire the frame-level change-control surface to the transaction
            manager's observational audit stream.

        Contract:
            - Passing `None` disables audit logging.
            - The callback is forwarded to the transaction manager, which later
              invokes it outside the manager lock.

        Passing `None` disables audit logging. The callback itself is later run
        by the transaction manager, outside this manager's internal lock.

        Args:
            fn: Callable that receives admitted requests, or `None` to disable
                audit logging.
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
            Install the outer commit-validation stage that runs after the
            structural validator during commit dispatch.

        Contract:
            - Passing `None` disables this validation stage.
            - The hook reference is snapshotted under the manager lock and later
              invoked outside the lock through `_dispatch_commit_validator(...)`.

        Args:
            fn: Callable that validates a staged mutation, or `None` to disable
                this hook.
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
            Install the first commit-validation stage for structural/runtime
            checks that must run before the general commit validator.

        Contract:
            - Passing `None` disables the structural validation stage.
            - The hook is invoked through `_dispatch_commit_validator(...)`
              before the outer validator hook.

        Args:
            fn: Callable that validates a staged mutation, or `None` to disable
                this hook.
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
            Install the general post-validation commit side-effect hook.

        Contract:
            - Passing `None` disables the hook.
            - The hook runs after the dirty marker inside
              `_dispatch_commit_hook(...)`.

        Args:
            fn: Callable invoked with a staged mutation, or `None` to disable
                this hook.
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
            Install the commit-side hook responsible for marking runtime state
            dirty after a successful mutation.

        Contract:
            - Passing `None` disables dirty marking.
            - The hook runs before the general commit hook so later side effects
              see already-dirtied runtime state.

        Args:
            fn: Callable invoked with a staged mutation, or `None` to disable
                dirty marking.
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
            Install the staged-mutation cleanup hook that runs when an admitted
            request aborts or a commit-side hook fails.

        Contract:
            - Passing `None` disables the hook.
            - The hook reference is snapshotted under the manager lock and
              invoked outside the lock through `_dispatch_abort_hook(...)` or
              orchestrator cleanup.

        Args:
            fn: Callable invoked when an admitted staged mutation aborts, or
                `None` to disable the hook.
        """
        self.check_cleaned()
        with self._lock:
            self._abort_hook = fn

    def _dispatch_commit_validator(self, staged: ChangeControlStagedMutation) -> None:
        """
        Run the registered commit validators in stable order.

        Ordering matters here:
        - structural validator first
        - general commit validator second

        The hook references are snapshotted under the manager lock and then
        executed outside the lock so validator code cannot deadlock this
        manager's internal state.

        Args:
            staged: Staged mutation metadata to validate.
        """
        self.check_cleaned()
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
        Run the registered commit-side hooks in stable order.

        Ordering matters here:
        - dirty marker first
        - general commit hook second

        As with validator dispatch, the hook references are snapshotted under
        the lock and executed outside it so hook code cannot deadlock this
        manager.

        Args:
            staged: Staged mutation metadata to process.
        """
        self.check_cleaned()
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
        Run the registered abort hook, if any.

        Purpose:
            Provide one lock-safe abort-hook dispatch path for the orchestrator.

        Contract:
            - Snapshots the hook reference under the manager lock.
            - Invokes the hook outside the lock so abort-side cleanup code
              cannot deadlock this manager.

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
        self.check_cleaned()
        hook: Optional[Callable[[ChangeControlStagedMutation], None]] = None
        with self._lock:
            hook = self._abort_hook
        if hook is not None:
            hook(staged)

    def _resolve_frame(self) -> Optional[Any]:
        """
        Internal

        Resolve the owning AethericFrame from SpellSystemStates.

        Purpose:
            Provide access to frame-level conduit registries for change-control
            validators without introducing an Aether dependency.
        Contract:
            - Returns None if the frame reference is unavailable or cleaned.
            - Does not acquire additional frame-level locks; callers own that
              responsibility when they dereference frame internals.
        Returns:
            Optional[Any]:
                The owning frame instance when available.
        """
        self.check_cleaned()
        return self._spell_system_states._frame

    def _resolve_conduit_by_id(self, conduit_id: str) -> Optional[Any]:
        """
        Internal

        Resolve a conduit instance by id from the owning frame.

        Purpose:
            Allow structural validators to locate the conduit/Spellbook involved
            in a staged mutation.
        Contract:
            - Returns None if the conduit cannot be resolved.
        Args:
            conduit_id:
                Conduit id to resolve.
        Returns:
            Optional[Any]:
                The resolved conduit instance, if found.
        """
        self.check_cleaned()
        if not conduit_id:
            return None
        frame = self._resolve_frame()
        if frame is None:
            return None
        lock = frame._lock
        conduits = frame._conduits
        if lock is None or conduits is None:
            return None
        with lock:
            return conduits.get(conduit_id)

    def _resolve_spellbook_for_staged(
            self,
            staged: ChangeControlStagedMutation,
    ) -> Optional[Any]:
        """
        Internal

        Resolve a Spellbook instance for a staged mutation.

        Purpose:
            Map staged mutation metadata to the owning Spellbook so structural
            validation can run locally.
        Contract:
            - Prefers initiator conduit when available.
            - Skips spellbook-only initiator ids (spellbook:{id}).
            - Returns None when no matching Spellbook can be resolved.
        Args:
            staged:
                Staged mutation metadata.
        Returns:
            Optional[Any]:
                The resolved Spellbook instance, if available.
        """
        self.check_cleaned()
        if staged is None:
            return None
        candidate_ids: list[str] = []
        initiator_id = staged.initiator_conduit_id
        if initiator_id and not initiator_id.startswith("spellbook:"):
            candidate_ids.append(initiator_id)
        for conduit_id in staged.conduit_ids:
            if conduit_id not in candidate_ids:
                candidate_ids.append(conduit_id)

        for conduit_id in candidate_ids:
            conduit = self._resolve_conduit_by_id(conduit_id)
            if conduit is None:
                continue
            spellbook = conduit._spellbook
            if spellbook is None:
                continue
            if staged.spellbook_id and spellbook._id != staged.spellbook_id:
                continue
            try:
                spellbook.check_cleaned()
            except Exception:
                continue
            return spellbook
        return None

    def _resolve_spells_for_binding_keys(
            self,
            spellbook: Any,
            binding_keys: Iterable[Tuple[str, str]],
    ) -> list:
        """
        Resolve live spell objects for staged binding keys.

        This helper translates normalized binding keys from staged mutation data
        back into concrete spell objects so later validators or dirty markers
        can work against live runtime state rather than key tuples.

        Returns an empty list when the spellbook is unavailable, the keys are
        empty, or a particular key no longer resolves cleanly.
        """
        self.check_cleaned()
        if spellbook is None or not binding_keys:
            return []
        resolved: list = []
        seen: set = set()
        with spellbook._lock:
            lookup_map = spellbook._lookup_spells
            spell_map = spellbook._spells
            if lookup_map is None or spell_map is None:
                return []
            for frame_key, binding_key in binding_keys:
                key = (frame_key, binding_key)
                if key in seen:
                    continue
                seen.add(key)
                spell_index = lookup_map.get(key)
                if spell_index is None:
                    continue
                spell = spell_map.get(spell_index)
                if spell is None:
                    continue
                resolved.append(spell)
        return resolved

    def _default_structural_validator(self, staged: ChangeControlStagedMutation) -> None:
        """
        Default structural-validation hook for bind transactions.

        This is the built-in validator used when a staged bind should force
        Phase 1-4 validation before commit completes. It is intentionally
        conservative:

        - only bind transactions participate
        - unconjured or unavailable spellbooks short-circuit to no-op
        - spells that already have Phase 4 results are skipped

        Any structural-phase exception is allowed to propagate so the commit
        path can fail loudly instead of accepting a broken staged bind.
        """
        self.check_cleaned()
        if staged.request_type is not ChangeTransactionType.BIND:
            return
        if not staged.binding_keys:
            return
        spellbook = self._resolve_spellbook_for_staged(staged)
        if spellbook is None:
            return
        if not spellbook._conjured:
            return
        spells = self._resolve_spells_for_binding_keys(spellbook, staged.binding_keys)
        if not spells:
            return
        pending = [spell for spell in spells if spell.validation_result_phase4 is None]
        if not pending:
            return
        spellbook._run_post_conjure_structural_phases(pending)

    def _default_dirty_marker(self, staged: ChangeControlStagedMutation) -> None:
        """
        Default dirty-marker for commit events.

        This is the built-in commit-side hook that pushes follow-on invalidation
        into `SpellSystemStates`. It marks collection dependents dirty for
        changed frame keys and marks contract dependents dirty for changed
        contract keys, but only when the staged mutation actually names a
        spellbook and contributes relevant keys.
        """
        self.check_cleaned()
        if staged.spellbook_id is None:
            return
        if not staged.binding_keys and not staged.contract_keys:
            return
        frame_keys = {frame_key for frame_key, _ in staged.binding_keys if frame_key}
        frame_keys.update(
            {frame_key for frame_key, _, _ in staged.contract_keys if frame_key}
        )
        if not frame_keys:
            return
        self._spell_system_states.mark_collection_dependents_dirty(
            spellbook_id=staged.spellbook_id,
            frame_keys=frame_keys,
        )
        contract_key_set = {
            (frame_key, binding_key)
            for frame_key, binding_key, _ in staged.contract_keys
            if frame_key and binding_key
        }
        if not contract_key_set:
            return
        self._spell_system_states.mark_contract_dependents_dirty(
            spellbook_id=staged.spellbook_id,
            contract_keys=contract_key_set,
            change_reason=SpellStateChangeReason.contract_unvalidated,
        )

    def transaction_manager(self) -> ChangeControlTransactionManager:
        """
        Return the owned transaction manager.

        Returns:
            ChangeControlTransactionManager: Admission/in-flight transaction
            bookkeeping surface owned by this manager.
        """
        self.check_cleaned()
        return self._transaction_manager

    def transaction_mediator(self) -> TransactionMediator:
        """
        Return the owned live transaction mediator.

        Returns:
            TransactionMediator: Frame-local live transaction/session surface.
        """
        self.check_cleaned()
        return self._transaction_mediator

    def conflict_manager(self) -> ChangeControlConflictManager:
        """
        Return the owned conflict manager.

        Returns:
            ChangeControlConflictManager: Scope-overlap/conflict surface owned
            by this manager.
        """
        self.check_cleaned()
        return self._conflict_manager

    def embargo_manager(self) -> ChangeControlEmbargoManager:
        """
        Return the owned embargo manager.

        Returns:
            ChangeControlEmbargoManager: Embargo/gating surface owned by this
            manager.
        """
        self.check_cleaned()
        return self._embargo_manager

    def orchestrator(self) -> ChangeControlOrchestrator:
        """
        Return the owned orchestrator.

        Returns:
            ChangeControlOrchestrator: Admission-sequencing surface owned by
            this manager.
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

        This is the main admission facade:

        - when change-control is enabled, the orchestrator performs the real
          conflict/embargo admission workflow
        - when change-control is disabled, the request is accepted directly and
          recorded as in-flight without that extra gating

        Returns:
            ChangeControlAdmissionResult: Admission decision plus any rejection
            evidence returned by the orchestrator path.
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
        Update staged mutation metadata for an admitted request.

        Purpose:
            Refresh staged metadata discovered after admission without
            mutating the in-flight request payload.
        Contract:
            - Returns False if no staged record exists for the request.
            - Updates only supplied fields; None keeps existing values.
            - Metadata merges into the staged record when provided.
            - Extends implicit embargo scopes when new staged metadata arrives.
            - No effect when change-control admission is disabled.
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
            RuntimeError: If this manager has been cleaned.
            ValueError: If request_id is empty.
        Threading:
            Uses the internal lock to read enable state; orchestrator uses
            its lock for staged updates.
        """
        self.check_cleaned()
        if not request_id:
            raise ValueError("request_id cannot be empty")
        with self._lock:
            enabled = bool(self._change_control_enabled)
        if not enabled:
            return False
        updated = self._orchestrator.update_staged(
            request_id,
            scope_keys=scope_keys,
            binding_keys=binding_keys,
            contract_keys=contract_keys,
            metadata=metadata,
        )
        if not updated:
            return False
        staged = self._orchestrator.get_staged(request_id)
        if staged is None:
            return True
        if self._embargo_manager is None:
            return True
        scope_keys = self._embargo_manager.collect_scope_keys_from_staged(staged)
        if scope_keys:
            self._embargo_manager.extend_embargoes(
                owner_request_id=request_id,
                scope_keys=scope_keys,
                reason_tag=staged.request_type.value,
            )
        return True

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
            spell_index: SpellIndex,
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
            conduit_id: str,
            fn: Callable[[Set[str], Optional[CancellationEvent]], Optional[Set[str]]],
    ) -> None:
        """
        Register a callable that performs revalidation for dirty roots.

        Purpose:
            Provide a conduit-scoped hook to revalidate roots after change detection.
        Contract:
            - Stored callable is invoked by revalidate_dirty_roots(conduit_id).
            - Callable signature: fn(dirty_roots, cancel_event) -> Optional[Set[str]].
            - Returning None indicates all supplied roots were validated.
            - Returning a subset allows partial validation without clearing all roots.
        Args:
            conduit_id:
                Conduit identifier whose dirty roots this revalidator handles.
            fn:
                Callable that performs revalidation on supplied root ids.
        Returns:
            None.
        Raises:
            ValueError: If conduit_id is empty or fn is None.
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while updating state.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        if fn is None:
            raise ValueError("revalidator fn must not be None.")
        with self._lock:
            self._revalidate_fn_by_conduit[conduit_id] = fn

    def has_revalidator_for_conduit(self, conduit_id: str) -> bool:
        """
        Return whether a conduit-specific dirty-root revalidator is registered.

        Purpose:
            Let callers preserve idempotent conduit wiring without probing
            manager internals.
        Contract:
            - Returns True only when the supplied conduit id already has a
              stored revalidator callback.
            - Does not mutate change-control manager state.
        Args:
            conduit_id:
                Conduit identifier to inspect.
        Returns:
            bool:
                True when this conduit already has a registered revalidator.
        Raises:
            ValueError: If conduit_id is empty.
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while reading registration state.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        with self._lock:
            return conduit_id in self._revalidate_fn_by_conduit

    def rebuild_component_of(
            self,
            conduit_id: str,
            root_blueprints: Dict[str, RootResolutionBlueprint],
    ) -> None:
        """
        Rebuild the component-of index for a conduit from root blueprints.

        Purpose:
            Recompute root dependencies used for targeted revalidation.
        Contract:
            - Clears existing component-of mappings for the supplied conduit.
            - Resets dirty tracking and monitoring flags for that conduit.
        Args:
            conduit_id:
                Conduit identifier whose component-of map should be rebuilt.
            root_blueprints:
                Mapping of root spell_id to root resolution blueprint.
        Returns:
            None.
        Raises:
            ValueError: If conduit_id is empty or root_blueprints is None.
            RuntimeError: If this manager has been cleaned.
        Threading:
            Acquires the internal lock while rebuilding mappings.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        if root_blueprints is None:
            raise ValueError("root_blueprints must not be None.")

        with self._lock:
            component_of = self._component_of_by_conduit.get(conduit_id)
            if component_of is None:
                component_of = {}
                self._component_of_by_conduit[conduit_id] = component_of
            else:
                for roots in component_of.values():
                    roots.clear()
                component_of.clear()

            for root_id, blueprint in root_blueprints.items():
                dag = blueprint.dag
                for node_id in dag.nodes.keys():
                    component_of.setdefault(node_id, set()).add(root_id)
                # Ensure root is present in its own set.
                component_of.setdefault(root_id, set()).add(root_id)

            dirty_spells = self._dirty_spells_by_conduit.setdefault(conduit_id, set())
            dirty_roots = self._dirty_roots_by_conduit.setdefault(conduit_id, set())
            dirty_spells.clear()
            dirty_roots.clear()
            self._monitor_active_by_conduit[conduit_id] = False

    def upsert_component_of(
            self,
            conduit_id: str,
            root_blueprints: Dict[str, RootResolutionBlueprint],
    ) -> None:
        """
        Upsert component-of mappings for specific roots without full rebuild.

        Purpose:
            Refresh component-of ownership for a subset of roots while
            preserving mappings for unrelated roots on the same conduit.
        Contract:
            - Does not clear unrelated conduit mappings.
            - Replaces existing mappings for the supplied root ids.
            - Removes stale root memberships for those root ids.
            - Clears supplied roots from dirty-root tracking.
        Args:
            conduit_id:
                Conduit identifier whose component-of map should be updated.
            root_blueprints:
                Mapping of root spell_id to root resolution blueprint.
        Returns:
            None.
        Raises:
            ValueError:
                If conduit_id is empty or root_blueprints is None.
            RuntimeError:
                If this manager has been cleaned.
        Threading:
            Acquires the internal lock while mutating mappings.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        if root_blueprints is None:
            raise ValueError("root_blueprints must not be None.")

        root_ids = root_blueprints.keys()
        if not root_ids:
            return

        with self._lock:
            component_of = self._component_of_by_conduit.get(conduit_id)
            if component_of is None:
                component_of = {}
                self._component_of_by_conduit[conduit_id] = component_of

            # Drop stale memberships for roots being upserted.
            empty_node_ids: List[str] = []
            for node_id, owners in component_of.items():
                owners.difference_update(root_ids)
                if not owners:
                    empty_node_ids.append(node_id)
            for node_id in empty_node_ids:
                component_of.pop(node_id, None)

            # Apply fresh memberships for the provided roots.
            for root_id, blueprint in root_blueprints.items():
                dag = blueprint.dag
                for node_id in dag.nodes.keys():
                    component_of.setdefault(node_id, set()).add(root_id)
                component_of.setdefault(root_id, set()).add(root_id)

            dirty_roots = self._dirty_roots_by_conduit.setdefault(conduit_id, set())
            dirty_roots.difference_update(root_ids)
            if not dirty_roots:
                self._monitor_active_by_conduit[conduit_id] = False

    def notify_spell_changed(self, spell_id: str) -> None:
        """
        Mark a spell as changed and flag dependent roots as dirty.

        Purpose:
            Record change signals that may require root revalidation.
        Contract:
            - Marks the spell id dirty.
            - Marks dependent roots dirty and enables monitoring for any conduit
              that includes the spell in its component-of map.
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
        affected_roots_by_conduit: Dict[str, Set[str]] = {}
        with self._lock:
            for conduit_id, component_of in self._component_of_by_conduit.items():
                affected_roots = set(component_of.get(spell_id, ()))
                if not affected_roots:
                    continue
                affected_roots_by_conduit[conduit_id] = affected_roots
                dirty_spells = self._dirty_spells_by_conduit.setdefault(conduit_id, set())
                dirty_roots = self._dirty_roots_by_conduit.setdefault(conduit_id, set())
                dirty_spells.add(spell_id)
                dirty_roots.update(affected_roots)
                self._monitor_active_by_conduit[conduit_id] = True

        if not affected_roots_by_conduit:
            return

        # Mirror dirty roots into SpellSystemStates so DevOps risk gating
        # can detect that revalidation is required.
        for affected_roots in affected_roots_by_conduit.values():
            for root_id in affected_roots:
                try:
                    state = self._spell_system_states.get_by_spell_id(root_id)
                except Exception:
                    state = None
                if state is None:
                    continue
                try:
                    state.mark_dependency_change()
                except Exception:
                    pass

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

    def revalidate_dirty_roots(
            self,
            conduit_id: str,
            cancel_event: Optional["CancellationEvent"] = None,
    ) -> None:
        """
        Invoke the registered revalidator for current dirty roots.

        Purpose:
            Execute the conduit-scoped revalidator on the current dirty root set.
        Contract:
            - Uses a snapshot of dirty roots for the supplied conduit.
            - Calls the revalidator outside the lock.
            - Clears dirty flags only for roots reported as validated.
            - A None return from the revalidator implies all supplied roots validated.
        Args:
            conduit_id:
                Conduit identifier whose dirty roots should be revalidated.
            cancel_event:
                Optional cancellation signal to abort validation.
        Returns:
            None.
        Raises:
            ValueError: If conduit_id is empty.
            RuntimeError: If this manager has been cleaned.
            OperationCancelledError: If the cancel_event is set.
        Threading:
            Copies state under lock and executes revalidation without the lock.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()
        with self._lock:
            dirty_roots = self._dirty_roots_by_conduit.get(conduit_id)
            revalidator = self._revalidate_fn_by_conduit.get(conduit_id)
            if not dirty_roots or revalidator is None:
                return
            dirty_roots_snapshot = set(dirty_roots)
        # Call outside the lock to avoid deadlocks.
        validated_roots = revalidator(dirty_roots_snapshot, cancel_event)
        if validated_roots is None:
            validated_roots = dirty_roots_snapshot
        else:
            validated_roots = set(validated_roots)
        with self._lock:
            dirty_roots = self._dirty_roots_by_conduit.get(conduit_id)
            if dirty_roots is None:
                return
            dirty_roots.difference_update(validated_roots)
            if not dirty_roots:
                dirty_spells = self._dirty_spells_by_conduit.get(conduit_id)
                if dirty_spells is not None:
                    dirty_spells.clear()
                self._monitor_active_by_conduit[conduit_id] = False

    def has_registered_revalidators(self) -> bool:
        """
        Return whether any conduit revalidator is currently registered.

        Returns:
            bool: True when at least one conduit id has a stored revalidator.

        Raises:
            RuntimeError: If this manager has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return bool(self._revalidate_fn_by_conduit)

    # ----------------------------------------------------------------------
    # Introspection helpers
    # ----------------------------------------------------------------------
    def is_root_dirty(self, conduit_id: str, root_id: str) -> bool:
        """
        Return True if the supplied root id is marked dirty for a conduit.

        Purpose:
            Allow callers to check if a root requires revalidation.
        Contract:
            - Returns False if monitoring is inactive for the conduit.
        Args:
            conduit_id:
                Conduit identifier whose dirty-root state should be queried.
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
        if not conduit_id or not root_id:
            return False
        with self._lock:
            if not self._monitor_active_by_conduit.get(conduit_id, False):
                return False
            dirty_roots = self._dirty_roots_by_conduit.get(conduit_id)
            if dirty_roots is None:
                return False
            return root_id in dirty_roots

    def describe(self) -> Dict[str, Any]:
        """
        Diagnostic snapshot of change-control state.

        Purpose:
            Provide a tooling-friendly snapshot of change-control registries,
            including conduit-scoped dirty/component-of maps and the nested
            transaction/embargo manager snapshots.
        Contract:
            - Returns a new mapping containing copies of internal state.
            - Exposes diagnostic structure only; callers cannot mutate manager
              state through the returned value.
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
                "dirty_spells_by_conduit": {
                    conduit_id: set(spells)
                    for conduit_id, spells in self._dirty_spells_by_conduit.items()
                },
                "dirty_roots_by_conduit": {
                    conduit_id: set(roots)
                    for conduit_id, roots in self._dirty_roots_by_conduit.items()
                },
                "component_of_by_conduit": {
                    conduit_id: {
                        spell_id: set(root_ids)
                        for spell_id, root_ids in component_of.items()
                    }
                    for conduit_id, component_of in self._component_of_by_conduit.items()
                },
                "monitor_active_by_conduit": dict(self._monitor_active_by_conduit),
                "revalidator_registered_by_conduit": set(self._revalidate_fn_by_conduit.keys()),
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

