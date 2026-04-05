import pytest

from melder.aether.nexus.acl.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_configuration_chain import (
    FrameACLConfigurationChain,
)
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer


def _make_locked_configuration(
        frame_name: str,
        *,
        reason: str,
        json_payload: str,
) -> FrameACLConfiguration:
    """
    Build one locked configuration node for matrix-driven chain tests.

    Args:
        frame_name:
            Owning frame name.
        reason:
            Creation reason recorded on the configuration node.
        json_payload:
            JSON payload string for the configuration contents.

    Returns:
        FrameACLConfiguration:
            Locked configuration node ready for chain insertion.
    """
    configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name=frame_name,
        json_configuration_string=json_payload,
        source_configuration_id=None,
        previous_configuration_id=None,
        reason=reason,
        locked=False,
    )
    configuration.finalize()
    return configuration


@pytest.mark.parametrize(
    "history_limit",
    [0, -1, None, "3", 1.5],
)
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
        FrameACLConfigurationChain("ops", history_limit=history_limit)


@pytest.mark.parametrize(
    "limit",
    [0, -1, None, "2", 1.2],
)
def test_chain_list_rejects_invalid_limit_values(limit: object) -> None:
    """
    Verify list_configurations rejects invalid limit values.

    Args:
        limit:
            Candidate list limit.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")

    if limit is None:
        assert chain.list_configurations(limit=limit) == [chain.get_current_configuration()]
        return

    with pytest.raises(ValueError, match="limit must be an integer >= 1"):
        chain.list_configurations(limit=limit)


@pytest.mark.parametrize(
    "configuration_id, expected",
    [
        ("__current__", True),
        ("__head__", True),
        ("missing", False),
        ("missing-2", False),
    ],
)
def test_chain_has_configuration_reports_known_and_unknown_ids(
        configuration_id: str,
        expected: bool,
) -> None:
    """
    Verify has_configuration answers correctly for known and unknown ids.

    Args:
        configuration_id:
            Target configuration id or one of the local test sentinels.
        expected:
            Expected existence result.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")
    second = _make_locked_configuration(
        "ops",
        reason="second",
        json_payload='{"frame_name":"ops","view_acl":{"v":1},"codegen_acl":{}}',
    )
    chain.insert_head_configuration(second, select_as_current=True)

    if configuration_id == "__current__":
        configuration_id = chain.current_configuration_id
    elif configuration_id == "__head__":
        configuration_id = chain.head_configuration_id

    assert chain.has_configuration(configuration_id) is expected


@pytest.mark.parametrize(
    "configuration_id",
    ["missing", "missing-2", "unknown", "unknown-2"],
)
def test_chain_get_configuration_raises_for_unknown_ids(
        configuration_id: str,
) -> None:
    """
    Verify get_configuration fails fast for unknown ids.

    Args:
        configuration_id:
            Unknown configuration id to resolve.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")

    with pytest.raises(KeyError, match=configuration_id):
        chain.get_configuration(configuration_id)


@pytest.mark.parametrize(
    "candidate",
    [None, 123, "ops", object(), []],
)
def test_chain_insert_rejects_invalid_candidate_types(candidate: object) -> None:
    """
    Verify head insertion rejects non-configuration objects.

    Args:
        candidate:
            Candidate object to insert.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")

    with pytest.raises(TypeError, match="FrameACLConfiguration"):
        chain.insert_head_configuration(candidate, select_as_current=True)


@pytest.mark.parametrize(
    "other_frame_name",
    ["finance", "ops_2", "OPS", "default"],
)
def test_chain_insert_rejects_wrong_frame_names(other_frame_name: str) -> None:
    """
    Verify insertion rejects locked nodes that target another frame.

    Args:
        other_frame_name:
            Wrong frame name for the candidate node.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")
    configuration = _make_locked_configuration(
        other_frame_name,
        reason="wrong-frame",
        json_payload='{"frame_name":"placeholder","view_acl":{},"codegen_acl":{}}',
    )

    with pytest.raises(ValueError, match="expected 'ops'"):
        chain.insert_head_configuration(configuration, select_as_current=True)


@pytest.mark.parametrize(
    "json_payload",
    [
        '{"frame_name":"ops","view_acl":{},"codegen_acl":{}}',
        '{"frame_name":"ops","view_acl":{"visible":true},"codegen_acl":{}}',
        '{"frame_name":"ops","view_acl":{},"codegen_acl":{"allowed":true}}',
        '{"frame_name":"ops","view_acl":{"spell":"one"},"codegen_acl":{"spell":"two"}}',
    ],
)
def test_chain_create_new_from_acl_configuration_preserves_source_payload(
        json_payload: str,
) -> None:
    """
    Verify create_new_from_acl_configuration preserves source payload and source id.

    Args:
        json_payload:
            Source payload string used to create the committed source node.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")
    source = _make_locked_configuration(
        "ops",
        reason="source",
        json_payload=json_payload,
    )
    chain.insert_head_configuration(source, select_as_current=True)

    copied = chain.create_new_from_acl_configuration(
        source.configuration_id,
        reason="copy",
    )

    assert copied.frame_name == "ops"
    assert copied.source_configuration_id == source.configuration_id
    assert copied.previous_configuration_id is None
    assert copied.locked is False
    assert copied.to_json_string() == source.to_json_string()


