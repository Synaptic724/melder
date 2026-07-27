"""
Packaged hardcopy runtime object for Melder component documentation.

Purpose:
    Publish `melder.__components__`, the subsystem inventory an agent reads
    after the architecture document: what each component owns, what it hands
    off to, and which are guarded kernel machinery.

Contract:
    - Module-level `StaticSystemDocument` instance, built at import from the
      committed manifest at `_build_assets/_system_documents/`.
    - `render_markdown()` returns the whole body; `render_json()` the raw
      hardcopy envelope.
    - BOUNDED READS are the intended path: `reader(...)`, `head(n)`, `tail(n)`,
      `lines(start, count)`, plus `line_count` / `char_count` to size a read
      before committing context to it. `render_markdown()` has no budget and
      will hand back the entire document in one call.
    - CURRENT STATE: a structured TEMPLATE, not a populated document. The
      section skeleton is real; the body is scaffolding. Ask
      `melder._build_assets._system_documents.system_documents.is_populated(
      "__components__")` rather than pattern-matching the prose - population is
      tracked as data precisely so callers do not have to guess.

Subsystem Context:
    One of four package-root document surfaces built on
    `melder.system_document.StaticSystemDocument`. Read order for an agent is
    architecture -> components -> graph network -> graph details: this document
    is the second step of that chain.

System Context:
    Answers at import time, before the `Aether()` substrate boot, and is
    queryable WITHOUT conjuring a conduit. It participates in no binding,
    resolution, or cleanup path. Its line index is built on FIRST bounded read,
    so a process that never queries it pays only for construction.
"""

from melder._build_assets._system_documents.system_documents import get

__components__ = get("__components__")
