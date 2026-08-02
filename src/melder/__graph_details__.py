"""
Melder's per-file graph documentation, queryable in-process.

Purpose:
    Publish `melder.__graph_details__` - the prose behind the graph. For each
    source file: its nodes, their roles and responsibilities, its outbound
    edges, the why-lines justifying authored claims, the unconfirmed edge
    candidates, and its published aliases.

Contract:
    - A `SystemGraphView`, addressed by SOURCE PATH, not by heading. The key for
      a file is its repository-relative path, which is also what
      `__graph_network__.details_key(node_id)` returns.
    - 24,730 lines across 575 sections. `index()` then `get(key)`; a single
      file's section is typically 20-80 lines. `stream(key)` pages the large
      ones.
    - The payload is imported on FIRST slice, so importing melder does not
      compile 1.6 MB of documentation.
    - TRUST TIERS DIFFER BY FIELD within a single section. Node identity,
      `bases` and `specializes` are mechanical. `role`, `responsibilities`,
      `owns_state`, `phases` and any authored edge were written by a reader of
      the code and can be stale. A node marked UNSEMANTIC has structure but no
      established meaning - do not infer purpose from its name. Edge candidates
      are guesses.
    - `verify()` re-checks the shipped text against its recorded digest.

Example:
    >>> import melder
    >>> view = melder.__graph_details__
    >>> [s.key for s in view.find("conduit/conduit_pool")]
    ['src/melder/aether/conduit/conduit_pool.py']

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

__graph_details__ = get("__graph_details__")
