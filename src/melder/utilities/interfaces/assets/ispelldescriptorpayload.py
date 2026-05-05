from typing import Any, Dict, Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.assets.idescriptorpayload import IDescriptorPayload

@runtime_checkable
class ISpellDescriptorPayload(IDescriptorPayload, Protocol):
    """
    Descriptor-safe spell payload contract.

    Purpose:
        Define the minimum sanitized spell payload shape stored by `SpellRecord`.
    """

    payload_type: str
    source_profile_name: Optional[str]
    source_profile_version: Optional[str]
    binding_payload: Dict[str, Any]
    resolution_payload: Any
    class_profile: Any
    callable_profile: Any
    metadata: Dict[str, Any]
    instance_members: Dict[str, Any]
    dynamic_access: Dict[str, bool]
