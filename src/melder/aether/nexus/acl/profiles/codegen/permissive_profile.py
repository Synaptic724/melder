from melder.aether.nexus.acl.profiles.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_view_profile import (
    FrameACLViewProfile,
)


def create_permissive_codegen_profile() -> FrameACLCodegenProfile:
    """
    Build the reusable `permissive` codegen profile.

    Contract:
        This is the most open of the standard codegen profiles. It allows the
        broadest set of conduit and spell operations while still denying the
        highest-risk capability gates such as mutation and unsafe reflection.

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
