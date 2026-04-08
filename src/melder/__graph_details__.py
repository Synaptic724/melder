"""
Packaged hardcopy runtime object for future Melder graph-details documentation.
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
