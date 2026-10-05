"""
Unit tests of the many registration trim (2026-10-01).

Scope:
    `Creations.register_many` (the positional hot verb emitted plans call) and the
    `ManyDisposalBucket` record it writes: one record per disposal-bearing many key whose
    `entries` IS the live bucket and whose `methods` is the Spell-owned list recorded once.
    Every reader of that record is exercised through the public store surface: whole-store
    cleanup, reusable clear, whole-target and single-object purge, extract/restore, and the
    refusal of a build that finishes after cleanup.
"""

from typing import List

import pytest

from melder.aether.conduit.creations.creations import Creations, ManyDisposalBucket
from melder.aether.spellbook.existence.existence import Existence


class _Probe:
    """Disposal probe that records the order its methods ran in a shared log."""

    def __init__(self, label: str, log: List[str]) -> None:
        self.label = label
        self.log = log

    def close(self) -> None:
        """First declared method."""
        self.log.append(f"{self.label}:close")

    def dispose(self) -> None:
        """Second declared method."""
        self.log.append(f"{self.label}:dispose")


class _Raising(_Probe):
    """Probe whose first method raises so aggregation can be observed."""

    def close(self) -> None:
        """Raise, then the second method must still run."""
        self.log.append(f"{self.label}:close")
        raise ValueError(self.label)


class _ManySpell:
    """Minimal spell stand-in for purge: an id and an Existence."""

    def __init__(self, spell_id: str, existence: Existence = Existence.many) -> None:
        self.spell_id = spell_id
        self.existence = existence


@pytest.fixture
def store() -> Creations:
    """A fresh store per test."""
    return Creations(owner_conduit_id="conduit-1", id="conduit-1")


@pytest.fixture
def methods() -> List[str]:
    """One Spell-owned method list, shared by every registration of a key."""
    return ["close", "dispose"]


def test_register_many_first_use_creates_bucket_and_record(store: Creations, methods: List[str]) -> None:
    """The first registration creates the live bucket and one record aliasing it."""
    log: List[str] = []
    first = _Probe("a", log)

    store.register_many("spell-many", first, methods)

    bucket = store._creations["spell-many"]
    record = store._disposable_creations["spell-many"]
    assert bucket == [first]
    assert isinstance(record, ManyDisposalBucket)
    assert record.entries is bucket
    assert record.methods is methods


def test_register_many_later_registrations_append_only(store: Creations, methods: List[str]) -> None:
    """Later registrations append to the bucket; the record is unchanged and still aliases it."""
    log: List[str] = []
    probes = [_Probe(label, log) for label in "abc"]
    for probe in probes:
        store.register_many("spell-many", probe, methods)

    bucket = store._creations["spell-many"]
    record = store._disposable_creations["spell-many"]
    assert bucket == probes
    assert record.entries is bucket
    assert len(record.entries) == 3
    assert record.methods is methods


def test_register_many_public_verb_writes_the_same_shape(store: Creations, methods: List[str]) -> None:
    """`add_many_creations` with disposal and `register_many` interleave on one record."""
    log: List[str] = []
    first = _Probe("a", log)
    second = _Probe("b", log)

    store.add_many_creations("spell-many", first, has_disposal_methods=True, disposal_methods=methods)
    store.register_many("spell-many", second, methods)

    record = store._disposable_creations["spell-many"]
    assert record.entries == [first, second]
    assert record.entries is store._creations["spell-many"]
    assert record.methods is methods


def test_cleanup_disposes_newest_first_with_the_keys_methods(store: Creations, methods: List[str]) -> None:
    """Whole-store cleanup runs every object of the record newest-first, methods in declared order."""
    log: List[str] = []
    for label in "abc":
        store.register_many("spell-many", _Probe(label, log), methods)

    store.cleanup()

    assert log == ["c:close", "c:dispose", "b:close", "b:dispose", "a:close", "a:dispose"]


def test_cleanup_orders_keys_newest_first_and_buckets_within(store: Creations, methods: List[str]) -> None:
    """Across keys the registry is walked newest key first; inside a key newest entry first."""
    log: List[str] = []
    store.register_many("leaf", _Probe("leaf1", log), methods)
    store.register_many("root", _Probe("root1", log), methods)
    store.register_many("leaf", _Probe("leaf2", log), methods)
    store.register_many("root", _Probe("root2", log), methods)

    store.cleanup()

    assert [entry.split(":")[0] for entry in log if entry.endswith(":close")] == [
        "root2", "root1", "leaf2", "leaf1",
    ]


