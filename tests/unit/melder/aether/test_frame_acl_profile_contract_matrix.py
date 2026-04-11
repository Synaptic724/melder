import pytest

from melder.aether.nexus.acl.configurations.profiles import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles import (
    FrameACLProfileBuilder,
)
from melder.aether.nexus.acl.configurations.profiles import (
    FrameACLRule,
)
from melder.aether.nexus.acl.configurations.profiles import (
    FrameACLRuleSet,
)
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)


def test_frame_acl_rule_to_json_round_trip_preserves_contract_fields() -> None:
    """
    Verify rule JSON round-trip preserves the public contract fields.

    Returns:
        None.
    """
    rule = FrameACLRule(
        rule_name="show_metadata",
        operation="show_metadata",
        effect="allow",
        conditions={"selector": "spell"},
    )

    rebuilt = FrameACLRule.from_json_dict(rule.to_json_dict())

    assert rebuilt.rule_name == "show_metadata"
    assert rebuilt.operation == "show_metadata"
    assert rebuilt.effect == "allow"
    assert rebuilt.conditions == {"selector": "spell"}


def test_frame_acl_rule_clone_detaches_condition_mapping() -> None:
    """
    Verify rule clones detach their condition mapping from the source.

    Returns:
        None.
    """
    rule = FrameACLRule(
        rule_name="show_dynamic_access",
        operation="show_dynamic_access",
        effect="deny",
        conditions={"pattern": "__*"},
    )

    cloned = rule.clone()
    cloned_conditions = cloned.conditions
    cloned_conditions["mutated"] = True

    assert cloned.conditions == {"pattern": "__*"}
    assert rule.conditions == {"pattern": "__*"}


def test_frame_acl_rule_cleanup_clears_owned_state() -> None:
    """
    Verify cleanup clears the owned rule state.

    Returns:
        None.
    """
    rule = FrameACLRule(
        rule_name="visible",
        operation="visible",
        effect="allow",
        conditions={"target": "frame"},
    )

    rule.cleanup()

    assert rule.cleaned is True
    assert rule._rule_name is None
    assert rule._operation is None
    assert rule._effect is None
    assert rule._conditions is None


def test_frame_acl_ruleset_requires_non_empty_name() -> None:
    """
    Verify rulesets reject empty names.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="name cannot be empty"):
        FrameACLRuleSet("")


def test_frame_acl_ruleset_init_registers_initial_rules_in_order() -> None:
    """
    Verify initial rules are registered in insertion order.

    Returns:
        None.
    """
    ruleset = FrameACLRuleSet(
        "spell_rules",
        rules=[
            FrameACLRule(
                rule_name="visible",
                operation="visible",
                effect="allow",
            ),
            FrameACLRule(
                rule_name="show_metadata",
                operation="show_metadata",
                effect="allow",
            ),
        ],
    )

    assert ruleset.list_rule_names() == ["visible", "show_metadata"]


def test_frame_acl_ruleset_snapshot_is_detached_from_future_mutation() -> None:
    """
    Verify registry snapshots are detached from future ruleset mutation.

    Returns:
        None.
    """
    ruleset = FrameACLRuleSet("spell_rules")
    ruleset.register_rule(
        FrameACLRule(
            rule_name="visible",
            operation="visible",
            effect="allow",
        )
    )

    snapshot = ruleset.rules_by_name
    ruleset.register_rule(
        FrameACLRule(
            rule_name="show_metadata",
            operation="show_metadata",
            effect="allow",
        )
    )

    assert list(snapshot.keys()) == ["visible"]
    assert ruleset.list_rule_names() == ["visible", "show_metadata"]


def test_frame_acl_ruleset_get_required_rule_raises_missing_name() -> None:
    """
    Verify missing rule lookup fails fast.

    Returns:
        None.
    """
    with pytest.raises(KeyError, match="missing"):
        FrameACLRuleSet("spell_rules").get_required_rule("missing")


def test_frame_acl_ruleset_from_json_rejects_invalid_payload_types() -> None:
    """
    Verify JSON reconstruction rejects invalid payload structures.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="payload must be a dict"):
        FrameACLRuleSet.from_json_dict(None)

    with pytest.raises(TypeError, match="rules must be a list"):
        FrameACLRuleSet.from_json_dict({"name": "spell_rules", "rules": {}})


