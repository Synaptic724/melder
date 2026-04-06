import types

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.nexus.frame_descriptor.spell_descriptor_payload import (
    SpellDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor_manager import FrameDescriptorManager
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable


def _bind_frame_posture(
        frame_name: str,
        *,
        rift_enabled: bool,
) -> Aether:
    """
    Bind one frame posture for manager component tests.

    Args:
        frame_name:
            Target frame name.
        rift_enabled:
            Whether passive publication should be allowed.

    Returns:
        Aether: Active Aether singleton.
    """
    aether = Aether()
    aether._ensure_frame(frame_name)
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=rift_enabled,
    )
    aether._bind_aetheric_frame_configuration(frame_configuration, frame_name)
    return aether


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


def test_component_manager_keeps_frame_conduit_and_spell_records_coherent() -> None:
    """
    Purpose:
        Validate the manager keeps mixed frame/conduit/spell state coherent
        across real Aether frame posture and record publication.
    Contract:
        - Frame overview, conduit records, and spell records all land under one
          descriptor.
        - Secondary spell indexes match the published spell record.
        - Removing the spell and conduit clears the secondary indexes.
    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = _bind_frame_posture("ops", rift_enabled=True)
    manager = FrameDescriptorManager(aether)
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

    try:
        assert manager._publish_frame_record(spellbook) is True
        assert manager._publish_conduit_record(conduit) is True
        assert manager._publish_spell_record(spellbook, spell, "conduit-1") is True

        descriptor = manager._get_required_frame_descriptor("ops")
        record_key = ("spellbook-alpha", "spell-1")
        assert descriptor.frame_overview is not None
        assert descriptor.frame_overview.payload.rift_enabled is True
        assert descriptor.conduit_records_by_id["conduit-1"].payload.conduit_name == "root"
        assert record_key in descriptor.spell_records_by_key
        assert descriptor.spell_keys_by_conduit_id == {"conduit-1": {record_key}}
        assert descriptor.spell_keys_by_spellbook_id == {"spellbook-alpha": {record_key}}

        assert manager._remove_spell_record("spellbook-alpha", "spell-1", "ops") is True
        assert manager._remove_conduit_record("conduit-1", "ops") is True

        descriptor = manager._get_required_frame_descriptor("ops")
        assert descriptor.spell_records_by_key == {}
        assert descriptor.conduit_records_by_id == {}
        assert descriptor.spell_keys_by_conduit_id == {}
        assert descriptor.spell_keys_by_spellbook_id == {}
    finally:
        manager.cleanup()
        Aether._reset_singleton_for_tests()
        AetherUtilitySystem._reset_singleton_for_tests()
