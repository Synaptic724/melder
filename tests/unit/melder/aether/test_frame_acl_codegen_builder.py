import pytest

from melder.aether.nexus.acl.builder.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.builder.frame_acl_codegen_builder import (
    FrameACLCodegenBuilder,
)
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer


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
