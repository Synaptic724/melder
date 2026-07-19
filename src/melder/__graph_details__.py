"""
Packaged hardcopy runtime object for future Melder graph-details documentation.

Purpose:
    Publish `melder.__graph_details__`, the interpretation guide for the graph
    surface: what each node field and edge relation MEANS, so an agent reads
    `owns_lifecycle_of` versus `borrows` correctly instead of guessing.

Contract:
    - Module-level `StaticSystemDocument` instance, built at import.
    - `render_markdown()` returns the document body; `render_json()` returns the
      raw hardcopy envelope.
    - CURRENT STATE: the payload is a PLACEHOLDER. Until populated, edge and
      node semantics live in the repository's graph usage documentation.

Subsystem Context:
    Fourth of the four package-root document surfaces and the terminal one in
    the read chain. `__graph_network__` supplies the topology; this supplies the
    vocabulary needed to read it without inferring meaning from names.

System Context:
    Answers at import time, before the `Aether()` substrate boot, and is
    queryable WITHOUT conjuring a conduit. It participates in no binding,
    resolution, or cleanup path.
"""

from melder.system_document import StaticSystemDocument


__graph_details__ = StaticSystemDocument(
    document_name="__graph_details__",
    document_json='{"m":"placeholder: packaged Melder graph details hardcopy"}',
    agent_purpose=(
        "access: public. Top-level Melder graph-details document object. "
        "Query this for graph-detail explanations once the hardcopy is populated."
    ),
)
