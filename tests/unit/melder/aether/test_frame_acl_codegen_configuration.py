import threading

import pytest

from melder.aether.nexus.acl.configurations.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_rule import FrameACLRule
from melder.aether.nexus.acl.configurations.profiles import FrameACLRuleSet


def _build_ruleset(name: str, rule_name: str = "allow_read") -> FrameACLRuleSet:
    """
    Build one small ruleset for direct configuration tests.

    Returns:
        FrameACLRuleSet: Ruleset with one concrete ACL rule.
    """
    return FrameACLRuleSet(
        name,
        rules=[
            FrameACLRule(
                rule_name=rule_name,
                operation="read",
                effect="allow",
                conditions={"scope": "frame"},
            )
        ],
    )


def test_frame_acl_codegen_configuration_init_rejects_invalid_inputs() -> None:
    """
    Verify construction rejects empty identity fields and invalid ruleset types.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="profile_name cannot be empty"):
        FrameACLCodegenConfiguration(
            profile_name="",
            profile_version="0.0.1",
        )

    with pytest.raises(ValueError, match="profile_version cannot be empty"):
        FrameACLCodegenConfiguration(
            profile_name="safe",
            profile_version="",
        )

    with pytest.raises(TypeError, match="ruleset must be a FrameACLRuleSet"):
        FrameACLCodegenConfiguration(
            profile_name="safe",
            profile_version="0.0.1",
            frame_override_ruleset="bad-ruleset",
        )


def test_frame_acl_codegen_configuration_init_detaches_passed_rulesets() -> None:
    """
    Verify passed override rulesets are detached from caller-owned state.

    Returns:
        None.
    """
    frame_ruleset = _build_ruleset("frame_override")
    configuration = FrameACLCodegenConfiguration(
        profile_name="safe",
        profile_version="0.0.1",
        frame_override_ruleset=frame_ruleset,
    )

    assert configuration.profile_name == "safe"
    assert configuration.profile_version == "0.0.1"
    assert configuration.frame_override_ruleset is not frame_ruleset
    assert configuration.frame_override_ruleset.to_json_dict() == frame_ruleset.to_json_dict()
    assert configuration.conduit_override_ruleset.name == "safe_conduit_override"
    assert configuration.spell_override_ruleset.name == "safe_spell_override"
    assert configuration.capability_override_ruleset.name == "safe_capability_override"

    frame_ruleset.remove_rule("allow_read")

    assert configuration.frame_override_ruleset.list_rule_names() == ["allow_read"]

    configuration.cleanup()

    assert frame_ruleset.cleaned is False
    assert frame_ruleset.list_rule_names() == []


def test_frame_acl_codegen_configuration_from_profile_uses_profile_identity() -> None:
    """
    Verify from_profile carries reusable profile identity and detaches overrides.

    Returns:
        None.
    """
    profile = FrameACLCodegenProfile.create_permissive()
    capability_ruleset = _build_ruleset("capability_override")

    configuration = FrameACLCodegenConfiguration.from_profile(
        profile,
        capability_override_ruleset=capability_ruleset,
    )

    assert configuration.profile_name == profile.name
    assert configuration.profile_version == profile.version
    assert configuration.capability_override_ruleset is not capability_ruleset
    assert configuration.capability_override_ruleset.to_json_dict() == capability_ruleset.to_json_dict()


def test_frame_acl_codegen_configuration_from_profile_rejects_wrong_type() -> None:
    """
    Verify from_profile rejects non-profile inputs.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="profile must be a FrameACLCodegenProfile"):
        FrameACLCodegenConfiguration.from_profile(None)


def test_frame_acl_codegen_configuration_from_json_round_trips() -> None:
    """
    Verify JSON reconstruction restores typed rulesets and serializes cleanly.

    Returns:
        None.
    """
    payload = {
        "profile_name": "hybrid",
        "profile_version": "1.2.3",
        "frame_override_ruleset": _build_ruleset("frame_override").to_json_dict(),
        "conduit_override_ruleset": _build_ruleset("conduit_override").to_json_dict(),
        "spell_override_ruleset": _build_ruleset("spell_override").to_json_dict(),
        "capability_override_ruleset": _build_ruleset("capability_override").to_json_dict(),
    }

    configuration = FrameACLCodegenConfiguration.from_json_dict(payload)

    assert configuration.profile_name == "hybrid"
    assert configuration.profile_version == "1.2.3"
    assert configuration.to_json_dict() == payload
    assert configuration.to_json_string().startswith("{")

    with pytest.raises(TypeError, match="payload must be a dict"):
        FrameACLCodegenConfiguration.from_json_dict(None)


def test_frame_acl_codegen_configuration_clone_returns_detached_copy() -> None:
    """
    Verify clone returns a detached configuration copy.

    Returns:
        None.
    """
    configuration = FrameACLCodegenConfiguration(
        profile_name="safe",
        profile_version="0.0.1",
        frame_override_ruleset=_build_ruleset("frame_override"),
    )

    cloned = configuration.clone()

    assert cloned is not configuration
    assert cloned.to_json_dict() == configuration.to_json_dict()
    assert cloned.frame_override_ruleset is not configuration.frame_override_ruleset

    cloned.frame_override_ruleset.remove_rule("allow_read")

    assert configuration.frame_override_ruleset.list_rule_names() == ["allow_read"]
    assert cloned.frame_override_ruleset.list_rule_names() == []


def test_frame_acl_codegen_configuration_cleanup_clears_fields() -> None:
    """
    Verify cleanup tears down owned rulesets and nulls builder state.

    Returns:
        None.
    """
    configuration = FrameACLCodegenConfiguration(
        profile_name="safe",
        profile_version="0.0.1",
        frame_override_ruleset=_build_ruleset("frame_override"),
        conduit_override_ruleset=_build_ruleset("conduit_override"),
        spell_override_ruleset=_build_ruleset("spell_override"),
        capability_override_ruleset=_build_ruleset("capability_override"),
    )
    frame_ruleset = configuration.frame_override_ruleset
    conduit_ruleset = configuration.conduit_override_ruleset
    spell_ruleset = configuration.spell_override_ruleset
    capability_ruleset = configuration.capability_override_ruleset

    configuration.cleanup()

    assert configuration.cleaned is True
    assert frame_ruleset.cleaned is True
    assert conduit_ruleset.cleaned is True
    assert spell_ruleset.cleaned is True
    assert capability_ruleset.cleaned is True
    assert configuration._profile_name is None
    assert configuration._profile_version is None
    assert configuration._frame_override_ruleset is None
    assert configuration._conduit_override_ruleset is None
    assert configuration._spell_override_ruleset is None
    assert configuration._capability_override_ruleset is None
    assert configuration._lock is None


def test_frame_acl_codegen_configuration_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    configuration = FrameACLCodegenConfiguration(
        profile_name="safe",
        profile_version="0.0.1",
    )

    configuration.cleanup()
    configuration.cleanup()

    assert configuration.cleaned is True


def test_frame_acl_codegen_configuration_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread cleans under the lock.

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

    configuration = FrameACLCodegenConfiguration(
        profile_name="safe",
        profile_version="0.0.1",
    )
    coordinated_lock = _CoordinatedLock()
    configuration._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        configuration.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert configuration.cleaned is True
    assert configuration._lock is None
