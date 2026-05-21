from typing import Optional, Protocol, Tuple, runtime_checkable
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.interfaces.idescriptorpayload import IDescriptorPayload

@runtime_checkable
class IConduitDescriptorPayload(IDescriptorPayload, Protocol):
    """
    Descriptor-safe conduit payload contract.

    Purpose:
        Define the minimum descriptor-safe conduit payload shape stored by
        `ConduitRecord`.
    """

    conduit_name: Optional[str]
    conduit_state: ConduitState
    policy: Optional[Policies]
    peer_conduit_ids: Tuple[str, ...]
    parent_conduit_id: Optional[str]
    lineage_depth: int
