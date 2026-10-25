"""
Unit tests - Creations files each binding's objects by store key, on one shelf per spell_id.

STORY-2026-10-25-creations_store_slots_by_binding. A slot's key is `Spell.store_key` (`<spell_id>:<binding_hash>`);
the store records each key on its spell_id's shelf, with its shape (one object, or a `many` list), the first time it
files the key. Purge, `count_spell_creations` and extract/restore walk the shelf and read each slot's recorded shape;
a key without ':' is its own shelf. These tests drive a bare store with spell stand-ins.
"""
import threading
from types import SimpleNamespace
from typing import Any, List
from threading import RLock

import pytest

from melder.aether.conduit.creations.creations import Creations
from melder.aether.spellbook.existence.existence import Existence

SPELL = "a" * 64
OTHER = "b" * 64


def _key(binding: str, spell_id: str = SPELL) -> str:
    """A store key of `spell_id` under the binding hash `binding`."""
    return f"{spell_id}:{binding}"


class Probe:
    """An object that records the disposal methods run on it, into its own list and a shared log."""

    def __init__(self, name: str, log: List[str]) -> None:
        self.name = name
        self.calls: List[str] = []
        self._log = log

    def close(self) -> None:
        """Record `close`."""
        self.calls.append("close")
        self._log.append(f"{self.name}.close")

    def shutdown(self) -> None:
        """Record `shutdown`."""
        self.calls.append("shutdown")
        self._log.append(f"{self.name}.shutdown")


def _spell(existence: Existence, binding: str = "h1", spell_id: str = SPELL) -> SimpleNamespace:
    """A spell stand-in for purge: the spell_id, the store key, the existence and a build lock."""
    return SimpleNamespace(spell_id=spell_id, store_key=_key(binding, spell_id), existence=existence, _lock=RLock())


@pytest.fixture
def store() -> Creations:
    """A fresh store per test."""
    return Creations(owner_conduit_id="conduit-1", id="conduit-1")


def test_every_writer_files_its_key_on_its_spell_ids_shelf(store: Creations) -> None:
    """Each registration verb puts its key on the spell_id's shelf once, in first-filing order, with its shape."""
    log: List[str] = []
    store.add_creation(_key("h1"), Probe("a", log))
    store.add_creation(_key("h2"), Probe("b", log), has_disposal_methods=True, disposal_methods=["close"])
    store.register_slot(_key("h3"), Probe("c", log))
    store.register_many(_key("h4"), Probe("d", log), ["close"])
    store.register_many(_key("h4"), Probe("e", log), ["close"])
    store.add_many_creations(_key("h5"), Probe("f", log), has_disposal_methods=True, disposal_methods=["shutdown"])
    store.add_creation(_key("x1", OTHER), Probe("g", log))
    assert store._shelves[SPELL] == [_key("h1"), _key("h2"), _key("h3"), _key("h4"), _key("h5")]
    assert store._shelves[OTHER] == [_key("x1", OTHER)]
    assert [store._slot_shapes[_key(b)] for b in ("h1", "h2", "h3", "h4", "h5")] == [False, False, False, True, True]
    assert store.count_spell_creations(SPELL) == 6
    assert store.count_spell_creations(OTHER) == 1


def test_count_spell_creations_counts_what_each_slot_holds(store: Creations) -> None:
    """A `many` slot counts its length, any other slot one; an absent, empty or None slot counts nothing."""
    log: List[str] = []
    store.add_creation(_key("u"), Probe("u", log))
    store.register_many(_key("m"), Probe("m1", log), ["close"])
    store.register_many(_key("m"), Probe("m2", log), ["close"])
    store.add_creation(_key("n"), None)
    store.add_creation(_key("l"), [Probe("in-a-list", log)])
    assert store.count_spell_creations(SPELL) == 4
    assert store.count_spell_creations("unknown") == 0


def test_purge_retires_every_slot_of_the_spell_each_with_its_own_record(store: Creations) -> None:
    """A whole purge counts every slot's objects, disposes each slot with its own methods, newest slot first."""
    log: List[str] = []
    old = Probe("old", log)
    news = [Probe("new1", log), Probe("new2", log)]
    other = Probe("other", log)
    store.add_creation(_key("old"), old, has_disposal_methods=True, disposal_methods=["close"])
    for each in news:
        store.register_many(_key("new"), each, ["shutdown"])
    store.add_creation(_key("x", OTHER), other, has_disposal_methods=True, disposal_methods=["close"])
    assert store.purge(_spell(Existence.many, "new")) == 3
    assert log == ["new2.shutdown", "new1.shutdown", "old.close"]
    assert store.count_spell_creations(SPELL) == 0
    assert store.get_creation(_key("x", OTHER)) is other
    assert store.purge(_spell(Existence.many, "new")) == 0


@pytest.mark.parametrize(
    "existence", [Existence.unique, Existence.unique_per_conduit, Existence.many],
    ids=["unique", "unique-per-conduit", "many"],
)
def test_purge_reads_the_recorded_shape_not_the_asking_spells(store: Creations, existence: Existence) -> None:
    """Whatever existence asks, a `many` slot counts its length and a slotted list-valued object counts one."""
    log: List[str] = []
    store.add_creation(_key("u"), [Probe("x", log), Probe("y", log)])
    store.register_many(_key("m"), Probe("m", log), ["close"])
    assert store.purge(_spell(existence, "asker")) == 2


