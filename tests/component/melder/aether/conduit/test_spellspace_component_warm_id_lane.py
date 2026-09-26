"""
Component tests for the SpellSpace-level warm id lane (`SpellSpace.meld(spell_id=...)`).

Purpose:
    A warm `spell_id=...` meld through `SpellSpace.meld` is served straight from the spellspace
    door's fast-door entry, with the same guard ladder and arms as `SpellSpaceMeld.meld`
    (2026-09-26). These tests drive real bind -> conjure -> scope -> meld flows and pin the
    contract: a hit returns the same object the door would, without entering the door; every
    guard trip, payload shape and call shape the lane does not own still reaches the door; and
    existence semantics and errors are unchanged.
"""

from typing import Iterator, List

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.spellspace_meld import SpellSpaceMeld
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


def _reset_runtime() -> None:
    """Reset the Nexus and Aether singletons and rebind the class-level Aether references."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def reset_runtime_for_spellspace_warm_id_lane() -> Iterator[None]:
    """
    Reset singleton runtime state around every test.

    Yields:
        None.
    """
    _reset_runtime()
    yield
    _reset_runtime()


@pytest.fixture
def door_calls(monkeypatch: pytest.MonkeyPatch) -> List[int]:
    """
    Count entries into the spellspace door (`SpellSpaceMeld.meld`).

    Contract:
        A warm hit served by the SpellSpace lane leaves the count unchanged; every meld the lane
        hands to the door increments it. Resolution itself is untouched: the wrapper delegates.

    Returns:
        List[int]: A one-element counter.
    """
    calls = [0]
    original = SpellSpaceMeld.meld

    def counting(self: SpellSpaceMeld, *args: object, **kwargs: object) -> object:
        """Record one door entry, then run the real door."""
        calls[0] += 1
        return original(self, *args, **kwargs)

    monkeypatch.setattr(SpellSpaceMeld, "meld", counting)
    return calls


def _make_spellbook() -> Spellbook:
    """
    Return a non-dynamic Spellbook (the only posture that builds fast-door entries).

    Returns:
        Spellbook: Configured with default properties and one phase-scheduler worker.
    """
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=False)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


class Marker:
    """Object scoped to one spellspace."""


class Session:
    """Object scoped to one conduit."""


class Shared:
    """Frame-wide singleton."""


class Fresh:
    """A new object on every meld."""


class Configurable:
    """A new object on every meld whose value a caller may override."""

    def __init__(self, value: int = 0) -> None:
        """Keep the supplied value."""
        self.value = value


class Bound:
    """An application object bound as an existing creation."""


def test_warm_id_meld_is_served_without_entering_the_door(door_calls: List[int]) -> None:
    """The first meld goes through the door and builds the entry; warm melds return from the lane."""
    book = _make_spellbook()
    marker_id = book.bind(spell=Marker, existence=Existence.unique_per_spell_space)
    conduit = book.conjure(name="root")
    try:
        with conduit.enter_spellspace() as space:
            first = space.meld(spell_id=marker_id)
            assert door_calls[0] == 1
            assert marker_id in space._meld._fast_meld_doors
            assert space.meld(spell_id=marker_id) is first
            assert space.meld(spell_id=marker_id) is first
            assert door_calls[0] == 1
    finally:
        conduit.permanent_cleanup()


def test_warm_lane_keeps_every_existence_semantics() -> None:
    """Through the lane: one marker per spellspace, one session per conduit, one singleton, many fresh."""
    book = _make_spellbook()
    marker_id = book.bind(spell=Marker, existence=Existence.unique_per_spell_space)
    session_id = book.bind(spell=Session, existence=Existence.unique_per_conduit)
    shared_id = book.bind(spell=Shared, existence=Existence.unique)
    fresh_id = book.bind(spell=Fresh, existence=Existence.many)
    conduit = book.conjure(name="root")
    try:
        shared = conduit.meld(spell_id=shared_id)
        lesser = conduit.create_lesser_conduit()
        session = lesser.meld(spell_id=session_id)
        markers = []
        for _ in range(2):
            with lesser.enter_spellspace() as space:
                for _ in range(3):
                    marker = space.meld(spell_id=marker_id)
                    assert space.meld(spell_id=marker_id) is marker
                    assert space.meld(spell_id=session_id) is session
                    assert space.meld(spell_id=shared_id) is shared
                    assert space.meld(spell_id=fresh_id) is not space.meld(spell_id=fresh_id)
                markers.append(marker)
        assert markers[0] is not markers[1]
        lesser.cleanup()
    finally:
        conduit.permanent_cleanup()


def test_dict_override_rides_the_lane_and_other_payloads_reach_the_door(door_calls: List[int]) -> None:
    """A non-empty dict override is served by the lane; an empty dict still goes through the door."""
    book = _make_spellbook()
    configurable_id = book.bind(spell=Configurable, existence=Existence.many)
    conduit = book.conjure(name="root")
    try:
        with conduit.enter_spellspace() as space:
            assert space.meld(spell_id=configurable_id).value == 0
            entered = door_calls[0]
            assert space.meld(spell_id=configurable_id, override={"value": 7}).value == 7
            assert door_calls[0] == entered
            assert space.meld(spell_id=configurable_id, override={}).value == 0
            assert door_calls[0] == entered + 1
    finally:
        conduit.permanent_cleanup()


@pytest.mark.parametrize("trip", ["validation_required", "spell_hooks", "meld_hooks"])
def test_guard_trips_send_the_meld_through_the_door(trip: str, door_calls: List[int]) -> None:
    """Every guard the lane mirrors hands the meld to the door, where hooks fire and results hold."""
    book = _make_spellbook()
    marker_id = book.bind(spell=Marker, existence=Existence.unique_per_spell_space)
    conduit = book.conjure(name="root")
    hook_calls: List[str] = []
    try:
        with conduit.enter_spellspace() as space:
            first = space.meld(spell_id=marker_id)
            entered = door_calls[0]
            if trip == "validation_required":
                book._set_spellbook_validation_required(True)
            elif trip == "spell_hooks":
                book._spell_id_pool[marker_id]._set_hooks(pre_hooks=[lambda: hook_calls.append("pre")])
            else:
                if space._meld._meld_hooks is None:
                    space._meld._meld_hooks = {}
                space._meld._meld_hooks["on_meld_pre_resolve"] = [lambda target: hook_calls.append("meld")]
            assert space.meld(spell_id=marker_id) is first
            assert door_calls[0] == entered + 1
            if trip == "spell_hooks":
                assert hook_calls == ["pre"]
            elif trip == "meld_hooks":
                assert hook_calls == ["meld"]
            if trip == "validation_required":
                book._set_spellbook_validation_required(False)
    finally:
        conduit.permanent_cleanup()


def test_existing_object_is_returned_by_the_lane(door_calls: List[int]) -> None:
    """A warm meld of a bound object returns that object itself without entering the door."""
    book = _make_spellbook()
    bound = Bound()
    bound_id = book.bind(spell=bound, existence=Existence.unique)
    conduit = book.conjure(name="root")
    try:
        with conduit.enter_spellspace() as space:
            assert space.meld(spell_id=bound_id) is bound
            entered = door_calls[0]
            assert space.meld(spell_id=bound_id) is bound
            assert door_calls[0] == entered
    finally:
        conduit.permanent_cleanup()


def test_call_shapes_outside_the_lane_are_unchanged(door_calls: List[int]) -> None:
    """Class input goes through the door as before; passing both identities still raises ValueError."""
    book = _make_spellbook()
    marker_id = book.bind(spell=Marker, existence=Existence.unique_per_spell_space)
    conduit = book.conjure(name="root")
    try:
        with conduit.enter_spellspace() as space:
            by_id = space.meld(spell_id=marker_id)
            entered = door_calls[0]
            assert space.meld(Marker) is by_id
            assert door_calls[0] == entered + 1
            with pytest.raises(ValueError, match="not both"):
                space.meld(Marker, spell_id=marker_id)
            assert door_calls[0] == entered + 1
    finally:
        conduit.permanent_cleanup()
