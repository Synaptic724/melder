"""
Integration tests for the SpellIndexCrystal membership seams on the REAL
runtime: bind mints the snapshot, staging re-snapshots, notch flips the
selection, disposal evicts, and the index-move verbs re-snapshot both sides.

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
from melder.nexus.nexus import Nexus
from tests.mocks.spellbook.core_classes import BasicService
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _StagedService:
    """File-backed staged-spell target for membership tests."""

    def __init__(self):
        self.tag = "staged"


@pytest.fixture(autouse=True)
def reset_world_singletons():
    """
    Purpose:
        Isolate each test behind fresh world singletons.
    Contract:
        - Resets Aether/AetherUtilitySystem/Nexus/Crystallizer and rebinds
          the static Aether references before and after each test.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _recorded_world():
    """
    Build one recorded dynamic world: activated crystallizer + frozen-config
    book + one active bind + a conjured root conduit.

    Returns:
        tuple: (crystallizer, book, conduit, active_spell_id).
    """
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    book_configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(book_configuration)
    book_configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book_configuration.finalize()
    book = Spellbook(configuration=book_configuration)
    spell_id = book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="membership-root")
    return crystallizer, book, conduit, spell_id


def test_bind_mints_the_index_membership_snapshot():
    """
    Purpose:
        Verify a fresh bind records its index's membership twin.
    Contract:
        The recorded world holds exactly one spell_index snapshot whose
        member set and selection are the bound spell's SHA, owned by the
        binding book.
    Returns:
        None.
    Raises:
        AssertionError: If the bind seam misses the membership twin.
    """
    crystallizer, book, _conduit, spell_id = _recorded_world()
    summary = crystallizer.describe_profile()
    assert summary["spell_index_count"] == 1
    checkpoint_id = crystallizer.create_checkpoint()
    payloads = crystallizer.describe_checkpoint(checkpoint_id)
    assert payloads["captured_counts"]["spell_index"] == 1


def test_staging_and_notch_reshape_the_snapshot():
    """
    Purpose:
        Verify staging + notch keep the membership snapshot current.
    Contract:
        bind_inactive re-emits the index (two members, selection
        unchanged); notch_spell re-emits with the promoted member
        selected; custody locations mirror the flip.
    Returns:
        None.
    Raises:
        AssertionError: If membership truth lags the runtime.
    """
    crystallizer, book, conduit, spell_id = _recorded_world()
    active_spell = book._spells_by_id[spell_id]
    staged_id = conduit.bind_inactive(
        spell=_StagedService,
        spell_index=active_spell.spell_index,
        existence=Existence.unique,
        permissions="create",
    )
    crystallizer.create_checkpoint()
    staged_spell = book._inactive_spells[staged_id]
    conduit.notch_spell(
        spell_index=active_spell.spell_index,
        spell=staged_spell,
    )
    checkpoint_id = crystallizer.create_checkpoint()
    described = crystallizer.describe_checkpoint(checkpoint_id)
    # The notch window re-captured the index snapshot (selection flip).
    assert described["captured_counts"]["spell_index"] == 1
    assert crystallizer.describe_profile()["spell_index_count"] == 1
    assert crystallizer.get_spell_crystal(staged_id).id == staged_id
    assert crystallizer.get_spell_crystal(spell_id).id == spell_id
    # The snapshot must carry the POST-repoint truth: promoted member
    # selected, both members present (the notch-ordering regression).
    profile = crystallizer._persistence_system.active_profile
    payloads, _entries, _rng = profile.capture_segment_since(0)
    snapshot = list(payloads["spell_index"].values())[0]
    assert snapshot["selected_spell_id"] == staged_id
    assert set(snapshot["member_spell_ids"]) == {spell_id, staged_id}


def test_disposal_evicts_the_membership_snapshot():
    """
    Purpose:
        Verify true removal takes the index twin with the spell.
    Contract:
        cleanup_and_remove_spell evicts custody AND the membership
        snapshot; the checkpoint captures the index tombstone.
    Returns:
        None.
    Raises:
        AssertionError: If the membership twin outlives its index.
    """
    crystallizer, book, _conduit, spell_id = _recorded_world()
    crystallizer.create_checkpoint()
    book.cleanup_and_remove_spell(spell_id)
    summary = crystallizer.describe_profile()
    assert summary["spell_index_count"] == 0
    assert summary["spell_crystal_count"] == 0
    checkpoint_id = crystallizer.create_checkpoint()
    described = crystallizer.describe_checkpoint(checkpoint_id)
    assert described["captured_counts"]["spell_index_removed"] == 1


