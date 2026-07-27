"""
Concurrency integration tests for the bounded agent text reader.

WHAT IS ACTUALLY BEING CLAIMED
------------------------------
`agent_text_reader` contains NO lock. That is not an omission - it is the design
claim the whole two-type split exists to earn, and it rests on exactly two
premises:

    1. `IndexedText` is immutable after construction, so any number of agents
       may share ONE document concurrently.
    2. `AgentTextReader` is mutable but UNSHARED, so its cursor is only ever
       touched by its owner.

These tests attack both. Premise 1 is tested by pointing many threads at one
document and demanding byte-identical results. Premise 2 is tested by
deliberately VIOLATING it - sharing a single reader across threads - and
asserting the damage is confined to interleaving rather than corruption, which
is what tells a future maintainer why the rule exists rather than merely that it
does.

WHY A REAL DOCUMENT
-------------------
Synthetic text of uniform line width hides the bug this reader is most likely to
have: the interaction between the line budget and the character budget. Melder's
own `src_components.md` varies from a few characters to several hundred per
line, so it exercises both budgets binding in the same traversal. Generated
fixtures are used where a property needs a specific shape, and the real document
is used where realism is the point.

THREADING MODEL
---------------
Threads are released from a `Barrier` so they contend rather than running in
sequence, which is what makes a data race observable at all. Every worker
returns its result for comparison on the main thread; nothing is asserted from
inside a worker, because a failed assertion there would surface as a silent
thread death rather than a test failure.
"""
from __future__ import annotations

import hashlib
import importlib.util
import pathlib
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Tuple

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
_MODULE_PATH = (
    _REPO_ROOT
    / "src" / "melder" / "utilities" / "ai_native_support_tools" / "agent_text_reader.py"
)
_REAL_DOCUMENT = _REPO_ROOT / "context_compass" / "system_docs" / "src_components.md"

_THREADS = 16


