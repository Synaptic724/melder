"""
Unit contracts for room code's captured `print` output (GitHub #337, task 2).

Purpose:
    A codegen room replaces room code's `print` with `CodegenOutputCapture.capture_print`, so what the code prints
    returns in `execute_codegen`'s payload under `output` instead of reaching the host's stdout. These tests pin the
    capture's `print` semantics, its limit and truncation line, its lock under concurrent prints and its cleanup; the
    execution result's `output` field and payload key; and the namespace that owns the capture.
"""
import io
import threading
from typing import List

import pytest

from melder.nexus.rift.codegen_system.execution.codegen_execution_result import (
    CodegenExecutionResult,
)
from melder.nexus.rift.codegen_system.namespace.codegen_namespace import (
    CodegenNamespace,
)
from melder.nexus.rift.codegen_system.namespace.codegen_output_capture import (
    CodegenOutputCapture,
)
from tests._codegen_system_support import build_namespace_configuration


def test_capture_print_joins_values_with_the_default_sep_and_end() -> None:
    """
    Contract: `capture_print(*values)` keeps what the builtin would write - each value's `str`, joined by a space,
    ended by a newline.
    """
    capture = CodegenOutputCapture(limit=1000)

    capture.capture_print(1, "a", None, [2])

    assert capture.output == "1 a None [2]\n"


@pytest.mark.parametrize(
    ("sep", "end", "expected"),
    [
        pytest.param("-", "!", "a-b!", id="custom"),
        pytest.param(None, None, "a b\n", id="none-means-the-defaults"),
        pytest.param("", "", "ab", id="empty"),
    ],
)
def test_capture_print_honours_sep_and_end(sep: object, end: object, expected: str) -> None:
    """
    Contract: `sep` and `end` behave as the builtin's - a string is used as given and None means the default.
    """
    capture = CodegenOutputCapture(limit=1000)

    capture.capture_print("a", "b", sep=sep, end=end)

    assert capture.output == expected


@pytest.mark.parametrize(
    ("keyword", "message"),
    [
        pytest.param("sep", "sep must be None or a string, not int", id="sep"),
        pytest.param("end", "end must be None or a string, not int", id="end"),
    ],
)
def test_capture_print_refuses_a_non_string_sep_or_end(keyword: str, message: str) -> None:
    """
    Contract: a `sep` or `end` that is neither None nor a string raises TypeError with the builtin's message, and
    nothing is kept.
    """
    capture = CodegenOutputCapture(limit=1000)

    with pytest.raises(TypeError, match=message):
        capture.capture_print("a", **{keyword: 5})

    assert capture.output == ""


def test_capture_print_writes_to_an_explicit_file_and_keeps_nothing() -> None:
    """
    Contract: `print(..., file=x)` with an explicit file writes to that file as the builtin does; the capture keeps
    only what would have gone to stdout.
    """
    capture = CodegenOutputCapture(limit=1000)
    target = io.StringIO()

    capture.capture_print("to", "file", sep="+", file=target)

    assert target.getvalue() == "to+file\n"
    assert capture.output == ""


def test_output_at_exactly_the_limit_has_no_truncation_line() -> None:
    """
    Contract: text that fills the limit exactly is kept whole, with no truncation line.
    """
    capture = CodegenOutputCapture(limit=4)

    capture.capture_print("abc")

    assert capture.output == "abc\n"


def test_output_one_character_past_the_limit_counts_the_dropped_character() -> None:
    """
    Contract: one character past the limit is dropped and counted; the kept text gets a newline before the
    truncation line when it does not end with one.
    """
    capture = CodegenOutputCapture(limit=3)

    capture.capture_print("abc")

    assert capture.output == "abc\n[output truncated: 1 more characters not kept]\n"


def test_truncation_keeps_the_first_characters_and_counts_every_later_print() -> None:
    """
    Contract: once the limit is reached, every later print is counted, not kept; a kept text that ends with a
    newline takes the truncation line directly.
    """
    capture = CodegenOutputCapture(limit=6)

    capture.capture_print("12345")
    capture.capture_print("678")
    capture.capture_print("9")

    assert capture.output == "12345\n[output truncated: 6 more characters not kept]\n"


@pytest.mark.parametrize(
    ("limit", "error_type"),
    [
        pytest.param(0, ValueError, id="zero"),
        pytest.param(-1, ValueError, id="negative"),
        pytest.param(True, TypeError, id="bool"),
        pytest.param(1.5, TypeError, id="float"),
    ],
)
def test_capture_refuses_a_limit_that_is_not_a_positive_int(limit: object, error_type: type) -> None:
    """
    Contract: the limit is an int of at least 1; a bool, a float or a value below 1 is refused at construction.
    """
    with pytest.raises(error_type):
        CodegenOutputCapture(limit=limit)


def test_concurrent_prints_lose_no_text_below_the_limit() -> None:
    """
    Contract: the capture's lock keeps every line whole and loses none when room code prints from several threads
    at once (run with the GIL off).
    """
    capture = CodegenOutputCapture(limit=1_000_000)
    barrier = threading.Barrier(8)

    def print_lines() -> None:
        barrier.wait()
        for _ in range(200):
            capture.capture_print("ab", "cd")

    threads: List[threading.Thread] = [threading.Thread(target=print_lines) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    lines = capture.output.splitlines()
    assert len(lines) == 1600
    assert set(lines) == {"ab cd"}


def test_capture_cleanup_is_idempotent_and_ends_its_output() -> None:
    """
    Contract: cleanup may run twice; after it the capture refuses reads and prints with RuntimeError.
    """
    capture = CodegenOutputCapture(limit=10)
    capture.capture_print("kept")

    capture.cleanup()
    capture.cleanup()

    with pytest.raises(RuntimeError):
        _ = capture.output
    with pytest.raises(RuntimeError):
        capture.capture_print("late")


def test_execution_result_payload_carries_output_only_when_text_was_printed() -> None:
    """
    Contract: `executed` and `runtime_failed` carry the printed text as `output`; the payload adds an `output` key
    only when it is not empty.
    """
    executed = CodegenExecutionResult.executed(frame_name="ops", result=1, output="hi\n")
    failed = CodegenExecutionResult.runtime_failed(
        frame_name="ops",
        runtime_error="ValueError: boom",
        output="before\n",
    )
    silent = CodegenExecutionResult.executed(frame_name="ops", result=1)

    assert executed.output == "hi\n"
    assert executed.to_payload() == {"accepted": True, "frame_name": "ops", "output": "hi\n", "result": 1}
    assert failed.to_payload()["output"] == "before\n"
    assert silent.output == ""
    assert "output" not in silent.to_payload()


def test_namespace_without_a_capture_reports_no_output() -> None:
    """
    Contract: a namespace built without a capture (a room with capture off) answers `get_output()` with "".
    """
    namespace = CodegenNamespace(configuration=build_namespace_configuration(frame_name="ops"))

    assert namespace.get_output() == ""


def test_namespace_reports_and_cleans_its_capture() -> None:
    """
    Contract: the namespace reports its capture's text through `get_output()` and cleans the capture it owns when it
    is cleaned.
    """
    capture = CodegenOutputCapture(limit=100)
    namespace = CodegenNamespace(
        configuration=build_namespace_configuration(frame_name="ops"),
        output_capture=capture,
    )
    capture.capture_print("from room code")

    assert namespace.get_output() == "from room code\n"

    namespace.cleanup()

    with pytest.raises(RuntimeError):
        _ = capture.output
