"""
Unit tests for the four package-root system documents and their reader wiring.

WHAT THESE PROTECT
------------------
1. LAZINESS. All four documents are imported by `melder/__init__.py` at package
   scope, so anything they do eagerly is paid by every `import melder` -
   including by the majority of processes that never ask a document anything.
   The line index must not exist until someone asks for a bounded read. This is
   the whole reason `StaticSystemDocument` defers indexing, and it is invisible
   to every other test.

2. BOUNDED READS ARE REACHABLE. `render_markdown()` has no budget and returns
   the entire payload. The reader surface is what makes these documents safe to
   consume once populated, so it must actually be wired through the carrier
   rather than only existing on `IndexedText`.

3. TEMPLATE-VERSUS-POPULATED IS DATA. While a document is a placeholder, callers
   need to know WITHOUT pattern-matching prose. `POPULATED` is a dict in the
   manifest precisely so a tool can branch on it.

The loader is imported through the package, not by file path: unlike the
builders, this IS runtime code that runs on a normal `import melder`, so testing
it any other way would test a path nobody uses.
"""
from __future__ import annotations

import json

import pytest

from melder._build_assets._system_documents import system_documents
from melder.system_document import StaticSystemDocument
from melder.utilities.ai_native_support_tools.agent_text_reader import (
    IndexedText,
    ReaderPolicy,
)


def _fresh(body: str = "line one\nline two\nline three\n") -> StaticSystemDocument:
    """
    Build a throwaway document with a known body.

    Args:
        body: Markdown payload.

    Returns:
        StaticSystemDocument: A document nobody else has read.
    """
    return StaticSystemDocument(
        document_name="__test__",
        document_json=json.dumps({"m": body}, separators=(",", ":")),
    )


# Laziness -------------------------------------------------------------------


def test_construction_does_not_build_the_index() -> None:
    """
    Purpose:
        THE boot-path guarantee. Four documents are constructed on every
        `import melder`; if construction indexed them, every process would pay
        for content most never read. Nothing else in the suite would notice.
    Contract:
        A newly constructed document holds no index.
    """
    assert _fresh()._indexed is None


@pytest.mark.parametrize(
    "trigger",
    [
        lambda d: d.line_count,
        lambda d: d.char_count,
        lambda d: d.head(2),
        lambda d: d.tail(2),
        lambda d: d.lines(0, 2),
        lambda d: d.reader(),
    ],
)
def test_every_bounded_surface_builds_the_index_on_demand(trigger) -> None:
    """
    Contract:
        Each reader-facing entry point materializes the index, so laziness never
        turns into a surface that silently fails to work.
    """
    document = _fresh()
    trigger(document)
    assert document._indexed is not None


def test_render_markdown_does_not_build_the_index() -> None:
    """
    Purpose:
        `render_markdown()` is the unbudgeted escape hatch and predates the
        reader. It must stay index-free so it costs exactly what it always did.
    Contract:
        Reading the raw payload does not index it.
    """
    document = _fresh()
    assert document.render_markdown()
    assert document.render_json()
    assert document._indexed is None


def test_index_is_built_once_and_reused() -> None:
    """
    Contract:
        Repeated reads share one index rather than rebuilding per call.
    """
    document = _fresh()
    document.head(2)
    first = document._indexed
    document.tail(2)
    assert document._indexed is first


# Reader wiring --------------------------------------------------------------


def test_reader_pages_and_reconstructs_the_document() -> None:
    """
    Purpose:
        The strongest single assertion: any gap or overlap in the wiring between
        the carrier and the reader breaks reconstruction.
    Contract:
        Concatenating every chunk equals `render_markdown()`.
    """
    body = "\n".join(f"line {index:03d}" for index in range(400))
    document = _fresh(body)
    rebuilt = "".join(chunk.text for chunk in document.reader(line_target=7, char_target=256))
    assert rebuilt == document.render_markdown()


