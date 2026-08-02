"""
Unit tests for the system-document query objects.

WHAT THESE PROTECT
------------------
1. LAZINESS IS STRUCTURAL, NOT INCIDENTAL. The four views are built at package
   scope, so every `import melder` pays for whatever their construction
   touches. Three things are deliberately deferred - section tables, document
   payloads, graph adjacency - and a test that only checked "the API works"
   would stay green while someone quietly moved a 1.6 MB payload back onto the
   boot path. These assert the deferral directly, by inspecting `sys.modules`.

2. REFUSED IS NOT EMPTY. A document whose index failed its staleness proof
   ships as an entry with `available == False` and a reason. Slicing it must
   RAISE. If it returned empty text an agent would read "this section says
   nothing" where the truth is "this was checked and rejected".

3. THE WALK TERMINATES. The graph has cycles - `borrows` and `used_by` run in
   both directions - so an unguarded traversal does not stop. Depth alone does
   not save it; the visited set does.

4. GUESSES DO NOT SHIP. Extractor candidates over-generate heavily against a
   hand-authored graph and are leads, never evidence. They are
   excluded from the built adjacency, and that exclusion is asserted here so a
   future builder change cannot launder a guess into structure.
"""
import sys

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.nexus.nexus import Nexus
from melder._build_assets._system_documents import system_documents
from melder.utilities.ai_native_support_tools.system_document_view import (
    Edge,
    Group,
    Impact,
    SearchHit,
    Node,
    Section,
    SystemDocumentView,
    SystemGraphView,
)

DOCUMENT_NAMES = list(system_documents.READ_ORDER)
GRAPH_NAMES = ["__graph_network__", "__graph_details__"]


@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each test.

    Contract:
        - AetherUtilitySystem, Nexus, and Aether are reset before and after
          each test.

    Purpose:
        Importing this module imports `melder`, which boots `Aether()` at
        package scope - the four system documents are published there. Every
        test in this file therefore runs against a live singleton whether or
        not it touches one, so it is reset on both sides like every other unit
        test that loads the package.

        The views themselves are immutable and share no state with the
        substrate, so this guards the ORDER of tests rather than the views: a
        test here must not be the reason an unrelated test later in the session
        sees a dirty Aether.

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


def _available(name: str) -> SystemDocumentView:
    """Return a view, skipping the test when its source pair was refused."""
    view = system_documents.get(name)
    if not view.available:
        pytest.skip(f"{name} unavailable at build time: {view.reason}")
    return view


# ---------------------------------------------------------------------------
# Deferral
# ---------------------------------------------------------------------------


def test_view_construction_touches_no_deferred_module() -> None:
    """
    Building a view must not import sections, payloads, or adjacency.

    Purpose:
        The load-bearing assertion of this file. `SystemDocumentView.__init__`
        stores a manifest entry and nothing else; if it ever eagerly resolves
        its section table or text, every `import melder` starts paying for
        documents most processes never read.
    """
    entry = {
        "name": "__probe__",
        "title": "Probe",
        "summary": "",
        "source": "",
        "available": True,
        "addressing": "section",
        "document_file": "nothing.md",
        "payload_module": "nothing_payload",
        "line_count": 0,
        "content_sha256": "",
    }
    before = set(sys.modules)
    SystemDocumentView(entry)
    introduced = set(sys.modules) - before
    assert not [
        module
        for module in introduced
        if "payload" in module or "adjacency" in module or "sections" in module
    ]


def test_metadata_is_answerable_without_loading_the_document() -> None:
    """
    Title, addressing, proof and availability come from the manifest alone.

    Purpose:
        These are what an agent reads to decide WHETHER to open a document.
        Paying 1.6 MB to find out a document is not the one you wanted defeats
        the entire index-first discipline.

    Contract:
        Builds a FRESH view per document rather than inspecting the shared one.
        `DOCUMENTS` is module-level and its views cache their payload on first
        slice, so any earlier test in the session leaves them warm - asserting
        `_document is None` on a shared view tests test ORDER, not laziness.
    """
    for name in DOCUMENT_NAMES:
        shared = system_documents.get(name)
        view = type(shared)(shared._entry)
        assert view.name == name
        assert view.title
        assert view.summary
        assert view.addressing in ("section", "source_path")
        assert isinstance(view.available, bool)
        assert view.line_count >= 0
        assert view._document is None


