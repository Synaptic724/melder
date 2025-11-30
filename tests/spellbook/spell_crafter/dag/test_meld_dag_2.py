import unittest
from typing import List, Set

from melder.spellbook.spell_crafter.dag.dag_node import (
    DagNode,
    DirectedAcyclicWorkGraph,
)


class TestDagNodeExtra(unittest.TestCase):
    # 1
    def test_whitespace_key_is_allowed(self):
        node = DagNode(key=" ")
        self.assertEqual(node.id, " ")

    # 2
    def test_long_key_is_preserved(self):
        long_key = "spell_" + "X" * 256
        node = DagNode(key=long_key)
        self.assertEqual(node.id, long_key)

    # 3
    def test_payload_setter_updates_value_before_cleanup(self):
        node = DagNode(key="A", payload=1)
        node.payload = 2
        self.assertEqual(node.payload, 2)

    # 4
    def test_three_level_dependency_chain_via_node(self):
        a = DagNode("A")
        b = DagNode("B")
        c = DagNode("C")

        b.add_dependency(a)
        c.add_dependency(b)

        self.assertIn(a, b.dependencies)
        self.assertIn(b, c.dependencies)
        self.assertIn(b, a.dependents)
        self.assertIn(c, b.dependents)

    # 5
    def test_add_dependency_after_cleanup_raises(self):
        a = DagNode("A")
        b = DagNode("B")
        a.cleanup()
        with self.assertRaises(Exception):
            b.add_dependency(a)

    # 6
    def test_run_tasks_stops_at_first_exception(self):
        node = DagNode("A")
        result: List[int] = []

        def task1():
            result.append(1)
            raise RuntimeError("boom")

        def task2():
            result.append(2)

        node.add_task(task1)
        node.add_task(task2)

        with self.assertRaises(RuntimeError):
            node.run_tasks()

        # Second task should not have executed
        self.assertEqual(result, [1])

    # 7
    def test_add_task_after_cleanup_raises(self):
        node = DagNode("A")
        node.cleanup()
        with self.assertRaises(Exception):
            node.add_task(lambda: None)

    # 8
    def test_run_tasks_on_node_with_no_tasks_is_noop(self):
        node = DagNode("A")
        # Should not raise
        node.run_tasks()

    # 9
    def test_multiple_dependencies_reflected_both_ways(self):
        a = DagNode("A")
        b = DagNode("B")
        c = DagNode("C")

        c.add_dependency(a)
        c.add_dependency(b)

        self.assertEqual(c.dependencies, {a, b})
        self.assertIn(c, a.dependents)
        self.assertIn(c, b.dependents)

    # 10
    def test_cleanup_does_not_change_node_id(self):
        node = DagNode("A")
        node.cleanup()
        self.assertEqual(node.id, "A")


