"""
Multithreaded integration tests for the system-document query objects.

WHY THIS FILE EXISTS
--------------------
`system_document_view` states, in its own module docstring, that views and their
adjacency are immutable and shared, that every cursor handed out is private, and
that many agents may read and walk concurrently with no lock. Until this file
that was REASONING, not measurement - and a concurrency claim nobody has run is
just a comfortable sentence.

THE PART THAT IS ACTUALLY RACY
------------------------------
The views are immutable in the sense that nothing mutates their DATA. They are
not immutable in the sense of having no writes: three things load lazily and
each has a readiness check followed by publication.

    _index()  ->  the section table
    _doc()    ->  the document payload
    _graph()  ->  the graph adjacency

Two threads arriving first can both see `None` and build equivalent values.
That is safe only when readiness implies COMPLETE data. The index has two
related fields: publishing its section tuple before its key map let another
reader return a None map. Event-controlled regressions force that exact window
and verify retry after construction failure; Barrier tests exercise simultaneous
loads and assert correct data, not merely non-crashing data.

WHAT A GREEN RUN HERE DOES AND DOES NOT PROVE
---------------------------------------------
The deterministic regressions force their interleaving even under a GIL. The
stress tests also need a Python 3.14 free-threaded run with the GIL disabled to
exercise real simultaneous loads. Report the actual interpreter and GIL state;
one ordinary green run alone does not establish the publication invariant.
"""
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, List, Mapping

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder._build_assets._system_documents import system_documents
import melder.utilities.ai_native_support_tools.system_document_view as document_views
from melder.utilities.ai_native_support_tools.system_document_view import (
    Section,
    SystemDocumentView,
    SystemGraphView,
)

WORKER_COUNT = 16


@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each test.

    Contract:
        - AetherUtilitySystem, Nexus, and Aether are reset before and after
          each test; after the test a fresh Aether is booted and bound to
          `Spellbook._aether`, so later tests find a live world (a reset alone
          boots nothing, and `Spellbook()` needs the Nexus an Aether boot builds).

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    yield
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()


def _contend(work: Callable[[int], Any], count: int = WORKER_COUNT) -> List[Any]:
    """
    Run `work` on `count` threads released simultaneously.

    Purpose:
        A `Barrier` holds every worker until all have started, so they contend
        rather than running in sequence. Without it a fast pool simply finishes
        each task before starting the next and the test proves nothing.

    Args:
        work: Called with the worker index.
        count: Number of workers.

    Returns:
        List[Any]: Each worker's result, in submission order.
    """
    barrier = threading.Barrier(count)

    def run(index: int) -> Any:
        barrier.wait()
        return work(index)

    with ThreadPoolExecutor(max_workers=count) as pool:
        return list(pool.map(run, range(count)))


def _cold(name: str) -> SystemDocumentView:
    """
    Return a FRESH view over a shipped document, with nothing loaded yet.

    Purpose:
        The shared views in `DOCUMENTS` are warm by the time any realistic test
        runs. Racing a lazy load requires an instance that has not performed
        one, so each test builds its own from the same manifest entry.
    """
    shared = system_documents.get(name)
    if not shared.available:
        pytest.skip(f"{name} unavailable at build time: {shared.reason}")
    return type(shared)(shared._entry)


