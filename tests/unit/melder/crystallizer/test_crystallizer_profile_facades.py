"""
Unit contract tests for the Crystallizer profile facades (the depths never
escape: names and dicts only) and deactivate() re-gating.
"""
import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.nexus.nexus import Nexus
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer


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


@pytest.fixture(autouse=True)
def reset_crystallizer_singleton():
    """
    Reset the world singletons and boot a hosting Aether around each test.

    Contract:
        - First-time Crystallizer initialization REQUIRES the hosting
          Aether (crystallizer.py:101); Aether() constructs the hosted
          crystallizer, so the later Crystallizer() call returns it.

    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    Aether()
    yield
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()


def _activated_crystallizer():
    """
    Build one activated crystallizer with default knobs.

    Returns:
        Crystallizer: The activated singleton.
    """
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def test_profile_facades_return_names_and_dicts_only():
    """
    Purpose:
        Verify the facade covenant (persistence model stays buried).
    Contract:
        create/list/active return plain names; describe returns a dict;
        no facade ever returns a PersistenceProfile object.
    Returns:
        None.
    Raises:
        AssertionError: If a facade leaks the depths.
    """
    crystallizer = _activated_crystallizer()
    created = crystallizer.create_profile("kit-a")
    assert created is None
    assert crystallizer.active_profile_name == "kit-a"
    names = crystallizer.list_profile_names()
    assert isinstance(names, list)
    assert set(names) == {"default", "kit-a"}
    summary = crystallizer.describe_profile()
    assert isinstance(summary, dict)
    assert summary["profile_name"] == "kit-a"


def test_clear_profile_facade_resets_content_in_place():
    """
    Purpose:
        Verify clear_profile through the facade.
    Contract:
        The cleared profile stays selectable and empty; recording works
        again afterwards.
    Returns:
        None.
    Raises:
        AssertionError: If clear routes or resets incorrectly.
    """
    crystallizer = _activated_crystallizer()
    crystallizer.emit_spell_crystal(_StubSpellCrystal("sha-a"), active=True)
    assert crystallizer.describe_profile()["spell_crystal_count"] == 1
    crystallizer.clear_profile("default")
    assert crystallizer.describe_profile()["spell_crystal_count"] == 0
    crystallizer.emit_spell_crystal(_StubSpellCrystal("sha-b"), active=True)
    assert crystallizer.describe_profile()["spell_crystal_count"] == 1


def test_delete_profile_facade_falls_selection_back_to_default():
    """
    Purpose:
        Verify delete_profile through the facade.
    Contract:
        Deleting the active named profile falls back to "default";
        deleting "default" raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If deletion routing drifts.
    """
    crystallizer = _activated_crystallizer()
    crystallizer.create_profile("kit-a")
    crystallizer.delete_profile("kit-a")
    assert crystallizer.active_profile_name == "default"
    with pytest.raises(ValueError):
        crystallizer.delete_profile("default")


def test_deactivate_regates_facades_and_silences_sinks():
    """
    Purpose:
        Verify deactivate() returns the crystallizer to passive posture.
    Contract:
        After deactivate, profile facades raise RuntimeError again and
        emit verbs are NO-OPs (proven by re-activating and describing).
    Returns:
        None.
    Raises:
        AssertionError: If deactivation leaves the sink live.
    """
    crystallizer = _activated_crystallizer()
    crystallizer.deactivate()
    with pytest.raises(RuntimeError):
        crystallizer.describe_profile()
    crystallizer.emit_spell_crystal(_StubSpellCrystal("sha-a"), active=True)
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer.activate(configuration)
    assert crystallizer.describe_profile()["spell_crystal_count"] == 0


def test_bug158_profile_scoped_checkpoint_records_policy_twin_into_that_profile():
    """
    BUG-158 regression: create_checkpoint(profile_name=X) must emit the
    self-describing policy twin into X's window, not into the active profile.
    With default active and an inactive 'named' profile, checkpointing 'named'
    must leave 'named' self-describing (a real, non-empty window) and must not
    advance the unrelated active default's emission sequence.
    """
    crystallizer = _activated_crystallizer()
    # "default" is the active emission target after activation.
    crystallizer.create_profile("named", activate=False)
    assert crystallizer.active_profile_name == "default"
    default_before = crystallizer.describe_profile("default")

    checkpoint_id = crystallizer.create_checkpoint(profile_name="named")

    # The policy twin landed in the TARGETED profile's window (self-describing,
    # non-empty), not in the active default.
    record = crystallizer.describe_checkpoint(checkpoint_id)
    assert record["profile_name"] == "named"
    assert record["journal_entry_count"] >= 1
    first, last = record["sequence_range"]
    assert first <= last  # a real window, not the empty/inverted marker the bug produced

    # The unrelated active profile is untouched (no stray policy traffic; its
    # emission sequence did not advance).
    assert crystallizer.describe_profile("default") == default_before
