import threading

import pytest

from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.frame_acl_profile import (
    FrameACLProfile,
)
from melder.aether.nexus.acl.configurations.profiles import (
    FrameACLProfileBuilder,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_rule import (
    FrameACLRule,
)
from melder.aether.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import (
    FrameACLRuleSet,
)
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.frame_acl_manager import FrameACLManager


def test_frame_acl_rule_requires_valid_core_fields() -> None:
    """
    Verify typed ACL rules fail fast on invalid required fields.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="rule_name cannot be empty"):
        FrameACLRule(rule_name="", operation="visible", effect="allow")

    with pytest.raises(ValueError, match="operation cannot be empty"):
        FrameACLRule(rule_name="visible_rule", operation="", effect="allow")

    with pytest.raises(ValueError, match="effect must be one of"):
        FrameACLRule(
            rule_name="visible_rule",
            operation="visible",
            effect="maybe",
        )

    with pytest.raises(TypeError, match="conditions must be a dict"):
        FrameACLRule(
            rule_name="visible_rule",
            operation="visible",
            effect="allow",
            conditions=[],
        )


def test_frame_acl_rule_copies_conditions() -> None:
    """
    Verify typed ACL rules detach their condition mapping.

    Returns:
        None.
    """
    conditions = {"target": "spell", "section": "metadata"}
    rule = FrameACLRule(
        rule_name="show_metadata",
        operation="show_metadata",
        effect="allow",
        conditions=conditions,
    )

    conditions["mutated"] = True

    assert rule.rule_name == "show_metadata"
    assert rule.id is not None
    assert rule.operation == "show_metadata"
    assert rule.effect == "allow"
    assert rule.conditions == {"target": "spell", "section": "metadata"}


def test_frame_acl_rule_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    rule = FrameACLRule(
        rule_name="visible_rule",
        operation="visible",
        effect="allow",
    )

    rule.cleanup()
    rule.cleanup()

    assert rule.cleaned is True


def test_frame_acl_rule_from_json_rejects_non_dict_payload() -> None:
    """
    Verify JSON reconstruction rejects non-dictionary payloads.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="payload must be a dict"):
        FrameACLRule.from_json_dict(None)


def test_frame_acl_ruleset_registers_replaces_and_removes_rules() -> None:
    """
    Verify rulesets own rules by name and clean replaced/removed rules.

    Returns:
        None.
    """
    ruleset = FrameACLRuleSet("spell_rules")
    first_rule = FrameACLRule(
        rule_name="visible",
        operation="visible",
        effect="allow",
    )
    second_rule = FrameACLRule(
        rule_name="visible",
        operation="visible",
        effect="deny",
    )

    ruleset.register_rule(first_rule)
    ruleset.register_rule(second_rule)

    assert first_rule.cleaned is True
    assert ruleset.get_required_rule("visible") is second_rule
    assert ruleset.list_rule_names() == ["visible"]
    assert ruleset.remove_rule("visible") is True
    assert second_rule.cleaned is True
    assert ruleset.remove_rule("visible") is False


def test_frame_acl_ruleset_exposes_id_and_missing_lookup_behavior() -> None:
    """
    Verify rulesets expose their stable id and missing-rule lookup contract.

    Returns:
        None.
    """
    ruleset = FrameACLRuleSet("spell_rules")

    assert ruleset.id is not None

    with pytest.raises(KeyError, match="missing_rule"):
        ruleset.get_required_rule("missing_rule")


