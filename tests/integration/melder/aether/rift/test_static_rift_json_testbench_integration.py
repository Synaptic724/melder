import gc
import json
from typing import Any, Dict, List

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)
from melder.spellbook.spellbook import Spellbook
from tests.integration.melder.aether.rift.static_rift_json_testbench_support import (
    StaticRiftJsonBench,
)


def _reset_runtime_singletons() -> None:
    """
    Reset the singleton runtime surfaces used by the static testbench.

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
    StaticFrameViewer._aether = aether


def _replace_case_placeholder(value: Any, case_name: str) -> Any:
    """
    Replace the `__CASE__` placeholder recursively in one request payload.

    Args:
        value:
            Raw request value.
        case_name:
            Spell case name to substitute.

        Returns:
            Any: Payload with the placeholder replaced.
    """
    if isinstance(value, list):
        return [_replace_case_placeholder(item, case_name) for item in value]
    if isinstance(value, dict):
        return {
            key: _replace_case_placeholder(current_value, case_name)
            for key, current_value in value.items()
        }
    if isinstance(value, str):
        return value.replace("__CASE__", case_name)
    return value


def _build_spell_case_matrix() -> List[Dict[str, object]]:
    """
    Build the 84 spell-focused request scenarios.

    Returns:
        List[Dict[str, object]]: Spell request scenarios.
    """
    spell_cases = {
        "unique_live": {
            "visible": True,
            "command_success": True,
            "error_contains": None,
        },
        "unique_per_conduit_live": {
            "visible": True,
            "command_success": True,
            "error_contains": None,
        },
        "unique_per_lineage_live": {
            "visible": True,
            "command_success": True,
            "error_contains": None,
        },
        "many_live": {
            "visible": False,
            "command_success": False,
            "error_contains": "unsupported static existence 'many'",
        },
        "spellspace_live": {
            "visible": False,
            "command_success": False,
            "error_contains": "unsupported static existence 'unique_per_spell_space'",
        },
        "unique_dead": {
            "visible": False,
            "command_success": False,
            "error_contains": "is not live",
        },
    }
    operations = (
        {
            "name": "viewer_spell_names",
            "request": {
                "surface": "viewer",
                "method": "list_spell_names",
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "viewer_names",
            "raises_when_invisible": False,
        },
        {
            "name": "viewer_spell_sources",
            "request": {
                "surface": "viewer",
                "method": "list_spell_source_ids_for_frame",
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "viewer_sources",
            "raises_when_invisible": False,
        },
        {
            "name": "viewer_spell_targets",
            "request": {
                "surface": "viewer",
                "method": "execute_method",
                "kwargs": {
                    "method_name": "list_targets",
                    "frame_name": "@manifest.frame_name",
                    "source_kind": "spell",
                },
            },
            "kind": "viewer_targets",
            "raises_when_invisible": False,
        },
        {
            "name": "viewer_describe_spell",
            "request": {
                "surface": "viewer",
                "method": "describe_spell_record",
                "kwargs": {
                    "spell_source_id": "@manifest.spells.__CASE__.source_id",
                    "frame_name": "@manifest.frame_name",
                },
            },
            "kind": "viewer_describe",
            "raises_when_invisible": True,
            "invisible_error_contains": "not found",
        },
        {
            "name": "command_get_by_index",
            "request": {
                "surface": "command",
                "method": "get_spell_by_index_id",
                "args": ["@manifest.spells.__CASE__.spell_index_id"],
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "command_object",
            "raises_when_command_hidden": True,
        },
        {
            "name": "command_get_by_source",
            "request": {
                "surface": "command",
                "method": "get_spell_by_source_id",
                "args": ["@manifest.spells.__CASE__.source_id"],
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "command_object",
            "raises_when_command_hidden": True,
            "hidden_error_contains": "not found",
        },
        {
            "name": "command_get_by_id",
            "request": {
                "surface": "command",
                "method": "get_spell_by_id",
                "args": ["@manifest.spells.__CASE__.spell_id"],
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "kind": "command_object",
            "raises_when_command_hidden": True,
        },
    )
    scenarios: List[Dict[str, object]] = []
    for frame_mode in ("automatic", "dynamic"):
        for case_name, case_expectation in spell_cases.items():
            for operation in operations:
                scenarios.append(
                    {
                        "name": "{0}_{1}_{2}".format(
                            frame_mode,
                            case_name,
                            operation["name"],
                        ),
                        "frame_mode": frame_mode,
                        "case_name": case_name,
                        "request_json": json.dumps(
                            _replace_case_placeholder(
                                operation["request"],
                                case_name,
                            )
                        ),
                        "kind": operation["kind"],
                        "visible": case_expectation["visible"],
                        "command_success": case_expectation["command_success"],
                        "error_contains": case_expectation["error_contains"],
                        "raises_when_invisible": operation.get(
                            "raises_when_invisible",
                            False,
                        ),
                        "raises_when_command_hidden": operation.get(
                            "raises_when_command_hidden",
                            False,
                        ),
                        "invisible_error_contains": operation.get(
                            "invisible_error_contains",
                            "not found",
                        ),
                        "hidden_error_contains": operation.get(
                            "hidden_error_contains",
                            case_expectation["error_contains"],
                        ),
                    }
                )
    return scenarios


def _build_discovery_case_matrix() -> List[Dict[str, object]]:
    """
    Build the 16 conduit-discovery request scenarios.

    Returns:
        List[Dict[str, object]]: Discovery request scenarios.
    """
    operations = (
        {
            "name": "rift_list_conduit_ids",
            "request": {
                "surface": "rift",
                "method": "list_conduit_ids",
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "expected_by_mode": {
                "automatic": ("@manifest.conduits.root.id",),
                "dynamic": ("@manifest.conduits.root.id",),
            },
        },
        {
            "name": "rift_list_conduit_names",
            "request": {
                "surface": "rift",
                "method": "list_conduit_names",
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "expected_by_mode": {
                "automatic": ("@manifest.conduits.root.name",),
                "dynamic": ("@manifest.conduits.root.name",),
            },
        },
        {
            "name": "rift_count_conduits",
            "request": {
                "surface": "rift",
                "method": "count_conduits",
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "expected_by_mode": {"automatic": 1, "dynamic": 1},
        },
        {
            "name": "rift_has_conduit_id",
            "request": {
                "surface": "rift",
                "method": "has_conduit_id",
                "args": ["@manifest.conduits.root.id"],
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "expected_by_mode": {"automatic": True, "dynamic": True},
        },
        {
            "name": "rift_find_conduit_id_by_name",
            "request": {
                "surface": "rift",
                "method": "find_conduit_id_by_name",
                "args": ["@manifest.conduits.root.name"],
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "expected_by_mode": {
                "automatic": "@manifest.conduits.root.id",
                "dynamic": "@manifest.conduits.root.id",
            },
        },
        {
            "name": "cloud_list_conduit_names",
            "request": {
                "surface": "cloud",
                "method": "list_conduit_names",
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "expected_by_mode": {
                "automatic": tuple(),
                "dynamic": ("@manifest.conduits.root.name",),
            },
        },
        {
            "name": "cloud_count_conduits",
            "request": {
                "surface": "cloud",
                "method": "count_conduits",
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "expected_by_mode": {"automatic": 0, "dynamic": 1},
        },
        {
            "name": "cloud_has_conduit_name",
            "request": {
                "surface": "cloud",
                "method": "has_conduit_name",
                "args": ["@manifest.conduits.root.name"],
                "kwargs": {"frame_name": "@manifest.frame_name"},
            },
            "expected_by_mode": {"automatic": False, "dynamic": True},
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
                    "expected": operation["expected_by_mode"][frame_mode],
                }
            )
    return scenarios


def _resolve_expected_value(bench: StaticRiftJsonBench, expected: Any) -> Any:
    """
    Resolve manifest placeholders inside one expected value.

    Args:
        bench:
            Active testbench.
        expected:
            Raw expected value.

        Returns:
            Any: Resolved expected value.
    """
    if isinstance(expected, tuple):
        return tuple(_resolve_expected_value(bench, item) for item in expected)
    if isinstance(expected, list):
        return [_resolve_expected_value(bench, item) for item in expected]
    if isinstance(expected, str) and expected.startswith("@manifest."):
        return bench._resolve_manifest_path(expected[len("@manifest."):])
    return expected


def _assert_spell_request_result(
        bench: StaticRiftJsonBench,
        scenario: Dict[str, object],
        result: Any,
) -> None:
    """
    Assert one spell-focused request result.

    Args:
        bench:
            Active testbench.
        scenario:
            Spell request scenario.
        result:
            Actual request result.

        Returns:
            None.
    """
    case_name = scenario["case_name"]
    visible = bool(scenario["visible"])
    kind = scenario["kind"]
    source_id = bench.manifest["spells"][case_name]["source_id"]
    spell_name = bench.manifest["spells"][case_name]["spell_name"]
    if kind == "viewer_names":
        assert (spell_name in result) is visible
        return
    if kind == "viewer_sources":
        assert (source_id in result) is visible
        return
    if kind == "viewer_targets":
        returned_source_ids = [
            frame_link.source_id
            for frame_link in result
            if frame_link.source_kind == "spell"
        ]
        assert (source_id in returned_source_ids) is visible
        return
    if kind == "viewer_describe":
        assert result["source_id"] == source_id
        return
    if kind == "command_object":
        assert getattr(result, "kind") == case_name
        return
    raise AssertionError(kind)


def _assert_discovery_request_result(
        bench: StaticRiftJsonBench,
        scenario: Dict[str, object],
        result: Any,
) -> None:
    """
    Assert one discovery request result.

    Args:
        bench:
            Active testbench.
        scenario:
            Discovery request scenario.
        result:
            Actual request result.

        Returns:
            None.
    """
    assert result == _resolve_expected_value(bench, scenario["expected"])


def build_request_scenarios() -> List[Dict[str, object]]:
    """
    Build the full 100-row request matrix.

    Returns:
        List[Dict[str, object]]: Full request matrix.
    """
    scenarios = _build_spell_case_matrix() + _build_discovery_case_matrix()
    if len(scenarios) != 100:
        raise RuntimeError(
            "Static Rift request matrix should contain 100 scenarios, got {0}.".format(
                len(scenarios)
            )
        )
    return scenarios


def _build_turn_script_scenarios() -> List[Dict[str, object]]:
    """
    Build 25 deterministic 5-step interaction scripts.

    Returns:
        List[Dict[str, object]]: Turn-script scenarios.
    """
    spell_scripts: List[Dict[str, object]] = []
    spell_cases = (
        ("unique_live", True, None),
        ("unique_per_conduit_live", True, None),
        ("unique_per_lineage_live", True, None),
        ("many_live", False, "unsupported static existence 'many'"),
        (
            "spellspace_live",
            False,
            "unsupported static existence 'unique_per_spell_space'",
        ),
        ("unique_dead", False, "is not live"),
    )
    for frame_mode in ("automatic", "dynamic"):
        for case_name, command_success, command_error in spell_cases:
            spell_scripts.append(
                {
                    "name": "{0}_{1}_spell_flow".format(frame_mode, case_name),
                    "frame_mode": frame_mode,
                    "kind": "spell_flow",
                    "case_name": case_name,
                    "command_success": command_success,
                    "command_error": command_error,
                    "script": {
                        "turns": [
                            {
                                "surface": "viewer",
                                "method": "list_spell_names",
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "names",
                            },
                            {
                                "surface": "viewer",
                                "method": "list_spell_source_ids_for_frame",
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "sources",
                            },
                            {
                                "surface": "viewer",
                                "method": "execute_method",
                                "kwargs": {
                                    "method_name": "list_targets",
                                    "frame_name": "@manifest.frame_name",
                                    "source_kind": "spell",
                                },
                                "save_as": "targets",
                            },
                            {
                                "surface": "viewer",
                                "method": "describe_spell_record",
                                "kwargs": {
                                    "spell_source_id": "@manifest.spells.__CASE__.source_id",
                                    "frame_name": "@manifest.frame_name",
                                },
                                "save_as": "describe",
                                "expect_error_contains": (
                                    None if command_success else "not found"
                                ),
                            },
                            {
                                "surface": "command",
                                "method": "get_spell_by_index_id",
                                "args": ["@manifest.spells.__CASE__.spell_index_id"],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "fetch",
                                "expect_error_contains": (
                                    None if command_success else command_error
                                ),
                            },
                        ]
                    },
                }
            )

    discovery_scripts = []
    for frame_mode in ("automatic", "dynamic"):
        discovery_scripts.extend(
            [
                {
                    "name": "{0}_rift_discovery_chain".format(frame_mode),
                    "frame_mode": frame_mode,
                    "kind": "rift_discovery_chain",
                    "script": {
                        "turns": [
                            {
                                "surface": "rift",
                                "method": "list_conduit_ids",
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "ids",
                            },
                            {
                                "surface": "rift",
                                "method": "list_conduit_names",
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "names",
                            },
                            {
                                "surface": "rift",
                                "method": "find_conduit_id_by_name",
                                "args": ["@manifest.conduits.root.name"],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "found_id",
                            },
                            {
                                "surface": "rift",
                                "method": "has_conduit_id",
                                "args": ["@turns.found_id"],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "has_id",
                            },
                            {
                                "surface": "rift",
                                "method": "get_conduit_by_id",
                                "args": ["@turns.found_id"],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "conduit",
                            },
                        ]
                    },
                },
                {
                    "name": "{0}_cloud_discovery_chain".format(frame_mode),
                    "frame_mode": frame_mode,
                    "kind": "cloud_discovery_chain",
                    "script": {
                        "turns": [
                            {
                                "surface": "cloud",
                                "method": "count_conduits",
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "count",
                            },
                            {
                                "surface": "cloud",
                                "method": "list_conduit_names",
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "names",
                            },
                            {
                                "surface": "cloud",
                                "method": "has_conduit_name",
                                "args": ["@manifest.conduits.root.name"],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "has_name",
                            },
                            {
                                "surface": "cloud",
                                "method": "find_conduit_id_by_name",
                                "args": ["@manifest.conduits.root.name"],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "found_id",
                            },
                            {
                                "surface": "rift",
                                "method": "has_conduit_name",
                                "args": ["@manifest.conduits.root.name"],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "rift_has_name",
                            },
                        ]
                    },
                },
                {
                    "name": "{0}_lesser_fetch_chain".format(frame_mode),
                    "frame_mode": frame_mode,
                    "kind": "lesser_fetch_chain",
                    "script": {
                        "turns": [
                            {
                                "surface": "rift",
                                "method": "list_conduit_ids",
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "ids",
                            },
                            {
                                "surface": "command",
                                "method": "get_conduit_by_id",
                                "args": ["@manifest.conduits.lesser.id"],
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "lesser",
                            },
                            {
                                "surface": "workstation",
                                "method": "bind_object",
                                "args": ["lesser", "@turns.lesser"],
                                "kwargs": {"weak_ref": False},
                                "save_as": "bound",
                            },
                            {
                                "surface": "workstation",
                                "method": "set_target",
                                "args": ["lesser"],
                                "kwargs": {"store": "objects"},
                                "save_as": "targeted",
                            },
                            {
                                "surface": "workstation",
                                "method": "get_target",
                                "save_as": "target",
                            },
                        ]
                    },
                },
                {
                    "name": "{0}_viewer_target_chain".format(frame_mode),
                    "frame_mode": frame_mode,
                    "kind": "viewer_target_chain",
                    "script": {
                        "turns": [
                            {
                                "surface": "viewer",
                                "method": "execute_method",
                                "kwargs": {
                                    "method_name": "list_targets",
                                    "frame_name": "@manifest.frame_name",
                                },
                                "save_as": "targets",
                            },
                            {
                                "surface": "space",
                                "method": "select_target",
                                "args": ["@turns.targets.0.link_id"],
                                "save_as": "selected",
                            },
                            {
                                "surface": "command",
                                "method": "get_selected_target_link",
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "link",
                            },
                            {
                                "surface": "command",
                                "method": "get_selected_target_record",
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "record",
                            },
                            {
                                "surface": "command",
                                "method": "get_selected_target_runtime_object",
                                "kwargs": {"frame_name": "@manifest.frame_name"},
                                "save_as": "runtime",
                            },
                        ]
                    },
                },
            ]
        )

    workstation_scripts = [
        {
            "name": "automatic_strong_binding_chain",
            "frame_mode": "automatic",
            "kind": "strong_binding_chain",
            "script": {
                "turns": [
                    {
                        "surface": "workstation",
                        "method": "bind_object",
                        "args": ["tool", "@objects.manual_target"],
                        "kwargs": {"weak_ref": False},
                        "save_as": "bound",
                    },
                    {
                        "surface": "workstation",
                        "method": "set_target",
                        "args": ["tool"],
                        "kwargs": {"store": "objects"},
                        "save_as": "selected",
                    },
                    {
                        "surface": "command",
                        "method": "get_selected_target_record",
                        "kwargs": {"frame_name": "@manifest.frame_name"},
                        "expect_error_contains": "no selected target",
                        "save_as": "record_error",
                    },
                    {
                        "surface": "workstation",
                        "method": "get_target",
                        "save_as": "target",
                    },
                    {
                        "surface": "workstation",
                        "method": "get",
                        "args": ["tool"],
                        "save_as": "fetched",
                    },
                ]
            },
        },
        {
            "name": "automatic_weak_binding_chain",
            "frame_mode": "automatic",
            "kind": "weak_binding_chain",
            "script": {
                "turns": [
                    {
                        "surface": "workstation",
                        "method": "bind_object",
                        "args": ["tool", "@objects.manual_target"],
                        "save_as": "bound",
                    },
                    {
                        "surface": "workstation",
                        "method": "set_target",
                        "args": ["tool"],
                        "kwargs": {"store": "objects"},
                        "save_as": "selected",
                    },
                    {
                        "surface": "workstation",
                        "method": "get_target",
                        "save_as": "target",
                    },
                    {
                        "surface": "workstation",
                        "method": "clear_target",
                        "save_as": "cleared",
                    },
                    {
                        "surface": "workstation",
                        "method": "describe_bindings",
                        "save_as": "bindings",
                    },
                ]
            },
        },
        {
            "name": "dynamic_execute_target_chain",
            "frame_mode": "dynamic",
            "kind": "execute_target_chain",
            "script": {
                "turns": [
                    {
                        "surface": "workstation",
                        "method": "bind_object",
                        "args": ["tool", "@objects.manual_target"],
                        "kwargs": {"weak_ref": False},
                        "save_as": "bound",
                    },
                    {
                        "surface": "workstation",
                        "method": "set_target",
                        "args": ["tool"],
                        "kwargs": {"store": "objects"},
                        "save_as": "selected",
                    },
                    {
                        "surface": "command",
                        "method": "execute_target_method",
                        "args": ["run", "json"],
                        "kwargs": {
                            "bind_as_name": "tool_result",
                            "bind_as_store": "attributes",
                        },
                        "save_as": "result",
                    },
                    {
                        "surface": "workstation",
                        "method": "get",
                        "args": ["tool_result"],
                        "kwargs": {"store": "attributes"},
                        "save_as": "bound_result",
                    },
                    {
                        "surface": "workstation",
                        "method": "describe_bindings",
                        "save_as": "bindings",
                    },
                ]
            },
        },
        {
            "name": "dynamic_spell_fetch_chain",
            "frame_mode": "dynamic",
            "kind": "spell_fetch_chain",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "get_spell_by_source_id",
                        "args": ["@manifest.spells.unique_live.source_id"],
                        "kwargs": {"frame_name": "@manifest.frame_name"},
                        "save_as": "spell",
                    },
                    {
                        "surface": "workstation",
                        "method": "bind_object",
                        "args": ["spell", "@turns.spell"],
                        "kwargs": {"weak_ref": False},
                        "save_as": "bound",
                    },
                    {
                        "surface": "workstation",
                        "method": "set_target",
                        "args": ["spell"],
                        "kwargs": {"store": "objects"},
                        "save_as": "selected",
                    },
                    {
                        "surface": "command",
                        "method": "execute_target_method",
                        "args": ["run", "turn"],
                        "save_as": "result",
                    },
                    {
                        "surface": "workstation",
                        "method": "get_target",
                        "save_as": "target",
                    },
                ]
            },
        },
        {
            "name": "dynamic_lesser_target_chain",
            "frame_mode": "dynamic",
            "kind": "lesser_target_chain",
            "script": {
                "turns": [
                    {
                        "surface": "command",
                        "method": "get_conduit_by_id",
                        "args": ["@manifest.conduits.lesser.id"],
                        "kwargs": {"frame_name": "@manifest.frame_name"},
                        "save_as": "lesser",
                    },
                    {
                        "surface": "workstation",
                        "method": "bind_object",
                        "args": ["lesser", "@turns.lesser"],
                        "kwargs": {"weak_ref": False},
                        "save_as": "bound",
                    },
                    {
                        "surface": "workstation",
                        "method": "set_target",
                        "args": ["lesser"],
                        "kwargs": {"store": "objects"},
                        "save_as": "selected",
                    },
                    {
                        "surface": "workstation",
                        "method": "get_target",
                        "save_as": "target",
                    },
                    {
                        "surface": "workstation",
                        "method": "describe_bindings",
                        "save_as": "bindings",
                    },
                ]
            },
        },
    ]

    scenarios = spell_scripts + discovery_scripts + workstation_scripts
    if len(scenarios) != 25:
        raise RuntimeError(
            "Turn-script matrix should contain 25 scenarios, got {0}.".format(
                len(scenarios)
            )
        )
    return scenarios


@pytest.mark.parametrize(
    "scenario",
    build_request_scenarios(),
    ids=lambda scenario: scenario["name"],
)
def test_static_rift_json_request_matrix(
        scenario: Dict[str, object],
) -> None:
    """
    Verify static-room behavior through a 100-row JSON-driven request matrix.

    Returns:
        None.
    """
    _reset_runtime_singletons()
    bench = StaticRiftJsonBench(
        frame_name="matrix_{0}".format(scenario["name"]),
        dynamic_frame=(scenario["frame_mode"] == "dynamic"),
    )
    try:
        if (
                scenario.get("kind") == "viewer_describe"
                and bool(scenario.get("visible", True)) is False
                and bool(scenario.get("raises_when_invisible", False)) is True
        ):
            with pytest.raises(
                    ValueError,
                    match=scenario["invisible_error_contains"],
            ):
                bench.dispatch_json(scenario["request_json"])
            return
        if (
                scenario.get("kind") == "command_object"
                and bool(scenario.get("command_success", True)) is False
                and bool(scenario.get("raises_when_command_hidden", False)) is True
        ):
            with pytest.raises(
                    ValueError,
                    match=scenario["hidden_error_contains"],
            ):
                bench.dispatch_json(scenario["request_json"])
            return
        result = bench.dispatch_json(scenario["request_json"])
        if "case_name" in scenario:
            _assert_spell_request_result(bench, scenario, result)
            return
        _assert_discovery_request_result(bench, scenario, result)
    finally:
        bench.cleanup()
        _reset_runtime_singletons()


def _assert_turn_script_result(
        bench: StaticRiftJsonBench,
        scenario: Dict[str, object],
        saved_results: Dict[str, Any],
) -> None:
    """
    Assert one completed turn-script result set.

    Args:
        bench:
            Active testbench.
        scenario:
            Turn-script scenario.
        saved_results:
            Saved turn results keyed by `save_as`.

        Returns:
            None.
    """
    kind = scenario["kind"]
    if kind == "spell_flow":
        case_name = scenario["case_name"]
        visible = case_name in {
            "unique_live",
            "unique_per_conduit_live",
            "unique_per_lineage_live",
        }
        source_id = bench.manifest["spells"][case_name]["source_id"]
        spell_name = bench.manifest["spells"][case_name]["spell_name"]
        assert (spell_name in saved_results["names"]) is visible
        assert (source_id in saved_results["sources"]) is visible
        returned_source_ids = [
            frame_link.source_id
            for frame_link in saved_results["targets"]
            if frame_link.source_kind == "spell"
        ]
        assert (source_id in returned_source_ids) is visible
        if visible:
            assert saved_results["describe"]["source_id"] == source_id
            assert getattr(saved_results["fetch"], "kind") == case_name
        else:
            assert "error" in saved_results["describe"]
            assert "error" in saved_results["fetch"]
        return
    if kind == "rift_discovery_chain":
        assert saved_results["ids"] == (bench.manifest["conduits"]["root"]["id"],)
        assert saved_results["names"] == (bench.manifest["conduits"]["root"]["name"],)
        assert saved_results["found_id"] == bench.manifest["conduits"]["root"]["id"]
        assert saved_results["has_id"] is True
        assert saved_results["conduit"].id == bench.manifest["conduits"]["root"]["id"]
        return
    if kind == "cloud_discovery_chain":
        if scenario["frame_mode"] == "automatic":
            assert saved_results["count"] == 0
            assert saved_results["names"] == tuple()
            assert saved_results["has_name"] is False
            assert saved_results["found_id"] is None
        else:
            assert saved_results["count"] == 1
            assert saved_results["names"] == (bench.manifest["conduits"]["root"]["name"],)
            assert saved_results["has_name"] is True
            assert saved_results["found_id"] == bench.manifest["conduits"]["root"]["id"]
        assert saved_results["rift_has_name"] is True
        return
    if kind == "lesser_fetch_chain":
        assert saved_results["target"].id == bench.manifest["conduits"]["lesser"]["id"]
        return
    if kind == "viewer_target_chain":
        assert saved_results["link"].source_kind == "frame"
        assert saved_results["record"].frame_name == bench.manifest["frame_name"]
        return
    if kind == "strong_binding_chain":
        assert saved_results["target"].name == "manual_target"
        assert saved_results["fetched"].name == "manual_target"
        return
    if kind == "weak_binding_chain":
        assert "tool" in saved_results["bindings"]["objects"]
        return
    if kind == "execute_target_chain":
        assert saved_results["result"].value == "manual_target:json"
        assert saved_results["bound_result"].value == "manual_target:json"
        return
    if kind == "spell_fetch_chain":
        assert saved_results["result"] == "unique_live:turn"
        assert saved_results["target"].kind == "unique_live"
        return
    if kind == "lesser_target_chain":
        assert saved_results["target"].id == bench.manifest["conduits"]["lesser"]["id"]
        return
    raise AssertionError(kind)


@pytest.mark.parametrize(
    "scenario",
    _build_turn_script_scenarios(),
    ids=lambda scenario: scenario["name"],
)
def test_static_rift_json_turn_script_matrix(
        scenario: Dict[str, object],
) -> None:
    """
    Verify 25 deterministic 5-step turn scripts on the static harness.

    Returns:
        None.
    """
    _reset_runtime_singletons()
    bench = StaticRiftJsonBench(
        frame_name="turn_{0}".format(scenario["name"]),
        dynamic_frame=(scenario["frame_mode"] == "dynamic"),
    )
    try:
        script = _replace_case_placeholder(
            scenario["script"],
            scenario.get("case_name", ""),
        )
        saved_results = bench.dispatch_turn_script(script)
        _assert_turn_script_result(bench, scenario, saved_results)
    finally:
        bench.cleanup()
        _reset_runtime_singletons()


def test_static_rift_json_driver_supports_explicit_strong_binding() -> None:
    """
    Verify the JSON driver can bind and retain a strong workstation object.

    Returns:
        None.
    """
    _reset_runtime_singletons()
    bench = StaticRiftJsonBench(
        frame_name="ops_static_workstation_strong",
        dynamic_frame=False,
    )
    try:
        bench.dispatch_json(
            json.dumps(
                {
                    "surface": "workstation",
                    "method": "bind_object",
                    "args": ["tool", "@objects.manual_target"],
                    "kwargs": {"weak_ref": False},
                }
            )
        )
        bench.drop_object_reference("manual_target")
        gc.collect()
        result = bench.dispatch_json(
            json.dumps(
                {
                    "surface": "workstation",
                    "method": "get",
                    "args": ["tool"],
                }
            )
        )
        assert result.name == "manual_target"
    finally:
        bench.cleanup()
        _reset_runtime_singletons()


def test_static_rift_json_driver_uses_default_weak_binding() -> None:
    """
    Verify static workstation defaults `weak_ref=None` to weak binding.

    Returns:
        None.
    """
    _reset_runtime_singletons()
    bench = StaticRiftJsonBench(
        frame_name="ops_static_workstation_weak",
        dynamic_frame=False,
    )
    try:
        bench.dispatch_json(
            json.dumps(
                {
                    "surface": "workstation",
                    "method": "bind_object",
                    "args": ["tool", "@objects.manual_target"],
                }
            )
        )
        bench.drop_object_reference("manual_target")
        gc.collect()
        with pytest.raises(ValueError, match="not found"):
            bench.dispatch_json(
                json.dumps(
                    {
                        "surface": "workstation",
                        "method": "get",
                        "args": ["tool"],
                    }
                )
            )
    finally:
        bench.cleanup()
        _reset_runtime_singletons()


def test_static_rift_json_driver_can_execute_bound_target_method() -> None:
    """
    Verify the JSON driver can bind a target, select it, and execute a method.

    Returns:
        None.
    """
    _reset_runtime_singletons()
    bench = StaticRiftJsonBench(
        frame_name="ops_static_workstation_execute",
        dynamic_frame=True,
    )
    try:
        bench.dispatch_json(
            json.dumps(
                {
                    "surface": "workstation",
                    "method": "bind_object",
                    "args": ["tool", "@objects.manual_target"],
                    "kwargs": {"weak_ref": False},
                }
            )
        )
        bench.dispatch_json(
            json.dumps(
                {
                    "surface": "workstation",
                    "method": "set_target",
                    "args": ["tool"],
                    "kwargs": {"store": "objects"},
                }
            )
        )
        result = bench.dispatch_json(
            json.dumps(
                {
                    "surface": "command",
                    "method": "execute_target_method",
                    "args": ["run", "json"],
                    "kwargs": {
                        "bind_as_name": "tool_result",
                        "bind_as_store": "attributes",
                    },
                }
            )
        )
        bound_result = bench.dispatch_json(
            json.dumps(
                {
                    "surface": "workstation",
                    "method": "get",
                    "args": ["tool_result"],
                    "kwargs": {"store": "attributes"},
                }
            )
        )
        assert result.value == "manual_target:json"
        assert bound_result.value == "manual_target:json"
    finally:
        bench.cleanup()
        _reset_runtime_singletons()


def test_static_rift_json_driver_can_fetch_lesser_conduit_by_id() -> None:
    """
    Verify the JSON driver can fetch a published lesser conduit through static command.

    Returns:
        None.
    """
    _reset_runtime_singletons()
    bench = StaticRiftJsonBench(
        frame_name="ops_static_lesser_fetch",
        dynamic_frame=True,
    )
    try:
        result = bench.dispatch_json(
            json.dumps(
                {
                    "surface": "command",
                    "method": "get_conduit_by_id",
                    "args": ["@manifest.conduits.lesser.id"],
                    "kwargs": {"frame_name": "@manifest.frame_name"},
                }
            )
        )
        assert result.id == bench.manifest["conduits"]["lesser"]["id"]
    finally:
        bench.cleanup()
        _reset_runtime_singletons()
