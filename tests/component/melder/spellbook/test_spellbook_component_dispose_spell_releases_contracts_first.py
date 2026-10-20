"""
Component tests: `Spellbook._dispose_spell` hands its `release_contracts` hook the version after its decision and
before its disposal (cleanup_releases_contracts_2026_10_19, 0.2.8261).

The hook is how `Conduit.cleanup_spell` takes a version out of every contract before the Book disposes it: it runs
once the Book has decided to dispose the version and marked it in flight, with no Book lock held, and never for a
refused call; a raise from it ends the call with nothing disposed and the in-flight mark cleared.
"""

from typing import Iterator, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _Active:
    """The index's active version."""


class _Parked:
    """A version parked on the active one's index."""


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_dispose_hook() -> Iterator[None]:
    """
    Purpose:
        Give each test a clean Aether singleton and frame registry.
    Returns:
        Iterator[None]: Control returns to the test between the two resets.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _book_with_parked_version() -> Tuple[Spellbook, str, str]:
    """
    Purpose:
        An unconjured Book with one index: `_Active` active, `_Parked` parked on it.
    Returns:
        Tuple[Spellbook, str, str]: The Book, the active spell_id and the parked spell_id.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(configuration=configuration)
    active_id = book.bind(spell=_Active, existence=Existence.unique, permissions="create", binding_name="active")
    index = book.find_spell_by_spell_id(active_id).spell_index
    parked_id = book.bind_inactive(spell=_Parked, spell_index=index, existence=Existence.unique,
                                   permissions="create", binding_name="parked")
    return book, active_id, parked_id


def test_release_contracts_runs_between_the_decision_and_the_disposal() -> None:
    book, _active_id, parked_id = _book_with_parked_version()
    parked = book._get_owned_spell(parked_id)
    seen: List[Tuple[str, bool, bool]] = []

    def release(spell_id: str) -> None:
        """Record the spell_id, whether the version is still live and still owned."""
        seen.append((spell_id, parked._cleaned, book._get_owned_spell(spell_id) is parked))

    try:
        assert book._dispose_spell(parked, release_contracts=release) is None
        assert seen == [(parked_id, False, True)]
        assert parked._cleaned
        assert book._get_owned_spell(parked_id) is None
    finally:
        book.cleanup()


def test_release_contracts_is_not_called_for_a_refused_disposal() -> None:
    book, active_id, _parked_id = _book_with_parked_version()
    calls: List[str] = []
    try:
        with pytest.raises(RuntimeError, match="active member of a multi-member index"):
            book._dispose_spell(book.find_spell_by_spell_id(active_id), release_contracts=calls.append)
        assert calls == []
    finally:
        book.cleanup()


def test_a_raising_release_contracts_disposes_nothing_and_a_retry_completes() -> None:
    book, _active_id, parked_id = _book_with_parked_version()
    parked = book._get_owned_spell(parked_id)

    def failing(spell_id: str) -> None:
        """Fail the release."""
        raise RuntimeError(f"release failed for {spell_id}")

    try:
        with pytest.raises(RuntimeError, match="release failed"):
            book._dispose_spell(parked, release_contracts=failing)
        assert not parked._cleaned
        assert book._get_owned_spell(parked_id) is parked
        assert book._dispose_spell(parked) is None
        assert parked._cleaned
    finally:
        book.cleanup()
