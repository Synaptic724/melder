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
    assert container.frame_acl_history == []
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
    previous_configuration = container.frame_acl_configuration
    builder = container.frame_acl_builder

    builder.begin_change()
    builder.load_json_configuration_string(
        '{"frame_name": "ops", "frame_acl": {"visible": true}, "conduit_acls": [], "spellbook_acls": [], "spell_acls": []}'
    )
    next_configuration = builder.commit_change()

    assert container.frame_acl_configuration is next_configuration
    assert next_configuration.previous_configuration_id == previous_configuration.configuration_id
    assert len(container.frame_acl_history) == 1
    assert container.frame_acl_history[0] is previous_configuration
    assert container.frame_acl_validator.last_validated_configuration_id == next_configuration.configuration_id


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

    builder.begin_change()

    with pytest.raises(RuntimeError, match="already has an active change"):
        builder.begin_change()

    builder.discard_change()

    assert builder.change_active is False
