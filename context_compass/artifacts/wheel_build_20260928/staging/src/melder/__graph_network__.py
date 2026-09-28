"""
Melder's dependency graph, walkable in-process.

Purpose:
    Publish `melder.__graph_network__` - the graph's SHAPE. Every source file
    melder defines, every node in it, and every edge between them, resolved at
    build time from the `Edges out` tables of
    `context_compass/system_docs/src_graph.md`.

Contract:
    - A `SystemGraphView`: everything `__graph_details__` can slice, plus
      traversal.
    - `node(id)`, `edges_from(id)`, `edges_to(id)`, `neighbors(id)`,
      `walk(id, depth=...)`. The walk yields as it goes and is breadth-first,
      so an agent can stop at the first useful hop.
    - `edges_to` is REVERSE lookup. Reading the document that is the expensive
      query - sections carry outbound edges only - but the build pass sees every
      row, so here it costs the same as the forward direction.
    - TRUST IS NOT UNIFORM. Every edge carries `origin`: `derived` came from the
      syntax tree and is rebuilt each extraction; `authored` was written by hand
      and may describe code that has since moved. Filter with
      `walk(..., origin=...)` rather than treating the two alike. Nodes carry
      `unsemantic` for the same reason - scaffold with no authored meaning.
    - EDGE CANDIDATES ARE ABSENT. The extractor's instantiation guesses
      over-generate roughly 8x and are leads, not edges. They are not in the
      shipped adjacency, so no walk can traverse one by accident.
    - `details_key(id)` and `describe(id)` join a walked node to the prose
      describing it.

Example:
    >>> import melder
    >>> graph = melder.__graph_network__
    >>> node = "melder.aether.conduit.conduit.Conduit"
    >>> [e.target.rsplit(".", 1)[-1]
    ...  for e in graph.edges_from(node, relation="owns_lifecycle_of")][:3]
    ['DevopsIdentity', 'ConduitPool', 'ConduitWard']
    >>> graph.details_key(node)
    'src/melder/aether/conduit/conduit.py'

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

__graph_network__ = get("__graph_network__")
