"""
Signature-lock component tests for DirectedAcyclicWorkGraph.add_dependency.

These exist because a caller (the S4 restore plan compiler) invoked
add_dependency with a phantom `depends_on=` keyword that never existed on
the real signature - it raised TypeError on every call and red-ran the
parallel_restore_ulid_identity suite. The real contract is
add_dependency(parent_key, child_key, *, param_name=None, socket_kind=None)
where child depends on parent (parent is processed first). This suite pins
that contract, including a direct assertion that the retired `depends_on=`
kwarg is rejected, so the guess can never come back silently.
"""
import pytest

from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind


def test_positional_parent_child_orders_parent_first_in_sort() -> None:
    """
    Purpose:
        Verify the positional (parent_key, child_key) contract: the child
        depends on the parent, so the parent sorts first.
    Contract:
        topological_sort yields the parent node before the child node.
    Returns:
        None.
    Raises:
        AssertionError: If child/parent order inverts.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child")
    order = [node.id for node in dag.topological_sort()]
    assert order.index("parent") < order.index("child")
    dag.cleanup()


def test_positional_parent_child_places_parent_in_a_lower_level() -> None:
    """
    Purpose:
        Verify the same direction under topological_levels (the S4 flatten
        surface).
    Contract:
        The parent's level index is strictly below the child's.
    Returns:
        None.
    Raises:
        AssertionError: If the level placement inverts the edge.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child")
    levels = dag.topological_levels()
    index = {node.id: i for i, level in enumerate(levels) for node in level}
    assert index["parent"] < index["child"]
    dag.cleanup()


def test_retired_depends_on_keyword_is_rejected() -> None:
    """
    Purpose:
        Lock the exact REOPEN regression: the phantom `depends_on=` kwarg
        must raise, never silently accept.
    Contract:
        add_dependency(child, depends_on=parent) raises TypeError for the
        unexpected keyword argument.
    Returns:
        None.
    Raises:
        AssertionError: If the retired kwarg is ever accepted.
    """
    dag = DirectedAcyclicWorkGraph()
    # Route the phantom keyword through a dict so the static checker
    # cannot flag it; the runtime rejection is exactly what we assert.
    retired_kwarg = {"depends_on": "parent"}
    with pytest.raises(TypeError):
        dag.add_dependency("child", **retired_kwarg)
    dag.cleanup()


def test_param_name_keyword_is_accepted_and_edge_recorded() -> None:
    """
    Purpose:
        Verify the real optional `param_name` keyword is accepted and the
        edge is still wired.
    Contract:
        add_dependency(parent, child, param_name="dep") does not raise and
        the dependency orders parent first.
    Returns:
        None.
    Raises:
        AssertionError: If the keyword is rejected or the edge is missing.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child", param_name="dep")
    order = [node.id for node in dag.topological_sort()]
    assert order.index("parent") < order.index("child")
    dag.cleanup()


def test_socket_kind_keyword_is_accepted_and_edge_recorded() -> None:
    """
    Purpose:
        Verify the real optional `socket_kind` keyword is accepted and the
        edge is still wired.
    Contract:
        add_dependency(parent, child, socket_kind=SocketKind.NORMAL) does
        not raise and the dependency orders parent first.
    Returns:
        None.
    Raises:
        AssertionError: If the keyword is rejected or the edge is missing.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("parent", "child", socket_kind=SocketKind.NORMAL)
    order = [node.id for node in dag.topological_sort()]
    assert order.index("parent") < order.index("child")
    dag.cleanup()


def test_empty_parent_key_refuses() -> None:
    """
    Purpose:
        Verify the on-demand node creation still guards empty keys.
    Contract:
        add_dependency("", "child") raises ValueError naming the empty-key
        rule.
    Returns:
        None.
    Raises:
        AssertionError: If an empty key is accepted.
    """
    dag = DirectedAcyclicWorkGraph()
    with pytest.raises(ValueError, match="empty"):
        dag.add_dependency("", "child")
    dag.cleanup()


def test_nodes_are_created_on_demand_by_add_dependency() -> None:
    """
    Purpose:
        Verify add_dependency materializes both endpoint nodes if they do
        not already exist (the plan compiler relies on this).
    Contract:
        After one add_dependency over fresh keys, both nodes are present in
        the graph.
    Returns:
        None.
    Raises:
        AssertionError: If either endpoint node is missing.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency("fresh_parent", "fresh_child")
    assert dag.get_node("fresh_parent") is not None
    assert dag.get_node("fresh_child") is not None
    dag.cleanup()
