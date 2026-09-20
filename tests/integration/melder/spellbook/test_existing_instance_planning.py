"""Existing values stay opaque through both contract planners and dependency walks.

Native minimal cases complement the unchanged real Iris/ActivityBootstrap
acceptance test; no factory wrappers are used to make existing values callable.
"""

from collections.abc import Iterator
from typing import Union

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_contract_processor_strategy import (
    SpellOccurrenceContractProcessorStrategy,
)


class ExistingValue:
    """A deliberately non-callable supplied object, not a constructor request."""

    def __init__(self, marker: str) -> None:
        """Receive required constructor input before the object is bound to Melder."""
        self.marker = marker


class ValueConsumer:
    """Borrow an existing non-callable object through ordinary type-hint DI."""

    def __init__(self, value: ExistingValue) -> None:
        """Retain the exact supplied value without acquiring its lifecycle."""
        self.value = value


class NestedValueConsumer:
    """Place the non-callable existing value at a transitive dependency position."""

    def __init__(self, child: ValueConsumer) -> None:
        """Retain the constructed child and its borrowed existing value."""
        self.child = child


class CollectionValueConsumer:
    """Request registered existing values as a collection."""

    def __init__(self, values: list[ExistingValue]) -> None:
        """Retain the injected collection and its original element identities."""
        self.values = values


class MappedValueConsumer:
    """Select an existing object through explicit frame and binding names."""

    def __init__(
            self,
            value: Union[ExistingValue, SpellMap] = SpellMap(
                spellframe="named-values", binding_name="chosen",
            ),
    ) -> None:
        """Retain the exact explicitly selected object."""
        self.value = value


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


@pytest.mark.parametrize("planner_type", (
    SpellOccurrenceGraphAnalyzerStrategy, SpellOccurrenceContractProcessorStrategy,
))
def test_existing_values_expose_no_constructor_contracts_to_either_planner(
        instance_book: Spellbook,
        planner_type: type,
) -> None:
    """Use real bound Spell inputs to guard both otherwise-identical planner defects."""
    supplied = ExistingValue("supplied-before-bind")
    spell_id = instance_book.bind(spell=supplied, existence="unique")
    spell = instance_book._spell_id_pool[spell_id]
    assert spell.is_existing_creation
    assert tuple(planner_type._iter_spell_contract_defaults(spell)) == ()


@pytest.mark.parametrize("registration", ("unqualified", "typed", "named"))
def test_existing_value_root_returns_original_without_factory_execution(
        instance_book: Spellbook,
        registration: str,
) -> None:
    """Guard the already-supported direct existing-object root path."""
    supplied = ExistingValue("supplied-before-bind")
    spell_id = instance_book.bind(
        spell=supplied, existence="unique",
        spellframe=ExistingValue if registration == "typed" else "named-values" if registration == "named" else None,
        binding_name="chosen" if registration == "named" else None,
    )
    root = instance_book.conjure(dynamic=True)
    assert root.meld(spell_id=spell_id) is supplied


def test_existing_value_dependency_retains_identity_without_contract_inspection(
        instance_book: Spellbook,
) -> None:
    """Construct a real dependent root without inspecting the supplied dependency as callable."""
    supplied = ExistingValue("supplied-before-bind")
    instance_book.bind(spell=supplied, existence="unique", spellframe=ExistingValue)
    consumer_id = instance_book.bind(spell=ValueConsumer, existence="many")
    root = instance_book.conjure(dynamic=True)
    assert root.meld(spell_id=consumer_id).value is supplied


def test_existing_value_transitive_dependency_retains_identity(instance_book: Spellbook) -> None:
    """A second dependency level must still end at the exact supplied object."""
    supplied = ExistingValue("supplied-before-bind")
    instance_book.bind(spell=supplied, existence="unique", spellframe=ExistingValue)
    instance_book.bind(spell=ValueConsumer, existence="many")
    root_id = instance_book.bind(spell=NestedValueConsumer, existence="many")
    root = instance_book.conjure(dynamic=True)
    assert root.meld(spell_id=root_id).child.value is supplied


def test_existing_values_in_collection_retain_identity(instance_book: Spellbook) -> None:
    """Collection planning must not discover constructors on existing elements."""
    supplied = ExistingValue("supplied-before-bind")
    instance_book.bind(spell=supplied, existence="unique", spellframe=ExistingValue)
    consumer_id = instance_book.bind(spell=CollectionValueConsumer, existence="many")
    root = instance_book.conjure(dynamic=True)
    values = root.meld(spell_id=consumer_id).values
    assert len(values) == 1 and values[0] is supplied


def test_explicit_map_injects_existing_value(instance_book: Spellbook) -> None:
    """An explicit named lookup must inject the registered object without signature inspection."""
    supplied = ExistingValue("supplied-before-bind")
    instance_book.bind(
        spell=supplied, existence="unique", spellframe="named-values", binding_name="chosen",
    )
    consumer_id = instance_book.bind(spell=MappedValueConsumer, existence="many")
    root = instance_book.conjure(dynamic=True)
    assert root.meld(spell_id=consumer_id).value is supplied


def test_late_bound_consumer_injects_existing_value(instance_book: Spellbook) -> None:
    """An existing provider remains a value when its dependent is bound after conjure."""
    supplied = ExistingValue("supplied-before-bind")
    instance_book.bind(spell=supplied, existence="unique", spellframe=ExistingValue)
    root = instance_book.conjure(dynamic=True)
    consumer_id = instance_book.bind(spell=ValueConsumer, existence="many")
    assert root.meld(spell_id=consumer_id).value is supplied
