import pytest

from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_validator import FrameACLValidator


def test_frame_acl_validator_accepts_matching_configuration() -> None:
    """
    Verify validator accepts a configuration targeting the same frame.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_default("ops")

    assert validator.validate_configuration(configuration) is True
    assert validator.last_validated_configuration_id == configuration.configuration_id


def test_frame_acl_validator_rejects_invalid_inputs() -> None:
    """
    Verify validator rejects non-config inputs and wrong-frame configs.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    finance_configuration = FrameACLConfiguration.create_default("finance")

    with pytest.raises(TypeError, match="configuration must be a FrameACLConfiguration"):
        validator.validate_configuration(None)

    with pytest.raises(ValueError, match="targets frame 'finance', expected 'ops'"):
        validator.validate_configuration(finance_configuration)


def test_frame_acl_validator_init_rejects_empty_frame_name() -> None:
    """
    Verify validator requires a non-empty frame name.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        FrameACLValidator("")


def test_frame_acl_validator_cleanup_clears_state() -> None:
    """
    Verify cleanup nulls validator state.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_default("ops")
    validator.validate_configuration(configuration)

    validator.cleanup()

    assert validator.cleaned is True
    assert validator._frame_name is None
    assert validator._last_validated_configuration_id is None
