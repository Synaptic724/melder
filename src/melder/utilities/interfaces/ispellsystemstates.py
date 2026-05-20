from typing import Dict, Iterable, Iterator, List, Mapping, Optional, Protocol, Sequence, Set, Tuple, runtime_checkable
import threading
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.spell_crafter.system.system_diagnostic import SystemDiagnostic
from melder.aether.spellbook.spell_crafter.topology.spell_local_topology import SpellLocalTopology
from melder.utilities.interfaces.iconduitresolutionstate import IConduitResolutionState
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.ispellindex import ISpellIndex

@runtime_checkable
class ISpellSystemStates(ICleanable, Protocol):
    """
    Per-frame registry for all SpellSystemState instances.

    This is the "control tower" object:

    - Owns the index: spell-index id -> SpellSystemState.
    - Keeps an auxiliary index: current_spell_id -> SpellSystemState
      (for convenience when you only know the version id).
    - Tracks which spell indexes are currently dirty so higher-level
      DevOps/validation flows can decide what to re-run.
    - Tracks collection dependency indices per Spellbook for targeted
      list[Frame] revalidation.
    - Tracks SpellContract consumer indices per Spellbook for targeted
      contract invalidation.

    Intended lifecycle:

    - One instance per AethericFrame (owned by the frame and initialized
      alongside Spellbook / DevOpsManager).
    - Spellbook / SpellCrafter call:
        * `register_index(...)` when a new SpellIndex appears
        * `update_dependencies(...)` after Phase 3/4 attaches dependency ids
        * `mark_structural_change(...)` when a spell index is rebound/mutated
    - DevOps / validation flows call:
        * `consume_dirty_indexes(...)` to get a worklist
        * `compute_impact_closure(...)` to fan out impacted spell indexes
    """
    _lock: threading.RLock
    _frame: Optional[object]
    _states_by_index_id: Optional[Dict[str, SpellSystemState]]
    _states_by_spell_id: Optional[Dict[str, SpellSystemState]]
    _dirty_indexes: Optional['Set[str]']
    _resolution_by_conduit_id: Optional[Dict[str, IConduitResolutionState]]
    _index_owner_spellbook_id: Optional[Dict[str, str]]
    _collection_frames_by_index: Optional[Dict[str, 'Set[str]']]
    _collection_dependents_by_spellbook: Optional[Dict[str, Dict[str, 'Set[str]']]]
    _contract_keys_by_index: Optional[Dict[str, 'Set[Tuple[str, str]]']]
    _contract_dependents_by_spellbook: Optional[Dict[str, Dict[Tuple[str, str], 'Set[str]']]]

    # ------------------------------------------------------------------
    # Registration / lookup
    # ------------------------------------------------------------------
    def register_index(self, spell_index: ISpellIndex) -> SpellSystemState:
        """
        Ensure a SpellSystemState exists for the given spell index and return it.

        Behaviour:
        - If this is the first time we see `spell_index.id`, create a new
          SpellSystemState with `spell_index.current` as the current_spell_id.
        - If it already exists, update its current_spell_id to match
          `spell_index.current`.
        - Update the spell-id index so `get_by_spell_id(...)` can resolve
          by current version id.
        - Record owner Spellbook identity from the attached SpellIndex owner
          surface when available.
        - Mark the spell index as structurally gated with reason
          SpellStateChangeReason.register_or_rebind and add it to the dirty set.

        This is intended to be called from Spellbook.bind(...) or equivalent.
        """
        ...

    def unregister_index(self, spell_index: ISpellIndex) -> Optional[SpellSystemState]:
        """
        Remove a spell index from this registry and return the removed state if present.

        Behaviour:
        - Drop the spell index from the index and current spell-id index.
        - Remove dirty markers and local topology for the current spell id.
        - Remove collection/contract indices for the owning spellbook.
        - Detach this spell index from reverse-dependency edges.
        - Cleanup the removed SpellSystemState instance.

        Returns:
            SpellSystemState | None: The removed state when present; otherwise None.
        """
        ...

    def get_by_index_id(self, index_id: str) -> Optional[SpellSystemState]:
        """
        Lookup a SpellSystemState by spell-index id.

        Returns:
            - The SpellSystemState instance for this spell index, or
            - None if no state has been registered for the id.
        """
        ...

    def get_by_spell_id(self, spell_id: str) -> Optional[SpellSystemState]:
        """
        Lookup a SpellSystemState by current spell version id.

        This is a convenience when the caller only knows the version id
        (e.g., SpellIndex.current) and wants to find the associated spell-index state.

        Returns:
            - The SpellSystemState instance, or
            - None if no state is currently indexed for that spell id.
        """
        ...

    # ------------------------------------------------------------------
    # Dependency wiring (Phase 3/4 integration)
    # ------------------------------------------------------------------
    def update_dependencies(self, spell_index: ISpellIndex, dependency_ids: Iterable[str]) -> None:
        """
        Attach direct dependency ids for this spell index and update reverse edges.

        `dependency_ids` are generic "spell ids" (version or index ids) - the
        SpellCrafter / Spellbook decides the semantics. This manager only
        cares about connectivity, not the type system.

        Behaviour:
        - Ensure there is a SpellSystemState for this spell index (create if missing).
        - Compute the delta between previous and new dependency sets.
        - Remove reverse edges from dependencies we no longer reference.
        - Add reverse edges for new dependencies.
        - Mark this spell index as gated due to dependency change and add to
          `_dirty_indexes`.
        """
        ...

    def mark_contract_dependents_dirty(
            self,
            *,
            spellbook_id: str,
            contract_keys: Optional[Iterable[Tuple[str, str]]] = None,
            change_reason: Optional["SpellStateChangeReason"] = None,
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
                Optional change reason override.
        Returns:
            Set[str]: Lineage ids marked dirty by this call.
        """
        ...

    # ------------------------------------------------------------------
    # Dirty / impact queries (used by DevOps / validation governor)
    # ------------------------------------------------------------------
    def mark_structural_change(
            self,
            spell_index: ISpellIndex,
            reason: 'SpellStateChangeReason' = SpellStateChangeReason.structure_changed,
    ) -> None:
        """
        Mark a spell index as structurally changed.

        Typical triggers:
        - New version promoted.
        - Class/method profile changed.
        - Binding semantics changed in a way that affects structure.

        Behaviour:
        - Ensure a SpellSystemState exists for the spell index.
        - Mark it structurally gated with the provided reason.
        - Add the spell-index id to `_dirty_indexes`.
        """
        ...

    def mark_collection_dependents_dirty(
            self,
            *,
            spellbook_id: str,
            frame_keys: Iterable[str],
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> Set[str]:
        """
        Mark list[Frame] consumers dirty for a specific Spellbook scope.

        Args:
            spellbook_id:
                Owning Spellbook id used to scope the collection index.
            frame_keys:
                Frame keys whose collection memberships changed.
            change_reason:
                Optional reason override; defaults to dependencies_changed.
        Returns:
            Set[str]: Lineage ids marked dirty by this call.
        """
        ...

    def register_local_topology(
            self,
            spell_index: ISpellIndex,
            topology: SpellLocalTopology,
    ) -> None:
        """
        Register or replace the local constructor topology for the given spell.

        This is invoked from SpellCrafter Phase 3 whenever a spell is (re)built.
        """
        ...

    def get_local_topology(
            self,
            spell_index: ISpellIndex,
    ) -> Optional[SpellLocalTopology]:
        """
        Retrieve the local constructor topology for the given spell, if any.

        Returns:
            Optional[SpellLocalTopology]:
                Local topology for the spell index when registered; otherwise None.
        """
        ...

    def get_local_topology_by_id(
            self,
            spell_id: str,
    ) -> Optional[SpellLocalTopology]:
        """
        Retrieve the local constructor topology using a version-id key.

        Returns:
            Optional[SpellLocalTopology]:
                Local topology for the current version id when indexed;
                otherwise None.
        """
        ...

    def compute_impact_closure(self, root_index_ids: Iterable[str]) -> Set[str]:
        """
        Compute the transitive closure of impacted spell indexes downstream.

        Args:
            root_index_ids:
                Spell-index ids that changed *directly* (e.g., newly promoted or
                structurally altered).

        Behaviour:
        - Walk reverse edges (`direct_dependents`) starting from each root.
        - Build a set of all spell indexes that depend (directly or indirectly)
          on any of the roots.
        - For each impacted spell index:
            * Roots: left in their existing structural state (already gated).
            * Non-roots: marked as transitively dirty (impacted_by_dependency).
        - All impacted spell indexes are added to `_dirty_indexes`.

        Returns:
            A set of all impacted spell-index ids, including the roots.
        """
        ...

    def consume_dirty_indexes(self) -> List[str]:
        """
        Pop and return the current set of dirty spell-index ids.

        This is the handoff to whatever runs the revalidation / mutation
        governor (your "Phase 5-7" or equivalent).

        Behaviour:
        - Snapshot all ids currently in `_dirty_indexes`.
        - Clear `_dirty_indexes`.
        - Return the snapshot list. Order is unspecified.
        """
        ...

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------
    def iter_states(self) -> List[SpellSystemState]:
        """
        Snapshot of all SpellSystemState instances currently registered.

        Returns:
            List[SpellSystemState]:
                Detached snapshot of all registered state objects.
        """
        ...

    # ------------------------------------------------------------------
    # Per-conduit resolution state (Phases 5-7)
    # ------------------------------------------------------------------
    def get_conduit_resolution_state(self, conduit_id: str) -> Optional[IConduitResolutionState]:
        """
        Retrieve the per-conduit resolution state for a conduit id.

        Returns:
            Optional[IConduitResolutionState]:
                Stored conduit-scoped resolution state, or None when the
                conduit has no registered state.
        """
        ...

    def get_or_create_conduit_resolution_state(self, conduit_id: str) -> IConduitResolutionState:
        """
        Retrieve or create the per-conduit resolution state for a conduit id.

        Returns:
            IConduitResolutionState:
                Existing or newly created conduit-scoped resolution state.
        """
        ...

    def drop_conduit_resolution_state(self, conduit_id: str) -> None:
        """
        Remove and clean up the per-conduit resolution state for a conduit id.

        Returns:
            None.
        """
        ...

    def iter_conduit_resolution_states(self) -> Iterator[IConduitResolutionState]:
        """
        Iterate over registered per-conduit resolution states.

        Returns:
            Iterator[IConduitResolutionState]:
                Iterator over the currently registered conduit-scoped states.
        """
        ...

    def set_conduit_spell_validity(
            self,
            conduit_id: str,
            spell_id: str,
            validity: SpellValidity,
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Set per-conduit resolution validity for a spell id.
        """
        ...

    def bulk_set_conduit_spell_validity(
            self,
            conduit_id: str,
            validity_map: Mapping[str, SpellValidity],
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Bulk update per-conduit resolution validity for spell ids.
        """
        ...

    def set_conduit_root_validity(
            self,
            conduit_id: str,
            root_id: str,
            validity: SpellValidity,
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Set per-conduit resolution validity for a root id.
        """
        ...

    def bulk_set_conduit_root_validity(
            self,
            conduit_id: str,
            validity_map: Mapping[str, SpellValidity],
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Bulk update per-conduit resolution validity for root ids.
        """
        ...

    def record_conduit_diagnostics(
            self,
            conduit_id: str,
            diagnostics: Sequence[SystemDiagnostic],
    ) -> None:
        """
        Record per-conduit system diagnostics, replacing on signature change.
        """
        ...

    def clear_conduit_diagnostics(self, conduit_id: str) -> None:
        """
        Clear per-conduit diagnostics for a conduit id.
        """
        ...

    def mark_conduit_dirty(
            self,
            conduit_id: str,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Mark a per-conduit resolution state as dirty.
        """
        ...

    def clear_conduit_dirty(self, conduit_id: str, validated_at: float) -> None:
        """
        Mark a per-conduit resolution state as clean after validation.
        """
        ...

    def set_risk_manager(self, risk_manager: Optional[object]) -> None:
        """
        Attach a RiskManager to this registry.
        """
        ...
