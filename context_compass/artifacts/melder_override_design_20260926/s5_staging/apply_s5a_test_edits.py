"""S5a tests: compiled Phase-5 blueprints record no SocketRefs and mint no paths - anchored edits.

Usage: python apply_s5a_test_edits.py <tree_root> [--check]

Tests that pinned the retired per-path overlay keep their DAG and order assertions and now assert the new contract
(no SocketRef, no minted path). Validation tests of SocketRefSanityStrategy add hand-built refs; the component
DagTargetingEngine tests feed the engine hand-built refs through a test-side helper. Overlay-walk unit tests are
removed; unit tests for `_install_fresh_index` and an O(n) binary-chain build are added. Each anchor must match
exactly once or nothing is written. Engine: ../s3_staging/apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "s3_staging"))

from apply_s3b1_edits import _apply_one

UNIT = "tests/unit/melder/spellbook/spell_crafter/system/test_spell_system_root_blueprint_builder.py"
C_SYS = "tests/component/melder/spellbook/spell_crafter/system/"
ROOTS = C_SYS + "test_spellbook_component_spell_system_root_blueprint_builder.py"
ADJ = C_SYS + "test_spellbook_component_spell_system_adjacency_snapshot.py"
CONTRACTS = C_SYS + "test_spellbook_component_spell_system_phase5_contracts.py"
SYSTEM = C_SYS + "test_spellbook_component_spell_system.py"
PHASE5 = "tests/component/melder/spellbook/spell_crafter/phases/test_spellbook_component_spell_crafter_phase5.py"
TARGETING = "tests/component/melder/spellbook/spell_crafter/dag/test_spellbook_component_dag_targeting.py"
MELD = "tests/component/melder/aether/conduit/test_conduit_component_meld_overrides.py"
REQUIRED = "tests/component/melder/spellbook/test_spellbook_component_override_required.py"
INTEG = "tests/integration/melder/spellbook/test_spellbook_integration_validation_system.py"

NO_REFS_TEST = '''def test_compiled_blueprint_records_no_socket_refs_or_paths():
    """Phase 5 keeps the dependency DAG but records no SocketRef and mints no path, whatever the topologies hold."""
    deps = {"root": {"child"}, "child": {"leaf"}, "leaf": set()}
    root_top = SpellLocalTopology(
        spell_id="root",
        sockets=(SpellSocketDescriptor("root", "child", 0, SocketKind.NORMAL, False, False, ("child",)),),
    )
    child_top = SpellLocalTopology(
        spell_id="child",
        sockets=(SpellSocketDescriptor("child", "leaf", 0, SocketKind.NORMAL, False, True, ("leaf",)),),
    )
    snapshot = _snapshot(deps, roots={"root"}, topologies={"root": root_top, "child": child_top})
    blueprint = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    blueprint.ensure_dag_index_built()

    assert set(blueprint.dag.nodes) == {"root", "child", "leaf"}
    assert blueprint.socket_refs == []
    assert list(blueprint.dag_index.iter_all_sockets()) == []
    assert blueprint.path_registry.resolve_path_id(("child",)) is None


'''

REJECTS_OLD = '''def test_overlay_sockets_and_index_rejects_none():
    builder = SpellSystemRootBlueprintBuilder()
    dag = DirectedAcyclicWorkGraph()
    bp = RootResolutionBlueprint("r", None, dag)
    with pytest.raises(AttributeError):
        builder._overlay_sockets_and_index(None, {})  # type: ignore[arg-type]
    with pytest.raises(AttributeError):
        builder._overlay_sockets_and_index(bp, None)  # type: ignore[arg-type]
'''
REJECTS_NEW = '''def test_install_fresh_index_rejects_none_and_cleaned_blueprints():
    """A missing blueprint fails on attribute access; a cleaned blueprint refuses the new index."""
    builder = SpellSystemRootBlueprintBuilder()
    bp = RootResolutionBlueprint("r", None, DirectedAcyclicWorkGraph())
    with pytest.raises(AttributeError):
        builder._install_fresh_index(None)
    bp.cleanup()
    with pytest.raises(RuntimeError):
        builder._install_fresh_index(bp)
'''

NO_TOPOLOGY_OLD = '''    # Only the socket from root->mid is recorded; no refs for deeper missing topology.
    path_registry = bp.path_registry
    assert {path_registry.materialize_path(r.param_path_id) for r in bp.socket_refs} == {
        ("mid",)
    }
'''
NO_TOPOLOGY_NEW = '''    assert bp.socket_refs == []
'''

CHAIN_TEST = '''def test_shared_binary_chain_builds_without_walking_paths():
    """Every spell takes the next one twice (2**20 logical paths); Phase 5 builds it in time linear in spells."""
    depth = 20
    names = [f"c{i}" for i in range(depth)]
    deps = {name: ({names[i + 1]} if i + 1 < depth else set()) for i, name in enumerate(names)}
    topologies = {
        name: SpellLocalTopology(
            spell_id=name,
            sockets=(
                SpellSocketDescriptor(name, "a", 0, SocketKind.NORMAL, False, False, (names[i + 1],)),
                SpellSocketDescriptor(name, "b", 1, SocketKind.NORMAL, False, False, (names[i + 1],)),
            ),
        )
        for i, name in enumerate(names[:-1])
    }
    snapshot = _snapshot(deps, roots={"c0"}, topologies=topologies)
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["c0"]
    assert set(bp.dag.nodes) == set(names)
    assert bp.ordered_node_ids[-1] == "c0"
    assert bp.socket_refs == []
    assert bp.path_registry.resolve_path_id(("a",)) is None


'''

IDEMPOTENT_OLD = '''def test_overlay_idempotent_call_replaces_index():
    deps = {"root": set()}
    topo = SpellLocalTopology(spell_id="root", sockets=())
    snapshot = _snapshot(deps, roots={"root"}, topologies={"root": topo})
    builder = SpellSystemRootBlueprintBuilder()
    bp = builder.build_root_blueprints(snapshot)["root"]
    old_index = bp.dag_index
    builder._overlay_sockets_and_index(bp, snapshot.topologies)
    assert bp.dag_index is not old_index
'''
IDEMPOTENT_NEW = '''def test_install_fresh_index_replaces_index_and_registry():
    """A second call drops the old index and registry, so no stale path id survives."""
    deps = {"root": set()}
    topo = SpellLocalTopology(spell_id="root", sockets=())
    snapshot = _snapshot(deps, roots={"root"}, topologies={"root": topo})
    builder = SpellSystemRootBlueprintBuilder()
    bp = builder.build_root_blueprints(snapshot)["root"]
    old_index = bp.dag_index
    old_registry = bp.path_registry
    old_registry.extend_path(old_registry.root_path_id, "stale")
    builder._install_fresh_index(bp)
    assert bp.dag_index is not old_index
    assert bp.path_registry is not old_registry
    assert bp.path_registry.resolve_path_id(("stale",)) is None
'''

UNIT_EDITS = [
    ("cut", "def test_overlay_sockets_and_index_builds_paths():", "def test_overlay_sockets_no_topologies_results_in_empty_index():"),
    ("replace", "def test_overlay_sockets_no_topologies_results_in_empty_index():\n",
     NO_REFS_TEST + "def test_blueprint_without_topologies_has_empty_index():\n"),
    ("replace", REJECTS_OLD, REJECTS_NEW),
    ("cut", "def test_overlay_walks_branching_paths():", "def test_build_single_root_dag_validates_inputs():"),
    ("cut", "def test_overlay_skips_missing_child_topology():",
     "def test_overlay_handles_cycle_in_topology_without_infinite_loop():"),
    ("replace", "def test_overlay_handles_cycle_in_topology_without_infinite_loop():\n",
     "def test_build_root_blueprints_refuses_dependency_cycle():\n"),
    ("cut", "def test_overlay_preserves_socket_kind():", "def test_build_single_root_dag_skips_revisiting_reachable_ids():"),
    ("replace", NO_TOPOLOGY_OLD, NO_TOPOLOGY_NEW),
    ("cut", "def test_overlay_stops_on_missing_topology_paths():", "def test_overlay_leaves_topologies_map_intact():"),
    ("replace", "def test_overlay_leaves_topologies_map_intact():\n",
     CHAIN_TEST + "def test_build_root_blueprints_leaves_topologies_map_intact():\n"),
    ("replace", "def test_overlay_no_topology_means_no_socket_refs_even_if_dependencies():\n",
     "def test_blueprint_without_topologies_records_no_socket_refs():\n"),
    ("replace", "def test_overlay_accepts_empty_topologies_and_non_empty_deps():\n",
     "def test_build_root_blueprints_accepts_empty_topologies():\n"),
    ("cut", "def test_overlay_handles_deep_chain_paths():", "def test_overlay_idempotent_call_replaces_index():"),
    ("replace", IDEMPOTENT_OLD, IDEMPOTENT_NEW),
]

NO_PATH = '''        assert blueprint.socket_refs == []
        assert blueprint.path_registry.resolve_path_id(("{0}",)) is None
'''

ROOTS_EDITS = [
    ("replace", '''def test_component_root_blueprint_builder_traverses_state_topologies() -> None:
    """
    Purpose:
        Validate root blueprint builder consumes state topologies.
    Contract:
        - Socket refs include nested param paths across dependencies.
        - DagIndex resolves sockets by exact path.
    Returns:
        None.
    Raises:
        AssertionError: If socket traversal or indexing is incorrect.
