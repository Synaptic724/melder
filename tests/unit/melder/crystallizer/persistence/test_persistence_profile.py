"""
Unit contract tests for PersistenceProfile: custody locations, removal
eviction, state switches, journaling, and incremental segment capture.

The profile is pure in-memory record structure (no melder runtime world), so
these are isolated unit tests; the only stand-in is a light spell-custody
crystal (the real SpellCrystal requires a live spell + AST walk, which is
integration scope).
"""
import pytest

from melder.crystallizer.crystals.aether_crystal import AetherCrystal
from melder.crystallizer.crystals.aetheric_frame_crystal import (
    AethericFrameCrystal,
)
from melder.crystallizer.crystals.conduit_crystal import ConduitCrystal
from melder.crystallizer.crystals.mutation_research_crystal import (
    MutationResearchCrystal,
)
from melder.crystallizer.crystals.nexus_crystal import NexusCrystal
from melder.crystallizer.crystals.spellbook_crystal import (
    SpellbookCrystal,
)
from melder.crystallizer.persistence.persistence_profile import PersistenceProfile
from melder.crystallizer.crystals.recorded_unit_state import RecordedUnitState


class _StubSpellCrystal:
    """
    Light custody stand-in exposing exactly what the profile reads.

    Contract:
        - `id` is the spell SHA identity (SpellCrystal.id contract).
        - `spellbook_id` is the parent edge the subtree sweeps match on.
        - `cleaned`/`cleanup()` mirror the Cleanable surface.
        - `describe()` returns detached plain data for segment capture.
    """

    def __init__(self, spell_id, spellbook_id=None):
        self.id = spell_id
        self.spellbook_id = spellbook_id
        self.cleaned = False

    def cleanup(self):
        self.cleaned = True

    def describe(self):
        return {"spell_id": self.id, "spellbook_id": self.spellbook_id}


def _frame(name="frame-a"):
    """Build one real frame twin for dispatch tests."""
    return AethericFrameCrystal(
        frame_name=name,
        system_state_name="dynamic",
        rift_enabled=True,
        ai_native_enabled=True,
    )


def _book(book_id="book-1", frame_name="frame-a"):
    """Build one real spellbook twin for dispatch/subtree tests."""
    return SpellbookCrystal(spellbook_id=book_id, frame_name=frame_name)


def _conduit(conduit_id="conduit-1", book_id="book-1"):
    """Build one real conduit twin carrying the spellbook parent edge."""
    return ConduitCrystal(
        conduit_id=conduit_id,
        spellbook_id=book_id,
        conduit_name="root",
        policy_name="policy",
        dynamic=True,
    )


def test_record_dispatches_each_twin_kind_and_journals():
    """
    Purpose:
        Verify record() routes every twin kind to its level container.
    Contract:
        Singletons, frame-by-name, book/conduit-by-id all land; each
        emission journals one entry (sequence strictly increases).
    Returns:
        None.
    Raises:
        AssertionError: If a twin kind fails to land or journal.
    """
    profile = PersistenceProfile("p")
    profile.record(AetherCrystal())
    profile.record(NexusCrystal(configured=True, enabled=True))
    profile.record(MutationResearchCrystal(activated=True))
    profile.record(_frame())
    profile.record(_book())
    profile.record(_conduit())
    summary = profile.describe()
    assert summary["has_aether_crystal"] is True
    assert summary["has_nexus_crystal"] is True
    assert summary["has_mutation_research_crystal"] is True
    assert summary["frame_count"] == 1
    assert summary["spellbook_count"] == 1
    assert summary["conduit_count"] == 1
    _payloads, entries, _rng = profile.capture_segment_since(0)
    assert [entry[1] for entry in entries] == [
        "aether", "nexus", "mutation_research", "frame", "spellbook", "conduit",
    ]
    assert [entry[0] for entry in entries] == [1, 2, 3, 4, 5, 6]


def test_record_replaces_and_cleans_displaced_singleton():
    """
    Purpose:
        Verify replace-on-emit for a singleton twin.
    Contract:
        The displaced aether twin is cleaned; the new one is held.
    Returns:
        None.
    Raises:
        AssertionError: If the displaced twin survives uncleaned.
    """
    profile = PersistenceProfile("p")
    first = AetherCrystal()
    profile.record(first)
    profile.record(AetherCrystal())
    assert first.cleaned is True
    assert profile.describe()["has_aether_crystal"] is True


def test_record_replaces_mapped_twin_by_key_and_keeps_siblings():
    """
    Purpose:
        Verify keyed replace-on-emit within one level map.
    Contract:
        Same-name frame replaces (old cleaned); different name coexists.
    Returns:
        None.
    Raises:
        AssertionError: If replacement leaks or siblings are lost.
    """
    profile = PersistenceProfile("p")
    original = _frame("frame-a")
    profile.record(original)
    profile.record(_frame("frame-a"))
    profile.record(_frame("frame-b"))
    assert original.cleaned is True
    assert profile.describe()["frame_count"] == 2


