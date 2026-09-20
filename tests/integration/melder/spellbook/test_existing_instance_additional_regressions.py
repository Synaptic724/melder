"""Stock-runtime regressions for gaps confirmed by the existing-instance experiment.

These assertions require the corrected public behavior. They never install the
experiment's in-memory scanner changes. Annotation, sharing and scope failures
remain independently visible until their native repairs are implemented.
"""

from typing import TYPE_CHECKING

import pytest

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.spellbook import Spellbook
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    ExistingValue as SuppliedValue,
)
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    ValueConsumer,
)
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    instance_book as instance_book,
)

if TYPE_CHECKING:
    from tests.integration.melder.spellbook.test_existing_instance_planning import (
        ExistingValue,
    )


class RepeatedValueConsumer:
    """Two required parameters must retain the same registered instance."""

    def __init__(self, left: SuppliedValue, right: SuppliedValue) -> None:
        """Retain both references without constructing or taking ownership of the value."""
        self.left = left
        self.right = right


class DeferredValueConsumer:
    """Python 3.14 deferred annotation imports must remain valid consumer declarations."""

    def __init__(self, value: ExistingValue) -> None:
        """Retain a required dependency whose type exists only in TYPE_CHECKING imports."""
        self.value = value


class LinkedValueConsumer:
    """Declare a named contract that a real existing provider can satisfy."""

    def __init__(
            self,
            value: SuppliedValue = SpellContract(spellframe=SuppliedValue, binding_name="shared"),
    ) -> None:
        """Retain the provider's object without acquiring its cleanup responsibility."""
        self.value = value


def build_value_consumer(value: SuppliedValue) -> ValueConsumer:
    """A function provider may itself require an existing object as a dependency."""
    return ValueConsumer(value)


def test_existing_provider_satisfies_repeated_parameters(instance_book: Spellbook) -> None:
    """A repeated dependency must share the original object through both parameters."""
    supplied = SuppliedValue("shared")
    instance_book.bind(spell=supplied, existence="unique", spellframe=SuppliedValue)
    target = instance_book.bind(spell=RepeatedValueConsumer, existence="many")
    consumer = instance_book.conjure(dynamic=True).meld(spell_id=target)
    assert consumer.left is supplied and consumer.right is supplied


def test_existing_provider_can_be_injected_into_function(instance_book: Spellbook) -> None:
    """Function dependency planning must preserve the existing value without making it callable."""
    supplied = SuppliedValue("function-input")
    instance_book.bind(spell=supplied, existence="unique", spellframe=SuppliedValue)
    target = instance_book.bind(spell=build_value_consumer, existence="unique")
    consumer = instance_book.conjure(dynamic=True).meld(spell_id=target)
    assert consumer.value is supplied


def test_existing_provider_typechecking_annotation_does_not_raise_nameerror(instance_book: Spellbook) -> None:
    """Resolve a real required TYPE_CHECKING-only annotation without eager evaluation failure."""
    supplied = SuppliedValue("deferred-input")
    instance_book.bind(spell=supplied, existence="unique", spellframe=SuppliedValue)
    target = instance_book.bind(spell=DeferredValueConsumer, existence="many")
    consumer = instance_book.conjure(dynamic=True).meld(spell_id=target)
    assert consumer.value is supplied


@pytest.mark.parametrize("scope,existence", (
    ("lesser", "unique_per_conduit"), ("spellspace", "unique_per_spell_space"),
))
def test_existing_provider_survives_consumer_scope_release(
        instance_book: Spellbook, scope: str, existence: str,
) -> None:
    """Scoped consumer reuse and teardown must preserve the root-owned existing value."""
    supplied = SuppliedValue("scope-input")
    provider_id = instance_book.bind(spell=supplied, existence="unique", spellframe=SuppliedValue)
    target = instance_book.bind(spell=ValueConsumer, existence=existence)
    root = instance_book.conjure(dynamic=True)
    door = root.create_lesser_conduit() if scope == "lesser" else root.create_spellspace()
    try:
        first = door.meld(spell_id=target)
        assert door.meld(spell_id=target) is first
        assert first.value is supplied
    finally:
        door.cleanup()
    assert root.meld(spell_id=provider_id) is supplied


@pytest.mark.parametrize("contract", (False, True), ids=("annotation", "spell_contract"))
def test_existing_provider_is_injected_across_read_contract(
        instance_book: Spellbook, contract: bool,
) -> None:
    """Borrower construction and cleanup must retain the existing provider's exact identity."""
    supplied = SuppliedValue("linked-input")
    provider_id = instance_book.bind(
        spell=supplied, existence="unique", spellframe=SuppliedValue, binding_name="shared",
    )
    owner = instance_book.conjure(dynamic=True, name="owner")
    borrower_book = Spellbook(aetheric_frame="existing-instance-planning-regression")
    try:
        borrower = borrower_book.conjure(dynamic=True, name="borrower")
        assert borrower.link(owner)
        assert borrower.add_spell_to_contract(spell_id=provider_id, conduit=owner, permissions="read")
        target = borrower.bind(spell=LinkedValueConsumer if contract else ValueConsumer, existence="many")
        assert borrower.meld(spell_id=target).value is supplied
    finally:
        if not borrower_book.cleaned:
            if borrower_book.conduit is None:
                borrower_book.cleanup()
            else:
                borrower_book.conduit.cleanup()
    assert owner.meld(spell_id=provider_id) is supplied


@pytest.mark.parametrize("lookup", ("instance", "frame"))
def test_existing_root_public_lookup_preserves_identity(instance_book: Spellbook, lookup: str) -> None:
    """Keep actual object/frame lookup covered independently of the machine-ID controls."""
    supplied = SuppliedValue("lookup-input")
    instance_book.bind(spell=supplied, existence="unique", spellframe=SuppliedValue)
    root = instance_book.conjure(dynamic=True)
    found = root.meld(spell=supplied) if lookup == "instance" else root.meld(spellframe=SuppliedValue)
    assert found is supplied


@pytest.mark.parametrize("container", (list, dict))
def test_empty_existing_container_is_present(instance_book: Spellbook, container: type) -> None:
    """Existing falsey containers remain values; presence must not depend on truthiness."""
    supplied = container()
    target = instance_book.bind(spell=supplied, existence="unique", binding_name="empty")
    root = instance_book.conjure(dynamic=True)
    assert root.meld(spell_id=target) is supplied
    assert root.meld_existing_spell(spell=target) is supplied