@pytest.mark.parametrize(
    "select_as_current, json_payload",
    [
        (True, '{"frame_name":"ops","view_acl":{"v":1},"codegen_acl":{}}'),
        (False, '{"frame_name":"ops","view_acl":{"v":2},"codegen_acl":{}}'),
        (True, '{"frame_name":"ops","view_acl":{},"codegen_acl":{"v":3}}'),
        (False, '{"frame_name":"ops","view_acl":{"v":4},"codegen_acl":{"v":4}}'),
    ],
)
def test_chain_insert_head_updates_head_and_current_semantics(
        select_as_current: bool,
        json_payload: str,
) -> None:
    """
    Verify head insertion updates previous/head/current state correctly.

    Args:
        select_as_current:
            Whether the new node should also become current.
        json_payload:
            Payload for the inserted node.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops")
    original = chain.get_current_configuration()
    configuration = _make_locked_configuration(
        "ops",
        reason="insert",
        json_payload=json_payload,
    )

    inserted = chain.insert_head_configuration(
        configuration,
        select_as_current=select_as_current,
    )

    assert inserted.previous_configuration_id == original.configuration_id
    assert chain.head_configuration_id == inserted.configuration_id
    expected_current_id = inserted.configuration_id if select_as_current else original.configuration_id
    assert chain.current_configuration_id == expected_current_id


@pytest.mark.parametrize(
    "limit, expected_count",
    [(None, 4), (1, 1), (2, 2), (3, 3)],
)
def test_chain_list_limit_returns_expected_counts(
        limit: int | None,
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
    chain = FrameACLConfigurationChain("ops")
    for marker in ("1", "2", "3"):
        chain.insert_head_configuration(
            _make_locked_configuration(
                "ops",
                reason="cfg-{0}".format(marker),
                json_payload='{{"frame_name":"ops","view_acl":{{"v":"{0}"}},"codegen_acl":{{}}}}'.format(marker),
            ),
            select_as_current=True,
        )

    listed = chain.list_configurations(limit=limit)

    assert len(listed) == expected_count
    assert listed[0].configuration_id == chain.head_configuration_id


@pytest.mark.parametrize(
    "history_limit",
    [2, 3, 4, 5],
)
def test_chain_tail_trim_enforces_limit_when_current_tracks_head(
        history_limit: int,
) -> None:
    """
    Verify trim_tail enforces the history limit when current follows head.

    Args:
        history_limit:
            Retained history limit for the chain.

    Returns:
        None.
    """
    chain = FrameACLConfigurationChain("ops", history_limit=history_limit)
    original = chain.get_current_configuration()
    original_configuration_id = original.configuration_id

    for marker in range(history_limit + 2):
        chain.insert_head_configuration(
            _make_locked_configuration(
                "ops",
                reason="cfg-{0}".format(marker),
                json_payload='{{"frame_name":"ops","view_acl":{{"v":{0}}},"codegen_acl":{{}}}}'.format(marker),
            ),
            select_as_current=True,
        )

    assert chain.count_configurations() == history_limit
    assert original.cleaned is True
    assert original_configuration_id not in chain.list_configuration_ids()


@pytest.mark.parametrize(
    "install_count",
    [1, 2, 3],
)
def test_container_history_excludes_current_after_installs(install_count: int) -> None:
    """
    Verify the container history view excludes the current configuration.

    Args:
        install_count:
            Number of successive installs to perform.

    Returns:
        None.
    """
    container = FrameACLContainer("ops", history_limit=10)

    for marker in range(install_count):
        container.install_configuration(
            _make_locked_configuration(
                "ops",
                reason="cfg-{0}".format(marker),
                json_payload='{{"frame_name":"ops","view_acl":{{"v":{0}}},"codegen_acl":{{}}}}'.format(marker),
            )
        )

    history = container.frame_acl_history

    assert container.frame_acl_configuration not in history
    assert len(history) == install_count


@pytest.mark.parametrize(
    "json_payload",
    [
        '{"frame_name":"ops","view_acl":{"visible":true},"codegen_acl":{}}',
        '{"frame_name":"ops","view_acl":{},"codegen_acl":{"allowed":true}}',
        '{"frame_name":"ops","view_acl":{"one":1},"codegen_acl":{"two":2}}',
        '{"frame_name":"ops","view_acl":{"spell":"alpha"},"codegen_acl":{"spell":"beta"}}',
    ],
)
def test_builder_commit_round_trip_for_multiple_payloads(
        json_payload: str,
) -> None:
    """
    Verify the builder can commit a range of JSON payloads into the chain.

    Args:
        json_payload:
            Draft payload to commit.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    previous_configuration = container.frame_acl_configuration
    builder = container.frame_acl_builder

    builder.begin_change()
    builder.load_json_configuration_string(json_payload)
    next_configuration = builder.commit_change()

    assert next_configuration.locked is True
    assert next_configuration.source_configuration_id == previous_configuration.configuration_id
    assert container.frame_acl_configuration is next_configuration
    assert builder.change_active is False
