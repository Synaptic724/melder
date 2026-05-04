from typing import runtime_checkable, Protocol, Optional

from melder.utilities.interfaces.assets.icleanable import ICleanable


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
