from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.acl.frame_acl_compiler import (
    FrameACLCompiler,
)
from melder.aether.nexus.acl.frame_acl_configuration import (
    FrameACLConfiguration,
)
from melder.aether.nexus.acl.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.aether.nexus.acl.profiles.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_rule import (
    FrameACLRule,
)
from melder.aether.nexus.acl.profiles.frame_acl_ruleset import (
    FrameACLRuleSet,
)
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
from melder.aether.nexus.frame_acl_manager import FrameACLManager
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence


def _build_frame_descriptor() -> FrameDescriptor:
    """
    Build one minimal payload-backed frame descriptor for compiler tests.

    Returns:
        FrameDescriptor:
            Descriptor with one frame record, one conduit, and one spell.
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


def _build_compiler() -> FrameACLCompiler:
    """
    Build one compiler using the manager-owned reusable profile catalog.

    Returns:
        FrameACLCompiler:
            ACL compiler bound to the real profile builder.
    """
    return FrameACLCompiler(FrameACLManager().frame_acl_profile_builder)


def test_compiled_access_surface_snapshot_dicts_are_detached() -> None:
    """
    Verify compiled surface dict snapshots are detached from internal storage.

    Returns:
        None.
    """
    surface = CompiledFrameACLAccessSurface(
        frame_name="ops",
        configuration_id="cfg-1",
        view_profile_name="safe",
        view_profile_version="0.0.1",
        codegen_profile_name="safe",
        codegen_profile_version="0.0.1",
        allowed_kinds=("frame",),
        allowed_commands=("query",),
        frame_payload_fields=("system_state",),
        visible_conduit_ids=("conduit-1",),
        visible_spell_keys=(("spellbook-1", "spell-1"),),
        conduit_payload_sections_by_id={"conduit-1": ("conduit_name",)},
        spell_payload_sections_by_key={
            ("spellbook-1", "spell-1"): ("binding_payload",),
        },
        metadata={"source": "compiled"},
    )

    conduit_snapshot = surface.conduit_payload_sections_by_id
    spell_snapshot = surface.spell_payload_sections_by_key
    metadata_snapshot = surface.metadata
    conduit_snapshot["conduit-1"] = ("mutated",)
    spell_snapshot[("spellbook-1", "spell-1")] = ("mutated",)
    metadata_snapshot["source"] = "mutated"

    assert surface.conduit_payload_sections_by_id == {
        "conduit-1": ("conduit_name",),
    }
    assert surface.spell_payload_sections_by_key == {
        ("spellbook-1", "spell-1"): ("binding_payload",),
    }
    assert surface.metadata == {"source": "compiled"}


def test_compiled_access_surface_cleanup_clears_owned_state() -> None:
    """
    Verify compiled surface cleanup clears all owned state.

    Returns:
        None.
    """
    surface = _build_compiler().compile_frame_access_surface(
        _build_frame_descriptor(),
        FrameACLConfiguration.create_default("ops"),
    )

    surface.cleanup()

    assert surface.cleaned is True
    assert surface._frame_name is None
    assert surface._configuration_id is None
    assert surface._allowed_kinds is None
    assert surface._allowed_commands is None
    assert surface._conduit_payload_sections_by_id is None
    assert surface._spell_payload_sections_by_key is None


def test_frame_acl_compiler_init_rejects_missing_profile_builder() -> None:
    """
    Verify compiler construction rejects a missing reusable profile builder.

    Returns:
        None.
    """
    import pytest

    with pytest.raises(TypeError, match="profile_builder cannot be None"):
        FrameACLCompiler(None)


def test_frame_acl_compiler_rejects_invalid_descriptor_input() -> None:
    """
    Verify compiler rejects invalid descriptor inputs.

    Returns:
        None.
    """
    import pytest

    with pytest.raises(TypeError, match="frame_descriptor must be a FrameDescriptor"):
        _build_compiler().compile_frame_access_surface(
            None,
            FrameACLConfiguration.create_default("ops"),
        )


def test_frame_acl_compiler_rejects_invalid_configuration_input() -> None:
    """
    Verify compiler rejects invalid configuration inputs.

    Returns:
        None.
    """
    import pytest

    with pytest.raises(TypeError, match="configuration must be a FrameACLConfiguration"):
        _build_compiler().compile_frame_access_surface(
            _build_frame_descriptor(),
            None,
        )


def test_collect_operation_effects_splits_allow_and_deny_rules() -> None:
    """
    Verify operation effect collection separates allow and deny operations.

    Returns:
        None.
    """
    ruleset = FrameACLRuleSet(
        "spell_rules",
        rules=[
            FrameACLRule(
                rule_name="visible",
                operation="visible",
                effect="allow",
            ),
            FrameACLRule(
                rule_name="hide_dynamic_access",
                operation="show_dynamic_access",
                effect="deny",
            ),
        ],
    )

    allow_operations, deny_operations = FrameACLCompiler._collect_operation_effects(
        ruleset
    )

    assert allow_operations == {"visible"}
    assert deny_operations == {"show_dynamic_access"}


def test_collect_effective_operation_effects_unions_base_and_override_rules() -> None:
    """
    Verify effective effect collection unions base and override rule effects.

    Returns:
        None.
    """
    base_ruleset = FrameACLRuleSet(
        "base",
        rules=[
            FrameACLRule(
                rule_name="visible",
                operation="visible",
                effect="allow",
            )
        ],
    )
    override_ruleset = FrameACLRuleSet(
        "override",
        rules=[
            FrameACLRule(
                rule_name="hide_dynamic_access",
                operation="show_dynamic_access",
                effect="deny",
            )
        ],
    )

    allow_operations, deny_operations = (
        FrameACLCompiler._collect_effective_operation_effects(
            base_ruleset,
            override_ruleset,
        )
    )

    assert allow_operations == {"visible"}
    assert deny_operations == {"show_dynamic_access"}


def test_frame_acl_compiler_frame_payload_denial_hides_frame_kind() -> None:
    """
    Verify denying frame payload visibility removes frame-kind output.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="frame_hide",
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration.from_profile(
            FrameACLViewProfile.create_safe(),
            frame_override_ruleset=FrameACLRuleSet(
                "frame_override",
                rules=[
                    FrameACLRule(
                        rule_name="hide_frame_payload",
                        operation="show_payload",
                        effect="deny",
                    )
                ],
            ),
        )
    )
    configuration.finalize()

    compiled_surface = _build_compiler().compile_frame_access_surface(
        _build_frame_descriptor(),
        configuration,
    )

    assert "frame" not in compiled_surface.allowed_kinds
    assert compiled_surface.frame_payload_fields == tuple()


