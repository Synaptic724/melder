"""
Component tests - Spellbook spell-map walks and the Conduit spell lookups under concurrent change (0.2.8230).

Every writer of `Spellbook._spells` now holds the Book lock, bind's publication included, so a walk that
holds that lock never meets an insert mid-walk; walks that cannot hold it (another Book's map, the book-wide
phase factories `Conduit.validate_resolution` runs) iterate a one-call snapshot; and the two lineage lookups
that walked the map (`Conduit.get_spell_permissions`, `CommandSystem.get_spell_by_spell_id`) answer from the
Book's id maps. Each race is forced with events, not sleeps: a thread is parked inside the walk while the
test thread binds. The last test locks the miss contract `Conduit.get_spell_by_spell_id` and
`get_conduit_by_spell_id` now document: an id no conduit claims raises ValueError, as it always did.
"""

import sys
import threading
import time
from collections.abc import Callable, Iterator
from typing import Any

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_compiler_system import SpellCompilerSystem
from melder.aether.spellbook.spellbook import Spellbook

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _ServiceA:
    """First active spell of the Book under test."""


class _ServiceB:
    """Second active spell, or a parked version of _ServiceA's index."""


class _ServiceC:
    """The spell another thread binds while a walk is parked."""


class _NoIterationDict(dict):
    """
    Stand-in for the live active-index map that fails the test on any iteration.

    Single-key reads (`get`, `[]`, `in`) behave as on a plain dict; `iter`, `items`, `keys` and `values`
    raise, so a lookup that walks the map fails loudly instead of racing concurrent writers.
    """

    def __iter__(self) -> Iterator[Any]:
        """Refuse iteration."""
        raise AssertionError("the lookup iterated the live active-index map")

    def items(self) -> Any:
        """Refuse an items walk."""
        raise AssertionError("the lookup walked the live active-index map with items()")

    def keys(self) -> Any:
        """Refuse a keys walk."""
        raise AssertionError("the lookup walked the live active-index map with keys()")

    def values(self) -> Any:
        """Refuse a values walk."""
        raise AssertionError("the lookup walked the live active-index map with values()")


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
    """Return a dynamic-posture configuration with one phase worker."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _bind(book: Spellbook, spell: type, name: str) -> str:
    """Bind `spell` as a unique, creatable spell under `name` and return its id."""
    return book.bind(spell=spell, existence=Existence.unique, permissions="create", binding_name=name)


def _wait_until(condition: Callable[[], bool], timeout: float) -> bool:
    """Poll `condition` until it holds or `timeout` seconds pass; return whether it held."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.005)
    return condition()


