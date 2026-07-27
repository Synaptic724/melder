"""
Loader for melder's four package-root system documents.

WHAT THIS IS
------------
Builds one `StaticSystemDocument` per entry in the committed manifest and hands
them to the four package-root modules that publish them as
`melder.__architecture__`, `__components__`, `__graph_network__` and
`__graph_details__`.

NO CACHE, DELIBERATELY
----------------------
Unlike `bind_guard` and `agent_documentation`, this asset does NOT hydrate
through `asset_cache`. A cache amortises COMPUTATION, and there is none here -
the payload is already a string, so hydration is a dict lookup. Adding one would
also defeat the laziness: these four are imported at package scope, and
`StaticSystemDocument` builds its line index on first read precisely so that
processes which never ask a document anything pay nothing for it.

WHAT IS PAID AT IMPORT
----------------------
One manifest import and four `StaticSystemDocument` constructions. Each
construction runs `json.loads` on that document's envelope to validate it - the
class's "construction is total" contract - and stores the extracted markdown.
Nothing is indexed, split, or paged until a caller asks.
"""
from typing import Dict, Tuple

from melder._build_assets._system_documents.manifest import (
    system_documents_manifest as _manifest,
)
from melder.system_document import StaticSystemDocument

MANIFEST_VERSION: str = _manifest.MANIFEST_VERSION
BUILT_FOR_VERSION: str = _manifest.BUILT_FOR_VERSION
READ_ORDER: Tuple[str, ...] = _manifest.READ_ORDER
POPULATED: Dict[str, bool] = dict(_manifest.POPULATED)


def _build_documents() -> Dict[str, StaticSystemDocument]:
    """
    Construct every system document from the committed manifest.

    Contract:
        Built in `READ_ORDER` so construction failures surface in the order an
        agent would read them. A malformed envelope raises here rather than
        silently publishing a broken document, matching the carrier's
        total-construction contract.

    Returns:
        Dict[str, StaticSystemDocument]: Document name -> document object.
    """
    built: Dict[str, StaticSystemDocument] = {}
    for name in _manifest.READ_ORDER:
        entry = _manifest.DOCUMENTS[name]
        built[name] = StaticSystemDocument(
            document_name=name,
            document_json=entry["json"],
            agent_purpose=entry["summary"],
        )
    return built


DOCUMENTS: Dict[str, StaticSystemDocument] = _build_documents()


def get(document_name: str) -> StaticSystemDocument:
    """
    Return one system document by name.

    Args:
        document_name: One of `READ_ORDER`.

    Returns:
        StaticSystemDocument: The named document.

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
    Return whether one document carries real content yet.

    Purpose:
        Let an agent distinguish a structured TEMPLATE from a populated
        document without pattern-matching the prose. While this returns False
        the document's section headings are real but its body is scaffolding.

    Args:
        document_name: One of `READ_ORDER`.

    Returns:
        bool: True when the document has been populated.
    """
    return bool(POPULATED.get(document_name, False))
