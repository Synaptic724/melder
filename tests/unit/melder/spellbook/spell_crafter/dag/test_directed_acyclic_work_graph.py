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
    # nodes cleaned as well
    assert dag.get_node("a") is None


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
