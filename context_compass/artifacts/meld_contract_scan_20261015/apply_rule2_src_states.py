"""Rule 2 / D2 source change: SpellSystemStates records a binding key per lineage and walks downstream (melder_1).

contract_recheck_on_notch_2026_10_16, component_patch_dependent_walk. usage: python <this script> <tree root> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]
REL = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py"

STEPS = [
    ("one",
     """    - Spellbook / SpellCrafter call:
        * `register_index(..., resolvable=...)` when a new SpellIndex+Spell
          appears or an index selects another version (bind, notch, an
          ownership transfer), passing the selected version's `Spell.resolvable`
""",
     """    - Spellbook / SpellCrafter call:
        * `register_index(..., resolvable=..., binding_key=...)` when a new
          SpellIndex+Spell appears or an index selects another version (bind,
          notch, an ownership transfer), passing the selected version's
          `Spell.resolvable` and, at bind and notch, its binding key
        * `mark_dependents_for_revalidation(...)` after a notch, so every
          lineage downstream of the notched one revalidates at its next meld
""", ""),
    ("one",
     """        dependency indices, per-Spellbook SpellContract consumer indices,
        per-conduit `ConduitResolutionState` keyed by conduit_id, and the
        published set of lineages flagged `SpellState.non_resolvable`.
""",
     """        dependency indices, per-Spellbook SpellContract consumer indices,
        the binding key each lineage was registered under, per-conduit
        `ConduitResolutionState` keyed by conduit_id, and the published set of
        lineages flagged `SpellState.non_resolvable`.
""", ""),
    ("one",
     """        "_contract_dependents_by_spellbook",
        "_risk_manager",
""",
     """        "_contract_dependents_by_spellbook",
        "_binding_key_by_index",
        "_risk_manager",
""", ""),
    ("one",
     """        self._contract_dependents_by_spellbook: Optional[
            Dict[str, Dict[Tuple[str, str], Set[str]]]
        ] = {}
        self._risk_manager: Optional[RiskManager] = None
""",
     """        self._contract_dependents_by_spellbook: Optional[
            Dict[str, Dict[Tuple[str, str], Set[str]]]
        ] = {}
        # The binding key of each lineage's selected version (`register_index(binding_key=...)`): the contract key a
        # SpellContract consumer of that lineage declares, read by the downstream walk (`_mark_dependents_locked`).
        self._binding_key_by_index: Optional[Dict[str, Tuple[str, str]]] = {}
        self._risk_manager: Optional[RiskManager] = None
""", ""),
    ("one",
     """                self._contract_keys_by_index.clear()

            if self._index_owner_spellbook_id is not None:
                self._index_owner_spellbook_id.clear()
""",
     """                self._contract_keys_by_index.clear()

            if self._binding_key_by_index is not None:
                self._binding_key_by_index.clear()

            if self._index_owner_spellbook_id is not None:
                self._index_owner_spellbook_id.clear()
""", ""),
    ("one",
     """            del self._contract_keys_by_index
            del self._index_owner_spellbook_id
""",
     """            del self._contract_keys_by_index
            del self._binding_key_by_index
            del self._index_owner_spellbook_id
""", ""),
    ("one",
     """            owner_spellbook_id: Optional[str] = None,
            *,
            resolvable: Optional[bool] = None,
    ) -> SpellSystemState:
""",
     """            owner_spellbook_id: Optional[str] = None,
            *,
            resolvable: Optional[bool] = None,
            binding_key: Optional[Tuple[str, str]] = None,
    ) -> SpellSystemState:
""", ""),
    ("one",
     """        - Keep the published set of flagged lineages in step with the flag
          (`_publish_non_resolvable_membership_locked`), also before the gate
          publishes, so the refresh that event runs reads the new set.
""",
     """        - Keep the published set of flagged lineages in step with the flag
          (`_publish_non_resolvable_membership_locked`), also before the gate
          publishes, so the refresh that event runs reads the new set.
        - Record `binding_key` as the lineage's binding key when one is given;
          None keeps the key recorded before. The downstream walk
          (`mark_dependents_for_revalidation`) reaches the SpellContract
          consumers of a lineage through this key, because a consumer declares
          the key, not an edge to the lineage.