def test_cleanup_aggregates_one_error_per_failing_method(store: Creations, methods: List[str]) -> None:
    """A failing method yields one chained RuntimeError and the other methods and objects still run."""
    log: List[str] = []
    store.register_many("spell-many", _Probe("a", log), methods)
    store.register_many("spell-many", _Raising("b", log), methods)

    with pytest.raises(ExceptionGroup) as caught:
        store.cleanup()

    assert len(caught.value.exceptions) == 1
    error = caught.value.exceptions[0]
    assert isinstance(error, RuntimeError)
    assert isinstance(error.__cause__, ValueError)
    assert log == ["b:close", "b:dispose", "a:close", "a:dispose"]


def test_clear_all_disposes_and_leaves_the_store_reusable(store: Creations, methods: List[str]) -> None:
    """A reusable clear disposes the record's objects and a later registration starts a new record."""
    log: List[str] = []
    store.register_many("spell-many", _Probe("a", log), methods)
    old_record = store._disposable_creations["spell-many"]

    store.clear_all()
    assert log == ["a:close", "a:dispose"]
    assert store._creations == {}
    assert store._disposable_creations == {}

    store.register_many("spell-many", _Probe("b", log), methods)
    new_record = store._disposable_creations["spell-many"]
    assert new_record is not old_record
    assert new_record.entries is store._creations["spell-many"]


def test_purge_all_disposes_the_bucket_and_removes_both_keys(store: Creations, methods: List[str]) -> None:
    """Whole-target purge detaches the bucket and its record and disposes newest-first."""
    log: List[str] = []
    for label in "ab":
        store.register_many("spell-many", _Probe(label, log), methods)

    count = store.purge(_ManySpell("spell-many"))

    assert count == 2
    assert "spell-many" not in store._creations
    assert "spell-many" not in store._disposable_creations
    assert log == ["b:close", "b:dispose", "a:close", "a:dispose"]


def test_purge_single_disposes_only_that_object_with_the_keys_methods(
        store: Creations, methods: List[str],
) -> None:
    """Single-object purge removes one entry from the aliased bucket and disposes it alone."""
    log: List[str] = []
    probes = [_Probe(label, log) for label in "abc"]
    for probe in probes:
        store.register_many("spell-many", probe, methods)

    count = store.purge(_ManySpell("spell-many"), purge_all=False, creation=probes[1])

    assert count == 1
    assert log == ["b:close", "b:dispose"]
    bucket = store._creations["spell-many"]
    record = store._disposable_creations["spell-many"]
    assert bucket == [probes[0], probes[2]]
    assert record.entries is bucket
    assert record.methods is methods


def test_purge_single_of_last_entry_removes_bucket_and_record(store: Creations, methods: List[str]) -> None:
    """Retiring the last object of a key removes the live bucket and the record together."""
    log: List[str] = []
    probe = _Probe("a", log)
    store.register_many("spell-many", probe, methods)

    assert store.purge(_ManySpell("spell-many"), purge_all=False, creation=probe) == 1
    assert "spell-many" not in store._creations
    assert "spell-many" not in store._disposable_creations
    assert log == ["a:close", "a:dispose"]


def test_purge_single_absent_reference_changes_nothing(store: Creations, methods: List[str]) -> None:
    """An object that is not retained under the key returns zero and disposes nothing."""
    log: List[str] = []
    store.register_many("spell-many", _Probe("a", log), methods)

    assert store.purge(_ManySpell("spell-many"), purge_all=False, creation=_Probe("x", log)) == 0
    assert log == []
    assert len(store._creations["spell-many"]) == 1


def test_extract_rows_carry_the_keys_methods_and_restore_rebuilds_one_record(
        store: Creations, methods: List[str],
) -> None:
    """Extract yields one row per object with the key's list; restore rebuilds the aliased record."""
    log: List[str] = []
    probes = [_Probe(label, log) for label in "ab"]
    for probe in probes:
        store.register_many("spell-many", probe, methods)

    rows = store.extract_spell_creations("spell-many")

    assert [row["stored"] for row in rows] == probes
    assert all(row["scope"] == "many" and row["disposable"] for row in rows)
    assert all(row["disposal_methods"] is methods for row in rows)
    assert "spell-many" not in store._creations
    assert "spell-many" not in store._disposable_creations

    target = Creations(owner_conduit_id="conduit-2", id="conduit-2")
    target.restore_spell_creations("spell-many", rows)

    bucket = target._creations["spell-many"]
    record = target._disposable_creations["spell-many"]
    assert bucket == probes
    assert record.entries is bucket
    assert record.methods is methods
    target.cleanup()
    assert log == ["b:close", "b:dispose", "a:close", "a:dispose"]


