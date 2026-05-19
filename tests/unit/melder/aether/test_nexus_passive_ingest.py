import types

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.nexus.frame_descriptor.spell_descriptor_payload import (
    SpellDescriptorPayload,
)
from melder.aether.nexus.nexus import Nexus
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable


@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each passive-ingest test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()


def _bind_frame_posture(
        frame_name: str,
        *,
        rift_enabled: bool,
) -> None:
    """
    Bind one narrow frame posture into Aether for passive-ingest tests.

    Args:
        frame_name:
            Target frame name.
        rift_enabled:
            Whether the frame should be publishable into Nexus.

    Returns:
        None.
    """
    aether = Aether()
    aether._ensure_frame(frame_name)
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=rift_enabled,
    )
    aether._ensure_frame(frame_name).bind_frame_configuration(frame_configuration)


class _PayloadProfile(Cleanable):
    def __init__(self, name: str = "detailed") -> None:
        super().__init__()
        self.profile_name = name
        self.profile_version = "0.0.1"
        self.binding_profile = object()
        self.resolution_profile = object()

    def to_descriptor_payload(self) -> SpellDescriptorPayload:
        return SpellDescriptorPayload(
            payload_type=self.profile_name,
            binding_payload={},
            resolution_payload={},
            class_profile=None,
            callable_profile=None,
            metadata={},
            instance_members={},
            dynamic_access={},
        )

    def complete_with_spell(self, spell) -> None:
        return None

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True


def test_publish_frame_record_does_not_require_nexus_enable() -> None:
    """
    Verify frame publication succeeds before interactive Nexus enablement.

    Returns:
        None.
    """
    _bind_frame_posture("ops", rift_enabled=True)
    nexus = Nexus()
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")

    assert nexus.is_enabled is False
    assert nexus._publish_frame_record(spellbook) is True

    record = nexus._get_required_frame_descriptor("ops").frame_overview

    assert record.frame_name == "ops"
    assert record.config_origin_spellbook_id == "spellbook-alpha"
    assert record.payload.rift_enabled is True
    assert record.payload.root_conduit_count == 0
    assert record.payload.root_conduit_ids == tuple()
    assert record.payload.named_root_conduits == tuple()
    assert record.payload.conduit_cloud_entry_count == 0
    assert record.payload.conduit_cloud_names == tuple()
    assert record.payload.cluster_count == 0
    assert record.payload.cluster_names == tuple()


def test_publish_frame_record_captures_frame_summary() -> None:
    """
    Verify frame publication captures cheap topology summary fields.

    Returns:
        None.
    """
    _bind_frame_posture("ops", rift_enabled=True)
    aether = Aether()
    frame = aether._ensure_frame("ops")
    conduit_alpha = types.SimpleNamespace(_id="conduit-a", _name="alpha")
    conduit_beta = types.SimpleNamespace(_id="conduit-b", _name=None)
    frame._conduits["conduit-a"] = conduit_alpha
    frame._conduits["conduit-b"] = conduit_beta
    frame._conduit_cloud._registry["alpha"] = conduit_alpha
    frame._conduit_cloud._conduit_clusters["cluster-z"] = types.SimpleNamespace()
    frame._conduit_cloud._conduit_clusters["cluster-a"] = types.SimpleNamespace()

    nexus = Nexus()
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")

    assert nexus._publish_frame_record(spellbook) is True

    record = nexus._get_required_frame_descriptor("ops").frame_overview

    assert record.payload.root_conduit_count == 2
    assert record.payload.root_conduit_ids == ("conduit-a", "conduit-b")
    assert record.payload.named_root_conduits == (("conduit-a", "alpha"),)
    assert record.payload.conduit_cloud_entry_count == 1
    assert record.payload.conduit_cloud_names == ("alpha",)
    assert record.payload.cluster_count == 2
    assert record.payload.cluster_names == ("cluster-a", "cluster-z")


