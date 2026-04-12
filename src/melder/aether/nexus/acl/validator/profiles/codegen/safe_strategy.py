from typing import Set

from melder.aether.nexus.acl.configurations.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import (
    FrameACLRuleSet,
)


_SAFE_CODEGEN_FORBIDDEN_OVERRIDES = {
    "conduit": {
        "link",
        "unlink",
        "create_lesser_conduit",
        "transfer_ownership",
    },
    "spell": {
        "local_create",
        "invoke_method",
        "read_attribute",
        "write_attribute",
    },
    "capability": {
        "dynamic_access",
        "mutation",
        "contract_override",
        "unsafe_reflection",
        "dunder_access",
    },
}


def validate_profile_configuration(
        profile: FrameACLCodegenProfile,
        configuration: FrameACLCodegenConfiguration,
) -> None:
    """
    Validate that the `safe` codegen profile stays restrictive.

    Returns:
        None.
    """
    _ = profile
    _assert_forbidden_operations_are_not_allowed(
        configuration.conduit_override_ruleset,
        _SAFE_CODEGEN_FORBIDDEN_OVERRIDES["conduit"],
        "safe codegen conduit",
    )
    _assert_forbidden_operations_are_not_allowed(
        configuration.spell_override_ruleset,
        _SAFE_CODEGEN_FORBIDDEN_OVERRIDES["spell"],
        "safe codegen spell",
    )
    _assert_forbidden_operations_are_not_allowed(
        configuration.capability_override_ruleset,
        _SAFE_CODEGEN_FORBIDDEN_OVERRIDES["capability"],
        "safe codegen capability",
    )


def _assert_forbidden_operations_are_not_allowed(
        ruleset: FrameACLRuleSet,
        forbidden_operations: Set[str],
        label: str,
) -> None:
    for rule in ruleset.rules_by_name.values():
        if rule.effect == "allow" and rule.operation in forbidden_operations:
            raise ValueError(
                "Safe profile cannot allow '{0}' in {1} ruleset.".format(
                    rule.operation,
                    label,
                )
            )
