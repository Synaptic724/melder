from typing import Set

from melder.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.utilities.interfaces.iframeaclcodegenconfiguration import (
    FrameACLCodegenConfiguration,
)
from melder.utilities.interfaces.iframeaclruleset import IFrameACLRuleSet


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
        "enable_imports",
        "import_modules",
        "dynamic_access",
        "mutation",
        "contract_override",
        "unsafe_reflection",
        "dunder_access",
        "builtin_names",
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
    _assert_safe_builtins_not_reallowed(configuration.capability_override_ruleset)


def _assert_forbidden_operations_are_not_allowed(
        ruleset: IFrameACLRuleSet,
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


def _assert_safe_builtins_not_reallowed(
        ruleset: IFrameACLRuleSet,
) -> None:
    """
    Validate that safe overrides do not re-allow dangerous builtin names.

    Args:
        ruleset:
            Capability override ruleset.

    Returns:
        None.
    """
    dangerous_builtin_names = {
        "breakpoint",
        "compile",
        "dir",
        "eval",
        "exec",
        "getattr",
        "globals",
        "input",
        "locals",
        "setattr",
        "delattr",
        "vars",
    }
    for rule in ruleset.rules_by_name.values():
        if rule.operation != "builtin_names" or rule.effect != "allow":
            continue
        builtin_names = set(rule.conditions.get("builtin_names", tuple()))
        widened_names = builtin_names.intersection(dangerous_builtin_names)
        if len(widened_names) == 0:
            continue
        raise ValueError(
            "Safe profile cannot allow dangerous builtin names: {0}.".format(
                ", ".join(sorted(widened_names))
            )
        )
