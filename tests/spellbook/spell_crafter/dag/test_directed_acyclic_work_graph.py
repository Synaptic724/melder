# tests/dag/test_dag_core.py
import unittest
import tempfile
import os
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
    Node,
    Edge,
    ExecutionContext,
    StateObject,
)
# --- Test doubles ------------------------------------------------------------

class StubContext(ExecutionContext):
    def __init__(self, state: StateObject, flag_store: dict, key: str):
        super().__init__(state)
        self.flag_store = flag_store
        self.key = key
        self.calls = 0

    def execute(self):
        self.calls += 1
        self.flag_store[self.key] = self.flag_store.get(self.key, 0) + 1
        if self.state:
            self.state.register_node_result(self.key, success=True)

class FailingContext(ExecutionContext):
    def __init__(self, state: StateObject, node_id):
        super().__init__(state)
        self.node_id = node_id
        self.calls = 0

    def execute(self):
        self.calls += 1
        if self.state:
            self.state.register_node_result(self.node_id, success=False)

# Minimal fake DAG interface for isolated StateObject tests (where needed)
class MiniDag:
    def __init__(self):
        self.removed = []
        self.sorted_called = 0
        self._nodes = {}
        self._edges = []

    def find_node_by_id(self, node_id):
        return node_id if node_id in self._nodes else None

    def remove_node(self, node):
        self.removed.append(node)
        self._nodes.pop(node, None)

    def topological_sort(self):
        self.sorted_called += 1
        return ["A", "B"]

# --- Test suite --------------------------------------------------------------

class TestStateObjectBasics(unittest.TestCase):
    def test_register_success_and_status_lookup(self):
        dag = MiniDag()
        s = StateObject(dag)
        s.register_node_result("N1", success=True)
        self.assertEqual(s.get_status("N1"), "SUCCESS")
        self.assertEqual(s.get_status("N2"), "UNKNOWN")

    def test_register_failure_removes_from_dag(self):
        dag = MiniDag()
        dag._nodes["N3"] = "N3"
        s = StateObject(dag)
        s.register_node_result("N3", success=False)
        self.assertEqual(s.get_status("N3"), "FAILED")
        self.assertIn("N3", dag.removed)

    def test_remove_node_and_edges_noop_when_missing(self):
        dag = MiniDag()
        s = StateObject(dag)
        s.remove_node_and_edges("ghost")
        self.assertEqual(dag.removed, [])

    def test_recalc_topological_order_calls_dag(self):
        dag = MiniDag()
        s = StateObject(dag)
        order = s.recalc_topological_order()
        self.assertEqual(order, ["A", "B"])
        self.assertEqual(dag.sorted_called, 1)

    def test_get_all_statuses_returns_copy(self):
        dag = MiniDag()
        s = StateObject(dag)
        s.register_node_result("X", True)
        snap = s.get_all_statuses()
        snap["X"] = "HACK"
        self.assertEqual(s.get_status("X"), "SUCCESS")

    def test_state_cleanup_clears_data_and_dag(self):
        dag = MiniDag()
        s = StateObject(dag)
        s.register_node_result("N", True)
        s.cleanup()
        self.assertEqual(s.get_all_statuses(), {})
        self.assertIsNone(s._dag)
        # idempotent
        s.cleanup()


