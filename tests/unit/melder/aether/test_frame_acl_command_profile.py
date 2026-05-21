import threading

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

    Returns:
        None.
    """

    class _CoordinatedLock:
        def __init__(self, profile: FrameACLCommandProfile) -> None:
            self._profile = profile
            self._entered_first = threading.Event()
            self._second_attempted = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self):
            if self._entered_first.is_set():
                self._second_attempted.set()
            self._lock.acquire()
            if not self._entered_first.is_set():
                self._entered_first.set()
                assert self._second_attempted.wait(timeout=1.0)
                self._profile._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    profile = FrameACLCommandProfile("safe")
    profile._lock = _CoordinatedLock(profile)

    thread = threading.Thread(target=profile.cleanup)
    thread.start()
    assert profile._lock._entered_first.wait(timeout=1.0)
    profile.cleanup()
    thread.join(timeout=1.0)

    assert profile.cleaned is True
    assert thread.is_alive() is False
