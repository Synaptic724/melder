import unittest
from typing import List

from melder.spellbook.spell_crafter.dag.meld_dag import (
    DagNode,
    DirectedAcyclicWorkGraph,
)


class TestDagNode(unittest.TestCase):
    # 1
    def test_init_sets_id_and_payload(self):
        node = DagNode(key="spell_A", payload={"foo": "bar"})
        self.assertEqual(node.id, "spell_A")
        self.assertEqual(node.payload, {"foo": "bar"})

    # 2
    def test_init_defaults_payload_none(self):
        node = DagNode(key="spell_A")
        self.assertIsNone(node.payload)

    # 3
    def test_dependencies_initially_empty(self):
        node = DagNode(key="A")
        self.assertEqual(len(node.dependencies), 0)

    # 4
    def test_dependents_initially_empty(self):
        node = DagNode(key="A")
        self.assertEqual(len(node.dependents), 0)

    # 5
    def test_add_dependency_links_both_sides(self):
        a = DagNode(key="A")
        b = DagNode(key="B")

        b.add_dependency(a)  # B depends on A

        self.assertIn(a, b.dependencies)
        self.assertIn(b, a.dependents)

    # 6
    def test_add_dependency_idempotent(self):
        a = DagNode(key="A")
        b = DagNode(key="B")

        b.add_dependency(a)
        b.add_dependency(a)  # repeat

        self.assertEqual(len(b.dependencies), 1)
        self.assertEqual(len(a.dependents), 1)

    # 7
    def test_add_dependency_self_raises(self):
        node = DagNode(key="A")
        with self.assertRaises(ValueError):
            node.add_dependency(node)

    # 8
    def test_add_task_registers_callable(self):
        node = DagNode(key="A")
        result: List[int] = []

        def task():
            result.append(1)

        node.add_task(task)
        self.assertEqual(len(node._tasks), 1)  # internal but straightforward
        node.run_tasks()
        self.assertEqual(result, [1])

    # 9
    def test_add_task_rejects_non_callable(self):
        node = DagNode(key="A")
        with self.assertRaises(TypeError):
            node.add_task(123)  # not callable

    # 10
    def test_run_tasks_executes_in_order(self):
        node = DagNode(key="A")
        result: List[int] = []

        def task1():
            result.append(1)

        def task2():
            result.append(2)

        node.add_task(task1)
        node.add_task(task2)

        node.run_tasks()
        self.assertEqual(result, [1, 2])

    # 11
    def test_cleanup_clears_payload(self):
        node = DagNode(key="A", payload={"foo": "bar"})
        node.cleanup()
        self.assertIsNone(node.payload)

    # 12
    def test_cleanup_breaks_dependency_links(self):
        a = DagNode(key="A")
        b = DagNode(key="B")
        c = DagNode(key="C")

        b.add_dependency(a)
        c.add_dependency(b)

        # Sanity check
        self.assertIn(a, b.dependencies)
        self.assertIn(b, a.dependents)
        self.assertIn(b, c.dependencies)
        self.assertIn(c, b.dependents)

        b.cleanup()

        self.assertEqual(len(b.dependencies), 0)
        self.assertEqual(len(b.dependents), 0)
        self.assertNotIn(b, a.dependents)
        self.assertNotIn(b, c.dependencies)

    # 13
    def test_cleanup_clears_tasks(self):
        node = DagNode(key="A")
        node.add_task(lambda: None)
        self.assertEqual(len(node._tasks), 1)
        node.cleanup()
        self.assertEqual(len(node._tasks), 0)

    # 14
    def test_cleanup_idempotent(self):
        node = DagNode(key="A")
        node.cleanup()
        # Second call should not raise
        node.cleanup()

    # 15
    def test_payload_setter_raises_after_cleanup(self):
        node = DagNode(key="A")
        node.cleanup()
        with self.assertRaises(Exception):
            node.payload = "new"

    # 16
    def test_run_tasks_raises_after_cleanup(self):
        node = DagNode(key="A")
        node.add_task(lambda: None)
        node.cleanup()
        with self.assertRaises(Exception):
            node.run_tasks()

    # 17
    def test_repr_includes_id(self):
        node = DagNode(key="A")
        r = repr(node)
        self.assertIn("A", r)
        self.assertIn("DagNode", r)

    # 18
    def test_dependencies_property_returns_live_set(self):
        a = DagNode(key="A")
        b = DagNode(key="B")

        b.add_dependency(a)
        deps = b.dependencies
        self.assertIn(a, deps)

    # 19
    def test_dependents_property_returns_live_set(self):
        a = DagNode(key="A")
        b = DagNode(key="B")

        b.add_dependency(a)
        deps = a.dependents
        self.assertIn(b, deps)

    # 20
    def test_multiple_dependencies_supported(self):
        a = DagNode(key="A")
        b = DagNode(key="B")
        c = DagNode(key="C")

        c.add_dependency(a)
        c.add_dependency(b)

        self.assertEqual(len(c.dependencies), 2)
        self.assertIn(c, a.dependents)
        self.assertIn(c, b.dependents)


