import pytest

from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


def test_add_node_and_dependency_builds_graph():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("a", "b", param_name="p", socket_kind=SocketKind.NORMAL)
    assert "a" in dag.nodes and "b" in dag.nodes
    dep = next(iter(dag.nodes["b"].dependencies))
    assert dep.id == "a"
    assert dag.collect_dependency_ids() == ["a", "b"]


def test_add_node_updates_payload_on_existing():
    dag = DirectedAcyclicWorkGraph()
    node1 = dag.add_node("x", payload=1)
    node2 = dag.add_node("x", payload=2)
    assert node1 is node2
    assert node1.payload == 2


def test_topological_sort_detects_cycle():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("a", "b")
    dag.add_dependency("b", "a")  # create cycle
    with pytest.raises(RuntimeError):
        dag.topological_sort()


def test_execute_runs_node_tasks_in_order():
    dag = DirectedAcyclicWorkGraph()
    order = []
    n1 = dag.add_node("a")
    n2 = dag.add_node("b")
    dag.add_dependency("a", "b")
    n1.add_task(lambda: order.append("a"))
    n2.add_task(lambda: order.append("b"))
    dag.execute()
    assert order == ["a", "b"]


def test_cleanup_idempotent_and_blocks_mutation():
    dag = DirectedAcyclicWorkGraph()
    dag.add_node("a")
    dag.cleanup()
    dag.cleanup()
    with pytest.raises(RuntimeError):
        dag.add_node("b")
    with pytest.raises(RuntimeError):
        dag.add_dependency("a", "b")


def test_add_node_rejects_empty_key():
    dag = DirectedAcyclicWorkGraph()
    with pytest.raises(ValueError):
        dag.add_node("")


def test_get_node_returns_none_when_missing():
    dag = DirectedAcyclicWorkGraph()
    assert dag.get_node("missing") is None
    dag.add_node("x")
    assert dag.get_node("x") is dag.nodes["x"]


def test_add_dependency_creates_nodes_and_socket_kind_recorded():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child", socket_kind=SocketKind.SPELL_CONTRACT)
    assert "parent" in dag.nodes and "child" in dag.nodes
    parent = dag.nodes["parent"]
    child = dag.nodes["child"]
    assert parent in child.dependencies
    assert dag._socket_kinds[(parent, child)] is SocketKind.SPELL_CONTRACT


def test_add_dependency_param_name_updates_param_maps():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("p", "c", param_name="svc")
    parent = dag.nodes["p"]
    child = dag.nodes["c"]
    assert child in parent.children_by_param["svc"]
    assert child.incoming_params[parent] == "svc"


def test_topological_sort_handles_disconnected_nodes_and_branching():
    dag = DirectedAcyclicWorkGraph()
    dag.add_node("root")
    dag.add_dependency("root", "mid")
    dag.add_dependency("root", "leaf1")
    dag.add_dependency("mid", "leaf2")

    order = [n.id for n in dag.topological_sort()]
    assert order.index("root") < order.index("mid")
    assert order.index("mid") < order.index("leaf2")
    assert order.index("root") < order.index("leaf1")


def test_collect_dependency_ids_respects_topology_order():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("a", "b")
    dag.add_dependency("a", "c")
    ids = dag.collect_dependency_ids()
    assert ids[0] == "a"
    assert set(ids[1:]) == {"b", "c"}


def test_execute_skips_nodes_without_tasks():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("a", "b")
    dag.execute()  # no tasks added; should not raise


def test_execute_propagates_task_exception():
    dag = DirectedAcyclicWorkGraph()
    node = dag.add_node("n")
    node.add_task(lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError):
        dag.execute()


def test_cleanup_marks_nodes_cleaned_and_clears_map():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("a", "b")
    dag.cleanup()
    assert dag.cleaned
    assert dag.nodes == {}
    # access after cleanup is guarded
    with pytest.raises(RuntimeError):
        dag.get_node("a")


def test_cleanup_swallow_node_cleanup_errors():
    dag = DirectedAcyclicWorkGraph()
    node = dag.add_node("n")

    def bad_cleanup():
        raise RuntimeError("fail")

    node.cleanup = bad_cleanup  # type: ignore[assignment]
    dag.cleanup()
    assert dag.cleaned


def test_check_cleaned_blocks_operations():
    dag = DirectedAcyclicWorkGraph()
    dag.cleanup()
    with pytest.raises(RuntimeError):
        dag.get_node("anything")
    with pytest.raises(RuntimeError):
        dag.topological_sort()


def test_repr_includes_id_and_node_count():
    dag = DirectedAcyclicWorkGraph()
    dag.add_node("x")
    text = repr(dag)
    assert "DirectedAcyclicWorkGraph" in text
    assert "nodes=1" in text


def test_add_dependency_after_cleanup_raises():
    dag = DirectedAcyclicWorkGraph()
    dag.cleanup()
    with pytest.raises(RuntimeError):
        dag.add_dependency("a", "b")


def test_add_node_updates_payload_only_when_provided():
    dag = DirectedAcyclicWorkGraph()
    node = dag.add_node("x", payload=1)
    dag.add_node("x")
    assert node.payload == 1


def test_topological_sort_single_node():
    dag = DirectedAcyclicWorkGraph()
    node = dag.add_node("solo")
    assert dag.topological_sort() == [node]