class TestNodeEdgesAndTasks(unittest.TestCase):
    def test_add_and_remove_edges_updates_nodes(self):
        n1, n2 = Node("A"), Node("B")
        dag = DirectedAcyclicWorkGraph()
        dag.add_node(n1)
        dag.add_node(n2)

        e = Edge(n1, n2)
        dag.add_edge(e)

        self.assertIn(e, dag.get_edges())
        self.assertIn(e, n1.get_outgoing_edges())
        self.assertIn(e, n2.get_incoming_edges())

        dag.remove_edge(e)
        self.assertNotIn(e, dag.get_edges())
        self.assertNotIn(e, n1.get_outgoing_edges())
        self.assertNotIn(e, n2.get_incoming_edges())

    def test_add_remove_node_prunes_edges(self):
        n1, n2 = Node("A"), Node("B")
        dag = DirectedAcyclicWorkGraph()
        dag.add_node(n1)
        dag.add_node(n2)
        e = Edge(n1, n2)
        dag.add_edge(e)
        self.assertIn(e, dag.get_edges())
        dag.remove_node(n1)
        self.assertNotIn(e, dag.get_edges())
        self.assertIsNone(dag.find_node_by_id("A"))

    def test_node_add_and_execute_tasks(self):
        n = Node("X")
        acc = []
        n.add_task(lambda: acc.append(1))
        n.add_task(lambda: acc.append(2))
        n.execute_tasks()
        self.assertEqual(acc, [1, 2])

    def test_set_and_get_execution_context(self):
        s = StateObject(MiniDag())
        n = Node("X")
        flags = {}
        ctx = StubContext(s, flags, "X")
        n.set_execution_context(ctx)
        self.assertIs(n.get_execution_context(), ctx)

    def test_execute_tasks_runs_context_after_tasks(self):
        s = StateObject(MiniDag())
        n = Node("X")
        seq = []
        n.add_task(lambda: seq.append("t1"))
        flags = {}
        n.set_execution_context(StubContext(s, flags, "X"))
        n.execute_tasks()
        self.assertEqual(seq, ["t1"])
        self.assertEqual(flags["X"], 1)

    def test_execute_chains_to_next_node_when_flag_true(self):
        a, b = Node("A"), Node("B")
        e = Edge(a, b)
        a.add_outgoing_edge(e)
        b.add_incoming_edge(e)

        acc = []
        a.add_task(lambda: acc.append("A"))
        b.add_task(lambda: acc.append("B"))

        a.execute(execute_internally=True)
        self.assertEqual(acc, ["A", "B"])

    def test_get_next_node_for_zero_or_many_edges(self):
        a, b, c = Node("A"), Node("B"), Node("C")
        self.assertIsNone(a.get_next_node())  # none

        e = Edge(a, b)
        a.add_outgoing_edge(e)
        b.add_incoming_edge(e)
        self.assertIs(a.get_next_node(), b)

        # add another edge; get_next_node still returns first if any (per current impl)
        e2 = Edge(a, c)
        a.add_outgoing_edge(e2)
        c.add_incoming_edge(e2)
        self.assertIsNotNone(a.get_next_node())

    def test_find_target_node(self):
        a, b, c = Node("A"), Node("B"), Node("C")
        e1, e2 = Edge(a, b), Edge(a, c)
        a.add_outgoing_edge(e1); b.add_incoming_edge(e1)
        a.add_outgoing_edge(e2); c.add_incoming_edge(e2)

        self.assertIs(a.find_target_node("B"), b)
        self.assertIs(a.find_target_node("C"), c)
        self.assertIsNone(a.find_target_node("Z"))

    def test_node_cleanup_disposes_context_and_clears_lists(self):
        s = StateObject(MiniDag())
        n = Node("X")
        n.add_task(lambda: None)
        n.add_incoming_edge(Edge(Node("S"), n))
        n.add_outgoing_edge(Edge(n, Node("T")))

        flags = {}
        ctx = StubContext(s, flags, "X")
        n.set_execution_context(ctx)
        n.cleanup()
        self.assertEqual(n.get_incoming_edges(), [])
        self.assertEqual(n.get_outgoing_edges(), [])
        self.assertEqual(n._tasks, [])
        self.assertIsNone(n.get_execution_context())
        # idempotent
        n.cleanup()


