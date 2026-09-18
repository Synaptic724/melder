"""Existing providers must satisfy the same declared Protocol members as class providers.

These native regressions exercise bind admission and usable dependency injection.
Concrete/string frame grouping and factory admission remain independent controls.
"""

from typing import Protocol

import pytest

from melder.aether.spellbook.spellbook import Spellbook
from tests.integration.melder.spellbook.test_existing_instance_planning import (
    instance_book as instance_book,
)


class ReaderContract(Protocol):
    """Require a readable provider without requiring runtime_checkable decoration."""

    def read(self) -> str:
        """Return a value usable by the consumer."""
        ...


class ValidReader:
    """Supply the actual operation requested by ReaderContract."""

    def read(self) -> str:
        """Return an observable value without allocating resources."""
        return "supplied-reader"


class InheritedReader(ValidReader):
    """Satisfy the contract through an inherited implementation."""


class MissingReader:
    """Intentionally lack the required read member."""


class NonCallableReader:
    """Expose a non-callable value where the contract requires a method."""

    read = None


class ReaderConsumer:
    """Borrow a required Protocol provider without acquiring its cleanup custody."""

    def __init__(self, reader: ReaderContract) -> None:
        """Retain the exact provider selected by native constructor injection."""
        self.reader = reader


class GroupingFrame:
    """Act as a concrete grouping key, with no declared Protocol semantics."""


def reader_factory() -> ValidReader:
    """Supply a reader through the existing callable binding family."""
    return ValidReader()


@pytest.mark.parametrize("late_bind", [False, True])
@pytest.mark.parametrize("existing", [False, True], ids=["class", "instance"])
@pytest.mark.parametrize("provider_type", [MissingReader, NonCallableReader])
def test_protocol_binding_rejects_missing_or_noncallable_members(
        instance_book: Spellbook,
        late_bind: bool,
        existing: bool,
        provider_type: type,
) -> None:
    """Reject incompatible providers at bind instead of injecting a later AttributeError.

    The class cases are passing controls. The existing-instance cases reproduce
    the skipped admission check before and after conjure, without mocking it.
    """
    if late_bind:
        instance_book.conjure(dynamic=True)
    target = provider_type() if existing else provider_type
    with pytest.raises(TypeError, match=r"Protocol.*ReaderContract.*Missing members: read"):
        instance_book.bind(spell=target, existence="unique", spellframe=ReaderContract)


@pytest.mark.parametrize("late_bind", [False, True])
@pytest.mark.parametrize("provider_type", [ValidReader, InheritedReader])
def test_valid_protocol_instance_remains_injectable_by_identity(
        instance_book: Spellbook,
        late_bind: bool,
        provider_type: type[ValidReader],
) -> None:
    """Accept a real member implementation and inject the same usable supplied object."""
    supplied = provider_type()
    root = instance_book.conjure(dynamic=True) if late_bind else None
    instance_book.bind(spell=supplied, existence="unique", spellframe=ReaderContract)
    consumer_id = instance_book.bind(spell=ReaderConsumer, existence="many")
    if root is None:
        root = instance_book.conjure(dynamic=True)
    consumer = root.meld(spell_id=consumer_id)
    assert consumer.reader is supplied
    assert consumer.reader.read() == "supplied-reader"


@pytest.mark.parametrize("existing", [False, True], ids=["class", "instance"])
@pytest.mark.parametrize("frame", [GroupingFrame, "reader-group"], ids=["concrete", "string"])
def test_non_protocol_frames_keep_grouping_semantics(
        instance_book: Spellbook,
        existing: bool,
        frame: object,
) -> None:
    """Keep non-Protocol frame grouping independent of nominal class inheritance checks."""
    supplied = ValidReader()
    target = supplied if existing else ValidReader
    spell_id = instance_book.bind(spell=target, existence="unique", spellframe=frame)
    root = instance_book.conjure(dynamic=True)
    resolved = root.meld(spell_id=spell_id)
    assert resolved.read() == "supplied-reader"
    if existing:
        assert resolved is supplied


@pytest.mark.parametrize("late_bind", [False, True])
def test_protocol_factory_admission_keeps_its_separate_callable_contract(
        instance_book: Spellbook,
        late_bind: bool,
) -> None:
    """A factory need not expose read itself; its existing registration behavior is preserved."""
    root = instance_book.conjure(dynamic=True) if late_bind else None
    spell_id = instance_book.bind(spell=reader_factory, existence="unique", spellframe=ReaderContract)
    if root is None:
        root = instance_book.conjure(dynamic=True)
    assert root.meld(spell_id=spell_id).read() == "supplied-reader"
