"""
Packaged hardcopy runtime object for Melder components documentation.
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
