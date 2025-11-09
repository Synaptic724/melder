# tests/dag/test_dag_core_2.py
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

# ---------------- Test doubles ----------------

class FlagContext(ExecutionContext):
    def __init__(self, state: StateObject, node_id: str, store: dict):
        super().__init__(state)
        self.node_id = node_id
        self.store = store
        self.exec_count = 0

    def execute(self):
        self.exec_count += 1
        self.store[self.node_id] = self.store.get(self.node_id, 0) + 1
        if self.state:
            self.state.register_node_result(self.node_id, True)

class BoomContext(ExecutionContext):
    def __init__(self, state: StateObject, node_id: str):
        super().__init__(state)
        self.node_id = node_id

    def execute(self):
        if self.state:
            self.state.register_node_result(self.node_id, False)

# ---------------- Tests ----------------

class TestNodeAPI(unittest.TestCase):
    def test_incoming_outgoing_are_copies(self):
        a, b = Node("A"), Node("B")
        e = Edge(a, b)
        a.add_outgoing_edge(e)
        b.add_incoming_edge(e)
        outs = a.get_outgoing_edges()
        ins = b.get_incoming_edges()
        outs.clear()
        ins.clear()
        self.assertEqual(len(a.get_outgoing_edges()), 1)
        self.assertEqual(len(b.get_incoming_edges()), 1)

    def test_add_task_and_execute_runs_all(self):
        n = Node("N")
        seq = []
        n.add_task(lambda: seq.append(1))
        n.add_task(lambda: seq.append(2))
        n.execute_tasks()
        self.assertEqual(seq, [1, 2])

    def test_execute_internal_follows_first_outgoing_only(self):
        a, b, c = Node("A"), Node("B"), Node("C")
        e1, e2 = Edge(a, b), Edge(a, c)
        a.add_outgoing_edge(e1); b.add_incoming_edge(e1)
        a.add_outgoing_edge(e2); c.add_incoming_edge(e2)
        seq = []
        a.add_task(lambda: seq.append("A"))
        b.add_task(lambda: seq.append("B"))
        c.add_task(lambda: seq.append("C"))
        a.execute(execute_internally=True)
        self.assertIn("A", seq)
        # Only one branch must be followed
        self.assertTrue(("B" in seq) ^ ("C" in seq))

    def test_set_get_context_none_by_default(self):
        n = Node("X")
        self.assertIsNone(n.get_execution_context())

    def test_node_cleanup_is_idempotent(self):
        n = Node("N")
        n.add_task(lambda: None)
        n.cleanup()
        n.cleanup()  # no crash
        self.assertEqual(n._tasks, [])
        self.assertIsNone(n._execution_context)

    def test_find_target_node_by_id(self):
        a, b = Node("A"), Node("B")
        e = Edge(a, b)
        a.add_outgoing_edge(e); b.add_incoming_edge(e)
        self.assertIs(a.find_target_node("B"), b)
        self.assertIsNone(a.find_target_node("Z"))


class TestEdgeAPI(unittest.TestCase):
    def test_edge_cleanup_clears_references(self):
        a, b = Node("A"), Node("B")
        e = Edge(a, b)
        e.cleanup()
        self.assertIsNone(e.from_node)
        self.assertIsNone(e.to_node)
        # idempotent
        e.cleanup()

    def test_remove_edge_when_not_in_graph_is_safe(self):
        dag = DirectedAcyclicWorkGraph()
        a, b = Node("A"), Node("B")
        dag.add_node(a); dag.add_node(b)
        e = Edge(a, b)
        dag.remove_edge(e)  # not added; should not crash
        self.assertEqual(dag.get_edges(), [])


