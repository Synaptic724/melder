from collections import deque
from typing import Deque, Dict, List, Optional, Sequence, Set, Tuple

from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, SocketRef
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.system.spell_system_adjacency_snapshot import (
    SpellSystemAdjacencySnapshot,
)
from melder.spellbook.spell_crafter.topology.spell_local_topology import (
    SpellLocalTopology,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

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
    __melder_internal__ = _mrg.sentinel
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

            self._overlay_sockets_and_index(
                blueprint=blueprint,
                topologies=snapshot.topologies,
            )

            result[root_spell_id] = blueprint

        return result

    def build_blueprint_for_spell_id(
            self,
            *,
            root_spell_id: str,
            snapshot: SpellSystemAdjacencySnapshot,
    ) -> RootResolutionBlueprint:
        """
        Build a RootResolutionBlueprint for a specific spell id.

        Purpose:
            Compile a deep DAG blueprint for an arbitrary spell id so downstream
            phases can generate occurrence/injection/patch/execution artifacts
            even when the spell is not a structural root.

        Contract:
            - Uses the same structural semantics as build_root_blueprints.
            - The resulting DAG includes all nodes reachable from root_spell_id.
            - SocketRefs and DagIndex are overlaid from snapshot topologies.
            - Does not mutate the snapshot.

        Args:
            root_spell_id:
                Version-id of the spell to treat as the blueprint root.
            snapshot:
                SpellSystemAdjacencySnapshot for the *entire* spell frame.

        Returns:
            RootResolutionBlueprint:
                The compiled blueprint for the requested spell id.

        Raises:
            ValueError:
                If root_spell_id or snapshot is None.
            ValueError:
                If root_spell_id is not present in snapshot.all_spell_ids.
        """
        if root_spell_id is None:
            raise ValueError("root_spell_id must not be None.")
        if snapshot is None:
            raise ValueError("snapshot must not be None.")

        all_spell_ids: Set[str] = snapshot.all_spell_ids
        if root_spell_id not in all_spell_ids:
            raise ValueError(
                f"root_spell_id '{root_spell_id}' is not present in the snapshot."
            )

        dag, ordered_ids = self._build_single_root_dag(
            root_spell_id=root_spell_id,
            dependencies=snapshot.dependencies,
        )

        blueprint = RootResolutionBlueprint(
            root_spell_id=root_spell_id,
            root_lineage_id=None,          # lineages can be threaded later if needed
            dag=dag,
            ordered_node_ids=ordered_ids,  # Sequence[str] in topo order
            socket_refs=None,              # Phase-5 socket overlay will populate
            dag_index=None,                # Phase-5 DagIndex builder will populate
        )

        self._overlay_sockets_and_index(
            blueprint=blueprint,
            topologies=snapshot.topologies,
        )

        return blueprint

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

    def _overlay_sockets_and_index(
            self,
            blueprint: RootResolutionBlueprint,
            topologies: Dict[str, SpellLocalTopology],
    ) -> None:
        """
        Overlay SocketRefs and build a deep DagIndex for the blueprint.
        """
        if blueprint is None:
            raise ValueError("blueprint must not be None.")
        if topologies is None:
            raise ValueError("topologies must not be None.")

        queue: Deque[Tuple[str, Tuple[str, ...]]] = deque()
        queue.append((blueprint.root_spell_id, ()))

        # Start with a fresh index to avoid stale entries in case of reuse.
        blueprint.replace_dag_index(DagIndex())

        visited: Set[Tuple[str, Tuple[str, ...]]] = set()

        while queue:
            node_id, path = queue.popleft()
            key = (node_id, path)
            if key in visited:
                continue
            visited.add(key)

            topology = topologies.get(node_id)
            if topology is None:
                continue

            for socket_desc in topology.sockets:
                socket_path = path + (socket_desc.param_name,)
                socket_ref = SocketRef(
                    node_id=node_id,
                    param_name=socket_desc.param_name,
                    param_path=socket_path,
                    socket_kind=socket_desc.socket_kind,
                )
                blueprint.add_socket_ref(socket_ref)

                targets: Tuple[str, ...] = tuple(socket_desc.target_spell_ids or ())
                for target_id in targets:
                    queue.append((target_id, socket_path))
