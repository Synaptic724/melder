import json
from typing import Any, Dict, List

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.rift_space.command_system.command_system import (
    CommandSystem,
)
from melder.spellbook.spellbook import Spellbook
from tests.integration.melder.aether.rift.capability_rift_json_testbench_support import (
    CapabilityRiftJsonBench,
)


def _reset_runtime_singletons() -> None:
    """
    Reset the singleton runtime surfaces used by the capability testbench.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    CommandSystem._aether = aether


def _build_capability_request_matrix() -> List[Dict[str, object]]:
    """
    Build the capability single-request scenario matrix.

    Returns:
        List[Dict[str, object]]: Capability request scenarios.
    """
    operations = (
        {
            "name": "command_list_supported_methods",
            "request": {"surface": "command", "method": "list_supported_command_methods"},
            "kind": "supported_methods",
        },
        {
            "name": "command_list_conduit_ids",
            "request": {
                "surface": "command",
                "method": "list_conduit_ids",
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "conduit_ids",
        },
        {
            "name": "command_list_conduit_names",
            "request": {
                "surface": "command",
                "method": "list_conduit_names",
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "conduit_names",
        },
        {
            "name": "command_count_conduits",
            "request": {
                "surface": "command",
                "method": "count_conduits",
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "conduit_count",
        },
        {
            "name": "command_find_conduit_id_by_name",
            "request": {
                "surface": "command",
                "method": "find_conduit_id_by_name",
                "args": ["@manifest.conduits.left.name"],
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "find_left_id",
        },
        {
            "name": "command_get_conduit_by_id",
            "request": {
                "surface": "command",
                "method": "get_conduit_by_id",
                "args": ["@manifest.conduits.left.id"],
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "left_conduit_object",
        },
        {
            "name": "command_get_conduit_by_name",
            "request": {
                "surface": "command",
                "method": "get_conduit_by_name",
                "args": ["@manifest.conduits.left.name"],
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "left_conduit_object",
        },
        {
            "name": "command_get_spell_by_index",
            "request": {
                "surface": "command",
                "method": "get_spell_object_by_index_id",
                "args": ["@manifest.spell.spell_index_id"],
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "spell_metadata_object",
        },
        {
            "name": "command_get_spell_by_source",
            "request": {
                "surface": "command",
                "method": "get_spell_object_by_source_id",
                "args": ["@manifest.spell.source_id"],
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "spell_metadata_object",
        },
        {
            "name": "command_create_lesser_conduit",
            "request": {
                "surface": "command",
                "method": "create_lesser_conduit",
                "args": ["@manifest.conduits.left.id"],
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "created_lesser",
        },
        {
            "name": "command_get_conduit_cloud",
            "request": {
                "surface": "command",
                "method": "get_conduit_cloud",
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "cloud_object",
        },
        {
            "name": "cloud_count_conduits",
            "request": {
                "surface": "cloud",
                "method": "count_conduits",
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "cloud_count",
        },
        {
            "name": "cloud_list_conduit_names",
            "request": {
                "surface": "cloud",
                "method": "list_conduit_names",
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "cloud_names",
        },
    )
    scenarios: List[Dict[str, object]] = []
    for frame_mode in ("automatic", "dynamic"):
        for operation in operations:
            scenarios.append(
                {
                    "name": "{0}_{1}".format(frame_mode, operation["name"]),
                    "frame_mode": frame_mode,
                    "request_json": json.dumps(operation["request"]),
                    "kind": operation["kind"],
                }
            )
    return scenarios


def _build_capability_turn_script_matrix() -> List[Dict[str, object]]:
    """
    Build the capability multistep turn-script matrix.

    Returns:
        List[Dict[str, object]]: Capability turn-script scenarios.
    """
    scenarios: List[Dict[str, object]] = []
    for index in range(10):
        cluster_name = "cluster_{0}".format(index)
        scenarios.append(
            {
                "name": "dynamic_cluster_cycle_{0}".format(index),
                "frame_mode": "dynamic",
                "script_json": json.dumps(
                    {
                        "turns": [
                            {
                                "surface": "command",
                                "method": "create_cluster",
                                "args": [
                                    "@manifest.conduits.left.id",
                                    cluster_name,
                                ],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                            },
                            {
                                "surface": "command",
                                "method": "join_cluster",
                                "args": [
                                    "@manifest.conduits.left.id",
                                    cluster_name,
                                ],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                            },
                            {
                                "surface": "command",
                                "method": "list_clusters",
                                "args": ["@manifest.conduits.left.id"],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "joined_clusters",
                            },
                            {
                                "surface": "command",
                                "method": "leave_cluster",
                                "args": [
                                    "@manifest.conduits.left.id",
                                    cluster_name,
                                ],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                            },
                            {
                                "surface": "command",
                                "method": "list_clusters",
                                "args": ["@manifest.conduits.left.id"],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "after_leave",
                            },
                        ]
                    }
                ),
                "kind": "cluster_cycle",
                "cluster_name": cluster_name,
            }
        )
        scenarios.append(
            {
                "name": "dynamic_link_cycle_{0}".format(index),
                "frame_mode": "dynamic",
                "script_json": json.dumps(
                    {
                        "turns": [
                            {
                                "surface": "command",
                                "method": "link_conduits",
                                "args": [
                                    "@manifest.conduits.left.id",
                                    "@manifest.conduits.right.id",
                                ],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "linked",
                            },
                            {
                                "surface": "command",
                                "method": "get_links",
                                "args": ["@manifest.conduits.left.id"],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "links_after_link",
                            },
                            {
                                "surface": "command",
                                "method": "sever_link",
                                "args": [
                                    "@manifest.conduits.left.id",
                                    "@manifest.conduits.right.id",
                                ],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "severed",
                            },
                            {
                                "surface": "command",
                                "method": "get_links",
                                "args": ["@manifest.conduits.left.id"],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "links_after_sever",
                            },
                            {
                                "surface": "cloud",
                                "method": "count_conduits",
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "cloud_count",
                            },
                        ]
                    }
                ),
                "kind": "link_cycle",
            }
        )
    for index in range(5):
        cluster_name = "auto_cluster_{0}".format(index)
        scenarios.append(
            {
                "name": "automatic_lower_floor_{0}".format(index),
                "frame_mode": "automatic",
                "cluster_name": cluster_name,
                "script_json": json.dumps(
                    {
                        "turns": [
                            {
                                "surface": "command",
                                "method": "create_lesser_conduit",
                                "args": ["@manifest.conduits.left.id"],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "created_lesser",
                            },
                            {
                                "surface": "command",
                                "method": "create_cluster",
                                "args": [
                                    "@manifest.conduits.left.id",
                                    cluster_name,
                                ],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                            },
                            {
                                "surface": "command",
                                "method": "join_cluster",
                                "args": [
                                    "@manifest.conduits.left.id",
                                    cluster_name,
                                ],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                            },
                            {
                                "surface": "command",
                                "method": "list_clusters",
                                "args": ["@manifest.conduits.left.id"],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "joined_clusters",
                            },
                            {
                                "surface": "command",
                                "method": "link_conduits",
                                "args": [
                                    "@manifest.conduits.left.id",
                                    "@manifest.conduits.right.id",
                                ],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "expect_error_contains": "Dynamic environment is not enabled",
                                "expect_error_type": "RuntimeError",
                                "save_as": "link_error",
                            },
                        ]
                    }
                ),
                "kind": "automatic_lower_floor",
            }
        )
    return scenarios


def _assert_capability_request_result(
        bench: CapabilityRiftJsonBench,
        scenario: Dict[str, object],
        result: Any,
) -> None:
    """
    Assert one capability single-request result.

    Args:
        bench:
            Active capability bench.
        scenario:
            Request scenario metadata.
        result:
            Actual request result.

    Returns:
        None.
    """
    kind = scenario["kind"]
    if kind == "supported_methods":
        assert "get_conduit_cloud" in result
        assert "create_lesser_conduit" in result
        assert "create_cluster" in result
        assert "link_conduits" in result
        return
    if kind == "conduit_ids":
        assert result == (
            bench.manifest["conduits"]["left"]["id"],
            bench.manifest["conduits"]["right"]["id"],
            bench.manifest["conduits"]["initial_lesser"]["id"],
        )
        return
    if kind == "conduit_names":
        assert result == (
            bench.manifest["conduits"]["left"]["name"],
            bench.manifest["conduits"]["right"]["name"],
        )
        return
    if kind == "conduit_count":
        assert result == 3
        return
    if kind == "find_left_id":
        assert result == bench.manifest["conduits"]["left"]["id"]
        return
    if kind == "left_conduit_object":
        assert result.id == bench.manifest["conduits"]["left"]["id"]
        assert result.name == bench.manifest["conduits"]["left"]["name"]
        return
    if kind == "spell_metadata_object":
        assert result.spell_id == bench.manifest["spell"]["spell_id"]
        assert result.spell_name == bench.manifest["spell"]["spell_name"]
        return
    if kind == "created_lesser":
        assert result.id != bench.manifest["conduits"]["left"]["id"]
        return
    if kind == "cloud_object":
        expected_count = 2 if bench.dynamic_frame else 0
        assert result.count_conduits() == expected_count
        return
    if kind == "cloud_count":
        expected_count = 2 if bench.dynamic_frame else 0
        assert result == expected_count
        return
    if kind == "cloud_names":
        if bench.dynamic_frame:
            assert result == (
                bench.manifest["conduits"]["left"]["name"],
                bench.manifest["conduits"]["right"]["name"],
            )
        else:
            assert result == tuple()
        return
    raise AssertionError(kind)


def _assert_capability_turn_script_result(
        bench: CapabilityRiftJsonBench,
        scenario: Dict[str, object],
        saved_results: Dict[str, Any],
) -> None:
    """
    Assert one capability multistep turn-script result.

    Args:
        bench:
            Active capability bench.
        scenario:
            Turn-script scenario metadata.
        saved_results:
            Saved results from the script.

    Returns:
        None.
    """
    kind = scenario["kind"]
    if kind == "cluster_cycle":
        assert saved_results["joined_clusters"] == (scenario["cluster_name"],)
        assert saved_results["after_leave"] == tuple()
        return
    if kind == "link_cycle":
        assert saved_results["linked"] is True
        assert len(saved_results["links_after_link"]) == 1
        assert (
            saved_results["links_after_link"][0].id
            == bench.manifest["conduits"]["right"]["id"]
        )
        assert saved_results["severed"] is True
        assert saved_results["links_after_sever"] == tuple()
        assert saved_results["cloud_count"] == 2
        return
    if kind == "automatic_lower_floor":
        assert (
            saved_results["created_lesser"].id
            != bench.manifest["conduits"]["left"]["id"]
        )
        assert saved_results["joined_clusters"] == (scenario["cluster_name"],)
        assert saved_results["link_error"]["error_type"] == "RuntimeError"
        return
    raise AssertionError(kind)


@pytest.fixture(autouse=True)
def _reset_singletons_per_test() -> None:
    """
    Reset singleton runtime surfaces before and after each capability test.

    Returns:
        None.
    """
    _reset_runtime_singletons()
    yield
    _reset_runtime_singletons()


@pytest.mark.parametrize(
    "scenario",
    _build_capability_request_matrix(),
    ids=lambda scenario: scenario["name"],
)
def test_capability_rift_json_request_matrix(
        scenario: Dict[str, object],
) -> None:
    """
    Verify capability-room single-request JSON scenarios.

    Args:
        scenario:
            Parametrized request scenario.

    Returns:
        None.
    """
    bench = CapabilityRiftJsonBench(
        frame_name="ops_capability_json",
        dynamic_frame=scenario["frame_mode"] == "dynamic",
    )
    try:
        result = bench.dispatch_json(scenario["request_json"])
        _assert_capability_request_result(bench, scenario, result)
    finally:
        bench.cleanup()


@pytest.mark.parametrize(
    "scenario",
    _build_capability_turn_script_matrix(),
    ids=lambda scenario: scenario["name"],
)
def test_capability_rift_json_turn_script_matrix(
        scenario: Dict[str, object],
) -> None:
    """
    Verify capability-room multistep JSON turn scripts.

    Args:
        scenario:
            Parametrized turn-script scenario.

    Returns:
        None.
    """
    bench = CapabilityRiftJsonBench(
        frame_name="ops_capability_turns",
        dynamic_frame=scenario["frame_mode"] == "dynamic",
    )
    try:
        saved_results = bench.dispatch_turn_script_json(scenario["script_json"])
        _assert_capability_turn_script_result(bench, scenario, saved_results)
    finally:
        bench.cleanup()
