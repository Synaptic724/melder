from typing import Set

from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.utilities.interfaces.iframeaclruleset import IFrameACLRuleSet
from melder.utilities.interfaces.iframeaclviewconfiguration import (
    FrameACLViewConfiguration,
)


_SAFE_VIEW_FORBIDDEN_OVERRIDES = {
    "conduit": {"show_policy", "show_peer_links"},
    "spell": {
        "show_class_profile",
        "show_callable_profile",
        "show_instance_members",
        "show_dynamic_access",
    },
}


def validate_profile_configuration(
        profile: FrameACLViewProfile,
        configuration: FrameACLViewConfiguration,
) -> None:
    """
    Validate that the `safe` view profile stays restrictive.

    Returns:
        None.
    """
    _ = profile
    _assert_forbidden_operations_are_not_allowed(
        configuration.conduit_override_ruleset,
        _SAFE_VIEW_FORBIDDEN_OVERRIDES["conduit"],
        "safe view conduit",
    )
    _assert_forbidden_operations_are_not_allowed(
        configuration.spell_override_ruleset,
        _SAFE_VIEW_FORBIDDEN_OVERRIDES["spell"],
        "safe view spell",
    )
    for rule in configuration.member_override_ruleset.rules_by_name.values():
        conditions = rule.conditions
        if (
                rule.operation == "show_member"
                and rule.effect == "allow"
                and (
                    conditions.get("pattern") == "__*"
                    or str(conditions.get("member_name", "")).startswith("__")
                )
        ):
            raise ValueError(
                "Safe profile cannot allow dunder member access in safe view member ruleset."
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
