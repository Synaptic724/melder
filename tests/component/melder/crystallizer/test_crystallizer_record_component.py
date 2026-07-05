"""
Component tests for the full record loop through the Crystallizer facades:
real twin objects, real persistence wiring (system + profile + ledger), no
mocks. The live Aether world is integration scope; here the emissions are
driven directly so the record semantics compose end to end.
"""
import pytest

from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.persistence.crystals.aether_crystal import AetherCrystal
from melder.crystallizer.persistence.crystals.aetheric_frame_crystal import (
    AethericFrameCrystal,
)
from melder.crystallizer.persistence.crystals.conduit_crystal import ConduitCrystal
from melder.crystallizer.persistence.crystals.nexus_crystal import NexusCrystal
from melder.crystallizer.persistence.crystals.spellbook_crystal import (
    SpellbookCrystal,
)
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


@pytest.fixture(autouse=True)
def reset_crystallizer_singleton():
    """
    Reset the Crystallizer singleton around each test.

    Returns:
        None.
    """
    Crystallizer._reset_singleton_for_tests()
    yield
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


def _emit_world(crystallizer, frame="frame-a", book="book-1", conduit="conduit-1"):
    """
    Emit one small recorded world: frame + book + conduit + two spells.

    Returns:
        tuple: (active custody stub, parked custody stub).
    """
    crystallizer.emit(AetherCrystal())
    crystallizer.emit(
        AethericFrameCrystal(
            frame_name=frame,
            system_state_name="dynamic",
            rift_enabled=True,
            ai_native_enabled=True,
        )
    )
    crystallizer.emit(SpellbookCrystal(spellbook_id=book, frame_name=frame))
    crystallizer.emit(
        ConduitCrystal(
            conduit_id=conduit,
            spellbook_id=book,
            conduit_name="root",
            policy_name="policy",
            dynamic=True,
        )
    )
    active = _StubSpellCrystal("sha-active", book)
    parked = _StubSpellCrystal("sha-parked", book)
    crystallizer.emit_spell_crystal(active, active=True)
    crystallizer.emit_spell_crystal(parked, active=False)
    return active, parked


def test_recorded_world_composes_and_checkpoints_capture_it():
    """
    Purpose:
        Verify the loop config-twins -> custody -> checkpoint end to end.
    Contract:
        The described profile mirrors the emitted world; the sealed
        checkpoint captures one payload per journaled identity with the
        documented kinds.
    Returns:
        None.
    Raises:
        AssertionError: If the composed record or capture drifts.
    """
    crystallizer = _activated_crystallizer()
    _emit_world(crystallizer)
    summary = crystallizer.describe_profile()
    assert summary["has_aether_crystal"] is True
    assert summary["frame_count"] == 1
    assert summary["spellbook_count"] == 1
    assert summary["conduit_count"] == 1
    assert summary["spell_crystal_count"] == 1
    assert summary["inactive_spell_crystal_count"] == 1
    checkpoint_id = crystallizer.create_checkpoint(description="world")
    described = crystallizer.describe_checkpoint(checkpoint_id)
    assert described["journal_entry_count"] == 6
    assert described["captured_counts"]["spell_crystal"] == 2


def test_subtree_eviction_through_the_facade_updates_checkpoint_truth():
    """
    Purpose:
        Verify book death recorded through the crystallizer facade.
    Contract:
        emit_spellbook_removed sweeps the book twin, its conduit twin,
        and BOTH custody entries; the incremental checkpoint captures the
        subtree tombstone.
    Returns:
        None.
    Raises:
        AssertionError: If eviction or capture drifts.
    """
    crystallizer = _activated_crystallizer()
    active, parked = _emit_world(crystallizer)
    crystallizer.create_checkpoint()
    crystallizer.emit_spellbook_removed("book-1")
    assert active.cleaned is True and parked.cleaned is True
    summary = crystallizer.describe_profile()
    assert summary["spellbook_count"] == 0
    assert summary["conduit_count"] == 0
    assert summary["spell_crystal_count"] == 0
    assert summary["inactive_spell_crystal_count"] == 0
    assert summary["frame_count"] == 1
    checkpoint_id = crystallizer.create_checkpoint()
    assert (
        crystallizer.describe_checkpoint(checkpoint_id)["journal_entry_count"]
        == 1
    )


def test_frame_eviction_completes_the_removal_cascade():
    """
    Purpose:
        Verify frame death recorded after its subtree already left.
    Contract:
        emit_frame_removed after a book sweep leaves an empty structural
        record while the aether twin (root config) is retained.
    Returns:
        None.
    Raises:
        AssertionError: If the frame or its net leaves residue.
    """
    crystallizer = _activated_crystallizer()
    _emit_world(crystallizer)
    crystallizer.emit_spellbook_removed("book-1")
    crystallizer.emit_frame_removed("frame-a")
    summary = crystallizer.describe_profile()
    assert summary["frame_count"] == 0
    assert summary["spellbook_count"] == 0
    assert summary["has_aether_crystal"] is True


def test_named_profiles_isolate_recorded_worlds():
    """
    Purpose:
        Verify the profiles-as-kits model through the facades.
    Contract:
        A world emitted into a named profile does not appear in default;
        switching the active profile switches what emissions see.
    Returns:
        None.
    Raises:
        AssertionError: If worlds bleed across profiles.
    """
    crystallizer = _activated_crystallizer()
    crystallizer.create_profile("kit-a")
    _emit_world(crystallizer)
    assert crystallizer.describe_profile()["spellbook_count"] == 1
    crystallizer.set_active_profile("default")
    summary = crystallizer.describe_profile()
    assert summary["spellbook_count"] == 0
    assert summary["spell_crystal_count"] == 0
    assert crystallizer.describe_profile("kit-a")["spellbook_count"] == 1


def test_state_switches_ride_checkpoints_with_twins_retained():
    """
    Purpose:
        Verify the MR/Nexus switch model through facades + capture.
    Contract:
        A nexus disable flip journals into the next checkpoint while the
        nexus twin stays described as present.
    Returns:
        None.
    Raises:
        AssertionError: If the switch evicts or skips capture.
    """
    crystallizer = _activated_crystallizer()
    crystallizer.emit(NexusCrystal(configured=True, enabled=True))
    crystallizer.create_checkpoint()
    crystallizer.emit_nexus_state(RecordedUnitState.disabled)
    summary = crystallizer.describe_profile()
    assert summary["has_nexus_crystal"] is True
    assert summary["nexus_state"] == "disabled"
    checkpoint_id = crystallizer.create_checkpoint()
    assert (
        crystallizer.describe_checkpoint(checkpoint_id)["journal_entry_count"]
        == 1
    )


def test_replayed_activity_keeps_single_custody_after_moves():
    """
    Purpose:
        Verify a park/promote cycle through the facade keeps one custody.
    Contract:
        active -> parked -> active leaves exactly one custody entry in
        the active location and the crystal object uncleaned.
    Returns:
        None.
    Raises:
        AssertionError: If moves duplicate or clean custody.
    """
    crystallizer = _activated_crystallizer()
    custody = _StubSpellCrystal("sha-a", "book-1")
    crystallizer.emit_spell_crystal(custody, active=True)
    crystallizer.emit_spell_activity("sha-a", active=False)
    crystallizer.emit_spell_activity("sha-a", active=True)
    summary = crystallizer.describe_profile()
    assert summary["spell_crystal_count"] == 1
    assert summary["inactive_spell_crystal_count"] == 0
    assert custody.cleaned is False
