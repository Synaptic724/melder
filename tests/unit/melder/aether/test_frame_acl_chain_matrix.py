import json
from typing import Optional

import pytest

from melder.aether.nexus.acl.frame_acl_configuration_chain import (
    FrameACLConfigurationChain,
)
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer
from melder.aether.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)


def _make_locked_view_configuration(
        *,
        profile_name: str = "safe",
        marker: str = "default",
        reason: str = "test",
) -> FrameACLViewConfiguration:
    """
    Build one locked view configuration revision for family-chain matrix tests.

    Returns:
        FrameACLViewConfiguration: Locked view configuration revision.
    """
    payload = {
        "profile_name": profile_name,
        "profile_version": "0.0.1",
        "required_nexus_label": "default",
        "required_nexus_version": "0.0.1",
        "minimum_spell_payload_type": "general",
        "minimum_spell_payload_version": "0.0.1",
        "frame_override_ruleset": {
            "name": "frame_override_{0}".format(marker),
            "rules": [],
        },
        "conduit_override_ruleset": {
            "name": "conduit_override",
            "rules": [],
        },
        "spell_override_ruleset": {
            "name": "spell_override",
            "rules": [],
        },
        "member_override_ruleset": {
            "name": "member_override",
            "rules": [],
        },
    }
    return FrameACLViewConfiguration.from_json_dict(
        payload,
        reason=reason,
        locked=True,
    )


@pytest.mark.parametrize("history_limit", [0, -1, None, "3", 1.5])
def test_chain_rejects_invalid_history_limit_values(history_limit: object) -> None:
    """
    Verify construction rejects invalid history-limit values.

    Args:
        history_limit:
            Candidate history limit.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="history_limit must be an integer >= 1"):
        FrameACLConfigurationChain(
            family_name="view",
            contract_name="default",
            default_configuration=_make_locked_view_configuration(),
            history_limit=history_limit,
        )


@pytest.mark.parametrize("limit", [0, -1, "2", 1.2])
def test_chain_list_rejects_invalid_limit_values(limit: object) -> None:
    """
    Verify list_configurations rejects invalid limit values.

    Args:
        limit:
            Candidate list limit.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain(
        family_name="view",
        contract_name="default",
        default_configuration=_make_locked_view_configuration(),
    )

    with pytest.raises(ValueError, match="limit must be an integer >= 1"):
        chain.list_configurations(limit=limit)


@pytest.mark.parametrize(
    "select_as_current, expected_current_is_new",
    [(True, True), (False, False)],
)
def test_chain_insert_head_updates_head_and_current_semantics(
        select_as_current: bool,
        expected_current_is_new: bool,
) -> None:
    """
    Verify head insertion updates head/current semantics under the current API.

    Args:
        select_as_current:
            Whether the new node should also become current.
        expected_current_is_new:
            Whether current should move to the new node.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain(
        family_name="view",
        contract_name="default",
        default_configuration=_make_locked_view_configuration(marker="v1"),
    )
    original = chain.get_current_configuration()
    configuration = _make_locked_view_configuration(marker="v2")

    inserted = chain.insert_head_configuration(
        configuration,
        select_as_current=select_as_current,
    )

    assert chain.head_configuration_id == inserted.configuration_id
    assert inserted.previous_configuration_id == original.configuration_id
    if expected_current_is_new:
        assert chain.current_configuration_id == inserted.configuration_id
    else:
        assert chain.current_configuration_id == original.configuration_id


def test_chain_create_new_from_acl_configuration_preserves_source_payload() -> None:
    """
    Verify create-new copies payload from an existing family-chain node.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain(
        family_name="view",
        contract_name="default",
        default_configuration=_make_locked_view_configuration(marker="v1"),
    )
    current = chain.get_current_configuration()

    copied = chain.create_new_from_acl_configuration(
        current.configuration_id,
        reason="copy",
    )

    assert copied.source_configuration_id == current.configuration_id
    assert copied.previous_configuration_id is None
    assert copied.locked is False
    assert copied.to_json_dict() == current.to_json_dict()


@pytest.mark.parametrize(
    "limit, expected_count",
    [(None, 4), (1, 1), (2, 2), (3, 3)],
)
def test_chain_list_limit_returns_expected_counts(
        limit: Optional[int],
        expected_count: int,
) -> None:
    """
    Verify listing preserves newest-first order and honors the optional limit.

    Args:
        limit:
            Optional list limit.
        expected_count:
            Expected result size.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain(
        family_name="view",
        contract_name="default",
        default_configuration=_make_locked_view_configuration(marker="v1"),
    )
    for marker in ("2", "3", "4"):
        chain.insert_head_configuration(
            _make_locked_view_configuration(marker=marker),
            select_as_current=True,
        )

    listed = chain.list_configurations(limit=limit)

    assert len(listed) == expected_count
    assert listed[0].configuration_id == chain.head_configuration_id


def test_container_view_history_is_read_from_family_chain() -> None:
    """
    Verify view history is now exposed through the family-chain APIs.

    Returns:
        None.
    """
    container = FrameACLContainer("ops", history_limit=10)
    current_view = container.get_current_view_configuration()
    next_view = FrameACLViewConfiguration.create_new_from_configuration(
        current_view,
        reason="matrix",
    )
    next_view.finalize()

    inserted = container.insert_head_view_configuration(
        next_view,
        select_as_current=True,
    )
    listed = container.list_view_configurations()

    assert listed[0] is inserted
    assert listed[1].configuration_id == current_view.configuration_id
    assert container.frame_acl_configuration.view_configuration.profile_name == (
        inserted.profile_name
    )


@pytest.mark.parametrize("profile_name", ["safe", "hybrid"])
def test_builder_view_family_round_trip_for_multiple_payloads(
        profile_name: str,
) -> None:
    """
    Verify the builder can round-trip current-family JSON payloads.

    Args:
        profile_name:
            View profile name for the draft payload.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder

    builder.begin_change("view")
    builder.load_json_configuration_string(
        json.dumps(
                {
                    "profile_name": profile_name,
                    "profile_version": "0.0.1",
                    "required_nexus_label": "default",
                    "required_nexus_version": "0.0.1",
                    "minimum_spell_payload_type": "general",
                    "minimum_spell_payload_version": "0.0.1",
                    "frame_override_ruleset": {
                        "name": "frame_override",
                        "rules": [],
                },
                "conduit_override_ruleset": {
                    "name": "conduit_override",
                    "rules": [],
                },
                "spell_override_ruleset": {
                    "name": "spell_override",
                    "rules": [],
                },
                "member_override_ruleset": {
                    "name": "member_override",
                    "rules": [],
                },
            },
            sort_keys=True,
        )
    )
    next_configuration = builder.commit_change()

    assert isinstance(next_configuration, FrameACLViewConfiguration)
    assert container.get_current_view_configuration() is next_configuration
    assert next_configuration.profile_name == profile_name
    assert builder.change_active is False
