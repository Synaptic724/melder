import json

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_compiler import FrameACLCompiler
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests._nexus_viewer_matrix_support import build_projection_backed_viewer_from_state
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_singletons_for_frame_acl_compiler_integration() -> None:
    """
    Reset singleton state around each ACL compiler integration test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_rift_publishable_configuration(
        *,
        aetheric_frame: str,
) -> Configuration:
    """
    Build one Spellbook configuration that publishes Nexus passive state.

    Args:
        aetheric_frame:
            Target frame name.

    Returns:
        Configuration:
            Spellbook configuration suitable for passive Nexus publication.
    """
    configuration = Configuration(aether_frame=aetheric_frame)
    configuration.automatic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property("rift_enabled", True)
    return configuration


def _build_typed_json_payload(
        frame_name: str,
        *,
        view_profile_name: str,
        codegen_profile_name: str,
        marker: str,
) -> str:
    """
    Build one typed ACL JSON payload for runtime integration tests.

    Args:
        frame_name:
            Frame name stored in the JSON payload.
        view_profile_name:
            Reusable view profile name for the payload.
        codegen_profile_name:
            Reusable codegen profile name for the payload.
        marker:
            Small marker used to vary the override ruleset name.

    Returns:
        str:
            JSON payload string that matches the live typed ACL contract.
    """
    return json.dumps(
        {
            "frame_name": frame_name,
            "view_configuration": {
                "profile_name": view_profile_name,
                "profile_version": "0.0.1",
                "precision_profile_name": "precision",
                "precision_profile_version": "0.0.1",
                "minimum_spell_payload_type": "detailed",
                "frame_override_ruleset": {
                    "name": "frame_override_{0}".format(marker),
                    "rules": [],
                },
                "conduit_override_ruleset": {
                    "name": "conduit_override",
                    "rules": [],
                },
                "spell_override_ruleset": {
                    "name": "spell_override",
                    "rules": [],
                },
                "member_override_ruleset": {
                    "name": "member_override",
                    "rules": [],
                },
            },
            "codegen_configuration": {
                "profile_name": codegen_profile_name,
                "profile_version": "0.0.1",
                "frame_override_ruleset": {
                    "name": "frame_override",
                    "rules": [],
                },
                "conduit_override_ruleset": {
                    "name": "conduit_override",
                    "rules": [],
                },
                "spell_override_ruleset": {
                    "name": "spell_override",
                    "rules": [],
                },
                "capability_override_ruleset": {
                    "name": "capability_override",
                    "rules": [],
                },
            },
        },
        sort_keys=True,
    )


def test_integration_passive_publish_compiles_default_safe_surface() -> None:
    """
    Verify passive runtime publication compiles into the default safe surface.

    Returns:
        None.
    """
    configuration = _make_rift_publishable_configuration(aetheric_frame="ops")
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        nexus = Nexus()
        compiler = FrameACLCompiler(nexus._frame_acl_manager.frame_acl_profile_builder)
        compiled_surface = compiler.compile_frame_access_surface(
            nexus._get_or_create_frame_descriptor("ops"),
            nexus.get_current_frame_acl_configuration("ops"),
        )

        assert compiled_surface.view_profile_name == "safe"
        assert compiled_surface.codegen_profile_name == "safe"
        assert "frame" in compiled_surface.allowed_kinds
        assert "spell" in compiled_surface.allowed_kinds
    finally:
        conduit.cleanup()


def test_integration_runtime_acl_commit_changes_compiled_command_surface() -> None:
    """
    Verify runtime ACL commits flow through the compiler and change commands.

    Returns:
        None.
    """
    configuration = _make_rift_publishable_configuration(aetheric_frame="ops")
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        nexus = Nexus()
        bundle = FrameACLConfiguration.from_json_configuration_string(
            frame_name="ops",
            json_configuration_string=_build_typed_json_payload(
                "ops",
                view_profile_name="hybrid",
                codegen_profile_name="permissive",
                marker="integration_permissive",
            ),
            source_configuration_id=None,
            previous_configuration_id=None,
            reason="integration-permissive",
            locked=True,
        )
        nexus.insert_head_frame_acl_configuration(
            "ops",
            bundle,
            select_as_current=True,
        )

        compiler = FrameACLCompiler(nexus._frame_acl_manager.frame_acl_profile_builder)
        compiled_surface = compiler.compile_frame_access_surface(
            nexus._get_or_create_frame_descriptor("ops"),
            nexus.get_current_frame_acl_configuration("ops"),
        )

        assert compiled_surface.view_profile_name == "hybrid"
        assert compiled_surface.codegen_profile_name == "permissive"
        assert "write_attribute" in compiled_surface.allowed_commands
        assert "spell" in compiled_surface.allowed_kinds
    finally:
        conduit.cleanup()


def test_integration_runtime_compiled_surface_projects_directly_into_frame_viewer() -> None:
    """
    Verify runtime compiled ACL output projects directly into a descriptor-driven viewer.

    Returns:
        None.
    """
    configuration = _make_rift_publishable_configuration(aetheric_frame="ops")
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        nexus = Nexus()
        compiler = FrameACLCompiler(nexus._frame_acl_manager.frame_acl_profile_builder)
        descriptor = nexus._get_or_create_frame_descriptor("ops")
        compiled_surface = compiler.compile_frame_access_surface(
            descriptor,
            nexus.get_current_frame_acl_configuration("ops"),
        )

        viewer = build_projection_backed_viewer_from_state(
            "ops",
            descriptor,
            nexus.get_current_frame_acl_configuration("ops"),
            compiled_surface,
        )

        assert len(viewer.execute_method("list_targets")) >= 1
        assert "frame" in {
            link.source_kind
            for link in viewer.execute_method("list_targets")
        }
    finally:
        conduit.cleanup()
