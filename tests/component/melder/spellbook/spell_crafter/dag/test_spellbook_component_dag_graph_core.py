import threading

import pytest

from melder.aether.spellbook.spell_compiler.dag.dag_node import DagNode
from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
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
    from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind

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


def test_component_dag_topological_levels_diamond_peels_by_dependency_depth() -> None:
    """
    Purpose:
        Validate topological_levels peels a diamond into independent
        layers (S4 flatten law).
    Contract:
        - root alone in level 0; both middles share level 1; sink in 2.
        - In-level order is ascending node id.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    for key in ("root", "mid_b", "mid_a", "sink"):
        dag.add_node(key)
    dag.add_dependency(parent_key="root", child_key="mid_a")
    dag.add_dependency(parent_key="root", child_key="mid_b")
    dag.add_dependency(parent_key="mid_a", child_key="sink")
    dag.add_dependency(parent_key="mid_b", child_key="sink")
    levels = dag.topological_levels()
    assert [[node.id for node in level] for level in levels] == [
        ["root"], ["mid_a", "mid_b"], ["sink"]
    ]
    dag.cleanup()


def test_component_dag_topological_levels_disjoint_components_share_levels() -> None:
    """
    Purpose:
        Validate mutually independent components land in the SAME level
        (maximum parallel width, not chain order).
    Contract:
        - Two independent chains peel level-by-level together.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    for key in ("a1", "a2", "b1", "b2"):
        dag.add_node(key)
    dag.add_dependency(parent_key="a1", child_key="a2")
    dag.add_dependency(parent_key="b1", child_key="b2")
    levels = dag.topological_levels()
    assert [[node.id for node in level] for level in levels] == [
        ["a1", "b1"], ["a2", "b2"]
    ]
    dag.cleanup()


def test_component_dag_topological_levels_flatten_matches_sort_law() -> None:
    """
    Purpose:
        Validate levels are a coarsening of topological_sort: flattening
        them yields a valid topological order over the same nodes.
    Contract:
        - Every dependency's level index is strictly below its dependent's.
        - Flattened node set equals the graph's node set.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    for key in ("f", "e", "d", "c", "b", "a"):
        dag.add_node(key)
    dag.add_dependency(parent_key="a", child_key="b")
    dag.add_dependency(parent_key="a", child_key="c")
    dag.add_dependency(parent_key="b", child_key="d")
    dag.add_dependency(parent_key="c", child_key="d")
    dag.add_dependency(parent_key="d", child_key="e")
    levels = dag.topological_levels()
    level_of = {
        node.id: index
        for index, level in enumerate(levels)
        for node in level
    }
    assert set(level_of) == {"a", "b", "c", "d", "e", "f"}
    for child_id, parent_id in (
            ("b", "a"), ("c", "a"), ("d", "b"), ("d", "c"), ("e", "d")
    ):
        assert level_of[parent_id] < level_of[child_id]
    dag.cleanup()


def test_component_dag_topological_levels_empty_and_singleton() -> None:
    """
    Purpose:
        Validate degenerate shapes: empty graph and one edgeless node.
    Contract:
        - Empty graph -> empty level list; singleton -> one one-node level.
    Returns:
        None.
    """
    empty = DirectedAcyclicWorkGraph()
    assert empty.topological_levels() == []
    empty.cleanup()

    single = DirectedAcyclicWorkGraph()
    single.add_node("only")
    levels = single.topological_levels()
    assert [[node.id for node in level] for level in levels] == [["only"]]
    single.cleanup()


def test_component_dag_topological_levels_cycle_refuses_like_sort() -> None:
    """
    Purpose:
        Validate the cycle refusal law is shared with topological_sort.
    Contract:
        - RuntimeError from BOTH traversals on the same cyclic graph.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_node("x")
    dag.add_node("y")
    dag.add_dependency(parent_key="y", child_key="x")
    dag.add_dependency(parent_key="x", child_key="y")
    with pytest.raises(RuntimeError):
        dag.topological_levels()
    with pytest.raises(RuntimeError):
        dag.topological_sort()
    dag.cleanup()


def test_component_dag_topological_levels_is_side_effect_free() -> None:
    """
    Purpose:
        Validate repeat calls return identical levels and sort() is
        untouched by the new traversal.
    Contract:
        - Two levels calls agree; sort still returns all nodes in order.
    Returns:
        None.
    """
    dag = DirectedAcyclicWorkGraph()
    for key in ("n1", "n2"):
        dag.add_node(key)
    dag.add_dependency(parent_key="n1", child_key="n2")
    first = [[node.id for node in level] for level in dag.topological_levels()]
    second = [[node.id for node in level] for level in dag.topological_levels()]
    assert first == second == [["n1"], ["n2"]]
    assert [node.id for node in dag.topological_sort()] == ["n1", "n2"]
    dag.cleanup()


