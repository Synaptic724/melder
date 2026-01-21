import pytest

from melder.spellbook.spell_crafter.system.spell_system_root_blueprint_builder import (
    SpellSystemRootBlueprintBuilder,
)
from melder.spellbook.spell_crafter.system.spell_system_adjacency_snapshot import (
    SpellSystemAdjacencySnapshot,
)
from melder.spellbook.spell_crafter.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)


def _snapshot(
    dependencies: dict[str, set[str]],
    roots: set[str],
    topologies: dict[str, SpellLocalTopology] | None = None,
) -> SpellSystemAdjacencySnapshot:
    reverse: dict[str, set[str]] = {}
    for consumer, providers in dependencies.items():
        for provider in providers:
            reverse.setdefault(provider, set()).add(consumer)
        reverse.setdefault(consumer, reverse.get(consumer, set()))
    all_ids = set(dependencies.keys()) | {p for vals in dependencies.values() for p in vals}
    return SpellSystemAdjacencySnapshot(
        dependencies=dependencies,
        reverse_dependencies=reverse,
        all_spell_ids=all_ids,
        root_spell_ids=set(roots),
        topologies=topologies or {},
    )


def test_build_root_blueprints_requires_snapshot():
    builder = SpellSystemRootBlueprintBuilder()
    with pytest.raises(ValueError):
        builder.build_root_blueprints(None)  # type: ignore[arg-type]


def test_build_root_blueprints_empty_roots_returns_empty():
    snapshot = _snapshot(dependencies={}, roots=set())
    assert SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot) == {}


def test_build_single_root_dag_discovers_reachable_nodes():
    deps = {
        "root": {"mid"},
        "mid": {"leaf"},
        "leaf": set(),
        "extra": {"orphan"},
        "orphan": set(),
    }
    builder = SpellSystemRootBlueprintBuilder()
    dag, ordered = builder._build_single_root_dag("root", deps)

    assert set(dag.nodes) == {"root", "mid", "leaf"}
    root_node = dag.get_node("root")
    mid_node = dag.get_node("mid")
    leaf_node = dag.get_node("leaf")
    assert mid_node in root_node.dependencies
    assert leaf_node in mid_node.dependencies
    # ensure topological order has leaf before mid before root
    idx = {node_id: i for i, node_id in enumerate(ordered)}
    assert idx["leaf"] < idx["mid"] < idx["root"]


def test_build_single_root_dag_cleans_on_cycle(monkeypatch):
    captured: list[DirectedAcyclicWorkGraph] = []

    def boom(self):
        captured.append(self)
        raise RuntimeError("cycle")

    monkeypatch.setattr(DirectedAcyclicWorkGraph, "collect_dependency_ids", boom)
    builder = SpellSystemRootBlueprintBuilder()
    with pytest.raises(RuntimeError):
        builder._build_single_root_dag("r", {"r": set()})
    assert captured and captured[0]._cleaned is True  # noqa: SLF001


def test_overlay_sockets_and_index_builds_paths():
    deps = {"root": {"child"}, "child": {"leaf"}, "leaf": set()}
    root_top = SpellLocalTopology(
        spell_id="root",
        sockets=(
            SpellSocketDescriptor(
                spell_id="root",
                param_name="child",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=False,
                target_spell_ids=("child",),
            ),
        ),
    )
    child_top = SpellLocalTopology(
        spell_id="child",
        sockets=(
            SpellSocketDescriptor(
                spell_id="child",
                param_name="leaf",
                position=0,
                socket_kind=SocketKind.NORMAL,
                is_collection=False,
                is_optional=True,
                target_spell_ids=("leaf",),
            ),
        ),
    )
    snapshot = _snapshot(deps, roots={"root"}, topologies={"root": root_top, "child": child_top})
    blueprint = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]

    sockets = blueprint.socket_refs
    assert {s.param_path for s in sockets} == {("child",), ("child", "leaf")}

    root_socket = blueprint.dag_index.get_by_exact_path(("child",))[0]
    child_socket = blueprint.dag_index.get_by_exact_path(("child", "leaf"))[0]
    assert root_socket.node_id == "root" and root_socket.param_name == "child"
    assert child_socket.node_id == "child" and child_socket.param_name == "leaf"


def test_overlay_sockets_no_topologies_results_in_empty_index():
    deps = {"root": {"child"}, "child": set()}
    snapshot = _snapshot(deps, roots={"root"}, topologies={})
    blueprint = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    assert list(blueprint.dag_index.iter_all_sockets()) == []
    assert blueprint.socket_refs == []


def test_multiple_roots_returned():
    deps = {"r1": set(), "r2": set()}
    snapshot = _snapshot(deps, roots={"r1", "r2"})
    result = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
    assert set(result) == {"r1", "r2"}


def test_overlay_sockets_and_index_rejects_none():
    builder = SpellSystemRootBlueprintBuilder()
    dag = DirectedAcyclicWorkGraph()
    bp = RootResolutionBlueprint("r", None, dag)
    with pytest.raises(ValueError):
        builder._overlay_sockets_and_index(None, {})  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        builder._overlay_sockets_and_index(bp, None)  # type: ignore[arg-type]


