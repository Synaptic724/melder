"""
Unit: a Spell carries the managed options Bind normalized (STORY-2026-10-15-managed_bind_options, S2).

The four values are native, read-only per-version policy like `resolvable`: set once at construction, read through
properties that refuse a cleaned Spell, never placed in `metadata`.
"""
from typing import Any

import pytest

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_types.spell_types import SpellType


class _States:
    """SpellSystemStates stand-in: Spell construction only reads the reference."""


class _SpellbookStub:
    """
    Minimal owner: Spell reads `_spell_system_states` at construction and asks the Book to remove it on cleanup.
    """

    def __init__(self) -> None:
        """Hold a states stand-in."""
        self._spell_system_states = _States()

    def cleanup_and_remove_spell(self, spell: Spell) -> None:
        """Run the local teardown the way the Book does."""
        spell._spellbook_cleanup = True
        spell.cleanup()


class Pooled:
    """A managed target class."""

    def reset(self) -> None:
        """Zero-argument reset."""


def _spell(existence: Existence = Existence.managed_spell_quantity, **options: Any) -> Spell:
    """Build one class Spell with the given existence and managed options."""
    return Spell(
        spell=Pooled,
        spell_index=SpellIndex("managed-version"),
        spellframe=None,
        binding_name=None,
        spell_name="Pooled",
        existence=existence,
        spell_type=SpellType.SPELL,
        spell_id="managed-version",
        permissions=Permissions.create,
        aetheric_frame="default",
        spellbook=_SpellbookStub(),
        **options,
    )


def test_a_managed_spell_exposes_its_options() -> None:
    """The four properties return the values the Spell was built with."""
    spell = _spell(
        managed_spell_mode=ManagedSpellMode.queue,
        managed_spell_limit=3,
        managed_spell_timeout_seconds=1.5,
        managed_spell_reset_methods=("reset",),
    )
    try:
        assert spell.managed_spell_mode is ManagedSpellMode.queue
        assert spell.managed_spell_limit == 3
        assert spell.managed_spell_timeout_seconds == 1.5
        assert spell.managed_spell_reset_methods == ("reset",)
    finally:
        spell.cleanup()


def test_a_spell_built_without_options_reports_none_and_no_resets() -> None:
    """A Spell of any other existence reads None, None, None and an empty tuple."""
    spell = _spell(existence=Existence.unique)
    try:
        assert spell.managed_spell_mode is None
        assert spell.managed_spell_limit is None
        assert spell.managed_spell_timeout_seconds is None
        assert spell.managed_spell_reset_methods == ()
    finally:
        spell.cleanup()


def test_the_options_are_native_keywords_not_metadata() -> None:
    """Passing the options does not put them in `metadata`; other keywords still do."""
    spell = _spell(managed_spell_mode=ManagedSpellMode.elastic, managed_spell_limit=256, team="pools")
    try:
        assert spell.metadata == {"team": "pools"}
    finally:
        spell.cleanup()


@pytest.mark.parametrize(
    "name",
    ["managed_spell_mode", "managed_spell_limit", "managed_spell_timeout_seconds", "managed_spell_reset_methods"],
)
def test_the_options_refuse_a_cleaned_spell(name: str) -> None:
    """Each property raises the cleaned RuntimeError once the Spell is cleaned, like `resolvable`."""
    spell = _spell(managed_spell_mode=ManagedSpellMode.elastic, managed_spell_limit=256)
    spell.cleanup()
    with pytest.raises(RuntimeError):
        getattr(spell, name)


def test_the_options_are_read_only() -> None:
    """There is no setter: changing a managed option takes another binding."""
    spell = _spell(managed_spell_mode=ManagedSpellMode.elastic, managed_spell_limit=256)
    try:
        with pytest.raises(AttributeError):
            spell.managed_spell_limit = 4
        assert spell.managed_spell_limit == 256
    finally:
        spell.cleanup()
