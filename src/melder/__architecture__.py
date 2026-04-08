"""
Packaged hardcopy runtime object for Melder architecture documentation.
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
