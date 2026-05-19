from melder.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.nexus.acl.configurations.profiles.codegen.stdlib_import_sets import (
    HYBRID_DENIED_BUILTIN_NAMES,
    HYBRID_DENIED_IMPORT_MODULE_ROOTS,
    HYBRID_IMPORT_MODULE_ROOTS,
)
from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.interfaces.iframeaclcodegenprofilestrategy import IFrameACLCodegenProfileStrategy


class HybridCodegenProfileStrategy(IFrameACLCodegenProfileStrategy):
    """
    Build the reusable `hybrid` codegen profile.

    Contract:
        This profile sits between the stricter `safe` posture and the fully
        open `permissive` posture. It allows core query/link/invoke/read
        operations while still denying local creation, direct mutation, and
        the more aggressive capability overrides.

    """
    __melder_internal__ = _mrg.sentinel
    _NAME = "hybrid"

    @property
    def name(self) -> str:
        """Return the stable codegen-profile strategy name."""
        return self._NAME

    def build(self) -> FrameACLCodegenProfile:
        """Build and return one configured `hybrid` codegen profile."""
        return FrameACLCodegenProfile(
        self._NAME,
        validation_strategy_name="generic",
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
                FrameACLViewProfile.build_rule(
                    "capability_enable_imports",
                    "enable_imports",
                    "allow",
                ),
                FrameACLViewProfile.build_rule(
                    "capability_allow_import_modules",
                    "import_modules",
                    "allow",
                    conditions={
                        "module_roots": HYBRID_IMPORT_MODULE_ROOTS,
                    },
                ),
                FrameACLViewProfile.build_rule(
                    "capability_deny_import_modules",
                    "import_modules",
                    "deny",
                    conditions={
                        "module_roots": HYBRID_DENIED_IMPORT_MODULE_ROOTS,
                    },
                ),
                FrameACLViewProfile.build_rule(
                    "capability_deny_dangerous_builtins",
                    "builtin_names",
                    "deny",
                    conditions={
                        "builtin_names": HYBRID_DENIED_BUILTIN_NAMES,
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
