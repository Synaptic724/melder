from __future__ import annotations
from typing import Dict, Iterable, Optional, Set
# Melder imports
from melder.spellbook.spell_crafter.system.spell_system_adjacency_snapshot import SpellSystemAdjacencySnapshot
from melder.utilities.interfaces.interfaces import ISpellSystemStates


class SpellSystemAdjacencyBuilder:
    """
    Builder for :class:`SpellSystemAdjacencySnapshot`.

    This is a thin adapter over :class:`ISpellSystemStates` and is
    intentionally dumb:

        * It trusts that SpellSystemStates contains correct per-spell
          direct_dependencies at the **version-id** level.
        * It does **not** perform validation or cycle detection.
        * It does **not** understand sockets or contracts.

    All higher-level semantics (RootResolutionBlueprints, Phase 6
    validation, etc.) sit on top of this structural snapshot.
    """

    __slots__ = []

    @staticmethod
    def build(spell_system_states: ISpellSystemStates,
              ) -> SpellSystemAdjacencySnapshot:
        """
        Build a frame-wide adjacency snapshot from SpellSystemStates.

        Args
        ----
        spell_system_states:
            The SpellSystemStates instance owned by the Spellbook /
            Aether DevOps layer. This must already have had dependencies
            populated by the Phase 3 local frame builder via
            SpellSystemStates.update_dependencies.

        Returns
        -------
        SpellSystemAdjacencySnapshot
            A structural view over all known spell_ids and their
            direct dependencies.
        """
        if spell_system_states is None:
            raise ValueError("spell_system_states must not be None.")

        # Outgoing edges: spell_id -> { dependency_id, ... }
        dependencies: Dict[str, Set[str]] = {}

        # Incoming edges: spell_id -> { parent_spell_id, ... }
        reverse_dependencies: Dict[str, Set[str]] = {}

        # All node ids we have seen as "owners" (sources in the graph).
        all_spell_ids: Set[str] = set()

        # All node ids that are used as dependencies anywhere.
        all_dependency_ids: Set[str] = set()

        # Optional per-spell constructor topologies keyed by version-id.
        topologies: Dict[str, 'SpellLocalTopology'] = {}

        # We rely on the concrete SpellSystemStates.iter_states() helper,
        # which returns SpellSystemState instances with:
        #
        #   * current_spell_id: str
        #   * direct_dependencies: Optional[Set[str]] (version_ids)
        #
        # The interface is already in your codebase.
        states_snapshot = spell_system_states.iter_states()
        for state in states_snapshot:
            spell_id = state.current_spell_id
            if spell_id is None:
                # The DevOps layer should never allow this, but we
                # defensively skip just in case.
                continue

            all_spell_ids.add(spell_id)

            direct_deps: Optional[Iterable[str]] = state.direct_dependencies
            if direct_deps is None:
                direct_dep_set: Set[str] = set()
            else:
                # Normalize to a concrete set so callers can rely on set
                # semantics regardless of how SpellSystemStates stored it.
                direct_dep_set = set(direct_deps)

            dependencies[spell_id] = direct_dep_set

            for dep_id in direct_dep_set:
                all_dependency_ids.add(dep_id)
                parents_for_dep = reverse_dependencies.get(dep_id)
                if parents_for_dep is None:
                    parents_for_dep = set()
                    reverse_dependencies[dep_id] = parents_for_dep
                parents_for_dep.add(spell_id)

            topology = spell_system_states.get_local_topology_by_id(spell_id)
            if topology is not None:
                topologies[spell_id] = topology

        # Structural roots are spells that **never appear as a dependency**
        # of any other spell in the frame.
        root_spell_ids: Set[str] = all_spell_ids.difference(all_dependency_ids)

        return SpellSystemAdjacencySnapshot(
            dependencies=dependencies,
            reverse_dependencies=reverse_dependencies,
            all_spell_ids=all_spell_ids,
            root_spell_ids=root_spell_ids,
            topologies=topologies,
        )
