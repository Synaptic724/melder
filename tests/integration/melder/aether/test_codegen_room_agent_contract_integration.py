"""
What an agent writing ordinary Python gets from a codegen room (GitHub #337).

Purpose:
    An external agent loop drove a codegen room under the safe profile and met the room's contract from the agent's
    side: validation refused valid Python that binds a name through an exception handler, a match pattern or a type
    parameter (task 1), and the room's help never said how a value comes back (task 2). These integration tests pin,
    in a real safe-profile room, that such code validates and executes and what the execution payload carries.

Runs only on 3.14t (melder package root import chain).
"""
from typing import TYPE_CHECKING, Iterator, Optional, Tuple

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
    Contract: code that prints nothing returns exactly `accepted`, `frame_name` and its `result` (GitHub #337,
    task 2).
    """
    conduit, command_system = _safe_room()
    try:
        execution = command_system.execute_codegen("result = {'answer': 42}\n", frame_name="ops")
    finally:
        conduit.cleanup()

    assert execution == {"accepted": True, "frame_name": "ops", "result": {"answer": 42}}