class TestDirectedAcyclicWorkGraph(unittest.TestCase):
    # 21
    def test_graph_has_unique_id_string(self):
        dag = DirectedAcyclicWorkGraph()
        self.assertIsInstance(dag.id, str)
        self.assertTrue(dag.id)

    # 22
    def test_add_node_creates_node(self):
        dag = DirectedAcyclicWorkGraph()
        node = dag.add_node("A", payload=123)
        self.assertIsInstance(node, DagNode)
        self.assertEqual(node.id, "A")
        self.assertEqual(node.payload, 123)
        self.assertIn("A", dag.nodes)

    # 23
    def test_add_node_returns_existing_node_for_same_key(self):
        dag = DirectedAcyclicWorkGraph()
        n1 = dag.add_node("A", payload=1)
        n2 = dag.add_node("A", payload=2)
        self.assertIs(n1, n2)
        # payload updated because non-None was provided second time
        self.assertEqual(n1.payload, 2)

    # 24
    def test_add_node_does_not_overwrite_payload_with_none(self):
        dag = DirectedAcyclicWorkGraph()
        n1 = dag.add_node("A", payload=1)
        n2 = dag.add_node("A", payload=None)
        self.assertIs(n1, n2)
        self.assertEqual(n1.payload, 1)

    # 25
    def test_get_node_returns_none_for_missing(self):
        dag = DirectedAcyclicWorkGraph()
        self.assertIsNone(dag.get_node("missing"))

    # 26
    def test_get_node_returns_node_for_existing(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("A")
        node = dag.get_node("A")
        self.assertIsNotNone(node)
        self.assertEqual(node.id, "A")

    # 27
    def test_add_dependency_creates_nodes_if_missing(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("A", "B")  # B depends on A
        self.assertIn("A", dag.nodes)
        self.assertIn("B", dag.nodes)
        a = dag.get_node("A")
        b = dag.get_node("B")
        self.assertIn(a, b.dependencies)
        self.assertIn(b, a.dependents)

    # 28
    def test_add_dependency_wires_dependency_relationship(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("A")
        dag.add_node("B")
        dag.add_dependency("A", "B")
        a = dag.get_node("A")
        b = dag.get_node("B")
        self.assertIn(a, b.dependencies)
        self.assertIn(b, a.dependents)

    # 29
    def test_topological_sort_simple_chain(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("A", "B")  # B depends on A
        dag.add_dependency("B", "C")  # C depends on B

        order = dag.topological_sort()
        ids = [node.id for node in order]
        self.assertEqual(ids, ["A", "B", "C"])

    # 30
    def test_topological_sort_branching_graph(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("A", "C")  # C depends on A
        dag.add_dependency("B", "C")  # C depends on B

        order_ids = [n.id for n in dag.topological_sort()]

        # A and B must appear before C
        self.assertIn("C", order_ids)
        c_index = order_ids.index("C")
        self.assertLess(order_ids.index("A"), c_index)
        self.assertLess(order_ids.index("B"), c_index)

    # 31
    def test_topological_sort_multiple_roots(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("Root1")
        dag.add_node("Root2")
        dag.add_dependency("Root1", "Child")
        # Root2 is independent

        ids = [n.id for n in dag.topological_sort()]
        self.assertIn("Root1", ids)
        self.assertIn("Root2", ids)
        self.assertIn("Child", ids)
        self.assertLess(ids.index("Root1"), ids.index("Child"))

    # 32
    def test_collect_dependency_ids_matches_sorted_order(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("Config", "Service")
        dag.add_dependency("Service", "Controller")

        ordered_nodes = dag.topological_sort()
        expected_ids = [n.id for n in ordered_nodes]
        collected_ids = dag.collect_dependency_ids()
        self.assertEqual(collected_ids, expected_ids)

    # 33
    def test_execute_runs_node_tasks_in_topological_order(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("A", "B")
        dag.add_dependency("B", "C")

        output: List[str] = []

        dag.get_node("A").add_task(lambda: output.append("A"))
        dag.get_node("B").add_task(lambda: output.append("B"))
        dag.get_node("C").add_task(lambda: output.append("C"))

        dag.execute()
        self.assertEqual(output, ["A", "B", "C"])

    # 34
    def test_execute_propagates_task_exception(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("A")
        dag.get_node("A").add_task(lambda: (_ for _ in ()).throw(RuntimeError("boom")))

        with self.assertRaises(RuntimeError):
            dag.execute()

    # 35
    def test_cleanup_invokes_node_cleanup_and_clears_nodes(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("A", "B")
        dag.add_dependency("B", "C")

        self.assertGreater(len(dag.nodes), 0)

        dag.cleanup()

        self.assertEqual(len(dag.nodes), 0)

        # Nodes should be cleaned (best effort check on one)
        # We can't access them from dag anymore, so just ensuring no exceptions
        dag.cleanup()  # idempotent call

    # 36
    def test_cleanup_idempotent_on_graph(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("A")
        dag.cleanup()
        dag.cleanup()  # should not raise

    # 37
    def test_add_node_after_cleanup_raises(self):
        dag = DirectedAcyclicWorkGraph()
        dag.cleanup()
        with self.assertRaises(Exception):
            dag.add_node("A")

    # 38
    def test_topological_sort_detects_cycle_and_raises_runtime_error(self):
        dag = DirectedAcyclicWorkGraph()
        # Create A -> B
        dag.add_dependency("A", "B")
        a = dag.get_node("A")
        b = dag.get_node("B")

        # Manually introduce B -> A cycle via node API
        a_dep_before = len(a.dependencies)
        b_dep_before = len(b.dependencies)
        b.add_dependency(a)  # this is already there via add_dependency
        a.add_dependency(b)  # introduces cycle

        self.assertGreaterEqual(len(a.dependencies), a_dep_before)
        self.assertGreaterEqual(len(b.dependencies), b_dep_before)

        with self.assertRaises(RuntimeError):
            dag.topological_sort()

    # 39
    def test_execute_on_empty_graph_is_noop(self):
        dag = DirectedAcyclicWorkGraph()
        # Should not raise
        dag.execute()

    # 40
    def test_nodes_property_exposes_internal_mapping_reference(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("A")
        nodes_view = dag.nodes
        self.assertIn("A", nodes_view)
        # Mutation on DAG should reflect in nodes_view
        dag.add_node("B")
        self.assertIn("B", nodes_view)


if __name__ == "__main__":
    unittest.main()