class TestDAGAddRemove(unittest.TestCase):
    def test_add_edge_only_when_nodes_present(self):
        dag = DirectedAcyclicWorkGraph()
        a, b = Node("A"), Node("B")
        e = Edge(a, b)
        dag.add_edge(e)  # no nodes yet
        self.assertEqual(dag.get_edges(), [])
        dag.add_node(a)
        dag.add_node(b)
        dag.add_edge(e)
        self.assertEqual(len(dag.get_edges()), 1)

    def test_duplicate_node_id_is_ignored(self):
        dag = DirectedAcyclicWorkGraph()
        a1 = Node("A")
        a2 = Node("A")
        dag.add_node(a1)
        dag.add_node(a2)  # ignored
        self.assertIs(dag.find_node_by_id("A"), a1)

    def test_remove_absent_node_is_safe(self):
        dag = DirectedAcyclicWorkGraph()
        x = Node("X")
        dag.remove_node(x)  # no crash
        self.assertEqual(dag.get_nodes(), [])

    def test_get_nodes_edges_return_copies(self):
        dag = DirectedAcyclicWorkGraph()
        a, b = Node("A"), Node("B")
        dag.add_node(a); dag.add_node(b)
        e = Edge(a, b); dag.add_edge(e)
        nodes = dag.get_nodes(); edges = dag.get_edges()
        nodes.clear(); edges.clear()
        self.assertEqual(len(dag.get_nodes()), 2)
        self.assertEqual(len(dag.get_edges()), 1)

    def test_generate_dot_file_empty_graph(self):
        dag = DirectedAcyclicWorkGraph()
        with tempfile.TemporaryDirectory() as td:
            fp = os.path.join(td, "empty.dot")
            dag.generate_dot_file(fp)
            with open(fp, "r") as f:
                txt = f.read()
            self.assertIn("digraph G", txt)

    def test_generate_dot_file_with_special_ids(self):
        dag = DirectedAcyclicWorkGraph()
        a, b = Node('A "quote"'), Node("B->C")
        dag.add_node(a); dag.add_node(b)
        dag.add_edge(Edge(a, b))
        with tempfile.TemporaryDirectory() as td:
            fp = os.path.join(td, "spec.dot")
            dag.generate_dot_file(fp)
            with open(fp, "r") as f:
                txt = f.read()
            self.assertIn('"A "quote"" -> "B->C";', txt)


class TestTopology(unittest.TestCase):
    def test_toposort_disconnected_components(self):
        dag = DirectedAcyclicWorkGraph()
        a, b, c = Node("A"), Node("B"), Node("C")
        for n in (a, b, c): dag.add_node(n)
        dag.add_edge(Edge(a, b))
        order_ids = [n.id for n in dag.topological_sort()]
        self.assertCountEqual(order_ids, ["A", "B", "C"])
        self.assertLess(order_ids.index("A"), order_ids.index("B"))

    def test_toposort_diamond(self):
        dag = DirectedAcyclicWorkGraph()
        a, b, c, d = Node("A"), Node("B"), Node("C"), Node("D")
        for n in (a, b, c, d): dag.add_node(n)
        dag.add_edge(Edge(a, b)); dag.add_edge(Edge(a, c))
        dag.add_edge(Edge(b, d)); dag.add_edge(Edge(c, d))
        order = [n.id for n in dag.topological_sort()]
        self.assertEqual(order[0], "A")
        self.assertEqual(order[-1], "D")

    def test_toposort_single_node(self):
        dag = DirectedAcyclicWorkGraph()
        x = Node("X")
        dag.add_node(x)
        order = [n.id for n in dag.topological_sort()]
        self.assertEqual(order, ["X"])

    def test_toposort_cycle_self_edge_detects(self):
        dag = DirectedAcyclicWorkGraph()
        a = Node("A"); dag.add_node(a)
        e = Edge(a, a)
        dag.add_edge(e)
        with self.assertRaises(ValueError):
            dag.topological_sort()


