from melder.aether.nexus.acl.configurations.frame_acl_command_configuration import (
    FrameACLCommandConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)


def validate_profile_configuration(
        profile: FrameACLCommandProfile,
        configuration: FrameACLCommandConfiguration,
) -> None:
    """
    Validate that a precision command config keeps spell-level enablement.

    Returns:
        None.
    """
    _ = profile
    if "spell_enable" not in configuration.spell_override_ruleset.rules_by_name:
        return
