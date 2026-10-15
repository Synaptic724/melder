"""
Unit tests of holder-owned many children (EPIC-2026-10-14-slotted_lifetime_ownership_fixes, 0.2.8238).

Scope:
    `Creations.adopt_children` - the verb an emitted miss calls right after it publishes a slotted holder - and the
    `HolderDisposalEntry` it writes: the holder, its own disposal list (possibly empty) and the disposal-bearing
    `many` children it adopted, each with its spell's list. Every reader of that record is exercised through the
    store surface: whole-store cleanup and reusable clear, whole-target and single-object purge, a `many` purge of
    the child spell, and extract/restore (the rows an ownership transfer moves).
"""

from threading import RLock
from typing import List

import pytest

from melder.aether.conduit.creations.creations import Creations, HolderDisposalEntry, ManyDisposalBucket
from melder.aether.spellbook.existence.existence import Existence


class _Probe:
    """Disposal probe that records its label in a shared log each time Melder runs its `close`."""

    def __init__(self, label: str, log: List[str]) -> None:
        """
        Keep the label and the shared log.

        Args:
            label: Name written to the log on every close.
            log: The test's shared, ordered disposal log.
        """
        self.label = label
        self.log = log

    def close(self) -> None:
        """Record one disposal."""
        self.log.append(self.label)


class _Raising(_Probe):
    """Probe whose `close` records the call and then raises a ValueError carrying its label."""

    def close(self) -> None:
        """Record one disposal, then fail."""
        super().close()
        raise ValueError(self.label)


class _Spell:
    """Spell stand-in for purge: an id, an Existence and the build lock a `unique` purge takes."""

    def __init__(self, spell_id: str, existence: Existence) -> None:
        """
        Keep the id and the Existence.

        Args:
            spell_id: The spell id the store keys the target by.
            existence: The target's Existence.
        """
        self.spell_id = spell_id
        self.existence = existence
        self._lock = RLock()


@pytest.fixture
def store() -> Creations:
    """A fresh store per test."""
    return Creations(owner_conduit_id="conduit-1", id="conduit-1")


@pytest.fixture
def log() -> List[str]:
    """The test's shared disposal log."""
    return []


@pytest.fixture
def child_methods() -> List[str]:
    """The child Spell's own method list: one object for every registration of the child key."""
    return ["close"]


@pytest.fixture
def holder_methods() -> List[str]:
    """The holder Spell's own method list."""
    return ["close"]


def _publish(store: Creations, holder: object, methods: List[str]) -> None:
    """
    Publish a holder the way an emitted miss does: through `add_creation` when it declares disposal methods.

    Args:
        store: The holder's store.
        holder: The holder object.
        methods: Its disposal methods; an empty list publishes without disposal metadata.
    """
    if methods:
        store.add_creation("holder", holder, has_disposal_methods=True, disposal_methods=methods)
    else:
        store.add_creation("holder", holder)


def test_adoption_moves_the_child_from_its_bucket_into_the_holders_record(
        store: Creations, log: List[str], child_methods: List[str], holder_methods: List[str]) -> None:
    """The child leaves its spell's bucket (dropped when empty) and joins the holder's record with its own list."""
    child = _Probe("child", log)
    holder = _Probe("holder", log)
    store.register_many("child", child, child_methods)
    _publish(store, holder, holder_methods)

    store.adopt_children("holder", holder, (("child", child),))

    assert "child" not in store._creations and "child" not in store._disposable_creations
    record = store._disposable_creations["holder"]
    assert isinstance(record, HolderDisposalEntry)
    assert record.item is holder and record.methods is holder_methods
    assert record.children == [(child, child_methods)] and record.children[0][1] is child_methods
    assert store.get_creation("holder") is holder


def test_a_holder_without_disposal_methods_gets_a_record_for_its_children(
        store: Creations, log: List[str], child_methods: List[str]) -> None:
    """A holder published without disposal metadata gets a record with no methods of its own."""
    child = _Probe("child", log)
    holder = _Probe("holder", log)
    store.register_many("child", child, child_methods)
    _publish(store, holder, [])
    assert "holder" not in store._disposable_creations

    store.adopt_children("holder", holder, (("child", child),))

    record = store._disposable_creations["holder"]
    assert isinstance(record, HolderDisposalEntry)
    assert record.methods == [] and record.children == [(child, child_methods)]
    store.cleanup()
    assert log == ["child"], "the holder runs no method; its child is still disposed"


