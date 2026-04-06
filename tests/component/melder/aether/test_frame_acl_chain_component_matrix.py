import json

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.nexus import Nexus


@pytest.fixture(autouse=True)
def fresh_component_singletons() -> None:
    """
    Reset singleton state around each component test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()


def _make_locked_configuration(
        frame_name: str,
        *,
        reason: str,
        marker: str,
) -> FrameACLConfiguration:
    """
    Build one locked ACL configuration node for component tests.

    Args:
        frame_name:
            Owning frame name.
        reason:
            Creation reason.
        marker:
            Small payload marker to make the config unique.

    Returns:
        FrameACLConfiguration:
            Locked configuration node.
    """
    configuration = FrameACLConfiguration.from_json_configuration_string(
        frame_name=frame_name,
        json_configuration_string=_build_typed_json_payload(
            frame_name,
            marker=marker,
        ),
        source_configuration_id=None,
        previous_configuration_id=None,
        reason=reason,
        locked=False,
    )
    configuration.finalize()
    return configuration


def _build_typed_json_payload(
        frame_name: str,
        *,
        marker: str,
) -> str:
    """
    Build one typed ACL JSON payload for component chain tests.

    Args:
        frame_name:
            Frame name stored in the JSON payload.
        marker:
            Small marker used to vary the view payload.

    Returns:
        str:
            JSON payload string that matches the live typed ACL contract.
    """
    return json.dumps(
        {
            "frame_name": frame_name,
            "view_configuration": {
                "profile_name": "safe",
                "profile_version": "0.0.1",
                "minimum_spell_payload_type": "detailed",
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
            },
            "codegen_configuration": {
                "profile_name": "safe",
                "profile_version": "0.0.1",
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
                "capability_override_ruleset": {
                    "name": "capability_override",
                    "rules": [],
                },
            },
        },
        sort_keys=True,
    )


@pytest.mark.parametrize(
    "frame_name",
    ["ops", "finance", "analytics", "default"],
)
def test_component_descriptor_creation_provisions_container_for_frame(
        frame_name: str,
) -> None:
    """
    Verify descriptor creation also provisions the matching ACL container.

    Args:
        frame_name:
            Target frame name.

    Returns:
        None.
    """
    aether = Aether()
    nexus = Nexus(aether=aether)

    descriptor = nexus._get_or_create_frame_descriptor(frame_name)
    container = nexus._frame_acl_manager._get_required_frame_acl_container(frame_name)

    assert descriptor.frame_name == frame_name
    assert container.frame_name == frame_name
    assert container.frame_acl_configuration_chain.count_configurations() == 1


@pytest.mark.parametrize(
    "frame_name",
    ["ops", "finance", "analytics", "default"],
)
def test_component_nexus_returns_same_builder_for_repeated_frame_requests(
        frame_name: str,
) -> None:
    """
    Verify repeated Nexus builder access returns the same per-frame builder.

    Args:
        frame_name:
            Target frame name.

    Returns:
        None.
    """
    aether = Aether()
    nexus = Nexus(aether=aether)

    first_builder = nexus.get_frame_acl_builder(frame_name)
    second_builder = nexus.get_frame_acl_builder(frame_name)

    assert second_builder is first_builder


@pytest.mark.parametrize(
    "marker",
    ["alpha", "beta", "gamma", "delta"],
)
def test_component_nexus_chain_round_trip_insert_select_and_rollback(
        marker: str,
) -> None:
    """
    Verify Nexus facades can drive the full insert/select/rollback loop.

    Args:
        marker:
            Payload marker for the inserted configuration.

    Returns:
        None.
    """
    aether = Aether()
    nexus = Nexus(aether=aether)
    frame_name = "ops-{0}".format(marker)
    original = nexus.get_current_frame_acl_configuration(frame_name)
    inserted = _make_locked_configuration(
        frame_name,
        reason="insert-{0}".format(marker),
        marker=marker,
    )

    inserted = nexus.insert_head_frame_acl_configuration(
        frame_name,
        inserted,
        select_as_current=True,
    )
    selected = nexus.select_current_frame_acl_configuration(
        frame_name,
        original.configuration_id,
    )
    rolled_back = nexus.rollback_frame_acl_configuration(
        frame_name,
        inserted.configuration_id,
    )

    assert selected is original
    assert rolled_back is inserted
    assert nexus.get_current_frame_acl_configuration(frame_name) is inserted


@pytest.mark.parametrize(
    "frame_name",
    ["ops", "finance", "analytics", "default"],
)
def test_component_frame_detach_cleans_container_after_chain_growth(
        frame_name: str,
) -> None:
    """
    Verify frame-detach cleanup removes a populated ACL container.

    Args:
        frame_name:
            Target frame name.

    Returns:
        None.
    """
    aether = Aether()
    nexus = Nexus(aether=aether)
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    nexus.enable(configuration)
    frame = aether._ensure_frame(frame_name)
    nexus._get_or_create_frame_descriptor(frame_name)
    original = nexus.get_current_frame_acl_configuration(frame_name)
    inserted = _make_locked_configuration(
        frame_name,
        reason="growth",
        marker="grown",
    )
    container = nexus._frame_acl_manager._get_required_frame_acl_container(frame_name)

    nexus.insert_head_frame_acl_configuration(
        frame_name,
        inserted,
        select_as_current=True,
    )
    nexus.select_current_frame_acl_configuration(frame_name, original.configuration_id)
    frame.cleanup()

    assert container.cleaned is True
    assert frame_name not in nexus._frame_acl_manager.frame_acl_containers_by_name


@pytest.mark.parametrize(
    "left_frame_name,right_frame_name",
    [
        ("ops", "finance"),
        ("analytics", "reporting"),
        ("default", "ops"),
        ("left", "right"),
    ],
)
def test_component_frame_isolation_keeps_chains_separate(
        left_frame_name: str,
        right_frame_name: str,
) -> None:
    """
    Verify per-frame containers and chains remain isolated from each other.

    Args:
        left_frame_name:
            First frame name.
        right_frame_name:
            Second frame name.

    Returns:
        None.
    """
    aether = Aether()
    nexus = Nexus(aether=aether)

    left_current = nexus.get_current_frame_acl_configuration(left_frame_name)
    right_current = nexus.get_current_frame_acl_configuration(right_frame_name)
    left_next = _make_locked_configuration(
        left_frame_name,
        reason="left",
        marker="left",
    )
    right_next = _make_locked_configuration(
        right_frame_name,
        reason="right",
        marker="right",
    )

    nexus.insert_head_frame_acl_configuration(
        left_frame_name,
        left_next,
        select_as_current=True,
    )
    nexus.insert_head_frame_acl_configuration(
        right_frame_name,
        right_next,
        select_as_current=True,
    )

    assert nexus.get_current_frame_acl_configuration(left_frame_name) is left_next
    assert nexus.get_current_frame_acl_configuration(right_frame_name) is right_next
    assert left_current.configuration_id != right_current.configuration_id
    assert left_next.configuration_id != right_next.configuration_id