def test_reader_budget_bounds_are_enforced_through_the_carrier() -> None:
    """
    Purpose:
        The 2-100 line bound is what stops a "read" becoming "return the whole
        document". Delegation must not lose it.
    Contract:
        Out-of-range budgets raise `ValueError` from the document surface.
    """
    document = _fresh()
    with pytest.raises(ValueError):
        document.reader(line_target=ReaderPolicy.MAX_LINE_TARGET + 1)
    with pytest.raises(ValueError):
        document.reader(line_target=1)


def test_head_and_tail_agree_with_the_underlying_index() -> None:
    """
    Contract:
        The carrier's delegates return exactly what `IndexedText` would, so the
        two access styles cannot disagree about one document.
    """
    body = "\n".join(f"L{index}" for index in range(120))
    document = _fresh(body)
    direct = IndexedText(body)
    assert document.head(5).text == direct.head(5).text
    assert document.tail(5).text == direct.tail(5).text
    assert document.lines(10, 4) == direct.lines_text(10, 4)


def test_line_and_char_counts_match_the_payload() -> None:
    """
    Contract:
        Counts describe the markdown body, not the JSON envelope that carries it.
    """
    body = "alpha\nbeta\ngamma\n"
    document = _fresh(body)
    assert document.line_count == 3
    assert document.char_count == len(body)
    assert document.char_count < len(document.render_json())


# The four real documents ----------------------------------------------------


def test_all_four_documents_are_published_in_read_order() -> None:
    """
    Purpose:
        Read order is DATA, not prose, so tooling can follow it without parsing
        English. If a document goes missing the chain breaks silently.
    Contract:
        `READ_ORDER` names exactly the four expected documents, in order.
    """
    assert system_documents.READ_ORDER == (
        "__architecture__",
        "__components__",
        "__graph_network__",
        "__graph_details__",
    )
    assert set(system_documents.DOCUMENTS) == set(system_documents.READ_ORDER)


@pytest.mark.parametrize("name", list(system_documents.READ_ORDER))
def test_each_real_document_is_readable_and_non_empty(name: str) -> None:
    """
    Contract:
        Every published document constructs, carries content, and pages.
    """
    document = system_documents.get(name)
    assert document.document_name == name
    assert document.line_count >= 2
    assert document.char_count > 0
    chunk = document.head(ReaderPolicy.MIN_LINE_TARGET)
    assert chunk.text
    assert chunk.total_lines == document.line_count


@pytest.mark.parametrize("name", list(system_documents.READ_ORDER))
def test_each_real_document_round_trips_through_its_reader(name: str) -> None:
    """
    Contract:
        Paging a real document reproduces it exactly.
    """
    document = system_documents.get(name)
    rebuilt = "".join(
        chunk.text for chunk in document.reader(line_target=3, char_target=256)
    )
    assert rebuilt == document.render_markdown()


def test_population_state_is_queryable_as_data() -> None:
    """
    Purpose:
        While these are templates, a caller must be able to tell placeholder
        from real content without matching on the word "TEMPLATE". When the real
        documents land, this test is what proves the flag moved with them.
    Contract:
        `is_populated` answers for every document and agrees with the manifest.
    """
    for name in system_documents.READ_ORDER:
        assert isinstance(system_documents.is_populated(name), bool)
        assert system_documents.is_populated(name) == system_documents.POPULATED[name]


def test_unknown_document_name_refuses_and_names_the_valid_ones() -> None:
    """
    Purpose:
        The four names are dunder-shaped and easy to mistype, so the refusal
        should teach rather than just fail.
    Contract:
        An unknown name raises `KeyError` listing the valid names.
    """
    with pytest.raises(KeyError, match="is not a melder system document"):
        system_documents.get("__architecture")


def test_documents_are_reachable_from_the_package_root() -> None:
    """
    Purpose:
        The published surface is `melder.__architecture__` and friends. The
        loader could be perfect while the package-root re-export was broken, and
        that is what a caller actually touches.
    Contract:
        Each dunder module exposes the same object the loader holds.
    """
    import melder

    for name in system_documents.READ_ORDER:
        assert getattr(melder, name) is system_documents.get(name)
