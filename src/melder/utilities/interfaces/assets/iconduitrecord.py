from typing import runtime_checkable, Protocol, Optional

from melder.utilities.interfaces.assets.icleanable import ICleanable


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
