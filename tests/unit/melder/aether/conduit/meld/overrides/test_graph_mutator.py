"""Contract tests for GraphMutator mutation override handling."""
from typing import Iterable, Optional
from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.meld.overrides.graph_mutator import GraphMutator
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, SocketRef
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


def _make_socket_ref(
    *,
    node_id: str,
    param_name: str,
    param_path: tuple[str, ...],
    socket_kind: SocketKind = SocketKind.MUTATION_CONTRACT,
) -> SocketRef:
    """
    Build a SocketRef for mutation override targeting.

    Args:
        node_id: Spell id for the socket owner.
        param_name: Parameter name on the target node.
        param_path: Path from the root for override targeting.
        socket_kind: Socket kind classification (mutation by default).

    Returns:
        SocketRef: Socket reference with the provided attributes.
    """
    return SocketRef(
        node_id=node_id,
        param_name=param_name,
        param_path=param_path,
        socket_kind=socket_kind,
    )


def _build_dag(
    *,
    edges: Iterable[tuple[str, str, Optional[str], Optional[SocketKind]]],
    node_ids: Optional[Iterable[str]] = None,
) -> DirectedAcyclicWorkGraph:
    """
    Build a DirectedAcyclicWorkGraph with explicit nodes and edges.

    Args:
        edges: Iterable of (parent_id, child_id, param_name, socket_kind).
        node_ids: Optional iterable of standalone node ids to include.

    Returns:
        DirectedAcyclicWorkGraph: DAG containing the requested nodes and edges.
    """
    dag = DirectedAcyclicWorkGraph()
    for node_id in node_ids or []:
        dag.add_node(node_id)
    for parent_id, child_id, param_name, socket_kind in edges:
        dag.add_dependency(
            parent_key=parent_id,
            child_key=child_id,
            param_name=param_name,
            socket_kind=socket_kind,
        )
    return dag


def _make_blueprint(
    *,
    root_id: str,
    root_lineage_id: str,
    edges: Iterable[tuple[str, str, Optional[str], Optional[SocketKind]]],
    socket_refs: Iterable[SocketRef],
    node_ids: Optional[Iterable[str]] = None,
) -> RootResolutionBlueprint:
    """
    Build a RootResolutionBlueprint with a DAG and socket index.

    Args:
        root_id: Root spell id for the blueprint.
        root_lineage_id: Root lineage id for identity checks.
        edges: Iterable of DAG edges to add.
        socket_refs: SocketRefs to index in the blueprint.
        node_ids: Optional standalone node ids to include.

    Returns:
        RootResolutionBlueprint: Blueprint ready for GraphMutator.
    """
    dag = _build_dag(edges=edges, node_ids=node_ids)
    ordered_ids = dag.collect_dependency_ids()
    index = DagIndex()
    for ref in socket_refs:
        index.add_socket(ref)
    return RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=root_lineage_id,
        dag=dag,
        ordered_node_ids=ordered_ids,
        socket_refs=list(socket_refs),
        dag_index=index,
    )


def _parent_ids(dag: DirectedAcyclicWorkGraph, child_id: str) -> list[str]:
    """
    Return the sorted parent ids for a given child node.

    Args:
        dag: DAG to inspect.
        child_id: Child node id to inspect.

    Returns:
        list[str]: Sorted list of parent ids.
    """
    child = dag.get_node(child_id)
    if child is None:
        return []
    return sorted(parent.id for parent in child.dependencies)


def _incoming_param(
    dag: DirectedAcyclicWorkGraph,
    *,
    child_id: str,
    parent_id: str,
) -> Optional[str]:
    """
    Lookup the incoming param name for a specific edge.

    Args:
        dag: DAG to inspect.
        child_id: Child node id.
        parent_id: Parent node id.

    Returns:
        Optional[str]: Param name if the edge exists, otherwise None.
    """
    child = dag.get_node(child_id)
    parent = dag.get_node(parent_id)
    if child is None or parent is None:
        return None
    return child.incoming_params.get(parent)


def test_init_requires_blueprint() -> None:
    """
    Verify GraphMutator rejects a None blueprint.

    Contract:
        - blueprint must not be None.
    """
    with pytest.raises(ValueError, match="blueprint must not be None"):
        GraphMutator(None)


def test_cleanup_clears_references_and_is_idempotent() -> None:
    """
    Verify cleanup clears references and can be called repeatedly.

    Contract:
        - cleanup nulls engine and blueprint references.
        - cleanup is idempotent.
    """
    socket_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[("parent", "child", "dep", SocketKind.MUTATION_CONTRACT)],
        socket_refs=[socket_ref],
    )
    mutator = GraphMutator(blueprint)
    engine_mock = MagicMock()
    mutator._engine = engine_mock
    mutator.cleanup()
    engine_mock.cleanup.assert_called_once()
    assert mutator._engine is None
    assert mutator._blueprint is None
    mutator.cleanup()
    assert mutator._engine is None
    assert mutator._blueprint is None


