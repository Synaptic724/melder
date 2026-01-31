from typing import Any, Dict, List, Set, Tuple

from melder.spellbook.spell_crafter.blueprints.injection_plan import (
    InjectionPlanBuilder,
)
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import (
    OccurrencePlan,
)
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


def test_injection_plan_missing_contract_overrides_defaults_empty() -> None:
    """
    Purpose:
        Ensure InjectionPlanBuilder treats missing contract override entries as empty payloads.
    Contract:
        - Missing contract_overrides_by_occurrence entries resolve to None payloads.
        - InjectionPlan still builds for shared root occurrences.
    Returns:
        None.
    """
    occurrence_graph: Dict[Tuple[str, Tuple[str, ...]], Dict[str, List[Tuple[str, Tuple[str, ...]]]]] = {
        ("root", ()): {},
    }
    execution_order = ["root"]
    instance_keys_by_spell_id = {"root": [("root", None)]}
    canonical_occurrences_by_spell_id = {"root": ("root", ())}
    root_instance_key = ("root", None)
    shared_spell_ids: Set[str] = {"root"}
    contract_overrides_by_occurrence: Dict[Tuple[str, Tuple[str, ...]], Dict[str, Any]] = {}
    contract_overrides_by_spell_id: Dict[str, List[Tuple[Tuple[str, Tuple[str, ...]], Dict[str, Any]]]] = {}

    plan = OccurrencePlan(
        root_spell_id="root",
        occurrence_graph=occurrence_graph,
        execution_order=execution_order,
        instance_keys_by_spell_id=instance_keys_by_spell_id,
        canonical_occurrences_by_spell_id=canonical_occurrences_by_spell_id,
        root_instance_key=root_instance_key,
        shared_spell_ids=shared_spell_ids,
        contract_overrides_by_occurrence=contract_overrides_by_occurrence,
        contract_overrides_by_spell_id=contract_overrides_by_spell_id,
        contract_dependencies_complete=True,
    )
    builder = InjectionPlanBuilder(occurrence_plan=plan)
    injection_plan = builder.build()

    injection_spec = injection_plan.instance_injections[root_instance_key]
    assert injection_spec.contract_payload is None
