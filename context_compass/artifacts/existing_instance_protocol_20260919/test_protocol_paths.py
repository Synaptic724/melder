"""Native Protocol path evidence and instance-surface controls.

The stock-prefixed cases deliberately characterize incorrect current admission.
Exclude those observations when running the separate admission_probe plugin.
All other cases qualify a bounded admission repair hypothesis or preserve the
existing helper's explicitly limited semantics; none is a production patch.
"""

import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Protocol, Union

import pytest

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spellbook import Spellbook
from tests.component.melder.spellbook.test_existing_instance_protocol_admission import (
    InheritedReader,
    MissingReader,
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
    """Receive all providers registered under the declared ReaderContract frame."""

    def __init__(self, readers: list[ReaderContract]) -> None:
        """Retain supplied references for identity and usable-member assertions."""
        self.readers = readers


class MappedReaderConsumer:
    """Select the supplied reader through the ordinary explicit SpellMap path."""

    def __init__(
            self,
            reader: Union[ReaderContract, SpellMap] = SpellMap(
                spellframe=ReaderContract, binding_name="primary",
            ),
    ) -> None:
        """Retain the resolved value; the fixture later checks exact identity."""
        self.reader = reader


class ContractReaderConsumer:
    """Select the supplied reader through a real cross-conduit SpellContract."""

    def __init__(
            self,
            reader: Union[ReaderContract, SpellContract] = SpellContract(
                spellframe=ReaderContract, binding_name="primary",
            ),
    ) -> None:
        """Retain the contracted reference without claiming cleanup ownership."""
        self.reader = reader


class InstanceOnlyReader:
    """Provide read on the actual instance, with no read attribute on its class."""

    def __init__(self) -> None:
        """Install the instance's callable member before registration."""
        self.read = self._read

    def _read(self) -> str:
        """Return an observable value for real consumer use."""
        return "instance-member"


class ShadowedReader(ValidReader):
    """Intentionally violate the Protocol by shadowing a valid class method."""

    def __init__(self) -> None:
        """Make the supplied value incompatible even though its class exposes read."""
        self.read = None


class ExtendedReaderContract(ReaderContract, Protocol):
    """Require an inherited read plus a directly declared child method."""

    def child(self) -> str:
        """Return the child operation result."""
        ...


class ChildOnlyReader:
    """Meet the direct Protocol member while intentionally lacking inherited read."""

    def child(self) -> str:
        """Prove that the directly declared member works independently."""
        return "child"


class LabelContract(Protocol):
    """Declare data through annotations without a class-dictionary value."""

    label: str


class UnlabelledValue:
    """Intentionally omit the Protocol's annotation-only field."""


@contextmanager
def consumer_runtime(
        owner_book: Spellbook, provider_id: str, path: str,
) -> Iterator[tuple[Conduit, str]]:
    """Own only the extra borrower runtime; the imported fixture owns the source world.

    Contract: use public bind/conjure/link/grant/meld paths without changing
    compiler behavior. The contract route grants the existing provider through
    the same transaction pattern as the repository's native contract tests.
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


@pytest.mark.parametrize("path", ("annotation", "collection", "map", "contract"))
def test_stock_bad_provider_passes_compiler_then_fails_at_use(instance_book: Spellbook, path: str) -> None:
    """Characterize the current gap; success here means the bad object was admitted, not repaired."""
    supplied = MissingReader()
    provider_id = instance_book.bind(
        spell=supplied, existence="unique", spellframe=ReaderContract, binding_name="primary",
    )
    with consumer_runtime(instance_book, provider_id, path) as (root, consumer_id):
        consumer = root.meld(spell_id=consumer_id)
        actual = consumer.readers[0] if path == "collection" else consumer.reader
        assert actual is supplied
        with pytest.raises(AttributeError, match="read"):
            actual.read()
        print("PROTOCOL_PATH " + json.dumps({
            "path": path, "injected_same_bad_reference": True, "failure_at_use": "AttributeError",
        }, sort_keys=True))


@pytest.mark.parametrize("path", ("annotation", "collection", "map", "contract"))
@pytest.mark.parametrize("provider_type", (ValidReader, InheritedReader, InstanceOnlyReader))
def test_valid_instance_surface_injects_without_compiler_changes(
        instance_book: Spellbook, path: str, provider_type: type,
) -> None:
    """Require exact identity and usable members across all four real compiler/runtime routes."""
    supplied = provider_type()
    expected = supplied.read()
    provider_id = instance_book.bind(
        spell=supplied, existence="unique", spellframe=ReaderContract, binding_name="primary",
    )
    with consumer_runtime(instance_book, provider_id, path) as (root, consumer_id):
        consumer = root.meld(spell_id=consumer_id)
        actual = consumer.readers[0] if path == "collection" else consumer.reader
        assert actual is supplied
        assert actual.read() == expected


@pytest.mark.parametrize("late_bind", (False, True))
def test_shadowed_method_requires_actual_instance_validation(instance_book: Spellbook, late_bind: bool) -> None:
    """Reject an instance whose class is compatible but whose live method was replaced with None."""
    if late_bind:
        instance_book.conjure(dynamic=True)
    with pytest.raises(TypeError, match=r"Protocol.*ReaderContract.*Missing members: read"):
        instance_book.bind(spell=ShadowedReader(), existence="unique", spellframe=ReaderContract)


@pytest.mark.parametrize("existing", (False, True))
@pytest.mark.parametrize("case", ("inherited_protocol", "annotation_only_data"))
def test_shared_helper_limits_are_preserved(instance_book: Spellbook, existing: bool, case: str) -> None:
    """Characterize existing class/instance limits, not demand expanded Protocol semantics.

    The narrow helper considers directly declared dictionary members. These
    cases remain admitted under the diagnostic repair and require a separate
    contract decision before their expected behavior changes.
    """
    provider_type = ChildOnlyReader if case == "inherited_protocol" else UnlabelledValue
    contract = ExtendedReaderContract if case == "inherited_protocol" else LabelContract
    target = provider_type() if existing else provider_type
    spell_id = instance_book.bind(spell=target, existence="unique", spellframe=contract)
    root = instance_book.conjure(dynamic=True)
    resolved = root.meld(spell_id=spell_id)
    if existing:
        assert resolved is target
    if case == "inherited_protocol":
        assert resolved.child() == "child"
        with pytest.raises(AttributeError, match="read"):
            resolved.read()
    else:
        with pytest.raises(AttributeError, match="label"):
            resolved.label


@pytest.mark.parametrize("late_bind", (False, True))
def test_inactive_bind_rejects_incompatible_protocol_value(instance_book: Spellbook, late_bind: bool) -> None:
    """The common admission boundary must also reject bad parked values before any selection."""
    active_id = instance_book.bind(
        spell=ValidReader(), existence="unique", spellframe=ReaderContract, binding_name="primary",
    )
    index = instance_book._spells_by_id[active_id].spell_index
    if late_bind:
        instance_book.conjure(dynamic=True)
    with pytest.raises(TypeError, match=r"Protocol.*ReaderContract.*Missing members: read"):
        instance_book.bind_inactive(
            spell=MissingReader(), spell_index=index, existence="unique",
            spellframe=ReaderContract, binding_name="primary",
        )


def test_valid_instance_member_survives_staging_and_selection(instance_book: Spellbook) -> None:
    """A valid instance-only member remains injectable after post-conjure staging and public notch."""
    active_id = instance_book.bind(
        spell=ValidReader(), existence="unique", spellframe=ReaderContract, binding_name="primary",
    )
    index = instance_book._spells_by_id[active_id].spell_index
    root = instance_book.conjure(dynamic=True)
    supplied = InstanceOnlyReader()
    staged_id = instance_book.bind_inactive(
        spell=supplied, spell_index=index, existence="unique",
        spellframe=ReaderContract, binding_name="primary",
    )
    root.notch_spell(spell_index=index, spell=instance_book._inactive_spells[staged_id])
    result = root.meld(spell_id=staged_id)
    assert result is supplied
    assert result.read() == "instance-member"
