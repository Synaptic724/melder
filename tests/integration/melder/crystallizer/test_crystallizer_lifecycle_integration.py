"""
Integration tests for record lifecycle seams on the REAL runtime: staged
custody (bind_inactive), notch park/promote activity mirroring, the Nexus/MR
state-switch seams, frame-death eviction, and SpellCrystal bind-fact capture.

Runs only on 3.14t (melder package root import chain).
"""
import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.crystals.recorded_unit_state import RecordedUnitState
from melder.mutation_research.mutation_configuration import (
    MutationResearchConfiguration,
)
from melder.mutation_research.mutation_research import MutationResearch
from melder.nexus.configuration.nexus_configuration import NexusConfiguration
from melder.nexus.nexus import Nexus
from tests.mocks.spellbook.core_classes import BasicService
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _PromotedService:
    """File-backed staged-spell target for notch promotion tests."""

    def __init__(self):
        self.tag = "promoted"


@pytest.fixture(autouse=True)
def reset_world_singletons():
    """
    Purpose:
        Isolate each test behind fresh world singletons.
    Contract:
        - Resets Aether/AetherUtilitySystem/Nexus/Crystallizer/
          MutationResearch and rebinds the static Aether references
          before and after each test.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    MutationResearch._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    MutationResearch._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _activate_crystallizer():
    """
    Activate the Aether-hosted crystallizer with default knobs.

    Returns:
        Crystallizer: The live, activated singleton.
    """
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def _recorded_world():
    """
    Build one recorded dynamic world: activated crystallizer + frozen-config
    book + one active bind + a conjured root conduit.

    Returns:
        tuple: (crystallizer, book, conduit, active_spell_id).
    """
    crystallizer = _activate_crystallizer()
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    book = Spellbook(configuration=configuration)
    spell_id = book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="lifecycle-root")
    return crystallizer, book, conduit, spell_id


def test_spell_crystal_captures_bind_facts():
    """
    Purpose:
        Verify the L3 crystal absorbs the bind signature (owner model:
        "normal spell_crystals capture the binding signatures").
    Contract:
        The bind-minted crystal exposes the spell/binding names, existence
        and permissions names, the spellbook parent edge, and derives
        rebindability "hydratable" for a class target.
    Returns:
        None.
    Raises:
        AssertionError: If a captured bind fact drifts.
    """
    crystallizer, book, _conduit, spell_id = _recorded_world()
    crystal = crystallizer.get_spell_crystal(spell_id)
    assert crystal.spellbook_id == book._id
    assert crystal.spell_name == "BasicService"
    # Frameless bind: no spellframe was declared, so the captured name is
    # honestly None (a spellframe=... bind would capture its __name__).
    assert crystal.spellframe_name is None
    assert crystal.existence_name == "unique"
    assert crystal.permissions_name == "create"
    assert crystal.rebindability == "hydratable"


def test_bind_inactive_stages_custody_in_the_inactive_location():
    """
    Purpose:
        Verify staged binds mirror into the parked custody location.
    Contract:
        conduit.bind_inactive emits custody active=False: the record's
        inactive count grows and the staged crystal is reachable.
    Returns:
        None.
    Raises:
        AssertionError: If staging leaks into the active location.
    """
    crystallizer, book, conduit, spell_id = _recorded_world()
    active_spell = book._spells_by_id[spell_id]
    staged_id = conduit.bind_inactive(
        spell=_PromotedService,
        spell_index=active_spell.spell_index,
        existence=Existence.unique,
        permissions="create",
    )
    summary = crystallizer.describe_profile()
    assert summary["spell_crystal_count"] == 1
    assert summary["inactive_spell_crystal_count"] == 1
    assert crystallizer.get_spell_crystal(staged_id).id == staged_id


def test_notch_promotion_moves_custody_both_directions():
    """
    Purpose:
        Verify the park/promote activity mirror through a REAL notch.
    Contract:
        notch_spell parks the old active (custody -> inactive location)
        and promotes the staged member (custody -> active location);
        both crystals survive the move uncleaned.
    Returns:
        None.
    Raises:
        AssertionError: If custody fails to follow the notch.
    """
    crystallizer, book, conduit, spell_id = _recorded_world()
    active_spell = book._spells_by_id[spell_id]
    staged_id = conduit.bind_inactive(
        spell=_PromotedService,
        spell_index=active_spell.spell_index,
        existence=Existence.unique,
        permissions="create",
    )
    staged_spell = book._inactive_spells[staged_id]
    conduit.notch_spell(
        spell_index=active_spell.spell_index,
        spell=staged_spell,
    )
    summary = crystallizer.describe_profile()
    assert summary["spell_crystal_count"] == 1
    assert summary["inactive_spell_crystal_count"] == 1
    assert crystallizer.get_spell_crystal(staged_id).id == staged_id
    assert crystallizer.get_spell_crystal(spell_id).id == spell_id
    checkpoint_id = crystallizer.create_checkpoint()
    described = crystallizer.describe_checkpoint(checkpoint_id)
    assert described["captured_counts"].get("spell_activity", 0) >= 2


def test_nexus_enable_disable_flip_the_recorded_state():
    """
    Purpose:
        Verify the Nexus state-switch seams on the real singleton.
    Contract:
        enable() emits the twin (configuration freeze) and records
        "enabled"; disable() records "disabled" with the twin RETAINED.
    Returns:
        None.
    Raises:
        AssertionError: If the switch evicts or mis-states the twin.
    """
    crystallizer = _activate_crystallizer()
    nexus = Aether()._nexus
    nexus.enable(configuration=NexusConfiguration().with_defaults())
    summary = crystallizer.describe_profile()
    assert summary["has_nexus_crystal"] is True
    assert summary["nexus_state"] == "enabled"
    nexus.disable()
    summary = crystallizer.describe_profile()
    assert summary["nexus_state"] == "disabled"
    assert summary["has_nexus_crystal"] is True


def test_nexus_cleanup_records_cleaned_while_the_record_lives():
    """
    Purpose:
        Verify the live-world teardown state ("cleaned") is recorded.
    Contract:
        nexus.cleanup() with the crystallizer alive flips the recorded
        state to "cleaned"; the twin remains configured-history.
    Returns:
        None.
    Raises:
        AssertionError: If teardown fails to record.
    """
    crystallizer = _activate_crystallizer()
    nexus = Aether()._nexus
    nexus.enable(configuration=NexusConfiguration().with_defaults())
    nexus.cleanup()
    summary = crystallizer.describe_profile()
    assert summary["nexus_state"] == "cleaned"
    assert summary["has_nexus_crystal"] is True


def test_mutation_research_lifecycle_records_all_three_states():
    """
    Purpose:
        Verify the MR state-switch seams on the real singleton.
    Contract:
        Configuration activation emits the twin; activate records
        "enabled"; deactivate records "disabled"; cleanup (record alive)
        records "cleaned"; the twin survives all three.
    Returns:
        None.
    Raises:
        AssertionError: If any MR lifecycle flip fails to record.
    """
    crystallizer = _activate_crystallizer()
    research = MutationResearch()
    configuration = MutationResearchConfiguration().with_defaults()
    configuration.activate()
    research.activate(configuration)
    summary = crystallizer.describe_profile()
    assert summary["has_mutation_research_crystal"] is True
    assert summary["mutation_research_state"] == "enabled"
    research.deactivate()
    assert (
        crystallizer.describe_profile()["mutation_research_state"]
        == "disabled"
    )
    research.cleanup()
    summary = crystallizer.describe_profile()
    assert summary["mutation_research_state"] == "cleaned"
    assert summary["has_mutation_research_crystal"] is True


def test_mutation_research_composition_twin_survives_the_real_record():
    """
    Purpose:
        Prove the GroupedResearchNode twin + bootstrap loop END TO END on
        the REAL crystallizer (no mocks anywhere): a composition emitted
        through the live persistence sink survives root death and rebuilds
        in a REBORN root through the untouched-registry hydration lane at activation.
    Contract:
        register_group emits the composition twin; the recorded payload is
        JSON-serializable with the tagged group node inside; after
        cleanup + singleton reset, a fresh root's activate() (default
        hydrate_from_record=True) pulls the record and every grouped read
        answers over the hydrated registry.
    Returns:
        None.
    Raises:
        AssertionError: If any hop of the loop drops the composition.
    """
    import json

    crystallizer = _activate_crystallizer()
    research = MutationResearch()
    configuration = MutationResearchConfiguration().with_defaults()
    configuration.activate()
    research.activate(configuration, hydrate_from_record=False)
    research_set = research.research_set()
    member_a = "a" * 64
    member_b = "b" * 64
    research_set.register_spell(member_a)
    research_set.register_spell(member_b)
    research_set.create_lane("subsystem", lane_type="production")
    first = research_set.register_group(
        [member_a, member_b], lane="subsystem", author="mutation_0",
    )
    group_id = first.group_id

    # The REAL record carries the tagged composition, JSON-clean.
    recorded = crystallizer.describe_mutation_research_record()
    composition = recorded["composition_payload"]
    assert json.loads(json.dumps(composition)) == composition
    lanes = composition["default"]["organization"]["lanes"]
    group_payloads = [
        node
        for lane in lanes
        for node in lane.get("nodes", [])
        if node.get("node_type") == "group"
    ]
    assert [node["group_id"] for node in group_payloads] == [group_id]

    # EXPLICIT NODE OBJECTS on the live twin (owner ruling 2026-07-12):
    # both families as flat DB-storable rows, straight off the record.
    group_rows = recorded["grouped_research_nodes"]
    assert [row["group_id"] for row in group_rows] == [group_id]
    assert group_rows[0]["member_spell_ids"] == [member_a, member_b]
    assert group_rows[0]["lane_name"] == "subsystem"
    assert group_rows[0]["lane_type"] == "production"
    spell_rows = recorded["research_nodes"]
    assert {row["spell_id"] for row in spell_rows} == {member_a, member_b}
    assert json.loads(json.dumps(recorded)) == recorded

    # Root death, then REBIRTH through the bootstrap lane.
    research.cleanup()
    MutationResearch._reset_singleton_for_tests()
    reborn = MutationResearch()
    reborn_configuration = MutationResearchConfiguration().with_defaults()
    reborn_configuration.activate()
    reborn.activate(reborn_configuration)  # hydrate_from_record default

    view = reborn.group_view(group_id)
    assert view["member_count"] == 2
    assert sorted(view["members"].keys()) == [member_a, member_b]
    row = reborn.residency_view(group_id)
    assert row["node_type"] == "group"
    assert row["runtime"] == "informational"
    assert row["lane_name"] == "subsystem"
    assert row["lane_type"] == "production"
    story = reborn.group_history_view(group_id)
    assert "group_registered" in [
        entry["act"] for entry in story["entries"]
    ]


def test_frame_cleanup_evicts_the_frame_and_its_whole_subtree():
    """
    Purpose:
        Verify frame death through the REAL teardown cascade.
    Contract:
        frame.cleanup() cascades conduit -> spellbook teardown (subtree
        eviction seams fire), then the frame twin leaves; the aether twin
        (root config, above the posture gate) is unaffected.
    Returns:
        None.
    Raises:
        AssertionError: If the frame or its subtree leaves residue.
    """
    crystallizer, book, _conduit, _spell_id = _recorded_world()
    assert crystallizer.describe_profile()["frame_count"] == 1
    frame = Aether()._aetheric_frames.get(book._aetheric_frame_name)
    assert frame is not None
    frame.cleanup()
    summary = crystallizer.describe_profile()
    assert summary["frame_count"] == 0
    assert summary["conduit_count"] == 0
    assert summary["spell_crystal_count"] == 0
    assert summary["inactive_spell_crystal_count"] == 0
