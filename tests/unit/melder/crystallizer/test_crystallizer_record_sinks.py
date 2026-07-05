"""
Unit contract tests for the Crystallizer record sinks and the emit-driven
automatic-checkpoint cadence: NO-OP-when-inactive gating, facade activation
gating, retention installation, and the monotonic-clock ticker.

These construct the real Crystallizer singleton (reset around each test) with
no Aether world; the catch-up walk early-returns on aether=None by contract.
"""
import pytest

import melder.crystallizer.crystallizer as crystallizer_module
from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.nexus.nexus import Nexus
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.persistence.recorded_unit_state import RecordedUnitState


class _StubSpellCrystal:
    """Light custody stand-in (id = spell SHA; Cleanable-shaped)."""

    def __init__(self, spell_id, spellbook_id=None):
        self.id = spell_id
        self.spellbook_id = spellbook_id
        # Real custody carries root_module_kind ("synthetic_module" /
        # "site_package" / "user_source"); emit_spell_activity reads it to
        # gate the module-world reaction. "user_source" = the non-synthetic
        # skip lane, matching a file-backed test class.
        self.root_module_kind = "user_source"
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


def _activated_crystallizer(interval_minutes=60, max_crystals=100):
    """
    Build one activated crystallizer with the given checkpoint knobs.

    Returns:
        Crystallizer: The activated singleton (no Aether world attached).
    """
    configuration = (
        CrystallizerConfiguration()
        .with_defaults()
        .with_checkpoint_interval_minutes(interval_minutes)
        .with_max_persistence_crystals(max_crystals)
    )
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def test_emit_verbs_are_noops_while_not_activated():
    """
    Purpose:
        Verify the passive-sink gate on every emit verb.
    Contract:
        Emits before activation record NOTHING: after activating, the
        active profile describes an empty world and a sealed checkpoint
        captures zero journal entries.
    Returns:
        None.
    Raises:
        AssertionError: If an inactive emit reaches the record.
    """
    crystallizer = Crystallizer()
    crystallizer.emit_spell_crystal(_StubSpellCrystal("sha-a"), active=True)
    crystallizer.emit_spell_activity("sha-a", active=False)
    crystallizer.emit_spell_removed("sha-a")
    crystallizer.emit_spellbook_removed("book-1")
    crystallizer.emit_frame_removed("frame-a")
    crystallizer.emit_nexus_state(RecordedUnitState.disabled)
    crystallizer.emit_mutation_research_state(RecordedUnitState.enabled)
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer.activate(configuration)
    summary = crystallizer.describe_profile()
    assert summary["spell_crystal_count"] == 0
    assert summary["nexus_state"] is None
    checkpoint_id = crystallizer.create_checkpoint()
    assert (
        crystallizer.describe_checkpoint(checkpoint_id)["journal_entry_count"]
        == 0
    )


def test_profile_and_checkpoint_facades_require_activation():
    """
    Purpose:
        Verify the facade activation gate.
    Contract:
        describe_profile and create_checkpoint raise RuntimeError before
        the crystallizer is activated.
    Returns:
        None.
    Raises:
        AssertionError: If a facade works pre-activation.
    """
    crystallizer = Crystallizer()
    with pytest.raises(RuntimeError):
        crystallizer.describe_profile()
    with pytest.raises(RuntimeError):
        crystallizer.create_checkpoint()


def test_activated_sinks_route_to_the_active_profile():
    """
    Purpose:
        Verify the full sink surface against the real record.
    Contract:
        Custody emission, activity move, removal, and both state switches
        land in the active profile and count in a sealed checkpoint.
    Returns:
        None.
    Raises:
        AssertionError: If any sink fails to reach the record.
    """
    crystallizer = _activated_crystallizer()
    crystallizer.emit_spell_crystal(_StubSpellCrystal("sha-a"), active=True)
    crystallizer.emit_spell_activity("sha-a", active=False)
    crystallizer.emit_nexus_state(RecordedUnitState.disabled)
    summary = crystallizer.describe_profile()
    assert summary["inactive_spell_crystal_count"] == 1
    assert summary["nexus_state"] == "disabled"
    assert crystallizer.get_spell_crystal("sha-a").id == "sha-a"
    crystallizer.emit_spell_removed("sha-a")
    with pytest.raises(KeyError):
        crystallizer.get_spell_crystal("sha-a")
    checkpoint_id = crystallizer.create_checkpoint()
    assert (
        crystallizer.describe_checkpoint(checkpoint_id)["journal_entry_count"]
        == 4
    )


