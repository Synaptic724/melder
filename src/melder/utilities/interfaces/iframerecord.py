from typing import Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframedescriptorpayload import IFrameDescriptorPayload

@runtime_checkable
class IFrameRecord(ICleanable, Protocol):
    """
    Descriptor-facing frame record contract.
    """

    nexus_label: str
    nexus_version: str
    frame_name: str
    frame_id: str
    config_origin_spellbook_id: Optional[str]
    payload: IFrameDescriptorPayload
