"""
Unit tests of `Creations.discard_managed_quantity` (STORY-2026-10-15-managed_ownership_transfer, S6).

Scope:
    The identity-checked removal an ownership transfer's rollback uses to take back the empty pool a stamp of that
    transfer composed in the target store: the pool leaves the store's map and the release registry, nothing else
    in the store changes, and the pool itself is left to the caller (the transfer cleans it).
"""
import threading
from collections.abc import Iterator
from typing import List

import pytest

from melder.aether.conduit.creations.conduit_creations import ConduitCreations
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from tests.unit.melder.aether.conduit.creations.test_creations_managed_quantities import (
    _idle_object,
    _Probe,
    _reset_world,
    _SpellStub,
)


@pytest.fixture(autouse=True)
def fresh_registry() -> Iterator[None]:
    """A fresh Aether, and with it a fresh ReleaseManagedSpell, around every test."""
    _reset_world()
    yield
    _reset_world()


@pytest.fixture
def store() -> ConduitCreations:
    """A root store per test."""
    return ConduitCreations(conduit_id="root-1")


def test_discard_removes_the_pool_it_is_given(store: ConduitCreations) -> None:
    """The pool under the id leaves the store and the call answers True."""
    pool = store.ensure_managed_quantity(_SpellStub())
    assert store.discard_managed_quantity("managed-sid", pool) is True
    assert store.get_managed_quantity("managed-sid") is None


def test_discard_unregisters_the_pool(store: ConduitCreations) -> None:
    """A discarded pool is no longer routable: the registry lists nothing for the class and a release refuses."""
    pool = store.ensure_managed_quantity(_SpellStub())
    assert len(ReleaseManagedSpell().describe(_Probe)) == 1
    store.discard_managed_quantity("managed-sid", pool)
    assert ReleaseManagedSpell().describe(_Probe) == ()
    with pytest.raises(ValueError, match="not a managed spell class in any live root"):
        ReleaseManagedSpell().release(_Probe("late", []))


def test_discard_leaves_the_pool_to_the_caller(store: ConduitCreations) -> None:
    """The pool is not cleaned: its idle object is not disposed and it still takes an object back."""
    log: List[str] = []
    pool = store.ensure_managed_quantity(_SpellStub())
    idle = _idle_object(pool, _Probe("idle", log))
    store.discard_managed_quantity("managed-sid", pool)
    assert log == []
    assert pool.idle_count == 1
    assert pool.reserve() is None
    pool.put_back(_Probe("back", log))
    assert (pool.count, pool.idle_count, log) == (2, 2, [])
    assert idle.label == "idle"


def test_discard_refuses_another_pool_under_the_id(store: ConduitCreations) -> None:
    """A pool that is not the one the store holds under the id is refused; the store's pool stays registered."""
    held = store.ensure_managed_quantity(_SpellStub())
    stranger = ConduitCreations(conduit_id="root-2").ensure_managed_quantity(_SpellStub())
    assert store.discard_managed_quantity("managed-sid", stranger) is False
    assert store.get_managed_quantity("managed-sid") is held
    holders = sorted(row["holding_conduit_id"] for row in ReleaseManagedSpell().describe(_Probe))
    assert holders == ["root-1", "root-2"]


def test_discard_answers_false_when_the_store_holds_no_pool(store: ConduitCreations) -> None:
    """Nothing under the id: nothing to discard."""
    pool = ConduitCreations(conduit_id="root-2").ensure_managed_quantity(_SpellStub())
    assert store.discard_managed_quantity("managed-sid", pool) is False
    assert store.get_managed_quantity("managed-sid") is None


def test_discard_answers_false_for_a_pool_held_under_another_id(store: ConduitCreations) -> None:
    """The pool is matched under the id the caller names, not wherever it sits."""
    pool = store.ensure_managed_quantity(_SpellStub("first-sid"))
    assert store.discard_managed_quantity("second-sid", pool) is False
    assert store.get_managed_quantity("first-sid") is pool


def test_a_second_discard_answers_false(store: ConduitCreations) -> None:
    """Discarding is once: the second call finds no pool under the id."""
    pool = store.ensure_managed_quantity(_SpellStub())
    assert store.discard_managed_quantity("managed-sid", pool) is True
    assert store.discard_managed_quantity("managed-sid", pool) is False


def test_discard_touches_no_object_or_other_pool(store: ConduitCreations) -> None:
    """Objects, disposal records and the pools of other ids are untouched."""
    log: List[str] = []
    kept = store.ensure_managed_quantity(_SpellStub("kept-sid"))
    gone = store.ensure_managed_quantity(_SpellStub("gone-sid"))
    unique = _Probe("unique", log)
    store.add_creation("unique-sid", unique, has_disposal_methods=True, disposal_methods=["close"])
    store.discard_managed_quantity("gone-sid", gone)
    assert store.get_creation("unique-sid") is unique
    assert store.get_managed_quantity("kept-sid") is kept
    store.cleanup()
    assert log == ["unique"]


def test_ensure_after_a_discard_composes_a_new_pool(store: ConduitCreations) -> None:
    """The id is free again: the next stamp composes and registers a fresh pool."""
    spell = _SpellStub()
    first = store.ensure_managed_quantity(spell)
    store.discard_managed_quantity("managed-sid", first)
    second = store.ensure_managed_quantity(spell)
    assert second is not first
    assert [row["holding_conduit_id"] for row in ReleaseManagedSpell().describe(_Probe)] == ["root-1"]


def test_discard_on_a_cleaned_store_raises(store: ConduitCreations) -> None:
    """A retired store refuses the call, as ensure does; its cleanup already gave its pools up."""
    pool = store.ensure_managed_quantity(_SpellStub())
    store.cleanup()
    with pytest.raises(RuntimeError):
        store.discard_managed_quantity("managed-sid", pool)


def test_concurrent_discards_remove_the_pool_once(store: ConduitCreations) -> None:
    """Racing callers: exactly one removes the pool; the others answer False."""
    pool = store.ensure_managed_quantity(_SpellStub())
    results: List[bool] = []
    results_lock = threading.Lock()
    start = threading.Barrier(8)

    def discard() -> None:
        start.wait()
        removed = store.discard_managed_quantity("managed-sid", pool)
        with results_lock:
            results.append(removed)

    threads = [threading.Thread(target=discard) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sorted(results) == [False] * 7 + [True]
    assert ReleaseManagedSpell().describe(_Probe) == ()
