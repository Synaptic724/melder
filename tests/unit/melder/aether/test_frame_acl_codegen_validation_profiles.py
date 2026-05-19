from types import SimpleNamespace

import pytest

from melder.aether.nexus.acl.frame_acl_compiler import FrameACLCompiler
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.configurations.profiles.builder.frame_acl_profile_builder import (
    FrameACLProfileBuilder,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_rule import (
    FrameACLRule,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import (
    FrameACLRuleSet,
)
from melder.aether.nexus.acl.validator.frame_acl_validator import FrameACLValidator
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.spellbook.configuration.system_state import SystemState


def _build_frame_descriptor() -> FrameDescriptor:
    descriptor = FrameDescriptor("ops")
    descriptor.set_frame_handle(SimpleNamespace(name="ops"))
    descriptor.set_frame_overview(
        FrameRecord(
            frame_name="ops",
            frame_id="ops-frame",
            config_origin_spellbook_id="ops-spellbook",
            payload=FrameDescriptorPayload(
                system_state=SystemState.dynamic,
                ai_native_enabled=True,
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
    )
    return descriptor


def _build_compiler() -> FrameACLCompiler:
    return FrameACLCompiler(FrameACLProfileBuilder())


def test_frame_acl_compiler_hybrid_codegen_profile_compiles_import_builtin_and_meta_controls() -> None:
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="hybrid_codegen_validation",
    )
    configuration.set_codegen_configuration(
        configuration.codegen_configuration.from_profile(
            FrameACLCodegenProfile.create_hybrid()
        )
    )
    configuration.finalize()

    compiled_surface = _build_compiler().compile_frame_access_surface(
        _build_frame_descriptor(),
        configuration,
    )

    assert compiled_surface.codegen_imports_enabled is True
    assert "json" in compiled_surface.allowed_import_module_roots
    assert "subprocess" in compiled_surface.denied_import_module_roots
    assert "eval" in compiled_surface.denied_builtin_names
    assert compiled_surface.codegen_unsafe_reflection_allowed is False
    assert compiled_surface.codegen_dunder_access_allowed is False


def test_frame_acl_compiler_permissive_codegen_profile_compiles_broad_runtime_controls() -> None:
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="permissive_codegen_validation",
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

    assert compiled_surface.codegen_imports_enabled is True
    assert "socket" in compiled_surface.allowed_import_module_roots
    assert "subprocess" in compiled_surface.allowed_import_module_roots
    assert "eval" not in compiled_surface.denied_builtin_names
    assert compiled_surface.codegen_unsafe_reflection_allowed is True
    assert compiled_surface.codegen_dunder_access_allowed is True
    assert "mutation" in compiled_surface.allowed_commands
    assert "unsafe_reflection" in compiled_surface.allowed_commands
    assert "dunder_access" in compiled_surface.allowed_commands


def test_frame_acl_compiler_precision_codegen_profile_narrows_imports_relative_to_hybrid() -> None:
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="precision_codegen_validation",
    )
    configuration.set_codegen_configuration(
        configuration.codegen_configuration.from_profile(
            FrameACLCodegenProfile.create_hybrid(),
            precision_profile=FrameACLCodegenProfile.create_precision(),
        )
    )
    configuration.finalize()

    compiled_surface = _build_compiler().compile_frame_access_surface(
        _build_frame_descriptor(),
        configuration,
    )

    assert compiled_surface.codegen_imports_enabled is True
    assert "json" in compiled_surface.allowed_import_module_roots
    assert "inspect" not in compiled_surface.allowed_import_module_roots
    assert "subprocess" in compiled_surface.denied_import_module_roots


def test_frame_acl_compiler_permissive_codegen_profile_allows_recursive_codegen() -> None:
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="permissive_recursive_codegen",
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

    assert compiled_surface.codegen_recursive_codegen_allowed is True


def test_frame_acl_compiler_safe_codegen_profile_denies_recursive_codegen() -> None:
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="safe_recursive_codegen",
    )
    configuration.set_codegen_configuration(
        configuration.codegen_configuration.from_profile(
            FrameACLCodegenProfile.create_safe()
        )
    )
    configuration.finalize()

    compiled_surface = _build_compiler().compile_frame_access_surface(
        _build_frame_descriptor(),
        configuration,
    )

    assert compiled_surface.codegen_recursive_codegen_allowed is False


def test_frame_acl_compiler_full_access_codegen_profile_leaves_import_roots_open() -> None:
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="full_access_codegen_validation",
    )
    configuration.set_codegen_configuration(
        configuration.codegen_configuration.from_profile(
            FrameACLCodegenProfile.create_full_access()
        )
    )
    configuration.finalize()

    compiled_surface = _build_compiler().compile_frame_access_surface(
        _build_frame_descriptor(),
        configuration,
    )

    assert compiled_surface.codegen_imports_enabled is True
    assert compiled_surface.allowed_import_module_roots == tuple()
    assert compiled_surface.denied_import_module_roots == tuple()
    assert compiled_surface.denied_builtin_names == tuple()
    assert compiled_surface.codegen_unsafe_reflection_allowed is True
    assert compiled_surface.codegen_dunder_access_allowed is True
    assert compiled_surface.codegen_recursive_codegen_allowed is True


def test_frame_acl_validator_rejects_codegen_import_rule_without_module_roots() -> None:
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="invalid_codegen_import_rule",
    )
    configuration.set_codegen_configuration(
        configuration.codegen_configuration.from_profile(
            FrameACLCodegenProfile.create_hybrid(),
            capability_override_ruleset=FrameACLRuleSet(
                "capability_override",
                rules=[
                    FrameACLRule(
                        rule_name="invalid_import_rule",
                        operation="import_modules",
                        effect="allow",
                    )
                ],
            ),
        )
    )

    validator = FrameACLValidator("ops", FrameACLProfileBuilder())

    with pytest.raises(ValueError, match="module_roots"):
        validator._validate_codegen_configuration_shape_only(
            configuration.codegen_configuration
        )


def test_frame_acl_validator_rejects_codegen_builtin_rule_without_builtin_names() -> None:
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="invalid_codegen_builtin_rule",
    )
    configuration.set_codegen_configuration(
        configuration.codegen_configuration.from_profile(
            FrameACLCodegenProfile.create_hybrid(),
            capability_override_ruleset=FrameACLRuleSet(
                "capability_override",
                rules=[
                    FrameACLRule(
                        rule_name="invalid_builtin_rule",
                        operation="builtin_names",
                        effect="deny",
                    )
                ],
            ),
        )
    )

    validator = FrameACLValidator("ops", FrameACLProfileBuilder())

    with pytest.raises(ValueError, match="builtin_names"):
        validator._validate_codegen_configuration_shape_only(
            configuration.codegen_configuration
        )