''', '''def test_component_root_blueprint_builder_mints_no_paths_from_state_topologies() -> None:
    """
    Purpose:
        Validate the root blueprint builder builds the DAG from state and walks no paths.
    Contract:
        - The DAG holds the full chain and the root is ordered last.
        - No SocketRef is recorded and no path is minted (Phase 8 mints paths).
    Returns:
        None.
    Raises:
        AssertionError: If the DAG is incomplete or socket refs appear.
'''),
    ("replace", '''        blueprint.ensure_dag_index_built()
        path_registry = blueprint.path_registry
        assert {path_registry.materialize_path(ref.param_path_id) for ref in blueprint.socket_refs} == {
            ("mid",),
            ("mid", "leaf"),
        }

        root_socket = blueprint.dag_index.get_by_exact_path(("mid",))[0]
        leaf_socket = blueprint.dag_index.get_by_exact_path(("mid", "leaf"))[0]
        assert root_socket.node_id == root_id
        assert leaf_socket.node_id == mid_id
''', "        assert set(blueprint.dag.nodes) == {root_id, mid_id, leaf_id}\n" + NO_PATH.format("mid")),
    ("replace", '''def test_component_root_blueprint_builder_skips_missing_topology() -> None:
    """
    Purpose:
        Validate missing topologies prune socket traversal.
    Contract:
        - Socket refs are only collected for spells with registered topologies.
        - DAG still contains the full dependency chain.
    Returns:
        None.
    Raises:
        AssertionError: If socket collection ignores missing topologies.
