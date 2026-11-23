"""Unit coverage for `Creations.forget_slot` (failed_late_bind_is_undone, #330, 2026-11-23).

The unwind of a refused late-bind window takes back the slot its bind filed for an existing object. The object is
the caller's, so forgetting the slot must run none of its disposal methods - unlike a purge, a clear or the store's
cleanup - while the store stops holding, counting and purging it. These tests drive a bare store.
"""

from typing import List

import pytest

from melder.aether.conduit.creations.creations import Creations

SPELL = "c" * 64
OTHER = "d" * 64


def _key(binding: str, spell_id: str = SPELL) -> str:
    """A store key of `spell_id` under the binding hash `binding`."""
    return f"{spell_id}:{binding}"


class Probe:
    """An object that records the disposal methods run on it."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.calls: List[str] = []

    def close(self) -> None:
        """Record `close`."""
        self.calls.append("close")


@pytest.fixture
def store() -> Creations:
    """A fresh store per test."""
    return Creations(owner_conduit_id="conduit-1", id="conduit-1")


def test_forgetting_a_filed_existing_object_returns_true_and_the_store_lets_it_go(store: Creations) -> None:
    """The slot's object is no longer held or counted, and nothing was disposed."""
    existing = Probe("existing")
    store.register_slot(_key("h1"), existing)

    assert store.forget_slot(_key("h1")) is True

    assert store.get_creation(_key("h1")) is None
    assert store.count_spell_creations(SPELL) == 0
    assert existing.calls == []


def test_a_forgotten_disposal_bearing_slot_is_not_disposed_by_cleanup(store: Creations) -> None:
    """The disposal record goes with the slot: the store's teardown no longer reaches the caller's object."""
    existing = Probe("existing")
    kept = Probe("kept")
    store.add_creation(_key("h1"), existing, has_disposal_methods=True, disposal_methods=["close"])
    store.add_creation(_key("x1", OTHER), kept, has_disposal_methods=True, disposal_methods=["close"])

    store.forget_slot(_key("h1"))
    store.cleanup()

    assert existing.calls == []
    assert kept.calls == ["close"]


def test_forgetting_one_slot_leaves_the_spells_other_slots(store: Creations) -> None:
    """Only the named key goes: a sibling slot of the same spell is still held, counted and purged."""
    gone = Probe("gone")
    sibling = Probe("sibling")
    store.add_creation(_key("h1"), gone, has_disposal_methods=True, disposal_methods=["close"])
    store.add_creation(_key("h2"), sibling, has_disposal_methods=True, disposal_methods=["close"])

    store.forget_slot(_key("h1"))

    assert store.get_creation(_key("h2")) is sibling
    assert store.count_spell_creations(SPELL) == 1
    store.cleanup()
    assert sibling.calls == ["close"]
    assert gone.calls == []


def test_a_key_filed_again_after_forgetting_is_held_and_purged_afresh(store: Creations) -> None:
    """A retry files the key again: the store holds the new object only and a purge reaches it once."""
    first = Probe("first")
    second = Probe("second")
    store.add_creation(_key("h1"), first, has_disposal_methods=True, disposal_methods=["close"])
    store.forget_slot(_key("h1"))

    store.add_creation(_key("h1"), second, has_disposal_methods=True, disposal_methods=["close"])

    assert store.get_creation(_key("h1")) is second
    assert store.count_spell_creations(SPELL) == 1
    store.cleanup()
    assert second.calls == ["close"]
    assert first.calls == []


def test_forgetting_a_key_the_store_does_not_hold_returns_false(store: Creations) -> None:
    """An unknown key, or one already forgotten, changes nothing and reports False."""
    held = Probe("held")
    store.register_slot(_key("h1"), held)

    assert store.forget_slot(_key("missing")) is False
    assert store.forget_slot(_key("h1")) is True
    assert store.forget_slot(_key("h1")) is False
    assert store.count_spell_creations(SPELL) == 0


def test_forgetting_after_cleanup_returns_false(store: Creations) -> None:
    """A cleaned store holds nothing to forget and does not raise."""
    store.register_slot(_key("h1"), Probe("held"))
    store.cleanup()

    assert store.forget_slot(_key("h1")) is False


def test_a_key_without_a_colon_is_its_own_shelf(store: Creations) -> None:
    """A bare key is forgotten whole and can be filed again."""
    first = Probe("first")
    store.register_slot("bare-key", first)

    assert store.forget_slot("bare-key") is True
    assert store.get_creation("bare-key") is None
    assert store.count_spell_creations("bare-key") == 0

    second = Probe("second")
    store.register_slot("bare-key", second)
    assert store.get_creation("bare-key") is second
    assert store.count_spell_creations("bare-key") == 1