def test_frame_acl_compiler_conduit_visibility_denial_hides_conduits() -> None:
    """
    Verify denying conduit visibility removes conduit access output.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="conduit_hide",
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration.from_profile(
            FrameACLViewProfile.create_safe(),
            conduit_override_ruleset=FrameACLRuleSet(
                "conduit_override",
                rules=[
                    FrameACLRule(
                        rule_name="hide_conduit",
                        operation="visible",
                        effect="deny",
                    )
                ],
            ),
        )
    )
    configuration.finalize()

    compiled_surface = _build_compiler().compile_frame_access_surface(
        _build_frame_descriptor(),
        configuration,
    )

    assert "conduit" not in compiled_surface.allowed_kinds
    assert compiled_surface.visible_conduit_ids == tuple()


def test_frame_acl_compiler_spell_visibility_denial_hides_spells() -> None:
    """
    Verify denying spell visibility removes spell access output.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="spell_hide",
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration.from_profile(
            FrameACLViewProfile.create_safe(),
            spell_override_ruleset=FrameACLRuleSet(
                "spell_override",
                rules=[
                    FrameACLRule(
                        rule_name="hide_spell",
                        operation="visible",
                        effect="deny",
                    )
                ],
            ),
        )
    )
    configuration.finalize()

    compiled_surface = _build_compiler().compile_frame_access_surface(
        _build_frame_descriptor(),
        configuration,
    )

    assert "spell" not in compiled_surface.allowed_kinds
    assert compiled_surface.visible_spell_keys == tuple()


def test_frame_acl_compiler_permissive_codegen_profile_expands_allowed_commands() -> None:
    """
    Verify permissive codegen profiles widen the derived command surface.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="permissive_codegen",
    )
    configuration.set_codegen_configuration(
        configuration.codegen_configuration.from_profile(
            FrameACLCodegenProfile.create_permissive()
        )
    )
    configuration.finalize()

    compiled_surface = _build_compiler().compile_frame_access_surface(
        _build_frame_descriptor(),
        configuration,
    )

    assert "local_create" in compiled_surface.allowed_commands
    assert "write_attribute" in compiled_surface.allowed_commands
    assert "transfer_ownership" in compiled_surface.allowed_commands


def test_frame_acl_compiler_codegen_override_deny_removes_allowed_command() -> None:
    """
    Verify deny overrides remove commands that a base profile would allow.

    Returns:
        None.
    """
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="deny_query",
    )
    configuration.set_codegen_configuration(
        configuration.codegen_configuration.from_profile(
            FrameACLCodegenProfile.create_safe(),
            frame_override_ruleset=FrameACLRuleSet(
                "frame_override",
                rules=[
                    FrameACLRule(
                        rule_name="deny_query",
                        operation="query",
                        effect="deny",
                    )
                ],
            ),
        )
    )
    configuration.finalize()

    compiled_surface = _build_compiler().compile_frame_access_surface(
        _build_frame_descriptor(),
        configuration,
    )

    assert "query" not in compiled_surface.allowed_commands
    assert compiled_surface.allowed_commands == (
        "bind_existing",
        "resolve_existing",
    )


def test_frame_acl_compiler_metadata_counts_follow_visible_entities() -> None:
    """
    Verify compiled metadata counts follow the visible entity counts.

    Returns:
        None.
    """
    compiled_surface = _build_compiler().compile_frame_access_surface(
        _build_frame_descriptor(),
        FrameACLConfiguration.create_default("ops"),
    )

    assert compiled_surface.metadata["visible_conduit_count"] == 1
    assert compiled_surface.metadata["visible_spell_count"] == 1