def test_activate_installs_retention_from_configuration():
    """
    Purpose:
        Verify the configuration-to-ledger retention hand-off.
    Contract:
        With max_persistence_crystals=2, sealing three checkpoints keeps
        only the two newest ledger ids.
    Returns:
        None.
    Raises:
        AssertionError: If the configured cap is not enforced.
    """
    crystallizer = _activated_crystallizer(max_crystals=2)
    first = crystallizer.create_checkpoint()
    second = crystallizer.create_checkpoint()
    third = crystallizer.create_checkpoint()
    assert crystallizer.list_checkpoint_ids() == [second, third]
    with pytest.raises(KeyError):
        crystallizer.describe_checkpoint(first)


def test_cadence_seals_exactly_once_per_elapsed_interval(monkeypatch):
    """
    Purpose:
        Verify the emit-driven automatic-checkpoint ticker.
    Contract:
        With a 1-minute interval: an emit before 60s seals nothing; the
        first emit at/after 60s seals exactly one automatic checkpoint;
        an immediate follow-up emit seals nothing more.
    Returns:
        None.
    Raises:
        AssertionError: If the cadence over- or under-fires.
    """
    clock = {"now": 1000.0}
    monkeypatch.setattr(
        crystallizer_module.time, "monotonic", lambda: clock["now"]
    )
    crystallizer = _activated_crystallizer(interval_minutes=1)
    clock["now"] += 59.0
    crystallizer.emit_spell_crystal(_StubSpellCrystal("sha-a"), active=True)
    assert crystallizer.list_checkpoint_ids() == []
    clock["now"] += 2.0
    crystallizer.emit_spell_crystal(_StubSpellCrystal("sha-b"), active=True)
    ledger = crystallizer.list_checkpoint_ids()
    assert len(ledger) == 1
    description = crystallizer.describe_checkpoint(ledger[0])["description"]
    assert description == "automatic cadence checkpoint"
    crystallizer.emit_spell_crystal(_StubSpellCrystal("sha-c"), active=True)
    assert len(crystallizer.list_checkpoint_ids()) == 1


def test_cadence_stamp_starts_at_activation(monkeypatch):
    """
    Purpose:
        Verify activation stamps the cadence origin.
    Contract:
        Emits immediately after activation never instant-seal, no matter
        how long the process ran before activate().
    Returns:
        None.
    Raises:
        AssertionError: If activation inherits a stale cadence origin.
    """
    clock = {"now": 50000.0}
    monkeypatch.setattr(
        crystallizer_module.time, "monotonic", lambda: clock["now"]
    )
    crystallizer = _activated_crystallizer(interval_minutes=1)
    crystallizer.emit_spell_crystal(_StubSpellCrystal("sha-a"), active=True)
    assert crystallizer.list_checkpoint_ids() == []


def test_manual_and_automatic_checkpoints_share_the_retention_window(
        monkeypatch,
):
    """
    Purpose:
        Verify manual and cadence-sealed crystals share one rolling ledger.
    Contract:
        With retention 2, a manual seal followed by an automatic seal and
        another manual seal keeps only the newest two.
    Returns:
        None.
    Raises:
        AssertionError: If the ledger tiers diverge.
    """
    clock = {"now": 1000.0}
    monkeypatch.setattr(
        crystallizer_module.time, "monotonic", lambda: clock["now"]
    )
    crystallizer = _activated_crystallizer(interval_minutes=1, max_crystals=2)
    crystallizer.create_checkpoint(description="manual-1")
    clock["now"] += 61.0
    crystallizer.emit_spell_crystal(_StubSpellCrystal("sha-a"), active=True)
    crystallizer.create_checkpoint(description="manual-2")
    ledger = crystallizer.list_checkpoint_ids()
    assert len(ledger) == 2
    descriptions = [
        crystallizer.describe_checkpoint(checkpoint_id)["description"]
        for checkpoint_id in ledger
    ]
    assert descriptions == ["automatic cadence checkpoint", "manual-2"]
