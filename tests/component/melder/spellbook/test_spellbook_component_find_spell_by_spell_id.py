"""
Component tests - Spellbook.find_spell_by_spell_id returns the spell that owns the spell_id (0.2.8253).

A spell_id is the SHA `bind` and `bind_inactive` return; `find_spell_by_spell_id` answers it with exactly that
Spell - the active version from the Book's active-id map, else the parked version from its parked map - or None.
It never answers with the spell the spell_id's index has active: that is the index's own lookup
(`get_spell_by_index_id`). The owner's rule (2026-10-17): a spell_id and a SpellIndex are separate things.

History: 0.2.8229 made the lookup answer from the id maps instead of walking the live index map (the walk raised
"dictionary changed size during iteration", or skipped a registered spell, while other spells were bound or
removed); it kept answering a parked spell_id with its index's active spell. 0.2.8253 renamed it from
`find_spell_by_id` and made it exact. These tests pin the exact answer across every writer that moves a spell_id
between the maps - notch, add-to-index, remove-from-index, ownership transfer and parked disposal - and the two
properties 0.2.8229 added: the lookup never iterates the live active-index map, and a parked version disposed in
the middle of a lookup never makes it raise.

Every version of an index is bound the way its first version was (2026-10-25,
STORY-2026-10-17-notch_moves_signature_by_incoming_key_only), so _ServiceB is staged under _ServiceA's
spellframe and binding name, and an add-to-index move takes a version split off its index back into it.
"""

import threading
from collections.abc import Iterator
from typing import Any

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _ServiceA:
    """First version of the index, bound at ('service', 'a'): the active version unless a test notches it out."""


class _ServiceB:
    """Second version of the index: bound parked into _ServiceA's index at the same ('service', 'a')."""


class _ForeignService:
    """Bound only in another Book, so its spell_id is unknown to the Book under test."""


class _NoIterationDict(dict):
    """
    Stand-in for the live active-index map that fails the test on any iteration.

    Single-key reads (`get`, `[]`, `in`) behave as on a plain dict; `iter`, `items`, `keys` and `values`
    raise, so a lookup that walks the map fails loudly instead of racing concurrent writers.
    """

    def __iter__(self) -> Iterator[Any]:
        """Refuse iteration."""
        raise AssertionError("find_spell_by_spell_id iterated the live active-index map")

    def items(self) -> Any:
        """Refuse an items walk."""
        raise AssertionError("find_spell_by_spell_id walked the live active-index map with items()")

    def keys(self) -> Any:
        """Refuse a keys walk."""
        raise AssertionError("find_spell_by_spell_id walked the live active-index map with keys()")

    def values(self) -> Any:
        """Refuse a values walk."""
        raise AssertionError("find_spell_by_spell_id walked the live active-index map with values()")


class _PausingGetDict(dict):
    """
    Stand-in for the parked-version map that pauses the first get() of one spell_id after reading it.

    The lookup thread then waits inside find_spell_by_spell_id holding the parked Spell it just read, so the test
    thread can dispose of that spell before the lookup returns. Every other read, and every write, behaves as on a
    plain dict.
    """

    def __init__(self, source: dict[str, Any], paused_id: str) -> None:
        """Copy the live parked map and arm the pause for `paused_id`."""
        super().__init__(source)
        self._paused_id = paused_id
        self.paused = threading.Event()
        self.resume = threading.Event()

    def get(self, key: Any, default: Any = None) -> Any:
        """Read the value, and on the first read of the armed spell_id wait for the test to resume."""
        value = super().get(key, default)
        if key == self._paused_id and not self.paused.is_set():
            self.paused.set()
            if not self.resume.wait(timeout=30):
                raise AssertionError("the test never resumed the paused lookup")
        return value


@pytest.fixture(autouse=True)
def _isolated_aether() -> Iterator[None]:
    """Give every test a fresh Aether so Books, frames and spell ids never leak between tests."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _dynamic_configuration() -> SpellbookConfiguration:
    """Return a dynamic-posture configuration with one phase worker, as the transfer tests build it."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


