from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.interfaces.interfaces import IFrameACLViewProfileStrategy


class SafeViewProfileStrategy(IFrameACLViewProfileStrategy):
    """
    Build the reusable `safe` view profile.

    Contract:
        This is the most restrictive of the standard view profiles. It keeps
        the main frame/conduit/spell surfaces visible while denying policy,
        peer-link, class-profile, callable-profile, instance-member, and other
        dynamic/introspection-heavy surfaces.
    """

    __melder_internal__ = _mrg.sentinel
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
