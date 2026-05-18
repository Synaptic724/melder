from types import SimpleNamespace

import pytest
import threading
from typing import Optional, Tuple

from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.nexus.frame_descriptor.conduit_descriptor_payload import (
    ConduitDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.frame_descriptor.conduit_record import ConduitRecord
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.spell_descriptor_payload import (
    SpellDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.frame_descriptor.spell_record import SpellRecord
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence


def test_descriptor_replaces_owned_frame_overview() -> None:
    """
    Verify descriptor replacement cleans superseded owned frame metadata.

    Contract:
        - Replacing `frame_overview` cleans the old `FrameRecord`.

    Returns:
        None.
    """
    descriptor = FrameDescriptor("ops")
    first_overview = FrameRecord(
        frame_name="ops",
        frame_id="frame-1",
        config_origin_spellbook_id="spellbook-1",
        payload=_frame_payload(
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
        ),
    )
    second_overview = FrameRecord(
        frame_name="ops",
        frame_id="frame-1",
        config_origin_spellbook_id="spellbook-2",
        payload=_frame_payload(
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
        ),
    )

    descriptor.set_frame_overview(first_overview)
    descriptor.set_frame_overview(second_overview)

    assert first_overview.cleaned is True
    assert descriptor.frame_overview is second_overview


def test_descriptor_cleanup_cleans_owned_metadata_and_releases_lock() -> None:
    """
    Verify descriptor cleanup performs grouped teardown under the owned lock.

    Contract:
        - Owned frame overview is cleaned.
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
        payload=_frame_payload(
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
        ),
    )
    descriptor.set_frame_handle(frame_handle)
    descriptor.set_frame_configuration(frame_configuration)
    descriptor.set_frame_overview(frame_overview)

    descriptor.cleanup()

    assert frame_overview.cleaned is True
    assert not hasattr(descriptor, '_lock')


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
        frame_name="ops",
        origin_spellbook_id="spellbook-1",
        payload=_conduit_payload(
            conduit_name="alpha",
            conduit_state=ConduitState.normal,
            policy=Policies.default,
            peer_conduit_ids=tuple(),
        ),
    )
    spell_record = SpellRecord(
        origin_spellbook_id="spellbook-1",
        frame_name="ops",
        owner_conduit_id="conduit-1",
        spell_id="spell-1",
        spell_index_id="lineage-1",
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.create,
        existence=Existence.many,
        payload=_spell_payload(),
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
        frame_name="ops",
        origin_spellbook_id="spellbook-1",
        payload=_conduit_payload(
            conduit_name="alpha",
            conduit_state=ConduitState.normal,
            policy=Policies.default,
            peer_conduit_ids=tuple(),
        ),
    )
    second_record = ConduitRecord(
        conduit_id="conduit-1",
        root_conduit_id="conduit-1",
        frame_name="ops",
        origin_spellbook_id="spellbook-2",
        payload=_conduit_payload(
            conduit_name="beta",
            conduit_state=ConduitState.normal,
            policy=Policies.outbound_only,
            peer_conduit_ids=("conduit-2",),
        ),
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
        spell_index_id="lineage-1",
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.create,
        existence=Existence.many,
        payload=_spell_payload("general"),
    )
    second_record = SpellRecord(
        origin_spellbook_id="spellbook-1",
        frame_name="ops",
        owner_conduit_id="conduit-2",
        spell_id="spell-1",
        spell_index_id="lineage-1",
        spell_name="SpellOneUpdated",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.read,
        existence=Existence.unique,
        payload=_spell_payload(),
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
        spell_index_id="lineage-1",
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.create,
        existence=Existence.many,
        payload=_spell_payload(),
    )
    record_key = ("spellbook-1", "spell-1")

    descriptor.upsert_spell_record(record)
    descriptor.remove_spell_record(record_key)

    assert record.cleaned is True
    assert descriptor.spell_records_by_key == {}
    assert descriptor.spell_keys_by_conduit_id == {}
    assert descriptor.spell_keys_by_spellbook_id == {}


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


def test_descriptor_exposes_frame_name_and_cleanup_rechecks_cleaned_inside_lock() -> None:
    class _CoordinatedLock:
        def __init__(self, descriptor: FrameDescriptor) -> None:
            self._descriptor = descriptor
            self._entered_first = threading.Event()
            self._second_attempted = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self):
            if self._entered_first.is_set():
                self._second_attempted.set()
            self._lock.acquire()
            if not self._entered_first.is_set():
                self._entered_first.set()
                assert self._second_attempted.wait(timeout=1.0)
                self._descriptor._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    descriptor = FrameDescriptor("ops")
    conduit_record = ConduitRecord(
        conduit_id="conduit-1",
        root_conduit_id="conduit-1",
        frame_name="ops",
        origin_spellbook_id="spellbook-1",
        payload=_conduit_payload(
            conduit_name="alpha",
            conduit_state=ConduitState.normal,
            policy=Policies.default,
            peer_conduit_ids=tuple(),
        ),
    )
    spell_record = SpellRecord(
        origin_spellbook_id="spellbook-1",
        frame_name="ops",
        owner_conduit_id="conduit-1",
        spell_id="spell-1",
        spell_index_id="lineage-1",
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.create,
        existence=Existence.many,
        payload=_spell_payload(),
    )

    descriptor.upsert_conduit_record(conduit_record)
    descriptor.upsert_spell_record(spell_record)
    assert descriptor.frame_name == "ops"

    descriptor = FrameDescriptor("ops")
    descriptor._lock = _CoordinatedLock(descriptor)

    first = threading.Thread(target=descriptor.cleanup)
    second = threading.Thread(target=descriptor.cleanup)
    first.start()
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert descriptor.cleaned is True


def test_descriptor_cleanup_cleans_owned_conduit_and_spell_records() -> None:
    descriptor = FrameDescriptor("ops")
    conduit_record = ConduitRecord(
        conduit_id="conduit-1",
        root_conduit_id="conduit-1",
        frame_name="ops",
        origin_spellbook_id="spellbook-1",
        payload=_conduit_payload(
            conduit_name="alpha",
            conduit_state=ConduitState.normal,
            policy=Policies.default,
            peer_conduit_ids=tuple(),
        ),
    )
    spell_record = SpellRecord(
        origin_spellbook_id="spellbook-1",
        frame_name="ops",
        owner_conduit_id="conduit-1",
        spell_id="spell-1",
        spell_index_id="lineage-1",
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.create,
        existence=Existence.many,
        payload=_spell_payload(),
    )

    descriptor.upsert_conduit_record(conduit_record)
    descriptor.upsert_spell_record(spell_record)
    descriptor.cleanup()
    descriptor.cleanup()

    assert conduit_record.cleaned is True
    assert spell_record.cleaned is True

def _spell_payload(payload_type: str = "detailed") -> SpellDescriptorPayload:
    """
    Build a minimal spell payload for descriptor tests.

    Args:
        payload_type:
            Spell payload detail type.

    Returns:
        SpellDescriptorPayload: Descriptor-safe spell payload stub.
    """
    return SpellDescriptorPayload(
        payload_type=payload_type,
        binding_payload={},
        resolution_payload={},
        class_profile=None,
        callable_profile=None,
        metadata={},
        instance_members={},
        dynamic_access={},
    )


def _conduit_payload(
        *,
        conduit_name: Optional[str],
        conduit_state: ConduitState,
        policy: Optional[Policies],
        peer_conduit_ids: Tuple[str, ...],
) -> ConduitDescriptorPayload:
    """
    Build a minimal conduit payload for descriptor tests.

    Args:
        conduit_name:
            Optional conduit display name.
        conduit_state:
            Conduit runtime state.
        policy:
            Optional conduit policy.
        peer_conduit_ids:
            Peer conduit ids carried by the payload.

    Returns:
        ConduitDescriptorPayload: Descriptor-safe conduit payload stub.
    """
    return ConduitDescriptorPayload(
        conduit_name=conduit_name,
        conduit_state=conduit_state,
        policy=policy,
        peer_conduit_ids=peer_conduit_ids,
    )


def _frame_payload(
        *,
        system_state: SystemState,
        ai_native_enabled: bool,
        rift_enabled: bool,
        root_conduit_count: int,
        root_conduit_ids: Tuple[str, ...],
        named_root_conduits: Tuple[Tuple[str, str], ...],
        conduit_cloud_entry_count: int,
        conduit_cloud_names: Tuple[str, ...],
        cluster_count: int,
        cluster_names: Tuple[str, ...],
) -> FrameDescriptorPayload:
    """
    Build a minimal frame payload for descriptor tests.

    Args:
        system_state:
            Frame system state.
        ai_native_enabled:
            Whether AI-native posture is enabled.
        rift_enabled:
            Whether Rift publication is enabled.
        root_conduit_count:
            Count of root conduits.
        root_conduit_ids:
            Root conduit ids.
        named_root_conduits:
            Named root conduit pairs.
        conduit_cloud_entry_count:
            Conduit cloud entry count.
        conduit_cloud_names:
            Conduit cloud names.
        cluster_count:
            Cluster count.
        cluster_names:
            Cluster names.

    Returns:
        FrameDescriptorPayload: Descriptor-safe frame payload stub.
    """
    return FrameDescriptorPayload(
        system_state=system_state,
        ai_native_enabled=ai_native_enabled,
        rift_enabled=rift_enabled,
        root_conduit_count=root_conduit_count,
        root_conduit_ids=root_conduit_ids,
        named_root_conduits=named_root_conduits,
        conduit_cloud_entry_count=conduit_cloud_entry_count,
        conduit_cloud_names=conduit_cloud_names,
        cluster_count=cluster_count,
        cluster_names=cluster_names,
    )