def test_adoption_takes_only_the_identical_child_and_keeps_the_rest_of_the_bucket(
        store: Creations, log: List[str], child_methods: List[str], holder_methods: List[str]) -> None:
    """Free children registered before and after the holder's child stay in the bucket, which the record aliases."""
    early, late = _Probe("early", log), _Probe("late", log)
    child = _Probe("child", log)
    holder = _Probe("holder", log)
    store.register_many("child", early, child_methods)
    store.register_many("child", child, child_methods)
    store.register_many("child", late, child_methods)
    _publish(store, holder, holder_methods)

    store.adopt_children("holder", holder, (("child", child),))

    assert store._creations["child"] == [early, late]
    bucket_record = store._disposable_creations["child"]
    assert isinstance(bucket_record, ManyDisposalBucket) and bucket_record.entries is store._creations["child"]
    assert store._disposable_creations["holder"].children == [(child, child_methods)]


def test_a_child_that_is_no_longer_in_its_bucket_is_skipped(
        store: Creations, log: List[str], child_methods: List[str], holder_methods: List[str]) -> None:
    """A purged child and a child its bucket never held are skipped; with no child found the tuple stays."""
    purged = _Probe("purged", log)
    other = _Probe("other", log)
    never = _Probe("never", log)
    holder = _Probe("holder", log)
    store.register_many("purged", purged, child_methods)
    assert store.purge(_Spell("purged", Existence.many)) == 1
    store.register_many("other", other, child_methods)
    _publish(store, holder, holder_methods)

    store.adopt_children("holder", holder, (("purged", purged), ("other", never)))

    assert store._disposable_creations["holder"] == (holder, holder_methods)
    assert store._creations["other"] == [other]
    assert log == ["purged"]


def test_adoption_does_nothing_after_a_whole_store_clear_or_cleanup(
        store: Creations, log: List[str], child_methods: List[str], holder_methods: List[str]) -> None:
    """A clear that swapped the registries after publication, or a cleanup, leaves nothing to adopt and no error."""
    child = _Probe("child", log)
    holder = _Probe("holder", log)
    store.register_many("child", child, child_methods)
    _publish(store, holder, holder_methods)
    store.clear_all()
    assert log == ["holder", "child"]

    store.adopt_children("holder", holder, (("child", child),))

    assert store._creations == {} and store._disposable_creations == {}
    store.cleanup()
    store.adopt_children("holder", holder, (("child", child),))
    assert log == ["holder", "child"]


def test_whole_store_disposal_runs_the_holder_then_its_children_newest_first_in_creation_order(
        store: Creations, log: List[str], child_methods: List[str], holder_methods: List[str]) -> None:
    """The record keeps the holder's position: later entries first, then the holder, its children, earlier entries."""
    early = _Probe("early", log)
    store.add_creation("early", early, has_disposal_methods=True, disposal_methods=["close"])
    first, second = _Probe("first", log), _Probe("second", log)
    holder = _Probe("holder", log)
    store.register_many("child", first, child_methods)
    store.register_many("child", second, child_methods)
    _publish(store, holder, holder_methods)
    store.adopt_children("holder", holder, (("child", first), ("child", second)))
    late = _Probe("late", log)
    store.add_creation("late", late, has_disposal_methods=True, disposal_methods=["close"])

    store.cleanup()

    assert log == ["late", "holder", "second", "first", "early"]


def test_clear_all_aggregates_holder_and_child_failures_and_stays_reusable(
        store: Creations, log: List[str], child_methods: List[str], holder_methods: List[str]) -> None:
    """Every method runs; each failure is one chained error, holder first; the store takes new entries after."""
    child = _Raising("child", log)
    holder = _Raising("holder", log)
    store.register_many("child", child, child_methods)
    _publish(store, holder, holder_methods)
    store.adopt_children("holder", holder, (("child", child),))

    with pytest.raises(ExceptionGroup) as raised:
        store.clear_all()

    assert log == ["holder", "child"]
    assert [str(error.__cause__) for error in raised.value.exceptions] == ["holder", "child"]
    store.add_creation("holder", _Probe("again", log))
    assert store.get_creation("holder") is not holder


