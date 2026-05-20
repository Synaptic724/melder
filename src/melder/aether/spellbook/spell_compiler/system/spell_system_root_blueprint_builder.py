from collections import deque
from typing import Collection, Deque, Dict, List, Optional, Sequence, Set, Tuple

from mypy_extensions import mypyc_attr

from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_compiler.dag.dag_index import DagIndex, SocketRef
from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.aether.spellbook.spell_compiler.system.spell_system_adjacency_snapshot import (
    SpellSystemAdjacencySnapshot,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
@mypyc_attr(native_class=True)
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

        for root_spell_id in sorted(root_ids):
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
            - Produces deterministic node/edge insertion order for equivalent
              dependency graphs.

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
            allowed_spell_ids: Optional[Collection[str]] = None,
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
                Optional membership filter that limits traversal to visible spell
                ids. Set semantics are not required here; the helper only
                performs membership checks against the provided collection.

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
        visible_spell_ids = allowed_spell_ids

        while stack:
            current_id = stack.pop()
            if current_id in reachable_ids:
                continue

            reachable_ids.add(current_id)

            direct_deps = dependencies.get(current_id)
            if not direct_deps:
                continue
            # Traversal order is intentionally not sorted here; final node and edge
            # order is normalized by deterministic sorted passes below.
            for dep_id in direct_deps:
                if visible_spell_ids is not None and dep_id not in visible_spell_ids:
                    continue
                if dep_id not in reachable_ids:
                    stack.append(dep_id)

        # ------------------------------------------------------------------
        # 2. Build the DAG nodes (one per reachable version-id).
        # ------------------------------------------------------------------
        dag = DirectedAcyclicWorkGraph()
        # Purely structural: payload is None. Payloads at this level
        # would couple the blueprint too tightly to runtime objects.
        ordered_reachable_ids = sorted(reachable_ids)
        dag.add_nodes_bulk(ordered_reachable_ids)

        # ------------------------------------------------------------------
        # 3. Add provider -> dependent edges within the reachable subgraph.
        # ------------------------------------------------------------------
        dag.add_dependencies_bulk(
            (
                (provider_id, consumer_id, None, None)
                for consumer_id in ordered_reachable_ids
                for provider_id in sorted(dependencies.get(consumer_id) or ())
                if provider_id in reachable_ids
            )
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
        Overlay SocketRefs and prepare the PathRegistry for the blueprint.

        Contract:
            - PathIds are extended via the blueprint PathRegistry.
            - DagIndex maps are built lazily when overrides are requested.
        """
        queue: Deque[Tuple[str, int]] = deque()

        # Start with a fresh index to avoid stale entries in case of reuse.
        blueprint.replace_dag_index(DagIndex())
        blueprint.check_cleaned()
        socket_refs = blueprint._socket_refs
        path_registry = blueprint.path_registry
        path_registry.check_cleaned()
        root_path_id = path_registry.root_path_id
        root_key = (blueprint.root_spell_id, root_path_id)
        queue.append(root_key)

        visited: Set[Tuple[str, int]] = {root_key}
        # Cache per (parent path id, param name) to avoid repeated registry lookups.
        path_cache: Dict[Tuple[int, str], int] = {}

        while queue:
            node_id, path_id = queue.popleft()

            topology = topologies.get(node_id)
            if topology is None:
                continue

            for socket_desc in topology.sockets:
                param_name = socket_desc.param_name
                cache_key = (path_id, param_name)
                socket_path_id = path_cache.get(cache_key)
                if socket_path_id is None:
                    socket_path_id = path_registry.extend_path(path_id, param_name)
                    path_cache[cache_key] = socket_path_id
                socket_ref = SocketRef(
                    node_id=node_id,
                    param_name=param_name,
                    param_path_id=socket_path_id,
                    socket_kind=socket_desc.socket_kind,
                )
                socket_refs.append(socket_ref)

                for target_id in socket_desc.target_spell_ids:
                    target_key = (target_id, socket_path_id)
                    if target_key in visited:
                        continue
                    visited.add(target_key)
                    queue.append(target_key)