class TestDirectedAcyclicWorkGraphExtra(unittest.TestCase):
    # 11
    def test_add_node_with_empty_key_raises(self):
        dag = DirectedAcyclicWorkGraph()
        with self.assertRaises(ValueError):
            dag.add_node("")

    # 12
    def test_add_node_with_whitespace_key_is_allowed(self):
        dag = DirectedAcyclicWorkGraph()
        node = dag.add_node(" ")
        self.assertEqual(node.id, " ")
        self.assertIn(" ", dag.nodes)

    # 13
    def test_topological_sort_single_node(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("Only")
        order = dag.topological_sort()
        self.assertEqual([n.id for n in order], ["Only"])

    # 14
    def test_collect_dependency_ids_on_empty_graph_returns_empty_list(self):
        dag = DirectedAcyclicWorkGraph()
        self.assertEqual(dag.collect_dependency_ids(), [])

    # 15
    def test_execute_with_nodes_but_no_tasks_is_noop(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("A")
        dag.add_node("B")
        # Should not raise
        dag.execute()

    # 16
    def test_topological_sort_is_pure_callable_twice(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("A", "B")
        dag.add_dependency("B", "C")

        first = [n.id for n in dag.topological_sort()]
        second = [n.id for n in dag.topological_sort()]
        self.assertEqual(first, second)

    # 17
    def test_multiple_disjoint_subgraphs_respect_local_order(self):
        dag = DirectedAcyclicWorkGraph()
        # Subgraph 1: X -> Y
        dag.add_dependency("X", "Y")
        # Subgraph 2: A -> B
        dag.add_dependency("A", "B")

        ids = [n.id for n in dag.topological_sort()]
        self.assertLess(ids.index("X"), ids.index("Y"))
        self.assertLess(ids.index("A"), ids.index("B"))
        # All four nodes present
        self.assertSetEqual(set(ids), {"X", "Y", "A", "B"})

    # 18
    def test_fan_out_dependencies_require_root_first(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("Root", "Left")
        dag.add_dependency("Root", "Right")

        ids = [n.id for n in dag.topological_sort()]
        self.assertLess(ids.index("Root"), ids.index("Left"))
        self.assertLess(ids.index("Root"), ids.index("Right"))

    # 19
    def test_large_linear_chain_topological_sort_length(self):
        dag = DirectedAcyclicWorkGraph()
        num = 50
        # Build chain 0 -> 1 -> ... -> 49
        for i in range(num - 1):
            dag.add_dependency(str(i), str(i + 1))

        order = dag.topological_sort()
        self.assertEqual(len(order), num)
        self.assertEqual(order[0].id, "0")
        self.assertEqual(order[-1].id, str(num - 1))

    # 20
    def test_execute_large_chain_calls_all_tasks(self):
        dag = DirectedAcyclicWorkGraph()
        num = 20
        for i in range(num - 1):
            dag.add_dependency(str(i), str(i + 1))

        seen: List[str] = []
        for i in range(num):
            dag.get_node(str(i)).add_task(lambda i=i: seen.append(str(i)))

        dag.execute()
        self.assertEqual(seen, [str(i) for i in range(num)])

    # 21
    def test_topological_sort_after_cleanup_raises(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("A")
        dag.cleanup()
        with self.assertRaises(Exception):
            dag.topological_sort()

    # 22
    def test_execute_after_cleanup_raises(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("A")
        dag.cleanup()
        with self.assertRaises(Exception):
            dag.execute()

    # 23
    def test_collect_dependency_ids_after_cleanup_raises(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("A")
        dag.cleanup()
        with self.assertRaises(Exception):
            dag.collect_dependency_ids()

    # 24
    def test_get_node_after_cleanup_raises(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("A")
        dag.cleanup()
        with self.assertRaises(Exception):
            dag.get_node("A")

    # 25
    def test_add_dependency_after_cleanup_raises(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("A")
        dag.cleanup()
        with self.assertRaises(Exception):
            dag.add_dependency("A", "B")

    # 26
    def test_cycle_via_dag_add_dependency_two_nodes(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("A", "B")
        dag.add_dependency("B", "A")  # introduce cycle
        with self.assertRaises(RuntimeError):
            dag.topological_sort()

    # 27
    def test_collect_dependency_ids_raises_on_cycle(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("A", "B")
        dag.add_dependency("B", "A")
        with self.assertRaises(RuntimeError):
            dag.collect_dependency_ids()

    # 28
    def test_isolated_nodes_without_dependencies_present_in_sort(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("A")
        dag.add_node("B")
        dag.add_node("C")

        ids = [n.id for n in dag.topological_sort()]
        self.assertSetEqual(set(ids), {"A", "B", "C"})

    # 29
    def test_execute_branching_graph_respects_dependency_order(self):
        dag = DirectedAcyclicWorkGraph()
        #   Base
        #   /  \
        #  L    R
        dag.add_dependency("Base", "Left")
        dag.add_dependency("Base", "Right")

        order: List[str] = []
        dag.get_node("Base").add_task(lambda: order.append("Base"))
        dag.get_node("Left").add_task(lambda: order.append("Left"))
        dag.get_node("Right").add_task(lambda: order.append("Right"))

        dag.execute()

        self.assertEqual(set(order), {"Base", "Left", "Right"})
        self.assertLess(order.index("Base"), order.index("Left"))
        self.assertLess(order.index("Base"), order.index("Right"))

    # 30
    def test_execute_with_some_nodes_without_tasks(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("A", "B")
        dag.add_dependency("B", "C")

        seen: List[str] = []
        dag.get_node("A").add_task(lambda: seen.append("A"))
        # B has no tasks
        dag.get_node("C").add_task(lambda: seen.append("C"))

        dag.execute()
        self.assertEqual(seen, ["A", "C"])

    # 31
    def test_nodes_property_returns_same_mapping_object(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("A")
        first = dag.nodes
        second = dag.nodes
        self.assertIs(first, second)

    # 32
    def test_reusing_node_with_new_payload_updates_payload(self):
        dag = DirectedAcyclicWorkGraph()
        node1 = dag.add_node("A", payload=1)
        node2 = dag.add_node("A", payload=2)
        self.assertIs(node1, node2)
        self.assertEqual(node1.payload, 2)

    # 33
    def test_add_dependency_does_not_duplicate_edges(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("A", "B")
        dag.add_dependency("A", "B")  # duplicate

        a = dag.get_node("A")
        b = dag.get_node("B")
        self.assertEqual(len(b.dependencies), 1)
        self.assertEqual(len(a.dependents), 1)

    # 34
    def test_execute_stops_on_first_failing_task_and_skips_rest(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("A", "B")

        output: List[str] = []

        dag.get_node("A").add_task(lambda: output.append("A"))
        dag.get_node("B").add_task(
            lambda: (_ for _ in ()).throw(RuntimeError("boom"))
        )
        dag.get_node("B").add_task(lambda: output.append("B-after"))

        with self.assertRaises(RuntimeError):
            dag.execute()

        # B-after should not run
        self.assertEqual(output, ["A"])

    # 35
    def test_dag_cleanup_marks_nodes_unusable(self):
        dag = DirectedAcyclicWorkGraph()
        node = dag.add_node("A")
        dag.cleanup()
        with self.assertRaises(Exception):
            node.run_tasks()

    # 36
    def test_three_node_cycle_detected(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("A", "B")
        dag.add_dependency("B", "C")
        dag.add_dependency("C", "A")  # cycle

        with self.assertRaises(RuntimeError):
            dag.topological_sort()

    # 37
    def test_topological_sort_obeys_all_dependency_constraints_generic(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("A", "C")
        dag.add_dependency("B", "C")
        dag.add_dependency("C", "D")
        dag.add_dependency("D", "E")

        order = dag.topological_sort()
        index = {node.id: i for i, node in enumerate(order)}

        def assert_dep(before: str, after: str):
            self.assertLess(index[before], index[after])

        assert_dep("A", "C")
        assert_dep("B", "C")
        assert_dep("C", "D")
        assert_dep("D", "E")

    # 38
    def test_execute_two_independent_chains_local_order_preserved(self):
        dag = DirectedAcyclicWorkGraph()
        # Chain 1: A1 -> B1
        dag.add_dependency("A1", "B1")
        # Chain 2: A2 -> B2
        dag.add_dependency("A2", "B2")

        out: List[str] = []
        dag.get_node("A1").add_task(lambda: out.append("A1"))
        dag.get_node("B1").add_task(lambda: out.append("B1"))
        dag.get_node("A2").add_task(lambda: out.append("A2"))
        dag.get_node("B2").add_task(lambda: out.append("B2"))

        dag.execute()

        # local order constraints
        self.assertLess(out.index("A1"), out.index("B1"))
        self.assertLess(out.index("A2"), out.index("B2"))
        self.assertSetEqual(set(out), {"A1", "B1", "A2", "B2"})

    # 39
    def test_collect_dependency_ids_after_graph_mutation_reflects_new_nodes(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_dependency("A", "B")
        first_ids = dag.collect_dependency_ids()
        self.assertEqual(set(first_ids), {"A", "B"})

        dag.add_dependency("B", "C")
        second_ids = dag.collect_dependency_ids()
        self.assertEqual(set(second_ids), {"A", "B", "C"})

    # 40
    def test_mixed_add_node_and_add_dependency_yields_consistent_relationships(self):
        dag = DirectedAcyclicWorkGraph()
        dag.add_node("Root")
        dag.add_node("Mid")
        dag.add_dependency("Root", "Leaf")
        dag.add_dependency("Mid", "Leaf")

        leaf = dag.get_node("Leaf")
        deps: Set[DagNode] = leaf.dependencies
        ids = {n.id for n in deps}
        self.assertSetEqual(ids, {"Root", "Mid"})


if __name__ == "__main__":
    unittest.main()
