from typing import Any, Protocol, Tuple, runtime_checkable
from melder.utilities.interfaces.idescriptorpayload import IDescriptorPayload

@runtime_checkable
class IFrameDescriptorPayload(IDescriptorPayload, Protocol):
    """
    Descriptor-safe frame payload contract.

    Purpose:
        Define the minimum descriptor-safe frame payload shape stored by
        `FrameRecord`.
    """

    system_state: Any
    ai_native_enabled: bool
    rift_enabled: bool
    root_conduit_count: int
    root_conduit_ids: Tuple[str, ...]
    named_root_conduits: Tuple[Tuple[str, str], ...]
    conduit_cloud_entry_count: int
    conduit_cloud_names: Tuple[str, ...]
    cluster_count: int
    cluster_names: Tuple[str, ...]
