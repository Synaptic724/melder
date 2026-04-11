import threading

import pytest

from melder.aether.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles import FrameACLRule
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)


def _build_ruleset(
    name: str,
    *,
    rule_name: str = "visible_rule",
    operation: str = "visible",
    effect: str = "allow",
    conditions: dict | None = None,
) -> FrameACLRuleSet:
    """
    Build one small ruleset for direct view-configuration tests.

    Returns:
        FrameACLRuleSet: Ruleset with one concrete ACL rule.
    """
    return FrameACLRuleSet(
        name,
        rules=[
            FrameACLRule(
                rule_name=rule_name,
                operation=operation,
                effect=effect,
                conditions=conditions,
            )
        ],
    )


def test_frame_acl_view_configuration_init_rejects_invalid_inputs() -> None:
    """
    Verify construction rejects empty identity and invalid ruleset inputs.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="profile_name cannot be empty"):
        FrameACLViewConfiguration(
            profile_name="",
            profile_version="0.0.1",
            minimum_spell_payload_type="general",
        )

    with pytest.raises(ValueError, match="profile_version cannot be empty"):
        FrameACLViewConfiguration(
            profile_name="safe",
            profile_version="",
            minimum_spell_payload_type="general",
        )

    with pytest.raises(ValueError, match="required_nexus_label cannot be empty"):
        FrameACLViewConfiguration(
            profile_name="safe",
            profile_version="0.0.1",
            minimum_spell_payload_type="general",
            required_nexus_label="",
        )

    with pytest.raises(ValueError, match="required_nexus_version cannot be empty"):
        FrameACLViewConfiguration(
            profile_name="safe",
            profile_version="0.0.1",
            minimum_spell_payload_type="general",
            required_nexus_version="",
        )

    with pytest.raises(ValueError, match="minimum_spell_payload_type cannot be empty"):
        FrameACLViewConfiguration(
            profile_name="safe",
            profile_version="0.0.1",
            minimum_spell_payload_type="",
        )

    with pytest.raises(ValueError, match="minimum_spell_payload_version cannot be empty"):
        FrameACLViewConfiguration(
            profile_name="safe",
            profile_version="0.0.1",
            minimum_spell_payload_type="general",
            minimum_spell_payload_version="",
        )

    with pytest.raises(TypeError, match="ruleset must be a FrameACLRuleSet"):
        FrameACLViewConfiguration(
            profile_name="safe",
            profile_version="0.0.1",
            minimum_spell_payload_type="general",
            frame_override_ruleset="bad-ruleset",
        )


def test_frame_acl_view_configuration_init_detaches_passed_rulesets() -> None:
    """
    Verify passed override rulesets are detached from caller-owned state.

    Returns:
        None.
    """
    frame_ruleset = _build_ruleset("frame_override")
    member_ruleset = _build_ruleset(
        "member_override",
        rule_name="member_rule",
        operation="show_member",
        conditions={"member_name": "state"},
    )
    configuration = FrameACLViewConfiguration(
        profile_name="safe",
        profile_version="0.0.1",
        minimum_spell_payload_type="general",
        frame_override_ruleset=frame_ruleset,
        member_override_ruleset=member_ruleset,
    )

    assert configuration.profile_name == "safe"
    assert configuration.profile_version == "0.0.1"
    assert configuration.required_nexus_label == "default"
    assert configuration.required_nexus_version == "0.0.1"
    assert configuration.minimum_spell_payload_type == "general"
    assert configuration.minimum_spell_payload_version == "0.0.1"
    assert configuration.frame_override_ruleset is not frame_ruleset
    assert configuration.member_override_ruleset is not member_ruleset
    assert configuration.frame_override_ruleset.to_json_dict() == frame_ruleset.to_json_dict()
    assert configuration.member_override_ruleset.to_json_dict() == member_ruleset.to_json_dict()
    assert configuration.conduit_override_ruleset.name == "safe_conduit_override"
    assert configuration.spell_override_ruleset.name == "safe_spell_override"

    frame_ruleset.remove_rule("visible_rule")
    member_ruleset.remove_rule("member_rule")

    assert configuration.frame_override_ruleset.list_rule_names() == ["visible_rule"]
    assert configuration.member_override_ruleset.list_rule_names() == ["member_rule"]

    configuration.cleanup()

    assert frame_ruleset.cleaned is False
    assert member_ruleset.cleaned is False


def test_frame_acl_view_configuration_from_profile_uses_profile_identity() -> None:
    """
    Verify from_profile carries reusable profile identity and detaches overrides.

    Returns:
        None.
    """
    profile = FrameACLViewProfile.create_hybrid()
    spell_ruleset = _build_ruleset("spell_override", operation="show_metadata")

    configuration = FrameACLViewConfiguration.from_profile(
        profile,
        spell_override_ruleset=spell_ruleset,
    )

    assert configuration.profile_name == profile.name
    assert configuration.profile_version == profile.version
    assert configuration.required_nexus_label == profile.required_nexus_label
    assert configuration.required_nexus_version == profile.required_nexus_version
    assert configuration.minimum_spell_payload_type == profile.minimum_spell_payload_type
    assert configuration.minimum_spell_payload_version == profile.minimum_spell_payload_version
    assert configuration.spell_override_ruleset is not spell_ruleset
    assert configuration.spell_override_ruleset.to_json_dict() == spell_ruleset.to_json_dict()


def test_frame_acl_view_configuration_from_profile_rejects_wrong_type() -> None:
    """
    Verify from_profile rejects non-profile inputs.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="profile must be a FrameACLViewProfile"):
        FrameACLViewConfiguration.from_profile(None)