""", ""),
    ("one",
     """                caller does not state it (a registration that keeps the
                selection, such as the ownership transfer's disable step).

        Returns:
""",
     """                caller does not state it (a registration that keeps the
                selection, such as the ownership transfer's disable step).
            binding_key:
                The selected version's normalized `(frame_key, binding_key)` -
                `Spell._key`, the form `SpellContract.canonical_key` takes - or
                None to keep the recorded key (bind and notch pass it; the
                ownership transfer's registrations keep the lineage's key).

        Returns:
""", ""),
    ("one",
     """            TypeError:
                If `resolvable` is neither None nor a bool; nothing is
                registered.
""",
     """            TypeError:
                If `resolvable` is neither None nor a bool, or `binding_key` is
                neither None nor a pair of strings; nothing is registered.
""", ""),
    ("one",
     """                f"got {type(resolvable).__name__}. Pass spell.resolvable for the version the index selects."
            )
        index_id = spell_index.id
""",
     """                f"got {type(resolvable).__name__}. Pass spell.resolvable for the version the index selects."
            )
        if binding_key is not None and not (
                type(binding_key) is tuple
                and len(binding_key) == 2
                and type(binding_key[0]) is str
                and type(binding_key[1]) is str
        ):
            raise TypeError(
                "register_index(binding_key=...) takes the selected version's normalized (frame_key, binding_key) "
                f"pair of strings or None; got {binding_key!r}. Pass spell._key for the version the index selects."
            )
        index_id = spell_index.id
""", ""),
    ("one",
     """                self._index_owner_spellbook_id[index_id] = owner_spellbook_id

            # The selected version's capability, written before the gate below
""",
     """                self._index_owner_spellbook_id[index_id] = owner_spellbook_id

            if binding_key is not None:
                self._binding_key_by_index[index_id] = binding_key

            # The selected version's capability, written before the gate below
""", ""),
    ("one",
     """        - Remove collection/contract indices for the owning spellbook.
        - Detach this spell index from reverse-dependency edges.
""",
     """        - Remove collection/contract indices for the owning spellbook, and
          forget the lineage's binding key.
        - Detach this spell index from reverse-dependency edges.
""", ""),
    ("one",
     """                if current_spell_id:
                    self._forget_resolution_verdicts_locked(
                        current_spell_id,
                        change_reason=SpellStateChangeReason.cleaned_up_spell,
                    )
                dirty_indexes.discard(index_id)
                return None
""",
     """                if current_spell_id:
                    self._forget_resolution_verdicts_locked(
                        current_spell_id,
                        change_reason=SpellStateChangeReason.cleaned_up_spell,
                    )
                dirty_indexes.discard(index_id)
                self._binding_key_by_index.pop(index_id, None)
                return None
""", ""),
    ("one",
     """            if self._index_owner_spellbook_id is not None:
                owner_spellbook_id = self._index_owner_spellbook_id.pop(index_id, None)
""",
     """            if self._index_owner_spellbook_id is not None:
                owner_spellbook_id = self._index_owner_spellbook_id.pop(index_id, None)
            self._binding_key_by_index.pop(index_id, None)
