from melder.aether.nexus.acl.builder.frame_acl_command_builder import (
    FrameACLCommandBuilder,
)
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer


def _build_container() -> FrameACLContainer:
    return FrameACLContainer("ops")


def test_frame_acl_builder_begin_command_change_returns_fluent_builder() -> None:
    """
    Verify the generic builder can open a command draft and return the fluent builder.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_command_change(reason="fluent")

    assert isinstance(builder, FrameACLCommandBuilder)
    assert container.frame_acl_builder.change_active is True
    assert container.frame_acl_builder.draft_family_name == "command"


def test_frame_acl_command_builder_can_set_profiles_and_commit() -> None:
    """
    Verify the fluent builder can switch command profiles and commit the draft.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_command_change(reason="fluent")

    next_configuration = (
        builder
        .use_profile("hybrid")
        .use_precision_profile("precision")
        .commit_change()
    )

    assert next_configuration.profile_name == "hybrid"
    assert next_configuration.precision_profile_name == "precision"
    assert container.get_current_command_configuration().configuration_id == (
        next_configuration.configuration_id
    )


def test_frame_acl_command_builder_can_author_enablement_and_member_rules() -> None:
    """
    Verify the fluent builder can author command-family enablement and member rules.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_command_change(reason="fluent")

    next_configuration = (
        builder
        .use_profile("permissive")
        .allow_frame_enable()
        .allow_conduit_enable()
        .allow_spell_enable()
        .allow_member_invoke_method()
        .allow_member_write_attribute()
        .deny_member_dunder_access()
        .commit_change()
    )

    frame_rules = next_configuration.frame_override_ruleset.rules_by_name
    conduit_rules = next_configuration.conduit_override_ruleset.rules_by_name
    spell_rules = next_configuration.spell_override_ruleset.rules_by_name
    member_rules = next_configuration.member_override_ruleset.rules_by_name

    assert frame_rules["enable"].effect == "allow"
    assert conduit_rules["enable"].effect == "allow"
    assert spell_rules["enable"].effect == "allow"
    assert member_rules["invoke_method"].effect == "allow"
    assert member_rules["write_attribute"].effect == "allow"
    assert member_rules["dunder_access"].effect == "deny"


def test_frame_acl_command_builder_remove_member_rule_is_fluent() -> None:
    """
    Verify member rules can be removed after being added.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_command_change(reason="fluent")

    next_configuration = (
        builder
        .use_profile("permissive")
        .allow_member_write_attribute()
        .remove_member_rule("write_attribute")
        .commit_change()
    )

    assert "write_attribute" not in (
        next_configuration.member_override_ruleset.rules_by_name
    )


def test_frame_acl_command_builder_discard_clears_active_change() -> None:
    """
    Verify discarding through the fluent builder clears the generic draft session.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_command_change(reason="fluent")

    builder.discard_change()

    assert container.frame_acl_builder.change_active is False
    assert container.frame_acl_builder.draft_family_name is None