# ---------------------------------------------------------------------------
# Racing the three lazy loads
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", system_documents.READ_ORDER)
def test_index_lookup_during_another_threads_key_map_construction(
    name: str, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A reader cannot observe sections before their exact-key map is complete.

    Pause the first builder at the real mapping constructor, then perform public
    reads on another thread. Events force the CI interleaving without sleeps;
    the paused worker is always released and joined, even when a read fails.
    """
    view = _cold(name)
    reference = system_documents.get(name)
    expected = reference.index()[0]
    expected_text = reference.get(expected.key)
    mapping_started = threading.Event()
    release_mapping = threading.Event()
    original_proxy = document_views.MappingProxyType

    def pause_first_builder(values: dict[str, Section]) -> Mapping[str, Section]:
        """Delay only the named loader, preserving the real read-only mapping."""
        if threading.current_thread().name.startswith("paused-document-index"):
            mapping_started.set()
            assert release_mapping.wait(10), "The test did not release its index builder."
        return original_proxy(values)

    monkeypatch.setattr(document_views, "MappingProxyType", pause_first_builder)
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="paused-document-index") as pool:
        first_read = pool.submit(view.section, expected.key)
        try:
            assert mapping_started.wait(10), "The first index builder never reached the mapping constructor."
            assert view.section(expected.key) == expected
            assert expected.key in view
            assert view.get(expected.key) == expected_text
        finally:
            release_mapping.set()
        assert first_read.result(timeout=10) == expected
    assert view.index() == reference.index()


@pytest.mark.parametrize("name", system_documents.READ_ORDER)
def test_failed_key_map_construction_leaves_index_retryable(
    name: str, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed first key-map build cannot leave the section marker falsely ready.

    The injected construction error must propagate, and a subsequent real public
    lookup must rebuild successfully instead of returning a missing key map.
    """
    view = _cold(name)
    reference = system_documents.get(name)
    expected = reference.index()[0]
    original_proxy = document_views.MappingProxyType

    def fail_mapping(values: dict[str, Section]) -> Mapping[str, Section]:
        """Simulate a mapping allocation failure before a complete index exists."""
        raise RuntimeError("injected key-map construction failure")

    monkeypatch.setattr(document_views, "MappingProxyType", fail_mapping)
    with pytest.raises(RuntimeError, match="injected key-map construction failure"):
        view.index()
    monkeypatch.setattr(document_views, "MappingProxyType", original_proxy)

    assert view.section(expected.key) == expected
    assert view.get(expected.key) == reference.get(expected.key)


def test_concurrent_first_index_load_gives_every_thread_the_same_table() -> None:
    """
    Sixteen threads hit an unloaded section table at once.

    Purpose:
        `_index()` is a check-then-set. Every thread must come away with the
        complete table - a partially populated one would silently shrink an
        agent's view of what a document contains.
    """
    view = _cold("__components__")
    tables = _contend(lambda _: view.index())
    assert all(table == tables[0] for table in tables)
    assert len(tables[0]) == len(system_documents.get("__components__").index())


def test_concurrent_first_payload_load_gives_every_thread_the_same_text() -> None:
    """
    Sixteen threads force the payload import simultaneously.

    Purpose:
        The riskiest of the three - it imports a module and constructs a
        carrier. Racing importlib is exactly where a half-initialised module
        would surface, and a truncated document would still slice cleanly.
    """
    view = _cold("__architecture__")
    section = view.index()[4].key
    slices = _contend(lambda _: view.get(section))
    assert all(text == slices[0] for text in slices)
    assert slices[0]


def test_concurrent_first_graph_load_gives_every_thread_the_same_edges() -> None:
    """
    Sixteen threads force the adjacency import simultaneously.

    Purpose:
        Node and edge tables are separate module attributes. A thread that saw
        one before the other would compute a walk against a half-built graph.
    """
    view = _cold("__graph_network__")
    assert isinstance(view, SystemGraphView)
    node_id = system_documents.get("__graph_network__").node_ids()[0]
    results = _contend(lambda _: view.edges_from(node_id))
    assert all(edges == results[0] for edges in results)


def test_racing_every_lazy_load_at_once_is_consistent() -> None:
    """
    Different threads trip different lazy loads on the same instance.

    Purpose:
        The three loads are independent, so a real agent population trips them
        interleaved rather than one at a time. This is the shape that actually
        occurs.
    """
    view = _cold("__graph_details__")
    reference = system_documents.get("__graph_details__")
    key = reference.index()[10].key

    def work(index: int) -> Any:
        if index % 3 == 0:
            return ("index", len(view.index()))
        if index % 3 == 1:
            return ("text", view.get(key))
        return ("edges", len(view.node_ids()))

    results = _contend(work)
    for kind, value in results:
        if kind == "index":
            assert value == len(reference.index())
        elif kind == "text":
            assert value == reference.get(key)
        else:
            assert value == len(reference.node_ids())


# ---------------------------------------------------------------------------
# Independent readers over one warm view
# ---------------------------------------------------------------------------


def test_many_threads_slice_different_sections_correctly() -> None:
    """
    Each thread reads a different span and gets exactly its own.

    Purpose:
        The realistic workload - many agents, one shared document, different
        questions. Cross-contamination here would return one agent another's
        section while looking entirely legitimate.
    """
    view = system_documents.get("__components__")
    if not view.available:
        pytest.skip("components unavailable")
    sections = view.index()[: WORKER_COUNT]
    expected = [view.get(section.key) for section in sections]
    results = _contend(lambda i: view.get(sections[i].key), len(sections))
    assert results == expected


def test_concurrent_readers_hold_private_cursors() -> None:
    """
    A cursor belongs to its caller alone.

    Purpose:
        THE property that makes a shared document safe to hand out. If cursors
        were shared, two agents paging the same document would each receive an
        interleaved half of it and neither would notice.
    """
    view = system_documents.get("__architecture__")
    if not view.available:
        pytest.skip("architecture unavailable")

    def read_three(_: int) -> List[int]:
        cursor = view.reader(line_target=10)
        return [cursor.read().start_line for _ in range(3)]

    starts = _contend(read_three)
    assert all(run == starts[0] for run in starts)
    assert starts[0] == sorted(starts[0])
    assert len(set(starts[0])) == 3


def test_concurrent_searches_agree_with_a_serial_search() -> None:
    """
    Search allocates a per-call array over shared text.

    Purpose:
        It builds a line-to-section map on every call. That scratch state must
        be local - a shared one would let two searches for different terms
        overwrite each other's attribution.
    """
    view = system_documents.get("__components__")
    if not view.available:
        pytest.skip("components unavailable")
    terms = ["spell", "conduit", "thread", "cleanup"]
    expected = {term: view.search(term, limit=5) for term in terms}
    results = _contend(lambda i: (terms[i % len(terms)],
                                  view.search(terms[i % len(terms)], limit=5)))
    for term, found in results:
        assert found == expected[term]


def test_concurrent_walks_terminate_and_agree() -> None:
    """
    Every walker carries its own visited set.

    Purpose:
        The graph has cycles. A shared visited set would make one walk truncate
        another - and truncation looks exactly like "nothing else depends on
        this", which is a dangerous thing to be wrong about.
    """
    view = system_documents.get("__graph_network__")
    if not view.available:
        pytest.skip("graph unavailable")
    node_id = max(view.node_ids(), key=lambda n: len(view.edges_from(n)))
    expected = list(view.walk(node_id, depth=3, direction="both"))
    results = _contend(lambda _: list(view.walk(node_id, depth=3, direction="both")))
    assert all(walked == expected for walked in results)


def test_concurrent_impact_analysis_is_stable() -> None:
    """
    `impact` walks inbound and aggregates - the heaviest read path.

    Purpose:
        It accumulates into local dicts while reading shared tables. Leakage
        would inflate another thread's blast radius, which is the number
        someone decides how carefully to review a change on.
    """
    view = system_documents.get("__graph_network__")
    if not view.available:
        pytest.skip("graph unavailable")
    node_id = max(view.node_ids(), key=lambda n: len(view.edges_to(n)))
    expected = view.impact(node_id, depth=2)
    results = _contend(lambda _: view.impact(node_id, depth=2))
    assert all(found == expected for found in results)


def test_concurrent_verification_does_not_disturb_readers() -> None:
    """
    `verify()` rehashes the whole payload while others are slicing it.

    Purpose:
        The most expensive read in the API, run against text other threads are
        actively reading. A reader that saw text mid-verification would be
        reading something being consumed by another operation.
    """
    view = system_documents.get("__graph_details__")
    if not view.available:
        pytest.skip("graph unavailable")
    key = view.index()[20].key
    expected = view.get(key)

    def work(index: int) -> Any:
        return ("verify", view.verify()) if index % 4 == 0 else ("slice", view.get(key))

    for kind, value in _contend(work):
        assert value is True if kind == "verify" else value == expected


def test_all_four_documents_read_concurrently() -> None:
    """
    The realistic population: agents on different documents at once.

    Purpose:
        Each document owns separate lazy state, and two of the four share one
        payload module. Loading that shared module from two views at once is
        the one cross-view interaction that exists.
    """
    names = [n for n in system_documents.READ_ORDER
             if system_documents.get(n).available]
    if len(names) < 2:
        pytest.skip("fewer than two documents available")
    expected = {n: system_documents.get(n).index()[0].key for n in names}

    def work(index: int) -> Any:
        name = names[index % len(names)]
        view = system_documents.get(name)
        return name, view.get(expected[name])[:200]

    results = _contend(work)
    for name, opening in results:
        assert opening == system_documents.get(name).get(expected[name])[:200]