@pytest.mark.parametrize("existence", [Existence.unique, Existence.unique_per_conduit])
def test_purge_of_the_holder_disposes_it_and_then_its_children_and_counts_one(
        existence: Existence, store: Creations, log: List[str], child_methods: List[str],
        holder_methods: List[str]) -> None:
    """A whole-target purge detaches the record with the holder; the count is the holder's own entry."""
    first, second = _Probe("first", log), _Probe("second", log)
    holder = _Probe("holder", log)
    store.register_many("child", first, child_methods)
    store.register_many("child", second, child_methods)
    _publish(store, holder, holder_methods)
    store.adopt_children("holder", holder, (("child", first), ("child", second)))

    assert store.purge(_Spell("holder", existence)) == 1

    assert log == ["holder", "second", "first"]
    assert store._creations == {} and store._disposable_creations == {}


def test_single_object_purge_of_the_holder_takes_its_children(
        store: Creations, log: List[str], child_methods: List[str], holder_methods: List[str]) -> None:
    """Purging the holder by reference disposes it and its child; another reference purges nothing."""
    child = _Probe("child", log)
    holder = _Probe("holder", log)
    store.register_many("child", child, child_methods)
    _publish(store, holder, holder_methods)
    store.adopt_children("holder", holder, (("child", child),))
    spell = _Spell("holder", Existence.unique_per_conduit)

    assert store.purge(spell, purge_all=False, creation=object()) == 0
    assert store.purge(spell, purge_all=False, creation=holder) == 1

    assert log == ["holder", "child"]


def test_a_many_purge_of_the_child_spell_leaves_adopted_children_alone(
        store: Creations, log: List[str], child_methods: List[str], holder_methods: List[str]) -> None:
    """Only the free child is the many spell's own entry; the holder's child stays in the holder's record."""
    free = _Probe("free", log)
    child = _Probe("child", log)
    holder = _Probe("holder", log)
    store.register_many("child", free, child_methods)
    store.register_many("child", child, child_methods)
    _publish(store, holder, holder_methods)
    store.adopt_children("holder", holder, (("child", child),))

    assert store.purge(_Spell("child", Existence.many)) == 1

    assert log == ["free"]
    assert store._disposable_creations["holder"].children == [(child, child_methods)]


def test_extract_carries_the_children_with_the_holder_and_restore_rebuilds_its_record(
        store: Creations, log: List[str], child_methods: List[str], holder_methods: List[str]) -> None:
    """The holder's row lists its children; a restore elsewhere rebuilds the record that disposes all of them."""
    first, second = _Probe("first", log), _Probe("second", log)
    holder = _Probe("holder", log)
    store.register_many("child", first, child_methods)
    store.register_many("child", second, child_methods)
    _publish(store, holder, holder_methods)
    store.adopt_children("holder", holder, (("child", first), ("child", second)))

    rows = store.extract_spell_creations("holder")

    assert rows == [{
        "scope": "unique",
        "disposable": True,
        "stored": holder,
        "disposal_methods": holder_methods,
        "children": [
            {"stored": first, "disposal_methods": child_methods},
            {"stored": second, "disposal_methods": child_methods},
        ],
    }]
    assert rows[0]["disposal_methods"] is holder_methods
    assert store._creations == {} and store._disposable_creations == {}
    target = Creations(owner_conduit_id="conduit-2", id="conduit-2")
    target.restore_spell_creations("holder", rows)
    record = target._disposable_creations["holder"]
    assert isinstance(record, HolderDisposalEntry)
    assert record.item is holder and record.methods is holder_methods
    assert record.children == [(first, child_methods), (second, child_methods)]
    store.cleanup()
    assert log == []
    target.cleanup()
    assert log == ["holder", "second", "first"]


def test_extract_of_a_holder_without_methods_is_disposable_with_an_empty_list(
        store: Creations, log: List[str], child_methods: List[str]) -> None:
    """The row of a holder that runs no method of its own still carries its child, so the move takes it."""
    child = _Probe("child", log)
    holder = _Probe("holder", log)
    store.register_many("child", child, child_methods)
    _publish(store, holder, [])
    store.adopt_children("holder", holder, (("child", child),))

    rows = store.extract_spell_creations("holder")

    assert rows[0]["disposable"] is True and rows[0]["disposal_methods"] == []
    assert rows[0]["children"] == [{"stored": child, "disposal_methods": child_methods}]


def test_a_row_without_children_restores_the_plain_tuple(
        store: Creations, log: List[str], holder_methods: List[str]) -> None:
    """Control: rows that carry no children restore exactly as before 0.2.8238."""
    holder = _Probe("holder", log)
    _publish(store, holder, holder_methods)
    rows = store.extract_spell_creations("holder")
    assert "children" not in rows[0]

    store.restore_spell_creations("holder", rows)

    assert store._disposable_creations["holder"] == (holder, holder_methods)
