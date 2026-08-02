"""
Melder's own architecture map, queryable in-process.

Purpose:
    Publish `melder.__architecture__` - the C4-level system map captured from
    `context_compass/system_docs/src_architecture.md` at build time. This is the
    ORIENTATION document and the one meant to be read broadly; the others are
    lookup surfaces.

Contract:
    - A `SystemDocumentView`, addressed by SECTION NAME.
    - `index()` first - every section with its line cost, so a read can be
      budgeted before it is committed to.
    - `get(key)` for one section, `find(substring)` when the exact heading path
      is unknown, `stream(key)` to page a large section.
    - `render_markdown()` exists and has NO budget. At 2,278 lines this one is
      survivable whole; treat that as the exception, not the pattern.
    - `verify()` re-checks the shipped text against the SHA-256 its source index
      claimed. The build already refused a mismatched pair; this catches a
      corrupted or hand-edited install.

Example:
    >>> import melder
    >>> [s.key for s in melder.__architecture__.find("Boot")]
    ['Boot and Configuration Sequence']
    >>> melder.__architecture__.section("Boot and Configuration Sequence").line_count
    67

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

__architecture__ = get("__architecture__")
