import json

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.nexus.nexus import Nexus


@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each ACL placeholder unit test.

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


def _build_typed_json_payload(
        frame_name: str,
        *,
        view_profile_name: str = "safe",
        codegen_profile_name: str = "safe",
) -> str:
    """
    Build one minimal typed ACL JSON payload for subsystem tests.

    Args:
        frame_name:
            Frame name stored in the JSON payload.
        view_profile_name:
            Reusable view profile name for the payload.
        codegen_profile_name:
            Reusable codegen profile name for the payload.

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
                "minimum_spell_payload_type": "general",
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


def test_descriptor_creation_also_creates_frame_acl_container_with_defaults() -> None:
    """
    Verify descriptor creation also provisions the matching frame ACL container.

    Returns:
        None.
    """
    aether = Aether()
    nexus = Nexus()

    descriptor = nexus._get_or_create_frame_descriptor("ops")
    container = nexus._frame_acl_manager._get_required_frame_acl_container("ops")

    assert descriptor.frame_name == "ops"
    assert container.frame_name == "ops"
    assert container.frame_acl_configuration.frame_name == "ops"
    assert container.frame_acl_builder is not None
    assert container.frame_acl_validator.frame_name == "ops"


def test_frame_acl_manager_returns_same_container_and_builder_for_same_frame() -> None:
    """
    Verify one frame keeps one container and one builder object.

    Returns:
        None.
    """
    Aether()
    nexus = Nexus()

    first_descriptor = nexus._get_or_create_frame_descriptor("ops")
    second_descriptor = nexus._get_or_create_frame_descriptor("ops")
    first_container = nexus._frame_acl_manager._get_required_frame_acl_container("ops")
    second_container = nexus._frame_acl_manager._ensure_frame_acl_container("ops")
    first_builder = first_container.frame_acl_builder
    second_builder = nexus._frame_acl_manager._get_or_create_frame_acl_builder("ops")

    assert second_descriptor is first_descriptor
    assert second_container is first_container
    assert second_builder is first_builder


def test_frame_acl_manager_keeps_containers_separate_by_frame_name() -> None:
    """
    Verify different frames get distinct ACL containers and builders.

    Returns:
        None.
    """
    Aether()
    nexus = Nexus()

    nexus._get_or_create_frame_descriptor("ops")
    nexus._get_or_create_frame_descriptor("finance")

    ops_container = nexus._frame_acl_manager._get_required_frame_acl_container("ops")
    finance_container = nexus._frame_acl_manager._get_required_frame_acl_container("finance")

    assert finance_container is not ops_container
    assert finance_container.frame_acl_builder is not ops_container.frame_acl_builder


def test_frame_acl_builder_commit_updates_current_configuration_and_history() -> None:
    """
    Verify builder commit installs a new configuration and retains history.

    Returns:
        None.
    """
    Aether()
    nexus = Nexus()
    nexus._get_or_create_frame_descriptor("ops")
    container = nexus._frame_acl_manager._get_required_frame_acl_container("ops")
    previous_configuration = container.get_current_view_configuration()
    builder = container.frame_acl_builder

    builder.begin_change("view")
    builder.load_json_configuration_string(
        json.dumps(json.loads(_build_typed_json_payload("ops"))["view_configuration"])
    )
    next_configuration = builder.commit_change()

    assert container.get_current_view_configuration() is next_configuration
    assert next_configuration.previous_configuration_id == previous_configuration.configuration_id
    assert container.frame_acl_configuration.view_configuration.profile_name == next_configuration.profile_name


def test_frame_acl_builder_rejects_parallel_change_sessions_and_can_discard() -> None:
    """
    Verify the per-frame builder enforces one open change session at a time.

    Returns:
        None.
    """
    Aether()
    nexus = Nexus()
    nexus._get_or_create_frame_descriptor("ops")
    builder = nexus._frame_acl_manager._get_or_create_frame_acl_builder("ops")

    builder.begin_change("view")

    with pytest.raises(RuntimeError, match="already has an active change"):
        builder.begin_change("view")

    builder.discard_change()

    assert builder.change_active is False


def test_frame_acl_manager_remove_container_cleans_it_and_reports_status() -> None:
    """
    Verify manager removal cleans the container and reports whether it existed.

    Returns:
        None.
    """
    Aether()
    nexus = Nexus()
    nexus._get_or_create_frame_descriptor("ops")
    container = nexus._frame_acl_manager._get_required_frame_acl_container("ops")

    assert nexus._frame_acl_manager._remove_frame_acl_container("ops") is True
    assert container.cleaned is True
    assert nexus._frame_acl_manager._remove_frame_acl_container("ops") is False


def test_frame_detach_also_removes_matching_acl_container() -> None:
    """
    Verify the Nexus frame-detach façade also removes the matching ACL
    container.

    Returns:
        None.
    """
    aether = Aether()
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    nexus.enable(configuration)

    nexus._get_or_create_frame_descriptor("ops")
    container = nexus._frame_acl_manager._get_required_frame_acl_container("ops")

    assert "ops" in nexus._frame_acl_manager.frame_acl_containers_by_name

    nexus.check_for_aetheric_frame("ops")

    assert container.cleaned is True
    assert "ops" not in nexus._frame_acl_manager.frame_acl_containers_by_name

