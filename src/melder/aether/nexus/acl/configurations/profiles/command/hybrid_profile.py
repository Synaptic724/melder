from melder.aether.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)


def create_hybrid_command_profile() -> FrameACLCommandProfile:
    """
    Build the reusable `hybrid` command profile.

    Returns:
        FrameACLCommandProfile: Reusable `hybrid` command profile.
    """
    return FrameACLCommandProfile(
        "hybrid",
        validation_strategy_name="generic",
        frame_ruleset=FrameACLCommandProfile.build_ruleset(
            "hybrid_frame_command",
            [
                FrameACLCommandProfile.build_rule("frame_enable", "enable", "allow"),
            ],
        ),
        conduit_ruleset=FrameACLCommandProfile.build_ruleset(
            "hybrid_conduit_command",
            [
                FrameACLCommandProfile.build_rule("conduit_enable", "enable", "allow"),
            ],
        ),
        spell_ruleset=FrameACLCommandProfile.build_ruleset(
            "hybrid_spell_command",
            [
                FrameACLCommandProfile.build_rule("spell_enable", "enable", "allow"),
            ],
        ),
        member_ruleset=FrameACLCommandProfile.build_ruleset(
            "hybrid_member_command",
            [
                FrameACLCommandProfile.build_rule("member_read_attribute", "read_attribute", "allow"),
                FrameACLCommandProfile.build_rule("member_invoke_method", "invoke_method", "allow"),
                FrameACLCommandProfile.build_rule("member_write_attribute", "write_attribute", "deny"),
                FrameACLCommandProfile.build_rule("member_dunder_access", "dunder_access", "deny"),
            ],
        ),
    )