''', '''def test_component_root_blueprint_builder_keeps_spells_without_topology() -> None:
    """
    Purpose:
        Validate a missing topology does not shorten the DAG.
    Contract:
        - No SocketRef is recorded.
        - DAG still contains the full dependency chain.
    Returns:
        None.
    Raises:
        AssertionError: If the DAG drops a spell without a topology.
'''),
    ("replace", '''        blueprint.ensure_dag_index_built()
        path_registry = blueprint.path_registry
        assert {path_registry.materialize_path(ref.param_path_id) for ref in blueprint.socket_refs} == {("mid",)}
        assert blueprint.dag_index.get_by_exact_path(("mid", "leaf")) == []
''', "        assert blueprint.socket_refs == []\n"),
    ("replace", '''def test_component_root_blueprint_builder_records_empty_target_sockets() -> None:
    """
    Purpose:
        Validate sockets with empty target spell ids are still indexed.
    Contract:
        - Socket refs are emitted even when target_spell_ids is empty.
        - DagIndex resolves the socket path for the root spell.
    Returns:
        None.
    Raises:
        AssertionError: If socket refs are missing.
''', '''def test_component_root_blueprint_builder_ignores_empty_target_sockets() -> None:
    """
    Purpose:
        Validate a socket with no target spell ids leaves a root-only blueprint.
    Contract:
        - The DAG holds only the root.
        - No SocketRef is recorded.
    Returns:
        None.
    Raises:
        AssertionError: If socket refs are recorded or the DAG grows.
'''),
    ("replace", '''        blueprint.ensure_dag_index_built()
        path_registry = blueprint.path_registry
        assert {path_registry.materialize_path(ref.param_path_id) for ref in blueprint.socket_refs} == {("config",)}
        assert blueprint.dag_index.get_by_exact_path(("config",)) != []
''', "        assert set(blueprint.dag.nodes) == {root_id}\n        assert blueprint.socket_refs == []\n"),
]

ADJ_EDITS = [
    ("replace", '''def test_component_snapshot_topologies_feed_blueprint_builder() -> None:
    """
    Purpose:
        Validate snapshot topologies are used to seed blueprint socket refs.
    Contract:
        - Socket refs match registered topology sockets.
        - DagIndex resolves the socket path.
    Returns:
        None.
    Raises:
        AssertionError: If socket refs are not recorded.