def test_component_dag_topological_levels_wide_star_is_two_levels():
    """
    Purpose:
        Validate maximum width: one root fanning out to 40 children peels
        into exactly two levels with the whole fan mutually independent
        (the restore plan's many-books-one-frame shape at scale).
    Contract:
        Level 0 = [root]; level 1 = all 40 children ascending by id.
    Returns:
        None.
    Raises:
        AssertionError: If fan-out width or in-level order drifts.
    """
    dag = DirectedAcyclicWorkGraph()
    children = ["child-{0:02d}".format(i) for i in range(40)]
    dag.add_node("root")
    for child in children:
        dag.add_dependency(parent_key="root", child_key=child)
    levels = dag.topological_levels()
    assert [[node.id for node in level] for level in levels] == [
        ["root"], sorted(children)
    ]
    dag.cleanup()


def test_component_dag_topological_levels_deep_chain_is_one_per_level():
    """
    Purpose:
        Validate maximum depth: a 60-node chain peels into 60 singleton
        levels in exact dependency order (no level ever coalesces nodes
        with an edge between them).
    Contract:
        Level i holds exactly node i of the chain.
    Returns:
        None.
    Raises:
        AssertionError: If chain depth collapses or reorders.
    """
    dag = DirectedAcyclicWorkGraph()
    keys = ["n-{0:03d}".format(i) for i in range(60)]
    for earlier, later in zip(keys, keys[1:]):
        dag.add_dependency(parent_key=earlier, child_key=later)
    levels = dag.topological_levels()
    assert [[node.id for node in level] for level in levels] == [
        [key] for key in keys
    ]
    dag.cleanup()


def test_component_dag_duplicate_edge_does_not_distort_levels():
    """
    Purpose:
        Validate edge set semantics: adding the SAME dependency twice
        must not double-count indegree - otherwise one peel could never
        release the child and the plan would refuse as a phantom cycle.
    Contract:
        Levels are identical to the single-edge graph.
    Returns:
        None.
    Raises:
        AssertionError: If a duplicate edge distorts the peel.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency(parent_key="a", child_key="b")
    dag.add_dependency(parent_key="a", child_key="b")
    levels = dag.topological_levels()
    assert [[node.id for node in level] for level in levels] == [
        ["a"], ["b"]
    ]
    dag.cleanup()


def test_component_dag_bulk_edges_flatten_like_individual_edges():
    """
    Purpose:
        Validate the bulk edge lane against the individual lane: both
        must produce identical levels for the same recorded shape.
    Contract:
        A diamond built via add_dependencies_bulk equals one built edge
        by edge.
    Returns:
        None.
    Raises:
        AssertionError: If the two edge lanes diverge structurally.
    """
    edges = [
        ("root", "mid_a", None, None),
        ("root", "mid_b", None, None),
        ("mid_a", "sink", None, None),
        ("mid_b", "sink", None, None),
    ]
    bulk = DirectedAcyclicWorkGraph()
    bulk.add_dependencies_bulk(edges)
    individual = DirectedAcyclicWorkGraph()
    for parent_key, child_key, _param, _kind in edges:
        individual.add_dependency(
            parent_key=parent_key, child_key=child_key
        )
    bulk_shape = [
        [node.id for node in level]
        for level in bulk.topological_levels()
    ]
    individual_shape = [
        [node.id for node in level]
        for level in individual.topological_levels()
    ]
    assert bulk_shape == individual_shape == [
        ["root"], ["mid_a", "mid_b"], ["sink"]
    ]
    bulk.cleanup()
    individual.cleanup()


def test_component_dag_levels_preserve_payload_object_identity():
    """
    Purpose:
        Validate the planner's payload contract: topological_levels hands
        back the SAME node objects, so payloads attached at add_node time
        (the restore plan's (kind, key) descriptors) survive by identity.
    Contract:
        The payload object in the peeled level IS the attached object.
    Returns:
        None.
    Raises:
        AssertionError: If payloads are copied or dropped by the peel.
    """
    dag = DirectedAcyclicWorkGraph()
    payload = ("book", ("b1", "extra"))
    dag.add_node("book:b1", payload=payload)
    dag.add_dependency(parent_key="frame:f", child_key="book:b1")
    levels = dag.topological_levels()
    assert levels[1][0].payload is payload
    assert levels[0][0].payload is None
    dag.cleanup()
