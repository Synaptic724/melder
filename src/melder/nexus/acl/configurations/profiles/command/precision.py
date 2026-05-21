from melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class PrecisionCommandProfileStrategy:
    """
    Build the reusable `precision` command profile.
    """

    __melder_internal__ = _mrg.sentinel
    _NAME = "precision"

    @property
    def name(self) -> str:
        """
        Return the stable command-profile strategy name.
        """
        return self._NAME

    def build(self) -> FrameACLCommandProfile:
        """
        Build and return one configured `precision` command profile.
        """
        return FrameACLCommandProfile(
            self._NAME,
            validation_strategy_name="precision",
            frame_ruleset=FrameACLCommandProfile.build_ruleset(
                "precision_frame_command",
                [
                    FrameACLCommandProfile.build_rule("frame_enable", "enable", "allow"),
                ],
            ),
            conduit_ruleset=FrameACLCommandProfile.build_ruleset(
                "precision_conduit_command",
                [
                    FrameACLCommandProfile.build_rule("conduit_enable", "enable", "allow"),
                ],
            ),
            spell_ruleset=FrameACLCommandProfile.build_ruleset(
                "precision_spell_command",
                [
                    FrameACLCommandProfile.build_rule("spell_enable", "enable", "allow"),
                ],
            ),
            member_ruleset=FrameACLCommandProfile.build_ruleset(
                "precision_member_command",
                [
                    FrameACLCommandProfile.build_rule("member_read_attribute", "read_attribute", "allow"),
                    FrameACLCommandProfile.build_rule("member_invoke_method", "invoke_method", "allow"),
                    FrameACLCommandProfile.build_rule("member_write_attribute", "write_attribute", "deny"),
                    FrameACLCommandProfile.build_rule("member_dunder_access", "dunder_access", "deny"),
                ],
            ),
        )