class _Lineage:
    """
    One dynamic Book whose index holds _ServiceA active and _ServiceB parked, both bound at ('service', 'a').

    The fixture owns the Book's root conduit for one test; `cleanup()` tears it down and the autouse fixture
    resets the Aether.
    """

    def __init__(self) -> None:
        """Bind A, conjure the dynamic root, then park B into A's index under A's binding."""
        self.book = Spellbook(configuration=_dynamic_configuration())
        self.id_a = self.book.bind(
            spell=_ServiceA, existence=Existence.unique, permissions="create", spellframe="service",
            binding_name="a",
        )
        self.conduit = self.book.conjure(dynamic=True, name="lineage")
        self.spell_a = self.book._spells_by_id[self.id_a]
        self.index = self.spell_a.spell_index
        self.id_b = self.conduit.bind_inactive(
            spell=_ServiceB, spell_index=self.index, existence=Existence.unique,
            permissions="create", spellframe="service", binding_name="a",
        )
        self.spell_b = self.book._inactive_spells[self.id_b]

    def cleanup(self) -> None:
        """Tear down the root conduit."""
        self.conduit.permanent_cleanup()


def test_active_spell_id_returns_its_active_spell() -> None:
    """The active version's spell_id answers that Spell."""
    world = _Lineage()
    try:
        assert world.book.find_spell_by_spell_id(world.id_a) is world.spell_a
    finally:
        world.cleanup()


def test_parked_spell_id_returns_the_parked_spell_itself() -> None:
    """A parked version's spell_id answers that parked Spell, not the spell its index has active."""
    world = _Lineage()
    try:
        assert world.book.find_spell_by_spell_id(world.id_b) is world.spell_b
        assert world.index.selected_spell_id == world.id_a
    finally:
        world.cleanup()


def test_after_a_notch_each_spell_id_returns_its_own_spell() -> None:
    """A notch moves which version the index has active; each spell_id still answers its own Spell."""
    world = _Lineage()
    try:
        world.conduit.notch_spell(spell_index=world.index, spell=world.spell_b)
        assert world.index.selected_spell_id == world.id_b
        assert world.book.find_spell_by_spell_id(world.id_b) is world.spell_b
        assert world.book.find_spell_by_spell_id(world.id_a) is world.spell_a
    finally:
        world.cleanup()


def test_parked_spell_moved_back_into_its_index_returns_itself() -> None:
    """
    An add-to-index move repoints the parked version's index; its spell_id still answers that Spell.

    The version is split off into an index of its own, then moved back into _ServiceA's index - the move an
    index allows, since every version of it is bound the same way.
    """
    world = _Lineage()
    try:
        world.conduit.remove_from_spell_index(spell=world.spell_b, source_index=world.index)
        split_index = world.spell_b.spell_index
        world.conduit.add_to_spell_index(spell=world.spell_b, target_index=world.index)
        assert world.book.find_spell_by_spell_id(world.id_b) is world.spell_b
        assert world.spell_b.spell_index is world.index
        assert world.spell_b.spell_index is not split_index
        assert world.book.find_spell_by_spell_id(world.id_a) is world.spell_a
    finally:
        world.cleanup()


def test_parked_spell_split_off_to_a_fresh_index_returns_itself() -> None:
    """A version moved out to a fresh index has no active spell there, and its spell_id still answers it."""
    world = _Lineage()
    try:
        world.conduit.remove_from_spell_index(spell=world.spell_b, source_index=world.index)
        assert world.book.find_spell_by_spell_id(world.id_b) is world.spell_b
        assert world.spell_b.spell_index is not world.index
        assert world.book.find_spell_by_spell_id(world.id_a) is world.spell_a
    finally:
        world.cleanup()


def test_disposed_parked_spell_returns_none() -> None:
    """Disposing a parked version drops its spell_id; the active version still answers."""
    world = _Lineage()
    try:
        world.book.cleanup_spell(spell=world.spell_b)
        assert world.book.find_spell_by_spell_id(world.id_b) is None
        assert world.book.find_spell_by_spell_id(world.id_a) is world.spell_a
    finally:
        world.cleanup()


