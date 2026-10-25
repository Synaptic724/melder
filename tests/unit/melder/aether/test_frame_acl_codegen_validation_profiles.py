from types import SimpleNamespace
from typing import Callable, Optional

import pytest

from melder.nexus.acl.frame_acl_compiler import FrameACLCompiler
from melder.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.nexus.acl.configurations.profiles.builder.frame_acl_profile_builder import (
    FrameACLProfileBuilder,
)
from melder.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.nexus.acl.configurations.profiles.rules.frame_acl_rule import (
    FrameACLRule,
)
from melder.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import (
    FrameACLRuleSet,
)
from melder.nexus.acl.validator.frame_acl_validator import FrameACLValidator
from melder.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.nexus.frame_descriptor.frame_record import FrameRecord
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


@pytest.mark.parametrize(
    ("profile_factory", "precision_profile_factory", "open_denied"),
    [
        pytest.param(FrameACLCodegenProfile.create_safe, None, True, id="safe"),
        pytest.param(FrameACLCodegenProfile.create_default, None, True, id="default"),
        pytest.param(FrameACLCodegenProfile.create_hybrid, None, True, id="hybrid"),
        pytest.param(
            FrameACLCodegenProfile.create_hybrid,
            FrameACLCodegenProfile.create_precision,
            True,
            id="hybrid+precision",
        ),
        pytest.param(
            FrameACLCodegenProfile.create_permissive,
            FrameACLCodegenProfile.create_precision,
            True,
            id="permissive+precision",
        ),
        pytest.param(FrameACLCodegenProfile.create_permissive, None, False, id="permissive"),
        pytest.param(FrameACLCodegenProfile.create_full_access, None, False, id="full_access"),
    ],
)
def test_frame_acl_compiler_denies_open_exactly_where_the_safe_tuple_applies(
        profile_factory: Callable[[], FrameACLCodegenProfile],
        precision_profile_factory: Optional[Callable[[], FrameACLCodegenProfile]],
        open_denied: bool,
) -> None:
    """
    Contract (D-10): the compiled deny list carries `open` for safe (the default profile), hybrid and any chain
    with the precision overlay - the postures whose rules use the safe tuple - and not for permissive or
    full_access, which keep `open` as a documented file posture.
    """
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="open_builtin_posture",
    )
    configuration.set_codegen_configuration(
        configuration.codegen_configuration.from_profile(
            profile_factory(),
            precision_profile=(
                precision_profile_factory() if precision_profile_factory is not None else None
            ),
        )
    )
    configuration.finalize()

    compiled_surface = _build_compiler().compile_frame_access_surface(
        _build_frame_descriptor(),
        configuration,
    )

    assert ("open" in compiled_surface.denied_builtin_names) is open_denied


@pytest.mark.parametrize(
    ("profile_factory", "precision_profile_factory", "pathlib_allowed"),
    [
        pytest.param(FrameACLCodegenProfile.create_safe, None, False, id="safe"),
        pytest.param(FrameACLCodegenProfile.create_hybrid, None, False, id="hybrid"),
        pytest.param(
            FrameACLCodegenProfile.create_hybrid,
            FrameACLCodegenProfile.create_precision,
            False,
            id="hybrid+precision",
        ),
        pytest.param(FrameACLCodegenProfile.create_permissive, None, True, id="permissive"),
        pytest.param(
            FrameACLCodegenProfile.create_permissive,
            FrameACLCodegenProfile.create_precision,
            False,
            id="permissive+precision",
        ),
    ],
)
def test_frame_acl_compiler_admits_pathlib_only_under_the_permissive_import_list(
        profile_factory: Callable[[], FrameACLCodegenProfile],
        precision_profile_factory: Optional[Callable[[], FrameACLCodegenProfile]],
        pathlib_allowed: bool,
) -> None:
    """
    Contract (D-10, the owner's option B): `pathlib` is an allowed import root of the permissive list only - hybrid's
    list leaves it out, the precision overlay narrows any chain to a list without it, and safe allows no import - so
    room code outside permissive and full_access cannot write files through `pathlib.Path`.
    """
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="pathlib_import_posture",
    )
    configuration.set_codegen_configuration(
        configuration.codegen_configuration.from_profile(
            profile_factory(),
            precision_profile=(
                precision_profile_factory() if precision_profile_factory is not None else None
            ),
        )
    )
    configuration.finalize()

    compiled_surface = _build_compiler().compile_frame_access_surface(
        _build_frame_descriptor(),
        configuration,
    )

    assert ("pathlib" in compiled_surface.allowed_import_module_roots) is pathlib_allowed