def test_publish_methods_short_circuit_when_frame_is_not_publishable() -> None:
    """
    Verify passive publication returns early when frame posture denies Rift.

    Returns:
        None.
    """
    _bind_frame_posture("ops", rift_enabled=False)
    nexus = Nexus()

    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")
    spell = types.SimpleNamespace(
        profile=None,
        resolution_profile=None,
        spell_id="spell-1",
        spell_index=types.SimpleNamespace(id="lineage-1"),
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.create,
        existence=Existence.many,
    )
    conduit = types.SimpleNamespace(
        _id="conduit-1",
        _root_conduit_id="conduit-1",
        _name="root",
        _aetheric_frame="ops",
        _spellbook=spellbook,
        _conduit_state=ConduitState.normal,
        _conduit_ward=types.SimpleNamespace(
            _policy=Policies.default,
            _parent_conduit=None,
            _get_links=lambda: [],
        ),
    )

    assert nexus._publish_frame_record(spellbook) is False
    assert nexus._publish_conduit_record(conduit) is False
    assert nexus._publish_spell_record(spellbook, spell, "conduit-1") is False
    descriptor = nexus._get_required_frame_descriptor("ops")
    assert descriptor.frame_overview is None
    assert descriptor.conduit_records_by_id == {}
    assert descriptor.spell_records_by_key == {}


def test_publish_spell_record_updates_primary_store_and_indexes() -> None:
    """
    Verify spell publication writes the primary record and secondary indexes.

    Returns:
        None.
    """
    _bind_frame_posture("ops", rift_enabled=True)
    nexus = Nexus()
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")
    spell = types.SimpleNamespace(
        profile=_PayloadProfile(),
        spell_id="spell-1",
        spell_index=types.SimpleNamespace(id="lineage-1"),
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.create,
        existence=Existence.many,
    )

    assert nexus._publish_spell_record(spellbook, spell, "conduit-1") is True

    record_key = ("spellbook-alpha", "spell-1")
    descriptor = nexus._get_required_frame_descriptor("ops")
    assert record_key in descriptor.spell_records_by_key
    assert record_key in descriptor.spell_keys_by_conduit_id["conduit-1"]
    assert record_key in descriptor.spell_keys_by_spellbook_id["spellbook-alpha"]


def test_publish_conduit_record_includes_lesser_conduits_in_passive_ingest() -> None:
    """
    Verify passive ingest now publishes ordinary lesser conduits as records.

    Returns:
        None.
    """
    _bind_frame_posture("ops", rift_enabled=True)
    nexus = Nexus()
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")
    conduit = types.SimpleNamespace(
        _id="conduit-1",
        _root_conduit_id="root-1",
        _name="lesser",
        _aetheric_frame="ops",
        _spellbook=spellbook,
        _conduit_state=ConduitState.lesser,
        _conduit_ward=types.SimpleNamespace(
            _policy=Policies.default,
            _parent_conduit=None,
            _get_links=lambda: [],
        ),
    )

    assert nexus._publish_conduit_record(conduit) is True

    descriptor = nexus._get_required_frame_descriptor("ops")

    assert descriptor.conduit_records_by_id["conduit-1"].payload.conduit_state is ConduitState.lesser
    assert descriptor.conduit_records_by_id["conduit-1"].payload.conduit_name == "lesser"


def test_remove_spell_and_conduit_records_clear_indexes() -> None:
    """
    Verify record removals clean their associated secondary indexes.

    Returns:
        None.
    """
    _bind_frame_posture("ops", rift_enabled=True)
    nexus = Nexus()
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")
    conduit = types.SimpleNamespace(
        _id="conduit-1",
        _root_conduit_id="conduit-1",
        _name="root",
        _aetheric_frame="ops",
        _spellbook=spellbook,
        _conduit_state=ConduitState.normal,
        _conduit_ward=types.SimpleNamespace(
            _policy=Policies.default,
            _parent_conduit=None,
            _get_links=lambda: [],
        ),
    )
    spell = types.SimpleNamespace(
        profile=_PayloadProfile(),
        spell_id="spell-1",
        spell_index=types.SimpleNamespace(id="lineage-1"),
        spell_name="SpellOne",
        spellframe=None,
        binding_name="spell_one",
        permissions=Permissions.create,
        existence=Existence.many,
    )

    assert nexus._publish_conduit_record(conduit) is True
    assert nexus._publish_spell_record(spellbook, spell, "conduit-1") is True

    nexus._remove_spell_record("spellbook-alpha", "spell-1", "ops")
    nexus._remove_conduit_record("conduit-1", "ops")

    descriptor = nexus._get_required_frame_descriptor("ops")
    assert descriptor.spell_records_by_key == {}
    assert descriptor.conduit_records_by_id == {}
    assert descriptor.spell_keys_by_conduit_id == {}
    assert descriptor.spell_keys_by_spellbook_id == {}