def test_frame_acl_ruleset_clone_returns_detached_copy() -> None:
    """
    Verify ruleset clones are detached from the source registry.

    Returns:
        None.
    """
    ruleset = FrameACLRuleSet(
        "spell_rules",
        rules=[
            FrameACLRule(
                rule_name="visible",
                operation="visible",
                effect="allow",
            )
        ],
    )

    cloned = ruleset.clone()
    cloned.register_rule(
        FrameACLRule(
            rule_name="show_metadata",
            operation="show_metadata",
            effect="allow",
        )
    )

    assert ruleset.list_rule_names() == ["visible"]
    assert cloned.list_rule_names() == ["visible", "show_metadata"]


def test_frame_acl_ruleset_cleanup_cascades_to_owned_rules() -> None:
    """
    Verify ruleset cleanup cascades into owned rules.

    Returns:
        None.
    """
    rule = FrameACLRule(
        rule_name="visible",
        operation="visible",
        effect="allow",
    )
    ruleset = FrameACLRuleSet("spell_rules", rules=[rule])

    ruleset.cleanup()

    assert ruleset.cleaned is True
    assert rule.cleaned is True
    assert ruleset._rules_by_name is None


def test_frame_acl_view_profile_requires_valid_inputs() -> None:
    """
    Verify view profiles reject invalid required fields.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="name cannot be empty"):
        FrameACLViewProfile(
            "",
            minimum_spell_payload_type="detailed",
        )

    with pytest.raises(ValueError, match="minimum_spell_payload_type cannot be empty"):
        FrameACLViewProfile(
            "safe",
            minimum_spell_payload_type="",
        )

    with pytest.raises(ValueError, match="version cannot be empty"):
        FrameACLViewProfile(
            "safe",
            minimum_spell_payload_type="detailed",
            version="",
        )


def test_frame_acl_view_profile_build_helpers_create_expected_types() -> None:
    """
    Verify view-profile helper builders create typed rules and rulesets.

    Returns:
        None.
    """
    rule = FrameACLViewProfile.build_rule(
        "visible",
        "visible",
        "allow",
        {"target": "frame"},
    )
    ruleset = FrameACLViewProfile.build_ruleset("frame_rules", [rule])

    assert isinstance(rule, FrameACLRule)
    assert isinstance(ruleset, FrameACLRuleSet)
    assert ruleset.list_rule_names() == ["visible"]


def test_frame_acl_view_profile_create_default_matches_safe_factory() -> None:
    """
    Verify the default view profile is the safe profile.

    Returns:
        None.
    """
    default_profile = FrameACLViewProfile.create_default()
    safe_profile = FrameACLViewProfile.create_safe()

    assert default_profile.name == "safe"
    assert default_profile.frame_ruleset.list_rule_names() == (
        safe_profile.frame_ruleset.list_rule_names()
    )


def test_frame_acl_view_profile_cleanup_cascades_to_owned_rulesets() -> None:
    """
    Verify view-profile cleanup cascades into the owned rulesets.

    Returns:
        None.
    """
    profile = FrameACLViewProfile.create_hybrid()
    frame_ruleset = profile.frame_ruleset
    conduit_ruleset = profile.conduit_ruleset
    spell_ruleset = profile.spell_ruleset
    member_ruleset = profile.member_ruleset

    profile.cleanup()

    assert frame_ruleset.cleaned is True
    assert conduit_ruleset.cleaned is True
    assert spell_ruleset.cleaned is True
    assert member_ruleset.cleaned is True


def test_frame_acl_codegen_profile_requires_valid_inputs() -> None:
    """
    Verify codegen profiles reject invalid required fields.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="name cannot be empty"):
        FrameACLCodegenProfile("")

    with pytest.raises(ValueError, match="version cannot be empty"):
        FrameACLCodegenProfile("safe", version="")


def test_frame_acl_codegen_profile_create_default_matches_safe_factory() -> None:
    """
    Verify the default codegen profile is the safe profile.

    Returns:
        None.
    """
    default_profile = FrameACLCodegenProfile.create_default()
    safe_profile = FrameACLCodegenProfile.create_safe()

    assert default_profile.name == "safe"
    assert default_profile.capability_ruleset.list_rule_names() == (
        safe_profile.capability_ruleset.list_rule_names()
    )


