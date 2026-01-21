from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.validation.root_reachability_strategy import (
    RootReachabilityStrategy,
)


def _blueprint(root_id: str, dag_nodes: list[str]) -> RootResolutionBlueprint:
    """
    Purpose:
        Build a minimal root blueprint for reachability tests.
    Contract:
        Produces a blueprint with the supplied DAG nodes.
    Args:
        root_id: Root spell id for the blueprint.
        dag_nodes: Node ids to register in the DAG.
    Returns:
        RootResolutionBlueprint: The constructed blueprint.
    """
    dag = DirectedAcyclicWorkGraph()
    for node_id in dag_nodes:
        dag.add_node(node_id)
    return RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=f"lineage-{root_id}",
        dag=dag,
    )


def test_root_reachability_missing_root_in_dag_includes_details():
    """
    Purpose:
        Verify missing-root DAG diagnostics include node context.
    Contract:
        Details include dag_nodes and dag_node_count.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostic details are incomplete.
    """
    strategy = RootReachabilityStrategy()
    index = SpellSystemIndex()
    blueprints = {"root": _blueprint("root", ["other"])}
    diagnostics = []

    strategy.run(
        index=index,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert len(diagnostics) == 1
    detail = diagnostics[0].details
    assert detail["root_id"] == "root"
    assert detail["dag_node_count"] == 1
    assert detail["dag_nodes"] == ["other"]


def test_root_reachability_orphan_nodes_include_reachable_details():
    """
    Purpose:
        Verify orphan-node diagnostics include reachable-node context.
    Contract:
        Details include reachable_nodes and reachable_node_count.
    Returns:
        None.
    Raises:
        AssertionError: If reachable-node details are missing.
    """
    strategy = RootReachabilityStrategy()
    index = SpellSystemIndex()
    blueprints = {"root": _blueprint("root", ["root", "orphan"])}
    diagnostics = []

    strategy.run(
        index=index,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert len(diagnostics) == 1
    detail = diagnostics[0].details
    assert detail["root_id"] == "root"
    assert detail["spell_id"] == "orphan"
    assert detail["reachable_node_count"] == 1
    assert detail["reachable_nodes"] == ["root"]
