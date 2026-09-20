"""Preserve supplied Protocol references through real compiler and contract paths."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Union

import pytest

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spellbook import Spellbook
from tests.component.melder.spellbook.test_existing_instance_protocol_admission import (
    InheritedReader,
    InstanceOnlyReader,
    ReaderConsumer,
    ReaderContract,
    ValidReader,
)
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    instance_book as instance_book,
)

if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit


class ReaderCollection:
    """Receive registered Protocol providers through collection DI."""

    def __init__(self, readers: list[ReaderContract]) -> None:
        """Borrow the resolved references without adopting their cleanup custody."""
        self.readers = readers


class MappedReaderConsumer:
    """Select the supplied provider through a named SpellMap socket."""

    def __init__(
            self,
            reader: Union[ReaderContract, SpellMap] = SpellMap(
                spellframe=ReaderContract, binding_name="primary",
            ),
    ) -> None:
        """Retain the exact resolved value for identity and member-use checks."""
        self.reader = reader


class ContractReaderConsumer:
    """Select the supplied provider across a real conduit link."""

    def __init__(
            self,
            reader: Union[ReaderContract, SpellContract] = SpellContract(
                spellframe=ReaderContract, binding_name="primary",
            ),
    ) -> None:
        """Borrow the contracted reference without acquiring its lifecycle."""
        self.reader = reader


@contextmanager
def consumer_runtime(
        owner_book: Spellbook, provider_id: str, path: str,
) -> Iterator[tuple[Conduit, str]]:
    """Create a consumer through public APIs and own any additional borrower.

    Contract: the imported fixture owns the source world. The contract route
    grants the provider inside the native link transaction and cleans the
    borrower in finally. No compiler stage or admission check is replaced.

    Args:
        owner_book: Isolated book containing the supplied provider.
        provider_id: Provider identifier to grant on the contract route.
        path: annotation, collection, map or contract consumer route.

    Yields:
        Runtime conduit and the selected consumer's spell identifier.
    """
    if path == "contract":
        owner = owner_book.conjure(dynamic=True, name="owner")
        borrower_book = Spellbook(aetheric_frame=owner_book._aetheric_frame_name)
        consumer_id = borrower_book.bind(spell=ContractReaderConsumer, existence="many")
        borrower = borrower_book.conjure(dynamic=True, name="borrower")
        try:
            assert owner.link(borrower)
            with borrower.transaction("link", conduits=[borrower, owner]):
                assert borrower.add_spell_to_contract(
                    spell_id=provider_id, conduit=owner, permissions="create",
                )
            assert borrower.validate_contracts_and_define()
            yield borrower, consumer_id
        finally:
            borrower.permanent_cleanup()
        return
    consumer_types = {
        "annotation": ReaderConsumer,
        "collection": ReaderCollection,
        "map": MappedReaderConsumer,
    }
    consumer_id = owner_book.bind(spell=consumer_types[path], existence="many")
    root = owner_book.conjure(dynamic=True)
    yield root, consumer_id


@pytest.mark.parametrize("path", ["annotation", "collection", "map", "contract"])
@pytest.mark.parametrize("provider_type", [ValidReader, InheritedReader, InstanceOnlyReader])
def test_protocol_instance_remains_the_same_usable_dependency(
        instance_book: Spellbook, path: str, provider_type: type,
) -> None:
    """Use admitted instances through four real compiler/runtime resolution routes.

    Contract: every consumer receives the exact supplied reference and can use
    its member, including members present only on the actual instance.
    """
    supplied = provider_type()
    provider_id = instance_book.bind(
        spell=supplied, existence="unique", spellframe=ReaderContract, binding_name="primary",
    )
    with consumer_runtime(instance_book, provider_id, path) as (root, consumer_id):
        consumer = root.meld(spell_id=consumer_id)
        if path == "collection":
            assert len(consumer.readers) == 1
            actual = consumer.readers[0]
        else:
            actual = consumer.reader
        assert actual is supplied
        assert actual.read() == "supplied-reader"
