"""
Where room code failed: run file names, the executor's traceback walk, kept run sources and the payload keys
(GitHub #339).

Purpose:
    Pin, below the room, the pieces that let an execute payload name its run and the line its code failed on:
    `CodegenCompiler` owns the run file-name form, `CodegenExecutor` walks a raised error's traceback to the
    innermost room-code frame, `CodegenSystem` keeps each accepted run's source until it is cleaned, and
    `CodegenExecutionResult.to_payload` adds `run_id` always and the three location keys when they are set.
"""
import json
from typing import Dict, Optional, Set

import pytest

from melder.nexus.rift.codegen_system.codegen_system import CodegenSystem
from melder.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.nexus.rift.codegen_system.execution.codegen_compiler import (
    CodegenCompiler,
)
from melder.nexus.rift.codegen_system.execution.codegen_execution_result import (
    CodegenExecutionResult,
)
from melder.nexus.rift.codegen_system.execution.codegen_executor import (
    CodegenExecutor,
)
from melder.nexus.rift.codegen_system.namespace.codegen_namespace import (
    CodegenNamespace,
)
from tests._codegen_system_support import (
    CodegenSpaceDouble,
    DetachedRiftProjectionOwner,
    build_namespace_configuration,
)


def _context(code: str) -> CodegenTransactionContext:
    """
    Build one transaction context for frame "ops" holding a bare namespace for `code`.

    Args:
        code: The run's source.

    Returns:
        CodegenTransactionContext: A context the executor can run (the caller cleans nothing; the objects are
        short-lived test values).
    """
    configuration = build_namespace_configuration(frame_name="ops")
    return CodegenTransactionContext(
        frame_name="ops",
        code=code,
        namespace_configuration=configuration,
        namespace=CodegenNamespace(configuration=configuration),
    )


def _run(
        context: CodegenTransactionContext,
        run_sources: Dict[str, str],
) -> Dict[str, object]:
    """
    Compile and execute one context the way `CodegenSystem` does, and return the execute payload.

    Args:
        context: The run to execute.
        run_sources: The kept sources handed to the executor.

    Returns:
        Dict[str, object]: The execute payload.
    """
    compiled_code = CodegenCompiler().compile(context)
    return CodegenExecutor().execute(compiled_code, context, run_sources).to_payload()


def test_run_filename_round_trips_its_run_id() -> None:
    """
    Contract: `run_filename` builds `<melder-codegen:{run_id}>` and `run_id_from_filename` reads the id back.
    """
    filename = CodegenCompiler.run_filename("01JRUN")

    assert filename == "<melder-codegen:01JRUN>"
    assert CodegenCompiler.run_id_from_filename(filename) == "01JRUN"


@pytest.mark.parametrize(
    "filename",
    [
        pytest.param("<string>", id="string"),
        pytest.param("C:/melder/src/melder/nexus/rift/rift_space/workstation.py", id="library-file"),
        pytest.param("<melder-codegen:01JRUN", id="no-suffix"),
        pytest.param("melder-codegen:01JRUN>", id="no-prefix"),
        pytest.param("<melder-codegen:>", id="empty-run-id"),
    ],
)
def test_run_id_from_filename_ignores_every_other_file_name(filename: str) -> None:
    """
    Contract: a file name that is not a run file name - another code object's, or the form with no id - has no run id.
    """
    assert CodegenCompiler.run_id_from_filename(filename) is None


def test_run_filename_refuses_an_empty_run_id() -> None:
    """
    Contract: a run file name needs a run id; an empty one raises ValueError.
    """
    with pytest.raises(ValueError, match="transaction_id cannot be empty."):
        CodegenCompiler.run_filename("")


def test_compile_names_the_code_object_after_its_run() -> None:
    """
    Contract: `compile` names the code object with the run file name of the context's transaction id.
    """
    context = _context("result = 1\n")

    compiled_code = CodegenCompiler().compile(context)

    assert compiled_code.co_filename == CodegenCompiler.run_filename(context.transaction_id)


def test_executor_locates_a_failing_line_of_its_own_run() -> None:
    """
    Contract: a failure in the run's own code names its line, the run and that line's text, stripped; the
    `runtime_error` text is unchanged.
    """
    context = _context("values = [1, 2]\nfor value in values:\n    assert value < 2, 'too big'\n")

    payload = _run(context, {context.transaction_id: context.code})

    assert payload["runtime_error"] == "AssertionError: too big"
    assert payload["run_id"] == context.transaction_id
    assert payload["runtime_error_line"] == 3
    assert payload["runtime_error_run_id"] == context.transaction_id
    assert payload["runtime_error_line_text"] == "assert value < 2, 'too big'"


def test_executor_locates_a_failure_inside_a_function_an_earlier_run_defined() -> None:
    """
    Contract: the innermost room-code frame wins - a failure inside a function an earlier run defined names that
    run and the line of its code, not the calling run.
    """
    earlier = _context("def check(value):\n    assert value == 2, 'value must be 2'\n    return value\n")
    later = _context("checked = check(3)\n")
    run_sources = {earlier.transaction_id: earlier.code, later.transaction_id: later.code}
    _run(earlier, run_sources)
    later.namespace.globals_dict["check"] = earlier.namespace.globals_dict["check"]

    payload = _run(later, run_sources)

    assert payload["run_id"] == later.transaction_id
    assert payload["runtime_error_run_id"] == earlier.transaction_id
    assert payload["runtime_error_line"] == 2
    assert payload["runtime_error_line_text"] == "assert value == 2, 'value must be 2'"


