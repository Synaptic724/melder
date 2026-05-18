from typing import Set

from melder.aether.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
from melder.utilities.interfaces.iframeaclcommandconfiguration import (
    IFrameACLCommandConfiguration,
)
from melder.utilities.interfaces.iframeaclruleset import IFrameACLRuleSet


_SAFE_COMMAND_FORBIDDEN_MEMBER_OVERRIDES: Set[str] = {
    "invoke_method",
    "write_attribute",
    "dunder_access",
}


def validate_profile_configuration(
        profile: FrameACLCommandProfile,
        configuration: IFrameACLCommandConfiguration,
) -> None:
    """
    Validate that the `safe` command profile stays restrictive.

    Returns:
        None.
    """
    _ = profile
    _assert_forbidden_operations_are_not_allowed(
        configuration.member_override_ruleset,
        _SAFE_COMMAND_FORBIDDEN_MEMBER_OVERRIDES,
        "safe command member",
    )


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