class TestDAGTopologyAndExecution(unittest.TestCase):
    def test_add_and_find_nodes(self):
        dag = DirectedAcyclicWorkGraph()
        a, b = Node("A"), Node("B")
        dag.add_node(a); dag.add_node(b)
        self.assertIs(dag.find_node_by_id("A"), a)
        self.assertIs(dag.find_node_by_id("B"), b)
        self.assertIsNone(dag.find_node_by_id("Z"))

    def test_topological_sort_linear_chain(self):
        dag = DirectedAcyclicWorkGraph()
        a, b, c = Node("A"), Node("B"), Node("C")
        for n in (a, b, c): dag.add_node(n)
        dag.add_edge(Edge(a, b)); dag.add_edge(Edge(b, c))
        order = [n.id for n in dag.topological_sort()]
        self.assertEqual(order, ["A", "B", "C"])

    def test_topological_sort_branching(self):
        dag = DirectedAcyclicWorkGraph()
        a, b, c, d = Node("A"), Node("B"), Node("C"), Node("D")
        for n in (a, b, c, d): dag.add_node(n)
        dag.add_edge(Edge(a, c)); dag.add_edge(Edge(b, c)); dag.add_edge(Edge(c, d))
        order = [n.id for n in dag.topological_sort()]
        self.assertEqual(order[0] in {"A", "B"}, True)
        self.assertIn("C", order[1:])
        self.assertEqual(order[-1], "D")

    def test_topological_sort_cycle_raises(self):
        dag = DirectedAcyclicWorkGraph()
        a, b = Node("A"), Node("B")
        for n in (a, b): dag.add_node(n)
        e1, e2 = Edge(a, b), Edge(b, a)
        dag.add_edge(e1); dag.add_edge(e2)
        with self.assertRaises(ValueError):
            dag.topological_sort()

    def test_execute_runs_tasks_in_topological_order(self):
        dag = DirectedAcyclicWorkGraph()
        acc = []
        a, b = Node("A"), Node("B")
        a.add_task(lambda: acc.append("A"))
        b.add_task(lambda: acc.append("B"))
        dag.add_node(a); dag.add_node(b)
        dag.add_edge(Edge(a, b))
        dag.execute()
        self.assertEqual(acc, ["A", "B"])

    def test_execute_layered_simple(self):
        dag = DirectedAcyclicWorkGraph()
        acc = []
        a, b, c = Node("A"), Node("B"), Node("C")
        a.add_task(lambda: acc.append("A"))
        b.add_task(lambda: acc.append("B"))
        c.add_task(lambda: acc.append("C"))

        dag.add_node(a); dag.add_node(b); dag.add_node(c)
        dag.add_edge(Edge(a, c))
        dag.add_edge(Edge(b, c))

        dag.execute_layered()
        # order must end with C; A and B can be before in any order
        self.assertEqual(acc[-1], "C")
        self.assertCountEqual(acc[:-1], ["A", "B"])

    def test_generate_dot_file_contains_edges(self):
        dag = DirectedAcyclicWorkGraph()
        a, b = Node("A"), Node("B")
        dag.add_node(a); dag.add_node(b)
        dag.add_edge(Edge(a, b))
        with tempfile.TemporaryDirectory() as td:
            fp = os.path.join(td, "g.dot")
            dag.generate_dot_file(fp)
            with open(fp, "r") as f:
                text = f.read()
            self.assertIn('digraph G {', text)
            self.assertIn('"A" -> "B";', text)

    def test_dag_cleanup_clears_nodes_and_edges(self):
        dag = DirectedAcyclicWorkGraph()
        a, b = Node("A"), Node("B")
        dag.add_node(a); dag.add_node(b)
        dag.add_edge(Edge(a, b))
        dag.cleanup()
        self.assertEqual(dag.get_nodes(), [])
        self.assertEqual(dag.get_edges(), [])
        # idempotent
        dag.cleanup()


class TestIntegrationStateWithContexts(unittest.TestCase):
    def test_stub_context_marks_success_in_state(self):
        dag = DirectedAcyclicWorkGraph()
        s = StateObject(dag)
        n = Node("N1")
        flags = {}
        n.set_execution_context(StubContext(s, flags, "N1"))
        n.execute_tasks()
        self.assertEqual(s.get_status("N1"), "SUCCESS")
        self.assertEqual(flags["N1"], 1)

    def test_failing_context_marks_failed_and_prunes(self):
        dag = DirectedAcyclicWorkGraph()
        a = Node("A")
        dag.add_node(a)
        s = StateObject(dag)
        a.set_execution_context(FailingContext(s, "A"))
        a.execute_tasks()
        self.assertEqual(s.get_status("A"), "FAILED")
        self.assertIsNone(dag.find_node_by_id("A"))

    def test_state_cleanup_does_not_break_context_cleanup(self):
        dag = DirectedAcyclicWorkGraph()
        s = StateObject(dag)
        n = Node("N")
        ctx = StubContext(s, {}, "N")
        n.set_execution_context(ctx)
        s.cleanup()
        # context cleanup should still be safe
        n.cleanup()  # should not crash

    def test_multiple_task_runs_and_context_calls_count(self):
        s = StateObject(MiniDag())
        n = Node("X")
        flags = {}
        ctx = StubContext(s, flags, "X")
        n.set_execution_context(ctx)

        n.add_task(lambda: None)
        n.execute_tasks()
        n.execute_tasks()
        self.assertEqual(flags["X"], 2)
        self.assertEqual(ctx.calls, 2)

    def test_remove_edge_method_keeps_graph_consistent(self):
        dag = DirectedAcyclicWorkGraph()
        a, b, c = Node("A"), Node("B"), Node("C")
        for n in (a, b, c): dag.add_node(n)
        e1, e2 = Edge(a, b), Edge(a, c)
        dag.add_edge(e1); dag.add_edge(e2)
        dag.remove_edge(e1)
        self.assertIn(e2, dag.get_edges())
        self.assertNotIn(e1, dag.get_edges())
        self.assertNotIn(e1, a.get_outgoing_edges())
        self.assertNotIn(e1, b.get_incoming_edges())


if __name__ == "__main__":
    unittest.main()
