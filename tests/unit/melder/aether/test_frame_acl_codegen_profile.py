import threading

import pytest

from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_rule import FrameACLRule
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet


def _build_ruleset(name: str) -> FrameACLRuleSet:
    """
    Build one tiny ruleset for direct codegen-profile tests.

    Returns:
        FrameACLRuleSet: Ruleset with one concrete ACL rule.
    """
    return FrameACLRuleSet(
        name,
        rules=[
            FrameACLRule(
                rule_name="query_rule",
                operation="query",
                effect="allow",
            )
        ],
    )


def test_frame_acl_codegen_profile_exposes_id_and_rulesets() -> None:
    """
    Verify the reusable codegen profile exposes its stable id and owned rulesets.

    Returns:
        None.
    """
    profile = FrameACLCodegenProfile(
        "custom",
        frame_ruleset=_build_ruleset("frame_rules"),
        conduit_ruleset=_build_ruleset("conduit_rules"),
        spell_ruleset=_build_ruleset("spell_rules"),
        capability_ruleset=_build_ruleset("capability_rules"),
    )

    assert profile.id is not None
    assert profile.name == "custom"
    assert profile.version == "0.0.1"
    assert profile.frame_ruleset.name == "frame_rules"
    assert profile.conduit_ruleset.name == "conduit_rules"
    assert profile.spell_ruleset.name == "spell_rules"
    assert profile.capability_ruleset.name == "capability_rules"


def test_frame_acl_codegen_profile_rejects_empty_validation_strategy_name() -> None:
    """
    Verify codegen profiles require a non-empty validation strategy name.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="validation_strategy_name cannot be empty"):
        FrameACLCodegenProfile(
            "custom",
            validation_strategy_name="",
        )


def test_frame_acl_codegen_profile_create_precision_exposes_precision_identity() -> None:
    """
    Verify the reusable precision codegen profile can be created directly.

    Returns:
        None.
    """
    profile = FrameACLCodegenProfile.create_precision()

    assert profile.name == "precision"
    assert profile.validation_strategy_name == "precision"


def test_frame_acl_codegen_profile_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    profile = FrameACLCodegenProfile("custom")

    profile.cleanup()
    profile.cleanup()

    assert profile.cleaned is True


def test_frame_acl_codegen_profile_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread already cleaned the profile.

    Returns:
        None.
    """

    class _CoordinatedLock:
        def __init__(self) -> None:
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
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    profile = FrameACLCodegenProfile("custom")
    coordinated_lock = _CoordinatedLock()
    profile._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        profile.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert profile.cleaned is True
    assert profile._lock is None
