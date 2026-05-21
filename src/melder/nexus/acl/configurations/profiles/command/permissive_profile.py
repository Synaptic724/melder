from melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.interfaces.iframeaclcommandprofilestrategy import IFrameACLCommandProfileStrategy


class PermissiveCommandProfileStrategy(IFrameACLCommandProfileStrategy):
    """
    Build the reusable `permissive` command profile.

    Contract:
        This is the most open of the standard command profiles. It allows
        member reads, invocation, and writes while still denying dunder access.
    """

    __melder_internal__ = _mrg.sentinel
    _NAME = "permissive"

    @property
    def name(self) -> str:
        """
        Return the stable command-profile strategy name.
        """
        return self._NAME

    def build(self) -> FrameACLCommandProfile:
        """
        Build and return one configured `permissive` command profile.
        """
        return FrameACLCommandProfile(
            self._NAME,
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