''', '''def test_component_snapshot_topologies_mint_no_blueprint_paths() -> None:
    """
    Purpose:
        Validate a snapshot with topologies builds the dependency DAG and no socket refs.
    Contract:
        - The DAG holds the root and its dependency.
        - Topology sockets are not copied into SocketRefs and mint no path.
    Returns:
        None.
    Raises:
        AssertionError: If socket refs are recorded or the DAG is incomplete.
'''),
    ("replace", '''        blueprint.ensure_dag_index_built()
        path_registry = blueprint.path_registry
        assert {path_registry.materialize_path(ref.param_path_id) for ref in blueprint.socket_refs} == {("dep",)}
        assert blueprint.dag_index.get_by_exact_path(("dep",)) != []
''', "        assert set(blueprint.dag.nodes) == {root_id, dep_id}\n" + NO_PATH.format("dep")),
]

CONTRACTS_EDITS = [
    ("replace", '''def test_component_phase5_contract_dependencies_generate_nested_socket_paths() -> None:
    """
    Purpose:
        Validate nested socket paths span contracted dependency graphs.
    Contract:
        - Contracted dependency graphs populate deep socket paths.
        - Root blueprints include the contracted dependency DAG.
    Returns:
        None.
    Raises:
        AssertionError: If nested socket paths or DAG nodes are missing.