class TestExecution(unittest.TestCase):
    def test_execute_respects_topological_order(self):
        dag = DirectedAcyclicWorkGraph()
        a, b, c = Node("A"), Node("B"), Node("C")
        seq = []
        a.add_task(lambda: seq.append("A"))
        b.add_task(lambda: seq.append("B"))
        c.add_task(lambda: seq.append("C"))
        for n in (a, b, c): dag.add_node(n)
        dag.add_edge(Edge(a, b)); dag.add_edge(Edge(b, c))
        dag.execute()
        self.assertEqual(seq, ["A", "B", "C"])

    def test_execute_layered_multi_roots(self):
        dag = DirectedAcyclicWorkGraph()
        a, b, c = Node("A"), Node("B"), Node("C")
        seq = []
        for n, tag in [(a, "A"), (b, "B"), (c, "C")]:
            n.add_task(lambda t=tag: seq.append(t))
        dag.add_node(a); dag.add_node(b); dag.add_node(c)
        dag.add_edge(Edge(a, c)); dag.add_edge(Edge(b, c))
        dag.execute_layered()
        self.assertEqual(seq[-1], "C")
        self.assertCountEqual(seq[:-1], ["A", "B"])

    def test_execute_with_contexts(self):
        dag = DirectedAcyclicWorkGraph()
        s = StateObject(dag)
        store = {}
        a, b = Node("A"), Node("B")
        a.set_execution_context(FlagContext(s, "A", store))
        b.set_execution_context(FlagContext(s, "B", store))
        dag.add_node(a); dag.add_node(b)
        dag.add_edge(Edge(a, b))
        dag.execute()
        self.assertEqual(store["A"], 1)
        self.assertEqual(store["B"], 1)
        self.assertEqual(s.get_status("A"), "SUCCESS")
        self.assertEqual(s.get_status("B"), "SUCCESS")

    def test_execute_with_failing_context_removes_node(self):
        dag = DirectedAcyclicWorkGraph()
        s = StateObject(dag)
        a = Node("A"); dag.add_node(a)
        a.set_execution_context(BoomContext(s, "A"))
        dag.execute()  # topo includes A, which fails in its context
        self.assertEqual(s.get_status("A"), "FAILED")
        self.assertIsNone(dag.find_node_by_id("A"))

    def test_execute_no_tasks_no_context_no_crash(self):
        dag = DirectedAcyclicWorkGraph()
        a = Node("A"); dag.add_node(a)
        dag.execute()  # should not crash

    def test_dag_cleanup_is_idempotent(self):
        dag = DirectedAcyclicWorkGraph()
        a, b = Node("A"), Node("B")
        dag.add_node(a); dag.add_node(b)
        dag.add_edge(Edge(a, b))
        dag.cleanup()
        dag.cleanup()
        self.assertEqual(dag.get_nodes(), [])
        self.assertEqual(dag.get_edges(), [])


class TestStateAndContextManager(unittest.TestCase):
    def test_state_multiple_records(self):
        dag = DirectedAcyclicWorkGraph()
        s = StateObject(dag)
        s.register_node_result("X", True)
        s.register_node_result("Y", False)
        statuses = s.get_all_statuses()
        self.assertEqual(statuses["X"], "SUCCESS")
        self.assertEqual(statuses["Y"], "FAILED")

    def test_execution_context_as_with_statement(self):
        dag = DirectedAcyclicWorkGraph()
        s = StateObject(dag)
        store = {}
        with FlagContext(s, "Z", store) as ctx:
            ctx.execute()
        # __exit__ calls cleanup
        self.assertIsNone(ctx.state)
        self.assertEqual(store["Z"], 1)

    def test_context_cleanup_idempotent(self):
        dag = DirectedAcyclicWorkGraph()
        s = StateObject(dag)
        ctx = FlagContext(s, "Q", {})
        ctx.cleanup()
        ctx.cleanup()
        self.assertIsNone(ctx.state)

    def test_state_cleanup_idempotent(self):
        dag = DirectedAcyclicWorkGraph()
        s = StateObject(dag)
        s.cleanup()
        s.cleanup()
        self.assertTrue(True)  # no crash


if __name__ == "__main__":
    unittest.main()
