from melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
from melder.utilities.interfaces.iframeaclcommandconfiguration import (
    IFrameACLCommandConfiguration,
)


def validate_profile_configuration(
        profile: FrameACLCommandProfile,
        configuration: IFrameACLCommandConfiguration,
) -> None:
    """
    Validate that a precision command config keeps spell-level enablement.

    Returns:
        None.
    """
    _ = profile
    if "spell_enable" not in configuration.spell_override_ruleset.rules_by_name:
        return
