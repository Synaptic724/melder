from melder.aether.nexus.acl.profiles.frame_acl_view_profile import (
    FrameACLViewProfile,
)


def create_permissive_view_profile() -> FrameACLViewProfile:
    """
    Build the reusable `permissive` view profile.

    Contract:
        This is the most open of the standard view profiles. It keeps the main
        frame/conduit/spell surfaces visible and also allows instance-member
        and dynamic-access visibility that the stricter profiles deny.

    Returns:
        FrameACLViewProfile: Reusable `permissive` view profile.
    """
    return FrameACLViewProfile(
        "permissive",
        minimum_spell_payload_profile_name="general",
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
