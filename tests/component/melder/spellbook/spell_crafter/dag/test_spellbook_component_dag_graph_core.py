import threading

import pytest

from melder.spellbook.spell_crafter.dag.dag_node import DagNode
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)


def test_component_dag_add_node_reuses_existing_and_updates_payload() -> None:
    """
    Purpose:
        Validate add_node reuses existing nodes and updates payloads.
    Contract:
        - Re-adding a node returns the same instance.
        - Payload is updated only when a new payload is provided.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    node = dag.add_node("root", payload="alpha")
    same = dag.add_node("root")
    assert same is node
    assert same.payload == "alpha"

    updated = dag.add_node("root", payload="beta")
    assert updated is node
    assert updated.payload == "beta"


def test_component_dag_topological_sort_orders_dependencies() -> None:
    """
    Purpose:
        Validate topological ordering respects dependency edges.
    Contract:
        - Parents appear before dependents in the sorted order.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency(parent_key="base", child_key="mid")
    dag.add_dependency(parent_key="mid", child_key="leaf")
    dag.add_node("solo")

    order = [node.id for node in dag.topological_sort()]
    assert order.index("base") < order.index("mid") < order.index("leaf")


def test_component_dag_collect_dependency_ids_matches_topological_order() -> None:
    """
    Purpose:
        Validate collect_dependency_ids mirrors topological order output.
    Contract:
        - Returned ids appear in dependency-safe order.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency(parent_key="a", child_key="b")
    dag.add_dependency(parent_key="b", child_key="c")
    dag.add_node("solo")

    ids = dag.collect_dependency_ids()
    assert ids.index("a") < ids.index("b") < ids.index("c")


def test_component_dag_execute_propagates_task_errors() -> None:
    """
    Purpose:
        Validate DAG execution propagates task exceptions.
    Contract:
        - Exceptions raised by tasks bubble to the caller.
        - Dependency tasks run before their dependents.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency(parent_key="dep", child_key="root")
    dep = dag.get_node("dep")
    root = dag.get_node("root")
    assert dep is not None
    assert root is not None

    order: list[str] = []

    def dep_task() -> None:
        order.append("dep")

    def root_task() -> None:
        order.append("root")
        raise RuntimeError("boom")

    dep.add_task(dep_task)
    root.add_task(root_task)

    with pytest.raises(RuntimeError):
        dag.execute()

    assert order == ["dep", "root"]


def test_component_dag_topological_sort_detects_cycles() -> None:
    """
    Purpose:
        Validate cycle detection prevents invalid topological ordering.
    Contract:
        - Cyclic graphs raise RuntimeError during sorting.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency(parent_key="a", child_key="b")
    dag.add_dependency(parent_key="b", child_key="a")

    with pytest.raises(RuntimeError):
        dag.topological_sort()


def test_component_dag_dependency_param_metadata_roundtrip() -> None:
    """
    Purpose:
        Validate param metadata is recorded on dependency edges.
    Contract:
        - child.incoming_params maps parent to the param name.
        - parent.children_by_param maps param name to child.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency(parent_key="service", child_key="root", param_name="service")

    parent = dag.get_node("service")
    child = dag.get_node("root")
    assert parent is not None
    assert child is not None

    assert child.incoming_params[parent] == "service"
    assert child in parent.children_by_param["service"]


def test_component_dag_records_socket_kind_for_edge() -> None:
    """
    Purpose:
        Validate socket kind metadata is recorded on DAG edges.
    Contract:
        - The edge is recorded in the socket-kinds map.
    Returns:
        None.
    """
    from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind

    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency(
        parent_key="service",
        child_key="root",
        socket_kind=SocketKind.SPELL_CONTRACT,
    )

    parent = dag.get_node("service")
    child = dag.get_node("root")
    assert parent is not None
    assert child is not None
    assert dag._socket_kinds[(parent, child)] is SocketKind.SPELL_CONTRACT


def test_component_dag_cleanup_cleans_nodes() -> None:
    """
    Purpose:
        Validate DAG cleanup cascades to nodes.
    Contract:
        - Nodes are marked cleaned after DAG cleanup.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency(parent_key="dep", child_key="root")
    root = dag.get_node("root")
    dep = dag.get_node("dep")
    assert root is not None
    assert dep is not None

    dag.cleanup()

    assert dag.cleaned is True
    assert root.cleaned is True
    assert dep.cleaned is True


def test_component_dag_rejects_empty_node_key() -> None:
    """
    Purpose:
        Validate add_node rejects empty keys.
    Contract:
        - ValueError is raised for empty node keys.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    with pytest.raises(ValueError):
        dag.add_node("")


def test_component_dag_add_dependency_is_thread_safe() -> None:
    """
    Purpose:
        Validate add_dependency tolerates concurrent calls.
    Contract:
        - All child nodes are registered.
        - Root lists all dependents after threaded additions.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    total = 20

    def worker(idx: int) -> None:
        dag.add_dependency(parent_key="root", child_key=f"child-{idx}")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(total)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(dag.nodes) == total + 1
    root = dag.get_node("root")
    assert root is not None
    assert len(root.dependents) == total


def test_component_dag_node_keeps_first_param_metadata_for_edge() -> None:
    """
    Purpose:
        Validate DagNode retains the first param name for a dependency edge.
    Contract:
        - Re-adding the same dependency does not override param metadata.
    Returns:
        None.
    """
    parent = DagNode("parent")
    child = DagNode("child")

    child.add_dependency(parent, param_name="alpha")
    child.add_dependency(parent, param_name="beta")

    assert child.incoming_params[parent] == "alpha"
    assert child in parent.children_by_param["alpha"]
    assert "beta" not in parent.children_by_param


def test_component_dag_node_rejects_self_dependency() -> None:
    """
    Purpose:
        Validate DagNode rejects self-dependency edges.
    Contract:
        - Adding a dependency to itself raises ValueError.
    Returns:
        None.
    """
    node = DagNode("solo")
    with pytest.raises(ValueError):
        node.add_dependency(node)


def test_component_dag_node_tasks_execute_in_order() -> None:
    """
    Purpose:
        Validate DagNode runs tasks in insertion order.
    Contract:
        - Tasks are executed sequentially as added.
    Returns:
        None.
    """
    node = DagNode("tasked")
    order: list[str] = []

    node.add_task(lambda: order.append("first"))
    node.add_task(lambda: order.append("second"))

    node.run_tasks()
    assert order == ["first", "second"]


def test_component_dag_node_rejects_non_callable_task() -> None:
    """
    Purpose:
        Validate DagNode rejects non-callable tasks.
    Contract:
        - TypeError is raised for non-callable tasks.
    Returns:
        None.
    """
    node = DagNode("tasked")
    with pytest.raises(TypeError):
        node.add_task("not-a-callable")  # type: ignore[arg-type]
