"""
Unit: SpellBinder stages a managed binding (STORY-2026-10-15-managed_bind_options, S2).

`as_managed_spell_quantity(mode=None, *, limit=None, timeout_seconds=None, reset_methods=None)` selects
`Existence.managed_spell_quantity` and stages the four options in the passthrough payload `finalize()` sends to
`Spellbook.bind`; Bind validates them there. `bind(..., managed_spell_mode=...)` passes them the same way.
"""
from typing import Any, Dict, List

import pytest

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spellbinder import SpellBinder

MANAGED_NAMES = (
    "managed_spell_mode", "managed_spell_limit", "managed_spell_timeout_seconds", "managed_spell_reset_methods",
)


class RecordingBook:
    """Spellbook double (weak-referenceable) recording every bind payload."""

    def __init__(self) -> None:
        """Start with no calls."""
        self.calls: List[Dict[str, Any]] = []

    def bind(self, **kwargs: Any) -> str:
        """Record the payload and return a fake spell id."""
        self.calls.append(kwargs)
        return "spell-id"


class Pooled:
    """Managed target."""


def test_as_managed_spell_quantity_selects_the_member_and_sends_the_options() -> None:
    """finalize() sends the managed existence and the four staged options."""
    book = RecordingBook()
    binder = SpellBinder(book)
    try:
        spell_id = (
            binder.bind(Pooled)
            .as_managed_spell_quantity(ManagedSpellMode.queue, limit=2, timeout_seconds=1.5, reset_methods=["reset"])
            .finalize()
        )
    finally:
        binder.cleanup()
    assert spell_id == "spell-id"
    call = book.calls[0]
    assert call["existence"] is Existence.managed_spell_quantity
    assert call["managed_spell_mode"] is ManagedSpellMode.queue
    assert call["managed_spell_limit"] == 2
    assert call["managed_spell_timeout_seconds"] == 1.5
    assert call["managed_spell_reset_methods"] == ["reset"]


def test_as_managed_spell_quantity_defaults_send_none() -> None:
    """With no arguments every option is None, so Bind applies the elastic defaults."""
    book = RecordingBook()
    binder = SpellBinder(book)
    try:
        binder.bind(Pooled).as_managed_spell_quantity().finalize()
    finally:
        binder.cleanup()
    call = book.calls[0]
    assert call["existence"] is Existence.managed_spell_quantity
    assert [call[name] for name in MANAGED_NAMES] == [None, None, None, None]


def test_the_next_registration_does_not_inherit_the_options() -> None:
    """finalize() resets the binder: a later bind carries no managed options."""
    book = RecordingBook()
    binder = SpellBinder(book)
    try:
        binder.bind(Pooled).as_managed_spell_quantity("limited_quantity", limit=3).finalize()
        binder.bind(Pooled).as_unique().finalize()
    finally:
        binder.cleanup()
    second = book.calls[1]
    assert second["existence"] is Existence.unique
    assert not any(name in second for name in MANAGED_NAMES)


def test_bind_passthrough_keywords_carry_the_options() -> None:
    """bind(..., managed_spell_mode=...) stages the options through the passthrough payload."""
    book = RecordingBook()
    binder = SpellBinder(book)
    try:
        binder.bind(
            Pooled, existence=Existence.managed_spell_quantity, managed_spell_mode="elastic", managed_spell_limit=9,
        ).finalize()
    finally:
        binder.cleanup()
    call = book.calls[0]
    assert call["managed_spell_mode"] == "elastic"
    assert call["managed_spell_limit"] == 9


def test_as_managed_spell_quantity_refuses_a_cleaned_binder() -> None:
    """A cleaned binder raises RuntimeError like every fluent method."""
    binder = SpellBinder(RecordingBook())
    binder.cleanup()
    with pytest.raises(RuntimeError):
        binder.as_managed_spell_quantity()
