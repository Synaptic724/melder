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
        * Edges are provider -> dependent (same orientation as Phase 3 DAGs).
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
                    (spell_id -> direct dependency version_ids; consumer -> providers)
                - snapshot.root_spell_ids:
                    Set[version_id] of structural roots for this frame.

        Returns:
            Dict[str, RootResolutionBlueprint]:
                Mapping from root version_id -> RootResolutionBlueprint.
        """
        root_ids: Set[str] = snapshot.root_spell_ids
        dependencies: Dict[str, Set[str]] = snapshot.dependencies

        result: Dict[str, RootResolutionBlueprint] = {}

        for root_spell_id in root_ids:
            dag, ordered_ids = self._build_single_root_dag(
                root_spell_id=root_spell_id,
                dependencies=dependencies,
                allowed_spell_ids=snapshot.all_spell_ids,
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

        """

        dag, ordered_ids = self._build_single_root_dag(
            root_spell_id=root_spell_id,
            dependencies=snapshot.dependencies,
            allowed_spell_ids=snapshot.all_spell_ids,
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
            allowed_spell_ids: Optional[Set[str]] = None,
    ) -> Tuple[DirectedAcyclicWorkGraph, Sequence[str]]:
        """
        Internal helper.

        Build a deep DirectedAcyclicWorkGraph for a single root spell:

            * Nodes: all version_ids reachable from ``root_spell_id``
              by recursively following ``dependencies``.
            * Edges: provider -> dependent (same orientation as Phase 3 DAG).

        Args:
            root_spell_id:
                Version-id of the root spell for this blueprint.
            dependencies:
                Mapping of ``spell_id -> { dependency_spell_id, ... }`` where
                edges are **consumer -> providers** at the adjacency level.
            allowed_spell_ids:
                Optional membership filter that limits traversal to visible spell ids.

        Returns:
            A tuple of:

            - The constructed DirectedAcyclicWorkGraph.
            - A Sequence[str] of node ids in topological order
              (dependencies first, root last).

        """

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

            direct_deps: Set[str] = dependencies.get(current_id, set())
            for dep_id in direct_deps:
                if allowed_spell_ids is not None and dep_id not in allowed_spell_ids:
                    continue
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
        # 3. Add provider -> dependent edges within the reachable subgraph.
        # ------------------------------------------------------------------
        for consumer_id in reachable_ids:
            direct_deps = dependencies.get(consumer_id, set())
            for provider_id in direct_deps:
                if provider_id in reachable_ids:
                    dag.add_dependency(
                        parent_key=provider_id,
                        child_key=consumer_id,
                        param_name=None,
                        socket_kind=None,
                    )

        # ------------------------------------------------------------------
        # 4. Compute a stable topological ordering of node ids.
        # ------------------------------------------------------------------
        ordered_node_ids: List[str] = dag.collect_dependency_ids()

        return dag, ordered_node_ids

    def _overlay_sockets_and_index(
            self,
            blueprint: RootResolutionBlueprint,
            topologies: Dict[str, SpellLocalTopology],
    ) -> None:
        """
        Overlay SocketRefs and build a deep DagIndex for the blueprint.
        """
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

                for target_id in socket_desc.target_spell_ids:
                    queue.append((target_id, socket_path))