def test_frame_acl_view_configuration_from_json_round_trips() -> None:
    """
    Verify JSON reconstruction restores typed rulesets and serializes cleanly.

    Returns:
        None.
    """
    payload = {
        "profile_name": "hybrid",
        "profile_version": "1.2.3",
        "required_nexus_label": "default",
        "required_nexus_version": "0.0.1",
        "minimum_spell_payload_type": "detailed",
        "minimum_spell_payload_version": "0.0.1",
        "frame_override_ruleset": _build_ruleset("frame_override").to_json_dict(),
        "conduit_override_ruleset": _build_ruleset("conduit_override").to_json_dict(),
        "spell_override_ruleset": _build_ruleset(
            "spell_override",
            operation="show_metadata",
        ).to_json_dict(),
        "member_override_ruleset": _build_ruleset(
            "member_override",
            rule_name="member_rule",
            operation="show_member",
            conditions={"member_name": "state"},
        ).to_json_dict(),
    }

    configuration = FrameACLViewConfiguration.from_json_dict(payload)

    assert configuration.to_json_dict() == payload
    assert configuration.to_json_string().startswith("{")

    with pytest.raises(TypeError, match="payload must be a dict"):
        FrameACLViewConfiguration.from_json_dict(None)


def test_frame_acl_view_configuration_clone_returns_detached_copy() -> None:
    """
    Verify clone returns a detached configuration copy.

    Returns:
        None.
    """
    configuration = FrameACLViewConfiguration(
        profile_name="safe",
        profile_version="0.0.1",
        minimum_spell_payload_type="general",
        frame_override_ruleset=_build_ruleset("frame_override"),
    )

    cloned = configuration.clone()

    assert cloned is not configuration
    assert cloned.to_json_dict() == configuration.to_json_dict()
    assert cloned.frame_override_ruleset is not configuration.frame_override_ruleset

    cloned.frame_override_ruleset.remove_rule("visible_rule")

    assert configuration.frame_override_ruleset.list_rule_names() == ["visible_rule"]
    assert cloned.frame_override_ruleset.list_rule_names() == []


def test_frame_acl_view_configuration_cleanup_clears_fields() -> None:
    """
    Verify cleanup tears down owned rulesets and nulls configuration state.

    Returns:
        None.
    """
    configuration = FrameACLViewConfiguration(
        profile_name="safe",
        profile_version="0.0.1",
        minimum_spell_payload_type="general",
        frame_override_ruleset=_build_ruleset("frame_override"),
        conduit_override_ruleset=_build_ruleset("conduit_override"),
        spell_override_ruleset=_build_ruleset("spell_override", operation="show_metadata"),
        member_override_ruleset=_build_ruleset(
            "member_override",
            rule_name="member_rule",
            operation="show_member",
            conditions={"member_name": "state"},
        ),
    )
    frame_ruleset = configuration.frame_override_ruleset
    conduit_ruleset = configuration.conduit_override_ruleset
    spell_ruleset = configuration.spell_override_ruleset
    member_ruleset = configuration.member_override_ruleset

    configuration.cleanup()

    assert configuration.cleaned is True
    assert frame_ruleset.cleaned is True
    assert conduit_ruleset.cleaned is True
    assert spell_ruleset.cleaned is True
    assert member_ruleset.cleaned is True
    assert configuration._profile_name is None
    assert configuration._profile_version is None
    assert configuration._required_nexus_label is None
    assert configuration._required_nexus_version is None
    assert configuration._minimum_spell_payload_type is None
    assert configuration._minimum_spell_payload_version is None
    assert configuration._frame_override_ruleset is None
    assert configuration._conduit_override_ruleset is None
    assert configuration._spell_override_ruleset is None
    assert configuration._member_override_ruleset is None
    assert configuration._lock is None


def test_frame_acl_view_configuration_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    configuration = FrameACLViewConfiguration(
        profile_name="safe",
        profile_version="0.0.1",
        minimum_spell_payload_type="general",
    )

    configuration.cleanup()
    configuration.cleanup()

    assert configuration.cleaned is True


def test_frame_acl_view_configuration_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread already cleaned under the lock.

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

    configuration = FrameACLViewConfiguration(
        profile_name="safe",
        profile_version="0.0.1",
        minimum_spell_payload_type="general",
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