def test_frame_acl_ruleset_rejects_invalid_inputs() -> None:
    """
    Verify ruleset construction, registration, and JSON rebuild reject bad inputs.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="name cannot be empty"):
        FrameACLRuleSet("")

    ruleset = FrameACLRuleSet("spell_rules")

    with pytest.raises(TypeError, match="rule must be a FrameACLRule"):
        ruleset.register_rule(None)

    with pytest.raises(TypeError, match="payload must be a dict"):
        FrameACLRuleSet.from_json_dict(None)

    with pytest.raises(TypeError, match="rules must be a list"):
        FrameACLRuleSet.from_json_dict({"name": "rules", "rules": {}})

    rebuilt = FrameACLRuleSet.from_json_dict({"name": "rules"})
    assert rebuilt.list_rule_names() == []


def test_frame_acl_ruleset_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    ruleset = FrameACLRuleSet("spell_rules")

    ruleset.cleanup()
    ruleset.cleanup()

    assert ruleset.cleaned is True


def test_frame_acl_ruleset_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread already cleaned the ruleset.

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

    ruleset = FrameACLRuleSet("spell_rules")
    coordinated_lock = _CoordinatedLock()
    ruleset._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        ruleset.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert ruleset.cleaned is True
    assert ruleset._lock is None


def test_view_and_codegen_profiles_create_named_default_catalog() -> None:
    """
    Verify the named reusable ACL profile catalog is seeded with rule content.

    Returns:
        None.
    """
    view_profile = FrameACLViewProfile.create_default()
    codegen_profile = FrameACLCodegenProfile.create_default()
    hybrid_view_profile = FrameACLViewProfile.create_hybrid()
    permissive_view_profile = FrameACLViewProfile.create_permissive()
    hybrid_codegen_profile = FrameACLCodegenProfile.create_hybrid()
    permissive_codegen_profile = FrameACLCodegenProfile.create_permissive()

    assert view_profile.name == "safe"
    assert view_profile.version == "0.0.1"
    assert view_profile.required_nexus_label == "default"
    assert view_profile.required_nexus_version == "0.0.1"
    assert view_profile.minimum_spell_payload_type == "general"
    assert view_profile.minimum_spell_payload_version == "0.0.1"
    assert view_profile.frame_ruleset.list_rule_names() == [
        "frame_visible",
        "frame_show_payload",
    ]
    assert view_profile.conduit_ruleset.list_rule_names() == [
        "conduit_visible",
        "conduit_show_payload",
        "conduit_hide_policy",
        "conduit_hide_peer_links",
    ]
    assert "spell_hide_class_profile" in view_profile.spell_ruleset.list_rule_names()
    assert "member_hide_dunder_pattern" in view_profile.member_ruleset.list_rule_names()

    assert codegen_profile.name == "safe"
    assert codegen_profile.version == "0.0.1"
    assert codegen_profile.frame_ruleset.list_rule_names() == ["frame_query"]
    assert "spell_local_create" in codegen_profile.spell_ruleset.list_rule_names()
    assert "capability_mutation" in codegen_profile.capability_ruleset.list_rule_names()

    assert hybrid_view_profile.name == "hybrid"
    assert "spell_show_class_profile" in hybrid_view_profile.spell_ruleset.list_rule_names()
    assert "spell_hide_instance_members" in hybrid_view_profile.spell_ruleset.list_rule_names()

    assert permissive_view_profile.name == "permissive"
    assert "spell_show_instance_members" in permissive_view_profile.spell_ruleset.list_rule_names()
    assert "spell_show_dynamic_access" in permissive_view_profile.spell_ruleset.list_rule_names()

    assert hybrid_codegen_profile.name == "hybrid"
    assert "spell_invoke_method" in hybrid_codegen_profile.spell_ruleset.list_rule_names()
    assert "spell_write_attribute" in hybrid_codegen_profile.spell_ruleset.list_rule_names()

    assert permissive_codegen_profile.name == "permissive"
    assert "spell_local_create" in permissive_codegen_profile.spell_ruleset.list_rule_names()
    assert "capability_dynamic_access" in permissive_codegen_profile.capability_ruleset.list_rule_names()


def test_frame_acl_profile_builder_seeds_defaults_and_composes_profiles() -> None:
    """
    Verify the builder seeds default reusable profiles and composes a frame ACL
    profile from them.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()

    composed_profile = builder.create_profile("support")

    assert builder.version == "0.0.1"
    assert builder.list_view_profile_names() == ["safe", "hybrid", "permissive"]
    assert builder.list_codegen_profile_names() == ["safe", "hybrid", "permissive"]
    assert composed_profile.name == "support"
    assert composed_profile.version == "0.0.1"
    assert composed_profile.view_profile is builder.get_required_view_profile(
        "safe"
    )
    assert (
        composed_profile.codegen_profile
        is builder.get_required_codegen_profile("safe")
    )
    assert composed_profile.view_override_ruleset.list_rule_names() == []
    assert composed_profile.codegen_override_ruleset.list_rule_names() == []