def test_build_single_root_dag_handles_isolated_root():
    dag, ordered = SpellSystemRootBlueprintBuilder()._build_single_root_dag("root", {"root": set()})
    assert set(dag.nodes) == {"root"}
    assert ordered == ["root"]


def test_overlay_walks_branching_paths():
    deps = {"root": {"a", "b"}, "a": set(), "b": set()}
    topo = SpellLocalTopology(
        spell_id="root",
        sockets=(
            SpellSocketDescriptor("root", "a", 0, SocketKind.NORMAL, False, False, ("a",)),
            SpellSocketDescriptor("root", "b", 1, SocketKind.NORMAL, False, False, ("b",)),
        ),
    )
    snapshot = _snapshot(deps, roots={"root"}, topologies={"root": topo})
    blueprint = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    assert {s.param_name for s in blueprint.socket_refs} == {"a", "b"}
    by_name_a = blueprint.dag_index.get_by_name("a")
    by_name_b = blueprint.dag_index.get_by_name("b")
    assert len(by_name_a) == 1 and by_name_a[0].param_path == ("a",)
    assert len(by_name_b) == 1 and by_name_b[0].param_path == ("b",)


def test_build_single_root_dag_validates_inputs():
    builder = SpellSystemRootBlueprintBuilder()
    with pytest.raises(ValueError):
        builder._build_single_root_dag(None, {})  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        builder._build_single_root_dag("root", None)  # type: ignore[arg-type]


def test_build_single_root_dag_topology_order_stable():
    deps = {"root": {"b", "a"}, "a": set(), "b": set()}
    dag, ordered = SpellSystemRootBlueprintBuilder()._build_single_root_dag("root", deps)
    assert ordered[-1] == "root"
    assert set(ordered) == {"root", "a", "b"}


def test_build_root_blueprints_handles_unknown_root_id():
    deps = {"other": {"x"}, "x": set()}
    snapshot = _snapshot(deps, roots={"missing"})
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["missing"]
    assert list(bp.dag.nodes.keys()) == ["missing"]
    assert bp.ordered_node_ids == ["missing"]


def test_overlay_skips_missing_child_topology():
    deps = {"root": {"child"}, "child": {"leaf"}, "leaf": set()}
    root_top = SpellLocalTopology(
        spell_id="root",
        sockets=(
            SpellSocketDescriptor("root", "child", 0, SocketKind.NORMAL, False, False, ("child",)),
        ),
    )
    snapshot = _snapshot(deps, roots={"root"}, topologies={"root": root_top})
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    assert {s.param_name for s in bp.socket_refs} == {"child"}
    assert bp.dag_index.get_by_exact_path(("child",))[0].node_id == "root"


def test_overlay_handles_cycle_in_topology_without_infinite_loop():
    topo_root = SpellLocalTopology(
        spell_id="root",
        sockets=(SpellSocketDescriptor("root", "child", 0, SocketKind.NORMAL, False, False, ("child",)),),
    )
    topo_child = SpellLocalTopology(
        spell_id="child",
        sockets=(SpellSocketDescriptor("child", "root", 0, SocketKind.NORMAL, False, False, ("root",)),),
    )
    deps = {"root": {"child"}, "child": {"root"}}
    snapshot = _snapshot(deps, roots={"root"}, topologies={"root": topo_root, "child": topo_child})
    with pytest.raises(RuntimeError):
        SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)


def test_overlay_preserves_socket_kind():
    topo = SpellLocalTopology(
        spell_id="root",
        sockets=(
            SpellSocketDescriptor("root", "k", 0, SocketKind.NORMAL, True, True, ("kid",)),
        ),
    )
    deps = {"root": {"kid"}, "kid": set()}
    snapshot = _snapshot(deps, roots={"root"}, topologies={"root": topo})
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    assert bp.socket_refs[0].socket_kind is SocketKind.NORMAL


def test_overlay_allows_multiple_sockets_same_path():
    # Two sockets pointing at the same param_path should both be retained and indexed.
    topo = SpellLocalTopology(
        spell_id="root",
        sockets=(
            SpellSocketDescriptor("root", "shared", 0, SocketKind.NORMAL, False, False, ()),
            SpellSocketDescriptor("root", "shared", 1, SocketKind.NORMAL, False, False, ()),
        ),
    )
    deps = {"root": {"child"}, "child": set()}
    snapshot = _snapshot(deps, roots={"root"}, topologies={"root": topo})
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    shared_refs = [s for s in bp.socket_refs if s.param_path == ("shared",)]
    assert len(shared_refs) == 2
    assert {s.param_name for s in shared_refs} == {"shared"}


