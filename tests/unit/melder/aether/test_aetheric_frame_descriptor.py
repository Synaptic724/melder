from types import SimpleNamespace

from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.nexus.aetheric_frame_descriptor import AethericFrameDescriptor
from melder.aether.nexus.canonical_store.conduit_record import ConduitRecord
from melder.aether.nexus.canonical_store.frame_record import FrameRecord
from melder.aether.nexus.canonical_store.spell_record import SpellRecord
from melder.aether.nexus.nexus_frame_record import NexusFrameRecord
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.nexus.configuration.nexus_frame_mode import NexusFrameMode
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence


def test_descriptor_replaces_owned_frame_overview_and_nexus_frame_record() -> None:
    """
    Verify descriptor replacement cleans superseded owned metadata objects.

    Contract:
        - Replacing `frame_overview` cleans the old `FrameRecord`.
        - Replacing `nexus_frame_record` cleans the old `NexusFrameRecord`.

    Returns:
        None.
    """
    descriptor = AethericFrameDescriptor("ops")
    frame_handle = SimpleNamespace(name="ops")

    first_overview = FrameRecord(
        frame_name="ops",
        frame_id="frame-1",
        config_origin_spellbook_id="spellbook-1",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=True,
        root_conduit_count=0,
        root_conduit_ids=tuple(),
        named_root_conduits=tuple(),
        conduit_cloud_entry_count=0,
        conduit_cloud_names=tuple(),
        cluster_count=0,
        cluster_names=tuple(),
    )
    second_overview = FrameRecord(
        frame_name="ops",
        frame_id="frame-1",
        config_origin_spellbook_id="spellbook-2",
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=True,
        root_conduit_count=1,
        root_conduit_ids=("conduit-1",),
        named_root_conduits=(("conduit-1", "alpha"),),
        conduit_cloud_entry_count=1,
        conduit_cloud_names=("alpha",),
        cluster_count=1,
        cluster_names=("cluster-1",),
    )

    first_nexus_record = NexusFrameRecord(
        frame_name="ops",
        frame=frame_handle,
        nexus_frame_mode=NexusFrameMode.single,
        creator_rift_id="rift-1",
        owner_rift_id="rift-1",
        immutable=False,
    )
    second_nexus_record = NexusFrameRecord(
        frame_name="ops",
        frame=frame_handle,
        nexus_frame_mode=NexusFrameMode.single,
        creator_rift_id="rift-2",
        owner_rift_id="rift-2",
        immutable=True,
    )

    descriptor.set_frame_overview(first_overview)
    descriptor.set_frame_overview(second_overview)
    descriptor.set_nexus_frame_record(first_nexus_record)
    descriptor.set_nexus_frame_record(second_nexus_record)

    assert first_overview.cleaned is True
    assert first_nexus_record.cleaned is True
    assert descriptor.frame_overview is second_overview
    assert descriptor.nexus_frame_record is second_nexus_record


def test_descriptor_cleanup_cleans_owned_metadata_and_releases_lock() -> None:
    """
    Verify descriptor cleanup performs grouped teardown under the owned lock.

    Contract:
        - Owned frame overview and Nexus frame record are cleaned.
        - Descriptor grouped state is nulled.
        - Descriptor lock is released and nulled last.

    Returns:
        None.
    """
    descriptor = AethericFrameDescriptor("ops")
    frame_handle = SimpleNamespace(name="ops")
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-1",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=True,
    )
    frame_overview = FrameRecord(
        frame_name="ops",
        frame_id="frame-1",
        config_origin_spellbook_id="spellbook-1",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=True,
        root_conduit_count=0,
        root_conduit_ids=tuple(),
        named_root_conduits=tuple(),
        conduit_cloud_entry_count=0,
        conduit_cloud_names=tuple(),
        cluster_count=0,
        cluster_names=tuple(),
    )
    nexus_frame_record = NexusFrameRecord(
        frame_name="ops",
        frame=frame_handle,
        nexus_frame_mode=NexusFrameMode.single,
        creator_rift_id="rift-1",
        owner_rift_id="rift-1",
        immutable=False,
    )

    descriptor.set_frame_handle(frame_handle)
    descriptor.set_frame_configuration(frame_configuration)
    descriptor.set_frame_overview(frame_overview)
    descriptor.set_nexus_frame_record(nexus_frame_record)

    descriptor.cleanup()

    assert frame_overview.cleaned is True
    assert nexus_frame_record.cleaned is True
    assert descriptor._lock is None


def test_descriptor_collection_properties_return_snapshots() -> None:
    """
    Verify descriptor collection properties do not expose live mutable state.

    Contract:
        - Map properties return snapshots rather than owned dict instances.
        - Nested set indexes are copied so caller mutation cannot affect the
          descriptor.

    Returns:
        None.
    """
    descriptor = AethericFrameDescriptor("ops")
    conduit_record = ConduitRecord(
        conduit_id="conduit-1",
        root_conduit_id="conduit-1",
        conduit_name="alpha",
        frame_name="ops",
        origin_spellbook_id="spellbook-1",
        conduit_state=ConduitState.normal,
        policy=Policies.default,
        peer_conduit_ids=tuple(),
    )
    spell_record = SpellRecord(
        origin_spellbook_id="spellbook-1",
        frame_name="ops",
        owner_conduit_id="conduit-1",
        spell_id="spell-1",
        lineage_id="lineage-1",
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.create,
        existence=Existence.many,
        binding_profile=None,
        resolution_profile=None,
        ai_profile=None,
    )

    descriptor.upsert_conduit_record(conduit_record)
    descriptor.upsert_spell_record(spell_record)

    conduit_snapshot = descriptor.conduit_records_by_id
    spell_snapshot = descriptor.spell_records_by_key
    conduit_spell_index_snapshot = descriptor.spell_keys_by_conduit_id
    spellbook_spell_index_snapshot = descriptor.spell_keys_by_spellbook_id

    conduit_snapshot.clear()
    spell_snapshot.clear()
    conduit_spell_index_snapshot["conduit-1"].clear()
    spellbook_spell_index_snapshot["spellbook-1"].clear()

    assert descriptor.conduit_records_by_id == {"conduit-1": conduit_record}
    assert descriptor.spell_records_by_key == {
        ("spellbook-1", "spell-1"): spell_record,
    }
    assert descriptor.spell_keys_by_conduit_id == {
        "conduit-1": {("spellbook-1", "spell-1")},
    }
    assert descriptor.spell_keys_by_spellbook_id == {
        "spellbook-1": {("spellbook-1", "spell-1")},
    }
