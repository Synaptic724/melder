from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.interfaces.iframeaclviewprofilestrategy import IFrameACLViewProfileStrategy


class HybridViewProfileStrategy(IFrameACLViewProfileStrategy):
    """
    Build the reusable `hybrid` view profile.

    Contract:
        This profile sits between the stricter `safe` posture and the fully
        open `permissive` posture. It allows the main frame/conduit/spell
        payloads and selected profile information while still denying the more
        aggressive dynamic/instance-member surfaces.

    """

    __melder_internal__ = _mrg.sentinel
    _NAME = "hybrid"

    @property
    def name(self) -> str:
        return self._NAME

    def build(self) -> FrameACLViewProfile:
        """
        Return one configured `hybrid` view profile instance.

        Returns:
            FrameACLViewProfile: Reusable `hybrid` view profile.
        """
        return FrameACLViewProfile(
            "hybrid",
            minimum_spell_payload_type="general",
            validation_strategy_name="generic",
            frame_ruleset=FrameACLViewProfile.build_ruleset(
                "hybrid_frame",
                [
                    FrameACLViewProfile.build_rule("frame_visible", "visible", "allow"),
                    FrameACLViewProfile.build_rule("frame_show_payload", "show_payload", "allow"),
                ],
            ),
            conduit_ruleset=FrameACLViewProfile.build_ruleset(
                "hybrid_conduit",
                [
                    FrameACLViewProfile.build_rule("conduit_visible", "visible", "allow"),
                    FrameACLViewProfile.build_rule("conduit_show_payload", "show_payload", "allow"),
                    FrameACLViewProfile.build_rule("conduit_show_policy", "show_policy", "allow"),
                    FrameACLViewProfile.build_rule("conduit_show_peer_links", "show_peer_links", "allow"),
                ],
            ),
            spell_ruleset=FrameACLViewProfile.build_ruleset(
                "hybrid_spell",
                [
                    FrameACLViewProfile.build_rule("spell_visible", "visible", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_binding_payload", "show_binding_payload", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_resolution_payload", "show_resolution_payload", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_metadata", "show_metadata", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_class_profile", "show_class_profile", "allow"),
                    FrameACLViewProfile.build_rule("spell_show_callable_profile", "show_callable_profile", "allow"),
                    FrameACLViewProfile.build_rule("spell_hide_instance_members", "show_instance_members", "deny"),
                    FrameACLViewProfile.build_rule("spell_hide_dynamic_access", "show_dynamic_access", "deny"),
                ],
            ),
            member_ruleset=FrameACLViewProfile.build_ruleset(
                "hybrid_member",
                [
                    FrameACLViewProfile.build_rule("member_hide_dunder_pattern", "show_member", "deny", {"pattern": "__*"}),
                    FrameACLViewProfile.build_rule("member_hide___dict__", "show_member", "deny", {"member_name": "__dict__"}),
                    FrameACLViewProfile.build_rule("member_hide___class__", "show_member", "deny", {"member_name": "__class__"}),
                ],
            ),
        )
