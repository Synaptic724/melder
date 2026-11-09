import pytest

from melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
from melder.nexus.acl.configurations.profiles.rules.frame_acl_rule import (
    FrameACLRule,
)
from melder.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import (
    FrameACLRuleSet,
)
from tests._cleanup_recheck_support import CleanupRecheckHandshake


def test_frame_acl_command_profile_init_rejects_empty_identity_fields() -> None:
    """
    Verify construction rejects empty profile identity inputs.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="name cannot be empty"):
        FrameACLCommandProfile("")

    with pytest.raises(ValueError, match="validation_strategy_name cannot be empty"):
        FrameACLCommandProfile(
            "safe",
            validation_strategy_name="",
        )

    with pytest.raises(ValueError, match="version cannot be empty"):
        FrameACLCommandProfile(
            "safe",
            version="",
        )


def test_frame_acl_command_profile_factory_methods_return_expected_profiles() -> None:
    """
    Verify the reusable factory helpers return the expected built-in profiles.

    Returns:
        None.
    """
    default_profile = FrameACLCommandProfile.create_default()
    safe_profile = FrameACLCommandProfile.create_safe()
    hybrid_profile = FrameACLCommandProfile.create_hybrid()
    permissive_profile = FrameACLCommandProfile.create_permissive()
    precision_profile = FrameACLCommandProfile.create_precision()

    assert default_profile.name == "safe"
    assert safe_profile.validation_strategy_name == "safe"
    assert hybrid_profile.name == "hybrid"
    assert permissive_profile.name == "permissive"
    assert precision_profile.validation_strategy_name == "precision"


def test_frame_acl_command_profile_exposes_stable_id() -> None:
    """
    Verify the public id property returns the stable identifier.

    Returns:
        None.
    """
    profile = FrameACLCommandProfile("safe")

    assert isinstance(profile.id, str)
    assert profile.id


def test_frame_acl_command_profile_coerce_ruleset_rejects_wrong_type() -> None:
    """
    Verify ruleset coercion rejects non-ruleset values.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="ruleset must be a FrameACLRuleSet instance."):
        FrameACLCommandProfile.coerce_ruleset("bad", "safe_spell")


def test_frame_acl_command_profile_build_helpers_return_typed_objects() -> None:
    """
    Verify the public build helpers return typed ACL rules and rulesets.

    Returns:
        None.
    """
    rule = FrameACLCommandProfile.build_rule(
        "allow_run",
        "invoke_method",
        "allow",
        {"member_name": "run"},
    )
    ruleset = FrameACLCommandProfile.build_ruleset("safe_member", [rule])

    assert isinstance(rule, FrameACLRule)
    assert isinstance(ruleset, FrameACLRuleSet)
    assert ruleset.get_required_rule("allow_run").conditions == {"member_name": "run"}


def test_frame_acl_command_profile_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly without error.

    Returns:
        None.
    """
    profile = FrameACLCommandProfile("safe")

    profile.cleanup()
    profile.cleanup()

    assert profile.cleaned is True
    assert not hasattr(profile, '_lock')


def test_frame_acl_command_profile_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread marks the profile cleaned.

    The handshake holds the first caller inside the lock until the second has passed the outer `_cleaned` check
    and is about to block, then marks the profile cleaned, as a cleanup racing in from elsewhere would. Both
    callers must return at the inner recheck and finish without raising - without it the teardown would run
    twice and the second run would raise on attributes the first had already deleted - and the profile must read
    cleaned. The handshake also fails the test if either caller is still running after its bounded join. The
    callers are ordered by the handshake, not by timing: the earlier hand-made lock could lose its signal and
    failed on CI (GitHub #206; TASK-2026-11-08-deterministic_cleanup_recheck_handshake).

    Returns:
        None.
    """
    profile = FrameACLCommandProfile("safe")

    def _mark_cleaned() -> None:
        """Mark the profile cleaned while the first caller holds the lock and the second waits for it."""
        profile._cleaned = True

    handshake = CleanupRecheckHandshake(on_holder_ready=_mark_cleaned)
    profile._lock = handshake.lock

    handshake.run(profile.cleanup)

    assert profile.cleaned is True
