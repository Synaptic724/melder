"""
Unit tests - Spell._spell_index_unless_cleaned, the cleanup-safe index read (0.2.8229).

Spellbook.find_spell_by_id reads a parked spell's index through this accessor without holding the Book
lock, so the read must answer the live index, follow an index move, answer None once the spell is cleaned,
and never interleave with a cleanup running under the spell's lock.
"""

import threading
from typing import Any

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_types.spell_types import SpellType


class _RecordingStates:
    """SpellSystemStates stand-in; Spell construction only needs the structural-change hook."""

    def __init__(self) -> None:
        """Start with no recorded notices."""
        self.calls: list[tuple[Any, Any]] = []

    def mark_structural_change(self, spell_index: Any, reason: Any = None) -> None:
        """Record the notice; nothing in these tests reads it."""
        self.calls.append((spell_index, reason))


class _SpellbookStub:
    """Minimal Spellbook stand-in: Spell construction reads its states, Spell.cleanup routes removal here."""

    def __init__(self) -> None:
        """Hold the states stand-in the Spell reads at construction."""
        self._spell_system_states = _RecordingStates()

    def cleanup_and_remove_spell(self, spell: Spell) -> None:
        """Finish the spell's own teardown, then clean its index, as the Book's removal does."""
        spell_index = spell.spell_index
        spell._spellbook_cleanup = True
        spell.cleanup()
        spell_index.cleanup()


class _Service:
    """Plain class registered as the spell under test."""


def _make_spell(spell_id: str = "unless-cleaned-fingerprint") -> Spell:
    """Build one live Spell with its own SpellIndex over the stub Book."""
    return Spell(
        spell=_Service,
        spell_index=SpellIndex(spell_id),
        spellframe=None,
        binding_name=None,
        spell_name="_Service",
        existence=Existence.unique,
        spell_type=SpellType.SPELL,
        spell_id=spell_id,
        permissions=Permissions.read,
        aetheric_frame="default",
        spellbook=_SpellbookStub(),
    )


def test_returns_the_spell_index_while_live() -> None:
    """A live spell answers the index it belongs to."""
    spell = _make_spell()
    try:
        assert spell._spell_index_unless_cleaned() is spell.spell_index
    finally:
        spell.cleanup()


def test_follows_an_index_move() -> None:
    """An index move repoints spell_index; the read answers the new index."""
    spell = _make_spell()
    original = spell.spell_index
    moved_to = SpellIndex("moved-index-member")
    try:
        spell.spell_index = moved_to
        assert spell._spell_index_unless_cleaned() is moved_to
    finally:
        spell.spell_index = original
        spell.cleanup()
        moved_to.cleanup()


def test_returns_none_after_cleanup_without_raising() -> None:
    """A cleaned spell has no spell_index attribute; the read answers None, repeatedly."""
    spell = _make_spell()
    spell.cleanup()
    assert spell._spell_index_unless_cleaned() is None
    assert spell._spell_index_unless_cleaned() is None


def test_waits_for_the_spell_lock_and_sees_the_cleanup_finished_under_it() -> None:
    """
    A read blocked behind a cleanup holding the spell's lock answers None once the cleanup is done.

    The holder thread takes the spell's lock and waits; the reader starts and must still be blocked after
    a bounded wait; the holder then cleans the spell under the same lock and releases it. A read that did
    not take the lock would have answered the index before the cleanup.
    """
    spell = _make_spell()
    holding = threading.Event()
    release = threading.Event()
    reader_done = threading.Event()
    outcome: dict[str, Any] = {}

    def _hold_lock_then_clean() -> None:
        """Hold the spell's lock until released, then clean the spell under it (the lock is reentrant)."""
        with spell._lock:
            holding.set()
            release.wait(timeout=30)
            spell.cleanup()

    def _read() -> None:
        """Read the index and keep the result or the exception for the test thread."""
        try:
            outcome["result"] = spell._spell_index_unless_cleaned()
        except BaseException as error:
            outcome["error"] = error
        finally:
            reader_done.set()

    holder = threading.Thread(target=_hold_lock_then_clean, name="spell-lock-holder")
    reader = threading.Thread(target=_read, name="spell-index-reader")
    holder.start()
    try:
        assert holding.wait(timeout=30)
        reader.start()
        assert not reader_done.wait(timeout=0.2), "the read returned while another thread held the spell lock"
        release.set()
        holder.join(timeout=30)
        reader.join(timeout=30)
        assert not holder.is_alive() and not reader.is_alive()
        assert "error" not in outcome, repr(outcome.get("error"))
        assert outcome["result"] is None
    finally:
        release.set()
        holder.join(timeout=30)
        if reader.is_alive():
            reader.join(timeout=30)