@pytest.mark.parametrize("payload", [None, {}, []])
def test_apply_returns_original_for_empty_override(payload) -> None:
    """
    Verify empty override payloads return the original blueprint.

    Contract:
        - falsy mutation_override returns the same blueprint instance.
    """
    socket_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[("parent", "child", "dep", SocketKind.MUTATION_CONTRACT)],
        socket_refs=[socket_ref],
    )
    mutator = GraphMutator(blueprint)
    assert mutator.apply(payload) is blueprint


def test_apply_rejects_non_dict_override() -> None:
    """
    Verify non-dict overrides are rejected.

    Contract:
        - mutation_override must be a dict when truthy.
    """
    socket_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[("parent", "child", "dep", SocketKind.MUTATION_CONTRACT)],
        socket_refs=[socket_ref],
    )
    mutator = GraphMutator(blueprint)
    with pytest.raises(RuntimeError, match="mutation_override must be a dict"):
        mutator.apply(["not-a-dict"])


def test_apply_rejects_invalid_override_key() -> None:
    """
    Verify invalid override keys are rejected.

    Contract:
        - empty or whitespace keys raise RuntimeError.
    """
    socket_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[("parent", "child", "dep", SocketKind.MUTATION_CONTRACT)],
        socket_refs=[socket_ref],
    )
    mutator = GraphMutator(blueprint)
    with pytest.raises(RuntimeError, match="Invalid mutation_override key"):
        mutator.apply({"   ": "target"})


@pytest.mark.parametrize("target_id", ["", "   ", 123])
def test_apply_rejects_invalid_override_target(target_id) -> None:
    """
    Verify invalid override targets are rejected.

    Contract:
        - non-string or empty target ids raise RuntimeError.
    """
    socket_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[("parent", "child", "dep", SocketKind.MUTATION_CONTRACT)],
        socket_refs=[socket_ref],
    )
    mutator = GraphMutator(blueprint)
    with pytest.raises(RuntimeError, match="Invalid mutation_override target"):
        mutator.apply({"dep": target_id})


def test_apply_rewires_mutation_socket_to_new_target() -> None:
    """
    Verify mutation sockets are rewired to the override target.

    Contract:
        - old parent edge is removed for the mutation param.
        - new parent edge is added for the override target.
    """
    socket_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[("old-parent", "child", "dep", SocketKind.MUTATION_CONTRACT)],
        socket_refs=[socket_ref],
    )
    mutator = GraphMutator(blueprint)
    mutated = mutator.apply({"dep": "new-parent"})
    assert _parent_ids(mutated.dag, "child") == ["new-parent"]
    assert _incoming_param(mutated.dag, child_id="child", parent_id="new-parent") == "dep"


def test_apply_preserves_root_identity() -> None:
    """
    Verify root identity is preserved during mutation.

    Contract:
        - root_spell_id and root_lineage_id remain unchanged.
    """
    socket_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[("old-parent", "child", "dep", SocketKind.MUTATION_CONTRACT)],
        socket_refs=[socket_ref],
    )
    mutator = GraphMutator(blueprint)
    mutated = mutator.apply({"dep": "new-parent"})
    assert mutated.root_spell_id == "child"
    assert mutated.root_lineage_id == "lineage-1"


def test_apply_adds_new_socket_ref_for_target() -> None:
    """
    Verify mutation adds socket refs for new targets.

    Contract:
        - new socket refs include the override target id.
    """
    socket_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[("old-parent", "child", "dep", SocketKind.MUTATION_CONTRACT)],
        socket_refs=[socket_ref],
    )
    mutator = GraphMutator(blueprint)
    mutated = mutator.apply({"dep": "new-parent"})
    mutated_refs = mutated.socket_refs
    assert len(mutated_refs) == 2
    assert any(
        ref.node_id == "new-parent"
        and ref.param_name == "dep"
        and ref.param_path == ("dep",)
        for ref in mutated_refs
    )


def test_apply_preserves_non_mutation_edges() -> None:
    """
    Verify non-mutation edges remain intact after apply.

    Contract:
        - edges with non-mutation socket kinds are preserved.
    """
    mutation_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
        socket_kind=SocketKind.MUTATION_CONTRACT,
    )
    normal_ref = _make_socket_ref(
        node_id="child",
        param_name="other",
        param_path=("other",),
        socket_kind=SocketKind.NORMAL,
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[
            ("old-parent", "child", "dep", SocketKind.MUTATION_CONTRACT),
            ("normal-parent", "child", "other", SocketKind.NORMAL),
        ],
        socket_refs=[mutation_ref, normal_ref],
    )
    mutator = GraphMutator(blueprint)
    mutated = mutator.apply({"dep": "new-parent"})
    assert "normal-parent" in _parent_ids(mutated.dag, "child")
    assert _incoming_param(mutated.dag, child_id="child", parent_id="normal-parent") == "other"


def test_apply_leaves_source_dag_untouched() -> None:
    """
    Verify apply does not mutate the source DAG.

    Contract:
        - source DAG edges remain as originally defined.
    """
    socket_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[("old-parent", "child", "dep", SocketKind.MUTATION_CONTRACT)],
        socket_refs=[socket_ref],
    )
    mutator = GraphMutator(blueprint)
    _ = mutator.apply({"dep": "new-parent"})
    assert _parent_ids(blueprint.dag, "child") == ["old-parent"]


