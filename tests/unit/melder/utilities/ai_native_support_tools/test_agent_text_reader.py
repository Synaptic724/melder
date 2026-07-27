"""
Unit tests for the bounded agent text reader.

WHAT THESE TARGET
-----------------
Three properties, in priority order:

1. LINE ACCOUNTING IS EXACT. Every offset, span and line number the reader
   reports is derived from one `array` index built by hand, so an off-by-one
   there is silent and poisons every consumer. Line counts are asserted against
   `str.splitlines()` as ground truth rather than against hand-written numbers.

2. BUDGETS ARE HONOURED AND BOUNDED. The type exists to stop one call returning
   a whole document. A budget that silently clamps instead of raising, or a read
   that overruns, defeats the entire purpose.

3. PROGRESS IS ALWAYS POSSIBLE. A chunk that is empty while `has_more` is true
   is a spin: the agent asks again, gets nothing again, forever. This is the one
   failure mode that hangs a caller rather than merely returning wrong data, and
   it is reachable whenever a single line exceeds the character budget.

The module is loaded BY FILE PATH. Importing `melder.utilities...` would boot
`Aether()` through the package root, which these tests do not need and which
would make a pure-data unit test depend on the whole runtime.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
from typing import Any

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[5]
_MODULE_PATH = (
    _REPO_ROOT
    / "src" / "melder" / "utilities" / "ai_native_support_tools" / "agent_text_reader.py"
)


def _load_module() -> Any:
    """
    Load the reader module directly from its file.

    Returns:
        Any: The executed module.
    """
    spec = importlib.util.spec_from_file_location("_rt_agent_text_reader", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["_rt_agent_text_reader"] = module
    spec.loader.exec_module(module)
    return module


_READER = _load_module()
IndexedText = _READER.IndexedText
AgentTextReader = _READER.AgentTextReader
ReaderPolicy = _READER.ReaderPolicy
TextChunk = _READER.TextChunk


def _numbered(count: int, width: int = 4) -> str:
    """
    Build a deterministic multi-line document.

    Args:
        count: How many lines.
        width: Characters of padding per line, for predictable widths.

    Returns:
        str: Newline-joined document without a trailing newline.
    """
    return "\n".join(f"L{index:0{width}d}" for index in range(count))


# Line accounting ------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    ["", "a", "a\n", "a\nb", "a\nb\n", "\n", "\n\n", "a\n\nb\n", "\n\n\n", "x" * 500],
)
def test_line_count_matches_splitlines(text: str) -> None:
    """
    Purpose:
        `splitlines()` is the behaviour every editor, diff and reviewer agrees
        on. The offset index is a hand-rolled reimplementation of that, and the
        trailing-newline case in particular is where such code goes wrong.
    Contract:
        Line count equals `len(text.splitlines())`, with an empty document
        counting as one line the way an empty file reads.
    """
    expected = len(text.splitlines()) or 1
    assert IndexedText(text).line_count == expected


@pytest.mark.parametrize("text", ["", "a", "a\nb\nc", "a\nb\nc\n", "\n\n"])
def test_every_line_round_trips_through_the_index(text: str) -> None:
    """
    Purpose:
        Catches an off-by-one in the offset array that a count check alone would
        miss - the right NUMBER of lines with the wrong BOUNDARIES.
    Contract:
        Concatenating every `line_text` reproduces the document exactly.
    """
    indexed = IndexedText(text)
    rebuilt = "".join(indexed.line_text(i) for i in range(indexed.line_count))
    assert rebuilt == text


def test_line_start_of_line_count_is_the_document_end() -> None:
    """
    Purpose:
        The end sentinel is what lets spans be end-exclusive with no special
        case for the final line. If it is missing, the last line is unreadable.
    Contract:
        `line_start(line_count)` returns `char_count`.
    """
    indexed = IndexedText("a\nb\nc")
    assert indexed.line_start(indexed.line_count) == indexed.char_count


@pytest.mark.parametrize("bad", [-1, 99])
def test_line_start_rejects_out_of_range(bad: int) -> None:
    """
    Purpose:
        Silent clamping here would produce a plausible-looking chunk from the
        wrong part of the document.
    Contract:
        Out-of-range lines raise `IndexError`.
    """
    with pytest.raises(IndexError):
        IndexedText("a\nb").line_start(bad)


def test_line_of_offset_agrees_with_line_starts() -> None:
    """
    Purpose:
        `line_of_offset` is a bisect over the index and is what keeps reported
        line numbers honest after a character-bounded read stops mid-line.
    Contract:
        Every offset inside line `i` maps back to `i`.
    """
    indexed = IndexedText(_numbered(50))
    for line in range(indexed.line_count):
        start = indexed.line_start(line)
        stop = indexed.line_start(line + 1)
        for offset in {start, (start + stop) // 2, stop - 1}:
            assert indexed.line_of_offset(offset) == line


def test_rejects_bytes_rather_than_indexing_them() -> None:
    """
    Purpose:
        `bytes` supports `find` and slicing, so it would index cleanly and
        produce byte offsets that only diverge from character offsets once
        non-ASCII appears - a bug that surfaces far from its cause.
    Contract:
        Non-`str` input raises `TypeError` at construction.
    """
    with pytest.raises(TypeError):
        IndexedText(b"a\nb")


def test_non_ascii_offsets_are_characters_not_bytes() -> None:
    """
    Purpose:
        The above rejection only matters if `str` offsets really are character
        offsets. Multi-byte content is where an index would betray that.
    Contract:
        Character counts and slices are correct for non-ASCII text.
    """
    indexed = IndexedText("héllo\nwörld\n日本語")
    assert indexed.line_count == 3
    assert indexed.char_count == len("héllo\nwörld\n日本語")
    assert indexed.line_text(2) == "日本語"


# Budgets --------------------------------------------------------------------


@pytest.mark.parametrize("bad", [0, 1, 101, -5, True])
def test_line_target_outside_bounds_raises(bad: Any) -> None:
    """
    Purpose:
        The 2-100 bound is the mechanism that stops a "read" becoming "return
        everything". Clamping instead of raising would hide a caller's mistake
        and hand back a surprising amount of text.
    Contract:
        Out-of-range line targets raise `ValueError`, and `True` is rejected
        despite being an `int` subclass.
    """
    with pytest.raises(ValueError):
        IndexedText(_numbered(10)).reader(line_target=bad)


@pytest.mark.parametrize(
    "good", [ReaderPolicy.MIN_LINE_TARGET, 50, ReaderPolicy.MAX_LINE_TARGET]
)
def test_line_target_bounds_are_inclusive(good: int) -> None:
    """
    Purpose:
        An exclusive bound would make the documented range a lie.
    Contract:
        Both endpoints of the documented range are accepted.
    """
    assert IndexedText(_numbered(10)).reader(line_target=good).line_target == good


@pytest.mark.parametrize(
    "bad", [0, ReaderPolicy.MIN_CHAR_TARGET - 1, ReaderPolicy.MAX_CHAR_TARGET + 1]
)
def test_char_target_outside_bounds_raises(bad: int) -> None:
    """
    Contract:
        Out-of-range character targets raise `ValueError`.
    """
    with pytest.raises(ValueError):
        IndexedText(_numbered(10)).reader(char_target=bad)


def test_read_stops_at_the_line_budget_and_says_so() -> None:
    """
    Contract:
        A line-bounded read returns exactly `line_target` lines and reports
        `truncated_by == "lines"`.
    """
    reader = IndexedText(_numbered(500)).reader(line_target=10, char_target=65_536)
    chunk = reader.read()
    assert len(chunk.text.splitlines()) == 10
    assert chunk.truncated_by == "lines"
    assert chunk.has_more is True


def test_read_stops_at_the_char_budget_and_says_so() -> None:
    """
    Purpose:
        `truncated_by` exists so an agent can widen the budget that actually
        bound rather than guessing. That is only useful if it is accurate when
        the CHARACTER budget is the binding one.
    Contract:
        A character-bounded read returns exactly `char_target` characters and
        reports `truncated_by == "chars"`.
    """
    reader = IndexedText(_numbered(5_000)).reader(line_target=100, char_target=256)
    chunk = reader.read()
    assert len(chunk.text) == 256
    assert chunk.truncated_by == "chars"


def test_final_chunk_reports_end_and_no_more() -> None:
    """
    Contract:
        The read that consumes the tail reports `truncated_by == "end"` and
        `has_more is False`.
    """
    reader = IndexedText(_numbered(6)).reader(line_target=100, char_target=65_536)
    chunk = reader.read()
    assert chunk.truncated_by == "end"
    assert chunk.has_more is False


def test_per_call_budget_does_not_change_the_standing_one() -> None:
    """
    Purpose:
        A one-off override that mutated the reader would silently change every
        subsequent read - the kind of state bug that only shows up in the third
        call.
    Contract:
        `read(line_target=...)` affects that call only.
    """
    reader = IndexedText(_numbered(500)).reader(line_target=10, char_target=65_536)
    reader.read(line_target=3)
    assert reader.line_target == 10
    assert len(reader.read().text.splitlines()) == 10


def test_set_targets_changes_the_standing_budget_without_moving_the_cursor() -> None:
    """
    Contract:
        `set_targets` updates budgets and leaves position untouched.
    """
    reader = IndexedText(_numbered(500)).reader(line_target=10, char_target=65_536)
    reader.read()
    reader.set_targets(line_target=25)
    assert reader.line_target == 25
    assert reader.current_line == 10


# Cursor behaviour -----------------------------------------------------------


def test_read_advances_and_peek_does_not() -> None:
    """
    Purpose:
        This pair IS the "call it twice for the next set" contract.
    Contract:
        Consecutive `read` calls return consecutive chunks; `peek` returns what
        the next `read` will return, without moving.
    """
    reader = IndexedText(_numbered(500)).reader(line_target=10, char_target=65_536)
    first = reader.read()
    peeked = reader.peek()
    second = reader.read()
    assert peeked.text == second.text
    assert first.end_char == second.start_char
    assert first.text != second.text


def test_reading_the_whole_document_reconstructs_it_exactly() -> None:
    """
    Purpose:
        The strongest single assertion available: any gap, overlap or dropped
        character anywhere in the paging arithmetic breaks it.
    Contract:
        Concatenating every chunk equals the original document.
    """
    text = _numbered(1_000)
    indexed = IndexedText(text)
    assert "".join(c.text for c in indexed.reader(line_target=7, char_target=256)) == text


def test_reading_past_the_end_returns_empty_rather_than_raising() -> None:
    """
    Purpose:
        Paging off the end is the NORMAL way a loop finishes. Requiring a try
        block for it would push that burden onto every caller.
    Contract:
        Reads past the end return an empty, exhausted chunk repeatedly.
    """
    reader = IndexedText("a\nb").reader(line_target=100, char_target=65_536)
    reader.read()
    for _ in range(3):
        chunk = reader.read()
        assert chunk.text == ""
        assert chunk.has_more is False
    assert reader.exhausted is True


def test_seek_and_reset_reposition_the_cursor() -> None:
    """
    Contract:
        `seek_line` moves to a line start; `reset` returns to the beginning.
    """
    reader = IndexedText(_numbered(500)).reader(line_target=10, char_target=65_536)
    reader.seek_line(100)
    assert reader.current_line == 100
    assert reader.read().start_line == 100
    reader.reset()
    assert reader.current_line == 0 and reader.current_offset == 0


def test_remaining_counts_shrink_to_zero() -> None:
    """
    Contract:
        `remaining_lines` and `remaining_chars` track consumption and reach zero
        exactly when `exhausted` becomes true.
    """
    indexed = IndexedText(_numbered(100))
    reader = indexed.reader(line_target=10, char_target=65_536)
    assert reader.remaining_lines == 100
    reader.read()
    assert reader.remaining_lines == 90
    for _ in reader:
        pass
    assert reader.remaining_lines == 0 and reader.remaining_chars == 0


def test_stream_resumes_rather_than_restarting() -> None:
    """
    Purpose:
        `stream()` shares the cursor deliberately. If it restarted, mixing it
        with `read()` would silently re-deliver content the agent already paid
        for.
    Contract:
        Streaming a partly-read reader yields only the remainder, and breaking
        out mid-stream leaves the cursor where it stopped.
    """
    reader = IndexedText(_numbered(100)).reader(line_target=10, char_target=65_536)
    reader.read()
    collected = []
    for chunk in reader.stream():
        collected.append(chunk)
        if len(collected) == 2:
            break
    assert collected[0].start_line == 10
    assert reader.read().start_line == 30


def test_iteration_and_manual_reads_share_one_cursor() -> None:
    """
    Contract:
        `for chunk in reader` and `reader.read()` traverse the same position.
    """
    reader = IndexedText(_numbered(100)).reader(line_target=10, char_target=65_536)
    assert next(iter(reader)).start_line == 0
    assert reader.read().start_line == 10


def test_stream_chars_and_stream_lines_do_not_mutate_standing_budgets() -> None:
    """
    Contract:
        The mode-specific generators apply their bound per call and leave the
        reader's own budgets alone.
    """
    reader = IndexedText(_numbered(500)).reader(line_target=10, char_target=1_024)
    next(reader.stream_chars(512))
    next(reader.stream_lines(3))
    assert reader.line_target == 10 and reader.char_target == 1_024


# Progress guarantee ---------------------------------------------------------


def test_a_line_longer_than_the_char_budget_still_advances() -> None:
    """
    Purpose:
        THE hang. Returning an empty chunk with `has_more=True` means the agent
        asks again, gets nothing again, and never terminates. Progress must beat
        the budget.
    Contract:
        A single line far longer than `char_target` still yields a non-empty
        chunk, and full traversal terminates and reconstructs the document.
    """
    text = "x" * 5_000 + "\nshort\n"
    indexed = IndexedText(text)
    reader = indexed.reader(line_target=2, char_target=ReaderPolicy.MIN_CHAR_TARGET)
    chunks = []
    for chunk in reader:
        assert chunk.text != "", "empty chunk while advancing - caller would spin"
        chunks.append(chunk)
        assert len(chunks) < 200, "did not terminate"
    assert "".join(c.text for c in chunks) == text


def test_single_line_document_pages_by_characters() -> None:
    """
    Purpose:
        A minified JSON document is one line of ~750 KB in this repo. Line
        budgets cannot bound it; only the character budget can.
    Contract:
        A one-line document still pages, and reconstructs exactly.
    """
    text = "z" * 20_000
    indexed = IndexedText(text)
    assert indexed.line_count == 1
    chunks = list(indexed.reader(line_target=2, char_target=4_096))
    assert len(chunks) == 5
    assert "".join(c.text for c in chunks) == text


# head / tail ----------------------------------------------------------------


def test_head_returns_the_first_lines() -> None:
    """
    Contract:
        `head(n)` returns the leading `n` lines and reports `has_more`.
    """
    chunk = IndexedText(_numbered(100)).head(5)
    assert chunk.text.splitlines() == ["L0000", "L0001", "L0002", "L0003", "L0004"]
    assert (chunk.start_line, chunk.end_line, chunk.has_more) == (0, 5, True)


def test_tail_returns_the_last_lines() -> None:
    """
    Contract:
        `tail(n)` returns the trailing `n` lines and never reports `has_more`.
    """
    chunk = IndexedText(_numbered(100)).tail(5)
    assert chunk.text.splitlines() == ["L0095", "L0096", "L0097", "L0098", "L0099"]
    assert (chunk.start_line, chunk.end_line, chunk.has_more) == (95, 100, False)


def test_head_and_tail_trim_from_opposite_ends() -> None:
    """
    Purpose:
        The asymmetry is the point: each trims the side furthest from what was
        asked for. Getting it backwards would return the middle of the document
        for both.
    Contract:
        `head(chars=)` keeps the beginning; `tail(chars=)` keeps the end.
    """
    indexed = IndexedText("\n".join("x" * 100 for _ in range(50)))
    head = indexed.head(20, chars=256)
    tail = indexed.tail(20, chars=256)
    assert head.start_char == 0 and len(head.text) == 256
    assert tail.end_char == indexed.char_count and len(tail.text) == 256
    assert head.truncated_by == "chars" and tail.truncated_by == "chars"


def test_head_and_tail_of_a_short_document_are_the_whole_document() -> None:
    """
    Contract:
        Asking for more lines than exist clamps rather than raising.
    """
    indexed = IndexedText("a\nb\n")
    assert indexed.head(50).text == "a\nb\n"
    assert indexed.tail(50).text == "a\nb\n"


@pytest.mark.parametrize("bad", [0, 1, 101, -1])
def test_head_and_tail_enforce_the_same_bounds(bad: int) -> None:
    """
    Purpose:
        An unbounded `head` on a one-line 750 KB document returns the whole
        file. The bound is the only thing preventing that.
    Contract:
        Both reject out-of-range line counts.
    """
    indexed = IndexedText(_numbered(10))
    with pytest.raises(ValueError):
        indexed.head(bad)
    with pytest.raises(ValueError):
        indexed.tail(bad)


def test_head_and_tail_do_not_move_the_cursor() -> None:
    """
    Purpose:
        An agent orienting itself mid-document must not lose its place doing so.
    Contract:
        Neither delegate disturbs position.
    """
    reader = IndexedText(_numbered(100)).reader(line_target=10, char_target=65_536)
    reader.read()
    reader.head(5)
    reader.tail(5)
    assert reader.current_line == 10
    assert reader.read().start_line == 10


# Direct access --------------------------------------------------------------


def test_lines_text_clamps_past_the_end_instead_of_raising() -> None:
    """
    Purpose:
        Overrunning is a normal outcome of paging by index; raising would force
        callers to pre-check bounds they already gave up tracking.
    Contract:
        Overrun returns what exists; a start past the end returns `""`.
    """
    indexed = IndexedText(_numbered(100))
    assert len(indexed.lines_text(90, 100).splitlines()) == 10
    assert indexed.lines_text(500, 10) == ""


@pytest.mark.parametrize("start,count", [(-1, 5), (0, 0), (0, -3)])
def test_lines_text_rejects_nonsense_spans(start: int, count: int) -> None:
    """
    Contract:
        Negative starts and non-positive counts raise `ValueError`.
    """
    with pytest.raises(ValueError):
        IndexedText(_numbered(10)).lines_text(start, count)


def test_split_lines_strips_newlines_and_defaults_bounded() -> None:
    """
    Purpose:
        `split_lines` materializes real `str` objects, which is exactly the
        GC-tracked cost the index avoids for the document. Defaulting to
        unbounded would reintroduce it.
    Contract:
        Newlines are stripped, and the default span is capped by policy.
    """
    indexed = IndexedText(_numbered(500))
    assert indexed.split_lines(0, 3) == ["L0000", "L0001", "L0002"]
    assert len(indexed.split_lines()) == ReaderPolicy.MAX_LINE_TARGET


def test_reader_rejects_a_non_indexed_document() -> None:
    """
    Contract:
        Constructing a reader over a raw `str` raises `TypeError` rather than
        failing later inside an offset lookup.
    """
    with pytest.raises(TypeError):
        AgentTextReader("not indexed")
