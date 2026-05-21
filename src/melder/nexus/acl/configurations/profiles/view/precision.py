from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class PrecisionViewProfileStrategy:
    """
    Build the reusable `precision` view profile.
    """

    __melder_internal__ = _mrg.sentinel
    _NAME = "precision"

    @property
    def name(self) -> str:
        return self._NAME

    def build(self) -> FrameACLViewProfile:
        """
        Return one configured `precision` view profile instance.

        Returns:
            FrameACLViewProfile: Reusable `precision` view profile.
        """
        return FrameACLViewProfile(
            "precision",
            minimum_spell_payload_type="detailed",
            validation_strategy_name="precision",
            frame_ruleset=FrameACLViewProfile.build_ruleset(
                "precision_frame",
                [
                    FrameACLViewProfile.build_rule("frame_visible", "visible", "allow"),
                    FrameACLViewProfile.build_rule("frame_show_payload", "show_payload", "allow"),
                ],
            ),
            conduit_ruleset=FrameACLViewProfile.build_ruleset(
                "precision_conduit",
                [
                    FrameACLViewProfile.build_rule("conduit_visible", "visible", "allow"),
                    FrameACLViewProfile.build_rule("conduit_show_payload", "show_payload", "allow"),
                    FrameACLViewProfile.build_rule("conduit_show_policy", "show_policy", "allow"),
                    FrameACLViewProfile.build_rule("conduit_show_peer_links", "show_peer_links", "allow"),
                ],
            ),
            spell_ruleset=FrameACLViewProfile.build_ruleset(
                "precision_spell",
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
                "precision_member",
                [
                    FrameACLViewProfile.build_rule("member_hide_dunder_pattern", "show_member", "deny", {"pattern": "__*"}),
                    FrameACLViewProfile.build_rule("member_hide___dict__", "show_member", "deny", {"member_name": "__dict__"}),
                ],
            ),
        )
