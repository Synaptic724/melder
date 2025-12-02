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
              - node payloads are None,
              - param_name and socket_kind on edges are left unset (None).
          Socket metadata and DagIndex are overlaid in later Phase-5 steps.
    """

    __slots__: list[str] = []

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
                    (spell_id -> direct dependency version_ids; consumer → providers)
                - snapshot.root_spell_ids:
                    Set[version_id] of structural roots for this frame.

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

        dependencies: Dict[str, Set[str]] = snapshot.dependencies

        result: Dict[str, RootResolutionBlueprint] = {}

        for root_spell_id in root_ids:
            dag, ordered_ids = self._build_single_root_dag(
                root_spell_id=root_spell_id,
                dependencies=dependencies,
            )

            blueprint = RootResolutionBlueprint(
                root_spell_id=root_spell_id,
                root_lineage_id=None,          # lineages can be threaded later if needed
                dag=dag,
                ordered_node_ids=ordered_ids,  # Sequence[str] in topo order
                socket_refs=None,              # Phase-5 socket overlay will populate
                dag_index=None,                # Phase-5 DagIndex builder will populate
            )

            result[root_spell_id] = blueprint

        return result

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #

    def _build_single_root_dag(
            self,
            root_spell_id: str,
            dependencies: Dict[str, Set[str]],
    ) -> Tuple[DirectedAcyclicWorkGraph, Sequence[str]]:
        """
        Internal helper.

        Build a deep DirectedAcyclicWorkGraph for a single root spell:

            * Nodes: all version_ids reachable from ``root_spell_id``
              by recursively following ``dependencies``.
            * Edges: provider → dependent (same orientation as Phase 3 DAG).

        Args:
            root_spell_id:
                Version-id of the root spell for this blueprint.
            dependencies:
                Mapping of ``spell_id -> { dependency_spell_id, ... }`` where
                edges are **consumer → providers** at the adjacency level.

        Returns:
            A tuple of:

            - The constructed DirectedAcyclicWorkGraph.
            - A Sequence[str] of node ids in topological order
              (dependencies first, root last).

        Raises:
            ValueError:
                If root_spell_id or dependencies is None.
            RuntimeError:
                If a cycle is detected while topologically sorting the DAG.
        """
        if root_spell_id is None:
            raise ValueError("root_spell_id must not be None.")
        if dependencies is None:
            raise ValueError("dependencies must not be None.")

        # ------------------------------------------------------------------
        # 1. Discover all nodes reachable from this root.
        # ------------------------------------------------------------------
        reachable_ids: Set[str] = set()
        stack: List[str] = [root_spell_id]

        while stack:
            current_id = stack.pop()
            if current_id in reachable_ids:
                continue

            reachable_ids.add(current_id)

            direct_deps: Optional[Set[str]] = dependencies.get(current_id)
            if not direct_deps:
                continue

            # Use a deterministic order so that traversal (and therefore
            # eventual DAG layout) is stable across runs.
            for dep_id in sorted(direct_deps):
                if dep_id not in reachable_ids:
                    stack.append(dep_id)

        # ------------------------------------------------------------------
        # 2. Build the DAG nodes (one per reachable version-id).
        # ------------------------------------------------------------------
        dag = DirectedAcyclicWorkGraph()

        for spell_id in reachable_ids:
            # Purely structural: payload is None. Payloads at this level
            # would couple the blueprint too tightly to runtime objects.
            dag.add_node(key=spell_id, payload=None)

        # ------------------------------------------------------------------
        # 3. Add provider → dependent edges within the reachable subgraph.
        # ------------------------------------------------------------------
        for consumer_id in reachable_ids:
            direct_deps = dependencies.get(consumer_id)
            if not direct_deps:
                continue

            for provider_id in direct_deps:
                if provider_id not in reachable_ids:
                    # Dependency exists in the global graph but is not
                    # reachable from this root's DFS (should not happen,
                    # but guard defensively).
                    continue

                dag.add_dependency(
                    parent_key=provider_id,
                    child_key=consumer_id,
                    param_name=None,
                    socket_kind=None,
                )

        # ------------------------------------------------------------------
        # 4. Compute a stable topological ordering of node ids.
        # ------------------------------------------------------------------
        try:
            ordered_node_ids: List[str] = dag.collect_dependency_ids()
        except RuntimeError as exc:
            # Clean up the DAG to avoid leaking partially-constructed graphs
            # in the face of structural bugs (cycles).
            dag.cleanup()
            raise RuntimeError(
                f"Cycle detected while building deep DAG for root '{root_spell_id}'."
            ) from exc

        return dag, ordered_node_ids
