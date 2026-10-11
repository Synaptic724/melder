"""
Component tests - Spellbook.find_spell_by_id answers from the Book's id maps (0.2.8229).

`find_spell_by_id` resolves any id in a spell's version lineage to the live Spell that represents the
lineage now: a current version id through the active-id map, a superseded or parked id through the parked
map and the parked spell's index. These tests pin that contract across every writer that moves an id
between the maps - notch, add-to-index, remove-from-index, ownership transfer and parked disposal - and pin
the two properties the repair exists for: the lookup never iterates the live active-index map (the old walk
raised "dictionary changed size during iteration", or skipped a registered spell, while other spells were
bound or removed), and a parked version disposed in the middle of a lookup answers None instead of raising.
"""

import threading
from collections.abc import Iterator
from typing import Any, Optional

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
    """First lineage member: the active version of its index unless a test notches it out."""


class _ServiceB:
    """Second lineage member: bound parked into _ServiceA's index."""


class _ServiceC:
    """Active member of a second index, the destination of an add-to-index move."""


class _ForeignService:
    """Bound only in another Book, so its id is unknown to the Book under test."""


class _NoIterationDict(dict):
    """
    Stand-in for the live active-index map that fails the test on any iteration.

    Single-key reads (`get`, `[]`, `in`) behave as on a plain dict; `iter`, `items`, `keys` and `values`
    raise, so a lookup that walks the map fails loudly instead of racing concurrent writers.
    """

    def __iter__(self) -> Iterator[Any]:
        """Refuse iteration."""
        raise AssertionError("find_spell_by_id iterated the live active-index map")

    def items(self) -> Any:
        """Refuse an items walk."""
        raise AssertionError("find_spell_by_id walked the live active-index map with items()")

    def keys(self) -> Any:
        """Refuse a keys walk."""
        raise AssertionError("find_spell_by_id walked the live active-index map with keys()")

    def values(self) -> Any:
        """Refuse a values walk."""
        raise AssertionError("find_spell_by_id walked the live active-index map with values()")


class _PausingGetDict(dict):
    """
    Stand-in for the parked-version map that pauses the first get() of one id after reading it.

    The lookup thread then waits inside find_spell_by_id holding the parked Spell it just read, so the test
    thread can dispose of that spell before the lookup reads the spell's index. Every other read, and every
    write, behaves as on a plain dict.
    """

    def __init__(self, source: dict[str, Any], paused_id: str) -> None:
        """Copy the live parked map and arm the pause for `paused_id`."""
        super().__init__(source)
        self._paused_id = paused_id
        self.paused = threading.Event()
        self.resume = threading.Event()

    def get(self, key: Any, default: Any = None) -> Any:
        """Read the value, and on the first read of the armed id wait for the test to resume."""
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
    One dynamic Book whose first index holds _ServiceA active and _ServiceB parked.

    With `second_index=True` the Book also holds _ServiceC active in its own index. The fixture owns the
    Book's root conduit for one test; `cleanup()` tears it down and the autouse fixture resets the Aether.
    """

    def __init__(self, *, second_index: bool = False) -> None:
        """Bind A (and C), conjure the dynamic root, then park B into A's index."""
        self.book = Spellbook(configuration=_dynamic_configuration())
        self.id_a = self.book.bind(
            spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a",
        )
        self.id_c: Optional[str] = None
        if second_index:
            self.id_c = self.book.bind(
                spell=_ServiceC, existence=Existence.unique, permissions="create", binding_name="c",
            )
        self.conduit = self.book.conjure(dynamic=True, name="lineage")
        self.spell_a = self.book._spells_by_id[self.id_a]
        self.index = self.spell_a.spell_index
        self.id_b = self.conduit.bind_inactive(
            spell=_ServiceB, spell_index=self.index, existence=Existence.unique,
            permissions="create", binding_name="b",
        )
        self.spell_b = self.book._inactive_spells[self.id_b]

    def cleanup(self) -> None:
        """Tear down the root conduit."""
        self.conduit.permanent_cleanup()


def test_current_version_id_returns_the_active_spell() -> None:
    """A current version id answers the active Spell itself."""
    world = _Lineage()
    try:
        assert world.book.find_spell_by_id(world.id_a) is world.spell_a
    finally:
        world.cleanup()


def test_parked_version_id_returns_the_live_spell_of_its_index() -> None:
    """A parked version id answers the live spell of the index that holds it, not the parked version."""
    world = _Lineage()
    try:
        assert world.book.find_spell_by_id(world.id_b) is world.spell_a
    finally:
        world.cleanup()


def test_both_lineage_ids_return_the_incoming_spell_after_a_notch() -> None:
    """After a notch the incoming id is current and the outgoing, now parked, id resolves to it."""
    world = _Lineage()
    try:
        world.conduit.notch_spell(spell_index=world.index, spell=world.spell_b)
        assert world.book.find_spell_by_id(world.id_b) is world.spell_b
        assert world.book.find_spell_by_id(world.id_a) is world.spell_b
    finally:
        world.cleanup()


