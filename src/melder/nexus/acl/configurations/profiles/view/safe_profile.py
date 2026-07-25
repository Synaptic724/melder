from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
class SafeViewProfileStrategy:
    """
    Build the reusable `safe` view profile.

    Contract:
        This is the most restrictive of the standard view profiles. It keeps
        the main frame/conduit/spell surfaces visible while denying policy,
        peer-link, class-profile, callable-profile, instance-member, and other
        dynamic/introspection-heavy surfaces.

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
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Build the reusable `safe` view profile. Melder kernel machinery: read "
        "it to understand the runtime, do not drive it directly."
    )

    _NAME = "safe"

    @property
    def name(self) -> str:
        """
        Return the stable strategy/profile name.
        """
        return self._NAME

    def build(self) -> FrameACLViewProfile:
        """
        Return one configured `safe` view profile instance.

        Returns:
            FrameACLViewProfile: Reusable `safe` view profile.
        """
        return FrameACLViewProfile(
            "safe",
            minimum_spell_payload_type="general",
            validation_strategy_name="safe",
            frame_ruleset=FrameACLViewProfile.build_ruleset(
                "safe_frame",
                [
                    FrameACLViewProfile.build_rule("frame_visible", "visible", "allow"),
                    FrameACLViewProfile.build_rule("frame_show_payload", "show_payload", "allow"),
                ],
            ),
            conduit_ruleset=FrameACLViewProfile.build_ruleset(
                "safe_conduit",
                [
                    FrameACLViewProfile.build_rule("conduit_visible", "visible", "allow"),
                    FrameACLViewProfile.build_rule("conduit_show_payload", "show_payload", "allow"),
                    FrameACLViewProfile.build_rule("conduit_hide_policy", "show_policy", "deny"),
                    FrameACLViewProfile.build_rule("conduit_hide_peer_links", "show_peer_links", "deny"),
                ],
            ),
            spell_ruleset=FrameACLViewProfile.build_ruleset(
                "safe_spell",
                [
                    FrameACLViewProfile.build_rule("spell_visible", "visible", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_binding_payload", "show_binding_payload", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_resolution_payload", "show_resolution_payload", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_metadata", "show_metadata", "allow"),
                    FrameACLViewProfile.build_rule("spell_hide_class_profile", "show_class_profile", "deny"),
                    FrameACLViewProfile.build_rule("spell_hide_callable_profile", "show_callable_profile", "deny"),
                    FrameACLViewProfile.build_rule("spell_hide_instance_members", "show_instance_members", "deny"),
                    FrameACLViewProfile.build_rule("spell_hide_dynamic_access", "show_dynamic_access", "deny"),
                ],
            ),
            member_ruleset=FrameACLViewProfile.build_ruleset(
                "safe_member",
                [
                    FrameACLViewProfile.build_rule("member_hide_dunder_pattern", "show_member", "deny", {"pattern": "__*"}),
                    FrameACLViewProfile.build_rule("member_hide___dict__", "show_member", "deny", {"member_name": "__dict__"}),
                    FrameACLViewProfile.build_rule("member_hide___class__", "show_member", "deny", {"member_name": "__class__"}),
                    FrameACLViewProfile.build_rule("member_hide___mro__", "show_member", "deny", {"member_name": "__mro__"}),
                    FrameACLViewProfile.build_rule("member_hide___bases__", "show_member", "deny", {"member_name": "__bases__"}),
                    FrameACLViewProfile.build_rule("member_hide___subclasses__", "show_member", "deny", {"member_name": "__subclasses__"}),
                    FrameACLViewProfile.build_rule("member_hide___globals__", "show_member", "deny", {"member_name": "__globals__"}),
                    FrameACLViewProfile.build_rule("member_hide___closure__", "show_member", "deny", {"member_name": "__closure__"}),
                    FrameACLViewProfile.build_rule("member_hide___code__", "show_member", "deny", {"member_name": "__code__"}),
                    FrameACLViewProfile.build_rule("member_hide___getattribute__", "show_member", "deny", {"member_name": "__getattribute__"}),
                    FrameACLViewProfile.build_rule("member_hide___setattr__", "show_member", "deny", {"member_name": "__setattr__"}),
                    FrameACLViewProfile.build_rule("member_hide___delattr__", "show_member", "deny", {"member_name": "__delattr__"}),
                    FrameACLViewProfile.build_rule("member_hide___reduce__", "show_member", "deny", {"member_name": "__reduce__"}),
                    FrameACLViewProfile.build_rule("member_hide___reduce_ex__", "show_member", "deny", {"member_name": "__reduce_ex__"}),
                ],
            ),
        )
