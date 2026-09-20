"""Both contract scanners must preserve their documented missing-provider error."""

from types import SimpleNamespace

import pytest

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_contract_processor_strategy import (
    SpellOccurrenceContractProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


@pytest.mark.parametrize("scanner_type", (
    SpellOccurrenceGraphAnalyzerStrategy, SpellOccurrenceContractProcessorStrategy,
))
def test_missing_provider_raises_contract_error(scanner_type: type) -> None:
    """A missing provider must produce MeldExecutionError, never an undefined-exception NameError."""
    consumer = SimpleNamespace(
        spell_index=SimpleNamespace(selected_spell_id="consumer"),
        spell_id="consumer", spell_name="Consumer",
    )
    book = SimpleNamespace(_lookup_contracted_spells={}, _contracted_spells={})
    contract = SpellContract(spellframe="missing-provider")
    try:
        with pytest.raises(MeldExecutionError, match="No contracted spell matched"):
            scanner_type()._resolve_spell_contract_spell_id(
                contract=contract, consumer_spell=consumer, param_name="dependency",
                spellbook=book, allow_missing=False,
            )
    finally:
        contract.cleanup()
