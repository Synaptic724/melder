from collections import deque
from typing import (
    TYPE_CHECKING,
    Collection,
    Deque,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    ClassVar,
    FrozenSet,
)
from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_compiler.dag.dag_index import DagIndex, SocketRef
from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.system.spell_system_adjacency_snapshot import (
        SpellSystemAdjacencySnapshot,
    )
    from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
        SpellLocalTopology,
    )

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
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__: list[str] = [
        "_reachable_by_id",
        "_requires_spellspace_request_by_id",
        "_reachable_snapshot_id",
        "_reachable_spellspace_scoped_spell_ids",
    ]

    def __init__(self) -> None:
        """Initialize the builder with an empty per-snapshot reachability memo."""
        self._reachable_by_id: Optional[Dict[str, Set[str]]] = None
        self._requires_spellspace_request_by_id: Optional[Dict[str, bool]] = None
        self._reachable_snapshot_id: Optional[int] = None
        self._reachable_spellspace_scoped_spell_ids: Optional[FrozenSet[str]] = None

    def build_root_blueprints(
            self,
            snapshot: SpellSystemAdjacencySnapshot,
            spellspace_scoped_spell_ids: Optional[Set[str]] = None,
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
        (
            reachable_by_id,
            requires_spellspace_request_by_id,
        ) = self._reachable_by_id_for(
            snapshot,
            spellspace_scoped_spell_ids,
        )
        result: Dict[str, RootResolutionBlueprint] = {}

        for root_spell_id in sorted(root_ids):
            dag, ordered_ids = self._build_single_root_dag(
                root_spell_id=root_spell_id,
                dependencies=dependencies,
                allowed_spell_ids=snapshot.all_spell_ids,
                reachable_ids=reachable_by_id.get(root_spell_id),
            )

            blueprint = RootResolutionBlueprint(
                root_spell_id=root_spell_id,
                root_lineage_id=None,          # lineages can be threaded later if needed
                dag=dag,
                ordered_node_ids=ordered_ids,  # Sequence[str] in topo order
                requires_spellspace_request=requires_spellspace_request_by_id.get(root_spell_id, False),
                socket_refs=None,              # Phase-5 socket overlay will populate
                dag_index=None,                # Phase-5 DagIndex builder will populate
            )

            topologies = snapshot.topologies
            if topologies is None:
                raise RuntimeError("Missing topologies in SpellSystemAdjacencySnapshot")
            self._overlay_sockets_and_index(
                blueprint=blueprint,
                topologies=topologies,
            )

            result[root_spell_id] = blueprint

        return result

    def build_blueprint_for_spell_id(
            self,
            *,
            root_spell_id: str,
            snapshot: SpellSystemAdjacencySnapshot,
            spellspace_scoped_spell_ids: Optional[Set[str]] = None,
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
        (
            reachable_by_id,
            requires_spellspace_request_by_id,
        ) = self._reachable_by_id_for(
            snapshot,
            spellspace_scoped_spell_ids,
        )
        dag, ordered_ids = self._build_single_root_dag(
            root_spell_id=root_spell_id,
            dependencies=snapshot.dependencies,
            allowed_spell_ids=snapshot.all_spell_ids,
            reachable_ids=reachable_by_id.get(root_spell_id),
        )

        blueprint = RootResolutionBlueprint(
            root_spell_id=root_spell_id,
            root_lineage_id=None,          # lineages can be threaded later if needed
            dag=dag,
            ordered_node_ids=ordered_ids,  # Sequence[str] in topo order
            requires_spellspace_request=requires_spellspace_request_by_id.get(root_spell_id, False),
            socket_refs=None,              # Phase-5 socket overlay will populate
            dag_index=None,                # Phase-5 DagIndex builder will populate
        )

        topologies = snapshot.topologies
        if topologies is None:
            raise RuntimeError("Missing topologies in SpellSystemAdjacencySnapshot")
        self._overlay_sockets_and_index(
            blueprint=blueprint,
            topologies=topologies,
        )

        return blueprint

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #

    def _reachable_by_id_for(
            self,
            snapshot: SpellSystemAdjacencySnapshot,
            spellspace_scoped_spell_ids: Optional[Set[str]] = None,
    ) -> Tuple[Dict[str, Set[str]], Dict[str, bool]]:
        """
        Return the reachable-id map for ``snapshot``, computing it once.

        Phase 5 builds a deep blueprint for every root and every non-root spell,
        and each build previously rediscovered its reachable subtree with a
        fresh DFS -- so a spell shared by many dependents had its subtree walked
        once per dependent. This memo computes every spell's reachable set a
        single time per snapshot; the result is consumed by
        ``_build_single_root_dag`` for all roots and per-spell blueprints.

        Memoized on snapshot identity; one builder instance only ever serves one
        snapshot, so this is effectively compute-once.
        """
        requested_spellspace_scoped_spell_ids: FrozenSet[str] = frozenset(
            spellspace_scoped_spell_ids or ()
        )
        cached = self._reachable_by_id
        cached_requires = self._requires_spellspace_request_by_id
        if (
                cached is not None
                and cached_requires is not None
                and self._reachable_snapshot_id == id(snapshot)
                and self._reachable_spellspace_scoped_spell_ids == requested_spellspace_scoped_spell_ids
        ):
            return cached, cached_requires
        computed, requires_spellspace_request_by_id = self._compute_reachable_by_id(
            dependencies=snapshot.dependencies,
            all_spell_ids=snapshot.all_spell_ids,
            spellspace_scoped_spell_ids=requested_spellspace_scoped_spell_ids,
        )
        self._reachable_by_id = computed
        self._requires_spellspace_request_by_id = requires_spellspace_request_by_id
        self._reachable_snapshot_id = id(snapshot)
        self._reachable_spellspace_scoped_spell_ids = requested_spellspace_scoped_spell_ids
        return computed, requires_spellspace_request_by_id

    def _compute_reachable_by_id(
            self,
            dependencies: Dict[str, Set[str]],
            all_spell_ids: Collection[str],
            spellspace_scoped_spell_ids: Collection[str],
    ) -> Tuple[Dict[str, Set[str]], Dict[str, bool]]:
        """
        Compute ``reachable(X)`` for every spell id, sharing subtree work.

        ``reachable(X)`` is ``{X}`` plus every version-id reachable by following
        ``dependencies``, restricted to ``all_spell_ids`` -- identical to the
        per-root DFS in ``_build_single_root_dag``.

        Spells are processed in provider-before-consumer (topological) order, so
        ``reachable(X)`` is composed from already-computed dependency closures in
        O(out-degree) instead of a fresh traversal. This makes the shared work
        O(V + E) total rather than O(roots x subtree).

        Cycle-safe: any spell a topological pass cannot order (a dependency
        cycle) is appended and resolved with a direct DFS closure, so the result
        matches the per-root DFS for cyclic graphs too.
        """
        allowed: Set[str] = set(all_spell_ids)

        # Kahn ordering over provider -> consumer edges (providers emitted first).
        indegree: Dict[str, int] = {}
        consumers_of: Dict[str, List[str]] = {}
        for consumer in allowed:
            providers = [
                provider
                for provider in dependencies.get(consumer, ())
                if provider in allowed
            ]
            indegree[consumer] = len(providers)
            for provider in providers:
                consumers_of.setdefault(provider, []).append(consumer)

        ready: Deque[str] = deque(
            node for node in allowed if indegree[node] == 0
        )
        order: List[str] = []
        while ready:
            node = ready.popleft()
            order.append(node)
            for consumer in consumers_of.get(node, ()):
                indegree[consumer] -= 1
                if indegree[consumer] == 0:
                    ready.append(consumer)

        # Nodes left unordered are inside a dependency cycle; append them so
        # their closures are still computed (via the DFS fallback below).
        if len(order) != len(allowed):
            ordered_set = set(order)
            order.extend(node for node in allowed if node not in ordered_set)

        reachable: Dict[str, Set[str]] = {}
        requires_spellspace_request_by_id: Dict[str, bool] = {}
        for node in order:
            closure: Set[str] = {node}
            requires_spellspace_request = node in spellspace_scoped_spell_ids
            for provider in dependencies.get(node, ()):
                if provider not in allowed:
                    continue
                provider_closure = reachable.get(provider)
                if provider_closure is not None:
                    closure |= provider_closure
                    if requires_spellspace_request_by_id.get(provider, False):
                        requires_spellspace_request = True
                else:
                    # Cycle member: provider closure not ready -> exact DFS.
                    fallback_closure = self._dfs_closure(provider, dependencies, allowed)
                    closure |= fallback_closure
                    if not requires_spellspace_request:
                        requires_spellspace_request = not fallback_closure.isdisjoint(
                            spellspace_scoped_spell_ids
                        )
            reachable[node] = closure
            requires_spellspace_request_by_id[node] = requires_spellspace_request
        return reachable, requires_spellspace_request_by_id

    @staticmethod
    def _dfs_closure(
            start: str,
            dependencies: Dict[str, Set[str]],
            allowed: Set[str],
    ) -> Set[str]:
        """
        Return the cycle-safe reachable closure of ``start`` within ``allowed``.

        Includes ``start`` itself. Used only as the fallback for spells inside a
        dependency cycle, where topological composition is not available.
        """
        closure: Set[str] = set()
        stack: List[str] = [start]
        while stack:
            current = stack.pop()
            if current in closure:
                continue
            closure.add(current)
            for dep in dependencies.get(current, ()):
                if dep in allowed and dep not in closure:
                    stack.append(dep)
        return closure

    def _build_single_root_dag(
            self,
            root_spell_id: str,
            dependencies: Dict[str, Set[str]],
            allowed_spell_ids: Optional[Collection[str]] = None,
            reachable_ids: Optional[Set[str]] = None,
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
        #    `reachable_ids` may be supplied precomputed once per snapshot so a
        #    subtree shared by many roots/per-spell blueprints is not
        #    re-traversed for each one; fall back to a local DFS otherwise.
        # ------------------------------------------------------------------
        if reachable_ids is None:
            reachable_ids = set()
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
        dependency_edges = []
        for consumer_id in ordered_reachable_ids:
            for provider_id in sorted(dependencies.get(consumer_id) or ()):
                if provider_id in reachable_ids:
                    dependency_edges.append(
                        (provider_id, consumer_id, None, None)
                    )

        dag.add_dependencies_bulk(dependency_edges)

        # ------------------------------------------------------------------
        # 4. Compute a stable topological ordering of node ids.
        # ------------------------------------------------------------------
        ordered_node_ids: List[str] = dag.collect_dependency_ids()

        return dag, ordered_node_ids

    def _overlay_sockets_and_index(
            self,
            blueprint: RootResolutionBlueprint,
            topologies: Dict[str, Optional[SpellLocalTopology]],
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
