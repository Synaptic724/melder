from melder.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.nexus.acl.configurations.profiles.codegen.stdlib_import_sets import (
    SAFE_DENIED_BUILTIN_NAMES,
)
from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
class SafeCodegenProfileStrategy:
    """
    Build the reusable `safe` codegen profile.

    Contract:
        This is the most restrictive of the standard codegen profiles. It
        limits codegen to safe query/bind-existing operations and denies link
        mutation, local creation, invocation, writes, and dangerous capability
        escalation.

    Threading:
        Stateless preset construction; holds no state between builds.

    Registration:
        MELDER KERNEL - guarded. Registered as a preset strategy in the codegen
        profile builder and selected by name.

    Subsystem Context:
        One rung of the codegen-family posture ladder. The standard ladder runs
        `safe` -> `hybrid` -> `permissive`, with `precision` as the
        explicitly-enumerated posture and `full_access` as the unconstrained top end.

    System Context:
        These presets exist so ACL authoring starts from a REVIEWED posture
        rather than from an empty ruleset. An operator choosing `safe` gets a
        deliberately restrictive policy someone reasoned about; building the
        same thing rule by rule invites a permissive gap nobody notices.
        The ladder is monotonic by intent - each rung allows a superset of the
        previous one's operations - so moving a frame up or down is a
        comprehensible change rather than an unrelated policy swap. `precision`
        sits outside that ordering deliberately: it is the posture for
        enumerating exactly what is permitted instead of picking a tier.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Build the reusable `safe` codegen profile. Melder kernel machinery:
        read it to understand the runtime, do not drive it directly.
    """
    _NAME = "safe"

    @property
    def name(self) -> str:
        """Return the stable codegen-profile strategy name."""
        return self._NAME

    def build(self) -> FrameACLCodegenProfile:
        """
        Build and return one configured `safe` codegen profile.

        Contract:
            Assembles a fresh `FrameACLCodegenProfile` (validation strategy
            `safe`) encoding the most restrictive standard posture:
            - frame: allow query only.
            - conduit: allow query; DENY link, unlink, create-lesser, and
              transfer-ownership.
            - spell: allow resolve-existing and bind-existing; DENY local-create,
              invoke-method, read-attribute, and write-attribute.
            - capability: imports are NOT enabled; DENY dangerous builtins,
              dynamic access, mutation, contract override, unsafe reflection,
              dunder access, and recursive codegen.
            Stateless: a new instance is returned per call.

        Returns:
            FrameACLCodegenProfile: A freshly built `safe` codegen profile.
        """
        return FrameACLCodegenProfile(
            self._NAME,
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
                    FrameACLViewProfile.build_rule("capability_recursive_codegen", "recursive_codegen", "deny"),
                ],
            ),
        )
