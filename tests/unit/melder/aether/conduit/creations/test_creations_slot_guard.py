"""
Unit contracts for `Creations` slot guards and the leaf store lock.

Background: before 2026-09-25 generated meld code held the store lock across whole
builds, which deadlocked against `unique` builders. Build-once exclusion now lives in
one build guard per slot (`Creations.slot_guard`), and the store lock is a leaf that
publication takes by itself. These tests pin the store-side half of that contract;
tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py
pins the end-to-end behaviour.
"""

from threading import Event, RLock, Thread
from typing import List

import pytest

from melder.aether.conduit.creations.creations import Creations
from melder.aether.spellbook.existence.existence import Existence


class DisposalProbe:
    """Records disposal calls so tests can observe refused publications."""

    def __init__(self) -> None:
        """Start with an empty call log."""
        self.calls: List[str] = []

    def close(self) -> None:
        """Record one disposal call."""
        self.calls.append("close")


class SpellStub:
    """
    Minimal stand-in for the two Spell attributes `Creations.purge` reads.

    Contract:
        Exposes `spell_id`, `existence` and `_lock` only; purge never reaches further.
    """

    def __init__(self, spell_id: str, existence: Existence) -> None:
        """
        Args:
            spell_id: Slot key used by the store.
            existence: Existence that selects the purge lock family.
        """
        self.spell_id: str = spell_id
        self.existence: Existence = existence
        self._lock: RLock = RLock()


BLOCK_TIMEOUT_SECONDS: float = 5.0
SHORT_WAIT_SECONDS: float = 0.2


@pytest.fixture()
def creations() -> Creations:
    """Build one scoped store for direct unit checks."""
    return Creations(owner_conduit_id="conduit-normal", id="scope-a")


def _run_in_thread(target: object) -> Thread:
    """
    Start a daemon thread for a zero-argument callable.

    Args:
        target: Callable to run.

    Returns:
        Thread: The started thread.
    """
    thread = Thread(target=target, daemon=True)
    thread.start()
    return thread


def test_slot_guard_is_stable_per_spell_id_and_distinct_across_ids(creations: Creations) -> None:
    """A slot keeps one guard; different slots never share one."""
    first = creations.slot_guard("spell-a")

    assert creations.slot_guard("spell-a") is first
    assert creations.slot_guard("spell-b") is not first


def test_slot_guard_survives_reusable_clear(creations: Creations) -> None:
    """Guards are per spell id, not per store generation, so clearing keeps them."""
    guard = creations.slot_guard("spell-a")
    creations.add_creation("spell-a", object())

    creations.clear_all()

    assert creations.slot_guard("spell-a") is guard


def test_slot_guard_is_reentrant_for_door_then_root_step(creations: Creations) -> None:
    """The door and the root plan step take the same guard on one thread."""
    guard = creations.slot_guard("spell-a")

    with guard:
        with creations.slot_guard("spell-a"):
            creations.add_creation("spell-a", "built")

    assert creations.get_creation("spell-a") == "built"


def test_holding_a_slot_guard_does_not_block_other_slots_publishing(creations: Creations) -> None:
    """The store lock is not held by a guard holder, so other slots publish freely."""
    published = Event()

    def publish_other_slot() -> None:
        creations.add_creation("spell-b", "other")
        published.set()

    with creations.slot_guard("spell-a"):
        thread = _run_in_thread(publish_other_slot)
        assert published.wait(BLOCK_TIMEOUT_SECONDS)
    thread.join(BLOCK_TIMEOUT_SECONDS)

    assert creations.get_creation("spell-b") == "other"


@pytest.mark.parametrize(
    "existence",
    [
        Existence.unique_per_conduit,
        Existence.unique_per_spell_space,
        Existence.unique_per_conduit_lineage,
        Existence.unique_per_conduit_cluster,
    ],
)
def test_purge_waits_for_an_in_flight_build_of_the_same_slot(
        creations: Creations,
        existence: Existence,
) -> None:
    """Purge of a slotted existence takes the slot guard, so it cannot retire a half-built slot."""
    spell = SpellStub("spell-a", existence)
    purged: List[int] = []

    def purge() -> None:
        purged.append(creations.purge(spell))

    with creations.slot_guard("spell-a"):
        thread = _run_in_thread(purge)
        thread.join(SHORT_WAIT_SECONDS)
        assert thread.is_alive(), "purge did not wait for the in-flight build"
        creations.add_creation("spell-a", "built")
    thread.join(BLOCK_TIMEOUT_SECONDS)

    assert purged == [1]
    assert creations.get_creation("spell-a") is None


def test_purge_of_unique_uses_the_spell_lock_not_the_slot_guard(creations: Creations) -> None:
    """`unique` keeps Spell._lock as its build lock; its store guard plays no part."""
    spell = SpellStub("spell-u", Existence.unique)
    creations.add_creation("spell-u", "built")

    with creations.slot_guard("spell-u"):
        assert creations.purge(spell) == 1


def test_clear_all_does_not_wait_for_an_in_flight_build(creations: Creations) -> None:
    """A reusable clear swaps the registries under the leaf lock without waiting for builders."""
    cleared = Event()

    def clear() -> None:
        creations.clear_all()
        cleared.set()

    creations.add_creation("spell-old", "old")
    with creations.slot_guard("spell-a"):
        thread = _run_in_thread(clear)
        assert cleared.wait(BLOCK_TIMEOUT_SECONDS)
        creations.add_creation("spell-a", "built-after-clear")
    thread.join(BLOCK_TIMEOUT_SECONDS)

    assert creations.get_creation("spell-old") is None
    assert creations.get_creation("spell-a") == "built-after-clear"


def test_add_creation_into_cleaned_store_disposes_and_raises(creations: Creations) -> None:
    """A build that finishes after cleanup is refused and its object disposed."""
    probe = DisposalProbe()
    creations.cleanup()

    with pytest.raises(RuntimeError, match="was cleaned while creation 'spell-a'"):
        creations.add_creation("spell-a", probe, has_disposal_methods=True, disposal_methods=["close"])

    assert probe.calls == ["close"]


def test_add_many_creations_into_cleaned_store_disposes_and_raises(creations: Creations) -> None:
    """The many append refuses a cleaned store the same way."""
    probe = DisposalProbe()
    creations.cleanup()

    with pytest.raises(RuntimeError, match="was cleaned while creation 'spell-m'"):
        creations.add_many_creations("spell-m", probe, has_disposal_methods=True, disposal_methods=["close"])

    assert probe.calls == ["close"]


def test_refused_publication_without_disposal_methods_disposes_nothing(creations: Creations) -> None:
    """Objects that declared no disposal methods are not touched, only refused."""
    probe = DisposalProbe()
    creations.cleanup()

    with pytest.raises(RuntimeError, match="not registered\\."):
        creations.add_creation("spell-a", probe)

    assert probe.calls == []


def test_refused_publication_chains_a_failing_disposal(creations: Creations) -> None:
    """A disposal failure during refusal is kept as the cause, not swallowed."""
    creations.cleanup()

    with pytest.raises(RuntimeError) as raised:
        creations.add_creation("spell-a", object(), has_disposal_methods=True, disposal_methods=["close"])

    assert isinstance(raised.value.__cause__, RuntimeError)
    assert "Failed to dispose object" in str(raised.value.__cause__)
