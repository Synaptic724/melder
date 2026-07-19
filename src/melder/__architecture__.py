"""
Packaged hardcopy runtime object for Melder architecture documentation.

Purpose:
    Publish `melder.__architecture__`, the C4-level system document an agent
    queries FIRST to understand Melder top-down: boundaries, entrypoints, boot
    and configuration sequencing, and execution lifecycle.

Contract:
    - Module-level `StaticSystemDocument` instance, built at import.
    - `render_markdown()` returns the document body; `render_json()` returns the
      raw hardcopy envelope.
    - CURRENT STATE: the payload is a PLACEHOLDER, not a live regenerated
      architecture snapshot. Populating it is tracked separately from the
      contract work.

Subsystem Context:
    One of four package-root document surfaces built on
    `melder.system_document.StaticSystemDocument`. Read order for an agent is
    architecture -> components -> graph network -> graph details: this document
    is the entry point of that chain.

System Context:
    Answers at import time, before the `Aether()` substrate boot, and is
    queryable WITHOUT conjuring a conduit. It participates in no binding,
    resolution, or cleanup path.
"""

from melder.system_document import StaticSystemDocument


__architecture__ = StaticSystemDocument(
    document_name="__architecture__",
    document_json='{"m":"placeholder: packaged Melder architecture hardcopy"}',
    agent_purpose=(
        "access: public. Top-level Melder architecture document object. "
        "Query this first for top-down system understanding."
    ),
)
