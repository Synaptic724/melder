import threading
from typing import Callable, Iterable, Optional, Set, TYPE_CHECKING, ClassVar


# Melder imports
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.risk_manager.risk_manager import RiskManager


class SpellSystemState(Cleanable):
    """
    System-level state for a single spell index: topology, validity, and flags.

    Identity
    --------
    - `spell_index_id`:
        Index identifier (ULID from SpellIndex.id).
    - `current_spell_id`:
        Currently promoted version id for this index (e.g., SpellIndex.selected_spell_id; typically a SHA).

    Topology
    --------
    - `direct_dependencies`:
        Set of dependency ids for this index. Caller decides whether ids are index or version ids.
    - `direct_dependents`:
        Reverse edges: indexes that depend on this index ("what breaks if this changes?").

    Validity / State
    ----------------
    - `validity`:
        Structural validity gate (unknown / valid / gated / invalid / disabled).
        This only reflects *global* spell-definition correctness (Phases 1-4),
        not conduit-specific resolution state.
    - `flags`:
        Fine-grained SpellState markers describing *why* the index is in its current condition
        (topology changes, contracts, mutation, ops).
    - `change_reason`:
        Last SpellStateChangeReason that moved this index into its current validity/flags.
    - `transitively_dirty`:
        True if impacted indirectly by upstream changes (dependency_changed closure).
    - `last_validated_at`:
        Optional timestamp (float seconds) of last *successful* structural validation.

    Contract:
        - Validity is STRUCTURAL only (Phases 1-4) and frame-global; it says
          nothing about whether any particular conduit can resolve the spell.
        - `validity` is the gate, `flags` are the explanation, and
          `change_reason` is the last cause - three separate axes, deliberately
          not collapsed into one status value.
        - `transitively_dirty` marks indirect impact via the
          `dependency_changed` closure rather than a direct edit.

    Threading:
        Mutated through the owning `SpellSystemStates` registry, which
        serializes access; this object adds no lock of its own.

    Lifecycle / Cleanup:
        One per spell index, created at `register_index(...)` and retired when
        the lineage is unregistered.

    Registration:
        MELDER KERNEL - guarded. Frame-owned control-plane state.

    Subsystem Context:
        The per-lineage row of the control tower. Its per-conduit counterpart
        is `ConduitResolutionState`; the split is the structural-versus-
        resolution axis and is the single most important distinction in this
        package.

    System Context:
        Keeping validity, flags, and reason as THREE fields rather than one
        status is what makes the control plane debuggable. `validity` answers
        the only question meld needs at speed - may this resolve, yes or no.
        `flags` carry the fine-grained SpellState markers explaining the
        condition, and `change_reason` records what moved it there. Collapsing
        them would force meld to parse a rich status on the hot path, or force
        diagnostics to guess causes from a coarse verdict.
        `direct_dependents` exists for one purpose: answering "what breaks if
        this changes" without walking the whole graph. Storing reverse edges at
        write time is what lets `compute_impact_closure` dirty a bounded set at
        change time instead of revalidating every lineage in the frame.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. System-level state for a single spell index: topology, validity, and "
        "flags. Melder kernel machinery: read it to understand the runtime, do not drive it "
        "directly."
    )
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_index_id",
        "_current_spell_id",
        "_direct_dependencies",
        "_direct_dependents",
        "_validity",
        "_flags",
        "_change_reason",
        "_transitively_dirty",
        "_last_validated_at",
        "_risk_manager",
    ]

    def __init__(self, spell_index_id: str, current_spell_id: str) -> None:
        """
        Initialize one index-scoped structural state record.

        Args:
            spell_index_id:
                Stable index identifier for the SpellIndex this state tracks.
            current_spell_id:
                Currently promoted spell version id for the index.
        Contract:
            - Starts with empty dependency and dependent sets.
            - Starts with `SpellValidity.unknown` plus the `new_index` flag so
              higher-level validation can distinguish first registration from a
              previously validated index.
            - Starts with no attached `RiskManager`; structural-risk propagation
              is enabled later by the owning registry.
        Raises:
            ValueError:
                If either identifier is empty.

        Returns:
            None.
        """
        super().__init__()

        if not spell_index_id:
            raise ValueError("spell_index_id cannot be empty")
        if not current_spell_id:
            raise ValueError("current_spell_id cannot be empty")

        self._lock: threading.RLock = threading.RLock()
        self._spell_index_id: str = spell_index_id
        self._current_spell_id: str = current_spell_id

        # Concurrent topology sets
        self._direct_dependencies: Set[str] = set()
        self._direct_dependents: Set[str] = set()

        # Validity + flags
        self._validity: SpellValidity = SpellValidity.unknown
        self._flags: Set[SpellState] = set()
        self._flags.add(SpellState.new_index)

        self._change_reason: SpellStateChangeReason | None = SpellStateChangeReason.new_index
        self._transitively_dirty: bool = False
        self._last_validated_at: Optional[float] = None
        self._risk_manager: Optional[RiskManager] = None

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Explicitly dispose references and mark this state as cleaned.

        Follows the Melder cleanup pattern:
        - idempotent
        - guarded by an internal lock
        - null-out references to assist GC

        Contract:
            - Clears topology and flag collections before dropping identity and
              validity fields.
            - Detaches the `RiskManager` reference so no later validity changes
              can be published accidentally.
            - Leaves future callers to fail through `check_cleaned()`.

        Returns:
            None.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True

            if self._direct_dependencies is not None:
                self._direct_dependencies.clear()
            if self._direct_dependents is not None:
                self._direct_dependents.clear()
            if self._flags is not None:
                self._flags.clear()
            self._transitively_dirty = False

            del self._direct_dependents
            del self._flags
            del self._direct_dependencies
            del self._validity
            del self._change_reason
            del self._last_validated_at
            del self._risk_manager
            del self._spell_index_id
            del self._current_spell_id

        # Drop lock last
        del self._lock

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def spell_index_id(self) -> str:
        """
        Index identifier (ULID from SpellIndex.id).

        Note:
            This assumes the state has not been cleaned; check_cleaned()
            will raise if cleanup() has been called.
        Threading:
            Acquires the internal lock to avoid torn reads while mutation
            helpers are updating index state.
        """
        
        with self._lock:
            return self._spell_index_id

    @property
    def current_spell_id(self) -> str:
        """
        Currently promoted version id for this index (e.g., SpellIndex.selected_spell_id).

        Threading:
            Acquires the internal lock to avoid torn reads while promotion
            updates are in flight.
        """
        
        with self._lock:
            return self._current_spell_id

    @property
    def direct_dependencies(self) -> Set[str]:
        """
        Snapshot of direct dependencies for this index.

        Returns:
            A plain set[str] copy so callers cannot mutate internal state.
        """
        
        with self._lock:
            if self._direct_dependencies is None:
                return set()
            return set(self._direct_dependencies)

    @property
    def direct_dependents(self) -> Set[str]:
        """
        Snapshot of direct dependents for this index.

        Returns:
            A plain set[str] copy so callers cannot mutate internal state.
        """
        
        with self._lock:
            if self._direct_dependents is None:
                return set()
            return set(self._direct_dependents)

    @property
    def validity(self) -> SpellValidity:
        """
        Structural validity gate for this index (unknown/valid/gated/invalid/disabled).

        Note:
            This is the *global* structural verdict for Phases 1-4 only. Per-conduit
            resolution validity for Phases 5-7 lives in ConduitResolutionState.
        Threading:
            Acquires the internal lock to avoid torn reads across validity transitions.
        """
        
        with self._lock:
            return self._validity

    @property
    def flags(self) -> Set[SpellState]:
        """
        Snapshot of SpellStateFlag markers for this index.

        Returns:
            A plain set[SpellStateFlag] copy so callers cannot mutate internal state.
        """
        
        with self._lock:
            if self._flags is None:
                return set()
            return set(self._flags)

    @property
    def change_reason(self) -> Optional[SpellStateChangeReason]:
        """
        Last event that changed this index's validity/flags.

        This is meant for DevOps / AI surfaces and TOON snapshots.
        Threading:
            Acquires the internal lock to avoid torn reads across validity transitions.
        """
        
        with self._lock:
            return self._change_reason

    @property
    def transitively_dirty(self) -> bool:
        """
        True if this index is impacted indirectly by upstream changes
        (dependency_changed closure).
        Threading:
            Acquires the internal lock to avoid torn reads across transitions.
        """
        
        with self._lock:
            return self._transitively_dirty

    @property
    def last_validated_at(self) -> Optional[float]:
        """
        Timestamp (seconds) of last successful validation, or None if never.
        Threading:
            Acquires the internal lock to avoid torn reads across transitions.
        """
        
        with self._lock:
            return self._last_validated_at

    @property
    def dirty(self) -> bool:
        """
        Convenience view: index is considered "dirty" if it is not valid.

        This is derived from `validity` and is mainly for legacy / quick checks.
        Threading:
            Acquires the internal lock to avoid torn reads across validity transitions.
        """
        
        with self._lock:
            v = self._validity
        return v is not None and v is not SpellValidity.valid

    # ------------------------------------------------------------------
    # Internal helper for validity/flags
    # ------------------------------------------------------------------
    def set_validity(
            self,
            validity: SpellValidity,
            *,
            change_reason: Optional[SpellStateChangeReason] = None,
            flags_to_add: Optional[Iterable[SpellState]] = None,
            flags_to_remove: Optional[Iterable[SpellState]] = None,
            transitively_dirty: Optional[bool] = None,
    ) -> None:
        """
        Core helper for updating validity/flags/change_reason in one shot.

        This is what higher-level helpers (mark_structural_change, etc.) use
        so that state transitions remain consistent and centralized.

        Args:
            validity: New SpellValidity to assign.
            change_reason: Optional reason code describing this transition.
            flags_to_add: Optional iterable of SpellState flags to add.
            flags_to_remove: Optional iterable of SpellState flags to remove.
            transitively_dirty: Optional bool to set the transitively_dirty flag.
        Contract:
            - Applies validity, flags, change reason, and transitive-dirty state
              as one coordinated transition.
            - Publishes to `RiskManager` only when the structural validity value
              itself changes; flag-only updates stay local.
            - Ignores None entries in add/remove flag iterables.

        Returns:
            None.
        """
        
        callback = None
        if self._risk_manager is not None:
            callback = self._risk_manager.on_structural_validity_change
        index_id = self._spell_index_id
        with self._lock:
            if self._flags is None:
                # Already cleaned; guard check should have prevented this.
                return

            previous_validity = self._validity
            self._validity = validity

            if change_reason is not None:
                self._change_reason = change_reason

            if flags_to_add is not None:
                for f in flags_to_add:
                    if f is not None:
                        self._flags.add(f)

            if flags_to_remove is not None:
                for f in flags_to_remove:
                    if f is not None:
                        self._flags.discard(f)

            if transitively_dirty is not None:
                self._transitively_dirty = transitively_dirty

        if (
                callback is not None
                and index_id is not None
                and previous_validity is not validity
        ):
            try:
                callback(index_id, validity)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Mutation helpers (used by manager / DevOps layer)
    # ------------------------------------------------------------------
    def update_current_spell_id(self, spell_id: str) -> None:
        """
        Update the currently promoted version id for this index.

        Caller is responsible for keeping the manager's spell-id index in sync.

        Args:
            spell_id: New current spell version id (non-empty).
        Contract:
            - Updates index identity for the promoted spell version only.
            - Does not change validity, flags, dependency edges, or dirty state.

        Raises:
            ValueError: If spell_id is empty.
            RuntimeError: If this state object has been cleaned.

        Returns:
            None.
        """
        
        if not spell_id:
            raise ValueError("spell_id cannot be empty")

        with self._lock:
            self._current_spell_id = spell_id

    def attach_dependencies(self, dependency_ids: Iterable[str]) -> None:
        """
        Replace the direct-dependency set for this index.

        The manager is responsible for keeping reverse edges up to date.

        Args:
            dependency_ids: Iterable of dependency ids (falsy entries ignored).
        Contract:
            - Treats the supplied iterable as the full desired dependency set.
            - Rebuilds the stored dependency set rather than mutating it
              incrementally, so stale edges do not survive.
            - Does not update reverse dependents; the owning manager handles
              reverse-edge maintenance separately.
        Raises:
            RuntimeError: If this state object has been cleaned.

        Returns:
            None.
        """
        

        deps = {d for d in dependency_ids if d}
        with self._lock:
            # Rebuild as a fresh concurrent set to avoid stale contents.
            self._direct_dependencies = set(deps)

    def add_dependent(self, index_id: str) -> None:
        """
        Register that another index depends on this index.

        Args:
            index_id: Index id to add as a dependent.
        Contract:
            - Adds one reverse-edge entry if the id is non-empty.
            - Does not dirty or revalidate the index; this is topology
              bookkeeping only.

        Returns:
            None.
        """
        
        if not index_id:
            return
        with self._lock:
            if self._direct_dependents is not None:
                self._direct_dependents.add(index_id)

    def remove_dependent(self, index_id: str) -> None:
        """
        Remove a dependent index from this index's reverse edges.

        Args:
            index_id: Index id to remove from dependents.
        Contract:
            - Best-effort removes the reverse-edge entry if present.
            - Missing or empty ids are ignored so caller cleanup can stay
              idempotent.

        Returns:
            None.
        """
        
        if not index_id:
            return
        with self._lock:
            if self._direct_dependents is not None:
                self._direct_dependents.discard(index_id)

    def mark_structural_change(
            self,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Mark this index as structurally changed.

        Typical triggers:
        - New version promoted.
        - Class/method profile changed.
        - Binding semantics changed in a way that affects structure.

        Args:
            change_reason: Optional reason override; defaults to structure_changed.
        Contract:
            - Gates the index structurally.
            - Adds the `structure_changed` flag.
            - Forces `transitively_dirty` to False because this helper models a
              direct change to the index itself, not downstream impact.

        Returns:
            None.
        """
        
        if change_reason is None:
            change_reason = SpellStateChangeReason.structure_changed

        self.set_validity(
            SpellValidity.gated,
            change_reason=change_reason,
            flags_to_add=[SpellState.structure_changed],
            transitively_dirty=False,
        )

    def mark_dependency_change(
            self,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Mark this index as dirty due to direct dependency changes.

        This does *not* automatically mark it as transitively dirty; the manager
        decides how to propagate closure.

        Args:
            change_reason: Optional reason override; defaults to dependencies_changed.
        Contract:
            - Gates the index.
            - Adds the `dependencies_changed` flag.
            - Leaves `transitively_dirty` unchanged unless a higher-level
              closure pass decides this index is only indirectly impacted.

        Returns:
            None.
        """
        
        if change_reason is None:
            change_reason = SpellStateChangeReason.dependencies_changed

        self.set_validity(
            SpellValidity.gated,
            change_reason=change_reason,
            flags_to_add=[SpellState.dependencies_changed],
        )

    def mark_transitively_dirty(
            self,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Mark this index as impacted indirectly by upstream changes.

        This is typically called by the manager during impact-closure expansion.

        Args:
            change_reason: Optional reason override; defaults to dependency_changed.
        Contract:
            - Gates the index.
            - Adds the `impacted_by_dependency` flag.
            - Sets `transitively_dirty` to True so callers can distinguish
              downstream fallout from direct structural changes.

        Returns:
            None.
        """
        
        if change_reason is None:
            change_reason = SpellStateChangeReason.dependency_changed

        self.set_validity(
            SpellValidity.gated,
            change_reason=change_reason,
            flags_to_add=[SpellState.impacted_by_dependency],
            transitively_dirty=True,
        )

    def clear_dirty(self, last_validated_at: Optional[float]) -> None:
        """
        Mark this index as clean after successful validation.

        Behaviour:
        - validity -> SpellValidity.valid
        - topology-related flags (new_index / structure_changed /
          dependencies_changed / impacted_by_dependency) are cleared.
        - transitively_dirty -> False
        - last_validated_at is set to the provided timestamp.

        Note:
        - Contract/mutation/ops flags are *not* cleared here; the subsystems
          that own those lifecycles should flip them explicitly.

        Args:
            last_validated_at: Timestamp (seconds) of successful validation.
        Contract:
            - Clears only topology/registration dirty markers.
            - Leaves contract, mutation, and ops flags untouched because those
              subsystems own their own cleanup semantics.
            - Publishes `SpellValidity.valid` to `RiskManager` only when this
              call actually changes the stored validity.

        Returns:
            None.
        """
        
        callback = None
        if self._risk_manager is not None:
            callback = self._risk_manager.on_structural_validity_change
        index_id = self._spell_index_id
        with self._lock:
            if self._flags is not None:
                self._flags.discard(SpellState.new_index)
                self._flags.discard(SpellState.structure_changed)
                self._flags.discard(SpellState.dependencies_changed)
                self._flags.discard(SpellState.impacted_by_dependency)

            previous_validity = self._validity
            self._validity = SpellValidity.valid
            self._change_reason = None
            self._transitively_dirty = False
            self._last_validated_at = last_validated_at

        if (
                callback is not None
                and index_id is not None
                and previous_validity is not SpellValidity.valid
        ):
            try:
                callback(index_id, SpellValidity.valid)
            except Exception:
                pass

    def _set_risk_manager(self, risk_manager: Optional[RiskManager]) -> None:
        """
        Attach or detach the `RiskManager` callback reference.

        This is a wiring helper used by the owning registry. It does not replay
        historical index state; it only controls where future validity
        transitions are published.
        """
        self._risk_manager = risk_manager
