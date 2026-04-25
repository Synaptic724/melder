from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.stdlib_import_sets import (
    SAFE_DENIED_BUILTIN_NAMES,
)
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)


def create_safe_codegen_profile() -> FrameACLCodegenProfile:
    """
    Build the reusable `safe` codegen profile.

    Contract:
        This is the most restrictive of the standard codegen profiles. It
        limits codegen to safe query/bind-existing operations and denies link
        mutation, local creation, invocation, writes, and dangerous capability
        escalation.

    Returns:
        FrameACLCodegenProfile: Reusable `safe` codegen profile.
    """
    return FrameACLCodegenProfile(
        "safe",
        validation_strategy_name="safe",
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
                FrameACLViewProfile.build_rule(
                    "capability_deny_dangerous_builtins",
                    "builtin_names",
                    "deny",
                    conditions={
                        "builtin_names": SAFE_DENIED_BUILTIN_NAMES,
                    },
                ),
                FrameACLViewProfile.build_rule("capability_dynamic_access", "dynamic_access", "deny"),
                FrameACLViewProfile.build_rule("capability_mutation", "mutation", "deny"),
                FrameACLViewProfile.build_rule("capability_contract_override", "contract_override", "deny"),
                FrameACLViewProfile.build_rule("capability_unsafe_reflection", "unsafe_reflection", "deny"),
                FrameACLViewProfile.build_rule("capability_dunder_access", "dunder_access", "deny"),
            ],
        ),
    )
