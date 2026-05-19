import pytest

from melder.nexus.acl.builder.frame_acl_view_builder import (
    FrameACLViewBuilder,
)
from melder.nexus.acl.frame_acl_container import FrameACLContainer


def _build_container() -> FrameACLContainer:
    return FrameACLContainer("ops")


def test_frame_acl_builder_begin_view_change_returns_fluent_builder() -> None:
    """
    Verify the generic builder can open a view draft and return the fluent builder.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_view_change(reason="fluent")

    assert isinstance(builder, FrameACLViewBuilder)
    assert container.frame_acl_builder.change_active is True
    assert container.frame_acl_builder.draft_family_name == "view"


def test_frame_acl_view_builder_can_set_profiles_and_commit() -> None:
    """
    Verify the fluent builder can switch view profiles and commit the draft.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_view_change(reason="fluent")

    next_configuration = (
        builder
        .use_profile("hybrid")
        .use_precision_profile("precision")
        .commit_change()
    )

    assert next_configuration.profile_name == "hybrid"
    assert next_configuration.precision_profile_name == "precision"
    assert next_configuration.minimum_spell_payload_type == "detailed"
    assert container.get_current_view_configuration().configuration_id == (
        next_configuration.configuration_id
    )


def test_frame_acl_view_builder_can_author_visibility_and_member_rules() -> None:
    """
    Verify the fluent builder can author view-family visibility and member rules.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_view_change(reason="fluent")

    next_configuration = (
        builder
        .use_profile("permissive")
        .allow_conduit_policy()
        .allow_conduit_peer_links()
        .allow_spell_instance_members()
        .allow_spell_dynamic_access()
        .deny_member_pattern("__*")
        .allow_member_name("public_name", rule_name="allow_public_name")
        .commit_change()
    )

    conduit_rules = next_configuration.conduit_override_ruleset.rules_by_name
    spell_rules = next_configuration.spell_override_ruleset.rules_by_name
    member_rules = next_configuration.member_override_ruleset.rules_by_name

    assert conduit_rules["show_policy"].effect == "allow"
    assert conduit_rules["show_peer_links"].effect == "allow"
    assert spell_rules["show_instance_members"].effect == "allow"
    assert spell_rules["show_dynamic_access"].effect == "allow"
    assert member_rules["show_member"].conditions["pattern"] == "__*"
    assert member_rules["allow_public_name"].conditions["member_name"] == (
        "public_name"
    )


def test_frame_acl_view_builder_rejects_empty_member_inputs() -> None:
    """
    Verify member-name and pattern helpers reject empty values.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_view_change(reason="fluent")

    with pytest.raises(ValueError, match="member_name cannot be empty"):
        builder.allow_member_name("")

    with pytest.raises(ValueError, match="pattern cannot be empty"):
        builder.deny_member_pattern("")


def test_frame_acl_view_builder_discard_clears_active_change() -> None:
    """
    Verify discarding through the fluent builder clears the generic draft session.

    Returns:
        None.
    """
    container = _build_container()
    builder = container.frame_acl_builder.begin_view_change(reason="fluent")

    builder.discard_change()

    assert container.frame_acl_builder.change_active is False
    assert container.frame_acl_builder.draft_family_name is None
