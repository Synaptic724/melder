"""
Packaged hardcopy runtime object for future Melder graph-network documentation.

Purpose:
    Publish `melder.__graph_network__`, the structural relationship map an agent
    queries to learn how objects wire together - who owns lifecycle, who only
    borrows, who creates, validates, publishes, or binds what.

Contract:
    - Module-level `StaticSystemDocument` instance, built at import.
    - `render_markdown()` returns the document body; `render_json()` returns the
      raw hardcopy envelope.
    - CURRENT STATE: the payload is a PLACEHOLDER. Until populated, an agent
      needing wiring truth reads the repository graph surface instead.

Subsystem Context:
    Third of the four package-root document surfaces. Architecture and
    components carry the narrative; this carries the topology. Pairs with
    `__graph_details__`, which explains how to interpret it.

System Context:
    Answers at import time, before the `Aether()` substrate boot, and is
    queryable WITHOUT conjuring a conduit. It participates in no binding,
    resolution, or cleanup path.
"""

from melder.system_document import StaticSystemDocument


__graph_network__ = StaticSystemDocument(
    document_name="__graph_network__",
    document_json='{"m":"placeholder: packaged Melder graph network hardcopy"}',
    agent_purpose=(
        "access: public. Top-level Melder graph-network document object. "
        "Query this for graph-network topology once the hardcopy is populated."
    ),
)
