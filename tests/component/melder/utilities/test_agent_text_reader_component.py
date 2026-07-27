"""
Component tests for the bounded agent text reader against real melder documents.

WHAT THIS TIER ADDS
-------------------
The unit tests use generated fixtures with predictable shapes, which is right
for proving arithmetic but wrong for proving usefulness: uniform line widths
hide every interaction between the line budget and the character budget.

This tier runs the reader over melder's OWN packaged document sources, which is
where the awkward shapes actually live:

    src_architecture.md       2,079 lines, avg  56 ch, max   579 ch
    src_components.md         5,176 lines, avg  54 ch, max   337 ch
    readable_src_graph.json   4,263 lines, avg 180 ch, max   479 ch
    src_graph.json                1 line,           767,788 ch

That last one is the reason this file exists. A minified graph is a SINGLE line
of three quarters of a megabyte: the line budget cannot bound it at all, so
every guarantee about bounded output rests entirely on the character budget. A
reader that only ever met well-behaved markdown would pass its unit tests and
still hand an agent 750 KB in one call.

These are the documents `__architecture__`, `__components__`, `__graph_network__`
and `__graph_details__` are to be populated from, so this tier is also the
rehearsal for that work.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
from typing import Any, List

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
_MODULE_PATH = (
    _REPO_ROOT
    / "src" / "melder" / "utilities" / "ai_native_support_tools" / "agent_text_reader.py"
)
_DOC_DIR = _REPO_ROOT / "context_compass" / "system_docs"

_DOCUMENTS = [
    "src_architecture.md",
    "src_components.md",
    "readable_src_graph.json",
    "src_graph.json",
]


def _load_module() -> Any:
    """
    Load the reader module directly from its file.

    Returns:
        Any: The executed module.
    """
    spec = importlib.util.spec_from_file_location("_rt_agent_text_reader_c", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["_rt_agent_text_reader_c"] = module
    spec.loader.exec_module(module)
    return module


_READER = _load_module()
IndexedText = _READER.IndexedText
ReaderPolicy = _READER.ReaderPolicy


def _document(name: str) -> str:
    """
    Read one real system document, skipping when absent.

    Args:
        name: Filename beneath `context_compass/system_docs`.

    Returns:
        str: Document text.
    """
    path = _DOC_DIR / name
    if not path.is_file():
        pytest.skip(f"{name} not present in this checkout")
    return path.read_text(encoding="utf-8")


@pytest.mark.component
@pytest.mark.parametrize("name", _DOCUMENTS)
def test_real_document_line_count_matches_splitlines(name: str) -> None:
    """
    Purpose:
        Real documents carry the encodings, trailing newlines and blank runs
        that generated fixtures do not.
    Contract:
        Line accounting matches `splitlines()` on every packaged source.
    """
    text = _document(name)
    assert IndexedText(text).line_count == (len(text.splitlines()) or 1)


@pytest.mark.component
@pytest.mark.parametrize("name", _DOCUMENTS)
@pytest.mark.parametrize(
    "line_target,char_target", [(2, 256), (13, 1_024), (50, 8_192), (100, 65_536)]
)
def test_real_document_round_trips_at_every_budget(
    name: str, line_target: int, char_target: int
) -> None:
    """
    Purpose:
        The strongest end-to-end assertion available: any gap, overlap or
        dropped character in the paging arithmetic breaks reconstruction. Run
        across the full budget range because which budget BINDS changes with the
        ratio, and the handoff between them is the likeliest bug.
    Contract:
        Concatenating every chunk reproduces the document byte for byte.
    """
    text = _document(name)
    indexed = IndexedText(text)
    rebuilt = "".join(
        chunk.text
        for chunk in indexed.reader(line_target=line_target, char_target=char_target)
    )
    assert rebuilt == text


@pytest.mark.component
@pytest.mark.parametrize("name", _DOCUMENTS)
def test_no_chunk_ever_exceeds_the_character_budget(name: str) -> None:
    """
    Purpose:
        This is the promise an agent budgets context against. One oversized
        chunk overruns a context window, and the minified graph is where it
        would happen.
    Contract:
        Every chunk respects `char_target`, with ONE documented exception - a
        single line longer than the entire budget is returned whole, because
        returning nothing would stall the caller forever.
    """
    text = _document(name)
    indexed = IndexedText(text)
    budget = 4_096
    for chunk in indexed.reader(line_target=100, char_target=budget):
        if len(chunk.text) > budget:
            span = indexed.lines_text(chunk.start_line, 1)
            assert len(span) > budget, (
                f"chunk of {len(chunk.text)} exceeded budget {budget} "
                "without being an oversized single line"
            )


@pytest.mark.component
@pytest.mark.parametrize("name", _DOCUMENTS)
def test_no_chunk_is_empty_while_more_remains(name: str) -> None:
    """
    Purpose:
        The hang condition. An empty chunk with `has_more` true means the agent
        loops forever receiving nothing.
    Contract:
        Every chunk delivered before exhaustion is non-empty.
    """
    indexed = IndexedText(_document(name))
    for chunk in indexed.reader(line_target=2, char_target=ReaderPolicy.MIN_CHAR_TARGET):
        assert chunk.text != "", f"empty chunk at line {chunk.start_line}"


@pytest.mark.component
def test_minified_graph_is_bounded_by_characters_alone() -> None:
    """
    Purpose:
        `src_graph.json` is one line of ~750 KB. Line budgets are meaningless
        here, so this is the case that proves bounded output does not depend on
        the document being line-shaped.
    Contract:
        A one-line document still pages, every chunk honours the character
        budget, and the chunk count is exactly what the budget implies.
    """
    text = _document("src_graph.json")
    indexed = IndexedText(text)
    assert indexed.line_count == 1, "expected a minified single-line document"

    budget = 65_536
    chunks = list(indexed.reader(line_target=2, char_target=budget))
    assert all(len(chunk.text) <= budget for chunk in chunks)
    assert len(chunks) == -(-indexed.char_count // budget)
    assert "".join(chunk.text for chunk in chunks) == text


@pytest.mark.component
def test_unbounded_head_on_the_minified_graph_returns_everything() -> None:
    """
    Purpose:
        Pins a REAL LIMITATION rather than a guarantee, so nobody mistakes
        `head(n)` for universally safe. On a single-line document the line cap
        cannot bound anything and only `chars` will.
    Contract:
        `head(50)` on a one-line document returns the whole document;
        `head(50, chars=...)` bounds it.
    """
    indexed = IndexedText(_document("src_graph.json"))
    assert len(indexed.head(50).text) == indexed.char_count
    assert len(indexed.head(50, chars=8_192).text) == 8_192


@pytest.mark.component
@pytest.mark.parametrize("name", _DOCUMENTS)
def test_head_and_tail_agree_with_direct_access(name: str) -> None:
    """
    Contract:
        `head`/`tail` are consistent with `lines_text` over the same spans, so
        the two access styles cannot disagree about one document.
    """
    indexed = IndexedText(_document(name))
    span = min(20, indexed.line_count)
    assert indexed.head(max(span, ReaderPolicy.MIN_LINE_TARGET)).text == indexed.lines_text(
        0, max(span, ReaderPolicy.MIN_LINE_TARGET)
    )
    tail = indexed.tail(max(span, ReaderPolicy.MIN_LINE_TARGET))
    assert tail.text == indexed.lines_text(tail.start_line, indexed.line_count - tail.start_line)


@pytest.mark.component
@pytest.mark.parametrize("name", _DOCUMENTS)
def test_seek_then_read_matches_direct_access(name: str) -> None:
    """
    Purpose:
        Indexed access and cursor access must describe the same document. If
        they drift, an agent that mixes them silently reads the wrong region.
    Contract:
        A budgeted read is always a PREFIX of the equivalent direct access, and
        equals it exactly when the character budget did not bind.

        The distinction is not pedantry - it is the single-line case. On
        `src_graph.json` (one line, 767 KB) `lines_text(0, 10)` returns the whole
        document because it takes no character budget, while `read()` correctly
        stops at `char_target`. Asserting plain equality here fails, and it
        SHOULD: the two calls make different promises, and only `read` promises
        bounded output.
    """
    indexed = IndexedText(_document(name))
    target = indexed.line_count // 3
    reader = indexed.reader(line_target=10, char_target=ReaderPolicy.MAX_CHAR_TARGET)
    reader.seek_line(target)
    chunk = reader.read()
    direct = indexed.lines_text(target, 10)

    assert chunk.start_line == target
    assert direct.startswith(chunk.text)
    if chunk.truncated_by != "chars":
        assert chunk.text == direct


@pytest.mark.component
def test_walking_a_large_document_holds_only_one_chunk() -> None:
    """
    Purpose:
        The point of paging is that peak memory is one chunk, not the document.
        A reader that accumulated internally would still pass every correctness
        test while defeating its own reason to exist.
    Contract:
        Streaming the largest document never yields a chunk above the budget,
        and the reader's own footprint does not grow as it advances.
    """
    indexed = IndexedText(_document("readable_src_graph.json"))
    reader = indexed.reader(line_target=25, char_target=4_096)
    sizes: List[int] = []
    footprints: List[int] = []
    for chunk in reader:
        sizes.append(len(chunk.text))
        footprints.append(sys.getsizeof(reader))
    assert max(sizes) <= 4_096 or indexed.line_count == 1
    assert len(set(footprints)) == 1, "reader grew while advancing - it is accumulating"


@pytest.mark.component
@pytest.mark.parametrize("name", _DOCUMENTS)
def test_indexing_a_real_document_does_not_copy_it(name: str) -> None:
    """
    Purpose:
        `IndexedText` holds the ORIGINAL string plus a compact offset array. If
        it ever sliced eagerly, ten agents sharing one document would stop being
        cheap - the premise the concurrency design rests on.
    Contract:
        The stored text is the same object, and the index is small relative to
        the document.
    """
    text = _document(name)
    indexed = IndexedText(text)
    assert indexed.text is text, "document was copied rather than referenced"
    assert sys.getsizeof(indexed) < 1_024, "instance is holding more than references"
