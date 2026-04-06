from melder.aether.nexus.acl.profiles.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_view_profile import (
    FrameACLViewProfile,
)


def create_permissive_view_profile() -> FrameACLViewProfile:
    """
    Build the reusable `permissive` view profile.

    Returns:
        FrameACLViewProfile: Reusable `permissive` view profile.
    """
    return FrameACLViewProfile(
        "permissive",
        minimum_spell_payload_profile_name="detailed",
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


def create_permissive_codegen_profile() -> FrameACLCodegenProfile:
    """
    Build the reusable `permissive` codegen profile.

    Returns:
        FrameACLCodegenProfile: Reusable `permissive` codegen profile.
    """
    return FrameACLCodegenProfile(
        "permissive",
        frame_ruleset=FrameACLViewProfile.build_ruleset(
            "permissive_frame_codegen",
            [
                FrameACLViewProfile.build_rule("frame_query", "query", "allow"),
            ],
        ),
        conduit_ruleset=FrameACLViewProfile.build_ruleset(
            "permissive_conduit_codegen",
            [
                FrameACLViewProfile.build_rule("conduit_query", "query", "allow"),
                FrameACLViewProfile.build_rule("conduit_link", "link", "allow"),
                FrameACLViewProfile.build_rule("conduit_unlink", "unlink", "allow"),
                FrameACLViewProfile.build_rule("conduit_create_lesser", "create_lesser_conduit", "allow"),
                FrameACLViewProfile.build_rule("conduit_transfer_ownership", "transfer_ownership", "allow"),
            ],
        ),
        spell_ruleset=FrameACLViewProfile.build_ruleset(
            "permissive_spell_codegen",
            [
                FrameACLViewProfile.build_rule("spell_resolve_existing", "resolve_existing", "allow"),
                FrameACLViewProfile.build_rule("spell_bind_existing", "bind_existing", "allow"),
                FrameACLViewProfile.build_rule("spell_local_create", "local_create", "allow"),
                FrameACLViewProfile.build_rule("spell_invoke_method", "invoke_method", "allow"),
                FrameACLViewProfile.build_rule("spell_read_attribute", "read_attribute", "allow"),
                FrameACLViewProfile.build_rule("spell_write_attribute", "write_attribute", "allow"),
            ],
        ),
        capability_ruleset=FrameACLViewProfile.build_ruleset(
            "permissive_capability_codegen",
            [
                FrameACLViewProfile.build_rule("capability_dynamic_access", "dynamic_access", "allow"),
                FrameACLViewProfile.build_rule("capability_contract_override", "contract_override", "allow"),
                FrameACLViewProfile.build_rule("capability_mutation", "mutation", "deny"),
                FrameACLViewProfile.build_rule("capability_unsafe_reflection", "unsafe_reflection", "deny"),
                FrameACLViewProfile.build_rule("capability_dunder_access", "dunder_access", "deny"),
            ],
        ),
    )

