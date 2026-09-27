import pytest
from typing import Dict, Iterable, List, Optional, Set, Tuple

from melder.aether.spellbook.spell_compiler.system.spell_system_root_blueprint_builder import (
    SpellSystemRootBlueprintBuilder,
)
from melder.aether.spellbook.spell_compiler.system.spell_system_adjacency_snapshot import (
    SpellSystemAdjacencySnapshot,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind


def _old_dependency_edges(
    ordered_reachable_ids: List[str],
    dependencies: Dict[str, Set[str]],
    reachable_ids: Set[str],
) -> List[Tuple[str, str, Optional[str], Optional[SocketKind]]]:
    """
    Purpose:
        Reproduce the pre-refactor dependency-edge materialization logic.

    Contract:
        - Preserves the original nested-loop order exactly.
        - Uses the same provider filtering semantics as the old inline
          generator expression.

    Args:
        ordered_reachable_ids:
            Sorted reachable node ids used by the builder before edge emission.
        dependencies:
            Full adjacency mapping from consumer -> providers.
        reachable_ids:
            Reachable-node membership filter for the current root subgraph.

    Returns:
        List[Tuple[str, str, Optional[str], Optional[SocketKind]]]:
            The provider -> consumer edge tuples produced by the old generator
            logic.
    """
    return list(
        (
            (provider_id, consumer_id, None, None)
            for consumer_id in ordered_reachable_ids
            for provider_id in sorted(dependencies.get(consumer_id) or ())
            if provider_id in reachable_ids
        )
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
    with pytest.raises(AttributeError):
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
    assert captured and captured[0]._cleaned is False  # noqa: SLF001


def test_compiled_blueprint_mints_no_paths():
    """Phase 5 keeps the dependency DAG and mints no path, whatever the topologies hold."""
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

    assert set(blueprint.dag.nodes) == {"root", "child", "leaf"}
    assert blueprint.path_registry.resolve_path_id(("child",)) is None


def test_multiple_roots_returned():
    deps = {"r1": set(), "r2": set()}
    snapshot = _snapshot(deps, roots={"r1", "r2"})
    result = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
    assert set(result) == {"r1", "r2"}
    assert list(result.keys()) == ["r1", "r2"]


def test_build_single_root_dag_handles_isolated_root():
    dag, ordered = SpellSystemRootBlueprintBuilder()._build_single_root_dag("root", {"root": set()})
    assert set(dag.nodes) == {"root"}
    assert ordered == ["root"]


def test_build_single_root_dag_validates_inputs():
    builder = SpellSystemRootBlueprintBuilder()
    with pytest.raises(ValueError):
        builder._build_single_root_dag(None, {})  # type: ignore[arg-type]
    with pytest.raises(AttributeError):
        builder._build_single_root_dag("root", None)  # type: ignore[arg-type]


def test_build_single_root_dag_topology_order_stable():
    deps = {"root": {"b", "a"}, "a": set(), "b": set()}
    dag, ordered = SpellSystemRootBlueprintBuilder()._build_single_root_dag("root", deps)
    assert ordered == ["a", "b", "root"]


@pytest.mark.parametrize(
    ("root_spell_id", "dependencies", "allowed_spell_ids"),
    [
        (
            "root",
            {"root": {"mid_b", "mid_a"}, "mid_a": {"leaf"}, "mid_b": set(), "leaf": set()},
            None,
        ),
        (
            "root",
            {
                "root": {"mid", "blocked"},
                "mid": {"leaf"},
                "leaf": set(),
                "blocked": {"ghost"},
            },
            {"root", "mid", "leaf"},
        ),
        (
            "root",
            {"root": {"shared"}, "shared": set(), "orphan": {"ghost"}, "ghost": set()},
            None,
        ),
        (
            "solo",
            {"solo": set()},
            None,
        ),
    ],
)
def test_build_single_root_dag_materializes_same_edges_as_old_generator(
    monkeypatch,
    root_spell_id: str,
    dependencies: Dict[str, Set[str]],
    allowed_spell_ids: Optional[Set[str]],
) -> None:
    captured_edges: List[Tuple[str, str, Optional[str], Optional[SocketKind]]] = []
    original = DirectedAcyclicWorkGraph.add_dependencies_bulk

    def _capture_edges(
        self: DirectedAcyclicWorkGraph,
        edges: Iterable[Tuple[str, str, Optional[str], Optional[SocketKind]]],
    ) -> None:
        materialized_edges = list(edges)
        captured_edges[:] = materialized_edges
        original(self, materialized_edges)

    monkeypatch.setattr(
        DirectedAcyclicWorkGraph,
        "add_dependencies_bulk",
        _capture_edges,
    )

    dag, _ = SpellSystemRootBlueprintBuilder()._build_single_root_dag(
        root_spell_id,
        dependencies,
        allowed_spell_ids=allowed_spell_ids,
    )

    reachable_ids = set(dag.nodes.keys())
    expected_edges = _old_dependency_edges(
        sorted(reachable_ids),
        dependencies,
        reachable_ids,
    )

    assert captured_edges == expected_edges


def test_build_root_blueprints_handles_unknown_root_id():
    deps = {"other": {"x"}, "x": set()}
    snapshot = _snapshot(deps, roots={"missing"})
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["missing"]
    assert list(bp.dag.nodes.keys()) == ["missing"]
    assert bp.ordered_node_ids == ["missing"]


def test_build_blueprint_for_spell_id_builds_non_root_blueprint():
    deps = {"root": {"mid"}, "mid": {"leaf"}, "leaf": set()}
    snapshot = _snapshot(deps, roots={"root"})

    blueprint = SpellSystemRootBlueprintBuilder().build_blueprint_for_spell_id(
        root_spell_id="mid",
        snapshot=snapshot,
    )

    assert blueprint.root_spell_id == "mid"
    assert set(blueprint.dag.nodes.keys()) == {"mid", "leaf"}
    assert blueprint.ordered_node_ids == ["leaf", "mid"]


def test_build_single_root_dag_respects_allowed_spell_ids_filter():
    deps = {"root": {"mid", "blocked"}, "mid": {"leaf"}, "leaf": set(), "blocked": set()}

    dag, ordered = SpellSystemRootBlueprintBuilder()._build_single_root_dag(
        "root",
        deps,
        allowed_spell_ids={"root", "mid", "leaf"},
    )

    assert set(dag.nodes.keys()) == {"root", "mid", "leaf"}
    assert "blocked" not in dag.nodes
    assert ordered == ["leaf", "mid", "root"]


def test_build_root_blueprints_refuses_dependency_cycle():
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


def test_build_single_root_dag_skips_revisiting_reachable_ids():
    deps = {"root": ["a", "a"], "a": set()}

    dag, ordered = SpellSystemRootBlueprintBuilder()._build_single_root_dag(
        "root",
        deps,
    )

    assert set(dag.nodes.keys()) == {"root", "a"}
    assert ordered == ["a", "root"]


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


def test_shared_binary_chain_builds_without_walking_paths():
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
    assert bp.path_registry.resolve_path_id(("a",)) is None


def test_build_root_blueprints_leaves_topologies_map_intact():
    deps = {"root": set()}
    topologies = {"root": SpellLocalTopology(spell_id="root", sockets=())}
    snapshot = _snapshot(deps, roots={"root"}, topologies=topologies)
    SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
    assert topologies == {"root": topologies["root"]}


def test_multiple_roots_with_shared_dependency_produce_separate_blueprints():
    deps = {"r1": {"x"}, "r2": {"x"}, "x": set()}
    snapshot = _snapshot(deps, roots={"r1", "r2"})
    result = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)
    assert set(result.keys()) == {"r1", "r2"}
    for bp in result.values():
        assert "x" in bp.dag.nodes


def test_build_root_blueprints_accepts_empty_topologies():
    deps = {"root": {"child"}, "child": set()}
    snapshot = _snapshot(deps, roots={"root"}, topologies={})
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    assert set(bp.dag.nodes) == {"root", "child"}


def test_build_root_blueprints_respects_unreachable_dependencies():
    deps = {"root": set(), "lonely": {"x"}, "x": set()}
    snapshot = _snapshot(deps, roots={"root"})
    bp = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    assert set(bp.dag.nodes) == {"root"}


