from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
class PermissiveViewProfileStrategy:
    """
    Build the reusable `permissive` view profile.

    Contract:
        This is the most open of the standard view profiles. It keeps the main
        frame/conduit/spell surfaces visible and also allows instance-member
        and dynamic-access visibility that the stricter profiles deny.

    Threading:
        Stateless preset construction; holds no state between builds.

    Registration:
        MELDER KERNEL - guarded. Registered as a preset strategy in the view
        profile builder and selected by name.

    Subsystem Context:
        One rung of the view-family posture ladder. The standard ladder runs
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
        "access: internal. Build the reusable `permissive` view profile. Melder kernel machinery: "
        "read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    _NAME = "permissive"

    @property
    def name(self) -> str:
        return self._NAME

    def build(self) -> FrameACLViewProfile:
        """
        Return one configured `permissive` view profile instance.

        Returns:
            FrameACLViewProfile: Reusable `permissive` view profile.
        """
        return FrameACLViewProfile(
            "permissive",
            minimum_spell_payload_type="general",
            validation_strategy_name="generic",
            frame_ruleset=FrameACLViewProfile.build_ruleset(
                "permissive_frame",
                [
                    FrameACLViewProfile.build_rule("frame_visible", "visible", "allow"),
                    FrameACLViewProfile.build_rule("frame_show_payload", "show_payload", "allow"),
                ],
            ),
            conduit_ruleset=FrameACLViewProfile.build_ruleset(
                "permissive_conduit",
                [
                    FrameACLViewProfile.build_rule("conduit_visible", "visible", "allow"),
                    FrameACLViewProfile.build_rule("conduit_show_payload", "show_payload", "allow"),
                    FrameACLViewProfile.build_rule("conduit_show_policy", "show_policy", "allow"),
                    FrameACLViewProfile.build_rule("conduit_show_peer_links", "show_peer_links", "allow"),
                ],
            ),
            spell_ruleset=FrameACLViewProfile.build_ruleset(
                "permissive_spell",
                [
                    FrameACLViewProfile.build_rule("spell_visible", "visible", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_binding_payload", "show_binding_payload", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_resolution_payload", "show_resolution_payload", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_metadata", "show_metadata", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_class_profile", "show_class_profile", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_callable_profile", "show_callable_profile", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_instance_members", "show_instance_members", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_dynamic_access", "show_dynamic_access", "allow"),
                ],
            ),
            member_ruleset=FrameACLViewProfile.build_ruleset(
                "permissive_member",
                [
                    FrameACLViewProfile.build_rule("member_hide_dunder_pattern", "show_member", "deny", {"pattern": "__*"}),
                    FrameACLViewProfile.build_rule("member_hide___dict__", "show_member", "deny", {"member_name": "__dict__"}),
                ],
            ),
        )