''', '''def test_component_phase5_contract_dependencies_span_borrower_blueprint() -> None:
    """
    Purpose:
        Validate a borrower's root blueprint spans the contracted dependency graph.
    Contract:
        - Root blueprints include the contracted dependency DAG.
        - No SocketRef is recorded (Phase 8 mints the deep paths).
    Returns:
        None.
    Raises:
        AssertionError: If DAG nodes are missing or socket refs appear.
'''),
    ("replace", '''        path_registry = blueprint.path_registry
        assert {path_registry.materialize_path(ref.param_path_id) for ref in blueprint.socket_refs} == {
            ("root",),
            ("root", "left"),
            ("root", "right"),
            ("root", "left", "left"),
            ("root", "left", "right"),
            ("root", "right", "left"),
            ("root", "right", "right"),
        }
''', NO_PATH.format("root")),
]

SYSTEM_EDITS = [
    ("replace", '''        - Deep DAG includes both consumer and dependency nodes.
        - Socket refs and DagIndex are populated from local topology.
    Returns:
        None.
    Raises:
        AssertionError: If blueprint structure or socket indexing is missing.
''', '''        - Deep DAG includes both consumer and dependency nodes.
        - No SocketRef is recorded and no path is minted (Phase 8 mints paths).
    Returns:
        None.
    Raises:
        AssertionError: If blueprint structure is wrong or socket refs appear.
'''),
    ("replace", '''        blueprint = blueprints[consumer_id]
        blueprint.ensure_dag_index_built()
''', "        blueprint = blueprints[consumer_id]\n"),
    ("replace", '''        sockets = blueprint.socket_refs
        assert len(sockets) == 1
        socket = sockets[0]
        assert socket.node_id == consumer_id
        assert socket.param_name == "service"
        path_registry = blueprint.path_registry
        assert path_registry.materialize_path(socket.param_path_id) == ("service",)

        by_path = blueprint.dag_index.get_by_exact_path(("service",))
        assert by_path and by_path[0] == socket
''', NO_PATH.format("service")),
    ("replace", '''        - socket_ref_duplicate is reported when a SocketRef is duplicated.
''', '''        - socket_ref_duplicate is reported when a SocketRef is duplicated (added by
          hand: compiled blueprints record none).
'''),
    ("replace", '''        socket = blueprint.socket_refs[0]
        blueprint.add_socket_ref(socket)
''', '''        path_registry = blueprint.path_registry
        socket = SocketRef(
            node_id=root_id,
            param_name="dependency",
            param_path_id=path_registry.extend_path(path_registry.root_path_id, "dependency"),
            socket_kind=SocketKind.NORMAL,
        )
        blueprint.add_socket_ref(socket)
        blueprint.add_socket_ref(socket)
'''),
]

PHASE5_EDITS = [
    ("replace", '''def test_component_phase5_blueprint_includes_deep_socket_paths() -> None:
    """
    Purpose:
        Validate Phase 5 builds deep socket paths from real topologies.
    Contract:
        - The root blueprint exists for the root spell.
        - Socket paths include the direct dependency and the nested dependency.
        - Topological order ends with the root spell id.