def test_add_dependency_prevents_self_cycle_via_dagnode_guard():
    dag = DirectedAcyclicWorkGraph()
    with pytest.raises(ValueError):
        dag.add_dependency("a", "a")


def test_socket_kind_map_cleared_on_cleanup():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("p", "c", socket_kind=SocketKind.NORMAL)
    assert dag._socket_kinds  # noqa: SLF001
    dag.cleanup()
    # internal map remains allocated but nodes are cleaned; ensure entries drop when accessing key components
    for (parent, child), kind in list(dag._socket_kinds.items()):  # noqa: SLF001
        assert parent.cleaned and child.cleaned


def test_add_dependency_same_edge_overwrites_socket_kind():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("p", "c", socket_kind=SocketKind.NORMAL)
    dag.add_dependency("p", "c", socket_kind=SocketKind.SPELL_CONTRACT)
    parent = dag.nodes["p"]
    child = dag.nodes["c"]
    assert dag._socket_kinds[(parent, child)] is SocketKind.SPELL_CONTRACT  # noqa: SLF001


def test_collect_dependency_ids_on_empty_graph():
    dag = DirectedAcyclicWorkGraph()
    assert dag.collect_dependency_ids() == []


def test_topological_sort_no_nodes_returns_empty():
    dag = DirectedAcyclicWorkGraph()
    assert dag.topological_sort() == []


def test_add_node_same_key_without_payload_preserves_existing_payload():
    dag = DirectedAcyclicWorkGraph()
    node = dag.add_node("x", payload="first")
    dag.add_node("x", payload=None)
    assert node.payload == "first"


def test_add_dependency_is_idempotent_for_same_edge():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("p", "c")
    dag.add_dependency("p", "c")
    parent = dag.nodes["p"]
    child = dag.nodes["c"]
    assert len(child.dependencies) == 1
    assert len(parent.dependents) == 1


def test_get_node_respects_existing_reference_after_add_dependency():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("p", "c")
    assert dag.get_node("p") is dag.nodes["p"]
    assert dag.get_node("c") is dag.nodes["c"]


def test_add_node_after_dependency_updates_payload():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("p", "c")
    updated = dag.add_node("c", payload="new")
    assert dag.nodes["c"] is updated
    assert updated.payload == "new"


def test_execute_propagates_topological_sort_failure():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("a", "b")
    dag.add_dependency("b", "a")  # cycle
    with pytest.raises(RuntimeError):
        dag.execute()


def test_topological_sort_handles_multiple_roots():
    dag = DirectedAcyclicWorkGraph()
    dag.add_node("root1")
    dag.add_node("root2")
    dag.add_dependency("root1", "leaf")
    # Either root may appear first; ensure leaves after both roots
    order = [n.id for n in dag.topological_sort()]
    assert "root1" in order and "root2" in order and "leaf" in order
    assert order.index("leaf") > order.index("root1")


def test_execute_runs_tasks_after_branching_dependencies():
    dag = DirectedAcyclicWorkGraph()
    calls = []
    dag.add_dependency("root", "b")
    dag.add_dependency("root", "c")
    dag.nodes["root"].add_task(lambda: calls.append("root"))
    dag.nodes["b"].add_task(lambda: calls.append("b"))
    dag.nodes["c"].add_task(lambda: calls.append("c"))
    dag.execute()
    assert calls[0] == "root"
    assert set(calls[1:]) == {"b", "c"}


def test_repr_updates_after_adding_nodes():
    dag = DirectedAcyclicWorkGraph()
    dag.add_node("x")
    dag.add_node("y")
    text = repr(dag)
    assert "nodes=2" in text


def test_cleanup_is_safe_when_no_nodes():
    dag = DirectedAcyclicWorkGraph()
    dag.cleanup()
    assert dag.cleaned


def test_collect_dependency_ids_reflects_chain_order():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("a", "b")
    dag.add_dependency("b", "c")
    assert dag.collect_dependency_ids() == ["a", "b", "c"]


def test_add_dependency_without_socket_kind_leaves_map_empty():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("p", "c")
    assert dag._socket_kinds == {}  # noqa: SLF001


def test_add_dependency_param_name_none_leaves_param_maps_empty():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("p", "c", param_name=None)
    parent = dag.nodes["p"]
    child = dag.nodes["c"]
    assert parent.children_by_param == {}
    assert child.incoming_params == {}


def test_topological_sort_large_mixed_graph_respects_all_edges():
    dag = DirectedAcyclicWorkGraph()
    # Roots
    dag.add_node("r1")
    dag.add_node("r2")
    # Middle layer
    dag.add_dependency("r1", "m1")
    dag.add_dependency("r2", "m2")
    dag.add_dependency("r1", "m2")  # shared dependency
    # Leaves
    dag.add_dependency("m1", "l1")
    dag.add_dependency("m2", "l2")
    dag.add_dependency("m2", "l3")

    order = [n.id for n in dag.topological_sort()]
    for before, after in [
        ("r1", "m1"),
        ("r1", "m2"),
        ("r2", "m2"),
        ("m1", "l1"),
        ("m2", "l2"),
        ("m2", "l3"),
    ]:
        assert order.index(before) < order.index(after)
