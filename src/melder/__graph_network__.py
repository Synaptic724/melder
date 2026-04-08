"""
Packaged hardcopy runtime object for future Melder graph-network documentation.
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
