"""
The room command line in static and capability rooms (GitHub #339).

Purpose:
    `describe_commands`, `describe_command`, `run_command` and `tool_definitions` live on the base `CommandSystem`, so
    every room has them, not only codegen rooms (whose acceptance tests are in
    `test_codegen_room_agent_contract_integration.py`). These tests open real static and capability rooms through
    Nexus and pin that each room's command list ends with the two help commands, that the catalog and the tool
    definitions cover the list, and that `run_command` round-trips one of the room's commands and refuses a name
    outside its list.

Runs only on 3.14t (melder package root import chain).
"""
from typing import TYPE_CHECKING, Iterator, Tuple

import pytest

from tests._codegen_system_support import (
    create_enabled_nexus,
    reset_runtime_singletons,
)

if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
    from melder.nexus.rift.rift import Rift


@pytest.fixture(autouse=True)
def isolated_runtime() -> Iterator[None]:
    """
    Run each test against fresh runtime singletons.

    Yields:
        None.
    """
    reset_runtime_singletons()
    yield
    reset_runtime_singletons()


def _room(space_type: str) -> Tuple[Conduit, Rift]:
    """
    Open a room of `space_type` on one Nexus-managed frame "ops".

    Args:
        space_type:
            "static" or "capability".

    Returns:
        Tuple[Conduit, Rift]: The frame's root conduit (the caller cleans it) and the Rift owning the room.
    """
    nexus = create_enabled_nexus()
    configuration = nexus.create_rift_configuration()
    configuration.with_space_type(space_type)
    rift = nexus.create_rift(configuration=configuration, rift_name="alpha")
    conduit = rift.create_nexus_frame(frame_name="ops")
    rift.create_frame_link("ops")
    return conduit, rift


@pytest.mark.parametrize("space_type", ["static", "capability"])
def test_the_room_command_list_ends_with_the_two_help_commands(space_type: str) -> None:
    """
    Contract: the room's command list keeps its order and ends with `describe_commands` and `describe_command`, once
    each; `run_command` and `tool_definitions` serve the caller and are not in it; `describe_commands()` covers
    exactly the list, in its order (GitHub #339).
    """
    conduit, rift = _room(space_type)
    try:
        command_system = rift.space.command_system
        supported = command_system.list_supported_command_methods()
        catalog = command_system.describe_commands()
    finally:
        conduit.cleanup()

    assert supported[-2:] == ("describe_commands", "describe_command")
    assert supported.count("describe_commands") == 1
    assert supported.count("describe_command") == 1
    assert "run_command" not in supported
    assert "tool_definitions" not in supported
    assert supported[:2] == ("link_frame", "get_nexus_frame")
    assert tuple(entry["command"] for entry in catalog) == supported


@pytest.mark.parametrize("space_type", ["static", "capability"])
def test_run_command_round_trips_a_room_command(space_type: str) -> None:
    """
    Contract: `run_command("get_nexus_frame", {"frame_name": "ops"})` returns the very object the direct call returns
    - the frame's root conduit - and `run_command("describe_command", ...)` the direct call's help (GitHub #339).
    """
    conduit, rift = _room(space_type)
    try:
        command_system = rift.space.command_system
        named_frame = command_system.run_command("get_nexus_frame", {"frame_name": "ops"})
        direct_frame = command_system.get_nexus_frame(frame_name="ops")
        named_help = command_system.run_command("describe_command", {"command_name": "link_frame"})
        direct_help = command_system.describe_command("link_frame")
    finally:
        conduit.cleanup()

    assert named_frame is direct_frame is conduit
    assert named_help == direct_help
    assert named_help["signature"] == "link_frame(frame_name: str) -> None"


@pytest.mark.parametrize("space_type", ["static", "capability"])
def test_run_command_refuses_a_name_outside_the_room_list(space_type: str) -> None:
    """
    Contract: `cleanup` is not a room command: `run_command` refuses it with the room's supported commands and the
    room stays live (GitHub #339).
    """
    conduit, rift = _room(space_type)
    try:
        command_system = rift.space.command_system
        supported = command_system.list_supported_command_methods()
        refusal = command_system.run_command("cleanup", {})
        still_cleaned = command_system.cleaned
    finally:
        conduit.cleanup()

    assert refusal["accepted"] is False
    assert refusal["reason"] == "command_not_supported"
    assert refusal["supported_commands"] == supported
    assert still_cleaned is False


@pytest.mark.parametrize("space_type", ["static", "capability"])
def test_tool_definitions_cover_the_room_list(space_type: str) -> None:
    """
    Contract: one tool definition per supported command, in the list's order; `execute_target_method`, the room
    command taking `**kwargs`, is the one whose schema allows additional properties (GitHub #339).
    """
    conduit, rift = _room(space_type)
    try:
        command_system = rift.space.command_system
        supported = command_system.list_supported_command_methods()
        definitions = command_system.tool_definitions()
    finally:
        conduit.cleanup()

    assert tuple(definition["name"] for definition in definitions) == supported
    open_schemas = [
        definition["name"]
        for definition in definitions
        if definition["input_schema"]["additionalProperties"] is True
    ]
    assert open_schemas == ["execute_target_method"]