def test_executor_locates_a_library_failure_at_the_room_line_that_called_it() -> None:
    """
    Contract: a failure inside library code room code called is located at the room line that made the call.
    """
    context = _context("text = '{'\nparsed = parse(text)\n")
    context.namespace.globals_dict["parse"] = json.loads

    payload = _run(context, {context.transaction_id: context.code})

    assert str(payload["runtime_error"]).startswith("JSONDecodeError: ")
    assert payload["runtime_error_line"] == 2
    assert payload["runtime_error_run_id"] == context.transaction_id
    assert payload["runtime_error_line_text"] == "parsed = parse(text)"


def test_executor_locates_without_text_when_the_run_source_is_not_kept() -> None:
    """
    Contract: a run whose source the room did not keep (another room's run) is located by line and run id only.
    """
    context = _context("assert 1 == 2\n")

    payload = _run(context, {})

    assert payload["runtime_error_line"] == 1
    assert payload["runtime_error_run_id"] == context.transaction_id
    assert "runtime_error_line_text" not in payload


def test_executor_omits_the_text_when_the_kept_source_has_no_such_line() -> None:
    """
    Contract: the line's text is quoted only when the kept source has that line.
    """
    context = _context("x = 1\nassert x == 2\n")

    payload = _run(context, {context.transaction_id: "x = 1"})

    assert payload["runtime_error_line"] == 2
    assert "runtime_error_line_text" not in payload


def test_executor_adds_no_location_to_a_success() -> None:
    """
    Contract: a run that does not raise carries its `run_id` and no location keys.
    """
    context = _context("result = 7\n")

    payload = _run(context, {context.transaction_id: context.code})

    assert payload == {"accepted": True, "frame_name": "ops", "run_id": context.transaction_id, "result": 7}


@pytest.mark.parametrize(
    ("line", "run_id", "line_text", "expected_keys"),
    [
        pytest.param(4, "01JRUN", "assert x", {"runtime_error_line", "runtime_error_run_id", "runtime_error_line_text"},
                     id="all"),
        pytest.param(4, "01JRUN", None, {"runtime_error_line", "runtime_error_run_id"}, id="no-text"),
        pytest.param(None, None, None, set(), id="none"),
    ],
)
def test_runtime_failure_payload_carries_the_location_keys_that_are_set(
        line: Optional[int],
        run_id: Optional[str],
        line_text: Optional[str],
        expected_keys: Set[str],
) -> None:
    """
    Contract: `runtime_failed` takes the three location values and the payload adds each one only when it is set,
    beside `run_id`, which every payload carries.
    """
    result = CodegenExecutionResult.runtime_failed(
        frame_name="ops",
        runtime_error="AssertionError: ",
        transaction_id="01JTXN",
        runtime_error_line=line,
        runtime_error_run_id=run_id,
        runtime_error_line_text=line_text,
    )

    payload = result.to_payload()

    assert payload["run_id"] == "01JTXN"
    assert {key for key in payload if key.startswith("runtime_error_")} == expected_keys
    if line is not None:
        assert payload["runtime_error_line"] == line
        assert payload["runtime_error_run_id"] == run_id
    if line_text is not None:
        assert payload["runtime_error_line_text"] == line_text


def test_every_payload_carries_run_id_even_without_a_transaction() -> None:
    """
    Contract: `run_id` is on every execute payload - the transaction id, None only for a result built without one.
    """
    refused = CodegenExecutionResult.validation_failed(
        frame_name="ops",
        validation_issues=("bad",),
        transaction_id="01JTXN",
    )
    unnamed = CodegenExecutionResult.executed(frame_name="ops", result=1)

    assert refused.to_payload()["run_id"] == "01JTXN"
    assert unnamed.to_payload()["run_id"] is None


def test_codegen_system_keeps_the_source_of_each_accepted_run_only() -> None:
    """
    Contract: the engine keeps an accepted run's source under its transaction id - also when the run raises - and
    keeps nothing for a run validation refused.
    """
    system = CodegenSystem(rift=DetachedRiftProjectionOwner(), space=CodegenSpaceDouble())
    try:
        accepted_context, accepted = system.execute_codegen_request("result = 1\n", frame_name="ops")
        failed_context, failed = system.execute_codegen_request("assert 1 == 2\n", frame_name="ops")
        refused_context, refused = system.execute_codegen_request("import os\n", frame_name="ops")
        kept = dict(system._run_sources)
    finally:
        system.cleanup()

    assert accepted.accepted is True
    assert failed.runtime_error == "AssertionError: "
    assert refused.reason == "codegen_execution_validation_failed"
    assert kept == {
        accepted_context.transaction_id: "result = 1\n",
        failed_context.transaction_id: "assert 1 == 2\n",
    }
    assert refused_context.transaction_id not in kept


def test_codegen_system_cleanup_drops_the_kept_sources() -> None:
    """
    Contract: cleaning the engine (the room's removal) clears and deletes its kept sources; a second cleanup is a
    no-op.
    """
    system = CodegenSystem(rift=DetachedRiftProjectionOwner(), space=CodegenSpaceDouble())
    system.execute_codegen_request("result = 1\n", frame_name="ops")
    kept_sources = system._run_sources

    system.cleanup()
    system.cleanup()

    assert kept_sources == {}
    with pytest.raises(AttributeError):
        _ = system._run_sources
