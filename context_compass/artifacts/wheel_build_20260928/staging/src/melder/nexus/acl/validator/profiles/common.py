from typing import Any

from melder.nexus.frame_descriptor.frame_descriptor import FrameDescriptor


def validate_noop_profile_configuration(
        profile: Any,
        configuration: Any,
) -> None:
    """
    Perform no additional profile-specific configuration validation.

    Args:
        profile:
            Resolved reusable profile object.
        configuration:
            Applied ACL configuration object using that profile.

    Returns:
        None.
    """
    _ = profile
    _ = configuration


def validate_noop_profile_descriptor(
        profile: Any,
        configuration: Any,
        frame_descriptor: FrameDescriptor,
) -> None:
    """
    Perform no additional profile-specific descriptor validation.

    Args:
        profile:
            Resolved reusable profile object.
        configuration:
            Applied ACL configuration object using that profile.
        frame_descriptor:
            Descriptor truth for the owning frame.

    Returns:
        None.
    """
    _ = profile
    _ = configuration
    _ = frame_descriptor
