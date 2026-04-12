import pytest

from melder.aether.nexus.acl.configurations.frame_acl_command_configuration import (
    FrameACLCommandConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_rule import FrameACLRule
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet


def test_frame_acl_command_configuration_create_default_sets_baseline() -> None:
    """
    Verify the default command configuration builds a stable typed baseline.

    Returns:
        None.
    """
    configuration = FrameACLCommandConfiguration.create_default()

    assert configuration.profile_name == "safe"
    assert configuration.profile_version == "0.0.1"
    assert configuration.to_json_dict()["profile_name"] == "safe"


def test_frame_acl_command_configuration_from_json_reconstructs_rulesets() -> None:
    """
    Verify JSON payloads rebuild the command configuration and rulesets.

    Returns:
        None.
    """
    configuration = FrameACLCommandConfiguration.from_json_dict(
        {
            "profile_name": "strict_command",
            "profile_version": "0.0.1",
            "frame_override_ruleset": {
                "name": "frame_override",
                "rules": [
                    {
                        "rule_name": "enable_frame",
                        "operation": "enable",
                        "effect": "allow",
                    }
                ],
            },
            "conduit_override_ruleset": {
                "name": "conduit_override",
                "rules": [],
            },
            "spell_override_ruleset": {
                "name": "spell_override",
                "rules": [],
            },
            "member_override_ruleset": {
                "name": "member_override",
                "rules": [
                    {
                        "rule_name": "allow_method",
                        "operation": "invoke_method",
                        "effect": "allow",
                        "conditions": {"member_name": "run"},
                    }
                ],
            },
        }
    )

    assert configuration.profile_name == "strict_command"
    assert configuration.frame_override_ruleset.get_required_rule(
        "enable_frame"
    ).operation == "enable"
    assert configuration.member_override_ruleset.get_required_rule(
        "allow_method"
    ).conditions == {"member_name": "run"}


def test_frame_acl_command_configuration_init_rejects_invalid_inputs() -> None:
    """
    Verify command configuration construction rejects invalid inputs.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="profile_name cannot be empty"):
        FrameACLCommandConfiguration(
            profile_name="",
            profile_version="0.0.1",
        )

    with pytest.raises(ValueError, match="profile_version cannot be empty"):
        FrameACLCommandConfiguration(
            profile_name="default",
            profile_version="",
        )

    with pytest.raises(TypeError, match="ruleset must be a FrameACLRuleSet"):
        FrameACLCommandConfiguration(
            profile_name="default",
            profile_version="0.0.1",
            frame_override_ruleset="bad",
        )


def test_frame_acl_command_configuration_clone_returns_detached_copy() -> None:
    """
    Verify clone returns a detached copy of the configuration and rulesets.

    Returns:
        None.
    """
    configuration = FrameACLCommandConfiguration(
        profile_name="strict_command",
        profile_version="0.0.1",
        member_override_ruleset=FrameACLRuleSet(
            "member_override",
            rules=[
                FrameACLRule(
                    rule_name="allow_run",
                    operation="invoke_method",
                    effect="allow",
                    conditions={"member_name": "run"},
                )
            ],
        ),
    )

    cloned = configuration.clone()

    assert cloned is not configuration
    assert cloned.profile_name == configuration.profile_name
    assert (
        cloned.member_override_ruleset
        is not configuration.member_override_ruleset
    )
    assert cloned.to_json_dict() == configuration.to_json_dict()


def test_frame_acl_command_configuration_cleanup_clears_owned_fields() -> None:
    """
    Verify cleanup nulls the owned rulesets and identity fields.

    Returns:
        None.
    """
    configuration = FrameACLCommandConfiguration(
        profile_name="strict_command",
        profile_version="0.0.1",
    )
    frame_ruleset = configuration.frame_override_ruleset
    member_ruleset = configuration.member_override_ruleset

    configuration.cleanup()

    assert configuration.cleaned is True
    assert frame_ruleset.cleaned is True
    assert member_ruleset.cleaned is True
    assert configuration._profile_name is None
    assert configuration._profile_version is None
    assert configuration._frame_override_ruleset is None
    assert configuration._member_override_ruleset is None
    assert configuration._lock is None
