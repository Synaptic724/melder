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


class InstanceOnlyReader:
    """Supply read on the instance, without a corresponding class member."""

    def __init__(self) -> None:
        """Install a callable on the supplied reference before binding."""
        self.read = self._read

    def _read(self) -> str:
        """Return a value proving that the actual supplied member is usable."""
        return "supplied-reader"


class ShadowedReader(ValidReader):
    """Model an instance whose method no longer satisfies its class's contract."""

    def __init__(self) -> None:
        """Shadow the inherited read method on this deliberately invalid input."""
        self.__dict__["read"] = None


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

    The class cases are controls. The existing-instance cases guard the same
    admission boundary before and after conjure, without mocking it.
    """
    if late_bind:
        instance_book.conjure(dynamic=True)
    target = provider_type() if existing else provider_type
    with pytest.raises(TypeError, match=r"Protocol.*ReaderContract.*Missing members: read"):
        instance_book.bind(spell=target, existence="unique", spellframe=ReaderContract)


@pytest.mark.parametrize("late_bind", [False, True])
@pytest.mark.parametrize("provider_type", [ValidReader, InheritedReader, InstanceOnlyReader])
def test_valid_protocol_instance_remains_injectable_by_identity(
        instance_book: Spellbook,
        late_bind: bool,
        provider_type: type,
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


@pytest.mark.parametrize("late_bind", [False, True])
def test_shadowed_instance_method_is_rejected_before_registration(
        instance_book: Spellbook, late_bind: bool,
) -> None:
    """Reject the supplied surface even when its class exposes a valid method.

    A subsequent compatible binding uses the same frame/name and resolves by
    identity, proving rejection did not publish a competing provider.
    """
    root = instance_book.conjure(dynamic=True) if late_bind else None
    with pytest.raises(TypeError, match=r"Existing object.*ReaderContract.*Missing members: read"):
        instance_book.bind(
            spell=ShadowedReader(), existence="unique", spellframe=ReaderContract, binding_name="primary",
        )
    supplied = InstanceOnlyReader()
    instance_book.bind(
        spell=supplied, existence="unique", spellframe=ReaderContract, binding_name="primary",
    )
    consumer_id = instance_book.bind(spell=ReaderConsumer, existence="many")
    if root is None:
        root = instance_book.conjure(dynamic=True)
    assert root.meld(spell_id=consumer_id).reader is supplied


@pytest.mark.parametrize("late_bind", [False, True])
def test_inactive_bind_rejects_incompatible_protocol_value(
        instance_book: Spellbook, late_bind: bool,
) -> None:
    """Reject a bad parked value without changing the active index or provider."""
    supplied = ValidReader()
    active_id = instance_book.bind(
        spell=supplied, existence="unique", spellframe=ReaderContract, binding_name="primary",
    )
    index = instance_book._spells_by_id[active_id].spell_index
    root = instance_book.conjure(dynamic=True) if late_bind else None
    with pytest.raises(TypeError, match=r"Existing object.*ReaderContract.*Missing members: read"):
        instance_book.bind_inactive(
            spell=MissingReader(), spell_index=index, existence="unique",
            spellframe=ReaderContract, binding_name="primary",
        )
    assert index.spells_in_index() == {active_id}
    if root is None:
        root = instance_book.conjure(dynamic=True)
    assert root.meld(spell_id=active_id) is supplied


def test_valid_instance_member_survives_staging_and_selection(instance_book: Spellbook) -> None:
    """Preserve instance-only members through staging, public selection and meld."""
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
    assert result.read() == "supplied-reader"


def test_existing_protocol_provider_keeps_unique_only_error_precedence(instance_book: Spellbook) -> None:
    """Report invalid existing-object lifetime before the incompatible member contract."""
    with pytest.raises(ValueError, match=r"Existing-object spells must use Existence.unique"):
        instance_book.bind(spell=MissingReader(), existence="many", spellframe=ReaderContract)