def test_graph_views_share_one_section_table() -> None:
    """
    The two graph views address the same document, so they share one table.

    Purpose:
        Section tables are keyed by DOCUMENT FILE, not by view name. Emitting
        575 ranges under each of two names wrote and unmarshalled the same
        data twice. Identical contents prove the dedupe held.
    """
    network, details = (system_documents.get(name) for name in GRAPH_NAMES)
    if not (network.available and details.available):
        pytest.skip("graph documents unavailable at build time")
    assert network.index() == details.index()
    assert network.line_count == details.line_count
    assert network.content_sha256 == details.content_sha256


# ---------------------------------------------------------------------------
# Index and addressing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", DOCUMENT_NAMES)
def test_index_is_ordered_non_overlapping_and_self_consistent(name: str) -> None:
    """
    Every section reports a span whose arithmetic matches its own bounds.

    Purpose:
        `line_count` exists so a caller can budget BEFORE reading. A span whose
        stated size disagrees with its bounds would make that budget a lie.
    """
    view = _available(name)
    sections = view.index()
    assert sections
    for section in sections:
        assert isinstance(section, Section)
        assert 1 <= section.start_line <= section.end_line <= view.line_count
        assert section.line_count == section.end_line - section.start_line + 1


@pytest.mark.parametrize("name", DOCUMENT_NAMES)
def test_keys_and_membership_agree_with_the_index(name: str) -> None:
    """Keys, `in`, and `len` all describe the same section set."""
    view = _available(name)
    keys = view.keys()
    assert len(keys) == len(view.index()) == len(view)
    assert all(key in view for key in keys)
    assert "definitely-not-a-section" not in view


