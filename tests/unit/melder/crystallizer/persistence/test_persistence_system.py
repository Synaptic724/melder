"""
Unit contract tests for PersistenceSystem: profile registry semantics,
checkpoint sealing (incremental windows, per-profile numbering, FIFO
retention dropout), and active-profile routing of the record verbs.
"""
import pytest

from melder.crystallizer.persistence.crystals.aether_crystal import AetherCrystal
from melder.crystallizer.persistence.crystals.spellbook_crystal import (
    SpellbookCrystal,
)
from melder.crystallizer.persistence.persistence_system import PersistenceSystem
from melder.crystallizer.persistence.recorded_unit_state import RecordedUnitState


class _StubSpellCrystal:
    """
    Light custody stand-in (see the profile suite for the read contract).
    """

    def __init__(self, spell_id, spellbook_id=None):
        self.id = spell_id
        self.spellbook_id = spellbook_id
        self.cleaned = False

    def cleanup(self):
        self.cleaned = True

    def describe(self):
        return {"spell_id": self.id, "spellbook_id": self.spellbook_id}


def test_default_profile_is_guaranteed_and_initially_active():
    """
    Purpose:
        Verify the guaranteed default slot.
    Contract:
        "default" exists immediately, is the active profile, and record()
        works with zero setup.
    Returns:
        None.
    Raises:
        AssertionError: If the default slot is missing or inactive.
    """
    system = PersistenceSystem()
    assert system.active_profile_name == PersistenceSystem.DEFAULT_PROFILE_NAME
    assert "default" in system.list_profile_names()
    system.record(AetherCrystal())
    assert system.active_profile.describe()["has_aether_crystal"] is True


def test_create_profile_activates_by_default_and_optionally_not():
    """
    Purpose:
        Verify create_profile activation semantics.
    Contract:
        Default activates the new profile; activate=False keeps the
        current selection.
    Returns:
        None.
    Raises:
        AssertionError: If activation semantics drift.
    """
    system = PersistenceSystem()
    system.create_profile("kit-a")
    assert system.active_profile_name == "kit-a"
    system.create_profile("kit-b", activate=False)
    assert system.active_profile_name == "kit-a"
    assert sorted(system.list_profile_names()) == ["default", "kit-a", "kit-b"]


def test_create_profile_rejects_empty_and_duplicate_names():
    """
    Purpose:
        Verify profile-name uniqueness guards.
    Contract:
        Empty name raises ValueError; duplicate name raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If invalid names are accepted.
    """
    system = PersistenceSystem()
    with pytest.raises(ValueError, match="non-empty"):
        system.create_profile("")
    system.create_profile("kit-a")
    with pytest.raises(ValueError, match="already exists"):
        system.create_profile("kit-a")


def test_record_routes_to_the_active_profile_only():
    """
    Purpose:
        Verify active-profile emission routing.
    Contract:
        Emissions land in the active profile; switching selection reroutes
        subsequent emissions without touching prior content.
    Returns:
        None.
    Raises:
        AssertionError: If routing leaks across profiles.
    """
    system = PersistenceSystem()
    system.create_profile("kit-a")
    system.record_spell_crystal(_StubSpellCrystal("sha-a"), active=True)
    system.set_active_profile("default")
    system.record_spell_crystal(_StubSpellCrystal("sha-b"), active=True)
    assert system.active_profile.describe()["spell_crystal_count"] == 1
    system.set_active_profile("kit-a")
    assert system.active_profile.get_spell_crystal("sha-a").id == "sha-a"
    with pytest.raises(KeyError):
        system.active_profile.get_spell_crystal("sha-b")


def test_delete_profile_guards_default_and_falls_back_selection():
    """
    Purpose:
        Verify deletion semantics for named profiles.
    Contract:
        Deleting "default" raises ValueError; deleting a missing name
        raises KeyError; deleting the ACTIVE named profile cleans it and
        falls the selection back to "default".
    Returns:
        None.
    Raises:
        AssertionError: If deletion semantics drift.
    """
    system = PersistenceSystem()
    with pytest.raises(ValueError, match="cannot be"):
        system.delete_profile("default")
    with pytest.raises(KeyError):
        system.delete_profile("ghost")
    profile = system.create_profile("kit-a")
    system.delete_profile("kit-a")
    assert system.active_profile_name == "default"
    assert profile.cleaned is True


def test_create_checkpoint_seals_and_describes_metadata():
    """
    Purpose:
        Verify the checkpoint seal path end to end.
    Contract:
        create_checkpoint returns a string id present in the ledger;
        describe_checkpoint carries the documented metadata keys.
    Returns:
        None.
    Raises:
        AssertionError: If sealing or metadata drifts.
    """
    system = PersistenceSystem()
    system.record(AetherCrystal())
    checkpoint_id = system.create_checkpoint(description="first")
    assert isinstance(checkpoint_id, str) and checkpoint_id
    assert checkpoint_id in system.list_checkpoint_ids()
    summary = system.describe_checkpoint(checkpoint_id)
    assert summary["profile_name"] == "default"
    assert summary["checkpoint_number"] == 1
    assert summary["description"] == "first"
    assert summary["journal_entry_count"] == 1
    assert summary["sequence_range"] == [1, 1]