def test_record_rejects_unsupported_twin_type():
    """
    Purpose:
        Verify the dispatch guard on unknown twin types.
    Contract:
        record() raises TypeError naming the offending type.
    Returns:
        None.
    Raises:
        AssertionError: If an unsupported type is accepted.
    """
    profile = PersistenceProfile("p")
    with pytest.raises(TypeError, match="unsupported twin"):
        profile.record(object())


def test_record_spell_crystal_routes_by_active_flag():
    """
    Purpose:
        Verify custody lands in the location the active flag selects.
    Contract:
        active=True fills the active map; active=False the inactive map;
        get_spell_crystal finds custody in either location.
    Returns:
        None.
    Raises:
        AssertionError: If custody lands in the wrong location.
    """
    profile = PersistenceProfile("p")
    profile.record_spell_crystal(_StubSpellCrystal("sha-a"), active=True)
    profile.record_spell_crystal(_StubSpellCrystal("sha-b"), active=False)
    summary = profile.describe()
    assert summary["spell_crystal_count"] == 1
    assert summary["inactive_spell_crystal_count"] == 1
    assert profile.get_spell_crystal("sha-a").id == "sha-a"
    assert profile.get_spell_crystal("sha-b").id == "sha-b"


def test_record_spell_crystal_displaces_across_both_locations():
    """
    Purpose:
        Verify replace-on-emit spans BOTH custody locations.
    Contract:
        Re-recording an id held inactive into the active location cleans
        the displaced crystal and leaves exactly one custody entry.
    Returns:
        None.
    Raises:
        AssertionError: If stale custody survives relocation.
    """
    profile = PersistenceProfile("p")
    parked = _StubSpellCrystal("sha-a")
    profile.record_spell_crystal(parked, active=False)
    profile.record_spell_crystal(_StubSpellCrystal("sha-a"), active=True)
    assert parked.cleaned is True
    summary = profile.describe()
    assert summary["spell_crystal_count"] == 1
    assert summary["inactive_spell_crystal_count"] == 0


def test_record_spell_activity_moves_custody_between_locations():
    """
    Purpose:
        Verify the park/promote mirror moves custody without cleaning it.
    Contract:
        active=False moves active->inactive; active=True moves back; the
        crystal object survives both moves.
    Returns:
        None.
    Raises:
        AssertionError: If custody is lost or cleaned during moves.
    """
    profile = PersistenceProfile("p")
    crystal = _StubSpellCrystal("sha-a")
    profile.record_spell_crystal(crystal, active=True)
    profile.record_spell_activity("sha-a", active=False)
    assert profile.describe()["inactive_spell_crystal_count"] == 1
    profile.record_spell_activity("sha-a", active=True)
    assert profile.describe()["spell_crystal_count"] == 1
    assert crystal.cleaned is False


def test_record_spell_activity_tolerates_missing_custody_but_journals():
    """
    Purpose:
        Verify pre-catch-up activity is tolerated and still journaled.
    Contract:
        No raise for unknown custody; the journal gains one
        "spell_activity" entry so checkpoints stay truthful.
    Returns:
        None.
    Raises:
        AssertionError: If the tolerant journal contract is broken.
    """
    profile = PersistenceProfile("p")
    profile.record_spell_activity("ghost", active=False)
    _payloads, entries, _rng = profile.capture_segment_since(0)
    assert entries == [(1, "spell_activity", "ghost")]


def test_remove_spell_crystal_evicts_both_locations_and_cleans():
    """
    Purpose:
        Verify true removal evicts custody entirely.
    Contract:
        The crystal is cleaned, both locations are emptied, and one
        "spell_removed" entry is journaled.
    Returns:
        None.
    Raises:
        AssertionError: If custody survives removal.
    """
    profile = PersistenceProfile("p")
    crystal = _StubSpellCrystal("sha-a")
    profile.record_spell_crystal(crystal, active=True)
    profile.remove_spell_crystal("sha-a")
    assert crystal.cleaned is True
    summary = profile.describe()
    assert summary["spell_crystal_count"] == 0
    assert summary["inactive_spell_crystal_count"] == 0
    with pytest.raises(KeyError):
        profile.get_spell_crystal("sha-a")


