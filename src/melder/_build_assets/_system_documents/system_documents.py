"""
Loader for melder's four package-root system documents.

WHAT THIS IS
------------
Builds one query view per entry in the committed manifest and hands them to the
four package-root modules that publish them as `melder.__architecture__`,
`__components__`, `__graph_network__` and `__graph_details__`.

WHAT IS PAID AT IMPORT
----------------------
One manifest import and four view constructions. A view construction reads the
manifest entry and turns its section table into `Section` tuples - roughly 760
tuples across all four - and touches nothing else.

Specifically NOT paid at import:

    payloads/        the document text. Imported on first slice, per document.
    graph adjacency  1,188 nodes and 1,444 edges. Imported on first walk.

That is deliberate and it is the whole reason the asset is split three ways.
These four are imported at package scope, so every `import melder` pays for
whatever this module touches. The graph payload alone is 1.6 MB of source; a
process that boots melder to bind a spell must not compile it.

NO CACHE, DELIBERATELY
----------------------
Unlike `bind_guard` and `agent_documentation`, this asset does NOT hydrate
through `asset_cache`. A cache amortises COMPUTATION, and there is none here -
the payload is already a string literal, so the interpreter's own `.pyc` has
already done the only parsing involved. Stacking a second marshal layer on top
of marshal measured slower when it was tried on this repo.
"""
from typing import Dict, List, NamedTuple, Tuple

from melder._build_assets._system_documents.manifest import (
    system_documents_manifest as _manifest,
)
from melder.utilities.ai_native_support_tools.system_document_view import (
    SearchHit,
    SystemDocumentView,
    SystemGraphView,
)

MANIFEST_VERSION: str = _manifest.MANIFEST_VERSION
BUILT_FOR_VERSION: str = _manifest.BUILT_FOR_VERSION
READ_ORDER: Tuple[str, ...] = _manifest.READ_ORDER

# Graph documents get the walkable view; the rest get the sliceable one. Keyed
# by addressing scheme rather than by name, so a fifth document picks up the
# right view by declaring how it is addressed instead of by editing a list here.
_GRAPH_ADDRESSING: str = "source_path"


def _build_views() -> Dict[str, SystemDocumentView]:
    """
    Construct every system document view from the committed manifest.

    Contract:
        Built in `READ_ORDER` so a construction failure surfaces in the order
        an agent would read them. An entry that failed the build-time
        verification gate still gets a view - one reporting `available` False
        and carrying the refusal reason. Skipping it would make a REFUSED
        document indistinguishable from an absent one, and that difference is
        the point: refused says "checked and rejected", absent invites an agent
        to assume nothing was ever meant to be there.

    Returns:
        Dict[str, SystemDocumentView]: Document name -> view.
    """
    built: Dict[str, SystemDocumentView] = {}
    for name in _manifest.READ_ORDER:
        entry = _manifest.DOCUMENTS[name]
        view = (
            SystemGraphView
            if entry["addressing"] == _GRAPH_ADDRESSING
            else SystemDocumentView
        )
        built[name] = view(entry)
    return built


DOCUMENTS: Dict[str, SystemDocumentView] = _build_views()

# Derived from the verification gate rather than hand-maintained. A document is
# populated when its pair passed its staleness proof and its text was captured;
# nothing can now say "populated" while carrying a refusal.
POPULATED: Dict[str, bool] = {
    name: view.available for name, view in DOCUMENTS.items()
}


def get(document_name: str) -> SystemDocumentView:
    """
    Return one system document view by name.

    Args:
        document_name: One of `READ_ORDER`.

    Returns:
        SystemDocumentView: The named view. A `SystemGraphView` for the two
            graph documents, which adds node and edge traversal.

    Raises:
        KeyError: When the name is not a published document. The message lists
            the valid names, because the four are dunder-shaped and easy to
            mistype.
    """
    if document_name not in DOCUMENTS:
        raise KeyError(
            f"{document_name!r} is not a melder system document; "
            f"valid names are {list(READ_ORDER)}"
        )
    return DOCUMENTS[document_name]