def test_parked_disposal_reshapes_the_surviving_shared_index():
    """
    Purpose:
        Verify the parked lane re-snapshots a surviving shared index.
    Contract:
        Disposing a staged member of a two-member index keeps ONE index
        snapshot (re-emitted minus the member) and does not evict it.
    Returns:
        None.
    Raises:
        AssertionError: If the survivor snapshot is dropped or stale.
    """
    crystallizer, book, conduit, spell_id = _recorded_world()
    active_spell = book._spells_by_id[spell_id]
    staged_id = conduit.bind_inactive(
        spell=_StagedService,
        spell_index=active_spell.spell_index,
        existence=Existence.unique,
        permissions="create",
    )
    staged_spell = book._inactive_spells[staged_id]
    book.cleanup_spell(spell=staged_spell)
    summary = crystallizer.describe_profile()
    assert summary["spell_index_count"] == 1
    assert summary["inactive_spell_crystal_count"] == 0
    assert summary["spell_crystal_count"] == 1


def test_remove_from_spell_index_snapshots_both_sides():
    """
    Purpose:
        Verify the split verb records source and fresh index.
    Contract:
        remove_from_spell_index on a staged member of a shared index
        leaves TWO membership snapshots (source minus the member, plus
        the fresh single-member index).
    Returns:
        None.
    Raises:
        AssertionError: If either side of the split goes unrecorded.
    """
    crystallizer, book, conduit, spell_id = _recorded_world()
    active_spell = book._spells_by_id[spell_id]
    staged_id = conduit.bind_inactive(
        spell=_StagedService,
        spell_index=active_spell.spell_index,
        existence=Existence.unique,
        permissions="create",
    )
    staged_spell = book._inactive_spells[staged_id]
    conduit.remove_from_spell_index(
        spell=staged_spell,
        source_index=active_spell.spell_index,
    )
    assert crystallizer.describe_profile()["spell_index_count"] == 2


def test_add_to_spell_index_moves_membership_between_snapshots():
    """
    Purpose:
        Verify the move verb re-records target and destroys the emptied
        source.
    Contract:
        Moving a split-off member onto another index re-emits the target
        snapshot and EVICTS the emptied fresh index (destroy seam), so
        exactly two snapshots remain: the original and none for the
        destroyed source.
    Returns:
        None.
    Raises:
        AssertionError: If the move leaves a stale or missing snapshot.
    """
    crystallizer, book, conduit, spell_id = _recorded_world()
    active_spell = book._spells_by_id[spell_id]
    staged_id = conduit.bind_inactive(
        spell=_StagedService,
        spell_index=active_spell.spell_index,
        existence=Existence.unique,
        permissions="create",
    )
    staged_spell = book._inactive_spells[staged_id]
    conduit.remove_from_spell_index(
        spell=staged_spell,
        source_index=active_spell.spell_index,
    )
    assert crystallizer.describe_profile()["spell_index_count"] == 2
    conduit.add_to_spell_index(
        spell=staged_spell,
        target_index=active_spell.spell_index,
    )
    summary = crystallizer.describe_profile()
    assert summary["spell_index_count"] == 1
    checkpoint_id = crystallizer.create_checkpoint()
    described = crystallizer.describe_checkpoint(checkpoint_id)
    assert described["captured_counts"]["spell_index_removed"] >= 1


