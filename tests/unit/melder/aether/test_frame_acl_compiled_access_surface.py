from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.nexus.acl.frame_acl_compiler import FrameACLCompiler
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.frame_descriptor.conduit_descriptor_payload import (
    ConduitDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.conduit_record import ConduitRecord
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.frame_descriptor.spell_descriptor_payload import (
    SpellDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.spell_record import SpellRecord
from melder.aether.nexus.rift.frame_link.frame_link_contract import FrameLinkContract
from melder.aether.nexus.rift.frame_link.profiles.frame_link_contract_profile import (
    FrameLinkContractProfile,
)
from melder.aether.nexus.rift.frame_link.profiles.frame_link_view_profile import (
    FrameLinkViewProfile,
)
from melder.aether.nexus.frame_acl_manager import FrameACLManager
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence


def test_compiler_builds_safe_effective_access_surface_from_descriptor_truth() -> None:
    """
    Verify the compiler derives effective access from descriptor truth plus the
    safe ACL configuration.

    Returns:
        None.
    """
    frame_descriptor = _build_frame_descriptor()
    compiler = FrameACLCompiler(FrameACLManager().frame_acl_profile_builder)
    configuration = FrameACLConfiguration.create_default("ops")

    compiled_surface = compiler.compile_frame_access_surface(
        frame_descriptor,
        configuration,
    )

    assert compiled_surface.frame_name == "ops"
    assert compiled_surface.view_profile_name == "safe"
    assert compiled_surface.codegen_profile_name == "safe"
    assert compiled_surface.allowed_kinds == ("conduit", "frame", "spell")
    assert compiled_surface.allowed_commands == (
        "bind_existing",
        "query",
        "resolve_existing",
    )
    assert compiled_surface.frame_payload_fields == (
        "ai_native_enabled",
        "cluster_count",
        "cluster_names",
        "conduit_cloud_entry_count",
        "conduit_cloud_names",
        "named_root_conduits",
        "rift_enabled",
        "root_conduit_count",
        "root_conduit_ids",
        "system_state",
    )
    assert compiled_surface.visible_conduit_ids == ("conduit-1",)
    assert compiled_surface.visible_spell_keys == (("spellbook-1", "spell-1"),)
    assert compiled_surface.conduit_payload_sections_by_id == {
        "conduit-1": ("conduit_name", "conduit_state"),
    }
    assert compiled_surface.spell_payload_sections_by_key == {
        ("spellbook-1", "spell-1"): (
            "binding_payload",
            "metadata",
            "resolution_payload",
        ),
    }


def test_frame_link_contract_can_be_shaped_from_compiled_access_surface() -> None:
    """
    Verify frame-link contracts are created from compiled ACL access output and
    can be narrowed by a downstream contract profile.

    Returns:
        None.
    """
    frame_descriptor = _build_frame_descriptor()
    compiler = FrameACLCompiler(FrameACLManager().frame_acl_profile_builder)
    configuration = FrameACLConfiguration.create_default("ops")
    compiled_surface = compiler.compile_frame_access_surface(
        frame_descriptor,
        configuration,
    )
    contract_profile = FrameLinkContractProfile(
        "frame_only",
        view_profile=FrameLinkViewProfile(
            "frame_only_view",
            allowed_kinds=("frame",),
            frame_payload_fields=("system_state",),
        ),
    )

    contract = FrameLinkContract.from_compiled_access_surface(
        compiled_surface,
        contract_profile=contract_profile,
    )

    assert contract.frame_name == "ops"
    assert contract.allowed_kinds == ("frame",)
    assert contract.metadata["frame_link_profile_name"] == "frame_only"
    assert contract.metadata["frame_payload_fields"] == ("system_state",)
    assert contract.metadata["conduit_payload_sections_by_id"] == {
        "conduit-1": tuple(),
    }
    assert contract.metadata["spell_payload_sections_by_key"] == {
        ("spellbook-1", "spell-1"): tuple(),
    }


def _build_frame_descriptor() -> FrameDescriptor:
    descriptor = FrameDescriptor("ops")
    descriptor.set_frame_overview(
        FrameRecord(
            frame_name="ops",
            frame_id="frame-1",
            config_origin_spellbook_id="spellbook-1",
            payload=FrameDescriptorPayload(
                system_state=SystemState.dynamic,
                ai_native_enabled=True,
                rift_enabled=True,
                root_conduit_count=1,
                root_conduit_ids=("conduit-1",),
                named_root_conduits=(("conduit-1", "default"),),
                conduit_cloud_entry_count=1,
                conduit_cloud_names=("default",),
                cluster_count=0,
                cluster_names=tuple(),
            ),
        )
    )
    descriptor.upsert_conduit_record(
        ConduitRecord(
            conduit_id="conduit-1",
            root_conduit_id="conduit-1",
            frame_name="ops",
            origin_spellbook_id="spellbook-1",
            payload=ConduitDescriptorPayload(
                conduit_name="default",
                conduit_state=ConduitState.normal,
                policy=Policies.default,
                peer_conduit_ids=tuple(),
            ),
        )
    )
    descriptor.upsert_spell_record(
        SpellRecord(
            origin_spellbook_id="spellbook-1",
            frame_name="ops",
            owner_conduit_id="conduit-1",
            spell_id="spell-1",
            lineage_id="lineage-1",
            spell_name="SpellOne",
            spellframe=None,
            binding_name="spell_one",
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=SpellDescriptorPayload(
                profile_name="detailed",
                binding_payload={"kind": "class"},
                resolution_payload={"requirements": []},
                class_profile={"methods": []},
                callable_profile=None,
                metadata={"doc": "spell"},
                instance_members={},
                dynamic_access={},
            ),
        )
    )
    return descriptor
