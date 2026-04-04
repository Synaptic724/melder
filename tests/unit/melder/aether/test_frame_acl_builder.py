import pytest

from melder.aether.nexus.acl.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer


def test_frame_acl_builder_begin_change_seeds_current_payload() -> None:
    """
    Verify begin_change seeds the draft from the current configuration payload.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder

    builder.begin_change()

    assert builder.change_active is True
    assert (
        builder._draft_json_configuration_string
        == container.frame_acl_configuration.normalized_json_configuration_string
    )


def test_frame_acl_builder_load_requires_active_change_and_string_payload() -> None:
    """
    Verify loading JSON requires an active change and a string payload.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder

    with pytest.raises(RuntimeError, match="has no active change"):
        builder.load_json_configuration_string("{}")

    builder.begin_change()

    with pytest.raises(TypeError, match="json_configuration_string must be a string"):
        builder.load_json_configuration_string(None)


def test_frame_acl_builder_commit_requires_active_change() -> None:
    """
    Verify commit_change rejects commits without an active change session.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder

    with pytest.raises(RuntimeError, match="has no active change"):
        builder.commit_change()


def test_frame_acl_builder_commit_installs_new_configuration() -> None:
    """
    Verify commit_change installs and returns the next configuration revision.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    previous_configuration = container.frame_acl_configuration
    builder = container.frame_acl_builder

    builder.begin_change()
    builder.load_json_configuration_string(
        '{"frame_name":"ops","frame_acl":{"visible":true},"conduit_acls":[],"spellbook_acls":[],"spell_acls":[]}'
    )
    next_configuration = builder.commit_change()

    assert isinstance(next_configuration, FrameACLConfiguration)
    assert container.frame_acl_configuration is next_configuration
    assert next_configuration.previous_configuration_id == previous_configuration.configuration_id
    assert builder.change_active is False
    assert builder._draft_json_configuration_string is None


def test_frame_acl_builder_discard_resets_session_state() -> None:
    """
    Verify discard_change clears the draft and closes the change session.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder

    builder.begin_change()
    builder.load_json_configuration_string(
        '{"frame_name":"ops","frame_acl":{"visible":false},"conduit_acls":[],"spellbook_acls":[],"spell_acls":[]}'
    )
    builder.discard_change()

    assert builder.change_active is False
    assert builder._draft_json_configuration_string is None


def test_frame_acl_builder_rejects_double_begin_change() -> None:
    """
    Verify only one open change session exists per builder.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder

    builder.begin_change()

    with pytest.raises(RuntimeError, match="already has an active change"):
        builder.begin_change()


def test_frame_acl_builder_init_rejects_missing_container() -> None:
    """
    Verify builder construction rejects a missing container.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="container cannot be None"):
        FrameACLBuilder(None)


def test_frame_acl_builder_cleanup_clears_fields() -> None:
    """
    Verify cleanup nulls builder-owned fields.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder

    builder.cleanup()

    assert builder.cleaned is True
    assert builder._lock is None
    assert builder._container is None
    assert builder._change_active is None
    assert builder._draft_json_configuration_string is None
