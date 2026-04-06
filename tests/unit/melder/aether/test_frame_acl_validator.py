import pytest

from melder.aether.nexus.acl.profiles.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_rule import (
    FrameACLRule,
)
from melder.aether.nexus.acl.profiles.frame_acl_ruleset import (
    FrameACLRuleSet,
)
from melder.aether.nexus.acl.profiles.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_validator import FrameACLValidator
from melder.aether.nexus.acl.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)


def test_frame_acl_validator_accepts_matching_configuration() -> None:
    """
    Verify validator accepts a configuration targeting the same frame.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_default("ops")

    assert validator.validate_configuration(configuration) is True
    assert validator.last_validated_configuration_id == configuration.configuration_id


def test_frame_acl_validator_rejects_invalid_inputs() -> None:
    """
    Verify validator rejects non-config inputs and wrong-frame configs.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    finance_configuration = FrameACLConfiguration.create_default("finance")

    with pytest.raises(TypeError, match="configuration must be a FrameACLConfiguration"):
        validator.validate_configuration(None)

    with pytest.raises(ValueError, match="targets frame 'finance', expected 'ops'"):
        validator.validate_configuration(finance_configuration)


def test_frame_acl_validator_init_rejects_empty_frame_name() -> None:
    """
    Verify validator requires a non-empty frame name.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        FrameACLValidator("")


def test_frame_acl_validator_cleanup_clears_state() -> None:
    """
    Verify cleanup nulls validator state.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_default("ops")
    validator.validate_configuration(configuration)

    validator.cleanup()

    assert validator.cleaned is True
    assert validator._frame_name is None
    assert validator._last_validated_configuration_id is None


def test_frame_acl_validator_properties_return_expected_values() -> None:
    """
    Verify validator properties expose the owning frame and last validated id.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_default("ops")

    assert validator.frame_name == "ops"
    assert validator.last_validated_configuration_id is None

    validator.validate_configuration(configuration)

    assert validator.last_validated_configuration_id == configuration.configuration_id


def test_frame_acl_validator_rejects_unsupported_spell_payload_floor() -> None:
    """
    Verify validator rejects unsupported spell payload floor values.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration(
            profile_name="custom",
            profile_version="0.0.1",
            minimum_spell_payload_profile_name="unknown_floor",
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Unsupported minimum_spell_payload_profile_name"):
        validator.validate_configuration(configuration)


def test_frame_acl_validator_rejects_wrong_operation_family() -> None:
    """
    Verify validator rejects operations stored in the wrong ruleset family.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    bad_ruleset = FrameACLRuleSet(
        "frame_override",
        rules=[
            FrameACLRule(
                rule_name="bad_invoke",
                operation="invoke_method",
                effect="allow",
            )
        ],
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration(
            profile_name="custom",
            profile_version="0.0.1",
            minimum_spell_payload_profile_name="detailed",
            frame_override_ruleset=bad_ruleset,
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Unsupported operation 'invoke_method' in view.frame ruleset"):
        validator.validate_configuration(configuration)


def test_frame_acl_validator_rejects_member_rule_without_pattern_or_name() -> None:
    """
    Verify validator rejects malformed member rules missing selector shape.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    bad_member_ruleset = FrameACLRuleSet(
        "member_override",
        rules=[
            FrameACLRule(
                rule_name="bad_member_rule",
                operation="show_member",
                effect="deny",
            )
        ],
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration(
            profile_name="custom",
            profile_version="0.0.1",
            minimum_spell_payload_profile_name="detailed",
            member_override_ruleset=bad_member_ruleset,
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Member rules in view.member must declare 'pattern' or 'member_name'"):
        validator.validate_configuration(configuration)


def test_frame_acl_validator_flags_unsafe_safe_profile_widening() -> None:
    """
    Verify validator flags safe-profile overrides that widen forbidden actions.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    unsafe_spell_ruleset = FrameACLRuleSet(
        "spell_override",
        rules=[
            FrameACLRule(
                rule_name="unsafe_dynamic_access",
                operation="show_dynamic_access",
                effect="allow",
            )
        ],
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration.from_profile(
            FrameACLViewProfile.create_safe(),
            spell_override_ruleset=unsafe_spell_ruleset,
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Safe profile cannot allow 'show_dynamic_access' in safe view spell ruleset"):
        validator.validate_configuration(configuration)


def test_frame_acl_validator_flags_unsafe_safe_codegen_widening() -> None:
    """
    Verify validator flags safe codegen overrides that widen forbidden actions.

    Returns:
        None.
    """
    validator = FrameACLValidator("ops")
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="draft",
    )
    unsafe_capability_ruleset = FrameACLRuleSet(
        "capability_override",
        rules=[
            FrameACLRule(
                rule_name="unsafe_dynamic_access",
                operation="dynamic_access",
                effect="allow",
            )
        ],
    )
    configuration.set_codegen_configuration(
        configuration.codegen_configuration.from_profile(
            FrameACLCodegenProfile.create_safe(),
            capability_override_ruleset=unsafe_capability_ruleset,
        )
    )
    configuration.finalize()

    with pytest.raises(ValueError, match="Safe profile cannot allow 'dynamic_access' in safe codegen capability ruleset"):
        validator.validate_configuration(configuration)