''', '''def test_component_phase5_blueprint_includes_deep_dag_without_socket_paths() -> None:
    """
    Purpose:
        Validate Phase 5 builds the deep DAG from real topologies and walks no paths.
    Contract:
        - The root blueprint exists for the root spell.
        - Its order holds the direct and nested dependencies and ends with the root.
        - No SocketRef is recorded (Phase 8 mints the paths).
'''),
    ("replace", '''        blueprint.ensure_dag_index_built()

        ordered = blueprint.ordered_node_ids
''', "        ordered = blueprint.ordered_node_ids\n"),
    ("replace", '''
        repo_refs = blueprint.dag_index.get_by_exact_path(("repository",))
        deep_refs = blueprint.dag_index.get_by_exact_path(("repository", "logger"))
        assert repo_refs
        assert deep_refs
        assert any(ref.node_id == root_id for ref in repo_refs)
        assert any(ref.node_id == repo_id for ref in deep_refs)
''', NO_PATH.format("repository")),
]

HELPER = '''def _add_socket_refs(
        blueprint: RootResolutionBlueprint,
        topologies: Mapping[str, Optional[SpellLocalTopology]],
) -> None:
    """
    Purpose:
        Record one SocketRef per socket per root path on a compiled blueprint.
    Contract:
        - Compiled blueprints carry no SocketRefs since 2026-09-26 (Phase 5 walks no
          paths), so these targeting tests give the engine its input by hand,
          breadth-first from the root, the way the retired overlay did.
        - Paths are interned in the blueprint's own PathRegistry.
    Args:
        blueprint: Compiled root blueprint to populate.
        topologies: Local topologies keyed by spell id.
    Returns:
        None.
    """
    registry = blueprint.path_registry
    queue = [(blueprint.root_spell_id, registry.root_path_id)]
    while queue:
        node_id, path_id = queue.pop(0)
        topology = topologies.get(node_id)
        if topology is None:
            continue
        for socket in topology.sockets:
            socket_path_id = registry.extend_path(path_id, socket.param_name)
            blueprint.add_socket_ref(
                SocketRef(
                    node_id=node_id,
                    param_name=socket.param_name,
                    param_path_id=socket_path_id,
                    socket_kind=socket.socket_kind,
                )
            )
            for target_id in socket.target_spell_ids:
                queue.append((target_id, socket_path_id))


'''

TARGETING_EDITS = [
    ("replace", "from melder.aether.aether import Aether\n",
     "from typing import Mapping, Optional\n\nfrom melder.aether.aether import Aether\n"),
    ("replace", "from melder.aether.spellbook.spell_compiler.dag.dag_index import DagTargetingEngine\n",
     "from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (\n"
     "    RootResolutionBlueprint,\n)\n"
     "from melder.aether.spellbook.spell_compiler.dag.dag_index import DagTargetingEngine, SocketRef\n"),
    ("replace", "def _build_blueprint():\n", HELPER + "def _build_blueprint():\n"),
    ("replace", '''        - Returns a RootResolutionBlueprint with a populated DagIndex.
''', '''        - Returns a RootResolutionBlueprint with a populated DagIndex (refs added by
          `_add_socket_refs`, since compiled blueprints record none).
'''),
    ("replace", '''    blueprint = blueprints[root_id]
    blueprint.ensure_dag_index_built()
''', '''    blueprint = blueprints[root_id]
    _add_socket_refs(blueprint, snapshot.topologies)
    blueprint.ensure_dag_index_built()
'''),
]

MELD_EDITS = [
    ("replace", '''def test_component_meld_root_blueprint_paths_two_node_graph() -> None:
    """
    Purpose:
        Validate root blueprint paths for a simple root->dependency graph.
    Contract:
        - Socket refs include "repo" and "repo>name" paths.
        - Each exact path maps to a single socket in the DagIndex.
        - Ordered nodes include the dependency before the root.
    Returns:
        None.
    Raises:
        AssertionError: If the deep path index is incomplete.
''', '''def test_component_meld_root_blueprint_order_two_node_graph() -> None:
    """
    Purpose:
        Validate the root blueprint for a simple root->dependency graph.
    Contract:
        - Ordered nodes include the dependency before the root.
        - No SocketRef is recorded (Phase 8 mints the paths).
    Returns:
        None.
    Raises:
        AssertionError: If the order is wrong or socket refs appear.
'''),
    ("replace", '''    blueprint.ensure_dag_index_built()

    ordered_ids = blueprint.ordered_node_ids
    assert repo_id in ordered_ids
''', '''    ordered_ids = blueprint.ordered_node_ids
    assert repo_id in ordered_ids
'''),
    ("replace", '''    path_registry = blueprint.path_registry
    socket_paths = {path_registry.materialize_path(socket.param_path_id) for socket in blueprint.socket_refs}
    assert socket_paths == {("repo",), ("repo", "name")}
    assert len(blueprint.dag_index.get_by_exact_path(("repo",))) == 1
    assert len(blueprint.dag_index.get_by_exact_path(("repo", "name"))) == 1
''', "    assert blueprint.socket_refs == []\n"),
    ("replace", '''def test_component_meld_root_blueprint_paths_shared_dependency() -> None:
    """
    Purpose:
        Validate root blueprint paths for a shared dependency graph.
    Contract:
        - The DagIndex exposes distinct paths for each branch to the shared repo.
        - The root blueprint captures all expected socket paths.
        - Dependencies are ordered before the root in the execution order.
    Returns:
        None.
    Raises:
        AssertionError: If shared dependency paths are missing or duplicated.
