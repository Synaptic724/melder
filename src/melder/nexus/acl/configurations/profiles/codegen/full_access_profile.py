from melder.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
class FullAccessCodegenProfileStrategy:
    """
    Build the reusable `full_access` codegen profile.

    Contract:
        This is the unconstrained top-end codegen posture in the current ACL
        model. It enables imports without an allowlist, leaves builtin/meta
        posture open, and allows the broadest conduit, spell, and capability
        operations including recursive codegen.

    Threading:
        Stateless preset construction; holds no state between builds.

    Registration:
        MELDER KERNEL - guarded. Registered as a preset strategy in the codegen
        profile builder and selected by name.

    Subsystem Context:
        The unconstrained top end of the codegen posture ladder, above
        `permissive`. It exists only in the codegen family - view and command
        stop at `permissive`.

    System Context:
        This posture removes the gates the others keep: imports without an
        allowlist, open builtin and meta posture, and recursive codegen. That
        combination means generated code can import arbitrarily, reach
        interpreter internals, and generate further code - so a room carrying
        it has effectively unbounded reach into the process.
        It is named `full_access` rather than something softer for exactly that
        reason. Naming it honestly is a safety feature: an operator selecting it
        cannot mistake it for a merely-generous posture, and an audit reading a
        frame's chain sees the widest grant spelled out.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Build the reusable `full_access` codegen profile. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )
    _NAME = "full_access"

    @property
    def name(self) -> str:
        """Return the stable codegen-profile strategy name."""
        return self._NAME

    def build(self) -> FrameACLCodegenProfile:
        """
        Build and return one configured `full_access` codegen profile.

        Contract:
            Assembles a fresh `FrameACLCodegenProfile` (validation strategy
            `generic`) encoding the unconstrained top-of-ladder posture: every
            frame, conduit (query/link/unlink/create-lesser/transfer-ownership),
            spell (resolve/bind/local-create/invoke/read/write), and capability
            operation is ALLOWED. This is the deliberately permissive preset;
            prefer a narrower rung unless full access is genuinely intended.
            Stateless: a new instance is returned per call.

        Returns:
            FrameACLCodegenProfile: A freshly built `full_access` codegen
                profile.
        """
        return FrameACLCodegenProfile(
        self._NAME,
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
