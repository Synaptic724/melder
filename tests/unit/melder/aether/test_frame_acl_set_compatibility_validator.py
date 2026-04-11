import pytest

from melder.aether.nexus.acl.configurations.frame_acl_command_configuration import (
    FrameACLCommandConfiguration,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.validator.compatibility.frame_acl_set_compatibility_report import (
    FrameACLSetCompatibilityReport,
)
from melder.aether.nexus.acl.validator.compatibility.frame_acl_set_compatibility_validator import (
    FrameACLSetCompatibilityValidator,
)
from melder.aether.nexus.acl.configurations.profiles.builder.frame_acl_profile_builder import (
    FrameACLProfileBuilder,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_rule import FrameACLRule
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet
from melder.aether.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)


def test_frame_acl_set_compatibility_report_tracks_messages_and_cleanup() -> None:
    """
    Verify the detached compatibility report stores warnings/errors cleanly.

    Returns:
        None.
    """
    report = FrameACLSetCompatibilityReport(
        frame_name="ops",
        configuration_id="cfg-1",
    )

    report.add_warning("warn")
    report.add_error("error")

    assert report.has_warnings is True
    assert report.has_errors is True
    assert report.warnings == ("warn",)
    assert report.errors == ("error",)
    assert report.first_error() == "error"

    report.cleanup()

    assert report.cleaned is True
    assert report._warnings is None
    assert report._errors is None


def test_frame_acl_set_compatibility_validator_warns_when_actionable_spell_is_hidden() -> None:
    """
    Verify the set validator warns when command spell access is hidden by view.

    Returns:
        None.
    """
    validator = FrameACLSetCompatibilityValidator(
        "ops",
        FrameACLProfileBuilder(),
    )
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="warning",
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration.from_profile(
            FrameACLViewProfile.create_safe(),
            spell_override_ruleset=FrameACLRuleSet(
                "spell_override",
                rules=[
                    FrameACLRule(
                        rule_name="hide_spell",
                        operation="visible",
                        effect="deny",
                    )
                ],
            ),
        )
    )
    configuration.set_command_configuration(
        FrameACLCommandConfiguration(
            profile_name="strict_command",
            profile_version="0.0.1",
            spell_override_ruleset=FrameACLRuleSet(
                "spell_override",
                rules=[
                    FrameACLRule(
                        rule_name="enable_spell",
                        operation="enable",
                        effect="allow",
                    )
                ],
            ),
        )
    )
    configuration.finalize()

    report = validator.validate_configuration(configuration)

    assert report.has_errors is False
    assert report.has_warnings is True
    assert report.warnings == (
        "command.spell is enabled while view.spell is not visible.",
    )


def test_frame_acl_set_compatibility_validator_warns_when_visible_spell_is_not_actionable() -> None:
    """
    Verify the set validator warns when explicit command policy removes spell actionability.

    Returns:
        None.
    """
    validator = FrameACLSetCompatibilityValidator(
        "ops",
        FrameACLProfileBuilder(),
    )
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="warning",
    )
    configuration.set_command_configuration(
        FrameACLCommandConfiguration(
            profile_name="strict_command",
            profile_version="0.0.1",
            spell_override_ruleset=FrameACLRuleSet(
                "spell_override",
                rules=[
                    FrameACLRule(
                        rule_name="disable_spell",
                        operation="enable",
                        effect="deny",
                    )
                ],
            ),
        )
    )
    configuration.finalize()

    report = validator.validate_configuration(configuration)

    assert report.has_errors is False
    assert report.has_warnings is True
    assert report.warnings == (
        "view.spell is visible while command.spell is not enabled.",
    )


def test_frame_acl_set_compatibility_validator_errors_when_member_actions_lack_spell_enable() -> None:
    """
    Verify member command actions require spell-level command enable.

    Returns:
        None.
    """
    validator = FrameACLSetCompatibilityValidator(
        "ops",
        FrameACLProfileBuilder(),
    )
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="error",
    )
    configuration.set_command_configuration(
        FrameACLCommandConfiguration(
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
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="command.member enables actions while command.spell does not enable spell access"):
        validator.validate_configuration(configuration)


def test_frame_acl_set_compatibility_validator_init_rejects_invalid_inputs() -> None:
    """
    Verify compatibility-validator construction rejects invalid inputs.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        FrameACLSetCompatibilityValidator(
            "",
            FrameACLProfileBuilder(),
        )

    with pytest.raises(TypeError, match="profile_builder cannot be None"):
        FrameACLSetCompatibilityValidator(
            "ops",
            None,
        )
