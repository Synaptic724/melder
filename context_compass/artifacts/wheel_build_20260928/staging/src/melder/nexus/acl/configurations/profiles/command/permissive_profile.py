from melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
class PermissiveCommandProfileStrategy:
    """
    Build the reusable `permissive` command profile.

    Contract:
        This is the most open of the standard command profiles. It allows
        member reads, invocation, and writes while still denying dunder access.

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

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Build the reusable `permissive` command profile. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """

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

        Contract:
            Assembles a fresh `FrameACLCommandProfile` (validation strategy
            `generic`) encoding the most open standard command posture: frame,
            conduit, and spell `enable` are allowed, and on member operations it
            allows read-attribute, invoke-method, and write-attribute - DENYING
            only dunder-access. Stateless: a new instance is returned per call.

        Returns:
            FrameACLCommandProfile: A freshly built `permissive` command profile.
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
