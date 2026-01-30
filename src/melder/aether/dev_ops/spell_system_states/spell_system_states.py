import threading
from typing import Iterable, Optional, Set, List, Dict, Iterator, Mapping, Sequence, Tuple
# Melder imports
from melder.aether.dev_ops.spell_system_states.conduit_resolution_state import (
    ConduitResolutionState,
)
from melder.aether.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.system.system_diagnostic import SystemDiagnostic
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpell, ISpellIndex, ISpellSystemStates
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellSystemStates(Cleanable, ISpellSystemStates):
    """
    Per-frame registry for all SpellSystemState instances.

    This is the "control tower" object:

    - Owns the index: lineage id -> SpellSystemState.
    - Keeps an auxiliary index: current_spell_id -> SpellSystemState
      (for convenience when you only know the version id).
    - Tracks which lineages are currently dirty so higher-level
      DevOps/validation flows can decide what to re-run.
    - Tracks collection dependency indices per Spellbook so targeted
      revalidation can gate only local list[Frame] consumers.
    - Tracks SpellContract consumer indices per Spellbook so contract
      changes can dirty only relevant lineages.

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
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_frame",
        "_states_by_index_id",
        "_states_by_spell_id",
        "_dirty_lineages",
        "_local_topologies",
        "_resolution_by_conduit_id",
        "_lineage_owner_spellbook_id",
        "_collection_frames_by_lineage",
        "_collection_dependents_by_spellbook",
        "_contract_keys_by_lineage",
        "_contract_dependents_by_spellbook",
        "_risk_manager",
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
        # Version-id keyed topologies captured during Phase 3.
        self._local_topologies: Dict[str, 'SpellLocalTopology'] = {}
        # Per-conduit resolution state for Phases 5-7.
        self._resolution_by_conduit_id: Optional[Dict[str, ConduitResolutionState]] = {}
        # Spellbook-scoped indices for collection dependencies (list[Frame]).
        self._lineage_owner_spellbook_id: Optional[Dict[str, str]] = {}
        self._collection_frames_by_lineage: Optional[Dict[str, Set[str]]] = {}
        self._collection_dependents_by_spellbook: Optional[Dict[str, Dict[str, Set[str]]]] = {}
        # Spellbook-scoped indices for SpellContract dependents.
        self._contract_keys_by_lineage: Optional[Dict[str, Set[Tuple[str, str]]]] = {}
        self._contract_dependents_by_spellbook: Optional[Dict[str, Dict[Tuple[str, str], Set[str]]]] = {}
        self._risk_manager: Optional[object] = None

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

            if self._local_topologies is not None:
                try:
                    for topology in list(self._local_topologies.values()):
                        if topology is not None:
                            topology.cleanup()
                except Exception:
                    pass
                self._local_topologies.clear()
                self._local_topologies = None
            if self._resolution_by_conduit_id is not None:
                for state in list(self._resolution_by_conduit_id.values()):
                    try:
                        state.cleanup()
                    except Exception:
                        pass
                self._resolution_by_conduit_id.clear()
                self._resolution_by_conduit_id = None

            if self._collection_dependents_by_spellbook is not None:
                for book_map in list(self._collection_dependents_by_spellbook.values()):
                    try:
                        for dependents in list(book_map.values()):
                            dependents.clear()
                    except Exception:
                        pass
                    book_map.clear()
                self._collection_dependents_by_spellbook.clear()
                self._collection_dependents_by_spellbook = None

            if self._collection_frames_by_lineage is not None:
                for frames in list(self._collection_frames_by_lineage.values()):
                    try:
                        frames.clear()
                    except Exception:
                        pass
                self._collection_frames_by_lineage.clear()
                self._collection_frames_by_lineage = None

            if self._contract_dependents_by_spellbook is not None:
                for book_map in list(self._contract_dependents_by_spellbook.values()):
                    try:
                        for dependents in list(book_map.values()):
                            dependents.clear()
                    except Exception:
                        pass
                    book_map.clear()
                self._contract_dependents_by_spellbook.clear()
                self._contract_dependents_by_spellbook = None

            if self._contract_keys_by_lineage is not None:
                for keys in list(self._contract_keys_by_lineage.values()):
                    try:
                        keys.clear()
                    except Exception:
                        pass
                self._contract_keys_by_lineage.clear()
                self._contract_keys_by_lineage = None

            if self._lineage_owner_spellbook_id is not None:
                self._lineage_owner_spellbook_id.clear()
                self._lineage_owner_spellbook_id = None

            self._frame = None
            self._risk_manager = None

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
        - Record the owning Spellbook id for targeted, spellbook-scoped
          collection revalidation.
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
                if self._risk_manager is not None:
                    state._set_risk_manager(self._risk_manager)
                self._states_by_index_id[index_id] = state
            else:
                # Keep current version id in sync
                state.update_current_spell_id(current_id)

            # Refresh the spell-id index as well
            self._states_by_spell_id[current_id] = state

            owner_spellbook_id = self._resolve_spellbook_id(spell)
            if owner_spellbook_id is not None and self._lineage_owner_spellbook_id is not None:
                existing_owner = self._lineage_owner_spellbook_id.get(index_id)
                if existing_owner is not None and existing_owner != owner_spellbook_id:
                    self._remove_lineage_from_collection_index(existing_owner, index_id)
                    self._remove_lineage_from_contract_index(existing_owner, index_id)
                    if self._collection_frames_by_lineage is not None:
                        self._collection_frames_by_lineage.pop(index_id, None)
                self._lineage_owner_spellbook_id[index_id] = owner_spellbook_id

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
    # Internal indexing helpers
    # ------------------------------------------------------------------
    def _resolve_spellbook_id(self, spell: ISpell) -> Optional[str]:
        """
        Internal

        Resolve the owning Spellbook id for a spell, if available.

        Args:
            spell: Spell instance that may carry a Spellbook reference.
        Returns:
            Optional[str]: Spellbook id or None if unavailable.
        """
        if spell is None:
            return None
        try:
            spellbook = spell._spellbook
        except AttributeError:
            return None
        if spellbook is None:
            return None
        try:
            return spellbook._id
        except AttributeError:
            return None

    def _remove_lineage_from_collection_index(
            self,
            spellbook_id: str,
            lineage_id: str,
    ) -> None:
        """
        Internal

        Remove a lineage from the collection-dependency index for a spellbook.
        """
        if not spellbook_id or not lineage_id:
            return
        if (
            self._collection_dependents_by_spellbook is None
            or self._collection_frames_by_lineage is None
        ):
            return

        frames = self._collection_frames_by_lineage.get(lineage_id)
        if not frames:
            return

        book_index = self._collection_dependents_by_spellbook.get(spellbook_id)
        if not book_index:
            return

        for frame_key in frames:
            dependents = book_index.get(frame_key)
            if dependents is None:
                continue
            dependents.discard(lineage_id)
            if not dependents:
                book_index.pop(frame_key, None)

        if not book_index:
            self._collection_dependents_by_spellbook.pop(spellbook_id, None)

    def _remove_lineage_from_contract_index(
            self,
            spellbook_id: str,
            lineage_id: str,
    ) -> None:
        """
        Internal

        Remove a lineage from the contract-dependent index for a spellbook.
        """
        if not spellbook_id or not lineage_id:
            return
        if (
            self._contract_dependents_by_spellbook is None
            or self._contract_keys_by_lineage is None
        ):
            return

        keys = self._contract_keys_by_lineage.pop(lineage_id, None)
        if not keys:
            return

        book_index = self._contract_dependents_by_spellbook.get(spellbook_id)
        if not book_index:
            return

        for contract_key in keys:
            dependents = book_index.get(contract_key)
            if dependents is None:
                continue
            dependents.discard(lineage_id)
            if not dependents:
                book_index.pop(contract_key, None)

        if not book_index:
            self._contract_dependents_by_spellbook.pop(spellbook_id, None)

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
                if self._risk_manager is not None:
                    state._set_risk_manager(self._risk_manager)
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
                if self._risk_manager is not None:
                    state._set_risk_manager(self._risk_manager)
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

    # ------------------------------------------------------------------
    # Per-conduit resolution state (Phases 5-7)
    # ------------------------------------------------------------------
    def get_conduit_resolution_state(self, conduit_id: str) -> Optional[ConduitResolutionState]:
        """
        Retrieve the per-conduit resolution state for a given conduit id.

        Args:
            conduit_id:
                Conduit identifier used as the resolution-state key.
        Returns:
            ConduitResolutionState | None:
                The resolution state if present; otherwise None.
        """
        self.check_cleaned()
        if not conduit_id:
            return None
        with self._lock:
            if self._resolution_by_conduit_id is None:
                return None
            return self._resolution_by_conduit_id.get(conduit_id)

    def get_or_create_conduit_resolution_state(self, conduit_id: str) -> ConduitResolutionState:
        """
        Retrieve or create the per-conduit resolution state for a conduit id.

        Args:
            conduit_id:
                Conduit identifier used as the resolution-state key.
        Returns:
            ConduitResolutionState:
                The resolution state instance for this conduit.
        Raises:
            ValueError:
                If conduit_id is empty.
            RuntimeError:
                If the registry has been cleaned.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        with self._lock:
            if self._resolution_by_conduit_id is None:
                raise RuntimeError("SpellSystemStates has been cleaned.")
            state = self._resolution_by_conduit_id.get(conduit_id)
            if state is None:
                state = ConduitResolutionState(conduit_id)
                if self._risk_manager is not None:
                    state._set_risk_manager(self._risk_manager)
                self._resolution_by_conduit_id[conduit_id] = state
            return state

    def unregister_lineage(self, spell_index: ISpellIndex) -> Optional[SpellSystemState]:
        """
        Remove a lineage and its indices from this registry.

        Behaviour:
        - Remove the lineage entry from `_states_by_index_id`.
        - Remove the current spell id entry from `_states_by_spell_id`.
        - Remove the lineage from `_dirty_lineages`.
        - Remove the local topology entry for the current spell id.
        - Remove collection/contract indices for the owning spellbook.
        - Detach this lineage from reverse-dependency edges.
        - Cleanup the removed SpellSystemState.

        Args:
            spell_index: Lineage to unregister (required).
        Returns:
            Optional[SpellSystemState]:
                The removed SpellSystemState instance, or None if it was not present.
        Raises:
            ValueError: If spell_index is None.
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        if spell_index is None:
            raise ValueError("spell_index cannot be None")

        index_id = spell_index.id
        removed_state: Optional[SpellSystemState] = None
        current_spell_id: Optional[str] = None
        owner_spellbook_id: Optional[str] = None
        dependencies: Set[str] = set()

        with self._lock:
            if (
                self._states_by_index_id is None
                or self._states_by_spell_id is None
                or self._dirty_lineages is None
            ):
                raise RuntimeError("SpellSystemStates has been cleaned")

            removed_state = self._states_by_index_id.pop(index_id, None)
            if removed_state is None:
                # Still clear the spell-id index if it points to this lineage.
                current_spell_id = spell_index.current
                if current_spell_id and self._states_by_spell_id.get(current_spell_id) is not None:
                    self._states_by_spell_id.pop(current_spell_id, None)
                self._dirty_lineages.discard(index_id)
                return None

            try:
                current_spell_id = removed_state.current_spell_id
            except Exception:
                current_spell_id = spell_index.current

            if current_spell_id and self._states_by_spell_id.get(current_spell_id) is removed_state:
                self._states_by_spell_id.pop(current_spell_id, None)

            self._dirty_lineages.discard(index_id)

            if self._local_topologies is not None and current_spell_id:
                self._local_topologies.pop(current_spell_id, None)

            if self._lineage_owner_spellbook_id is not None:
                owner_spellbook_id = self._lineage_owner_spellbook_id.pop(index_id, None)

            if owner_spellbook_id is not None:
                self._remove_lineage_from_collection_index(owner_spellbook_id, index_id)
                self._remove_lineage_from_contract_index(owner_spellbook_id, index_id)
                if self._collection_frames_by_lineage is not None:
                    self._collection_frames_by_lineage.pop(index_id, None)

            try:
                dependencies = removed_state.direct_dependencies
            except Exception:
                dependencies = set()

            # Detach reverse edges from dependencies that still exist.
            for dep_id in dependencies:
                dep_state = None
                if self._states_by_spell_id is not None:
                    dep_state = self._states_by_spell_id.get(dep_id)
                if dep_state is None and self._states_by_index_id is not None:
                    dep_state = self._states_by_index_id.get(dep_id)
                if dep_state is not None:
                    dep_state.remove_dependent(index_id)

        try:
            removed_state.cleanup()
        except Exception:
            pass

        return removed_state

    def set_risk_manager(self, risk_manager: Optional[object]) -> None:
        """
        Attach a RiskManager to all registered state objects.
        """
        self.check_cleaned()
        with self._lock:
            self._risk_manager = risk_manager
            if self._states_by_index_id is not None:
                for state in self._states_by_index_id.values():
                    try:
                        state._set_risk_manager(risk_manager)
                    except Exception:
                        pass
            if self._resolution_by_conduit_id is not None:
                for state in self._resolution_by_conduit_id.values():
                    try:
                        state._set_risk_manager(risk_manager)
                    except Exception:
                        pass

    def drop_conduit_resolution_state(self, conduit_id: str) -> None:
        """
        Remove and cleanup the per-conduit resolution state for a conduit id.

        Args:
            conduit_id:
                Conduit identifier to remove.
        """
        self.check_cleaned()
        if not conduit_id:
            return
        with self._lock:
            if self._resolution_by_conduit_id is None:
                return
            state = self._resolution_by_conduit_id.pop(conduit_id, None)
            if state is not None:
                try:
                    state.cleanup()
                except Exception:
                    pass

    def iter_conduit_resolution_states(self) -> Iterator[ConduitResolutionState]:
        """
        Iterate over all registered per-conduit resolution states.

        Returns:
            Iterator[ConduitResolutionState]:
                Snapshot iterator over registered resolution states.
        """
        self.check_cleaned()
        with self._lock:
            if self._resolution_by_conduit_id is None:
                return iter(())
            return iter(list(self._resolution_by_conduit_id.values()))

    def set_conduit_spell_validity(
            self,
            conduit_id: str,
            spell_id: str,
            validity: SpellValidity,
            *,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Set per-conduit resolution validity for a spell id.
        """
        self.check_cleaned()
        state = self.get_or_create_conduit_resolution_state(conduit_id)
        state.set_spell_validity(spell_id, validity, change_reason=change_reason)

    def bulk_set_conduit_spell_validity(
            self,
            conduit_id: str,
            validity_map: Mapping[str, SpellValidity],
            *,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Bulk update per-conduit resolution validity for spell ids.
        """
        self.check_cleaned()
        state = self.get_or_create_conduit_resolution_state(conduit_id)
        state.bulk_set_spell_validity(validity_map, change_reason=change_reason)

    def set_conduit_root_validity(
            self,
            conduit_id: str,
            root_id: str,
            validity: SpellValidity,
            *,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Set per-conduit resolution validity for a root spell id.
        """
        self.check_cleaned()
        state = self.get_or_create_conduit_resolution_state(conduit_id)
        state.set_root_validity(root_id, validity, change_reason=change_reason)

    def bulk_set_conduit_root_validity(
            self,
            conduit_id: str,
            validity_map: Mapping[str, SpellValidity],
            *,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Bulk update per-conduit resolution validity for root spell ids.
        """
        self.check_cleaned()
        state = self.get_or_create_conduit_resolution_state(conduit_id)
        state.bulk_set_root_validity(validity_map, change_reason=change_reason)

    def record_conduit_diagnostics(
            self,
            conduit_id: str,
            diagnostics: Sequence[SystemDiagnostic],
    ) -> None:
        """
        Record per-conduit system diagnostics, replacing if signatures differ.
        """
        self.check_cleaned()
        state = self.get_or_create_conduit_resolution_state(conduit_id)
        state.record_diagnostics(diagnostics)

    def clear_conduit_diagnostics(self, conduit_id: str) -> None:
        """
        Clear per-conduit system diagnostics for a conduit id.
        """
        self.check_cleaned()
        state = self.get_conduit_resolution_state(conduit_id)
        if state is None:
            return
        state.clear_diagnostics()

    def mark_conduit_dirty(
            self,
            conduit_id: str,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        """
        Mark a per-conduit resolution state as dirty.
        """
        self.check_cleaned()
        state = self.get_or_create_conduit_resolution_state(conduit_id)
        state.mark_dirty(change_reason=change_reason)

    def clear_conduit_dirty(self, conduit_id: str, validated_at: float) -> None:
        """
        Mark a per-conduit resolution state as clean after validation.
        """
        self.check_cleaned()
        state = self.get_conduit_resolution_state(conduit_id)
        if state is None:
            return
        state.clear_dirty(validated_at)

    def mark_collection_dependents_dirty(
            self,
            *,
            spellbook_id: str,
            frame_keys: Iterable[str],
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> Set[str]:
        """
        Mark list[Frame] consumers dirty for a specific Spellbook scope.

        Args:
            spellbook_id:
                Owning Spellbook id used to scope the collection index.
            frame_keys:
                Frame keys whose collection memberships changed.
            change_reason:
                Optional change reason override; defaults to dependencies_changed.
        Returns:
            Set[str]: Lineage ids marked dirty by this call.
        """
        self.check_cleaned()
        if not spellbook_id:
            return set()

        impacted: Set[str] = set()
        frame_key_set = {key for key in frame_keys if key}
        if not frame_key_set:
            return impacted

        if change_reason is None:
            change_reason = SpellStateChangeReason.dependencies_changed

        with self._lock:
            if (
                self._states_by_index_id is None
                or self._dirty_lineages is None
                or self._collection_dependents_by_spellbook is None
            ):
                return impacted

            book_index = self._collection_dependents_by_spellbook.get(spellbook_id)
            if not book_index:
                return impacted

            for frame_key in frame_key_set:
                dependents = book_index.get(frame_key)
                if not dependents:
                    continue
                for lineage_id in list(dependents):
                    state = self._states_by_index_id.get(lineage_id)
                    if state is None:
                        continue
                    state.mark_dependency_change(change_reason=change_reason)
                    self._dirty_lineages.add(lineage_id)
                    impacted.add(lineage_id)

        return impacted

    def mark_contract_dependents_dirty(
            self,
            *,
            spellbook_id: str,
            contract_keys: Optional[Iterable[Tuple[str, str]]] = None,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> Set[str]:
        """
        Mark SpellContract consumers dirty for a specific Spellbook scope.

        Args:
            spellbook_id:
                Owning Spellbook id used to scope the contract index.
            contract_keys:
                Canonical contract keys to invalidate. When None, all
                SpellContract dependents for the spellbook are marked dirty.
            change_reason:
                Optional change reason override; defaults to contract_unvalidated.
        Returns:
            Set[str]: Lineage ids marked dirty by this call.
        """
        self.check_cleaned()
        if not spellbook_id:
            return set()

        impacted: Set[str] = set()

        if change_reason is None:
            change_reason = SpellStateChangeReason.contract_unvalidated

        with self._lock:
            if (
                self._states_by_index_id is None
                or self._dirty_lineages is None
                or self._contract_dependents_by_spellbook is None
            ):
                return impacted

            book_index = self._contract_dependents_by_spellbook.get(spellbook_id)
            if not book_index:
                return impacted

            if contract_keys is None:
                key_iter = book_index.keys()
            else:
                key_iter = (key for key in contract_keys if key)

            for contract_key in key_iter:
                dependents = book_index.get(contract_key)
                if not dependents:
                    continue
                for lineage_id in dependents:
                    state = self._states_by_index_id.get(lineage_id)
                    if state is None:
                        continue
                    state.set_validity(
                        SpellValidity.gated,
                        change_reason=change_reason,
                        flags_to_add=[SpellState.contract_unvalidated],
                        transitively_dirty=False,
                    )
                    self._dirty_lineages.add(lineage_id)
                    impacted.add(lineage_id)

        return impacted


    def register_local_topology(
            self,
            spell_index: SpellIndex,
            topology: 'SpellLocalTopology',
    ) -> None:
        """
        Internal / DevOps

        Register or replace the local constructor topology for the given spell.

        This is called by :class:`SpellCrafter` during Phase 3 and is the
        primary entry point for building higher-level blueprints in phases 5–7.
        It also refreshes the collection-dependency index used for targeted
        list[Frame] revalidation within the owning Spellbook scope.
        """
        self.check_cleaned()
        if spell_index is None:
            raise ValueError("spell_index must not be None.")
        if topology is None:
            raise ValueError("topology must not be None.")

        with self._lock:
            spell_id = spell_index.current
            self._local_topologies[spell_id] = topology
            if self._lineage_owner_spellbook_id is None:
                return
            owner_spellbook_id = self._lineage_owner_spellbook_id.get(spell_index.id)
            if owner_spellbook_id is None:
                return
            if (
                self._collection_dependents_by_spellbook is not None
                and self._collection_frames_by_lineage is not None
            ):
                collection_frames = self._extract_collection_frame_keys(topology)
                self._update_collection_index(
                    spellbook_id=owner_spellbook_id,
                    lineage_id=spell_index.id,
                    frame_keys=collection_frames,
                )
            if (
                self._contract_dependents_by_spellbook is not None
                and self._contract_keys_by_lineage is not None
            ):
                contract_keys = self._extract_contract_keys(topology)
                self._update_contract_index(
                    spellbook_id=owner_spellbook_id,
                    lineage_id=spell_index.id,
                    contract_keys=contract_keys,
                )

    def get_local_topology(
            self,
            spell_index: SpellIndex,
    ) -> Optional['SpellLocalTopology']:
        """
        Internal / DevOps

        Retrieve the local constructor topology for the given spell, if any.
        """
        self.check_cleaned()
        if spell_index is None:
            raise ValueError("spell_index must not be None.")

        with self._lock:
            return self._local_topologies.get(spell_index.current)

    def get_local_topology_by_id(
            self,
            spell_id: str,
    ) -> Optional['SpellLocalTopology']:
        """
        Internal / DevOps

        Retrieve the local constructor topology using a version-id key.
        """
        self.check_cleaned()
        if not spell_id:
            raise ValueError("spell_id must not be None.")

        with self._lock:
            return self._local_topologies.get(spell_id)

    def _extract_collection_frame_keys(
            self,
            topology: 'SpellLocalTopology',
    ) -> Set[str]:
        """
        Internal

        Extract collection frame keys from a local topology.
        """
        frames: Set[str] = set()
        if topology is None:
            return frames
        for socket in topology.iter_sockets():
            if socket.socket_kind is not SocketKind.NORMAL:
                continue
            if not socket.is_collection:
                continue
            if socket.dependency_key is None:
                continue
            frames.add(socket.dependency_key[0])
        return frames

    def _extract_contract_keys(
            self,
            topology: 'SpellLocalTopology',
    ) -> Set[Tuple[str, str]]:
        """
        Internal

        Extract SpellContract keys from a local topology.
        """
        keys: Set[Tuple[str, str]] = set()
        if topology is None:
            return keys
        for socket in topology.iter_sockets():
            if socket.socket_kind is not SocketKind.SPELL_CONTRACT:
                continue
            if socket.contract_key is None:
                continue
            keys.add(socket.contract_key)
        return keys

    def _update_collection_index(
            self,
            *,
            spellbook_id: str,
            lineage_id: str,
            frame_keys: Set[str],
    ) -> None:
        """
        Internal

        Update the collection-dependency index for a lineage within a spellbook.
        """
        if not spellbook_id or not lineage_id:
            return
        if (
            self._collection_dependents_by_spellbook is None
            or self._collection_frames_by_lineage is None
        ):
            return

        existing_frames = self._collection_frames_by_lineage.get(lineage_id, set())
        removed = existing_frames - frame_keys
        added = frame_keys - existing_frames

        if removed:
            book_index = self._collection_dependents_by_spellbook.get(spellbook_id)
            if book_index is not None:
                for frame_key in removed:
                    dependents = book_index.get(frame_key)
                    if dependents is None:
                        continue
                    dependents.discard(lineage_id)
                    if not dependents:
                        book_index.pop(frame_key, None)
                if not book_index:
                    self._collection_dependents_by_spellbook.pop(spellbook_id, None)

        if added:
            book_index = self._collection_dependents_by_spellbook.setdefault(spellbook_id, {})
            for frame_key in added:
                dependents = book_index.setdefault(frame_key, set())
                dependents.add(lineage_id)

        if frame_keys:
            self._collection_frames_by_lineage[lineage_id] = set(frame_keys)
        else:
            self._collection_frames_by_lineage.pop(lineage_id, None)

    def _update_contract_index(
            self,
            *,
            spellbook_id: str,
            lineage_id: str,
            contract_keys: Set[Tuple[str, str]],
    ) -> None:
        """
        Internal

        Update the SpellContract-dependent index for a lineage within a spellbook.
        """
        if not spellbook_id or not lineage_id:
            return
        if (
            self._contract_dependents_by_spellbook is None
            or self._contract_keys_by_lineage is None
        ):
            return

        existing_keys = self._contract_keys_by_lineage.get(lineage_id, set())
        removed = existing_keys - contract_keys
        added = contract_keys - existing_keys

        if removed:
            book_index = self._contract_dependents_by_spellbook.get(spellbook_id)
            if book_index is not None:
                for contract_key in removed:
                    dependents = book_index.get(contract_key)
                    if dependents is None:
                        continue
                    dependents.discard(lineage_id)
                    if not dependents:
                        book_index.pop(contract_key, None)
                if not book_index:
                    self._contract_dependents_by_spellbook.pop(spellbook_id, None)

        if added:
            book_index = self._contract_dependents_by_spellbook.setdefault(spellbook_id, {})
            for contract_key in added:
                dependents = book_index.setdefault(contract_key, set())
                dependents.add(lineage_id)

        if contract_keys:
            self._contract_keys_by_lineage[lineage_id] = set(contract_keys)
        else:
            self._contract_keys_by_lineage.pop(lineage_id, None)