def test_frame_acl_codegen_profile_cleanup_cascades_to_owned_rulesets() -> None:
    """
    Verify codegen-profile cleanup cascades into the owned rulesets.

    Returns:
        None.
    """
    profile = FrameACLCodegenProfile.create_permissive()
    frame_ruleset = profile.frame_ruleset
    conduit_ruleset = profile.conduit_ruleset
    spell_ruleset = profile.spell_ruleset
    capability_ruleset = profile.capability_ruleset

    profile.cleanup()

    assert frame_ruleset.cleaned is True
    assert conduit_ruleset.cleaned is True
    assert spell_ruleset.cleaned is True
    assert capability_ruleset.cleaned is True


def test_frame_acl_profile_builder_get_required_profiles_raise_for_missing_names() -> None:
    """
    Verify missing reusable profiles fail fast.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()

    with pytest.raises(KeyError, match="missing_view"):
        builder.get_required_view_profile("missing_view")

    with pytest.raises(KeyError, match="missing_codegen"):
        builder.get_required_codegen_profile("missing_codegen")


def test_frame_acl_profile_builder_create_profile_uses_named_catalog_entries() -> None:
    """
    Verify composed profiles use the requested named catalog entries.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()

    profile = builder.create_profile(
        "support",
        view_profile_name="hybrid",
        codegen_profile_name="permissive",
    )

    assert profile.view_profile.name == "hybrid"
    assert profile.codegen_profile.name == "permissive"


def test_frame_acl_profile_builder_registry_snapshots_are_detached() -> None:
    """
    Verify registry snapshot dictionaries are detached from future mutation.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()
    view_snapshot = builder.view_profiles_by_name
    codegen_snapshot = builder.codegen_profiles_by_name

    builder.register_view_profile(
        FrameACLViewProfile(
            "custom_view",
            minimum_spell_payload_type="detailed",
        )
    )
    builder.register_codegen_profile(FrameACLCodegenProfile("custom_codegen"))

    assert "custom_view" not in view_snapshot
    assert "custom_codegen" not in codegen_snapshot


def test_frame_acl_profile_builder_replacing_view_profile_cleans_old_profile() -> None:
    """
    Verify replacing a reusable view profile cleans the older object.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()
    first_profile = FrameACLViewProfile(
        "custom_view",
        minimum_spell_payload_type="detailed",
    )
    second_profile = FrameACLViewProfile(
        "custom_view",
        minimum_spell_payload_type="detailed",
    )

    builder.register_view_profile(first_profile)
    builder.register_view_profile(second_profile)

    assert first_profile.cleaned is True
    assert builder.get_required_view_profile("custom_view") is second_profile


def test_frame_acl_profile_builder_replacing_codegen_profile_cleans_old_profile() -> None:
    """
    Verify replacing a reusable codegen profile cleans the older object.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()
    first_profile = FrameACLCodegenProfile("custom_codegen")
    second_profile = FrameACLCodegenProfile("custom_codegen")

    builder.register_codegen_profile(first_profile)
    builder.register_codegen_profile(second_profile)

    assert first_profile.cleaned is True
    assert (
        builder.get_required_codegen_profile("custom_codegen")
        is second_profile
    )


def test_frame_acl_profile_builder_create_profile_preserves_custom_overrides() -> None:
    """
    Verify composed profiles keep the supplied override rulesets.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()
    view_override = FrameACLRuleSet("view_override")
    codegen_override = FrameACLRuleSet("codegen_override")

    profile = builder.create_profile(
        "support",
        view_override_ruleset=view_override,
        codegen_override_ruleset=codegen_override,
    )

    assert profile.view_override_ruleset is view_override
    assert profile.codegen_override_ruleset is codegen_override


def test_frame_acl_profile_builder_cleanup_cascades_to_owned_profiles() -> None:
    """
    Verify builder cleanup cascades into the owned reusable profiles.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()
    safe_view = builder.get_required_view_profile("safe")
    safe_codegen = builder.get_required_codegen_profile("safe")

    builder.cleanup()

    assert builder.cleaned is True
    assert safe_view.cleaned is True
    assert safe_codegen.cleaned is True
    assert builder._view_profiles_by_name is None
    assert builder._codegen_profiles_by_name is None

