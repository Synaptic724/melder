from typing import Dict, Set

from mypy_extensions import mypyc_attr

# Melder imports
from melder.aether.spellbook.spell_compiler.system.spell_system_adjacency_snapshot import SpellSystemAdjacencySnapshot
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import SpellLocalTopology
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
@mypyc_attr(native_class=True)
class SpellSystemAdjacencyBuilder:
    """
    Builder for: class:`SpellSystemAdjacencySnapshot`.

    This is a thin adapter over: class:`SpellSystemStates` and is
    intentionally dumb:

        * It trusts that SpellSystemStates contain correct per-spell
          direct_dependencies at the **version-id** level.
        * It does **not** perform validation or cycle detection.
        * It does **not** understand sockets or contracts.

    All higher-level semantics (RootResolutionBlueprints, Phase 6
    validation, etc.) sit on top of this structural view.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = []

    @staticmethod
    def build(spell_system_states: SpellSystemStates,
              ) -> SpellSystemAdjacencySnapshot:
        """
        Build a frame-wide adjacency view from SpellSystemStates.

        Args
        ----
        spell_system_states:
            The SpellSystemStates instance is owned by the Spellbook /
            Aether DevOps layer. This must already have had dependencies
            populated by the Phase 3 local frame builder via
            SpellSystemStates.update_dependencies.

        Returns
        -------
        SpellSystemAdjacencySnapshot
            A structural view over all known spell_ids and their
            direct dependencies.
        """
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

        with spell_system_states._lock:
            states_by_index_id = spell_system_states._states_by_index_id
            local_topologies = spell_system_states._local_topologies

            for state in states_by_index_id.values():
                with state._lock:
                    spell_id = state._current_spell_id
                    direct_dep_set: Set[str] = state._direct_dependencies

                all_spell_ids.add(spell_id)
                dependencies[spell_id] = direct_dep_set

                for dep_id in direct_dep_set:
                    all_dependency_ids.add(dep_id)
                    reverse_dependencies.setdefault(dep_id, set()).add(spell_id)

                topologies[spell_id] = local_topologies.get(spell_id)

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