def test_bind_publishes_only_after_a_book_locked_walk_finishes(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Pin bind's publication under the Book lock against a walk that holds that lock.
    Contract:
        A walk of `_spells` under the Book lock (here `_find_spell_index_by_index_id`, parked on the first
        index it reads) sees no insert from a bind running meanwhile: the bind publishes after the walk
        releases the lock, the walk returns its index, and the bind still lands. Before 0.2.8230 the bind
        inserted at once and the walk raised "dictionary changed size during iteration".
    Raises:
        AssertionError: If the walk raises or misses, the bind publishes mid-walk, or the bind fails.
    """
    book = Spellbook(configuration=_dynamic_configuration())
    _bind(book, _ServiceA, "a")
    id_b = _bind(book, _ServiceB, "b")
    index_b = book._spells_by_id[id_b].spell_index
    index_b_id = index_b.id

    bind_paused = threading.Event()
    release_bind = threading.Event()
    walk_paused = threading.Event()
    release_walk = threading.Event()
    outcome: dict[str, Any] = {}
    original_claim_lookup = AethericFrame.claim_lookup
    original_index_id = SpellIndex.id

    def paused_claim_lookup(frame: AethericFrame, *args: Any, **kwargs: Any) -> Any:
        """Park the binding thread just before it claims its lookup key and publishes."""
        if threading.current_thread() is binder:
            bind_paused.set()
            assert release_bind.wait(timeout=30), "the test never released the bind"
        return original_claim_lookup(frame, *args, **kwargs)

    def paused_index_id(index: SpellIndex) -> str:
        """Park the walking thread on the first index id it reads, inside its walk."""
        if threading.current_thread() is walker and not walk_paused.is_set():
            walk_paused.set()
            assert release_walk.wait(timeout=30), "the test never released the walk"
        return original_index_id.fget(index)

    def bind_c() -> None:
        """Bind a third spell from another thread."""
        try:
            outcome["id_c"] = _bind(book, _ServiceC, "c")
        except BaseException as exc:
            outcome["bind_error"] = exc

    def walk_for_b() -> None:
        """Look index B up by its id under the Book lock."""
        try:
            outcome["index"] = book._find_spell_index_by_index_id(index_b_id)
        except BaseException as exc:
            outcome["walk_error"] = exc

    monkeypatch.setattr(AethericFrame, "claim_lookup", paused_claim_lookup)
    monkeypatch.setattr(SpellIndex, "id", property(paused_index_id))
    binder = threading.Thread(target=bind_c, name="spell-map-binder")
    walker = threading.Thread(target=walk_for_b, name="spell-map-walker")
    try:
        binder.start()
        assert bind_paused.wait(timeout=30), "the bind never reached its publication"
        walker.start()
        assert walk_paused.wait(timeout=30), "the walk never started"
        size_in_walk = len(book._spells)
        release_bind.set()
        # The bind now runs to its publication. Under the Book lock it waits for the walk; the bounded wait
        # only gives an unlocked insert the chance to show itself.
        published_mid_walk = _wait_until(lambda: len(book._spells) > size_in_walk, timeout=1.0)
    finally:
        release_bind.set()
        release_walk.set()
        walker.join(timeout=30)
        binder.join(timeout=30)

    try:
        assert not walker.is_alive() and not binder.is_alive()
        assert "walk_error" not in outcome, outcome.get("walk_error")
        assert "bind_error" not in outcome, outcome.get("bind_error")
        assert published_mid_walk is False
        assert outcome["index"] is index_b
        assert len(book._spells) == size_in_walk + 1
        assert book.find_spell_by_spell_id(outcome["id_c"]) is not None
    finally:
        book.cleanup()


def test_validate_resolution_cleanup_pass_survives_a_concurrent_bind(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Pin the snapshot walk of the book-wide resolution pass that public `validate_resolution` runs.
    Contract:
        `Conduit.validate_resolution` runs the book-wide phases with no Book lock, so a bind can land while
        its artifact-cleanup pass walks the Book's spells; the pass walks a snapshot and the call returns the
        conduit's resolution state, with the late spell registered. Before 0.2.8230 the pass walked the live
        map and raised "dictionary changed size during iteration".
    Raises:
        AssertionError: If validation raises, never reaches its cleanup pass, or the bind is lost.
    """
    book = Spellbook(configuration=_dynamic_configuration())
    _bind(book, _ServiceA, "a")
    _bind(book, _ServiceB, "b")
    conduit = book.conjure(dynamic=True, name="validate")
    pass_paused = threading.Event()
    release_pass = threading.Event()
    outcome: dict[str, Any] = {}
    original_cleanup = SpellCompilerSystem.cleanup_phase_artifacts

    def paused_cleanup(compiler_system: SpellCompilerSystem, spell: Any) -> Any:
        """Park the validating thread inside the resolution cleanup pass, after its first spell."""
        result = original_cleanup(compiler_system, spell)
        if (
                threading.current_thread() is validator
                and sys._getframe(1).f_code.co_name == "cleanup_phase_artifacts_after_resolution"
                and not pass_paused.is_set()
        ):
            pass_paused.set()
            assert release_pass.wait(timeout=30), "the test never released the cleanup pass"
        return result

    def validate() -> None:
        """Run the public validation hook from another thread."""
        try:
            outcome["state"] = conduit.validate_resolution()
        except BaseException as exc:
            outcome["validate_error"] = exc

    monkeypatch.setattr(SpellCompilerSystem, "cleanup_phase_artifacts", paused_cleanup)
    validator = threading.Thread(target=validate, name="spell-map-validator")
    try:
        validator.start()
        assert pass_paused.wait(timeout=60), "validate_resolution never reached its cleanup pass"
        id_c = _bind(book, _ServiceC, "c")
    finally:
        release_pass.set()
        validator.join(timeout=60)

    try:
        assert not validator.is_alive()
        assert "validate_error" not in outcome, outcome.get("validate_error")
        assert outcome["state"] is not None
        assert book.find_spell_by_spell_id(id_c) is not None
    finally:
        conduit.permanent_cleanup()


def test_get_spell_permissions_answers_from_the_id_maps_without_walking() -> None:
    """
    Purpose:
        Pin `Conduit.get_spell_permissions` to the Book's id-map lookup.
    Contract:
        The permissions of a current id, and of a parked id (the version's own permissions since 0.2.8253;
        before, the lineage's CURRENT ones), resolve without iterating the live active-index map; an id the
        Book does not know raises RuntimeError. Before 0.2.8230 the method walked that map under the conduit
        lock, which a concurrent bind or removal could resize mid-walk.
    Raises:
        AssertionError: If the lookup walks the map or answers the wrong permissions.
    """
    book = Spellbook(configuration=_dynamic_configuration())
    id_a = _bind(book, _ServiceA, "a")
    conduit = book.conjure(dynamic=True, name="permissions")
    try:
        index_a = book._spells_by_id[id_a].spell_index
        id_b = conduit.bind_inactive(
            spell=_ServiceB, spell_index=index_a, existence=Existence.unique,
            permissions="read", binding_name="b",
        )
        live_map = book._spells
        book._spells = _NoIterationDict(live_map)
        try:
            assert conduit.get_spell_permissions(id_a) == "create"
            assert conduit.get_spell_permissions(id_b) == "read"
            with pytest.raises(RuntimeError, match="not found"):
                conduit.get_spell_permissions("0" * 64)
        finally:
            book._spells = live_map
    finally:
        conduit.permanent_cleanup()


def test_conduit_spell_lookups_raise_for_an_id_no_conduit_claims() -> None:
    """
    Purpose:
        Lock the miss contract of `Conduit.get_spell_by_spell_id` and `Conduit.get_conduit_by_spell_id`.
    Contract:
        An id no conduit claims raises ValueError naming the id from both lookups - the `get_*` lookups raise
        on a miss (owner decision 2026-10-11; until 0.2.8230 their docstrings promised None, which they never
        returned); a registered id resolves to its spell and its owning root; a frame that does not exist
        raises ValueError.
    Raises:
        AssertionError: If an unclaimed id answers instead of raising, or a known id or a missing frame answers
            wrongly.
    """
    book = Spellbook(configuration=_dynamic_configuration())
    id_a = _bind(book, _ServiceA, "a")
    conduit = book.conjure(dynamic=True, name="lookups")
    try:
        unclaimed = "0" * 64
        with pytest.raises(ValueError, match=f"Spell version {unclaimed} not found in any conduit"):
            conduit.get_spell_by_spell_id(unclaimed)
        with pytest.raises(ValueError, match=f"Spell version {unclaimed} not found in any conduit"):
            conduit.get_conduit_by_spell_id(unclaimed)
        assert conduit.get_spell_by_spell_id(id_a) is book._spells_by_id[id_a]
        assert conduit.get_conduit_by_spell_id(id_a) is conduit
        with pytest.raises(ValueError, match="does not exist"):
            conduit.get_spell_by_spell_id(id_a, aetheric_frame_name="no-such-frame")
        with pytest.raises(ValueError, match="does not exist"):
            conduit.get_conduit_by_spell_id(id_a, aetheric_frame_name="no-such-frame")
    finally:
        conduit.permanent_cleanup()
