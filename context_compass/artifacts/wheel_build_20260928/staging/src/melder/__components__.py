"""
Melder's component inventory, queryable in-process.

Purpose:
    Publish `melder.__components__` - what each subsystem owns, hands off to,
    and whether an agent may drive it, captured from
    `context_compass/system_docs/src_components.md` at build time.

Contract:
    - A `SystemDocumentView`, addressed by SECTION NAME.
    - A LOOKUP TABLE, not orientation. At 8,171 lines, reading it whole to
      answer a question about one component costs orders of magnitude more than
      the answer needs. `index()`, then `get(key)` for the sections your task
      actually touches.
    - `find(substring)` matches section keys only, never body text - a body
      search would mean reading the document, which is the cost this object
      exists to avoid.
    - `verify()` re-checks the shipped text against its recorded digest.

Example:
    >>> import melder
    >>> view = melder.__components__
    >>> len(view.index())
    135

Subsystem Context:
    One of four package-root document surfaces. Read order for an agent is
    architecture -> components -> graph network -> graph details.

System Context:
    Answers at import time, before the `Aether()` substrate boot, and is
    queryable WITHOUT conjuring a conduit. It participates in no binding,
    resolution, or cleanup path.

    Construction reads the manifest only. The section table, the document text,
    and the graph adjacency each load on first use, so a process that never
    queries this document pays for none of them.
"""

from melder._build_assets._system_documents.system_documents import get

__components__ = get("__components__")
