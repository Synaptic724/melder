"""
Unit contract tests for the persistence twin family's describe surfaces and
lifecycle, plus PersistenceProfile maintenance verbs (clear).

Twins are pure-data carriers by design: constructible without any live
runtime, immutable after birth, cleanable exactly once.
"""
import pytest

from melder.crystallizer.persistence.crystals.aether_crystal import AetherCrystal
from melder.crystallizer.persistence.crystals.aetheric_frame_crystal import (
    AethericFrameCrystal,
)
from melder.crystallizer.persistence.crystals.conduit_crystal import ConduitCrystal
from melder.crystallizer.persistence.crystals.mutation_research_crystal import (
    MutationResearchCrystal,
)
from melder.crystallizer.persistence.crystals.nexus_crystal import NexusCrystal
from melder.crystallizer.persistence.crystals.spellbook_crystal import (
    SpellbookCrystal,
)
from melder.crystallizer.persistence.persistence_profile import PersistenceProfile
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


def test_aether_twin_describe_carries_kind_and_detached_payload():
    """
    Purpose:
        Verify the root twin's describe contract and payload detachment.
    Contract:
        describe() reports twin_kind "aether" and a COPY of the payload
        (mutating the result must not touch the twin).
    Returns:
        None.
    Raises:
        AssertionError: If the payload is shared instead of detached.
    """
    twin = AetherCrystal(configuration_payload={"resolver": "present"})
    described = twin.describe()
    assert described["twin_kind"] == "aether"
    described["configuration_payload"]["resolver"] = "mutated"
    assert twin.describe()["configuration_payload"]["resolver"] == "present"


def test_frame_twin_describe_carries_posture_fields():
    """
    Purpose:
        Verify the frame twin's posture snapshot.
    Contract:
        describe() reports frame_name, system_state_name, rift/ai flags,
        and a detached dev_ops_payload.
    Returns:
        None.
    Raises:
        AssertionError: If a posture field drifts.
    """
    twin = AethericFrameCrystal(
        frame_name="frame-a",
        system_state_name="dynamic",
        rift_enabled=True,
        ai_native_enabled=False,
        dev_ops_payload={"incidents": 0},
    )
    described = twin.describe()
    assert described["twin_kind"] == "frame"
    assert described["frame_name"] == "frame-a"
    assert described["system_state_name"] == "dynamic"
    assert described["rift_enabled"] is True
    assert described["ai_native_enabled"] is False
    assert described["dev_ops_payload"] == {"incidents": 0}


def test_spellbook_twin_describe_carries_identity_and_bind_order():
    """
    Purpose:
        Verify the book twin's identity edges and ordered captures.
    Contract:
        describe() reports spellbook_id, frame_name (L1 edge), hook_names,
        and bind_order as detached lists.
    Returns:
        None.
    Raises:
        AssertionError: If identity or ordering drifts.
    """
    twin = SpellbookCrystal(
        spellbook_id="book-1",
        frame_name="frame-a",
        hook_names=["conduit:on_x"],
        bind_order=["sha-1", "sha-2"],
    )
    described = twin.describe()
    assert described["twin_kind"] == "spellbook"
    assert described["spellbook_id"] == "book-1"
    assert described["frame_name"] == "frame-a"
    assert described["bind_order"] == ["sha-1", "sha-2"]
    described["bind_order"].append("sha-x")
    assert twin.describe()["bind_order"] == ["sha-1", "sha-2"]


