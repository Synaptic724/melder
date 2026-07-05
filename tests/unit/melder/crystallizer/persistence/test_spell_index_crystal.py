"""
Unit contract tests for SpellIndexCrystal: the record's membership map
(dispatch, replace-on-emit, eviction + tombstone capture, subtree sweep).
"""
import pytest

from melder.crystallizer.persistence.crystals.spell_index_crystal import (
    SpellIndexCrystal,
)
from melder.crystallizer.persistence.persistence_profile import PersistenceProfile


def _index(index_id="idx-1", book="book-1", selected="sha-a", members=("sha-a",)):
    """Build one membership twin."""
    return SpellIndexCrystal(
        index_id=index_id,
        spellbook_id=book,
        selected_spell_id=selected,
        member_spell_ids=list(members),
    )


def test_dispatch_and_describe_detachment():
    """
    Purpose:
        Verify record() routes index twins and describe() detaches.
    Contract:
        The twin lands in its level map (spell_index_count), journals kind
        "spell_index", and mutating a described member list never touches
        the twin.
    Returns:
        None.
    Raises:
        AssertionError: If dispatch or detachment drifts.
    """
    profile = PersistenceProfile("p")
    twin = _index(members=("sha-a", "sha-b"))
    profile.record(twin)
    assert profile.describe()["spell_index_count"] == 1
    described = twin.describe()
    described["member_spell_ids"].append("sha-x")
    assert twin.describe()["member_spell_ids"] == ["sha-a", "sha-b"]
    _payloads, entries, _rng = profile.capture_segment_since(0)
    assert entries == [(1, "spell_index", "idx-1")]


def test_replace_on_emit_keeps_one_snapshot_per_index():
    """
    Purpose:
        Verify membership snapshots replace by index_id.
    Contract:
        A re-emitted index displaces + cleans the previous snapshot; the
        capture window reports the CURRENT membership.
    Returns:
        None.
    Raises:
        AssertionError: If stale snapshots survive.
    """
    profile = PersistenceProfile("p")
    first = _index(members=("sha-a",))
    profile.record(first)
    profile.record(_index(members=("sha-a", "sha-b"), selected="sha-b"))
    assert first.cleaned is True
    assert profile.describe()["spell_index_count"] == 1
    payloads, _entries, _rng = profile.capture_segment_since(0)
    snapshot = payloads["spell_index"]["idx-1"]
    assert snapshot["member_spell_ids"] == ["sha-a", "sha-b"]
    assert snapshot["selected_spell_id"] == "sha-b"


def test_removal_evicts_and_captures_tombstone():
    """
    Purpose:
        Verify index destruction leaves the record truthfully.
    Contract:
        remove_spell_index_crystal cleans + evicts the twin, tolerates an
        unrecorded index, and captures the {"index_id", "removed"}
        tombstone.
    Returns:
        None.
    Raises:
        AssertionError: If eviction or capture drifts.
    """
    profile = PersistenceProfile("p")
    twin = _index()
    profile.record(twin)
    profile.remove_spell_index_crystal("idx-1")
    assert twin.cleaned is True
    assert profile.describe()["spell_index_count"] == 0
    profile.remove_spell_index_crystal("ghost-idx")
    payloads, _entries, _rng = profile.capture_segment_since(0)
    assert payloads["spell_index_removed"]["idx-1"] == {
        "index_id": "idx-1", "removed": True,
    }
    assert payloads["spell_index_removed"]["ghost-idx"] == {
        "index_id": "ghost-idx", "removed": True,
    }


def test_subtree_sweep_takes_index_twins_by_owner_edge():
    """
    Purpose:
        Verify book death sweeps its membership twins.
    Contract:
        remove_spellbook_subtree evicts index twins whose spellbook_id
        matches; a sibling book's index survives.
    Returns:
        None.
    Raises:
        AssertionError: If the sweep misses or over-reaches.
    """
    profile = PersistenceProfile("p")
    doomed = _index(index_id="idx-1", book="book-1")
    survivor = _index(index_id="idx-2", book="book-2")
    profile.record(doomed)
    profile.record(survivor)
    profile.remove_spellbook_subtree("book-1")
    assert doomed.cleaned is True
    assert survivor.cleaned is False
    assert profile.describe()["spell_index_count"] == 1
