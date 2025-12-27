import threading
from typing import Iterable, Optional, Set, List
# Melder imports
from melder.aether.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellSystemState(Cleanable):
    """
    System-level state for a single spell lineage: topology, validity, and flags.

    Identity
    --------
    - `spell_index_id`:
        Lineage identifier (ULID from SpellIndex.id).
    - `current_spell_id`:
        Currently promoted version id for this lineage (e.g., SpellIndex.current; typically a SHA).

    Topology
    --------
    - `direct_dependencies`:
        Set of dependency ids for this lineage. Caller decides whether ids are lineage or version ids.
    - `direct_dependents`:
        Reverse edges: lineages that depend on this lineage ("what breaks if this changes?").

    Validity / State
    ----------------
    - `validity`:
        Structural validity gate (unknown / valid / gated / invalid / disabled).
        This only reflects *global* spell-definition correctness (Phases 1-4),
        not conduit-specific resolution state.
    - `flags`:
        Fine-grained SpellState markers describing *why* the lineage is in its current condition
        (topology changes, contracts, mutation, ops).
    - `change_reason`:
        Last SpellStateChangeReason that moved this lineage into its current validity/flags.
    - `transitively_dirty`:
        True if impacted indirectly by upstream changes (dependency_changed closure).
    - `last_validated_at`:
        Optional timestamp (float seconds) of last *successful* structural validation.
    """
    __melder_internal__ = _mrg.sentinel
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
    ]

    def __init__(self, spell_index_id: str, current_spell_id: str) -> None:
        super().__init__()

        if not spell_index_id:
            raise ValueError("spell_index_id cannot be empty")
        if not current_spell_id:
            raise ValueError("current_spell_id cannot be empty")

        self._lock: threading.RLock = threading.RLock()
        self._spell_index_id: Optional[str] = spell_index_id
        self._current_spell_id: Optional[str] = current_spell_id

        # Concurrent topology sets
        self._direct_dependencies: Optional[Set[str]] = set()
        self._direct_dependents: Optional[Set[str]] = set()

        # Validity + flags
        self._validity: Optional[SpellValidity] = SpellValidity.unknown
        self._flags: Optional[Set[SpellState]] = set()
        self._flags.add(SpellState.new_lineage)

        self._change_reason: Optional[SpellStateChangeReason] = SpellStateChangeReason.new_lineage
        self._transitively_dirty: bool = False
        self._last_validated_at: Optional[float] = None

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
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            if self._direct_dependencies is not None:
                self._direct_dependencies.clear()
                self._direct_dependencies = None

            if self._direct_dependents is not None:
                self._direct_dependents.clear()
                self._direct_dependents = None

            if self._flags is not None:
                self._flags.clear()
                self._flags = None

            self._validity = None
            self._change_reason = None
            self._transitively_dirty = False
            self._last_validated_at = None

            self._spell_index_id = None
            self._current_spell_id = None

        # Drop lock last
        self._lock = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def spell_index_id(self) -> str:
        """
        Lineage identifier (ULID from SpellIndex.id).

        Note:
            This assumes the state has not been cleaned; check_cleaned()
            will raise if cleanup() has been called.
        """
        self.check_cleaned()
        return self._spell_index_id

    @property
    def current_spell_id(self) -> str:
        """
        Currently promoted version id for this lineage (e.g., SpellIndex.current).
        """
        self.check_cleaned()
        return self._current_spell_id

    @property
    def direct_dependencies(self) -> Set[str]:
        """
        Snapshot of direct dependencies for this lineage.

        Returns:
            A plain set[str] copy so callers cannot mutate internal state.
        """
        self.check_cleaned()
        with self._lock:
            if self._direct_dependencies is None:
                return set()
            return set(self._direct_dependencies)

    @property
    def direct_dependents(self) -> Set[str]:
        """
        Snapshot of direct dependents for this lineage.

        Returns:
            A plain set[str] copy so callers cannot mutate internal state.
        """
        self.check_cleaned()
        with self._lock:
            if self._direct_dependents is None:
                return set()
            return set(self._direct_dependents)

    @property
    def validity(self) -> SpellValidity:
        """
        Structural validity gate for this lineage (unknown/valid/gated/invalid/disabled).

        Note:
            This is the *global* structural verdict for Phases 1-4 only. Per-conduit
            resolution validity for Phases 5-7 lives in ConduitResolutionState.
        """
        self.check_cleaned()
        return self._validity

    @property
    def flags(self) -> Set[SpellState]:
        """
        Snapshot of SpellStateFlag markers for this lineage.

        Returns:
            A plain set[SpellStateFlag] copy so callers cannot mutate internal state.
        """
        self.check_cleaned()
        with self._lock:
            if self._flags is None:
                return set()
            return set(self._flags)

    @property
    def change_reason(self) -> Optional[SpellStateChangeReason]:
        """
        Last event that changed this lineage's validity/flags.

        This is meant for DevOps / AI surfaces and TOON snapshots.
        """
        self.check_cleaned()
        return self._change_reason

    @property
    def transitively_dirty(self) -> bool:
        """
        True if this lineage is impacted indirectly by upstream changes
        (dependency_changed closure).
        """
        self.check_cleaned()
        return self._transitively_dirty

    @property
    def last_validated_at(self) -> Optional[float]:
        """
        Timestamp (seconds) of last successful validation, or None if never.
        """
        self.check_cleaned()
        return self._last_validated_at

    @property
    def dirty(self) -> bool:
        """
        Convenience view: lineage is considered "dirty" if it is not valid.

        This is derived from `validity` and is mainly for legacy / quick checks.
        """
        self.check_cleaned()
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
        """
        self.check_cleaned()
        with self._lock:
            if self._flags is None:
                # Already cleaned; guard check should have prevented this.
                return

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

    # ------------------------------------------------------------------
    # Mutation helpers (used by manager / DevOps layer)
    # ------------------------------------------------------------------
    def update_current_spell_id(self, spell_id: str) -> None:
        """
        Update the currently promoted version id for this lineage.

        Caller is responsible for keeping the manager's spell-id index in sync.

        Args:
            spell_id: New current spell version id (non-empty).

        Raises:
            ValueError: If spell_id is empty.
            RuntimeError: If this state object has been cleaned.
        """
        self.check_cleaned()
        if not spell_id:
            raise ValueError("spell_id cannot be empty")

        with self._lock:
            self._current_spell_id = spell_id

    def attach_dependencies(self, dependency_ids: Iterable[str]) -> None:
        """
        Replace the direct-dependency set for this lineage.

        The manager is responsible for keeping reverse edges up to date.

        Args:
            dependency_ids: Iterable of dependency ids (falsy entries ignored).
        Raises:
            RuntimeError: If this state object has been cleaned.
        """
        self.check_cleaned()

        deps = {d for d in dependency_ids if d}
        with self._lock:
            # Rebuild as a fresh concurrent set to avoid stale contents.
            self._direct_dependencies = set(deps)

    def add_dependent(self, index_id: str) -> None:
        """
        Register that another lineage depends on this lineage.

        Args:
            index_id: Lineage id to add as a dependent.
        """
        self.check_cleaned()
        if not index_id:
            return
        with self._lock:
            if self._direct_dependents is not None:
                self._direct_dependents.add(index_id)

    def remove_dependent(self, index_id: str) -> None:
        """
        Remove a dependent lineage from this lineage's reverse edges.

        Args:
            index_id: Lineage id to remove from dependents.
        """
        self.check_cleaned()
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
        Mark this lineage as structurally changed.

        Typical triggers:
        - New version promoted.
        - Class/method profile changed.
        - Binding semantics changed in a way that affects structure.

        Args:
            change_reason: Optional reason override; defaults to structure_changed.
        """
        self.check_cleaned()
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
        Mark this lineage as dirty due to direct dependency changes.

        This does *not* automatically mark it as transitively dirty; the manager
        decides how to propagate closure.

        Args:
            change_reason: Optional reason override; defaults to dependencies_changed.
        """
        self.check_cleaned()
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
        Mark this lineage as impacted indirectly by upstream changes.

        This is typically called by the manager during impact-closure expansion.

        Args:
            change_reason: Optional reason override; defaults to dependency_changed.
        """
        self.check_cleaned()
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
        Mark this lineage as clean after successful validation.

        Behaviour:
        - validity → SpellValidity.valid
        - topology-related flags (new_lineage / structure_changed /
          dependencies_changed / impacted_by_dependency) are cleared.
        - transitively_dirty → False
        - last_validated_at is set to the provided timestamp.

        Note:
        - Contract/mutation/ops flags are *not* cleared here; the subsystems
          that own those lifecycles should flip them explicitly.

        Args:
            last_validated_at: Timestamp (seconds) of successful validation.
        """
        self.check_cleaned()
        with self._lock:
            if self._flags is not None:
                self._flags.discard(SpellState.new_lineage)
                self._flags.discard(SpellState.structure_changed)
                self._flags.discard(SpellState.dependencies_changed)
                self._flags.discard(SpellState.impacted_by_dependency)

            self._validity = SpellValidity.valid
            self._change_reason = None
            self._transitively_dirty = False
            self._last_validated_at = last_validated_at