def is_populated(document_name: str) -> bool:
    """
    Return whether one document carries real content.

    Purpose:
        Kept under the name other modules already call. Now answered by the
        verification gate rather than a hand-maintained flag: a document is
        populated when it passed its staleness proof at build time and its text
        was captured.

    Args:
        document_name: One of `READ_ORDER`.

    Returns:
        bool: True when the document shipped with content.
    """
    return document_name in DOCUMENTS and DOCUMENTS[document_name].available


def refusals() -> Dict[str, str]:
    """
    Return every document that did not ship, and why.

    Purpose:
        Makes a build-time refusal visible in-process. A stale index means the
        pair was rejected, and an agent asking why should not have to read the
        builder to find out.

    Returns:
        Dict[str, str]: Document name -> reason. Empty when all four shipped.
    """
    return {
        name: view.reason for name, view in DOCUMENTS.items() if not view.available
    }


class DocumentHit(NamedTuple):
    """
    One search result, carrying which document it came from.

    Attributes:
        document: The melder document name, e.g. `__components__`.
        hit: The `SearchHit` within that document.
        citation: `document_file:line` for the first match, ready to cite.
    """

    document: str
    hit: SearchHit
    citation: str


def search_all(
        needle: str, *, limit: int = 5, documents: Tuple[str, ...] = ()
) -> Tuple[DocumentHit, ...]:
    """
    Search every system document at once.

    Purpose:
        "What does melder say about X" is one question, and asking it per
        document made it four calls plus the caller merging results. Worse, an
        agent that only thought to ask `__components__` never learns the
        architecture document had the better answer.

    Contract:
        Ranked by hit count ACROSS documents, so the strongest match wins
        regardless of which document holds it. Ties break in `READ_ORDER`,
        which puts orientation ahead of lookup - if architecture and graph both
        mention a term equally, architecture is the one to read first.

        `limit` is per document, not overall; a term that genuinely lives in
        one document should not be crowded out by weak hits elsewhere.

        Documents sharing a source file are searched ONCE. The two graph views
        address the same 25,291 lines, so searching both would double every
        graph hit in a ranked list.

        Unavailable documents are skipped silently. They are already reported
        by `refusals()`, and raising here would make one stale pair break every
        search.

        Loads the payload of every document it searches. That is the honest
        cost of asking all four - use a single view's `search()` when the
        document is already known.

    Args:
        needle: Text to look for.
        limit: Maximum hits per document.
        documents: Restrict to these document names, or empty for all.

    Returns:
        Tuple[DocumentHit, ...]: Matches, strongest first.

    Raises:
        ValueError: When `needle` is empty.
        KeyError: When a named document does not exist.
    """
    if not needle:
        raise ValueError("search needle cannot be empty")
    names = documents or READ_ORDER
    for name in names:
        if name not in DOCUMENTS:
            raise KeyError(
                f"{name!r} is not a melder system document; "
                f"valid names are {list(READ_ORDER)}"
            )

    found: List[DocumentHit] = []
    # `__graph_network__` and `__graph_details__` address the SAME document.
    # Searching both returns every graph hit twice, which is pure noise in a
    # ranked list - the caller asked one question. First name in READ_ORDER
    # wins, so the result is reported under the view an agent reaches for first.
    searched: Dict[str, bool] = {}
    for name in names:
        view = DOCUMENTS[name]
        if not view.available:
            continue
        document_file = str(view._entry["document_file"])
        if document_file in searched:
            continue
        searched[document_file] = True
        for hit in view.search(needle, limit=limit):
            found.append(
                DocumentHit(name, hit, view.cite(hit.key, line=hit.first_line))
            )
    order = {name: position for position, name in enumerate(READ_ORDER)}
    return tuple(
        sorted(found, key=lambda item: (-item.hit.hits, order[item.document]))
    )
