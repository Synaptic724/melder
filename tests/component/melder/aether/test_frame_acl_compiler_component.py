from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.nexus.acl.frame_acl_compiler import FrameACLCompiler
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.aether.nexus.acl.profiles.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_profile import FrameACLProfile
from melder.aether.nexus.acl.profiles.frame_acl_rule import FrameACLRule
from melder.aether.nexus.acl.profiles.frame_acl_ruleset import FrameACLRuleSet
from melder.aether.nexus.acl.profiles.frame_acl_view_profile import (
    FrameACLViewProfile,
)
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
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.frame_acl_manager import FrameACLManager
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence


def _build_frame_descriptor() -> FrameDescriptor:
    """
    Build one minimal payload-backed frame descriptor for component tests.

    Returns:
        FrameDescriptor:
            Descriptor with frame, conduit, and spell truth.
    """
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
                    payload_type="detailed",
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


def test_component_compiler_uses_manager_seeded_safe_profiles() -> None:
    """
    Verify the compiler uses the manager-owned seeded safe profile catalog.

    Returns:
        None.
    """
    manager = FrameACLManager()
    compiler = FrameACLCompiler(manager.frame_acl_profile_builder)
    compiled_surface = compiler.compile_frame_access_surface(
        _build_frame_descriptor(),
        FrameACLConfiguration.create_default("ops"),
    )

    assert compiled_surface.view_profile_name == "safe"
    assert compiled_surface.codegen_profile_name == "safe"
    assert compiled_surface.allowed_commands == (
        "bind_existing",
        "query",
        "resolve_existing",
    )


def test_component_compiler_uses_registered_custom_profile_pair() -> None:
    """
    Verify the compiler respects custom profiles registered through the manager.

    Returns:
        None.
    """
    manager = FrameACLManager()
    manager._register_view_acl_profile(
        FrameACLViewProfile(
            "frame_only",
            minimum_spell_payload_type="detailed",
            frame_ruleset=FrameACLRuleSet(
                "frame_only_frame",
                rules=[
                    FrameACLRule(
                        rule_name="frame_visible",
                        operation="visible",
                        effect="allow",
                    ),
                    FrameACLRule(
                        rule_name="frame_show_payload",
                        operation="show_payload",
                        effect="allow",
                    ),
                ],
            ),
        )
    )
    manager._register_codegen_acl_profile(FrameACLCodegenProfile("query_only"))
    profile = manager._create_frame_acl_profile(
        "frame_only_contract",
        view_profile_name="frame_only",
        codegen_profile_name="query_only",
    )
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="custom_profile",
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration.from_profile(profile.view_profile)
    )
    configuration.set_codegen_configuration(
        configuration.codegen_configuration.from_profile(profile.codegen_profile)
    )
    configuration.finalize()

    compiled_surface = FrameACLCompiler(
        manager.frame_acl_profile_builder
    ).compile_frame_access_surface(_build_frame_descriptor(), configuration)

    assert compiled_surface.allowed_kinds == ("frame",)
    assert compiled_surface.allowed_commands == tuple()


def test_component_container_builder_commit_flows_into_compiler_output() -> None:
    """
    Verify container builder commits feed compiler output through the shared
    manager-owned profile catalog.

    Returns:
        None.
    """
    manager = FrameACLManager()
    container = manager._ensure_frame_acl_container("ops")
    builder = container.frame_acl_builder

    builder.begin_change()
    builder.apply_frame_acl_profile(
        FrameACLProfile(
            "support",
            view_profile=FrameACLViewProfile.create_hybrid(),
            codegen_profile=FrameACLCodegenProfile.create_permissive(),
        )
    )
    next_configuration = builder.commit_change()

    compiled_surface = FrameACLCompiler(
        manager.frame_acl_profile_builder
    ).compile_frame_access_surface(_build_frame_descriptor(), next_configuration)

    assert compiled_surface.view_profile_name == "hybrid"
    assert compiled_surface.codegen_profile_name == "permissive"
    assert "write_attribute" in compiled_surface.allowed_commands


def test_component_compiled_surface_flows_directly_into_frame_viewer_projection() -> None:
    """
    Verify compiled ACL output flows directly into descriptor-driven viewer projection.

    Returns:
        None.
    """
    compiler = FrameACLCompiler(FrameACLManager().frame_acl_profile_builder)
    descriptor = _build_frame_descriptor()
    compiled_surface = compiler.compile_frame_access_surface(
        descriptor,
        FrameACLConfiguration.create_default("ops"),
    )

    viewer = FrameViewer(
        frame_descriptors_by_name={"ops": descriptor},
        compiled_access_surfaces_by_frame_name={"ops": compiled_surface},
        default_view_frame_name="ops",
    )

    assert viewer.describe_frame("ops")["available_kinds"] == (
        "conduit",
        "frame",
        "spell",
    )
    assert len(viewer.list_available_targets()) == 3


def test_component_rollback_restores_original_compiled_command_surface() -> None:
    """
    Verify rolling back current ACL selection restores the original compiled
    command surface.

    Returns:
        None.
    """
    manager = FrameACLManager()
    container = manager._ensure_frame_acl_container("ops")
    original = container.frame_acl_configuration
    draft = FrameACLConfiguration.create_new_from_acl_configuration(
        original,
        reason="rollback_test",
    )
    draft.set_codegen_configuration(
        draft.codegen_configuration.from_profile(
            FrameACLCodegenProfile.create_permissive()
        )
    )
    draft.finalize()
    inserted = manager._insert_head_frame_acl_configuration(
        "ops",
        draft,
        select_as_current=True,
    )
    manager._rollback_frame_acl_configuration("ops", original.configuration_id)

    compiler = FrameACLCompiler(manager.frame_acl_profile_builder)
    rolled_back_surface = compiler.compile_frame_access_surface(
        _build_frame_descriptor(),
        manager._get_current_frame_acl_configuration("ops"),
    )
    inserted_surface = compiler.compile_frame_access_surface(
        _build_frame_descriptor(),
        inserted,
    )

    assert "write_attribute" not in rolled_back_surface.allowed_commands
    assert "write_attribute" in inserted_surface.allowed_commands

