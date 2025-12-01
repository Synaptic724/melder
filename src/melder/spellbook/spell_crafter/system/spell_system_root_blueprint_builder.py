# melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Set, Tuple

from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.system.spell_system_adjacency_snapshot import (
    SpellSystemAdjacencySnapshot,
)


class SpellSystemRootBlueprintBuilder:
    """
    Phase-5 structural builder.

    Given a SpellSystemAdjacencySnapshot (version-id graph for the *frame*),
    construct a RootResolutionBlueprint for every root spell in that frame.

    Semantics:

        * Each RootResolutionBlueprint is anchored at a **root version-id**,
          but its DAG contains **all reachable version-ids** for that root.
        * Edges are provider → dependent (same orientation as Phase 3 DAGs).
        * This is *purely structural*:
              - payloads are None,
              - param_name and socket_kind are left unset (None).
          Socket metadata and DagIndex are overlaid in later Phase-5 steps.
    """

    __slots__ = ()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def build_root_blueprints(
            self,
            snapshot: SpellSystemAdjacencySnapshot,
    ) -> Dict[str, RootResolutionBlueprint]:
        """
        Build a RootResolutionBlueprint for every root spell in the snapshot.

        Args:
            snapshot:
                SpellSystemAdjacencySnapshot for the *entire* spell frame.

                - snapshot.dependencies:
                    Dict[version_id, Set[version_id]]
                    (child_version_id -> direct provider version_ids)
                - snapshot.root_spell_ids:
                    Set[version_id] for entrypoint spells.

        Returns:
            Dict[str, RootResolutionBlueprint]:
                Mapping from root version_id -> RootResolutionBlueprint.
        """
        if snapshot is None:
            raise ValueError("snapshot must not be None.")

        root_ids: Set[str] = snapshot.root_spell_ids
        if not root_ids:
            # Weird but legal: empty frame or misconfigured snapshot.
            # Nothing to compile; just return an empty mapping.
            return {}

        dependencies = snapshot.dependencies

        result: Dict[str, RootResolutionBlueprint] = {}

        for root_spell_id in root_ids:
            dag, ordered_ids = self._build_single_root_dag(
                root_spell_id=root_spell_id,
                dependencies=dependencies,
            )

            blueprint = RootResolutionBlueprint(
                root_spell_id=root_spell_id,
                root_lineage_id=None,          # can be threaded later if you want
                dag=dag,
                ordered_node_ids=ordered_ids,  # already a Sequence[str]
                socket_refs=None,              # Phase 5 socket overlay will fill this
                dag_index=None,                # Phase 5 DagIndex builder will fill this
            )

            result[root_spell_id] = blueprint

        return result

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _build_single_root_dag(
            self,
            root_spell_id: str,
            dependencies: Dict[str, Set[str]],
    ) -> Tuple[DirectedAcyclicWorkGraph, Sequence[str]]:
        """
        Internal helper.

        Build a deep DirectedAcyclicWorkGraph for a single root spell:

            * Nodes: all version_ids reachable from `root_spell_id`
              by recursively following `dependencies`.
            * Edges: provider → dependent (same orientation as Phase 3 DAG).

        Args:
            root_spell_id:
                Version-id of the root spell for this blueprint.
            dependencies:
                Dict[child_version_id, Set[parent_version_id]] – i.e. each spell's
                direct provider dependencies.

        Returns:
            Tuple[DirectedAcyclicWorkGraph, Sequence[str]]:
                - The constructed DAG.
                - A topologically sorted list of all node ids in that DAG.
        """
        if not root_spell_id:
            raise ValueError("root_spell_id must not be empty.")

        dag = DirectedAcyclicWorkGraph()

        visited: Set[str] = set()
        stack: List[str] = [root_spell_id]

        while stack:
            current_id = stack.pop()
            if current_id in visited:
                continue
            visited.add(current_id)

            # Structural DAG: payloads are not used at Phase 5.
            dag.add_node(key=current_id, payload=None)

            direct_parents: Optional[Set[str]] = dependencies.get(current_id)
            if not direct_parents:
                continue

            for parent_id in direct_parents:
                # Ensure provider node exists.
                dag.add_node(key=parent_id, payload=None)

                # Edge orientation: provider → dependent.
                # No param_name / socket_kind yet; those are part of later overlays.
                dag.add_dependency(
                    parent_key=parent_id,
                    child_key=current_id,
                    param_name=None,
                    socket_kind=None,
                )

                if parent_id not in visited:
                    stack.append(parent_id)

        # Use your existing topological helper; no root arg.
        ordered_ids: List[str] = dag.collect_dependency_ids()
        return dag, ordered_ids