def test_remove_spell_crystal_tolerates_absent_custody():
    """
    Purpose:
        Verify removal of unrecorded custody is a journaled no-op.
    Contract:
        No raise; the "spell_removed" entry is journaled either way.
    Returns:
        None.
    Raises:
        AssertionError: If absence raises or skips the journal.
    """
    profile = PersistenceProfile("p")
    profile.remove_spell_crystal("ghost")
    _payloads, entries, _rng = profile.capture_segment_since(0)
    assert entries == [(1, "spell_removed", "ghost")]


def test_remove_spellbook_subtree_sweeps_by_parent_edge():
    """
    Purpose:
        Verify book death takes its whole record subtree.
    Contract:
        Book twin, conduit twin(s) with the matching spellbook_id, and
        custody in BOTH locations with the matching parent edge are all
        evicted and cleaned; one "spellbook_removed" entry journals.
    Returns:
        None.
    Raises:
        AssertionError: If any subtree member survives.
    """
    profile = PersistenceProfile("p")
    book = _book("book-1")
    conduit = _conduit("conduit-1", "book-1")
    active = _StubSpellCrystal("sha-a", "book-1")
    parked = _StubSpellCrystal("sha-b", "book-1")
    profile.record(book)
    profile.record(conduit)
    profile.record_spell_crystal(active, active=True)
    profile.record_spell_crystal(parked, active=False)
    profile.remove_spellbook_subtree("book-1")
    assert book.cleaned and conduit.cleaned and active.cleaned and parked.cleaned
    summary = profile.describe()
    assert summary["spellbook_count"] == 0
    assert summary["conduit_count"] == 0
    assert summary["spell_crystal_count"] == 0
    assert summary["inactive_spell_crystal_count"] == 0
    _payloads, entries, _rng = profile.capture_segment_since(0)
    assert entries[-1][1] == "spellbook_removed"


def test_remove_spellbook_subtree_retains_other_books_world():
    """
    Purpose:
        Verify the sweep is scoped to one parent edge.
    Contract:
        A sibling book's twin, conduit, and custody survive untouched.
    Returns:
        None.
    Raises:
        AssertionError: If the sweep over-reaches.
    """
    profile = PersistenceProfile("p")
    profile.record(_book("book-1"))
    profile.record(_book("book-2"))
    profile.record(_conduit("conduit-2", "book-2"))
    survivor = _StubSpellCrystal("sha-keep", "book-2")
    profile.record_spell_crystal(survivor, active=True)
    profile.remove_spellbook_subtree("book-1")
    summary = profile.describe()
    assert summary["spellbook_count"] == 1
    assert summary["conduit_count"] == 1
    assert summary["spell_crystal_count"] == 1
    assert survivor.cleaned is False


def test_remove_spellbook_subtree_tolerates_unrecorded_book():
    """
    Purpose:
        Verify subtree eviction of an unrecorded book is a journaled no-op.
    Contract:
        No raise; "spellbook_removed" journals for replay truth.
    Returns:
        None.
    Raises:
        AssertionError: If absence raises or skips the journal.
    """
    profile = PersistenceProfile("p")
    profile.remove_spellbook_subtree("ghost-book")
    _payloads, entries, _rng = profile.capture_segment_since(0)
    assert entries == [(1, "spellbook_removed", "ghost-book")]


def test_remove_frame_crystal_evicts_frame_and_leftover_books():
    """
    Purpose:
        Verify frame death evicts the frame twin plus the by-frame net.
    Contract:
        The frame twin and every remaining book subtree whose frame_name
        matches are evicted (per-book "spellbook_removed" entries), then
        ONE "frame_removed" entry seals the frame.
    Returns:
        None.
    Raises:
        AssertionError: If the net misses a matching book subtree.
    """
    profile = PersistenceProfile("p")
    profile.record(_frame("frame-a"))
    profile.record(_book("book-1", "frame-a"))
    profile.record(_conduit("conduit-1", "book-1"))
    orphan = _StubSpellCrystal("sha-a", "book-1")
    profile.record_spell_crystal(orphan, active=True)
    profile.record(_book("book-other", "frame-b"))
    profile.remove_frame_crystal("frame-a")
    summary = profile.describe()
    assert summary["frame_count"] == 0
    assert summary["spellbook_count"] == 1
    assert summary["conduit_count"] == 0
    assert orphan.cleaned is True
    _payloads, entries, _rng = profile.capture_segment_since(0)
    kinds = [entry[1] for entry in entries]
    assert kinds[-1] == "frame_removed"
    assert "spellbook_removed" in kinds


