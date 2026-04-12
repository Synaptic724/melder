from melder.aether.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)


def create_permissive_command_profile() -> FrameACLCommandProfile:
    """
    Build the reusable `permissive` command profile.

    Returns:
        FrameACLCommandProfile: Reusable `permissive` command profile.
    """
    return FrameACLCommandProfile(
        "permissive",
        validation_strategy_name="generic",
        frame_ruleset=FrameACLCommandProfile.build_ruleset(
            "permissive_frame_command",
            [
                FrameACLCommandProfile.build_rule("frame_enable", "enable", "allow"),
            ],
        ),
        conduit_ruleset=FrameACLCommandProfile.build_ruleset(
            "permissive_conduit_command",
            [
                FrameACLCommandProfile.build_rule("conduit_enable", "enable", "allow"),
            ],
        ),
        spell_ruleset=FrameACLCommandProfile.build_ruleset(
            "permissive_spell_command",
            [
                FrameACLCommandProfile.build_rule("spell_enable", "enable", "allow"),
            ],
        ),
        member_ruleset=FrameACLCommandProfile.build_ruleset(
            "permissive_member_command",
            [
                FrameACLCommandProfile.build_rule("member_read_attribute", "read_attribute", "allow"),
                FrameACLCommandProfile.build_rule("member_invoke_method", "invoke_method", "allow"),
                FrameACLCommandProfile.build_rule("member_write_attribute", "write_attribute", "allow"),
                FrameACLCommandProfile.build_rule("member_dunder_access", "dunder_access", "deny"),
            ],
        ),
    )
