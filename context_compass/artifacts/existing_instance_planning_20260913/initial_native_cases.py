"""Existing values stay opaque through both contract planners and dependency walks.

Native minimal cases complement the unchanged real Iris/ActivityBootstrap
acceptance test; no factory wrappers are used to make existing values callable.
"""

from collections.abc import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_contract_processor_strategy import (
    SpellOccurrenceContractProcessorStrategy,
)


class ExistingValue:
    """A deliberately non-callable supplied object, not a constructor request."""

    def __init__(self) -> None:
        """Initialize a resource-free marker for the existing-value contract."""
        self.marker = "existing-value"


class CallableExistingValue:
    """A supplied callable whose call signature must not become constructor DI."""

    def __call__(self, ignored: object = SpellContract(spellframe="unrelated-call-input")) -> None:
        """Refuse factory execution; the contract default belongs only to explicit caller use."""
        raise AssertionError("An existing callable must not be executed as a factory.")


class ValueConsumer:
    """Borrow an existing non-callable object through ordinary type-hint DI."""

    def __init__(self, value: ExistingValue) -> None:
        """Retain the exact supplied value without acquiring its lifecycle."""
        self.value = value


class CallableValueConsumer:
    """Borrow an existing callable as an object rather than invoking it."""

    def __init__(self, value: CallableExistingValue) -> None:
        """Retain the exact callable object without calling its method."""
        self.value = value


class NestedValueConsumer:
    """Place the non-callable existing value at a transitive dependency position."""

    def __init__(self, child: ValueConsumer) -> None:
        """Retain the constructed child and its borrowed existing value."""
        self.child = child


@pytest.fixture
def instance_book() -> Iterator[Spellbook]:
    """Own an isolated dynamic book, disable disk cache and clean every runtime allocation."""
    Aether._reset_singleton_for_tests()
    world = Aether()
    Spellbook._aether = world
    Conduit._aether = world
    book = Spellbook(aetheric_frame="existing-instance-planning-regression")
    try:
        book.configure_aether_frame(
            system_state="dynamic", system_caching_enabled=False,
            disposal=None, disposal_method_names=None,
        )
        yield book
    finally:
        try:
            if not book.cleaned:
                if book.conduit is None:
                    book.cleanup()
                else:
                    book.conduit.cleanup()
        finally:
            Aether._reset_singleton_for_tests()
            world = Aether()
            Spellbook._aether = world
            Conduit._aether = world


@pytest.mark.parametrize("value_type", (ExistingValue, CallableExistingValue))
@pytest.mark.parametrize("planner_type", (
    SpellOccurrenceGraphAnalyzerStrategy, SpellOccurrenceContractProcessorStrategy,
))
def test_existing_values_expose_no_constructor_contracts_to_either_planner(
        instance_book: Spellbook,
        value_type: type,
        planner_type: type,
) -> None:
    """Use real bound Spell inputs to guard both otherwise-identical planner defects."""
    supplied = value_type()
    spell_id = instance_book.bind(spell=supplied, existence="unique")
    spell = instance_book._spell_id_pool[spell_id]
    assert spell.is_existing_creation
    assert tuple(planner_type._iter_spell_contract_defaults(spell)) == ()


@pytest.mark.parametrize("value_type", (ExistingValue, CallableExistingValue))
def test_existing_value_root_returns_original_without_factory_execution(
        instance_book: Spellbook,
        value_type: type,
) -> None:
    """Guard the already-supported direct existing-object root path."""
    supplied = value_type()
    spell_id = instance_book.bind(spell=supplied, existence="unique")
    root = instance_book.conjure(dynamic=True)
    assert root.meld(spell_id=spell_id) is supplied


@pytest.mark.parametrize("value_type,consumer_type", (
    (ExistingValue, ValueConsumer), (CallableExistingValue, CallableValueConsumer),
))
def test_existing_value_dependency_retains_identity_without_contract_inspection(
        instance_book: Spellbook,
        value_type: type,
        consumer_type: type,
) -> None:
    """Construct a real dependent root without inspecting the supplied dependency as callable."""
    supplied = value_type()
    instance_book.bind(spell=supplied, existence="unique")
    consumer_id = instance_book.bind(spell=consumer_type, existence="many")
    root = instance_book.conjure(dynamic=True)
    assert root.meld(spell_id=consumer_id).value is supplied


def test_existing_value_transitive_dependency_retains_identity(instance_book: Spellbook) -> None:
    """A second dependency level must still end at the exact supplied object."""
    supplied = ExistingValue()
    instance_book.bind(spell=supplied, existence="unique")
    instance_book.bind(spell=ValueConsumer, existence="many")
    root_id = instance_book.bind(spell=NestedValueConsumer, existence="many")
    root = instance_book.conjure(dynamic=True)
    assert root.meld(spell_id=root_id).child.value is supplied
