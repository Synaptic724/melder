import threading
from typing import Iterable, Optional, Set, List, Dict
# Melder imports
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpell, ISpellIndex, ISpellSystemStates


class SpellSystemStates(Cleanable):
    """
    Per-frame registry for all SpellSystemState instances.

    This is the "control tower" object:

    - Owns the index: lineage id -> SpellSystemState.
    - Keeps an auxiliary index: current_spell_id -> SpellSystemState
      (for convenience when you only know the version id).
    - Tracks which lineages are currently dirty so higher-level
      DevOps/validation flows can decide what to re-run.

    Intended lifecycle:

    - One instance per AethericFrame (owned by the frame and initialized
      alongside Spellbook / DevOpsManager).
    - Spellbook / SpellCrafter call:
        * `register_lineage(...)` when a new SpellIndex+Spell appears
        * `update_dependencies(...)` after Phase 3/4 attaches dependency ids
        * `mark_structural_change(...)` when a lineage is rebound/mutated
    - DevOps / validation flows call:
        * `consume_dirty_lineages(...)` to get a worklist
        * `compute_impact_closure(...)` to fan out impacted lineages
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_frame",
        "_states_by_index_id",
        "_states_by_spell_id",
        "_dirty_lineages",
    ]

    def __init__(self, frame: "AethericFrame") -> None:
        """
        Initialize the SpellSystemStates registry for a given AethericFrame.

        The frame is only stored as an opaque handle so higher layers can
        associate this registry with its owning frame; this class does not
        call back into the frame.
        """
        super().__init__()

        if frame is None:
            raise ValueError("frame cannot be None")

        self._lock: threading.RLock = threading.RLock()
        self._frame: Optional["AethericFrame"] = frame

        self._states_by_index_id: Optional[Dict[str, SpellSystemState]] = {}
        self._states_by_spell_id: Optional[Dict[str, SpellSystemState]] = {}
        self._dirty_lineages: Optional[Set[str]] = set()

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Cleanup all SpellSystemState instances and dispose internal indexes.

        Idempotent and lock-guarded:

        - Marks this registry as cleaned.
        - Calls cleanup() on all child SpellSystemState objects.
        - Cleans and nulls all ConcurrentDict / ConcurrentSet instances.
        - Drops the frame reference and lock to assist GC.

        After cleanup(), all public methods will raise via check_cleaned().
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            if self._states_by_index_id is not None:
                # Explicitly clean child state objects first.
                for state in list(self._states_by_index_id.values()):
                    state.cleanup()
                self._states_by_index_id.clear()
                self._states_by_index_id = None

            if self._states_by_spell_id is not None:
                self._states_by_spell_id.clear()
                self._states_by_spell_id = None

            if self._dirty_lineages is not None:
                self._dirty_lineages.clear()
                self._dirty_lineages = None

            self._frame = None

        # Drop lock last
        self._lock = None

    # ------------------------------------------------------------------
    # Registration / lookup
    # ------------------------------------------------------------------
    def register_lineage(self, spell_index: ISpellIndex, spell: ISpell) -> SpellSystemState:
        """
        Ensure a SpellSystemState exists for the given lineage and return it.

        Behaviour:
        - If this is the first time we see `spell_index.id`, create a new
          SpellSystemState with `spell_index.current` as the current_spell_id.
        - If it already exists, update its current_spell_id to match
          `spell_index.current`.
        - Update the spell-id index so `get_by_spell_id(...)` can resolve
          by current version id.
        - Mark the lineage as structurally gated with reason
          SpellStateChangeReason.register_or_rebind and add it to the dirty set.

        This is intended to be called from Spellbook.bind(...) or equivalent.
        """
        self.check_cleaned()

        if spell_index is None:
            raise ValueError("spell_index cannot be None")
        if spell is None:
            raise ValueError("spell cannot be None")

        index_id = spell_index.id
        current_id = spell_index.current

        with self._lock:
            if self._states_by_index_id is None or self._states_by_spell_id is None or self._dirty_lineages is None:
                raise RuntimeError("SpellSystemStates has been cleaned")

            state = self._states_by_index_id.get(index_id)
            if state is None:
                state = SpellSystemState(index_id, current_id)
                self._states_by_index_id[index_id] = state
            else:
                # Keep current version id in sync
                state.update_current_spell_id(current_id)

            # Refresh the spell-id index as well
            self._states_by_spell_id[current_id] = state

            # Any (re)binding is treated as structural change.
            state.mark_structural_change(change_reason=SpellStateChangeReason.register_or_rebind)
            self._dirty_lineages.add(index_id)

            return state

    def get_by_index_id(self, index_id: str) -> Optional[SpellSystemState]:
        """
        Lookup a SpellSystemState by lineage id.

        Returns:
            - The SpellSystemState instance for this lineage, or
            - None if no state has been registered for the id.
        """
        self.check_cleaned()
        if not index_id:
            return None
        with self._lock:
            if self._states_by_index_id is None:
                return None
            return self._states_by_index_id.get(index_id)

    def get_by_spell_id(self, spell_id: str) -> Optional[SpellSystemState]:
        """
        Lookup a SpellSystemState by current spell version id.

        This is a convenience when the caller only knows the version id
        (e.g., SpellIndex.current) and wants to find the associated lineage state.

        Returns:
            - The SpellSystemState instance, or
            - None if no state is currently indexed for that spell id.
        """
        self.check_cleaned()
        if not spell_id:
            return None
        with self._lock:
            if self._states_by_spell_id is None:
                return None
            return self._states_by_spell_id.get(spell_id)

    # ------------------------------------------------------------------
    # Dependency wiring (Phase 3/4 integration)
    # ------------------------------------------------------------------
    def update_dependencies(self, spell_index: ISpellIndex, dependency_ids: Iterable[str]) -> None:
        """
        Attach direct dependency ids for this lineage and update reverse edges.

        `dependency_ids` are generic "spell ids" (version or lineage ids) – the
        SpellCrafter / Spellbook decides the semantics. This manager only
        cares about connectivity, not the type system.

        Behaviour:
        - Ensure there is a SpellSystemState for this lineage (create if missing).
        - Compute the delta between previous and new dependency sets.
        - Remove reverse edges from dependencies we no longer reference.
        - Add reverse edges for new dependencies.
        - Mark this lineage as gated due to dependency change and add to
          `_dirty_lineages`.
        """
        self.check_cleaned()
        if spell_index is None:
            raise ValueError("spell_index cannot be None")

        index_id = spell_index.id
        new_deps = {d for d in (dependency_ids or []) if d}

        with self._lock:
            if self._states_by_index_id is None or self._states_by_spell_id is None or self._dirty_lineages is None:
                return

            state = self._states_by_index_id.get(index_id)
            if state is None:
                # Defensive: create on first use if not present
                state = SpellSystemState(index_id, spell_index.current)
                self._states_by_index_id[index_id] = state

            old_deps = set(state.direct_dependencies)

            # Remove reverse edges for dependencies no longer referenced
            removed = old_deps - new_deps
            for dep_id in removed:
                dep_state = self._states_by_spell_id.get(dep_id)
                if dep_state is not None:
                    dep_state.remove_dependent(index_id)

            # Attach new dependencies and update reverse edges
            state.attach_dependencies(new_deps)
            for dep_id in new_deps:
                dep_state = self._states_by_spell_id.get(dep_id)
                if dep_state is not None:
                    dep_state.add_dependent(index_id)

            # Mark this lineage gated due to dependency changes
            state.mark_dependency_change()
            self._dirty_lineages.add(index_id)

    # ------------------------------------------------------------------
    # Dirty / impact queries (used by DevOps / validation governor)
    # ------------------------------------------------------------------
    def mark_structural_change(
            self,
            spell_index: ISpellIndex,
            reason: SpellStateChangeReason = SpellStateChangeReason.structure_changed,
    ) -> None:
        """
        Mark a lineage as structurally changed.

        Typical triggers:
        - New version promoted.
        - Class/method profile changed.
        - Binding semantics changed in a way that affects structure.

        Behaviour:
        - Ensure a SpellSystemState exists for the lineage.
        - Mark it structurally gated with the provided reason.
        - Add the lineage id to `_dirty_lineages`.
        """
        self.check_cleaned()
        if spell_index is None:
            raise ValueError("spell_index cannot be None")

        index_id = spell_index.id
        with self._lock:
            if self._states_by_index_id is None or self._dirty_lineages is None:
                return

            state = self._states_by_index_id.get(index_id)
            if state is None:
                state = SpellSystemState(index_id, spell_index.current)
                self._states_by_index_id[index_id] = state

            state.mark_structural_change(change_reason=reason)
            self._dirty_lineages.add(index_id)

    def compute_impact_closure(self, root_index_ids: Iterable[str]) -> Set[str]:
        """
        Compute the transitive closure of impacted lineages downstream.

        Args:
            root_index_ids:
                Lineage ids that changed *directly* (e.g., newly promoted or
                structurally altered).

        Behaviour:
        - Walk reverse edges (`direct_dependents`) starting from each root.
        - Build a set of all lineages that depend (directly or indirectly)
          on any of the roots.
        - For each impacted lineage:
            * Roots: left in their existing structural state (already gated).
            * Non-roots: marked as transitively dirty (impacted_by_dependency).
        - All impacted lineages are added to `_dirty_lineages`.

        Returns:
            A set of all impacted lineage ids, including the roots.
        """
        self.check_cleaned()

        impacted: Set[str] = set()
        worklist: List[str] = [index_id for index_id in root_index_ids if index_id]

        with self._lock:
            if self._states_by_index_id is None or self._dirty_lineages is None:
                return impacted

            while worklist:
                current = worklist.pop()
                if current in impacted:
                    continue
                impacted.add(current)

                state = self._states_by_index_id.get(current)
                if state is None:
                    continue

                dependents = state.direct_dependents
                for dependent_id in dependents:
                    if dependent_id not in impacted:
                        worklist.append(dependent_id)

            # Mark all impacted lineages as dirty; roots remain
            # structurally gated, others become transitively gated.
            root_set = set(root_index_ids)
            for index_id in impacted:
                state = self._states_by_index_id.get(index_id)
                if state is None:
                    continue

                if index_id in root_set:
                    # Already marked structurally gated; leave as-is.
                    pass
                else:
                    state.mark_transitively_dirty()

                self._dirty_lineages.add(index_id)

        return impacted

    def consume_dirty_lineages(self) -> List[str]:
        """
        Pop and return the current set of dirty lineage ids.

        This is the handoff to whatever runs the revalidation / mutation
        governor (your "Phase 5–7" or equivalent).

        Behaviour:
        - Snapshot all ids currently in `_dirty_lineages`.
        - Clear `_dirty_lineages`.
        - Return the snapshot list. Order is unspecified.
        """
        self.check_cleaned()
        with self._lock:
            if self._dirty_lineages is None or not self._dirty_lineages:
                return []
            pending = list(self._dirty_lineages)
            self._dirty_lineages.clear()
            return pending

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------
    def iter_states(self) -> List[SpellSystemState]:
        """
        Snapshot of all SpellSystemState instances currently registered.

        Returns:
            A list of SpellSystemState objects. The list is detached from the
            underlying ConcurrentDict so callers cannot accidentally keep a
            live iterator into internal state.
        """
        self.check_cleaned()
        with self._lock:
            if self._states_by_index_id is None:
                return []
            return list(self._states_by_index_id.values())