def test_apply_adds_new_node_for_target() -> None:
    """
    Verify override targets are added as nodes in the mutated DAG.

    Contract:
        - override target ids are present in the mutated DAG nodes.
    """
    socket_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[("old-parent", "child", "dep", SocketKind.MUTATION_CONTRACT)],
        socket_refs=[socket_ref],
    )
    mutator = GraphMutator(blueprint)
    mutated = mutator.apply({"dep": "new-parent"})
    assert mutated.dag.get_node("new-parent") is not None


def test_apply_preserves_socket_kind_on_new_edge() -> None:
    """
    Verify the new edge retains the mutation socket kind.

    Contract:
        - new edge in the mutated DAG preserves socket_kind.
    """
    socket_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
        socket_kind=SocketKind.MUTATION_CONTRACT,
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[("old-parent", "child", "dep", SocketKind.MUTATION_CONTRACT)],
        socket_refs=[socket_ref],
    )
    mutator = GraphMutator(blueprint)
    mutated = mutator.apply({"dep": "new-parent"})
    parent_node = mutated.dag.get_node("new-parent")
    child_node = mutated.dag.get_node("child")
    assert mutated.dag._socket_kinds[(parent_node, child_node)] is SocketKind.MUTATION_CONTRACT


def test_apply_orders_new_target_before_child() -> None:
    """
    Verify the mutated blueprint orders the new target before the child.

    Contract:
        - ordered_node_ids contains the new parent before its child.
    """
    socket_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[("old-parent", "child", "dep", SocketKind.MUTATION_CONTRACT)],
        socket_refs=[socket_ref],
    )
    mutator = GraphMutator(blueprint)
    mutated = mutator.apply({"dep": "new-parent"})
    order = mutated.ordered_node_ids
    assert order.index("new-parent") < order.index("child")


def test_apply_skips_nonexistent_child_nodes() -> None:
    """
    Verify missing child nodes do not cause rewiring failures.

    Contract:
        - missing child nodes are ignored without raising.
    """
    socket_ref = _make_socket_ref(
        node_id="missing-child",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        edges=[],
        socket_refs=[socket_ref],
        node_ids=["root"],
    )
    mutator = GraphMutator(blueprint)
    mutated = mutator.apply({"dep": "new-parent"})
    assert mutated.dag.get_node("new-parent") is None


def test_apply_filters_only_mutation_sockets() -> None:
    """
    Verify only mutation sockets are rewired when both kinds exist.

    Contract:
        - normal sockets are ignored by the mutation filter.
    """
    mutation_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
        socket_kind=SocketKind.MUTATION_CONTRACT,
    )
    normal_ref = _make_socket_ref(
        node_id="other-child",
        param_name="dep",
        param_path=("dep",),
        socket_kind=SocketKind.NORMAL,
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[
            ("old-parent", "child", "dep", SocketKind.MUTATION_CONTRACT),
            ("normal-parent", "other-child", "dep", SocketKind.NORMAL),
        ],
        socket_refs=[mutation_ref, normal_ref],
    )
    mutator = GraphMutator(blueprint)
    mutated = mutator.apply({"dep": "new-parent"})
    assert _parent_ids(mutated.dag, "child") == ["new-parent"]
    assert _parent_ids(mutated.dag, "other-child") == ["normal-parent"]


def test_apply_raises_when_no_mutation_socket_matches() -> None:
    """
    Verify overrides that match no mutation sockets raise.

    Contract:
        - DagTargetingEngine raises when no mutation sockets match.
    """
    normal_ref = _make_socket_ref(
        node_id="child",
        param_name="dep",
        param_path=("dep",),
        socket_kind=SocketKind.NORMAL,
    )
    blueprint = _make_blueprint(
        root_id="child",
        root_lineage_id="lineage-1",
        edges=[("parent", "child", "dep", SocketKind.NORMAL)],
        socket_refs=[normal_ref],
    )
    mutator = GraphMutator(blueprint)
    with pytest.raises(RuntimeError, match="No sockets found"):
        mutator.apply({"dep": "new-parent"})


def test_apply_handles_multiple_overrides() -> None:
    """
    Verify multiple overrides are applied in one run.

    Contract:
        - each override rewires its corresponding mutation socket.
    """
    ref_a = _make_socket_ref(
        node_id="child-a",
        param_name="dep",
        param_path=("dep",),
    )
    ref_b = _make_socket_ref(
        node_id="child-b",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="child-a",
        root_lineage_id="lineage-1",
        edges=[
            ("old-a", "child-a", "dep", SocketKind.MUTATION_CONTRACT),
            ("old-b", "child-b", "dep", SocketKind.MUTATION_CONTRACT),
        ],
        socket_refs=[ref_a, ref_b],
    )
    mutator = GraphMutator(blueprint)
    mutated = mutator.apply({"dep": "new-parent"})
    assert _parent_ids(mutated.dag, "child-a") == ["new-parent"]
    assert _parent_ids(mutated.dag, "child-b") == ["new-parent"]
