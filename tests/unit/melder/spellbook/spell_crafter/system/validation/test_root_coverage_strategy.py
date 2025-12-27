from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.validation.root_coverage_strategy import (
    RootCoverageStrategy,
)


def _blueprint(root_id: str, dag_nodes: list[str]) -> RootResolutionBlueprint:
    """
    Purpose:
        Build a minimal root blueprint for strategy tests.
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


def _node(spell_id: str, *, is_root: bool) -> SpellSystemNode:
    """
    Purpose:
        Build a minimal SpellSystemNode for index tests.
    Contract:
        Returns a node with the supplied root flag.
    Args:
        spell_id: Spell id for the node.
        is_root: Whether the node is marked as a root.
    Returns:
        SpellSystemNode: The constructed node.
    """
    return SpellSystemNode(
        spell_id=spell_id,
        lineage_id=f"lineage-{spell_id}",
        dependencies=set(),
        existence=None,
        spell_type=None,
        conduit_id=None,
        ward_id=None,
        is_root=is_root,
    )


def test_root_coverage_missing_root_in_index_includes_details():
    """
    Purpose:
        Verify missing-index roots include diagnostic details.
    Contract:
        Details include root_id and index node/root lists.
    Returns:
        None.
    Raises:
        AssertionError: If details are missing or incorrect.
    """
    strategy = RootCoverageStrategy()
    index = SpellSystemIndex()
    blueprints = {"root": _blueprint("root", ["root"])}
    diagnostics = []

    strategy.run(
        index=index,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert len(diagnostics) == 1
    detail = diagnostics[0].details
    assert detail["root_id"] == "root"
    assert detail["index_node_ids"] == []
    assert detail["index_root_ids"] == []


def test_root_coverage_root_not_marked_in_index_includes_details():
    """
    Purpose:
        Verify non-root index nodes include diagnostic details.
    Contract:
        Details include root_id and index root list context.
    Returns:
        None.
    Raises:
        AssertionError: If details are missing or incorrect.
    """
    strategy = RootCoverageStrategy()
    index = SpellSystemIndex()
    index.upsert_node(_node("root", is_root=False))
    blueprints = {"root": _blueprint("root", ["root"])}
    diagnostics = []

    strategy.run(
        index=index,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert len(diagnostics) == 1
    detail = diagnostics[0].details
    assert detail["root_id"] == "root"
    assert detail["node_is_root"] is False
    assert detail["index_root_ids"] == []


def test_root_coverage_missing_root_blueprint_includes_details():
    """
    Purpose:
        Verify missing blueprint roots include diagnostic details.
    Contract:
        Details include root_id and blueprint root list context.
    Returns:
        None.
    Raises:
        AssertionError: If details are missing or incorrect.
    """
    strategy = RootCoverageStrategy()
    index = SpellSystemIndex()
    index.upsert_node(_node("root", is_root=True))
    diagnostics = []

    strategy.run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert len(diagnostics) == 1
    detail = diagnostics[0].details
    assert detail["root_id"] == "root"
    assert detail["blueprint_root_ids"] == []
    assert detail["index_root_ids"] == ["root"]
