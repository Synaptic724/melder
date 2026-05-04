from typing import runtime_checkable, Protocol, Optional, Any, Tuple

from melder.utilities.interfaces.assets.idescriptorpayload import IDescriptorPayload


@runtime_checkable
class IConduitDescriptorPayload(IDescriptorPayload, Protocol):
    """
    Descriptor-safe conduit payload contract.

    Purpose:
        Define the minimum descriptor-safe conduit payload shape stored by
        `ConduitRecord`.
    """

    conduit_name: Optional[str]
    conduit_state: Any
    policy: Any
    peer_conduit_ids: Tuple[str, ...]
    parent_conduit_id: Optional[str]
    lineage_depth: int
