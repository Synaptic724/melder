"""
What an agent writing ordinary Python gets from a codegen room (GitHub #337).

Purpose:
    An external agent loop drove a codegen room under the safe profile and met the room's contract from the agent's
    side: validation refused valid Python that binds a name through an exception handler, a match pattern or a type
    parameter (task 1), and the room's help never said how a value comes back (task 2). These integration tests pin,
    in a real safe-profile room, that such code validates and executes and what the execution payload carries.
    Tasks 6 and 7 (GitHub #339) add the room's command line - `run_command`, `describe_commands`, `describe_command`
    and `tool_definitions`, `frame_name` optional on the three codegen commands - and the run id and failure location
    every execute payload carries; the tests after the #337 ones pin each of #339's acceptance criteria.

Runs only on 3.14t (melder package root import chain).
"""
import annotationlib
import inspect
import json
from typing import TYPE_CHECKING, Callable, Dict, Iterator, Optional, Set, Tuple

import pytest

from tests._codegen_system_support import (
    create_enabled_nexus,
    reset_runtime_singletons,
)

if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
    from melder.nexus.rift.command_system.codegen_command_system import CodegenCommandSystem


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


def _safe_room(
        output_capture: Optional[bool] = None,
        output_limit: Optional[int] = None,
) -> Tuple[Conduit, CodegenCommandSystem]:
    """
    Open a codegen room on frame "ops" governed by the safe codegen profile.

    Args:
        output_capture:
            When given, the room configuration's `with_codegen_output_capture` value; None keeps the default.
        output_limit:
            When given, the room configuration's `with_codegen_output_limit` value; None keeps the default.

    Returns:
        Tuple[Conduit, CodegenCommandSystem]: The frame's root conduit (the caller cleans it) and the room's command
        system.
    """
    nexus = create_enabled_nexus()
    configuration = nexus.create_rift_configuration()
    configuration.with_space_type("codegen")
    if output_capture is not None:
        configuration.with_codegen_output_capture(output_capture)
    if output_limit is not None:
        configuration.with_codegen_output_limit(output_limit)
    rift = nexus.create_rift(configuration=configuration, rift_name="alpha")
    conduit = rift.create_nexus_frame(frame_name="ops")
    codegen_change = nexus.get_frame_acl_builder("ops").begin_codegen_change(
        reason="agent_contract",
    )
    codegen_change.use_profile("safe")
    codegen_change.commit_change()
    rift.create_frame_link("ops")
    return conduit, rift.space.command_system


@pytest.mark.parametrize(
    ("code", "expected_result"),
    [
        pytest.param(
            "try:\n    int('x')\nexcept ValueError as error:\n    result = str(error)\n",
            "invalid literal for int() with base 10: 'x'",
            id="except-as",
        ),
        pytest.param(
            "match [1, 2, 3]:\n    case [first, *rest]:\n        result = (first, rest)\n",
            (1, [2, 3]),
            id="match-star",
        ),
        pytest.param(
            "match {'a': 1, 'b': 2}:\n    case {'a': value, **others}:\n        result = (value, others)\n",
            (1, {"b": 2}),
            id="match-mapping-rest",
        ),
        pytest.param(
            "def first[T](items: list[T]) -> T:\n    return items[0]\nresult = first([7])\n",
            7,
            id="type-parameter",
        ),
    ],
)
def test_safe_room_validates_and_executes_code_that_binds_names_beyond_assignment(
        code: str,
        expected_result: object,
) -> None:
    """
    Contract: in a safe-profile room, code that binds a name through `except ... as`, a match pattern or a PEP 695
    type parameter is accepted by `validate_codegen` and by `execute_codegen`, which returns its `result` (GitHub
    #337, task 1; before the fix both refused it with "Name '<name>' is not available in the codegen namespace.").
    """
    conduit, command_system = _safe_room()
    try:
        validation = command_system.validate_codegen(code, frame_name="ops")
        execution = command_system.execute_codegen(code, frame_name="ops")
    finally:
        conduit.cleanup()

    assert validation["accepted"] is True
    assert execution["accepted"] is True
    assert execution["result"] == expected_result