def test_parked_version_moved_to_another_index_returns_that_index_live_spell() -> None:
    """An add-to-index move repoints the parked version, so its id resolves through its new index."""
    world = _Lineage(second_index=True)
    try:
        spell_c = world.book._spells_by_id[world.id_c]
        world.conduit.add_to_spell_index(spell=world.spell_b, target_index=spell_c.spell_index)
        assert world.book.find_spell_by_id(world.id_b) is spell_c
        assert world.book.find_spell_by_id(world.id_a) is world.spell_a
    finally:
        world.cleanup()


def test_parked_version_removed_from_its_index_returns_none() -> None:
    """A version moved out to a fresh index has no live spell to resolve to, so the lookup misses."""
    world = _Lineage()
    try:
        world.conduit.remove_from_spell_index(spell=world.spell_b, source_index=world.index)
        assert world.book.find_spell_by_id(world.id_b) is None
        assert world.book.find_spell_by_id(world.id_a) is world.spell_a
    finally:
        world.cleanup()


def test_disposed_parked_version_returns_none() -> None:
    """Disposing a parked version drops its id; the rest of the lineage still resolves."""
    world = _Lineage()
    try:
        world.book.cleanup_spell(spell=world.spell_b)
        assert world.book.find_spell_by_id(world.id_b) is None
        assert world.book.find_spell_by_id(world.id_a) is world.spell_a
    finally:
        world.cleanup()


def test_transfer_moves_lineage_resolution_to_the_target_book() -> None:
    """A transfer moves the whole lineage, so both ids resolve in the target Book and miss in the source."""
    configuration = _dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    id_a = owner_book.bind(spell=_ServiceA, existence=Existence.unique, permissions="create", binding_name="a")
    target_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        index = owner_book._spells_by_id[id_a].spell_index
        id_b = owner.bind_inactive(
            spell=_ServiceB, spell_index=index, existence=Existence.unique,
            permissions="create", binding_name="b",
        )
        owner.transfer_spell_ownership(spell=id_a, target_conduit=target)
        current = target_book.find_spell_by_id(id_a)
        parked = target_book.find_spell_by_id(id_b)
        assert current is not None and current.spell_id == id_a
        assert parked is current
        assert owner_book.find_spell_by_id(id_a) is None
        assert owner_book.find_spell_by_id(id_b) is None
    finally:
        target.permanent_cleanup()
        owner.permanent_cleanup()


def test_unknown_and_foreign_ids_return_none() -> None:
    """An id no Book owns, and an id owned by another Book, both miss."""
    world = _Lineage()
    foreign_book = Spellbook(aetheric_frame="foreign-frame")
    try:
        foreign_id = foreign_book.bind(spell=_ForeignService, existence=Existence.unique, permissions="create")
        assert world.book.find_spell_by_id("no-such-spell-id") is None
        assert world.book.find_spell_by_id(foreign_id) is None
        assert foreign_book.find_spell_by_id(world.id_a) is None
    finally:
        foreign_book.cleanup()
        world.cleanup()


def test_lookup_never_iterates_the_live_active_index_map() -> None:
    """Every kind of id is answered with single-key reads; a walk of the live map fails the test."""
    world = _Lineage()
    live_map = world.book._spells
    world.book._spells = _NoIterationDict(live_map)
    try:
        assert world.book.find_spell_by_id(world.id_a) is world.spell_a
        assert world.book.find_spell_by_id(world.id_b) is world.spell_a
        assert world.book.find_spell_by_id("no-such-spell-id") is None
    finally:
        world.book._spells = live_map
        world.cleanup()


def test_parked_version_disposed_mid_lookup_returns_none_without_raising() -> None:
    """
    A parked version disposed after the lookup read it, and before it read its index, answers None.

    The lookup thread pauses right after reading the parked Spell; the test thread disposes of it through
    the public removal verb, which cleans the Spell and deletes its index reference; the lookup then
    resumes. Reading the index unguarded would raise AttributeError here.
    """
    world = _Lineage()
    pausing = _PausingGetDict(world.book._inactive_spells, world.id_b)
    world.book._inactive_spells = pausing
    outcome: dict[str, Any] = {}

    def _lookup() -> None:
        """Run the lookup and keep its result or its exception for the test thread."""
        try:
            outcome["result"] = world.book.find_spell_by_id(world.id_b)
        except BaseException as error:
            outcome["error"] = error

    lookup_thread = threading.Thread(target=_lookup, name="find-spell-by-id-lookup")
    lookup_thread.start()
    try:
        assert pausing.paused.wait(timeout=10), "the lookup never read the parked version"
        world.book.cleanup_spell(spell=world.spell_b)
        pausing.resume.set()
        lookup_thread.join(timeout=30)
        assert not lookup_thread.is_alive()
        assert "error" not in outcome, repr(outcome.get("error"))
        assert outcome["result"] is None
        assert world.book.find_spell_by_id(world.id_a) is world.spell_a
    finally:
        pausing.resume.set()
        lookup_thread.join(timeout=30)
        world.cleanup()
