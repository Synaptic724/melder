"""Unit coverage for the late-bind marks of SpellSystemStates (failed_late_bind_is_undone, #330, 2026-11-23).

A bind after conjure registers its lineage with the binding thread's id: the state gains
`SpellState.late_bind_in_progress` and the spell id is published in `late_bind_thread_ids`, the map the meld gate
reads without a lock to refuse another thread's meld of the spell while its bind window is open. The window's end
clears the marks (`clear_late_bind_marks`), and the unwind of a refused window drops them with the lineage
(`unregister_index`). These tests drive a real registry over a mocked frame.
"""

import threading
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Tuple
from unittest.mock import MagicMock

import pytest

from melder.aether.aetheric_frame.dev_ops.devops_information_registry import DevopsInformationRegistry
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.aether.spellbook.bind.spell_index import SpellIndex


@pytest.fixture
def information_registry() -> Iterator[DevopsInformationRegistry]:
    """A live DevOps information registry, cleaned after the test."""
    registry = DevopsInformationRegistry("late-bind-marks-frame")
    yield registry
    registry.cleanup()


@pytest.fixture
def states(information_registry: DevopsInformationRegistry) -> Iterator[SpellSystemStates]:
    """A SpellSystemStates registry over a mocked frame, cleaned after the test unless the test cleaned it."""
    frame = MagicMock()
    frame.name = "late-bind-marks-frame"
    registry = SpellSystemStates(frame, information_registry)
    yield registry
    if not registry._cleaned:
        registry.cleanup()


def _mark(states: SpellSystemStates, spell_id: str, thread_id: int) -> SpellIndex:
    """Register a lineage the way a bind after conjure does: with the binding thread's id."""
    index = SpellIndex(spell_id)
    states.register_index(index, "book", late_bind_thread_id=thread_id)
    return index


def test_a_late_bind_flags_the_state_and_publishes_the_binding_thread(states: SpellSystemStates) -> None:
    """The registration flags the lineage and publishes spell_id -> thread id, read by the meld gate."""
    index = _mark(states, "late-v1", 4242)

    state = states.get_by_index_id(index.id)
    assert state is not None
    assert state.has_flag(SpellState.late_bind_in_progress)
    assert states.late_bind_thread_ids == {"late-v1": 4242}


def test_a_registration_without_a_thread_id_marks_nothing(states: SpellSystemStates) -> None:
    """A bind before conjure, a notch or a transfer passes no thread id: no flag and an empty map."""
    index = SpellIndex("plain-v1")
    states.register_index(index, "book")

    state = states.get_by_index_id(index.id)
    assert state is not None
    assert not state.has_flag(SpellState.late_bind_in_progress)
    assert states.late_bind_thread_ids == {}


def test_a_later_registration_without_a_thread_id_keeps_an_open_mark(states: SpellSystemStates) -> None:
    """None leaves an existing mark as it is: only the window's end or an unregistration takes it out."""
    index = _mark(states, "late-v1", 7)
    states.register_index(index, "book")

    state = states.get_by_index_id(index.id)
    assert state is not None
    assert state.has_flag(SpellState.late_bind_in_progress)
    assert states.late_bind_thread_ids == {"late-v1": 7}


def test_the_published_map_is_replaced_never_mutated(states: SpellSystemStates) -> None:
    """A reader's snapshot stays as it was when it read it: marks and clears publish new maps."""
    before_mark = states.late_bind_thread_ids
    _mark(states, "late-v1", 11)
    after_mark = states.late_bind_thread_ids
    states.clear_late_bind_marks(["late-v1"])

    assert before_mark == {}
    assert after_mark == {"late-v1": 11}
    assert states.late_bind_thread_ids == {}


def test_clearing_one_mark_leaves_the_others_and_changes_no_validity(states: SpellSystemStates) -> None:
    """The window's end clears exactly its ids, flag-only: each state's validity is what it was."""
    first = _mark(states, "late-a", 1)
    second = _mark(states, "late-b", 2)
    first_state = states.get_by_index_id(first.id)
    second_state = states.get_by_index_id(second.id)
    assert first_state is not None and second_state is not None
    validity_before = (first_state.validity, second_state.validity)

    states.clear_late_bind_marks(["late-a"])

    assert not first_state.has_flag(SpellState.late_bind_in_progress)
    assert second_state.has_flag(SpellState.late_bind_in_progress)
    assert states.late_bind_thread_ids == {"late-b": 2}
    assert (first_state.validity, second_state.validity) == validity_before


def test_clearing_unknown_or_unmarked_ids_changes_nothing(states: SpellSystemStates) -> None:
    """An id the unwind already removed, or one never marked, is skipped and the published map is not replaced."""
    _mark(states, "late-v1", 5)
    plain = SpellIndex("plain-v1")
    states.register_index(plain, "book")
    published = states.late_bind_thread_ids

    states.clear_late_bind_marks(["gone-v1", "plain-v1"])

    assert states.late_bind_thread_ids is published
    assert published == {"late-v1": 5}


def test_unregistering_a_marked_lineage_drops_its_mark(states: SpellSystemStates) -> None:
    """The unwind of a refused window unregisters the lineage, and no mark outlives it."""
    index = _mark(states, "late-v1", 9)
    kept = _mark(states, "late-v2", 9)

    states.unregister_index(index)

    assert states.get_by_spell_id("late-v1") is None
    assert states.late_bind_thread_ids == {"late-v2": 9}
    assert states.get_by_index_id(kept.id) is not None


@pytest.mark.parametrize("bad_thread_id", ["12", 12.0, True], ids=["str", "float", "bool"])
def test_a_thread_id_that_is_not_an_int_is_refused_and_registers_nothing(
        states: SpellSystemStates,
        bad_thread_id: object,
) -> None:
    """Only an int (threading.get_ident()) is a thread id - a bool is refused too - and nothing is registered."""
    index = SpellIndex("late-v1")

    with pytest.raises(TypeError, match="late_bind_thread_id"):
        states.register_index(index, "book", late_bind_thread_id=bad_thread_id)

    assert states.get_by_index_id(index.id) is None
    assert states.late_bind_thread_ids == {}


def test_the_marks_cannot_be_read_or_cleared_after_cleanup(states: SpellSystemStates) -> None:
    """A cleaned registry refuses both the meld gate's read and the window's clear."""
    _mark(states, "late-v1", 3)
    states.cleanup()

    with pytest.raises(RuntimeError):
        _ = states.late_bind_thread_ids
    with pytest.raises(RuntimeError):
        states.clear_late_bind_marks(["late-v1"])


def test_concurrent_late_binds_each_publish_their_own_thread(states: SpellSystemStates) -> None:
    """Marks registered at once from many threads all land, each under its own binding thread's id."""
    workers = 16
    start = threading.Barrier(workers)

    def bind_one(position: int) -> Tuple[str, int]:
        """Register one lineage with this thread's id once every worker is ready; return what it published."""
        start.wait(timeout=20.0)
        spell_id = f"late-{position}"
        thread_id = threading.get_ident()
        _mark(states, spell_id, thread_id)
        return spell_id, thread_id

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(bind_one, position) for position in range(workers)]
        published: Dict[str, int] = dict(future.result(timeout=30.0) for future in futures)

    assert len(published) == workers
    assert states.late_bind_thread_ids == published