def test_safe_room_still_refuses_a_name_that_nothing_binds() -> None:
    """
    Contract: an exception handler's binding admits only its own name - a load of a name nothing in the code binds
    is still refused, and the code does not run (GitHub #337, task 1).
    """
    code = "try:\n    int('x')\nexcept ValueError as error:\n    result = str(mystery)\n"
    conduit, command_system = _safe_room()
    try:
        execution = command_system.execute_codegen(code, frame_name="ops")
    finally:
        conduit.cleanup()

    assert execution["accepted"] is False
    assert execution["validation_issues"] == (
        "Name 'mystery' is not available in the codegen namespace.",
    )
    assert "result" not in execution


def test_safe_room_returns_what_the_code_printed_under_output(
        capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Contract: by default a codegen room captures room code's `print` - `sep` and `end` honoured - into the payload's
    `output` key beside `result`, and nothing reaches the host process's stdout (GitHub #337, task 2).
    """
    conduit, command_system = _safe_room()
    try:
        execution = command_system.execute_codegen(
            "print('rows:', 3)\nprint('a', 'b', sep='-', end='!')\nresult = 1\n",
            frame_name="ops",
        )
    finally:
        conduit.cleanup()

    assert execution["accepted"] is True
    assert execution["output"] == "rows: 3\na-b!"
    assert execution["result"] == 1
    assert capsys.readouterr().out == ""


def test_a_run_that_raises_still_returns_what_it_printed() -> None:
    """
    Contract: when room code raises, the payload carries what it printed before the error beside `runtime_error`
    (GitHub #337, task 2).
    """
    conduit, command_system = _safe_room()
    try:
        execution = command_system.execute_codegen(
            "print('before')\nraise ValueError('boom')\n",
            frame_name="ops",
        )
    finally:
        conduit.cleanup()

    assert execution["accepted"] is False
    assert execution["runtime_error"] == "ValueError: boom"
    assert execution["output"] == "before\n"


def test_output_past_the_room_limit_is_cut_with_a_truncation_line() -> None:
    """
    Contract: a room whose configuration sets `with_codegen_output_limit(10)` keeps the first 10 printed characters,
    then one line counting the characters it dropped (GitHub #337, task 2).
    """
    conduit, command_system = _safe_room(output_limit=10)
    try:
        execution = command_system.execute_codegen("print('x' * 25)\nresult = 1\n", frame_name="ops")
    finally:
        conduit.cleanup()

    assert execution["accepted"] is True
    assert execution["output"] == "x" * 10 + "\n[output truncated: 16 more characters not kept]\n"


def test_a_room_with_capture_off_prints_to_the_host_stdout(
        capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Contract: a room whose configuration sets `with_codegen_output_capture(False)` keeps the interpreter's `print`:
    the text reaches the host's stdout and the payload has no `output` key (GitHub #337, task 2).
    """
    conduit, command_system = _safe_room(output_capture=False)
    try:
        execution = command_system.execute_codegen("print('hello')\nresult = 1\n", frame_name="ops")
    finally:
        conduit.cleanup()

    assert execution["accepted"] is True
    assert "output" not in execution
    assert capsys.readouterr().out == "hello\n"


def test_the_payload_has_no_output_key_when_nothing_was_printed() -> None:
    """
    Contract: code that prints nothing returns exactly `accepted`, `frame_name`, its `run_id` and its `result`
    (GitHub #337, task 2; `run_id` since GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        execution = command_system.execute_codegen("result = {'answer': 42}\n", frame_name="ops")
    finally:
        conduit.cleanup()

    run_id = execution.pop("run_id")
    assert isinstance(run_id, str) and run_id
    assert execution == {"accepted": True, "frame_name": "ops", "result": {"answer": 42}}


def _command_parameters(method: Callable[..., object]) -> Tuple[inspect.Parameter, ...]:
    """
    Read a room command's parameters without evaluating its annotations.

    Args:
        method: The bound room command.

    Returns:
        Tuple[inspect.Parameter, ...]: Its parameters, in signature order.
    """
    signature = inspect.signature(method, annotation_format=annotationlib.Format.FORWARDREF)
    return tuple(signature.parameters.values())


def _schema_keywords(schema: Dict[str, object]) -> Set[str]:
    """
    Collect every keyword one JSON Schema uses, nested schemas included.

    Args:
        schema: A property schema of a tool definition.

    Returns:
        Set[str]: The keywords found.
    """
    keywords = set(schema)
    nested = list(schema.get("anyOf", ()))
    if "items" in schema:
        nested.append(schema["items"])
    for nested_schema in nested:
        keywords |= _schema_keywords(nested_schema)
    return keywords


def test_run_command_refuses_a_call_missing_a_required_argument() -> None:
    """
    Contract: `run_command("validate_codegen", {})` answers the refusal shape naming `code` as missing, its message
    naming the command and its signature, where a by-name call used to raise Python's TypeError (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        refusal = command_system.run_command("validate_codegen", {})
    finally:
        conduit.cleanup()

    assert refusal == {
        "accepted": False,
        "command": "validate_codegen",
        "reason": "command_arguments_invalid",
        "message": (
            "Command 'validate_codegen' cannot run with these arguments: missing required argument 'code'. "
            "Call it as validate_codegen(code: str, *, frame_name: Optional[str] = None) -> Dict[str, object]."
        ),
        "missing_arguments": ("code",),
        "unknown_arguments": (),
    }


@pytest.mark.parametrize(
    ("command_name", "arguments", "expected_missing", "expected_unknown"),
    [
        pytest.param("validate_codegen", {"code": "result = 1", "frame": "ops"}, (), ("frame",), id="unknown"),
        pytest.param("execute_codegen", {"source": "result = 1"}, ("code",), ("source",), id="missing-and-unknown"),
        pytest.param(
            "materialize_codegen",
            {"code": "value = 1"},
            ("module_name",),
            (),
            id="missing-keyword-only",
        ),
    ],
)
def test_run_command_names_the_unknown_and_missing_arguments(
        command_name: str,
        arguments: Dict[str, object],
        expected_missing: Tuple[str, ...],
        expected_unknown: Tuple[str, ...],
) -> None:
    """
    Contract: arguments that do not bind are refused naming every missing and every unknown argument, and nothing
    runs (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        refusal = command_system.run_command(command_name, arguments)
    finally:
        conduit.cleanup()

    assert refusal["accepted"] is False
    assert refusal["command"] == command_name
    assert refusal["reason"] == "command_arguments_invalid"
    assert refusal["missing_arguments"] == expected_missing
    assert refusal["unknown_arguments"] == expected_unknown
    for name in expected_missing + expected_unknown:
        assert "'{0}'".format(name) in refusal["message"]


@pytest.mark.parametrize(
    "command_name",
    [
        pytest.param("cleanup", id="cleanup"),
        pytest.param("_require_codegen_system", id="private-method"),
        pytest.param("attach_codegen_system", id="public-method-outside-the-list"),
        pytest.param("run_command", id="run_command-itself"),
        pytest.param("tool_definitions", id="tool_definitions"),
        pytest.param("list_supported_command_methods", id="list_supported_command_methods"),
    ],
)
def test_run_command_refuses_a_name_outside_the_rooms_command_list(command_name: str) -> None:
    """
    Contract: a name outside the room's command list - `cleanup`, a private method, any public method the list does
    not carry - is refused with the supported commands, and nothing runs: the room is still live (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        supported = command_system.list_supported_command_methods()
        refusal = command_system.run_command(command_name, {})
        still_cleaned = command_system.cleaned
        after = command_system.execute_codegen("result = 1\n", frame_name="ops")
    finally:
        conduit.cleanup()

    assert refusal == {
        "accepted": False,
        "command": command_name,
        "reason": "command_not_supported",
        "message": "Command '{0}' is not in this room's command list. Supported commands: {1}.".format(
            command_name,
            ", ".join(supported),
        ),
        "supported_commands": supported,
    }
    assert still_cleaned is False
    assert after["accepted"] is True


def test_run_command_returns_what_the_direct_call_returns() -> None:
    """
    Contract: a call that binds returns the command's own value, unwrapped - the same payload as the direct call,
    the same live object - and an omitted `frame_name` runs on the room's default frame (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        direct_validation = command_system.validate_codegen("result = 1\n", frame_name="ops")
        named_validation = command_system.run_command(
            "validate_codegen",
            {"code": "result = 1\n", "frame_name": "ops"},
        )
        direct_frame = command_system.get_nexus_frame(frame_name="ops")
        named_frame = command_system.run_command("get_nexus_frame", {"frame_name": "ops"})
        direct_execution = command_system.execute_codegen("result = {'answer': 42}\n")
        named_execution = command_system.run_command("execute_codegen", {"code": "result = {'answer': 42}\n"})
    finally:
        conduit.cleanup()

    assert named_validation == direct_validation
    assert named_frame is direct_frame is conduit
    assert named_execution.pop("run_id") != direct_execution.pop("run_id")
    assert named_execution == direct_execution == {"accepted": True, "frame_name": "ops", "result": {"answer": 42}}


def test_run_command_never_catches_what_the_command_raises() -> None:
    """
    Contract: only the bind is checked; what the dispatched command raises - here the empty-code ValueError -
    propagates unchanged (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        with pytest.raises(ValueError, match="code cannot be empty."):
            command_system.run_command("execute_codegen", {"code": ""})
        with pytest.raises(ValueError, match="frame_name cannot be empty."):
            command_system.run_command("validate_codegen", {"code": "result = 1", "frame_name": ""})
    finally:
        conduit.cleanup()


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        pytest.param(["code"], "arguments must be a mapping", id="list"),
        pytest.param({7: "result = 1"}, "argument names must be strings", id="int-key"),
    ],
)
def test_run_command_raises_type_error_for_arguments_that_are_not_a_name_mapping(
        arguments: object,
        message: str,
) -> None:
    """
    Contract: arguments that are not a mapping with string keys are a caller bug and raise TypeError (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        with pytest.raises(TypeError, match=message):
            command_system.run_command("execute_codegen", arguments)
    finally:
        conduit.cleanup()


def test_describe_commands_covers_every_supported_command() -> None:
    """
    Contract: `describe_commands()` has one entry per supported command, in the list's order - `command`,
    `signature` and `summary` (the docstring's first line) - and both help commands are in the list (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        supported = command_system.list_supported_command_methods()
        catalog = command_system.describe_commands()
        summaries = {
            name: inspect.getdoc(getattr(command_system, name)).splitlines()[0]
            for name in supported
        }
    finally:
        conduit.cleanup()

    assert supported[-2:] == ("describe_commands", "describe_command")
    assert tuple(entry["command"] for entry in catalog) == supported
    for entry in catalog:
        assert set(entry) == {"command", "signature", "summary"}
        assert entry["signature"].startswith(entry["command"] + "(")
        assert entry["summary"] == summaries[entry["command"]]
    assert catalog[supported.index("execute_codegen")] == {
        "command": "execute_codegen",
        "signature": "execute_codegen(code: str, *, frame_name: Optional[str] = None) -> Dict[str, object]",
        "summary": "Execute generated Python code through the attached codegen system.",
    }


def test_describe_command_gives_one_commands_arguments_and_docstring() -> None:
    """
    Contract: `describe_command("execute_codegen")` answers `accepted: True`, its signature, one row per argument
    and its full docstring, which names the payload's run and failure-location keys, the `frame_name` default and
    the workstation for state kept between runs (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        help_payload = command_system.describe_command("execute_codegen")
        docstring = inspect.getdoc(command_system.execute_codegen)
    finally:
        conduit.cleanup()

    assert help_payload == {
        "accepted": True,
        "command": "execute_codegen",
        "signature": "execute_codegen(code: str, *, frame_name: Optional[str] = None) -> Dict[str, object]",
        "arguments": (
            {"name": "code", "type": "str", "required": True},
            {"name": "frame_name", "type": "Optional[str]", "required": False, "default": None},
        ),
        "doc": docstring,
    }
    for key in ("run_id", "runtime_error_line", "runtime_error_run_id", "runtime_error_line_text"):
        assert "`{0}`".format(key) in docstring
    assert "default runtime frame" in docstring
    assert "workstation.bind_object" in docstring
    assert "workstation.get" in docstring


def test_research_heads_help_says_its_tip_is_the_newest_recorded_version() -> None:
    """
    Contract: `research_heads`' help says each tip is the newest version recorded on the lane, not the active one,
    and points at `research_residency` for which is active (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        docstring = command_system.describe_command("research_heads")["doc"]
    finally:
        conduit.cleanup()

    assert "newest version recorded" in docstring
    assert "not the version" in docstring
    assert "research_residency" in docstring


def test_describe_command_refuses_an_unknown_name() -> None:
    """
    Contract: `describe_command` of a name outside the room's command list answers the refusal shape with the
    supported commands (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        supported = command_system.list_supported_command_methods()
        refusal = command_system.describe_command("cleanup")
    finally:
        conduit.cleanup()

    assert refusal["accepted"] is False
    assert refusal["command"] == "cleanup"
    assert refusal["reason"] == "command_not_supported"
    assert refusal["supported_commands"] == supported


def test_tool_definitions_give_one_schema_per_command_matching_its_signature() -> None:
    """
    Contract: `tool_definitions()` has one `{name, description, input_schema}` per supported command; each schema is
    a JSON-serializable object schema whose `required` is exactly the parameters without defaults, whose properties
    are the keyword-passable parameters, which uses only the keywords the catalog emits, and which allows additional
    properties only for a command taking `**kwargs` (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        supported = command_system.list_supported_command_methods()
        definitions = command_system.tool_definitions()
        parameters_by_name = {
            name: _command_parameters(getattr(command_system, name))
            for name in supported
        }
    finally:
        conduit.cleanup()

    assert tuple(definition["name"] for definition in definitions) == supported
    assert [definition["name"] for definition in json.loads(json.dumps(definitions))] == list(supported)
    for definition in definitions:
        parameters = parameters_by_name[definition["name"]]
        schema = definition["input_schema"]
        assert set(definition) == {"name", "description", "input_schema"}
        assert set(schema) == {"type", "properties", "required", "additionalProperties"}
        assert schema["type"] == "object"
        assert schema["required"] == [
            parameter.name
            for parameter in parameters
            if parameter.default is inspect.Parameter.empty
            and parameter.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        ]
        assert list(schema["properties"]) == [
            parameter.name
            for parameter in parameters
            if parameter.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
        ]
        assert schema["additionalProperties"] is any(
            parameter.kind is inspect.Parameter.VAR_KEYWORD for parameter in parameters
        )
        for property_schema in schema["properties"].values():
            assert _schema_keywords(property_schema) <= {"type", "items", "anyOf", "enum", "description", "default"}


def test_frame_name_is_optional_on_the_three_codegen_commands() -> None:
    """
    Contract: the codegen commands' tool schemas require `code` (and `module_name`) but not `frame_name`, and an
    omitted `frame_name` runs on the room's default frame (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        definitions = {definition["name"]: definition for definition in command_system.tool_definitions()}
        validation = command_system.validate_codegen("result = 1\n")
        execution = command_system.execute_codegen("result = 1\n")
        materialization = command_system.materialize_codegen("value = 1\n", module_name="json")
    finally:
        conduit.cleanup()

    assert definitions["validate_codegen"]["input_schema"]["required"] == ["code"]
    assert definitions["execute_codegen"]["input_schema"]["required"] == ["code"]
    assert definitions["materialize_codegen"]["input_schema"]["required"] == ["code", "module_name"]
    assert validation["frame_name"] == "ops"
    assert execution["frame_name"] == "ops"
    assert materialization["materialized"] is False
    assert materialization["validation"]["frame_name"] == "ops"


@pytest.mark.parametrize(
    "command_name",
    [
        pytest.param("validate_codegen", id="validate"),
        pytest.param("execute_codegen", id="execute"),
        pytest.param("materialize_codegen", id="materialize"),
    ],
)
def test_an_omitted_frame_name_in_a_room_without_a_default_frame_raises(command_name: str) -> None:
    """
    Contract: a room with no single assigned frame has no default, so an omitted `frame_name` raises the room's
    existing "Rift has no default runtime frame." ValueError (GitHub #339).
    """
    nexus = create_enabled_nexus()
    configuration = nexus.create_rift_configuration()
    configuration.with_space_type("codegen")
    command_system = nexus.create_rift(configuration=configuration, rift_name="alpha").space.command_system
    arguments: Dict[str, object] = {"code": "value = 1\n"}
    if command_name == "materialize_codegen":
        arguments["module_name"] = "json"

    with pytest.raises(ValueError, match="Rift has no default runtime frame."):
        getattr(command_system, command_name)(**arguments)


def test_every_execute_payload_carries_its_run_id() -> None:
    """
    Contract: every execute payload - accepted, refused by validation, failed at run time - carries its own run id,
    and only the runtime failure carries a location (GitHub #339).
    """
    location_keys = {"runtime_error_line", "runtime_error_run_id", "runtime_error_line_text"}
    conduit, command_system = _safe_room()
    try:
        accepted = command_system.execute_codegen("result = 1\n", frame_name="ops")
        refused = command_system.execute_codegen("import os\n", frame_name="ops")
        failed = command_system.execute_codegen("assert 1 == 2\n", frame_name="ops")
    finally:
        conduit.cleanup()

    run_ids = {accepted["run_id"], refused["run_id"], failed["run_id"]}
    assert len(run_ids) == 3
    assert all(isinstance(run_id, str) and run_id for run_id in run_ids)
    assert refused["reason"] == "codegen_execution_validation_failed"
    assert not location_keys & set(accepted)
    assert not location_keys & set(refused)
    assert location_keys <= set(failed)


def test_a_failing_bare_assert_reports_its_line_text_and_run() -> None:
    """
    Contract: a failing bare `assert` reports `runtime_error` as before plus its line number, that line's text and
    the id of its run (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        execution = command_system.execute_codegen("assert 1 == 2\n", frame_name="ops")
    finally:
        conduit.cleanup()

    assert execution["accepted"] is False
    assert execution["runtime_error"] == "AssertionError: "
    assert execution["runtime_error_line"] == 1
    assert execution["runtime_error_run_id"] == execution["run_id"]
    assert execution["runtime_error_line_text"] == "assert 1 == 2"


def test_a_failure_inside_a_method_an_earlier_run_left_reports_that_runs_line() -> None:
    """
    Contract: a run that calls a method an earlier run left on the workstation, and fails inside it, reports the
    earlier run's id, the line of its code and that line's text (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        defined = command_system.execute_codegen(
            "def check(value):\n"
            "    assert value == 2, 'value must be 2'\n"
            "    return value\n"
            "workstation.bind_object('check', check)\n",
            frame_name="ops",
        )
        failed = command_system.execute_codegen("checked = workstation.get('check')(3)\n", frame_name="ops")
    finally:
        conduit.cleanup()

    assert defined["accepted"] is True
    assert failed["runtime_error"] == "AssertionError: value must be 2"
    assert failed["runtime_error_run_id"] == defined["run_id"]
    assert failed["runtime_error_run_id"] != failed["run_id"]
    assert failed["runtime_error_line"] == 2
    assert failed["runtime_error_line_text"] == "assert value == 2, 'value must be 2'"


def test_a_failure_inside_melder_code_names_the_room_line_that_called_it() -> None:
    """
    Contract: a failure raised inside melder code that room code called is located at the room line that made the
    call (GitHub #339).
    """
    conduit, command_system = _safe_room()
    try:
        execution = command_system.execute_codegen(
            "x = 1\nworkstation.get('nothing_bound_here')\n",
            frame_name="ops",
        )
    finally:
        conduit.cleanup()

    assert execution["runtime_error"] == "ValueError: Binding 'nothing_bound_here' was not found."
    assert execution["runtime_error_line"] == 2
    assert execution["runtime_error_run_id"] == execution["run_id"]
    assert execution["runtime_error_line_text"] == "workstation.get('nothing_bound_here')"


def test_the_kept_run_sources_are_gone_after_the_room_is_removed() -> None:
    """
    Contract: the room's codegen engine keeps each accepted run's source until the room is removed; removing the
    Rift cleans the engine and drops them (GitHub #339).
    """
    nexus = create_enabled_nexus()
    configuration = nexus.create_rift_configuration()
    configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=configuration, rift_name="alpha")
    conduit = rift.create_nexus_frame(frame_name="ops")
    try:
        rift.create_frame_link("ops")
        codegen_system = rift.space.codegen_system
        execution = rift.space.command_system.execute_codegen("result = 1\n", frame_name="ops")
        kept_before_removal = dict(codegen_system._run_sources)
        nexus.remove_rift(rift.id)
    finally:
        conduit.cleanup()

    assert kept_before_removal == {execution["run_id"]: "result = 1\n"}
    assert codegen_system.cleaned is True
    with pytest.raises(AttributeError):
        _ = codegen_system._run_sources
