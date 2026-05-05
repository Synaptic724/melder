from typing import Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iconduitdescriptorpayload import IConduitDescriptorPayload

@runtime_checkable
class IConduitRecord(ICleanable, Protocol):
    """
    Descriptor-facing conduit record contract.
    """

    nexus_label: str
    nexus_version: str
    conduit_id: str
    root_conduit_id: str
    frame_name: str
    origin_spellbook_id: Optional[str]
    payload: IConduitDescriptorPayload