def test_single_object_purge_finds_the_object_in_any_slot(store: Creations) -> None:
    """A single purge retires the one object it is given, from whichever slot of the spell holds it."""
    log: List[str] = []
    old = Probe("old", log)
    kept = Probe("kept", log)
    target = Probe("target", log)
    store.add_creation(_key("old"), old, has_disposal_methods=True, disposal_methods=["close"])
    store.register_many(_key("many"), kept, ["shutdown"])
    store.register_many(_key("many"), target, ["shutdown"])
    asker = _spell(Existence.unique, "other")
    assert store.purge(asker, purge_all=False, creation=target) == 1
    assert store.purge(asker, purge_all=False, creation=old) == 1
    assert store.purge(asker, purge_all=False, creation=Probe("stranger", log)) == 0
    assert log == ["target.shutdown", "old.close"]
    assert store.count_spell_creations(SPELL) == 1


def test_extract_moves_every_slot_with_its_key_and_restore_installs_them(store: Creations) -> None:
    """Extract returns the whole shelf, each row with its key; restore files every row under its key."""
    log: List[str] = []
    one = Probe("one", log)
    many = [Probe("m1", log), Probe("m2", log)]
    store.add_creation(_key("u"), one, has_disposal_methods=True, disposal_methods=["close"])
    for each in many:
        store.register_many(_key("m"), each, ["shutdown"])
    rows = store.extract_spell_creations(SPELL)
    assert [(row["key"], row["scope"], row["stored"]) for row in rows] == [
        (_key("u"), "unique", one), (_key("m"), "many", many[0]), (_key("m"), "many", many[1]),
    ]
    assert store.count_spell_creations(SPELL) == 0
    target = Creations(owner_conduit_id="conduit-2", id="conduit-2")
    target.restore_spell_creations(SPELL, rows)
    assert target.get_creation(_key("u")) is one
    assert target.get_creation(_key("m")) == many
    assert target.count_spell_creations(SPELL) == 3
    target.cleanup()
    assert log == ["m2.shutdown", "m1.shutdown", "one.close"]


def test_restore_replaces_the_target_shelf(store: Creations) -> None:
    """Restore drops, undisposed, every slot of the spell already in the target, then installs the rows."""
    log: List[str] = []
    stale = Probe("stale", log)
    store.add_creation(_key("stale"), stale, has_disposal_methods=True, disposal_methods=["close"])
    moved = Probe("moved", log)
    rows = [{"key": _key("moved"), "scope": "unique", "disposable": True, "stored": moved,
             "disposal_methods": ["shutdown"]}]
    store.restore_spell_creations(SPELL, rows)
    assert store.get_creation(_key("stale")) is None
    assert store.get_creation(_key("moved")) is moved
    store.cleanup()
    assert log == ["moved.shutdown"]


def test_a_row_without_a_key_restores_under_the_spell_id(store: Creations) -> None:
    """A row made before rows carried keys is filed under the bare spell_id, which is its own shelf."""
    log: List[str] = []
    obj = Probe("obj", log)
    store.restore_spell_creations(SPELL, [{"scope": "unique", "disposable": False, "stored": obj}])
    assert store.get_creation(SPELL) is obj
    assert store.count_spell_creations(SPELL) == 1
    assert [row["key"] for row in store.extract_spell_creations(SPELL)] == [SPELL]


def test_a_key_without_a_colon_is_its_own_shelf(store: Creations) -> None:
    """A legacy or test key is the shelf of the spell_id it spells."""
    log: List[str] = []
    store.add_creation("spell-1", Probe("legacy", log), has_disposal_methods=True, disposal_methods=["close"])
    assert store.count_spell_creations("spell-1") == 1
    assert store.purge(SimpleNamespace(spell_id="spell-1", existence=Existence.many)) == 1
    assert log == ["legacy.close"]


def test_the_shelves_survive_reusable_clears_and_go_with_cleanup(store: Creations) -> None:
    """Like the slot guards, the shelf index lives as long as the store; a clear empties the slots only."""
    log: List[str] = []
    store.add_creation(_key("u"), Probe("u", log))
    store.clear_all()
    assert store._shelves[SPELL] == [_key("u")]
    assert store.count_spell_creations(SPELL) == 0
    store.add_creation(_key("u"), Probe("u2", log))
    store.reset_for_pool()
    assert store._shelves[SPELL] == [_key("u")]
    store.add_creation(_key("u"), Probe("u3", log))
    assert store.count_spell_creations(SPELL) == 1
    store.cleanup()
    assert not hasattr(store, "_shelves")
    assert not hasattr(store, "_slot_shapes")


def test_concurrent_first_filings_put_each_key_on_the_shelf_once(store: Creations) -> None:
    """Threads filing different keys of one spell_id, and the same keys again, leave each key on the shelf once."""
    keys = [_key(f"h{index}") for index in range(16)]
    barrier = threading.Barrier(8)
    errors: List[BaseException] = []

    def worker(offset: int) -> None:
        try:
            barrier.wait()
            for round_ in range(50):
                key = keys[(offset + round_) % len(keys)]
                if offset % 2:
                    store.register_many(key + ":m", object(), ["close"])
                else:
                    try:
                        store.add_creation(key, object())
                    except ValueError:
                        pass
        except BaseException as exc:  # pragma: no cover - reported below
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(offset,)) for offset in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert errors == []
    shelf_keys: List[Any] = []
    for shelf in store._shelves.values():
        shelf_keys.extend(shelf)
    assert len(shelf_keys) == len(set(shelf_keys))
    assert set(keys) <= set(store._shelves[SPELL])
