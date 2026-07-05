"""
Component tests for PersistenceSystem flows with real twins: multi-profile
checkpoint isolation, ledger survival across profile deletion, clear-then-
capture-from-zero, and eviction/state events inside sealed windows.
"""
from melder.crystallizer.persistence.crystals.aether_crystal import AetherCrystal
from melder.crystallizer.persistence.crystals.conduit_crystal import ConduitCrystal
from melder.crystallizer.persistence.crystals.nexus_crystal import NexusCrystal
from melder.crystallizer.persistence.crystals.spellbook_crystal import (
    SpellbookCrystal,
)
from melder.crystallizer.persistence.persistence_system import PersistenceSystem
from melder.crystallizer.persistence.recorded_unit_state import RecordedUnitState


class _StubSpellCrystal:
    """Light custody stand-in (id = spell SHA; Cleanable-shaped)."""

    def __init__(self, spell_id, spellbook_id=None):
        self.id = spell_id
        self.spellbook_id = spellbook_id
        self.cleaned = False

    def cleanup(self):
        self.cleaned = True

    def describe(self):
        return {"spell_id": self.id, "spellbook_id": self.spellbook_id}


def test_checkpoints_capture_only_the_named_profiles_window():
    """
    Purpose:
        Verify per-profile checkpoint isolation on one shared ledger.
    Contract:
        Emissions into kit-a never appear in a default-profile
        checkpoint; each profile's checkpoint_number advances
        independently.
    Returns:
        None.
    Raises:
        AssertionError: If windows bleed across profiles.
    """
    system = PersistenceSystem()
    system.create_profile("kit-a")
    system.record(AetherCrystal())
    kit_checkpoint = system.create_checkpoint()
    system.set_active_profile("default")
    system.record(NexusCrystal(configured=True, enabled=True))
    default_checkpoint = system.create_checkpoint()
    kit_summary = system.describe_checkpoint(kit_checkpoint)
    default_summary = system.describe_checkpoint(default_checkpoint)
    assert kit_summary["profile_name"] == "kit-a"
    assert kit_summary["captured_counts"] == {"aether": 1}
    assert default_summary["profile_name"] == "default"
    assert default_summary["captured_counts"] == {"nexus": 1}
    assert kit_summary["checkpoint_number"] == 1
    assert default_summary["checkpoint_number"] == 1


def test_ledger_crystals_survive_their_source_profiles_deletion():
    """
    Purpose:
        Verify history outlives its source (delete_profile contract).
    Contract:
        A checkpoint sealed from a named profile stays describable after
        that profile is deleted.
    Returns:
        None.
    Raises:
        AssertionError: If deletion reaps sealed history.
    """
    system = PersistenceSystem()
    system.create_profile("kit-a")
    system.record(AetherCrystal())
    checkpoint_id = system.create_checkpoint()
    system.delete_profile("kit-a")
    summary = system.describe_checkpoint(checkpoint_id)
    assert summary["profile_name"] == "kit-a"
    assert summary["captured_counts"] == {"aether": 1}


def test_clear_profile_makes_the_next_checkpoint_capture_from_zero():
    """
    Purpose:
        Verify the clear_profile + checkpoint interplay.
    Contract:
        After clear_profile, the next checkpoint's window restarts (no
        stale entries) and captures only post-clear emissions.
    Returns:
        None.
    Raises:
        AssertionError: If cleared history leaks into a new window.
    """
    system = PersistenceSystem()
    system.record(AetherCrystal())
    system.create_checkpoint()
    system.clear_profile("default")
    system.record(NexusCrystal(configured=True, enabled=False))
    checkpoint_id = system.create_checkpoint()
    summary = system.describe_checkpoint(checkpoint_id)
    assert summary["captured_counts"] == {"nexus": 1}
    assert summary["sequence_range"] == [1, 1]


def test_subtree_eviction_and_state_flip_ride_one_sealed_window():
    """
    Purpose:
        Verify mixed-event windows seal truthfully.
    Contract:
        A window containing custody birth, a subtree eviction, and a
        state flip captures all three payload kinds with the tombstone
        and switch shapes.
    Returns:
        None.
    Raises:
        AssertionError: If a mixed window loses an event kind.
    """
    system = PersistenceSystem()
    system.record(SpellbookCrystal(spellbook_id="book-1", frame_name="f"))
    system.record(
        ConduitCrystal(
            conduit_id="conduit-1", spellbook_id="book-1",
            conduit_name="root", policy_name="p", dynamic=True,
        )
    )
    system.record_spell_crystal(_StubSpellCrystal("sha-a", "book-1"), active=True)
    system.remove_spellbook_subtree("book-1")
    system.record_nexus_state(RecordedUnitState.disabled)
    checkpoint_id = system.create_checkpoint()
    summary = system.describe_checkpoint(checkpoint_id)
    assert summary["captured_counts"]["spellbook_removed"] == 1
    assert summary["captured_counts"]["nexus_state"] == 1
    assert summary["journal_entry_count"] == 5


def test_retention_applies_across_profiles_on_the_shared_ledger():
    """
    Purpose:
        Verify the cap governs the LEDGER, not per-profile counts.
    Contract:
        With retention 2, checkpoints from two different profiles still
        evict the globally oldest crystal first.
    Returns:
        None.
    Raises:
        AssertionError: If retention becomes per-profile.
    """
    system = PersistenceSystem()
    system.set_checkpoint_retention(2)
    first = system.create_checkpoint()
    system.create_profile("kit-a")
    second = system.create_checkpoint()
    third = system.create_checkpoint()
    assert system.list_checkpoint_ids() == [second, third]
    assert first not in system.list_checkpoint_ids()
