from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)


def create_full_access_codegen_profile() -> FrameACLCodegenProfile:
    """
    Build the reusable `full_access` codegen profile.

    Contract:
        This is the unconstrained top-end codegen posture in the current ACL
        model. It enables imports without an allowlist, leaves builtin/meta
        posture open, and allows the broadest conduit, spell, and capability
        operations including recursive codegen.

    Returns:
        FrameACLCodegenProfile: Reusable `full_access` codegen profile.
    """
    return FrameACLCodegenProfile(
        "full_access",
        validation_strategy_name="generic",
        frame_ruleset=FrameACLViewProfile.build_ruleset(
            "full_access_frame_codegen",
            [
                FrameACLViewProfile.build_rule("frame_query", "query", "allow"),
            ],
        ),
        conduit_ruleset=FrameACLViewProfile.build_ruleset(
            "full_access_conduit_codegen",
            [
                FrameACLViewProfile.build_rule("conduit_query", "query", "allow"),
                FrameACLViewProfile.build_rule("conduit_link", "link", "allow"),
                FrameACLViewProfile.build_rule("conduit_unlink", "unlink", "allow"),
                FrameACLViewProfile.build_rule(
                    "conduit_create_lesser",
                    "create_lesser_conduit",
                    "allow",
                ),
                FrameACLViewProfile.build_rule(
                    "conduit_transfer_ownership",
                    "transfer_ownership",
                    "allow",
                ),
            ],
        ),
        spell_ruleset=FrameACLViewProfile.build_ruleset(
            "full_access_spell_codegen",
            [
                FrameACLViewProfile.build_rule(
                    "spell_resolve_existing",
                    "resolve_existing",
                    "allow",
                ),
                FrameACLViewProfile.build_rule(
                    "spell_bind_existing",
                    "bind_existing",
                    "allow",
                ),
                FrameACLViewProfile.build_rule(
                    "spell_local_create",
                    "local_create",
                    "allow",
                ),
                FrameACLViewProfile.build_rule(
                    "spell_invoke_method",
                    "invoke_method",
                    "allow",
                ),
                FrameACLViewProfile.build_rule(
                    "spell_read_attribute",
                    "read_attribute",
                    "allow",
                ),
                FrameACLViewProfile.build_rule(
                    "spell_write_attribute",
                    "write_attribute",
                    "allow",
                ),
            ],
        ),
        capability_ruleset=FrameACLViewProfile.build_ruleset(
            "full_access_capability_codegen",
            [
                FrameACLViewProfile.build_rule(
                    "capability_enable_imports",
                    "enable_imports",
                    "allow",
                ),
                FrameACLViewProfile.build_rule(
                    "capability_dynamic_access",
                    "dynamic_access",
                    "allow",
                ),
                FrameACLViewProfile.build_rule(
                    "capability_contract_override",
                    "contract_override",
                    "allow",
                ),
                FrameACLViewProfile.build_rule(
                    "capability_mutation",
                    "mutation",
                    "allow",
                ),
                FrameACLViewProfile.build_rule(
                    "capability_unsafe_reflection",
                    "unsafe_reflection",
                    "allow",
                ),
                FrameACLViewProfile.build_rule(
                    "capability_dunder_access",
                    "dunder_access",
                    "allow",
                ),
                FrameACLViewProfile.build_rule(
                    "capability_recursive_codegen",
                    "recursive_codegen",
                    "allow",
                ),
            ],
        ),
    )