def test_create_checkpoint_windows_are_incremental_per_profile():
    """
    Purpose:
        Verify incremental sealing and per-profile numbering.
    Contract:
        The second checkpoint captures only entries after the first; an
        empty window still seals honestly; checkpoint_number increments
        per profile.
    Returns:
        None.
    Raises:
        AssertionError: If windows overlap or numbering drifts.
    """
    system = PersistenceSystem()
    system.record(AetherCrystal())
    first = system.create_checkpoint()
    system.record(SpellbookCrystal(spellbook_id="book-1", frame_name="f"))
    second = system.create_checkpoint()
    empty = system.create_checkpoint()
    assert system.describe_checkpoint(first)["journal_entry_count"] == 1
    assert system.describe_checkpoint(second)["journal_entry_count"] == 1
    assert system.describe_checkpoint(second)["checkpoint_number"] == 2
    assert system.describe_checkpoint(empty)["journal_entry_count"] == 0
    assert system.describe_checkpoint(empty)["checkpoint_number"] == 3


def test_checkpoint_ids_sort_chronologically():
    """
    Purpose:
        Verify the ULID time-ordering contract on ledger ids.
    Contract:
        list_checkpoint_ids returns creation order (lexicographic = age).
    Returns:
        None.
    Raises:
        AssertionError: If id ordering is not chronological.
    """
    system = PersistenceSystem()
    minted = [system.create_checkpoint() for _ in range(3)]
    assert system.list_checkpoint_ids() == sorted(minted)
    assert system.list_checkpoint_ids() == minted


def test_retention_cap_drops_oldest_checkpoints_first():
    """
    Purpose:
        Verify FIFO dropout at the retention cap.
    Contract:
        With retention 2, sealing 3 checkpoints evicts the OLDEST id
        (describe raises KeyError) and keeps the 2 newest.
    Returns:
        None.
    Raises:
        AssertionError: If dropout order or size drifts.
    """
    system = PersistenceSystem()
    system.set_checkpoint_retention(2)
    first = system.create_checkpoint()
    second = system.create_checkpoint()
    third = system.create_checkpoint()
    assert system.list_checkpoint_ids() == [second, third]
    with pytest.raises(KeyError):
        system.describe_checkpoint(first)


def test_set_checkpoint_retention_rejects_non_positive_and_bool():
    """
    Purpose:
        Verify retention knob validation.
    Contract:
        bool, zero, and negative values raise ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If invalid retention values are accepted.
    """
    system = PersistenceSystem()
    for bad in (True, 0, -1):
        with pytest.raises(ValueError, match="positive int"):
            system.set_checkpoint_retention(bad)


def test_load_checkpoint_validates_id_before_depth_limit():
    """
    Purpose:
        Verify the boot-verb stub's error ordering.
    Contract:
        Unknown ids raise KeyError FIRST; a known id reaches the
        NotImplementedError placeholder (restore engine pending).
    Returns:
        None.
    Raises:
        AssertionError: If error ordering drifts.
    """
    system = PersistenceSystem()
    checkpoint_id = system.create_checkpoint()
    with pytest.raises(KeyError):
        system.load_checkpoint("ghost")
    with pytest.raises(NotImplementedError):
        system.load_checkpoint(checkpoint_id)


def test_removal_and_state_verbs_route_to_active_profile():
    """
    Purpose:
        Verify the record verbs added for the removal ladder route to the
        ACTIVE profile.
    Contract:
        remove_spell_crystal / remove_spellbook_subtree /
        remove_frame_crystal / record_nexus_state /
        record_mutation_research_state all act on the active profile.
    Returns:
        None.
    Raises:
        AssertionError: If any verb routes elsewhere.
    """
    system = PersistenceSystem()
    custody = _StubSpellCrystal("sha-a", "book-1")
    system.record_spell_crystal(custody, active=True)
    system.remove_spell_crystal("sha-a")
    assert custody.cleaned is True
    book = SpellbookCrystal(spellbook_id="book-1", frame_name="frame-a")
    system.record(book)
    system.remove_spellbook_subtree("book-1")
    assert book.cleaned is True
    system.remove_frame_crystal("frame-a")
    system.record_nexus_state(RecordedUnitState.disabled)
    system.record_mutation_research_state(RecordedUnitState.enabled)
    summary = system.active_profile.describe()
    assert summary["nexus_state"] == "disabled"
    assert summary["mutation_research_state"] == "enabled"


def test_cleanup_is_idempotent_and_blocks_further_use():
    """
    Purpose:
        Verify terminal subsystem cleanup.
    Contract:
        Cleanup is idempotent; any verb afterwards raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If post-cleanup use is allowed.
    """
    system = PersistenceSystem()
    system.create_checkpoint()
    system.cleanup()
    system.cleanup()
    with pytest.raises(RuntimeError):
        system.create_checkpoint()