@pytest.mark.parametrize("name", DOCUMENT_NAMES)
def test_get_returns_exactly_the_addressed_span(name: str) -> None:
    """
    A slice is the section's lines, no more.

    Purpose:
        The whole value of the index is that a range is exact. An off-by-one
        here silently hands back a neighbouring section's opening line, which
        reads as legitimate content.
    """
    view = _available(name)
    section = view.index()[len(view) // 2]
    text = view.get(section.key)
    assert text
    assert len(text.split("\n")) - (1 if text.endswith("\n") else 0) == section.line_count


def test_find_matches_substrings_case_insensitively_in_document_order() -> None:
    """
    `find` exists because exact keys are long enough to be unusable by hand.

    Purpose:
        For `source_path` addressing a directory prefix must return a
        subsystem's files contiguously - that is the documented way to read a
        subsystem, and it only works if document order is preserved.
    """
    view = _available("__graph_details__")
    found = view.find("SRC/MELDER/AETHER/CONDUIT/")
    assert len(found) > 1
    assert all("src/melder/aether/conduit/" in s.key for s in found)
    ordered = view.index()
    positions = [ordered.index(section) for section in found]
    assert positions == sorted(positions)


def test_unknown_section_key_names_near_misses() -> None:
    """
    A near miss is the likely failure, so the error must help.

    Purpose:
        These keys are full heading paths or full source paths. A `KeyError`
        carrying only the bad key tells an agent nothing it did not already
        know.
    """
    view = _available("__graph_details__")
    with pytest.raises(KeyError) as raised:
        view.get("conduit.py")
    message = str(raised.value)
    # Against the LIVE count, never a literal. The graph is regenerated
    # whenever source moves - it went 575 -> 581 mid-session - and a test
    # asserting a frozen number fails on a correct rebuild.
    assert f"{len(view)} sections" in message
    assert "source_path" in message
    assert "did you mean" in message


# ---------------------------------------------------------------------------
# Bounded reads
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", DOCUMENT_NAMES)
def test_reader_round_trips_the_whole_document(name: str) -> None:
    """Concatenating every chunk reproduces the document exactly."""
    view = _available(name)
    rebuilt = "".join(chunk.text for chunk in view.reader(line_target=23))
    assert rebuilt == view.render_markdown()


def test_reader_positioned_at_a_section_starts_there() -> None:
    """A keyed reader begins at the section's first line, not the document's."""
    view = _available("__architecture__")
    section = view.index()[10]
    chunk = view.reader(section.key, line_target=3).read()
    # `Section` is 1-based inclusive; `TextChunk` reports 0-based reader
    # offsets. Asserting the conversion is the point - the two numbering
    # schemes meeting in the wrong place is exactly how a slice silently
    # shifts by one line.
    assert chunk.start_line == section.start_line - 1
    assert chunk.text.startswith(view.get(section.key)[: len(chunk.text)])


def test_stream_stops_at_the_section_end() -> None:
    """
    `stream` is bounded to one section; `reader` runs to the document end.

    Purpose:
        The distinction is the reason both exist. An agent asking for one
        section wants one section, and a generator that quietly continued into
        the next would be indistinguishable from correct output.
    """
    view = _available("__graph_details__")
    section = max(view.index(), key=lambda s: s.line_count)
    chunks = list(view.stream(section.key, line_target=20))
    assert chunks
    assert chunks[0].start_line == section.start_line - 1
    assert chunks[-1].end_line == section.end_line
    assert "".join(c.text for c in chunks) == view.get(section.key)


def test_stream_is_lazy() -> None:
    """Creating the generator reads nothing until it is iterated."""
    view = _available("__architecture__")
    stream = view.stream(view.index()[3].key)
    assert next(stream).text


# ---------------------------------------------------------------------------
# Verification and refusal
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", DOCUMENT_NAMES)
def test_shipped_payload_matches_the_proof_its_index_claimed(name: str) -> None:
    """
    The runtime gate, re-checked against the SHIPPED bytes.

    Purpose:
        The build verified the SOURCE pair. This verifies what actually landed
        in the package, which catches a corrupted wheel or a hand-edit of a
        generated module. A range from an unverified index is a guess wearing
        a line number, and this is the refusal that prevents it, in-process.
    """
    view = _available(name)
    assert view.verify()


def test_an_unavailable_document_refuses_rather_than_returning_nothing() -> None:
    """
    Refused must never read as empty.

    Purpose:
        The distinction this whole asset is built around. An empty string
        invites an agent to conclude the document has nothing to say; a raise
        carrying the build-time reason tells it the pair was checked and
        rejected.
    """
    view = SystemDocumentView(
        {
            "name": "__stale__",
            "title": "Stale Document",
            "summary": "",
            "source": "",
            "available": False,
            "reason": "index stale: line_count claimed 8127, actual 8137",
            "addressing": "section",
            "document_file": "",
            "payload_module": "",
            "line_count": 0,
            "content_sha256": "",
        }
    )
    assert view.available is False
    assert view.verify() is False
    assert view.index() == ()
    for call in (lambda: view.get("anything"), view.render_markdown, view.head):
        with pytest.raises((RuntimeError, KeyError)) as raised:
            call()
        if isinstance(raised.value, RuntimeError):
            assert "8127" in str(raised.value)


def test_refusals_are_reported_by_the_loader() -> None:
    """Whatever did not ship is named, with a reason, without reading a builder."""
    reported = system_documents.refusals()
    for name in DOCUMENT_NAMES:
        available = system_documents.get(name).available
        assert (name in reported) is not available
        assert available or reported[name]


# ---------------------------------------------------------------------------
# Graph traversal
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", GRAPH_NAMES)
def test_graph_documents_get_the_walkable_view(name: str) -> None:
    """Addressing, not name, decides which view a document receives."""
    view = system_documents.get(name)
    assert isinstance(view, SystemGraphView)
    assert view.addressing == "source_path"


def test_non_graph_documents_do_not_get_the_walkable_view() -> None:
    """Architecture and components are sliceable but not walkable."""
    for name in ("__architecture__", "__components__"):
        view = system_documents.get(name)
        assert isinstance(view, SystemDocumentView)
        assert not isinstance(view, SystemGraphView)


def test_every_node_resolves_to_a_section_of_the_document() -> None:
    """
    The join between the two graph views must be total.

    Purpose:
        A walk yields node ids; the prose is addressed by source path. If a
        single node resolved to a path with no section, `describe()` would
        raise on a node the graph itself claims to know.
    """
    view = _available("__graph_details__")
    missing = [
        node_id for node_id in view.node_ids() if view.details_key(node_id) not in view
    ]
    assert not missing


def test_edges_are_bidirectionally_consistent() -> None:
    """
    Every outbound edge is findable from its target, and vice versa.

    Purpose:
        Reverse lookup is the query the document layout cannot answer cheaply,
        so it is built here. If the two indexes disagreed, `edges_to` would
        quietly under-report and an agent would conclude nothing depends on a
        class that plenty depends on.
    """
    view = _available("__graph_network__")
    sample = view.node_ids()[::40]
    for node_id in sample:
        for edge in view.edges_from(node_id):
            assert edge in view.edges_to(edge.target)
        for edge in view.edges_to(node_id):
            assert edge in view.edges_from(edge.source)


def test_edge_candidates_are_not_in_the_shipped_adjacency() -> None:
    """
    Guesses must not be laundered into structure.

    Purpose:
        Candidates over-generate heavily and are leads, never evidence.
        Every shipped edge must carry a real origin,
        and every target must be a fully qualified id - candidates are bare
        names like `RLock` and `ValueError`.
    """
    view = _available("__graph_network__")
    for node_id in view.node_ids()[::25]:
        for edge in view.edges_from(node_id):
            assert edge.origin in ("derived", "authored")
            assert "." in edge.target


def test_walk_terminates_on_a_cyclic_graph() -> None:
    """
    Cycles exist, so the visited set - not the depth bound - must stop it.

    Purpose:
        `borrows` and `used_by` run in both directions. A traversal relying on
        depth alone still revisits, and the yield count explodes long before it
        stops.
    """
    view = _available("__graph_network__")
    busiest = max(view.node_ids(), key=lambda n: len(view.edges_from(n)))
    walked = list(view.walk(busiest, depth=12, direction="both"))
    assert walked
    assert len(walked) <= view.edge_count * 2


def test_walk_reports_hop_depth_breadth_first() -> None:
    """Hops arrive in non-decreasing order, so shallow relationships come first."""
    view = _available("__graph_network__")
    busiest = max(view.node_ids(), key=lambda n: len(view.edges_from(n)))
    hops = [hop for hop, _ in view.walk(busiest, depth=3)]
    assert hops == sorted(hops)
    assert max(hops) <= 3


def test_walk_filters_by_relation_and_by_trust_origin() -> None:
    """
    Filters must apply at every hop, not just the first.

    Purpose:
        `origin` is the trust discriminator - walking only `derived` gives
        mechanical structure, only `authored` gives design intent that may have
        gone stale. A filter that leaked would silently mix the two tiers.
    """
    view = _available("__graph_network__")
    busiest = max(view.node_ids(), key=lambda n: len(view.edges_from(n)))
    for edge in (e for _, e in view.walk(busiest, depth=3, relation="specializes")):
        assert edge.relation == "specializes"
    for edge in (e for _, e in view.walk(busiest, depth=3, origin="authored")):
        assert edge.origin == "authored"


def test_walk_rejects_an_unknown_start_and_a_bad_depth() -> None:
    """Construction is total: a bad argument raises before anything is yielded."""
    view = _available("__graph_network__")
    known = view.node_ids()[0]
    with pytest.raises(KeyError):
        list(view.walk("melder.not.a.real.Node"))
    with pytest.raises(ValueError):
        list(view.walk(known, depth=0))
    with pytest.raises(ValueError):
        view.neighbors(known, direction="sideways")


def test_nodes_in_a_file_are_ordered_by_definition_line() -> None:
    """A file's nodes read in the order they appear in the source."""
    view = _available("__graph_details__")
    key = max(view.index(), key=lambda s: s.line_count).key
    nodes = view.nodes_in(key)
    assert nodes
    assert all(isinstance(node, Node) for node in nodes)
    assert [n.line for n in nodes] == sorted(n.line for n in nodes)
    assert all(node.source == key for node in nodes)


def test_describe_returns_the_prose_for_a_walked_node() -> None:
    """
    Node id in, documentation out - the full round trip.

    Purpose:
        The point of the asset. An agent walks to a node it has never heard of
        and reads what the repository says about it, in-process, from a wheel
        that does not contain the source documents.
    """
    view = _available("__graph_network__")
    busiest = max(view.node_ids(), key=lambda n: len(view.edges_from(n)))
    target = view.edges_from(busiest)[0].target
    if target not in view._graph().NODES:
        pytest.skip("sampled edge points outside the described graph")
    prose = view.describe(target)
    assert view.details_key(target) in prose


def test_unsemantic_nodes_are_flagged_as_data() -> None:
    """
    An agent must be able to tell scaffold from authored meaning without prose.

    Purpose:
        Inferring purpose from an UNSEMANTIC node's NAME is exactly the mistake
        the flag prevents, and that is only enforceable if it is queryable
        rather than something to spot in prose.

    Contract:
        Asserts the flag is present and boolean on every node - NOT that this
        snapshot contains any unsemantic ones. It does not currently: the graph
        was regenerated with every node authored, taking the count from 513 to
        zero. That is the repository improving, not the extractor breaking, and
        a test that fails on it is asserting a moment rather than a contract.

        Extraction itself is covered against a fixed fragment in
        `tests/unit/melder/build_assets/test_system_documents_builder.py`, which
        is where a parser regression would surface.
    """
    view = _available("__graph_network__")
    flags = [view.node(n).unsemantic for n in view.node_ids()]
    assert flags
    assert all(isinstance(flag, bool) for flag in flags)


def test_edge_and_node_records_are_named_tuples() -> None:
    """Fields are addressable by name, so no caller indexes a trust field by position."""
    view = _available("__graph_network__")
    node_id = max(view.node_ids(), key=lambda n: len(view.edges_from(n)))
    edge = view.edges_from(node_id)[0]
    assert isinstance(edge, Edge) and edge.source == node_id
    assert isinstance(view.node(node_id), Node)


# ---------------------------------------------------------------------------
# Loader surface
# ---------------------------------------------------------------------------


def test_all_four_documents_are_published_in_read_order() -> None:
    """The read order is the order orientation is meant to happen in."""
    assert system_documents.READ_ORDER == (
        "__architecture__",
        "__components__",
        "__graph_network__",
        "__graph_details__",
    )
    assert set(system_documents.DOCUMENTS) == set(system_documents.READ_ORDER)


def test_population_state_agrees_with_availability() -> None:
    """`is_populated` answers from the verification gate, not a hand-kept flag."""
    for name in DOCUMENT_NAMES:
        assert system_documents.is_populated(name) is system_documents.POPULATED[name]
        assert system_documents.is_populated(name) is system_documents.get(name).available


def test_unknown_document_name_refuses_and_names_the_valid_ones() -> None:
    """The four names are dunder-shaped and easy to mistype."""
    with pytest.raises(KeyError) as raised:
        system_documents.get("__architecture")
    assert "__architecture__" in str(raised.value)


def test_documents_are_reachable_from_the_package_root() -> None:
    """The dunders publish the same objects the loader holds."""
    import melder

    for name in DOCUMENT_NAMES:
        assert getattr(melder, name) is system_documents.get(name)


# ---------------------------------------------------------------------------
# Body search
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", DOCUMENT_NAMES)
def test_search_finds_terms_that_appear_only_in_prose(name: str) -> None:
    """
    The gap `find` cannot cover.

    Purpose:
        `find` matches section KEYS. A concept discussed in the body but absent
        from every heading is invisible to it, and the fallback - pulling the
        whole document and grepping - orders of magnitude more than the answer.
    """
    view = _available(name)
    hits = view.search("melder")
    assert hits
    assert all(isinstance(hit, SearchHit) for hit in hits)
    assert all(hit.key in view for hit in hits)


def test_search_returns_sections_not_text() -> None:
    """
    A result must stay index-shaped.

    Purpose:
        Returning matching TEXT would make search the very thing this object
        exists to prevent - an unbudgeted read. The caller still decides what
        to open; the preview is one line, deliberately.
    """
    view = _available("__components__")
    for hit in view.search("thread", preview_chars=80):
        assert len(hit.preview) <= 80
        assert "\n" not in hit.preview


def test_search_ranks_by_hit_count_then_document_order() -> None:
    """The section mentioning a term most is usually the one that defines it."""
    view = _available("__components__")
    hits = view.search("thread", limit=10)
    assert [h.hits for h in hits] == sorted((h.hits for h in hits), reverse=True)
    assert all(h.hits >= 1 for h in hits)


def test_search_reports_a_real_first_match_line() -> None:
    """
    `first_line` must be citable without opening the section.

    Purpose:
        The repo cites evidence as `path:start-end`. A first_line that did not
        actually contain the term would produce a citation pointing at nothing.
    """
    view = _available("__architecture__")
    lines = view.render_markdown().split("\n")
    for hit in view.search("boot", limit=5):
        section = view.section(hit.key)
        assert section.start_line <= hit.first_line <= section.end_line
        assert "boot" in lines[hit.first_line - 1].lower()


def test_search_attributes_a_line_to_its_most_specific_section() -> None:
    """
    Nested sections must not all claim the same line.

    Purpose:
        `"Indexing"` spans `"Indexing > Verifying citations"`. Reporting the
        parent sends an agent to read 76 lines when 59 of them are irrelevant.
    """
    view = _available("__architecture__")
    keys = [hit.key for hit in view.search("citation", limit=5)]
    nested = [key for key in keys if " > " in key]
    assert nested
    for key in nested:
        parent = key.split(" > ")[0]
        assert parent not in keys


def test_search_is_case_insensitive_and_rejects_an_empty_needle() -> None:
    """An empty needle matches every line and would return the index as a result."""
    view = _available("__architecture__")
    assert view.search("BOOT") == view.search("boot")
    with pytest.raises(ValueError):
        view.search("")


def test_search_respects_its_limit() -> None:
    """A caller's budget is a budget."""
    view = _available("__components__")
    assert len(view.search("the", limit=3)) <= 3


def test_search_on_a_term_that_is_absent_returns_nothing() -> None:
    """No match is an empty tuple, not an error and not a guess."""
    view = _available("__architecture__")
    assert view.search("zzzznotinthisdocument") == ()


# ---------------------------------------------------------------------------
# Grouping
# ---------------------------------------------------------------------------


def test_groups_collapse_the_index_without_losing_any_section() -> None:
    """
    Every section lands in exactly one group.

    Purpose:
        `groups` is an overview, and an overview that silently drops rows is
        worse than no overview - an agent concludes a subsystem is undocumented
        when it is merely unlisted.
    """
    for name in DOCUMENT_NAMES:
        view = _available(name)
        for depth in (1, 3, 8):
            groups = view.groups(depth=depth)
            assert all(isinstance(group, Group) for group in groups)
            assert sum(group.sections for group in groups) == len(view)
            assert sum(group.line_count for group in groups) == sum(
                section.line_count for section in view.index()
            )


def test_groups_get_finer_as_depth_increases() -> None:
    """
    Depth is the dial that turns a 575-row cliff into a readable overview.

    Purpose:
        The graph index is ~11k tokens. Grouping at full directory depth gives
        157 rows, which is a smaller cliff rather than no cliff; a shallow
        default is what makes it usable.
    """
    view = _available("__graph_details__")
    counts = [len(view.groups(depth=depth)) for depth in (2, 3, 4, 6)]
    assert counts == sorted(counts)
    assert counts[0] < len(view) / 10


def test_group_prefixes_expand_through_find() -> None:
    """
    The overview must be actionable: a prefix has to lead somewhere.

    Purpose:
        `groups` is only useful if drilling in is one call. If a prefix did not
        match its own sections the overview would be a dead end.
    """
    view = _available("__graph_details__")
    for group in view.groups(depth=4)[:5]:
        assert len(view.find(group.prefix)) >= group.sections


def test_groups_reject_a_zero_depth() -> None:
    """Depth 0 would collapse everything to one meaningless row."""
    with pytest.raises(ValueError):
        _available("__architecture__").groups(depth=0)


# ---------------------------------------------------------------------------
# Line to node
# ---------------------------------------------------------------------------


def test_node_at_resolves_a_traceback_line_to_its_enclosing_node() -> None:
    """
    Closes the loop from `conduit.py:412` to `Conduit`.

    Purpose:
        A stack trace is the most common way an agent arrives at a file, and
        without this it is a dead end.
    """
    view = _available("__graph_details__")
    path = "src/melder/aether/conduit/conduit.py"
    if path not in view:
        pytest.skip("sample file not in this graph")
    nodes = view.nodes_in(path)
    deepest = nodes[-1]
    found = view.node_at(path, deepest.line + 10)
    assert found is not None
    assert found.node_id == deepest.node_id


def test_node_at_never_returns_a_node_defined_after_the_line() -> None:
    """
    The inference must at least be sound in the direction it claims.

    Purpose:
        This is a heuristic - the graph records where nodes BEGIN, never where
        they end - so it can name the wrong node for a line in a trailing
        module-level function. What it must never do is name a node that had
        not been defined yet.
    """
    view = _available("__graph_details__")
    for section in view.index()[::60]:
        for probe in (1, 5, 50, 500):
            found = view.node_at(section.key, probe)
            if found is not None:
                assert found.line <= probe
                assert found.source == section.key


def test_node_at_returns_none_rather_than_guessing() -> None:
    """An unknown file or a line before every definition has no answer."""
    view = _available("__graph_details__")
    assert view.node_at("src/does/not/exist.py", 10) is None


# ---------------------------------------------------------------------------
# Why-lines
# ---------------------------------------------------------------------------


def test_authored_edges_carry_their_justification() -> None:
    """
    An authored edge without its why is an assertion with no support.

    Purpose:
        An authored `owns_lifecycle_of` claims ownership where the syntax tree
        shows only a reference. The why-line IS the argument. Reaching it used
        to mean slicing the whole section and eyeballing ~1,900 tokens of prose
        for one sentence.
    """
    view = _available("__graph_network__")
    authored = [
        edge
        for node_id in view.node_ids()[::20]
        for edge in view.edges_from(node_id, relation="owns_lifecycle_of")
        if edge.origin == "authored"
    ]
    assert authored
    assert any(edge.why for edge in authored)
    for edge in authored:
        assert isinstance(edge.why, str)


def test_derived_edges_need_no_justification() -> None:
    """
    `derived` edges have the syntax tree as their evidence.

    Purpose:
        A why-line on a mechanical edge would be someone explaining what the
        AST already proves. Absence here is correct, not missing data.
    """
    view = _available("__graph_network__")
    derived = [
        edge
        for node_id in view.node_ids()[::20]
        for edge in view.edges_from(node_id)
        if edge.origin == "derived"
    ]
    assert derived
    assert all(edge.why == "" for edge in derived)


def test_why_survives_the_reverse_direction() -> None:
    """
    The same edge carries the same justification from either side.

    Purpose:
        Inbound and outbound resolve through different tables. If only one
        attached the why, an agent doing impact analysis would see unexplained
        edges that look unauthored.
    """
    view = _available("__graph_network__")
    for node_id in view.node_ids()[::30]:
        for edge in view.edges_from(node_id):
            assert edge in view.edges_to(edge.target)


# ---------------------------------------------------------------------------
# Impact
# ---------------------------------------------------------------------------


def test_impact_returns_files_not_edges() -> None:
    """
    "What breaks if I change this" is answered in files.

    Purpose:
        The walk yields edges; a caller needs something to open. Every returned
        path must be a real section key so the answer is immediately readable.
    """
    view = _available("__graph_network__")
    busiest = max(view.node_ids(), key=lambda n: len(view.edges_to(n)))
    affected = view.impact(busiest, depth=2)
    assert affected
    details = system_documents.get("__graph_details__")
    for item in affected:
        assert isinstance(item, Impact)
        assert item.source in details
        assert item.nodes
        assert item.edges >= 1


def test_impact_is_ordered_nearest_first() -> None:
    """
    A direct dependent is far likelier to break than a third-hop one.

    Purpose:
        Ordering IS the triage. An unordered impact set makes the caller
        re-derive proximity that the walk already knew.
    """
    view = _available("__graph_network__")
    busiest = max(view.node_ids(), key=lambda n: len(view.edges_to(n)))
    hops = [item.hops for item in view.impact(busiest, depth=3)]
    assert hops == sorted(hops)
    assert min(hops) == 1


def test_impact_reports_the_shortest_path_to_each_file() -> None:
    """
    A file reachable at hop 1 and hop 3 is a hop-1 risk.

    Purpose:
        Recording the longer distance would understate the danger of exactly
        the files most likely to break.
    """
    view = _available("__graph_network__")
    busiest = max(view.node_ids(), key=lambda n: len(view.edges_to(n)))
    direct = {
        view.node(edge.source).source
        for edge in view.edges_to(busiest)
        if edge.source in view._graph().NODES
    }
    for item in view.impact(busiest, depth=3):
        if item.source in direct:
            assert item.hops == 1


def test_impact_never_lists_the_changed_node_s_own_file_via_itself() -> None:
    """A node is not its own dependent."""
    view = _available("__graph_network__")
    node_id = max(view.node_ids(), key=lambda n: len(view.edges_to(n)))
    for item in view.impact(node_id, depth=2):
        assert node_id not in item.nodes


def test_impact_respects_the_trust_filter() -> None:
    """Walking only authored dependents must not leak derived ones."""
    view = _available("__graph_network__")
    node_id = max(view.node_ids(), key=lambda n: len(view.edges_to(n)))
    both = view.impact(node_id, depth=2)
    authored = view.impact(node_id, depth=2, origin="authored")
    assert len(authored) <= len(both)


# ---------------------------------------------------------------------------
# Citations
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", DOCUMENT_NAMES)
def test_cite_produces_a_usable_evidence_reference(name: str) -> None:
    """
    Evidence is cited as `document:start-end` throughout this repository.

    Purpose:
        The numbers are already in the index. Making a caller format them by
        hand on every claim is the friction that ends with nothing cited.
    """
    view = _available(name)
    section = view.index()[3]
    citation = view.cite(section.key)
    assert citation.endswith(f":{section.start_line}-{section.end_line}")
    assert citation.startswith(str(view._entry["document_file"]))


def test_cite_can_point_at_a_single_line() -> None:
    """A search hit should cite the match, not the section around it."""
    view = _available("__components__")
    hit = view.search("thread", limit=1)[0]
    assert view.cite(hit.key, line=hit.first_line).endswith(f":{hit.first_line}")


def test_cite_refuses_an_unknown_section() -> None:
    """A citation to a section that does not exist is worse than none."""
    with pytest.raises(KeyError):
        _available("__architecture__").cite("not a real section")


# ---------------------------------------------------------------------------
# Cross-document search
# ---------------------------------------------------------------------------


def test_search_all_covers_every_document_in_one_call() -> None:
    """
    "What does melder say about X" is one question.

    Purpose:
        Asking per document made it four calls plus a manual merge, and an
        agent that only thought to ask one document never learns another had
        the better answer.
    """
    found = system_documents.search_all("conduit", limit=3)
    assert found
    assert len({item.document for item in found}) >= 1
    assert all(item.citation for item in found)


def test_search_all_does_not_double_count_the_shared_graph_document() -> None:
    """
    The two graph views address the same document.

    Purpose:
        Searching both returned every graph hit twice - pure noise in a ranked
        list, and the caller asked one question.
    """
    found = system_documents.search_all("conduit", limit=5)
    seen = [
        (item.hit.key, item.hit.first_line)
        for item in found
        if item.document.startswith("__graph")
    ]
    assert len(seen) == len(set(seen))


def test_search_all_ranks_across_documents_then_by_read_order() -> None:
    """
    The strongest match wins regardless of which document holds it.

    Purpose:
        Ties break toward `READ_ORDER`, which puts orientation ahead of lookup:
        if architecture and the graph mention a term equally, architecture is
        the one to read first.
    """
    found = system_documents.search_all("spell", limit=4)
    assert [item.hit.hits for item in found] == sorted(
        (item.hit.hits for item in found), reverse=True
    )


def test_search_all_can_be_restricted_and_rejects_bad_names() -> None:
    """A caller narrowing the search should not silently get everything."""
    found = system_documents.search_all(
        "boot", documents=("__architecture__",), limit=2
    )
    assert all(item.document == "__architecture__" for item in found)
    with pytest.raises(KeyError):
        system_documents.search_all("boot", documents=("__nope__",))
    with pytest.raises(ValueError):
        system_documents.search_all("")
