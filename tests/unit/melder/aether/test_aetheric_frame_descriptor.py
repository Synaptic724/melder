from types import SimpleNamespace

import pytest

from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.frame_descriptor.conduit_record import ConduitRecord
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.frame_descriptor.spell_record import SpellRecord
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
    descriptor = FrameDescriptor("ops")
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
    descriptor = FrameDescriptor("ops")
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
    descriptor = FrameDescriptor("ops")
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
        detailed_profile=None,
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


def test_descriptor_replaces_and_removes_conduit_records_cleanly() -> None:
    """
    Verify conduit record replacement and removal cleanup old owned records.

    Contract:
        - Upserting the same conduit id replaces the old record.
        - Replaced and removed records are cleaned.
        - The final conduit record map reflects the last write.

    Returns:
        None.
    """
    descriptor = FrameDescriptor("ops")
    first_record = ConduitRecord(
        conduit_id="conduit-1",
        root_conduit_id="conduit-1",
        conduit_name="alpha",
        frame_name="ops",
        origin_spellbook_id="spellbook-1",
        conduit_state=ConduitState.normal,
        policy=Policies.default,
        peer_conduit_ids=tuple(),
    )
    second_record = ConduitRecord(
        conduit_id="conduit-1",
        root_conduit_id="conduit-1",
        conduit_name="beta",
        frame_name="ops",
        origin_spellbook_id="spellbook-2",
        conduit_state=ConduitState.normal,
        policy=Policies.outbound_only,
        peer_conduit_ids=("conduit-2",),
    )

    descriptor.upsert_conduit_record(first_record)
    descriptor.upsert_conduit_record(second_record)

    assert first_record.cleaned is True
    assert descriptor.conduit_records_by_id == {"conduit-1": second_record}

    descriptor.remove_conduit_record("conduit-1")

    assert second_record.cleaned is True
    assert descriptor.conduit_records_by_id == {}


def test_descriptor_replaces_spell_record_and_refreshes_indexes() -> None:
    """
    Verify spell record replacement cleans old state and refreshes indexes.

    Contract:
        - Replacing a spell record with the same record key cleans the old
          record.
        - Conduit/spellbook indexes are rebuilt from the replacement record.

    Returns:
        None.
    """
    descriptor = FrameDescriptor("ops")
    first_record = SpellRecord(
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
        detailed_profile=None,
    )
    second_record = SpellRecord(
        origin_spellbook_id="spellbook-1",
        frame_name="ops",
        owner_conduit_id="conduit-2",
        spell_id="spell-1",
        lineage_id="lineage-1",
        spell_name="SpellOneUpdated",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.read,
        existence=Existence.unique,
        binding_profile=None,
        resolution_profile=None,
        detailed_profile=None,
    )

    descriptor.upsert_spell_record(first_record)
    descriptor.upsert_spell_record(second_record)

    record_key = ("spellbook-1", "spell-1")
    assert first_record.cleaned is True
    assert descriptor.spell_records_by_key == {record_key: second_record}
    assert descriptor.spell_keys_by_conduit_id == {"conduit-2": {record_key}}
    assert descriptor.spell_keys_by_spellbook_id == {"spellbook-1": {record_key}}


def test_descriptor_remove_spell_record_cleans_record_and_indexes() -> None:
    """
    Verify spell record removal clears the owned record and both indexes.

    Contract:
        - Removing a stored spell record cleans it.
        - Conduit and spellbook secondary indexes are removed when empty.

    Returns:
        None.
    """
    descriptor = FrameDescriptor("ops")
    record = SpellRecord(
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
        detailed_profile=None,
    )
    record_key = ("spellbook-1", "spell-1")

    descriptor.upsert_spell_record(record)
    descriptor.remove_spell_record(record_key)

    assert record.cleaned is True
    assert descriptor.spell_records_by_key == {}
    assert descriptor.spell_keys_by_conduit_id == {}
    assert descriptor.spell_keys_by_spellbook_id == {}


def test_descriptor_detach_nexus_frame_record_clears_property_without_cleaning_record() -> None:
    """
    Verify detaching a Nexus frame record removes ownership without cleanup.

    Contract:
        - `detach_nexus_frame_record()` returns the current record.
        - Descriptor property becomes None after detach.
        - Detached record is not cleaned by the detach operation itself.

    Returns:
        None.
    """
    descriptor = FrameDescriptor("ops")
    frame_handle = SimpleNamespace(name="ops")
    nexus_frame_record = NexusFrameRecord(
        frame_name="ops",
        frame=frame_handle,
        nexus_frame_mode=NexusFrameMode.single,
        creator_rift_id="rift-1",
        owner_rift_id="rift-1",
        immutable=False,
    )

    descriptor.set_nexus_frame_record(nexus_frame_record)
    detached = descriptor.detach_nexus_frame_record()

    assert detached is nexus_frame_record
    assert descriptor.nexus_frame_record is None
    assert nexus_frame_record.cleaned is False


def test_descriptor_set_frame_handle_and_configuration_round_trip() -> None:
    """
    Verify frame handle and frame configuration are stored directly.

    Returns:
        None.
    """
    descriptor = FrameDescriptor("ops")
    frame_handle = SimpleNamespace(name="ops")
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-1",
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=True,
    )

    descriptor.set_frame_handle(frame_handle)
    descriptor.set_frame_configuration(frame_configuration)

    assert descriptor.frame_handle is frame_handle
    assert descriptor.frame_configuration is frame_configuration


def test_descriptor_remove_missing_records_is_no_op() -> None:
    """
    Verify missing conduit/spell removal paths do not invent failures.

    Returns:
        None.
    """
    descriptor = FrameDescriptor("ops")

    descriptor.remove_conduit_record("missing-conduit")
    descriptor.remove_spell_record(("spellbook-1", "missing-spell"))

    assert descriptor.conduit_records_by_id == {}
    assert descriptor.spell_records_by_key == {}


def test_descriptor_properties_raise_after_cleanup() -> None:
    """
    Verify descriptor getters fail after cleanup rather than returning stale
    state.

    Returns:
        None.
    """
    descriptor = FrameDescriptor("ops")
    descriptor.cleanup()

    with pytest.raises(RuntimeError):
        _ = descriptor.frame_name

    with pytest.raises(RuntimeError):
        _ = descriptor.frame_handle

    with pytest.raises(RuntimeError):
        _ = descriptor.frame_configuration