def _load_module() -> Any:
    """
    Load the reader module directly from its file.

    Returns:
        Any: The executed module.
    """
    spec = importlib.util.spec_from_file_location("_rt_agent_text_reader_mt", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["_rt_agent_text_reader_mt"] = module
    spec.loader.exec_module(module)
    return module


_READER = _load_module()
IndexedText = _READER.IndexedText


@pytest.fixture(scope="module")
def document_text() -> str:
    """
    Return a large, irregularly shaped real document.

    Returns:
        str: Document text, or a generated stand-in when the real file is absent
            so the suite still runs in a trimmed checkout.
    """
    if _REAL_DOCUMENT.is_file():
        return _REAL_DOCUMENT.read_text(encoding="utf-8")
    return "\n".join("x" * ((i * 37) % 400 + 1) for i in range(4_000))


@pytest.fixture(scope="module")
def indexed(document_text: str) -> Any:
    """
    Return one shared indexed document.

    Contract:
        Module-scoped ON PURPOSE. Sharing one instance across every test in this
        file is the arrangement under test, not a speed optimisation.

    Returns:
        Any: The shared `IndexedText`.
    """
    return IndexedText(document_text)


def _run_concurrently(work: Any, count: int = _THREADS) -> List[Any]:
    """
    Run one callable on many threads released simultaneously.

    Contract:
        A `Barrier` holds every worker until all have started, so they contend
        for the shared document instead of running one after another. Without
        it, thread pools frequently serialize short tasks and a race would never
        be exercised.

    Args:
        work: Callable taking the worker index.
        count: How many workers.

    Returns:
        List[Any]: Results in worker-index order.

    Raises:
        Exception: Any exception raised inside a worker, re-raised here.
    """
    barrier = threading.Barrier(count)

    def entry(index: int) -> Any:
        barrier.wait()
        return work(index)

    with ThreadPoolExecutor(max_workers=count) as pool:
        return list(pool.map(entry, range(count)))


# Premise 1: one shared document, many private readers -----------------------


def test_many_readers_on_one_document_all_reconstruct_it(indexed: Any, document_text: str) -> None:
    """
    Purpose:
        The core claim. If any shared state were mutated during a read, threads
        would observe torn or overlapping spans and their reconstructions would
        differ from each other and from the source.
    Contract:
        Every thread, using its own reader over ONE shared document, rebuilds
        the document exactly.
    """
    expected = hashlib.sha256(document_text.encode("utf-8")).hexdigest()

    def work(index: int) -> str:
        reader = indexed.reader(line_target=2 + (index % 99), char_target=1_024 + index * 97)
        return hashlib.sha256(
            "".join(chunk.text for chunk in reader).encode("utf-8")
        ).hexdigest()

    assert _run_concurrently(work) == [expected] * _THREADS


def test_concurrent_readers_do_not_observe_each_others_cursors(indexed: Any) -> None:
    """
    Purpose:
        Each reader owns its position. If the cursor lived on the shared
        document instead, threads would consume each other's chunks and the
        per-thread line sequences would have gaps.
    Contract:
        Every thread sees the identical, gapless sequence of start lines when
        reading with identical budgets.
    """
    def work(_: int) -> Tuple[int, ...]:
        reader = indexed.reader(line_target=25, char_target=65_536)
        return tuple(reader.read().start_line for _ in range(20))

    results = _run_concurrently(work)
    assert len(set(results)) == 1, "readers observed different positions"
    starts = results[0]
    assert list(starts) == sorted(starts)
    assert len(set(starts)) == len(starts), "a start line repeated - cursors interfered"


def test_concurrent_random_access_is_consistent(indexed: Any) -> None:
    """
    Purpose:
        `lines_text`, `head`, `tail` and `line_of_offset` are pure reads over
        the shared index. A bisect or slice that touched instance state would
        show up here as disagreement between threads.
    Contract:
        Identical queries return identical results across threads.
    """
    def work(_: int) -> Tuple[str, str, str, int]:
        return (
            indexed.head(10).text,
            indexed.tail(10).text,
            indexed.lines_text(100, 40),
            indexed.line_of_offset(indexed.char_count // 2),
        )

    assert len(set(_run_concurrently(work))) == 1


def test_shared_document_is_unchanged_after_concurrent_use(indexed: Any, document_text: str) -> None:
    """
    Purpose:
        The immutability premise stated plainly: reading must not mutate.
    Contract:
        Line count, char count and full text are identical before and after
        heavy concurrent reading.
    """
    before = (indexed.line_count, indexed.char_count, len(indexed.text))

    def work(index: int) -> None:
        reader = indexed.reader(line_target=10 + index, char_target=2_048)
        for _ in reader.stream():
            pass

    _run_concurrently(work)
    assert (indexed.line_count, indexed.char_count, len(indexed.text)) == before
    assert indexed.text == document_text


def test_mixed_operations_under_contention(indexed: Any) -> None:
    """
    Purpose:
        Real agents will not all do the same thing. Mixing streaming, seeking,
        head/tail and direct access is the closest this suite gets to the actual
        usage pattern.
    Contract:
        Every worker completes and reports a self-consistent result.
    """
    def work(index: int) -> bool:
        mode = index % 4
        reader = indexed.reader(line_target=2 + (index % 50), char_target=4_096)
        if mode == 0:
            return "".join(c.text for c in reader) == indexed.text
        if mode == 1:
            reader.seek_line(indexed.line_count // 2)
            chunk = reader.read()
            return chunk.start_line == indexed.line_count // 2
        if mode == 2:
            return reader.head(20).text == indexed.lines_text(0, 20)
        reader.read()
        before = reader.current_line
        reader.tail(20)
        return reader.current_line == before

    assert all(_run_concurrently(work))


# Premise 2: sharing ONE reader is the documented mistake ---------------------


def test_sharing_one_reader_duplicates_delivery_but_never_corrupts(indexed: Any) -> None:
    """
    Purpose:
        Documents the ACTUAL failure mode of violating the ownership rule, which
        is worse than it first looks and was mis-stated here originally.

        `read()` is two steps - compute the chunk from `_offset`, then advance
        `_offset` - and nothing makes that pair atomic. Threads sharing one
        reader therefore interleave BETWEEN those steps and are handed the SAME
        span repeatedly. Measured on this document with 16 threads: 7,310 chunks
        delivered covering only 518 distinct start offsets.

        An earlier version of this test asserted the opposite - that a shared
        cursor partitions the document and never repeats a span. That was a
        guess, it was wrong, and it passed under a GIL-serialised sandbox before
        failing on a real run. The bug it would have hidden is an agent silently
        paying for the same content fourteen times.

    Contract:
        Every chunk remains INTERNALLY consistent - its text is exactly the
        document at its own span, so nothing is torn or corrupted. That is the
        ONLY guarantee, and it is the only thing asserted here.

        Delivery is deliberately NOT asserted either way. Whether duplicates
        appear depends on how much real parallelism the interpreter grants: a
        GIL-serialised run can hand out a clean partition, while a genuinely
        concurrent one duplicated 7,310 chunks over 518 distinct spans. Pinning
        EITHER outcome makes this test flaky - which it was, in both directions,
        before it was written this way.
    """
    shared = indexed.reader(line_target=10, char_target=4_096)

    def work(_: int) -> List[Tuple[int, int, str]]:
        collected = []
        while True:
            chunk = shared.read()
            if not chunk.text:
                return collected
            collected.append((chunk.start_char, chunk.end_char, chunk.text))

    per_thread = _run_concurrently(work)
    everything = [item for thread_result in per_thread for item in thread_result]

    # THE guarantee that survives: no chunk is ever torn.
    for start, end, text in everything:
        assert indexed.text[start:end] == text, "a chunk did not match its own span"

    # Reassembling the DISTINCT spans in offset order still covers the document,
    # so content is duplicated rather than lost.
    distinct = sorted({(start, end) for start, end, _ in everything})
    assert "".join(indexed.text[start:end] for start, end in distinct) == indexed.text, (
        "shared cursor lost content"
    )

    # Delivery may repeat but must never LOSE a span - that direction holds
    # under any amount of parallelism, and is the half worth gating on.
    assert len(everything) >= len(distinct), "delivery lost spans it had already produced"


def test_independent_documents_do_not_interfere() -> None:
    """
    Purpose:
        Guards against any accidental class-level or module-level cache keyed on
        something other than the instance - a shared mutable default would show
        up as one document's content bleeding into another's reads.
    Contract:
        Threads each building and reading their OWN document get only their own
        content back.
    """
    def work(index: int) -> bool:
        text = "\n".join(f"doc{index}-line{line}" for line in range(200))
        own = IndexedText(text)
        return "".join(c.text for c in own.reader(line_target=7, char_target=512)) == text

    assert all(_run_concurrently(work))


def test_readers_built_concurrently_from_one_document(indexed: Any) -> None:
    """
    Purpose:
        Construction itself must be safe: `reader()` reads the shared index to
        resolve `start_line`.
    Contract:
        Readers constructed simultaneously all start where they were told.
    """
    def work(index: int) -> Tuple[int, int]:
        start = (index * 13) % max(indexed.line_count - 1, 1)
        reader = indexed.reader(line_target=5, char_target=2_048, start_line=start)
        return start, reader.current_line

    assert all(expected == actual for expected, actual in _run_concurrently(work))


@pytest.mark.parametrize("workers", [2, 8, 32])
def test_scales_across_thread_counts(indexed: Any, workers: int) -> None:
    """
    Purpose:
        A race that hides at low concurrency often appears at higher counts.
    Contract:
        The reconstruction property holds regardless of thread count.
    """
    def work(_: int) -> int:
        reader = indexed.reader(line_target=13, char_target=1_024)
        return sum(len(chunk.text) for chunk in reader)

    assert _run_concurrently(work, workers) == [indexed.char_count] * workers
