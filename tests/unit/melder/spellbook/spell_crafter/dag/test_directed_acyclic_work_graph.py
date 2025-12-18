import pytest

from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


def test_add_node_and_dependency_builds_graph():
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("a", "b", param_name="p", socket_kind=SocketKind.NORMAL)
    assert "a" in dag.nodes and "b" in dag.nodes
    assert dag.nodes["b"].dependencies[0].id == "a"
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