def test_frame_acl_profile_builder_registers_custom_profiles_and_blocks_default_removal() -> None:
    """
    Verify custom reusable profiles can be registered while default profiles
    remain protected.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()
    support_view = FrameACLViewProfile(
        "support_view",
        minimum_spell_payload_type="detailed",
    )
    support_codegen = FrameACLCodegenProfile("support_codegen")

    builder.register_view_profile(support_view)
    builder.register_codegen_profile(support_codegen)

    assert builder.list_view_profile_names() == [
        "safe",
        "hybrid",
        "permissive",
        "support_view",
    ]
    assert builder.list_codegen_profile_names() == [
        "safe",
        "hybrid",
        "permissive",
        "support_codegen",
    ]
    assert builder.remove_view_profile("support_view") is True
    assert builder.remove_codegen_profile("support_codegen") is True

    with pytest.raises(RuntimeError, match="default view profile"):
        builder.remove_view_profile("safe")

    with pytest.raises(RuntimeError, match="default codegen profile"):
        builder.remove_codegen_profile("safe")


def test_frame_acl_profile_requires_typed_profiles() -> None:
    """
    Verify composed frame ACL profiles require typed reusable view/codegen
    profiles.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="name cannot be empty"):
        FrameACLProfile(
            "",
            view_profile=FrameACLViewProfile.create_default(),
            codegen_profile=FrameACLCodegenProfile.create_default(),
        )

    with pytest.raises(TypeError, match="view_profile must be a FrameACLViewProfile"):
        FrameACLProfile(
            "support",
            view_profile=object(),
            codegen_profile=FrameACLCodegenProfile.create_default(),
        )

    with pytest.raises(TypeError, match="codegen_profile must be a FrameACLCodegenProfile"):
        FrameACLProfile(
            "support",
            view_profile=FrameACLViewProfile.create_default(),
            codegen_profile=object(),
        )

    with pytest.raises(ValueError, match="required_nexus_label cannot be empty"):
        FrameACLViewProfile(
            "custom",
            minimum_spell_payload_type="general",
            required_nexus_label="",
        )

    with pytest.raises(ValueError, match="required_nexus_version cannot be empty"):
        FrameACLViewProfile(
            "custom",
            minimum_spell_payload_type="general",
            required_nexus_version="",
        )

    with pytest.raises(ValueError, match="minimum_spell_payload_version cannot be empty"):
        FrameACLViewProfile(
            "custom",
            minimum_spell_payload_type="general",
            minimum_spell_payload_version="",
        )

    with pytest.raises(ValueError, match="version cannot be empty"):
        FrameACLProfile(
            "support",
            view_profile=FrameACLViewProfile.create_default(),
            codegen_profile=FrameACLCodegenProfile.create_default(),
            version="",
        )


