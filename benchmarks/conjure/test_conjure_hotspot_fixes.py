from typing import Dict, List, Tuple

from melder.spellbook.spell_crafter.blueprints.occurrence_plan import (
    OccurrencePlanBuilder,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


def test_occurrence_plan_execution_order_linear_chain() -> None:
    """
    Purpose:
        Ensure execution order remains topologically correct for a simple chain.
    Contract:
        - Dependencies appear before dependents in the order output.
        - Linear chains preserve the only valid topological order.
    Returns:
        None.
    """
    occurrence_graph: Dict[Tuple[str, Tuple[str, ...]], Dict[str, List[Tuple[str, Tuple[str, ...]]]]] = {
        ("C", ()): {"dep": [("B", ())]},
        ("B", ()): {"dep": [("A", ())]},
        ("A", ()): {},
    }

    order = OccurrencePlanBuilder._build_execution_order(
        occurrence_graph=occurrence_graph,
        fallback_order=[],
    )

    assert order == ["A", "B", "C"]


def test_dag_index_exact_path_lookup_accepts_list_and_tuple() -> None:
    """
    Purpose:
        Verify DagIndex exact-path lookups work with list and tuple inputs.
    Contract:
        - Tuple path and list path resolve to the same sockets.
        - Single-segment paths resolve as expected.
    Returns:
        None.
    """
    index = DagIndex()
    deep_socket = SocketRef(
        node_id="root",
        param_name="repo",
        param_path=("left", "repo"),
        socket_kind=SocketKind.NORMAL,
    )
    shallow_socket = SocketRef(
        node_id="root",
        param_name="left",
        param_path=("left",),
        socket_kind=SocketKind.NORMAL,
    )

    index.add_socket(deep_socket)
    index.add_socket(shallow_socket)

    tuple_matches = index.get_by_exact_path(("left", "repo"))
    list_matches = index.get_by_exact_path(["left", "repo"])
    shallow_matches = index.get_by_exact_path(["left"])

    assert deep_socket in tuple_matches
    assert deep_socket in list_matches
    assert shallow_socket in shallow_matches