def test_transfer_moves_both_spell_ids_to_the_target_book() -> None:
    """A transfer moves the whole index: each spell_id answers its own Spell in the target Book, none in the source."""
    configuration = _dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    id_a = owner_book.bind(
        spell=_ServiceA, existence=Existence.unique, permissions="create", spellframe="service", binding_name="a",
    )
    target_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        index = owner_book._spells_by_id[id_a].spell_index
        id_b = owner.bind_inactive(
            spell=_ServiceB, spell_index=index, existence=Existence.unique,
            permissions="create", spellframe="service", binding_name="a",
        )
        owner.transfer_spell_ownership(spell=id_a, target_conduit=target)
        active = target_book.find_spell_by_spell_id(id_a)
        parked = target_book.find_spell_by_spell_id(id_b)
        assert active is not None and active.spell_id == id_a and active.spell is _ServiceA
        assert parked is not None and parked.spell_id == id_b and parked.spell is _ServiceB
        assert owner_book.find_spell_by_spell_id(id_a) is None
        assert owner_book.find_spell_by_spell_id(id_b) is None
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()


def test_unknown_and_foreign_spell_ids_return_none() -> None:
    """A spell_id no Book owns, and one owned by another Book, both miss."""
    world = _Lineage()
    foreign_book = Spellbook(aetheric_frame="foreign-frame")
    try:
        foreign_id = foreign_book.bind(spell=_ForeignService, existence=Existence.unique, permissions="create")
        assert world.book.find_spell_by_spell_id("no-such-spell-id") is None
        assert world.book.find_spell_by_spell_id(foreign_id) is None
        assert foreign_book.find_spell_by_spell_id(world.id_a) is None
    finally:
        foreign_book.cleanup()
        world.cleanup()


def test_lookup_never_iterates_the_live_active_index_map() -> None:
    """Every kind of spell_id is answered with single-key reads; a walk of the live map fails the test."""
    world = _Lineage()
    live_map = world.book._spells
    world.book._spells = _NoIterationDict(live_map)
    try:
        assert world.book.find_spell_by_spell_id(world.id_a) is world.spell_a
        assert world.book.find_spell_by_spell_id(world.id_b) is world.spell_b
        assert world.book.find_spell_by_spell_id("no-such-spell-id") is None
    finally:
        world.book._spells = live_map
        world.cleanup()


def test_parked_spell_disposed_mid_lookup_never_makes_it_raise() -> None:
    """
    A parked version disposed after the lookup read it answers the Spell it read - a borrowed reference - and
    the next lookup misses.

    The lookup thread pauses right after reading the parked Spell; the test thread disposes of it through the
    public removal verb, which cleans the Spell; the lookup then resumes and returns what it read, without
    raising. A Spell a lookup returns is borrowed, not leased, for active and parked versions alike.
    """
    world = _Lineage()
    pausing = _PausingGetDict(world.book._inactive_spells, world.id_b)
    world.book._inactive_spells = pausing
    outcome: dict[str, Any] = {}

    def _lookup() -> None:
        """Run the lookup and keep its result or its exception for the test thread."""
        try:
            outcome["result"] = world.book.find_spell_by_spell_id(world.id_b)
        except BaseException as error:
            outcome["error"] = error

    lookup_thread = threading.Thread(target=_lookup, name="find-spell-by-spell-id-lookup")
    lookup_thread.start()
    try:
        assert pausing.paused.wait(timeout=10), "the lookup never read the parked version"
        world.book.cleanup_spell(spell=world.spell_b)
        pausing.resume.set()
        lookup_thread.join(timeout=30)
        assert not lookup_thread.is_alive()
        assert "error" not in outcome, repr(outcome.get("error"))
        assert outcome["result"] is world.spell_b
        assert world.book.find_spell_by_spell_id(world.id_b) is None
        assert world.book.find_spell_by_spell_id(world.id_a) is world.spell_a
    finally:
        pausing.resume.set()
        lookup_thread.join(timeout=30)
        world.cleanup()
