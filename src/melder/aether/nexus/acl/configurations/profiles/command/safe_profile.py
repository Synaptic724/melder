from melder.aether.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.interfaces.iframeaclcommandprofilestrategy import IFrameACLCommandProfileStrategy


class SafeCommandProfileStrategy(IFrameACLCommandProfileStrategy):
    """
    Build the reusable `safe` command profile.

    Contract:
        This is the most restrictive of the standard command profiles. It
        keeps the main frame/conduit/spell enablement surfaces available while
        limiting member operations to read-only access.
    """

    __melder_internal__ = _mrg.sentinel
    _NAME = "safe"

    @property
    def name(self) -> str:
        """
        Return the stable command-profile strategy name.
        """
        return self._NAME

    def build(self) -> FrameACLCommandProfile:
        """
        Build and return one configured `safe` command profile.
        """
        return FrameACLCommandProfile(
            self._NAME,
            validation_strategy_name="safe",
            frame_ruleset=FrameACLCommandProfile.build_ruleset(
                "safe_frame_command",
                [
                    FrameACLCommandProfile.build_rule("frame_enable", "enable", "allow"),
                ],
            ),
            conduit_ruleset=FrameACLCommandProfile.build_ruleset(
                "safe_conduit_command",
                [
                    FrameACLCommandProfile.build_rule("conduit_enable", "enable", "allow"),
                ],
            ),
            spell_ruleset=FrameACLCommandProfile.build_ruleset(
                "safe_spell_command",
                [
                    FrameACLCommandProfile.build_rule("spell_enable", "enable", "allow"),
                ],
            ),
            member_ruleset=FrameACLCommandProfile.build_ruleset(
                "safe_member_command",
                [
                    FrameACLCommandProfile.build_rule("member_read_attribute", "read_attribute", "allow"),
                    FrameACLCommandProfile.build_rule("member_invoke_method", "invoke_method", "deny"),
                    FrameACLCommandProfile.build_rule("member_write_attribute", "write_attribute", "deny"),
                    FrameACLCommandProfile.build_rule("member_dunder_access", "dunder_access", "deny"),
                ],
            ),
        )