def test_state_switches_flip_markers_and_retain_twins():
    """
    Purpose:
        Verify the MR/Nexus state-switch model.
    Contract:
        Switch verbs flip the described marker without evicting or
        cleaning the singleton twins (disable keeps configuration).
    Returns:
        None.
    Raises:
        AssertionError: If a twin is evicted by a state flip.
    """
    profile = PersistenceProfile("p")
    nexus_twin = NexusCrystal(configured=True, enabled=True)
    mr_twin = MutationResearchCrystal(activated=True)
    profile.record(nexus_twin)
    profile.record(mr_twin)
    profile.record_nexus_state(RecordedUnitState.disabled)
    profile.record_mutation_research_state(RecordedUnitState.cleaned)
    summary = profile.describe()
    assert summary["nexus_state"] == "disabled"
    assert summary["mutation_research_state"] == "cleaned"
    assert summary["has_nexus_crystal"] is True
    assert summary["has_mutation_research_crystal"] is True
    assert nexus_twin.cleaned is False and mr_twin.cleaned is False


def test_capture_segment_since_filters_by_sequence_mark():
    """
    Purpose:
        Verify incremental capture windows.
    Contract:
        Only entries with sequence > mark appear; the returned range is
        (mark + 1, current sequence).
    Returns:
        None.
    Raises:
        AssertionError: If the window leaks earlier entries.
    """
    profile = PersistenceProfile("p")
    profile.record(AetherCrystal())
    profile.record(_frame())
    _p1, first_entries, first_range = profile.capture_segment_since(0)
    assert len(first_entries) == 2 and first_range == (1, 2)
    profile.record(_book())
    _p2, second_entries, second_range = profile.capture_segment_since(2)
    assert [entry[1] for entry in second_entries] == ["spellbook"]
    assert second_range == (3, 3)


def test_capture_segment_payload_special_cases():
    """
    Purpose:
        Verify every non-twin journal kind captures its documented payload.
    Contract:
        spell_removed/spellbook_removed/frame_removed are tombstones;
        spell_activity reports current custody truth; state switches
        report the flipped value plus twin presence.
    Returns:
        None.
    Raises:
        AssertionError: If a payload shape drifts from the contract.
    """
    profile = PersistenceProfile("p")
    profile.record_spell_crystal(_StubSpellCrystal("sha-a"), active=True)
    profile.record_spell_activity("sha-a", active=False)
    profile.remove_spell_crystal("sha-a")
    profile.remove_spellbook_subtree("book-x")
    profile.remove_frame_crystal("frame-x")
    profile.record(NexusCrystal(configured=True, enabled=True))
    profile.record_nexus_state(RecordedUnitState.disabled)
    payloads, _entries, _rng = profile.capture_segment_since(0)
    assert payloads["spell_activity"]["sha-a"] == {
        "spell_id": "sha-a", "active": False, "custody_present": False,
    }
    assert payloads["spell_removed"]["sha-a"] == {
        "spell_id": "sha-a", "removed": True,
    }
    assert payloads["spellbook_removed"]["book-x"] == {
        "spellbook_id": "book-x", "removed": True,
    }
    assert payloads["frame_removed"]["frame-x"] == {
        "frame_name": "frame-x", "removed": True,
    }
    assert payloads["nexus_state"]["disabled"] == {
        "state": "disabled", "twin_present": True,
    }


def test_capture_segment_captures_current_twin_for_replaced_identity():
    """
    Purpose:
        Verify full-object capture semantics under replacement.
    Contract:
        An identity journaled then replaced captures its CURRENT twin
        (final state within the window), not the displaced one.
    Returns:
        None.
    Raises:
        AssertionError: If a stale twin state is captured.
    """
    profile = PersistenceProfile("p")
    profile.record(NexusCrystal(configured=True, enabled=False))
    profile.record(NexusCrystal(configured=True, enabled=True))
    payloads, _entries, _rng = profile.capture_segment_since(0)
    # Singleton twins journal under the fixed key "root".
    assert payloads["nexus"]["root"]["enabled"] is True


def test_mark_checkpoint_rejects_backward_movement():
    """
    Purpose:
        Verify the checkpoint mark is monotonic.
    Contract:
        Advancing works; moving backward raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If a backward mark is accepted.
    """
    profile = PersistenceProfile("p")
    profile.mark_checkpoint(5)
    with pytest.raises(ValueError, match="cannot move backward"):
        profile.mark_checkpoint(4)


def test_cleanup_is_idempotent_and_blocks_further_use():
    """
    Purpose:
        Verify terminal cleanup semantics.
    Contract:
        Held twins/custody are cleaned; repeat cleanup is a no-op; any
        further verb raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If post-cleanup use is allowed.
    """
    profile = PersistenceProfile("p")
    twin = AetherCrystal()
    custody = _StubSpellCrystal("sha-a")
    profile.record(twin)
    profile.record_spell_crystal(custody, active=True)
    profile.cleanup()
    profile.cleanup()
    assert twin.cleaned is True and custody.cleaned is True
    with pytest.raises(RuntimeError):
        profile.record(AetherCrystal())
