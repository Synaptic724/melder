"""
Packaged hardcopy runtime object for Melder components documentation.

Purpose:
    Publish `melder.__components__`, the C3/C2/C1 system document an agent
    queries AFTER architecture to get component responsibilities, contracts,
    owned state, concurrency posture, and method-level call flows.

Contract:
    - Module-level `StaticSystemDocument` instance, built at import.
    - `render_markdown()` returns the document body; `render_json()` returns the
      raw hardcopy envelope.
    - CURRENT STATE: the payload is a PLACEHOLDER, not a live regenerated
      components snapshot. Populating it is tracked separately from the
      contract work.

Subsystem Context:
    Second of the four package-root document surfaces. Architecture answers
    "what is the shape of the system"; this answers "what does each part own and
    guarantee". Hands off to the graph documents for structural relationships.

System Context:
    Answers at import time, before the `Aether()` substrate boot, and is
    queryable WITHOUT conjuring a conduit. It participates in no binding,
    resolution, or cleanup path.
"""

from melder.system_document import StaticSystemDocument


__components__ = StaticSystemDocument(
    document_name="__components__",
    document_json='{"m":"placeholder: packaged Melder components hardcopy"}',
    agent_purpose=(
        "access: public. Top-level Melder components document object. "
        "Query this after architecture for component-level understanding."
    ),
)
