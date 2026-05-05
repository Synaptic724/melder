from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.assets.icleanable import ICleanable

@runtime_checkable
class IDescriptorPayload(ICleanable, Protocol):
    """
    Base contract for descriptor-safe published payloads.

    Purpose:
        Define the minimum shape required for payloads stored on descriptor
        records.
    """

    payload_version: str