""", ""),
]

WALK_OLD = """    def consume_dirty_indexes(self) -> List[str]:
"""
WALK_NEW = '''    def mark_dependents_for_revalidation(self, index_ids: Iterable[Optional[str]]) -> Set[str]:
        """
        Mark for revalidation every lineage downstream of `index_ids`, by registry edge or by contract key.

        Purpose:
            A notch changes what every dependent of the notched lineage resolves: a dependent's plan names the
            old version, and the topology it expands may too. `Spellbook._apply_notch` calls this with the
            notched lineage, so each dependent's next meld rechecks its structure and rebuilds against the
            versions now active (contract_recheck_on_notch_2026_10_16, D2). Mark only: no plan, context or
            object is touched here.

        Contract:
            - The walk starts from the given lineages (the seeds) and follows, from every lineage it reaches,
              the reverse dependency edges (`direct_dependents`, recorded by Phase 3's `update_dependencies`) and
              the SpellContract consumers, in every Spellbook of the frame, of the binding key that lineage was
              registered under (`register_index(binding_key=...)`) - a contract consumer declares a key, not an
              edge. A lineage with no recorded key is followed by its edges only.
            - A lineage reached by an edge gets `mark_transitively_dirty()` (gated, `impacted_by_dependency`,
              transitively dirty); one reached as a contract consumer gets rule 2's contract mark (gated,
              `contract_unvalidated`, not transitively dirty); one reached both ways gets the contract mark,
              then the edge mark.
            - Seeds are never marked (each caller gates its seeds for their own change), and a dependent with
              no registered state is passed over. Each lineage is visited once, so a cycle of edges or contracts
              terminates.
            - Every marked lineage joins the dirty set. `set_validity` publishes a validity only when it
              changes, so a walk over lineages already gated publishes nothing.

        Args:
            index_ids:
                Spell-index ids (lineage ids) whose change starts the walk; empty and None ids are ignored.

        Returns:
            Set[str]:
                The lineage ids this call marked, seeds excluded; empty when nothing is downstream.

        Raises:
            RuntimeError:
                If the registry has been cleaned (`check_cleaned`), before or while waiting for its lock.

        Threading:
            Runs under the registry lock; each mark takes the state's lock inside it (registry -> state) and
            publishes to RiskManager inside the registry lock and outside the state lock, the order every
            registry mark takes. It takes no Book, conduit, ward or contract lock, so a caller may hold those.
        """
        self.check_cleaned()
        seeds = {index_id for index_id in index_ids if index_id}
        if not seeds:
            return set()
        with self._lock:
            self.check_cleaned()
            return self._mark_dependents_locked(seeds)

    def _mark_dependents_locked(self, seeds: Set[str]) -> Set[str]:
        """
        Walk downstream of `seeds` and mark every lineage reached; the caller holds `_lock`.

        Purpose:
            The one body behind `mark_dependents_for_revalidation` (a notch) and the walk-on of
            `mark_contract_dependents_dirty` (a contract change), so both fan out the same way.

        Contract:
            - Follows reverse edges and the contract consumers of each reached lineage's binding key, across
              every Spellbook, visiting each lineage once (see `mark_dependents_for_revalidation`).
            - Marks after the walk, so a lineage's mark knows every way it was reached: the contract mark
              first, then the edge mark. Seeds are never marked; lineages with no registered state are
              skipped; every marked lineage joins `_dirty_indexes`.

        Args:
            seeds:
                Non-empty lineage ids the walk starts from.

        Returns:
            Set[str]:
                The lineage ids marked.
        """
        edge_reached: Set[str] = set()
        contract_reached: Set[str] = set()
        visited: Set[str] = set(seeds)
        worklist: List[str] = list(seeds)
        while worklist:
            current = worklist.pop()
            followers: List[str] = []
            state = self._states_by_index_id.get(current)
            if state is not None:
                dependents = state.direct_dependents
                edge_reached.update(dependents)
                followers.extend(dependents)
            binding_key = self._binding_key_by_index.get(current)
            if binding_key is not None:
                for book_index in self._contract_dependents_by_spellbook.values():
                    consumers = book_index.get(binding_key)
                    if consumers:
                        contract_reached.update(consumers)
                        followers.extend(consumers)
            for follower in followers:
                if follower not in visited:
                    visited.add(follower)
                    worklist.append(follower)

        marked: Set[str] = set()
        for index_id in (edge_reached | contract_reached) - seeds:
            state = self._states_by_index_id.get(index_id)
            if state is None:
                continue
            if index_id in contract_reached:
                state.set_validity(
                    SpellValidity.gated,
                    change_reason=SpellStateChangeReason.contract_unvalidated,
                    flags_to_add=[SpellState.contract_unvalidated],
                    transitively_dirty=False,
                )
            if index_id in edge_reached:
                state.mark_transitively_dirty()
            self._dirty_indexes.add(index_id)
            marked.add(index_id)
        return marked

    def consume_dirty_indexes(self) -> List[str]:
'''

CONTRACT_DOC_OLD = """            - Impacted spell indexes are gated with the `contract_unvalidated` flag
              rather than marked transitively dirty, because the topology did
              not change; only contract truth must be recomputed.
        Returns:
            Set[str]: Spell-index ids marked dirty by this call.
        \"\"\"
"""
CONTRACT_DOC_NEW = """            - Impacted spell indexes are gated with the `contract_unvalidated` flag
              rather than marked transitively dirty, because the topology did
              not change; only contract truth must be recomputed.
            - The mark walks on (`_mark_dependents_locked`, D2 of
              contract_recheck_on_notch_2026_10_16): whatever depends on a
              consumer it marks - by registry edge, or as a contract consumer of
              that consumer's binding key in any Spellbook - is marked for
              revalidation too, so a dependent built against the old provider
              rebuilds at its next meld.
        Returns:
            Set[str]: The consumers this call gated (the lineages the walk-on
            marked are not included).
        \"\"\"
"""

WALK_ON_OLD = """                        flags_to_add=[SpellState.contract_unvalidated],
                        transitively_dirty=False,
                    )
                    self._dirty_indexes.add(index_id)
                    impacted.add(index_id)

        return impacted
"""
WALK_ON_NEW = """                        flags_to_add=[SpellState.contract_unvalidated],
                        transitively_dirty=False,
                    )
                    self._dirty_indexes.add(index_id)
                    impacted.add(index_id)

            if impacted:
                self._mark_dependents_locked(impacted)

        return impacted
"""

STEPS += [
    ("one", WALK_OLD, WALK_NEW, ""),
    ("one", CONTRACT_DOC_OLD, CONTRACT_DOC_NEW, ""),
    ("one", WALK_ON_OLD, WALK_ON_NEW, ""),
]

apply(ROOT, REL, STEPS, CHECK)
