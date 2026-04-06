from melder.aether.nexus.acl.profiles.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_view_profile import (
    FrameACLViewProfile,
)


def create_safe_view_profile() -> FrameACLViewProfile:
    """
    Build the reusable `safe` view profile.

    Returns:
        FrameACLViewProfile: Reusable `safe` view profile.
    """
    return FrameACLViewProfile(
        "safe",
        minimum_spell_payload_profile_name="detailed",
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


def create_safe_codegen_profile() -> FrameACLCodegenProfile:
    """
    Build the reusable `safe` codegen profile.

    Returns:
        FrameACLCodegenProfile: Reusable `safe` codegen profile.
    """
    return FrameACLCodegenProfile(
        "safe",
        frame_ruleset=FrameACLViewProfile.build_ruleset(
            "safe_frame_codegen",
            [
                FrameACLViewProfile.build_rule("frame_query", "query", "allow"),
            ],
        ),
        conduit_ruleset=FrameACLViewProfile.build_ruleset(
            "safe_conduit_codegen",
            [
                FrameACLViewProfile.build_rule("conduit_query", "query", "allow"),
                FrameACLViewProfile.build_rule("conduit_link", "link", "deny"),
                FrameACLViewProfile.build_rule("conduit_unlink", "unlink", "deny"),
                FrameACLViewProfile.build_rule("conduit_create_lesser", "create_lesser_conduit", "deny"),
                FrameACLViewProfile.build_rule("conduit_transfer_ownership", "transfer_ownership", "deny"),
            ],
        ),
        spell_ruleset=FrameACLViewProfile.build_ruleset(
            "safe_spell_codegen",
            [
                FrameACLViewProfile.build_rule("spell_resolve_existing", "resolve_existing", "allow"),
                FrameACLViewProfile.build_rule("spell_bind_existing", "bind_existing", "allow"),
                FrameACLViewProfile.build_rule("spell_local_create", "local_create", "deny"),
                FrameACLViewProfile.build_rule("spell_invoke_method", "invoke_method", "deny"),
                FrameACLViewProfile.build_rule("spell_read_attribute", "read_attribute", "deny"),
                FrameACLViewProfile.build_rule("spell_write_attribute", "write_attribute", "deny"),
            ],
        ),
        capability_ruleset=FrameACLViewProfile.build_ruleset(
            "safe_capability_codegen",
            [
                FrameACLViewProfile.build_rule("capability_dynamic_access", "dynamic_access", "deny"),
                FrameACLViewProfile.build_rule("capability_mutation", "mutation", "deny"),
                FrameACLViewProfile.build_rule("capability_contract_override", "contract_override", "deny"),
                FrameACLViewProfile.build_rule("capability_unsafe_reflection", "unsafe_reflection", "deny"),
                FrameACLViewProfile.build_rule("capability_dunder_access", "dunder_access", "deny"),
            ],
        ),
    )