def test_frame_acl_profile_cleanup_cleans_only_owned_overrides() -> None:
    """
    Verify composed profile cleanup clears owned override rulesets but leaves
    shared reusable profiles alone.

    Returns:
        None.
    """
    view_profile = FrameACLViewProfile.create_default()
    codegen_profile = FrameACLCodegenProfile.create_default()
    profile = FrameACLProfile(
        "support",
        view_profile=view_profile,
        codegen_profile=codegen_profile,
    )

    view_override_ruleset = profile.view_override_ruleset
    codegen_override_ruleset = profile.codegen_override_ruleset

    profile.cleanup()

    assert profile.cleaned is True
    assert view_override_ruleset.cleaned is True
    assert codegen_override_ruleset.cleaned is True
    assert view_profile.cleaned is False
    assert codegen_profile.cleaned is False
    assert view_profile.id is not None


def test_frame_acl_profile_exposes_stable_id() -> None:
    """
    Verify the composed profile exposes its stable id.

    Returns:
        None.
    """
    profile = FrameACLProfile(
        "support",
        view_profile=FrameACLViewProfile.create_default(),
        codegen_profile=FrameACLCodegenProfile.create_default(),
    )

    assert profile.id is not None


def test_frame_acl_profile_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    profile = FrameACLProfile(
        "support",
        view_profile=FrameACLViewProfile.create_default(),
        codegen_profile=FrameACLCodegenProfile.create_default(),
    )

    profile.cleanup()
    profile.cleanup()

    assert profile.cleaned is True


def test_frame_acl_profile_cleanup_rechecks_cleaned_inside_lock() -> None:
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

    profile = FrameACLProfile(
        "support",
        view_profile=FrameACLViewProfile.create_default(),
        codegen_profile=FrameACLCodegenProfile.create_default(),
    )
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


def test_frame_acl_view_profile_cleanup_is_idempotent() -> None:
    """
    Verify reusable view profile cleanup can be called repeatedly.

    Returns:
        None.
    """
    profile = FrameACLViewProfile(
        "custom",
        minimum_spell_payload_type="general",
    )

    profile.cleanup()
    profile.cleanup()

    assert profile.cleaned is True


def test_frame_acl_view_profile_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify reusable view profile cleanup returns early when already cleaned.

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

    profile = FrameACLViewProfile(
        "custom",
        minimum_spell_payload_type="general",
    )
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


def test_frame_acl_view_profile_coerce_ruleset_rejects_invalid_type() -> None:
    """
    Verify the reusable view profile ruleset coercion rejects wrong types.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="ruleset must be a FrameACLRuleSet"):
        FrameACLViewProfile.coerce_ruleset("bad_ruleset", "default_name")


def test_frame_acl_manager_exposes_profile_builder_and_profile_registry_surface() -> None:
    """
    Verify the manager owns the ACL profile builder/library and the composed
    profile registry separately.

    Returns:
        None.
    """
    manager = FrameACLManager()
    profile = manager._create_frame_acl_profile("support")

    assert manager.version == "0.0.1"
    assert manager.frame_acl_profile_builder.version == "0.0.1"
    assert manager._list_view_acl_profile_names() == ["safe", "hybrid", "permissive"]
    assert manager._list_codegen_acl_profile_names() == ["safe", "hybrid", "permissive"]
    assert manager._get_required_frame_acl_profile("support") is profile
    assert manager._list_frame_acl_profile_names() == ["support"]
    assert manager.frame_acl_profiles_by_name == {"support": profile}


def test_frame_acl_manager_profile_replace_and_remove_cleanup_old_profiles() -> None:
    """
    Verify composed profile replacement and removal clean old profile objects.

    Returns:
        None.
    """
    manager = FrameACLManager()
    first_profile = manager._create_frame_acl_profile("support")
    second_profile = manager.frame_acl_profile_builder.create_profile("support")

    manager._register_frame_acl_profile(second_profile)

    assert first_profile.cleaned is True
    assert manager._get_required_frame_acl_profile("support") is second_profile
    assert manager._remove_frame_acl_profile("support") is True
    assert second_profile.cleaned is True
    assert manager._remove_frame_acl_profile("support") is False
    with pytest.raises(KeyError, match="support"):
        manager._get_required_frame_acl_profile("support")

