import pytest

from melder.nexus.acl.builder.frame_acl_codegen_builder import (
    FrameACLCodegenBuilder,
)
from melder.nexus.acl.frame_acl_container import FrameACLContainer


def _build_container() -> FrameACLContainer:
    return FrameACLContainer("ops")


def test_frame_acl_builder_begin_codegen_change_returns_fluent_builder() -> None:
    """
    Verify the generic builder can open a codegen draft and return the fluent builder.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_codegen_change(reason="fluent")

    assert isinstance(builder, FrameACLCodegenBuilder)
    assert container.frame_acl_builder.change_active is True
    assert container.frame_acl_builder.draft_family_name == "codegen"


def test_frame_acl_codegen_builder_can_set_profiles_and_commit() -> None:
    """
    Verify the fluent builder can switch profiles and commit a codegen draft.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_codegen_change(reason="fluent")

    next_configuration = (
        builder
        .use_profile("hybrid")
        .use_precision_profile("precision")
        .commit_change()
    )

    assert next_configuration.profile_name == "hybrid"
    assert next_configuration.precision_profile_name == "precision"
    assert container.get_current_codegen_configuration().configuration_id == (
        next_configuration.configuration_id
    )


def test_frame_acl_codegen_builder_can_merge_import_and_builtin_rules() -> None:
    """
    Verify the fluent builder merges import and builtin values into stable rules.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_codegen_change(reason="fluent")

    next_configuration = (
        builder
        .use_profile("permissive")
        .enable_imports()
        .allow_import_module_roots("json", "math")
        .allow_import_module_roots("inspect")
        .deny_import_module_roots("subprocess")
        .deny_builtin_names("eval", "exec")
        .deny_builtin_names("compile")
        .commit_change()
    )

    capability_rules = next_configuration.capability_override_ruleset.rules_by_name

    assert capability_rules["builder_enable_imports"].effect == "allow"
    assert capability_rules["builder_allow_import_modules"].conditions["module_roots"] == (
        "json",
        "math",
        "inspect",
    )
    assert capability_rules["builder_deny_import_modules"].conditions["module_roots"] == (
        "subprocess",
    )
    assert capability_rules["builder_deny_builtin_names"].conditions["builtin_names"] == (
        "eval",
        "exec",
        "compile",
    )


def test_frame_acl_codegen_builder_can_toggle_meta_and_recursive_rules() -> None:
    """
    Verify the fluent builder can author reflection, dunder, and recursive posture.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_codegen_change(reason="fluent")

    next_configuration = (
        builder
        .use_profile("full_access")
        .allow_unsafe_reflection()
        .allow_dunder_access()
        .allow_recursive_codegen()
        .commit_change()
    )

    capability_rules = next_configuration.capability_override_ruleset.rules_by_name

    assert capability_rules["builder_unsafe_reflection"].effect == "allow"
    assert capability_rules["builder_dunder_access"].effect == "allow"
    assert capability_rules["builder_recursive_codegen"].effect == "allow"


def test_frame_acl_codegen_builder_discard_clears_active_change() -> None:
    """
    Verify discarding through the fluent builder clears the generic draft session.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_codegen_change(reason="fluent")

    builder.discard_change()

    assert container.frame_acl_builder.change_active is False
    assert container.frame_acl_builder.draft_family_name is None


def test_frame_acl_codegen_builder_rejects_empty_value_batches() -> None:
    """
    Verify merge helpers reject empty or invalid value batches.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_codegen_change(reason="fluent")

    with pytest.raises(ValueError, match="values cannot be empty"):
        builder.allow_import_module_roots()

    with pytest.raises(ValueError, match="module_roots values must be non-empty strings"):
        builder.allow_import_module_roots("")


def test_frame_acl_codegen_builder_remove_capability_rule_is_fluent() -> None:
    """
    Verify capability rules can be removed after being added.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_codegen_change(reason="fluent")

    next_configuration = (
        builder
        .allow_recursive_codegen()
        .remove_capability_rule("builder_recursive_codegen")
        .commit_change()
    )

    assert "builder_recursive_codegen" not in (
        next_configuration.capability_override_ruleset.rules_by_name
    )


def test_frame_acl_codegen_builder_merges_materialize_module_roots() -> None:
    """
    Verify (D-20) the fluent builder merges generation-namespace roots into stable `materialize_modules` rules that
    the validator accepts at commit.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_codegen_change(reason="generation")

    next_configuration = (
        builder
        .use_profile("hybrid")
        .allow_materialize_module_roots("codegen_generated")
        .allow_materialize_module_roots("tools.gen")
        .deny_materialize_module_roots("codegen_generated.secret")
        .commit_change()
    )

    rules = next_configuration.capability_override_ruleset.rules_by_name

    assert rules["builder_allow_materialize_modules"].operation == "materialize_modules"
    assert rules["builder_allow_materialize_modules"].effect == "allow"
    assert rules["builder_allow_materialize_modules"].conditions["module_roots"] == (
        "codegen_generated",
        "tools.gen",
    )
    assert rules["builder_deny_materialize_modules"].effect == "deny"
    assert rules["builder_deny_materialize_modules"].conditions["module_roots"] == (
        "codegen_generated.secret",
    )


def test_frame_acl_validator_rejects_malformed_materialize_module_rules() -> None:
    """
    Verify (D-20) a `materialize_modules` rule must declare non-empty, dotted-identifier-legal `module_roots`.

    Returns:
        None.
    """
    from melder.nexus.acl.configurations.profiles.rules.frame_acl_rule import FrameACLRule
    from melder.nexus.acl.validator.frame_acl_validator import FrameACLValidator

    for conditions in ({}, {"module_roots": ()}, {"module_roots": ("",)}, {"module_roots": ("not-legal",)}):
        rule = FrameACLRule(
            rule_name="generation",
            operation="materialize_modules",
            effect="allow",
            conditions=conditions,
        )
        with pytest.raises(ValueError, match="materialize"):
            FrameACLValidator._validate_materialize_module_rule_conditions(rule, "capability")
