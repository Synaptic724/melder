from melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
class PrecisionCommandProfileStrategy:
    """
    Build the reusable `precision` command profile.

    Threading:
        Stateless preset construction; holds no state between builds.

    Registration:
        MELDER KERNEL - guarded. Registered as a preset strategy in the command
        profile builder and selected by name.

    Subsystem Context:
        One rung of the command-family posture ladder. The standard ladder runs
        `safe` -> `hybrid` -> `permissive`, with `precision` as the
        explicitly-enumerated posture.

    System Context:
        These presets exist so ACL authoring starts from a REVIEWED posture
        rather than from an empty ruleset. An operator choosing `safe` gets a
        deliberately restrictive policy someone reasoned about; building the
        same thing rule by rule invites a permissive gap nobody notices.
        The ladder is monotonic by intent - each rung allows a superset of the
        previous one's operations - so moving a frame up or down is a
        comprehensible change rather than an unrelated policy swap. `precision`
        sits outside that ordering deliberately: it is the posture for
        enumerating exactly what is permitted instead of picking a tier.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Build the reusable `precision` command profile. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

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