''', '''def test_component_meld_root_blueprint_order_shared_dependency() -> None:
    """
    Purpose:
        Validate the root blueprint for a shared dependency graph.
    Contract:
        - The shared repo is one node, ordered before both services and the root.
        - No SocketRef is recorded (Phase 8 mints one path per branch).
    Returns:
        None.
    Raises:
        AssertionError: If the order is wrong or socket refs appear.
'''),
    ("replace", '''    blueprint.ensure_dag_index_built()

    ordered_ids = blueprint.ordered_node_ids
    assert ordered_ids[-1] == root_id
''', '''    ordered_ids = blueprint.ordered_node_ids
    assert ordered_ids[-1] == root_id
'''),
    ("replace", '''    expected_paths = {
        ("service_a",),
        ("service_b",),
        ("service_a", "repo"),
        ("service_b", "repo"),
        ("service_a", "repo", "name"),
        ("service_b", "repo", "name"),
    }
    path_registry = blueprint.path_registry
    socket_paths = {path_registry.materialize_path(socket.param_path_id) for socket in blueprint.socket_refs}
    assert socket_paths == expected_paths
    for path in expected_paths:
        assert len(blueprint.dag_index.get_by_exact_path(path)) == 1
''', "    assert blueprint.socket_refs == []\n"),
]

REQUIRED_EDITS = [
    ("replace", '''        if include_consumer:
            socket, = artifact._root_blueprint_phase5.socket_refs
            assert socket.socket_kind is SocketKind.OVERRIDE_REQUIRED
''', '''        if include_consumer:
            assert artifact._root_blueprint_phase5.socket_refs == []
            socket, = compiler_book._spell_system_states.get_local_topology_by_id(anchor_id).sockets
            assert socket.socket_kind is SocketKind.OVERRIDE_REQUIRED
'''),
]

HAND_REF = '''        socket = SocketRef(
            node_id=consumer_id,
            param_name="service",
            param_path_id=path_registry.extend_path(path_registry.root_path_id, "service"),
            socket_kind=SocketKind.NORMAL,
        )
'''

INTEG_EDITS = [
    ("replace", '''        - socket_ref_missing_in_index is reported when the DagIndex is empty.
        - socket_ref_missing_in_index_name is also reported for name buckets.
''', '''        - A SocketRef added by hand (compiled blueprints record none) that is missing
          from an empty built DagIndex reports socket_ref_missing_in_index.
        - socket_ref_missing_in_index_name is also reported for name buckets.
'''),
    ("replace", '''        path_registry = root_blueprint.path_registry
        root_blueprint._dag_index = DagIndex(path_registry=path_registry)
''', "        path_registry = root_blueprint.path_registry\n" + HAND_REF + '''        root_blueprint.add_socket_ref(socket)
        root_blueprint._dag_index = DagIndex(path_registry=path_registry)
'''),
    ("replace", '''        - socket_ref_duplicate is reported when a socket ref is duplicated.
''', '''        - socket_ref_duplicate is reported when a socket ref is duplicated (added by
          hand: compiled blueprints record none).
'''),
    ("replace", '''        socket = root_blueprint.socket_refs[0]
        root_blueprint.add_socket_ref(socket)
''', "        path_registry = root_blueprint.path_registry\n" + HAND_REF + '''        root_blueprint.add_socket_ref(socket)
        root_blueprint.add_socket_ref(socket)
'''),
]

EDITS = {
    UNIT: UNIT_EDITS,
    ROOTS: ROOTS_EDITS,
    ADJ: ADJ_EDITS,
    CONTRACTS: CONTRACTS_EDITS,
    SYSTEM: SYSTEM_EDITS,
    PHASE5: PHASE5_EDITS,
    TARGETING: TARGETING_EDITS,
    MELD: MELD_EDITS,
    REQUIRED: REQUIRED_EDITS,
    INTEG: INTEG_EDITS,
}


def main() -> None:
    """Check every anchor, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        data = path.read_bytes().decode("utf-8")
        for edit in edits:
            data = _apply_one(data, edit, rel)
        compile(data, rel, "exec")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