def test_extract_restore_of_a_plain_many_key_keeps_it_plain(store: Creations) -> None:
    """A many key registered without disposal round-trips with no record."""
    first = object()
    store.add_many_creations("spell-plain", first)

    rows = store.extract_spell_creations("spell-plain")
    assert rows == [{"scope": "many", "disposable": False, "stored": first}]

    store.restore_spell_creations("spell-plain", rows)
    assert store._creations["spell-plain"] == [first]
    assert "spell-plain" not in store._disposable_creations


def test_restore_refuses_rows_that_disagree_on_disposable(store: Creations, methods: List[str]) -> None:
    """Rows of one many key must agree on `disposable`; a mix is refused loudly."""
    first = object()
    second = object()
    mixed = [
        {"scope": "many", "disposable": True, "stored": first, "disposal_methods": methods},
        {"scope": "many", "disposable": False, "stored": second},
    ]
    with pytest.raises(RuntimeError, match="without disposal methods"):
        store.restore_spell_creations("spell-many", mixed)

    reversed_mix = [
        {"scope": "many", "disposable": False, "stored": second},
        {"scope": "many", "disposable": True, "stored": first, "disposal_methods": methods},
    ]
    with pytest.raises(RuntimeError, match="beside entries restored without"):
        store.restore_spell_creations("spell-other", reversed_mix)


def test_public_verb_refuses_mixed_declarations_both_ways(store: Creations, methods: List[str]) -> None:
    """The checked verb refuses a plain registration under a disposal-bearing key and the reverse."""
    log: List[str] = []
    store.register_many("spell-a", _Probe("a", log), methods)
    with pytest.raises(ValueError, match="one disposal declaration"):
        store.add_many_creations("spell-a", object())
    assert len(store._creations["spell-a"]) == 1

    store.add_many_creations("spell-b", object())
    with pytest.raises(ValueError, match="one disposal declaration"):
        store.add_many_creations("spell-b", _Probe("b", log), has_disposal_methods=True, disposal_methods=methods)
    assert len(store._creations["spell-b"]) == 1
    assert "spell-b" not in store._disposable_creations


def test_public_verb_refuses_a_singleton_slot_before_appending(store: Creations, methods: List[str]) -> None:
    """A many registration under a singleton key is refused and the slot is untouched."""
    singleton = object()
    store.add_creation("spell-s", singleton)

    with pytest.raises(ValueError, match="non-list slot"):
        store.add_many_creations("spell-s", object(), has_disposal_methods=True, disposal_methods=methods)
    assert store._creations["spell-s"] is singleton
    assert "spell-s" not in store._disposable_creations


def test_register_many_into_cleaned_store_disposes_and_raises(store: Creations, methods: List[str]) -> None:
    """A build that finishes after cleanup is refused through the hot verb and its methods run."""
    log: List[str] = []
    store.cleanup()

    with pytest.raises(RuntimeError, match="was cleaned while creation"):
        store.register_many("spell-many", _Probe("late", log), methods)

    assert log == ["late:close", "late:dispose"]


def test_register_many_into_cleaned_store_chains_the_disposal_failure(
        store: Creations, methods: List[str],
) -> None:
    """The refusal chains the disposal failure of the stranded object."""
    log: List[str] = []
    store.cleanup()

    with pytest.raises(RuntimeError) as caught:
        store.register_many("spell-many", _Raising("late", log), methods)

    assert isinstance(caught.value.__cause__, RuntimeError)
    assert isinstance(caught.value.__cause__.__cause__, ValueError)
    assert log == ["late:close", "late:dispose"]


def test_reset_for_pool_fast_path_ignores_plain_buckets_only(store: Creations, methods: List[str]) -> None:
    """A pool reset with a record present takes the disposing path; without one it only clears."""
    log: List[str] = []
    store.add_many_creations("spell-plain", object())
    store.reset_for_pool()
    assert store._creations == {}

    store.register_many("spell-many", _Probe("a", log), methods)
    store.reset_for_pool()
    assert log == ["a:close", "a:dispose"]
    assert store._creations == {} and store._disposable_creations == {}


def test_record_fields_are_borrowed_not_copied(store: Creations, methods: List[str]) -> None:
    """The record never copies: appending to the live bucket is visible through it, and vice versa."""
    log: List[str] = []
    store.register_many("spell-many", _Probe("a", log), methods)
    record = store._disposable_creations["spell-many"]
    extra = _Probe("b", log)

    store._creations["spell-many"].append(extra)
    assert record.entries[-1] is extra
    methods.append("close")
    assert record.methods == ["close", "dispose", "close"]
