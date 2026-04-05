import pytest

from melder.aether.nexus.acl.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_configuration_chain import FrameACLConfigurationChain
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer
from melder.aether.nexus.acl.frame_acl_validator import FrameACLValidator


def test_frame_acl_container_builds_defaults() -> None:
    """
    Verify the container creates default config, validator, and builder.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")

    assert container.frame_name == "ops"
    assert isinstance(container.frame_acl_builder, FrameACLBuilder)
    assert isinstance(container.frame_acl_configuration, FrameACLConfiguration)
    assert isinstance(container.frame_acl_configuration_chain, FrameACLConfigurationChain)
    assert isinstance(container.frame_acl_validator, FrameACLValidator)
    assert container.frame_acl_history == []


def test_frame_acl_container_rejects_invalid_init_inputs() -> None:
    """
    Verify container requires a frame name and valid history limit.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        FrameACLContainer("")

    with pytest.raises(ValueError, match="history_limit must be an integer >= 1"):
        FrameACLContainer("ops", history_limit=0)


def test_frame_acl_container_install_configuration_appends_history() -> None:
    """
    Verify installing a new configuration retains the previous one in history.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    previous_configuration = container.frame_acl_configuration
    next_configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string='{"frame_name":"ops","frame_acl":{"visible":true},"conduit_acls":[],"spellbook_acls":[],"spell_acls":[]}',
        source_configuration_id=None,
        previous_configuration_id=previous_configuration.configuration_id,
        reason="install",
        locked=True,
    )

    container.install_configuration(next_configuration)

    assert container.frame_acl_configuration is next_configuration
    assert next_configuration.previous_configuration_id == previous_configuration.configuration_id
    assert container.frame_acl_history == [previous_configuration]
    assert container.frame_acl_validator.last_validated_configuration_id == next_configuration.configuration_id


def test_frame_acl_container_history_is_capped_and_drops_oldest() -> None:
    """
    Verify history trimming drops and cleans the oldest configuration.

    Returns:
        None.
    """
    container = FrameACLContainer("ops", history_limit=2)
    first_configuration = container.frame_acl_configuration

    second_configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string='{"frame_name":"ops","view_acl":{"v":1},"codegen_acl":{}}',
        source_configuration_id=None,
        previous_configuration_id=first_configuration.configuration_id,
        reason="second",
        locked=True,
    )
    third_configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string='{"frame_name":"ops","view_acl":{"v":2},"codegen_acl":{}}',
        source_configuration_id=None,
        previous_configuration_id=second_configuration.configuration_id,
        reason="third",
        locked=True,
    )
    fourth_configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string='{"frame_name":"ops","view_acl":{"v":3},"codegen_acl":{}}',
        source_configuration_id=None,
        previous_configuration_id=third_configuration.configuration_id,
        reason="fourth",
        locked=True,
    )

    container.install_configuration(second_configuration)
    container.install_configuration(third_configuration)
    container.install_configuration(fourth_configuration)

    assert first_configuration.cleaned is True
    assert len(container.frame_acl_history) == 1
    assert container.frame_acl_history == [third_configuration]


def test_frame_acl_container_install_rejects_wrong_frame_configuration() -> None:
    """
    Verify container install fails when configuration targets another frame.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    wrong_configuration = FrameACLConfiguration.create_default("finance")

    with pytest.raises(ValueError, match="targets frame 'finance', expected 'ops'"):
        container.install_configuration(wrong_configuration)


def test_frame_acl_container_select_and_rollback_delegate_to_chain() -> None:
    """
    Verify container selection helpers delegate to the underlying chain.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    original = container.frame_acl_configuration
    next_configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string='{"frame_name":"ops","view_acl":{"visible":true},"codegen_acl":{}}',
        source_configuration_id=None,
        previous_configuration_id=original.configuration_id,
        reason="next",
        locked=True,
    )
    container.install_configuration(next_configuration)

    selected = container.select_current_configuration(original.configuration_id)
    rolled_back = container.rollback_to_configuration(next_configuration.configuration_id)

    assert selected is original
    assert rolled_back is next_configuration


def test_frame_acl_container_cleanup_cleans_all_owned_acl_objects() -> None:
    """
    Verify cleanup cascades through builder, validator, current config, and
    history.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    previous_configuration = container.frame_acl_configuration
    next_configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name="ops",
        json_configuration_string='{"frame_name":"ops","view_acl":{"visible":true},"codegen_acl":{}}',
        source_configuration_id=None,
        previous_configuration_id=previous_configuration.configuration_id,
        reason="cleanup",
        locked=True,
    )
    container.install_configuration(next_configuration)
    builder = container.frame_acl_builder
    validator = container.frame_acl_validator
    chain = container.frame_acl_configuration_chain

    container.cleanup()

    assert builder.cleaned is True
    assert validator.cleaned is True
    assert previous_configuration.cleaned is True
    assert next_configuration.cleaned is True
    assert chain.cleaned is True
    assert container._lock is None
    assert container._frame_acl_builder is None
    assert container._frame_acl_validator is None