def test_conduit_twin_describe_carries_parent_edge_and_config():
    """
    Purpose:
        Verify the conduit twin's parent edge and conjure-time truth.
    Contract:
        describe() reports conduit_id, spellbook_id (the sweep edge),
        policy/dynamic posture, and detached payload containers.
    Returns:
        None.
    Raises:
        AssertionError: If the parent edge or posture drifts.
    """
    twin = ConduitCrystal(
        conduit_id="conduit-1",
        spellbook_id="book-1",
        conduit_name="root",
        policy_name="policy",
        dynamic=True,
        link_targets=["conduit-2", "conduit-3"],
        configuration_payload={"conduit_state": "normal"},
    )
    described = twin.describe()
    assert described["twin_kind"] == "conduit"
    assert described["conduit_id"] == "conduit-1"
    assert described["spellbook_id"] == "book-1"
    assert described["dynamic"] is True
    assert described["configuration_payload"] == {"conduit_state": "normal"}
    # Outbound link topology is part of the snapshot and detached.
    assert described["link_targets"] == ["conduit-2", "conduit-3"]
    described["link_targets"].append("conduit-x")
    assert twin.describe()["link_targets"] == ["conduit-2", "conduit-3"]


def test_singleton_twins_describe_activation_truth():
    """
    Purpose:
        Verify the Nexus/MR twins' activation snapshots.
    Contract:
        NexusCrystal reports configured/enabled; MutationResearchCrystal
        reports activated; both carry detached payloads.
    Returns:
        None.
    Raises:
        AssertionError: If activation truth drifts.
    """
    nexus_twin = NexusCrystal(configured=True, enabled=False)
    mr_twin = MutationResearchCrystal(activated=True)
    assert nexus_twin.describe()["configured"] is True
    assert nexus_twin.describe()["enabled"] is False
    assert mr_twin.describe()["twin_kind"] == "mutation_research"
    assert mr_twin.describe()["activated"] is True


def test_twins_cleanup_idempotently_and_block_describe():
    """
    Purpose:
        Verify Cleanable discipline across the whole twin family.
    Contract:
        cleanup() is idempotent; describe() afterwards raises
        RuntimeError for every twin kind.
    Returns:
        None.
    Raises:
        AssertionError: If any twin survives cleanup usable.
    """
    twins = [
        AetherCrystal(),
        AethericFrameCrystal(
            frame_name="f", system_state_name="dynamic",
            rift_enabled=False, ai_native_enabled=False,
        ),
        SpellbookCrystal(spellbook_id="b", frame_name="f"),
        ConduitCrystal(
            conduit_id="c", spellbook_id="b", conduit_name=None,
            policy_name="p", dynamic=False,
        ),
        NexusCrystal(configured=False, enabled=False),
        MutationResearchCrystal(activated=False),
    ]
    for twin in twins:
        twin.cleanup()
        twin.cleanup()
        assert twin.cleaned is True
        with pytest.raises(RuntimeError):
            twin.describe()


def test_profile_clear_resets_content_but_stays_usable():
    """
    Purpose:
        Verify clear() as the generalized clear_bootstrap.
    Contract:
        Held twins/custody are cleaned and dropped, state markers reset,
        and the profile keeps recording afterwards (unlike cleanup).
    Returns:
        None.
    Raises:
        AssertionError: If clear() kills the profile or leaks content.
    """
    profile = PersistenceProfile("p")
    twin = AetherCrystal()
    custody = _StubSpellCrystal("sha-a")
    profile.record(twin)
    profile.record_spell_crystal(custody, active=True)
    profile.record_nexus_state(RecordedUnitState.disabled)
    profile.clear()
    assert twin.cleaned is True and custody.cleaned is True
    summary = profile.describe()
    assert summary["has_aether_crystal"] is False
    assert summary["spell_crystal_count"] == 0
    assert summary["nexus_state"] is None
    profile.record(AetherCrystal())
    assert profile.describe()["has_aether_crystal"] is True


def test_profile_clear_resets_capture_baseline():
    """
    Purpose:
        Verify clear() resets the incremental journal baseline.
    Contract:
        After clear(), capture_segment_since(0) reflects only NEW
        emissions (the next checkpoint captures from zero).
    Returns:
        None.
    Raises:
        AssertionError: If stale journal entries survive clear().
    """
    profile = PersistenceProfile("p")
    profile.record(AetherCrystal())
    profile.record(AetherCrystal())
    profile.clear()
    profile.record(AetherCrystal())
    _payloads, entries, _rng = profile.capture_segment_since(0)
    assert [entry[1] for entry in entries] == ["aether"]
