from __future__ import annotations

import pytest

from melder.aether.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.aether.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.aether.spellbook.spell_crafter.system.system_diagnostic import SystemDiagnostic
from melder.aether.spellbook.spell_crafter.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)


def _index(*spell_ids: str) -> SpellSystemIndex:
    """
    Purpose:
        Build a SpellSystemIndex populated with nodes for the provided ids.
    Contract:
        Inserts nodes in order without additional mutation.
    Args:
        spell_ids: Spell ids to insert into the index.
    Returns:
        SpellSystemIndex: The populated index.
    """
    idx = SpellSystemIndex()
    for spell_id in spell_ids:
        idx.upsert_node(
            SpellSystemNode(
                spell_id=spell_id,
                lineage_id=f"lineage-{spell_id}",
            )
        )
    return idx


def _blueprint(*, root_id: str, node_ids: tuple[str, ...]) -> dict[str, RootResolutionBlueprint]:
    """
    Purpose:
        Build a RootResolutionBlueprint with the provided node ids.
    Contract:
        Adds nodes without dependencies; order reflects insertion order.
    Args:
        root_id: Root id for the blueprint mapping.
        node_ids: Node ids to add to the DAG.
    Returns:
        dict[str, RootResolutionBlueprint]: Mapping containing the blueprint.
    """
    dag = DirectedAcyclicWorkGraph()
    for node_id in node_ids:
        dag.add_node(node_id)
    return {
        root_id: RootResolutionBlueprint(
            root_spell_id=root_id,
            root_lineage_id=f"lineage-{root_id}",
            dag=dag,
        )
    }


class _RecorderStrategy(SpellSystemValidationStrategy):
    """
    Purpose:
        Concrete strategy to record inputs for testing the base contract.
    Contract:
        Stores each run call and optionally appends a diagnostic.
    """

    def __init__(self, *, emit: bool = False) -> None:
        """
        Purpose:
            Initialize a recording strategy.
        Contract:
            Stores whether it should append a diagnostic when run is called.
        Args:
            emit: Whether to append a diagnostic during run.
        Returns:
            None.
        """
        self.calls: list[tuple] = []
        self._emit = emit

    def run(
        self,
        *,
        index: SpellSystemIndex,
        blueprints: dict[str, RootResolutionBlueprint],
        phase4_results: dict[str, object],
        broken_spell_ids: set[str],
        spell_system_states: object,
        spell_lookup: dict[str, object],
        diagnostics: list[SystemDiagnostic],
        cancel_event,
    ) -> None:
        """
        Purpose:
            Record the received inputs and optionally append a diagnostic.
        Contract:
            - Captures inputs in order of calls.
            - Appends a diagnostic only when emit is True.
        Args:
            index: SpellSystemIndex to record.
            blueprints: Blueprints mapping to record.
            phase4_results: Phase-4 results to record.
            broken_spell_ids: Broken spell ids to record.
            spell_system_states: Spell system states to record.
            spell_lookup: Spell lookup mapping to record.
            diagnostics: Diagnostics list to append into.
            cancel_event: Cancellation event to record.
        Returns:
            None.
        """
        self.calls.append(
            (
                index,
                blueprints,
                phase4_results,
                broken_spell_ids,
                spell_system_states,
                spell_lookup,
                diagnostics,
                cancel_event,
            )
        )
        if self._emit:
            diagnostics.append(SystemDiagnostic("rec", "recorded"))


def test_strategy_base_is_abstract() -> None:
    """
    Purpose:
        Ensure the abstract base cannot be instantiated.
    Contract:
        Instantiating SpellSystemValidationStrategy raises TypeError.
    Returns:
        None.
    Raises:
        AssertionError: If instantiation succeeds.
    """
    with pytest.raises(TypeError):
        SpellSystemValidationStrategy()


def test_subclass_without_run_is_abstract() -> None:
    """
    Purpose:
        Verify subclasses must implement run to be instantiated.
    Contract:
        Instantiating a subclass without run raises TypeError.
    Returns:
        None.
    Raises:
        AssertionError: If instantiation succeeds.
    """

    class _NoRunStrategy(SpellSystemValidationStrategy):
        """
        Purpose:
            Placeholder strategy with no run implementation.
        Contract:
            Remains abstract because run is not implemented.
        """

    with pytest.raises(TypeError):
        _NoRunStrategy()


def test_concrete_strategy_records_inputs() -> None:
    """
    Purpose:
        Ensure a concrete strategy receives and records all inputs.
    Contract:
        run captures the provided objects without modification.
    Returns:
        None.
    Raises:
        AssertionError: If recorded inputs do not match.
    """
    strategy = _RecorderStrategy()
    idx = _index("a")
    blueprints = _blueprint(root_id="root", node_ids=("a",))
    phase4_results = {"a": object()}
    broken = {"b"}
    diags: list[SystemDiagnostic] = []
    spell_system_states = object()
    spell_lookup: dict[str, object] = {}
    cancel = object()

    strategy.run(
        index=idx,
        blueprints=blueprints,
        phase4_results=phase4_results,
        broken_spell_ids=broken,
        spell_system_states=spell_system_states,
        spell_lookup=spell_lookup,
        diagnostics=diags,
        cancel_event=cancel,
    )

    assert strategy.calls
    assert strategy.calls[0] == (
        idx,
        blueprints,
        phase4_results,
        broken,
        spell_system_states,
        spell_lookup,
        diags,
        cancel,
    )


def test_concrete_strategy_can_append_diagnostics() -> None:
    """
    Purpose:
        Validate a concrete strategy can append diagnostics during run.
    Contract:
        Diagnostics list includes the appended SystemDiagnostic.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic is missing.
    """
    strategy = _RecorderStrategy(emit=True)
    diags: list[SystemDiagnostic] = []

    strategy.run(
        index=_index("a"),
        blueprints=_blueprint(root_id="root", node_ids=("a",)),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )

    assert len(diags) == 1
    assert diags[0].code == "rec"