def test_dependency_without_topology_still_in_dag():
    deps = {"root": {"mid"}, "mid": {"leaf"}, "leaf": set()}
    topo_root = SpellLocalTopology(
        spell_id="root",
        sockets=(SpellSocketDescriptor("root", "mid", 0, SocketKind.NORMAL, False, False, ("mid",)),),
    )
    # No topology for 'mid' or 'leaf'; they should still appear as nodes in the DAG.
    snapshot = _snapshot(deps, roots={"root"}, topologies={"root": topo_root})
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    assert set(bp.dag.nodes.keys()) == {"root", "mid", "leaf"}
    # Only the socket from root->mid is recorded; no refs for deeper missing topology.
    assert {r.param_path for r in bp.socket_refs} == {("mid",)}


def test_overlay_stops_on_missing_topology_paths():
    deps = {"root": {"mid"}, "mid": {"leaf"}, "leaf": set()}
    topo = SpellLocalTopology(
        spell_id="root",
        sockets=(SpellSocketDescriptor("root", "mid", 0, SocketKind.NORMAL, False, False, ("mid",)),),
    )
    snapshot = _snapshot(deps, roots={"root"}, topologies={"root": topo})
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    assert {s.param_path for s in bp.socket_refs} == {("mid",)}


def test_overlay_handles_shared_target_under_different_paths():
    deps = {"root": {"a", "b"}, "a": {"leaf"}, "b": {"leaf"}, "leaf": set()}
    topo_root = SpellLocalTopology(
        spell_id="root",
        sockets=(
            SpellSocketDescriptor("root", "a", 0, SocketKind.NORMAL, False, False, ("a",)),
            SpellSocketDescriptor("root", "b", 1, SocketKind.NORMAL, False, False, ("b",)),
        ),
    )
    topo_child = SpellLocalTopology(
        spell_id="a",
        sockets=(SpellSocketDescriptor("a", "leaf", 0, SocketKind.NORMAL, False, False, ("leaf",)),),
    )
    topo_child_b = SpellLocalTopology(
        spell_id="b",
        sockets=(SpellSocketDescriptor("b", "leaf", 0, SocketKind.NORMAL, False, False, ("leaf",)),),
    )
    snapshot = _snapshot(
        deps,
        roots={"root"},
        topologies={"root": topo_root, "a": topo_child, "b": topo_child_b},
    )
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    paths = {s.param_path for s in bp.socket_refs if s.param_name == "leaf"}
    assert paths == {("a", "leaf"), ("b", "leaf")}


def test_overlay_leaves_topologies_map_intact():
    deps = {"root": set()}
    topologies = {"root": SpellLocalTopology(spell_id="root", sockets=())}
    snapshot = _snapshot(deps, roots={"root"}, topologies=topologies)
    SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
    assert topologies == {"root": topologies["root"]}


def test_overlay_no_topology_means_no_socket_refs_even_if_dependencies():
    deps = {"root": {"child"}, "child": set()}
    snapshot = _snapshot(deps, roots={"root"})
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    assert bp.socket_refs == []


def test_multiple_roots_with_shared_dependency_produce_separate_blueprints():
    deps = {"r1": {"x"}, "r2": {"x"}, "x": set()}
    snapshot = _snapshot(deps, roots={"r1", "r2"})
    result = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
    assert set(result.keys()) == {"r1", "r2"}
    for bp in result.values():
        assert "x" in bp.dag.nodes


def test_overlay_accepts_empty_topologies_and_non_empty_deps():
    deps = {"root": {"child"}, "child": set()}
    snapshot = _snapshot(deps, roots={"root"}, topologies={})
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    assert bp.dag_index.get_by_name("child") == []


def test_build_root_blueprints_respects_unreachable_dependencies():
    deps = {"root": set(), "lonely": {"x"}, "x": set()}
    snapshot = _snapshot(deps, roots={"root"})
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    assert set(bp.dag.nodes) == {"root"}


def test_overlay_handles_deep_chain_paths():
    deps = {"root": {"a"}, "a": {"b"}, "b": {"c"}, "c": set()}
    topo_root = SpellLocalTopology(
        spell_id="root",
        sockets=(SpellSocketDescriptor("root", "a", 0, SocketKind.NORMAL, False, False, ("a",)),),
    )
    topo_a = SpellLocalTopology(
        spell_id="a",
        sockets=(SpellSocketDescriptor("a", "b", 0, SocketKind.NORMAL, False, False, ("b",)),),
    )
    topo_b = SpellLocalTopology(
        spell_id="b",
        sockets=(SpellSocketDescriptor("b", "c", 0, SocketKind.NORMAL, False, False, ("c",)),),
    )
    snapshot = _snapshot(deps, roots={"root"}, topologies={"root": topo_root, "a": topo_a, "b": topo_b})
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    assert ("a", "b", "c") in {s.param_path for s in bp.socket_refs}


def test_overlay_idempotent_call_replaces_index():
    deps = {"root": set()}
    topo = SpellLocalTopology(spell_id="root", sockets=())
    snapshot = _snapshot(deps, roots={"root"}, topologies={"root": topo})
    builder = SpellSystemRootBlueprintBuilder()
    bp = builder.build_root_blueprints(snapshot)["root"]
    old_index = bp.dag_index
    builder._overlay_sockets_and_index(bp, snapshot.topologies)
    assert bp.dag_index is not old_index
