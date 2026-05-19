from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.utilities.interfaces.iframeaclviewconfiguration import (
    IFrameACLViewConfiguration,
)


def validate_profile_configuration(
        profile: FrameACLViewProfile,
        configuration: IFrameACLViewConfiguration,
) -> None:
    """
    Validate that a precision view config preserves the required detailed floor.

    Returns:
        None.
    """
    _ = profile
    if configuration.minimum_spell_payload_type != "detailed":
        raise ValueError(
            "Precision view profile requires minimum_spell_payload_type='detailed'."
        )
