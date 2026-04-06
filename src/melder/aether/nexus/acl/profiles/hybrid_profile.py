from melder.aether.nexus.acl.profiles.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_view_profile import (
    FrameACLViewProfile,
)


def create_hybrid_view_profile() -> FrameACLViewProfile:
    """
    Build the reusable `hybrid` view profile.

    Returns:
        FrameACLViewProfile: Reusable `hybrid` view profile.
    """
    return FrameACLViewProfile(
        "hybrid",
        minimum_spell_payload_profile_name="detailed",
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


def create_hybrid_codegen_profile() -> FrameACLCodegenProfile:
    """
    Build the reusable `hybrid` codegen profile.

    Returns:
        FrameACLCodegenProfile: Reusable `hybrid` codegen profile.
    """
    return FrameACLCodegenProfile(
        "hybrid",
        frame_ruleset=FrameACLViewProfile.build_ruleset(
            "hybrid_frame_codegen",
            [
                FrameACLViewProfile.build_rule("frame_query", "query", "allow"),
            ],
        ),
        conduit_ruleset=FrameACLViewProfile.build_ruleset(
            "hybrid_conduit_codegen",
            [
                FrameACLViewProfile.build_rule("conduit_query", "query", "allow"),
                FrameACLViewProfile.build_rule("conduit_link", "link", "allow"),
                FrameACLViewProfile.build_rule("conduit_unlink", "unlink", "allow"),
                FrameACLViewProfile.build_rule("conduit_create_lesser", "create_lesser_conduit", "deny"),
                FrameACLViewProfile.build_rule("conduit_transfer_ownership", "transfer_ownership", "deny"),
            ],
        ),
        spell_ruleset=FrameACLViewProfile.build_ruleset(
            "hybrid_spell_codegen",
            [
                FrameACLViewProfile.build_rule("spell_resolve_existing", "resolve_existing", "allow"),
                FrameACLViewProfile.build_rule("spell_bind_existing", "bind_existing", "allow"),
                FrameACLViewProfile.build_rule("spell_invoke_method", "invoke_method", "allow"),
                FrameACLViewProfile.build_rule("spell_read_attribute", "read_attribute", "allow"),
                FrameACLViewProfile.build_rule("spell_local_create", "local_create", "deny"),
                FrameACLViewProfile.build_rule("spell_write_attribute", "write_attribute", "deny"),
            ],
        ),
        capability_ruleset=FrameACLViewProfile.build_ruleset(
            "hybrid_capability_codegen",
            [
                FrameACLViewProfile.build_rule("capability_dynamic_access", "dynamic_access", "deny"),
                FrameACLViewProfile.build_rule("capability_mutation", "mutation", "deny"),
                FrameACLViewProfile.build_rule("capability_contract_override", "contract_override", "deny"),
                FrameACLViewProfile.build_rule("capability_unsafe_reflection", "unsafe_reflection", "deny"),
                FrameACLViewProfile.build_rule("capability_dunder_access", "dunder_access", "deny"),
            ],
        ),
    )