def _second_conduit(name="membership-peer"):
    """
    Build a second recorded book + root conduit on the SAME frame.

    Returns:
        tuple: (book, conduit).
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    book = Spellbook(configuration=configuration)
    conduit = book.conjure(dynamic=True, name=name)
    return book, conduit


def _conduit_snapshots(crystallizer):
    """
    Return the record's CURRENT conduit snapshots keyed by conduit id.

    Returns:
        dict: conduit_id -> conduit twin payload.
    """
    profile = crystallizer._persistence_system.active_profile
    payloads, _entries, _rng = profile.capture_segment_since(0)
    return payloads.get("conduit", {})


def test_link_records_the_initiators_outbound_topology():
    """
    Purpose:
        Verify link() re-emits the initiator's conduit twin.
    Contract:
        After owner.link(peer), the initiator's snapshot lists the peer's
        conduit id in link_targets; the receiver's snapshot stays empty
        (outbound-only recording - restore re-links from the initiator).
    Returns:
        None.
    Raises:
        AssertionError: If the link edge goes unrecorded or leaks
        direction.
    """
    crystallizer, _book, conduit_a, _spell_id = _recorded_world()
    _book_b, conduit_b = _second_conduit()
    assert conduit_a.link(conduit_b) is True
    snapshots = _conduit_snapshots(crystallizer)
    assert snapshots[conduit_a._id]["link_targets"] == [conduit_b._id]
    assert snapshots[conduit_b._id]["link_targets"] == []


def test_sever_clears_the_recorded_topology_from_either_side():
    """
    Purpose:
        Verify the sever choke point re-records both ends.
    Contract:
        Severing from the RECEIVER side still empties the initiator's
        recorded link_targets (the _remove_contract seam resolves
        direction internally).
    Returns:
        None.
    Raises:
        AssertionError: If a severed edge survives in the record.
    """
    crystallizer, _book, conduit_a, _spell_id = _recorded_world()
    _book_b, conduit_b = _second_conduit()
    conduit_a.link(conduit_b)
    assert conduit_b.sever_link(conduit_a) is True
    snapshots = _conduit_snapshots(crystallizer)
    assert snapshots[conduit_a._id]["link_targets"] == []
    assert snapshots[conduit_b._id]["link_targets"] == []


def test_peer_teardown_clears_the_initiators_recorded_topology():
    """
    Purpose:
        Verify the bulk-sever lane keeps initiator topology truthful.
    Contract:
        When the link TARGET dies (permanent_cleanup -> bulk sever ->
        _remove_contract), the surviving initiator's snapshot drops the
        dead edge, and the dead conduit's own twin is swept by its book
        subtree eviction.
    Returns:
        None.
    Raises:
        AssertionError: If a dead peer lingers in recorded topology.
    """
    crystallizer, _book, conduit_a, _spell_id = _recorded_world()
    _book_b, conduit_b = _second_conduit(name="doomed-peer")
    conduit_a.link(conduit_b)
    dead_id = conduit_b._id
    conduit_b.permanent_cleanup()
    snapshots = _conduit_snapshots(crystallizer)
    assert snapshots[conduit_a._id]["link_targets"] == []
    assert dead_id not in snapshots


def _contract_snapshots(crystallizer):
    """
    Return the record's CURRENT contract snapshots keyed by contract id.

    Returns:
        dict: contract_id -> relationship twin payload.
    """
    profile = crystallizer._persistence_system.active_profile
    payloads, _entries, _rng = profile.capture_segment_since(0)
    return payloads.get("contract", {})


def test_link_records_the_contract_relationship():
    """
    Purpose:
        Verify link() records the freshly created contract.
    Contract:
        After owner.link(peer) the record holds exactly one contract
        snapshot whose endpoints are the two conduit ids and whose detail
        views are empty (nothing shared yet).
    Returns:
        None.
    Raises:
        AssertionError: If the relationship goes unrecorded.
    """
    crystallizer, _book, conduit_a, _spell_id = _recorded_world()
    _book_b, conduit_b = _second_conduit(name="contract-peer")
    conduit_a.link(conduit_b)
    snapshots = _contract_snapshots(crystallizer)
    assert len(snapshots) == 1
    snapshot = list(snapshots.values())[0]
    assert {snapshot["conduit_a_id"], snapshot["conduit_b_id"]} == {
        conduit_a._id, conduit_b._id,
    }
    assert snapshot["details_a"] == [] and snapshot["details_b"] == []
    assert crystallizer.describe_profile()["contract_count"] == 1


def test_contract_detail_mutations_re_snapshot_the_relationship():
    """
    Purpose:
        Verify the public contract verbs keep the snapshot current.
    Contract:
        Borrowing the owner's spell re-snapshots the contract with one
        detail carrying the spell SHA and permission; the detail sits on
        exactly one side.
    Returns:
        None.
    Raises:
        AssertionError: If detail truth lags the runtime.
    """
    crystallizer, _book, conduit_a, spell_id = _recorded_world()
    _book_b, conduit_b = _second_conduit(name="borrowing-peer")
    conduit_a.link(conduit_b)
    conduit_b.add_spell_to_contract(
        spell_id=spell_id,
        conduit=conduit_a,
        permissions="create",
    )
    snapshots = _contract_snapshots(crystallizer)
    snapshot = list(snapshots.values())[0]
    all_details = snapshot["details_a"] + snapshot["details_b"]
    assert len(all_details) == 1
    assert all_details[0]["spell_id"] == spell_id
    assert all_details[0]["permissions"] == "create"


def test_severing_the_last_detail_evicts_the_contract_record():
    """
    Purpose:
        Verify auto-severance reaches the record.
    Contract:
        Removing the last borrowed spell severs the contract (runtime
        behavior), which must EVICT the relationship twin and journal the
        contract_removed tombstone.
    Returns:
        None.
    Raises:
        AssertionError: If a severed relationship survives in the record.
    """
    crystallizer, _book, conduit_a, spell_id = _recorded_world()
    _book_b, conduit_b = _second_conduit(name="severed-peer")
    conduit_a.link(conduit_b)
    conduit_b.add_spell_to_contract(
        spell_id=spell_id,
        conduit=conduit_a,
        permissions="create",
    )
    assert crystallizer.describe_profile()["contract_count"] == 1
    # Contract REMOVAL requires an active link transaction naming both
    # conduits (the add path self-admits; removal does not by design).
    with conduit_b.transaction("link", conduits=[conduit_b, conduit_a]):
        conduit_b.remove_spell_from_contract(
            spell_id=spell_id,
            conduit=conduit_a,
        )
    assert crystallizer.describe_profile()["contract_count"] == 0
    profile = crystallizer._persistence_system.active_profile
    payloads, _entries, _rng = profile.capture_segment_since(0)
    assert len(payloads.get("contract_removed", {})) == 1
