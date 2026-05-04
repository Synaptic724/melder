from typing import runtime_checkable, Protocol, Optional

from melder.utilities.interfaces.assets.icleanable import ICleanable


@runtime_checkable
class IFrameACLSetCompatibilityValidator(ICleanable, Protocol):
    """
    Frame-local validator for cross-set ACL bundle compatibility.
    """

    frame_name: str
    last_report: Optional[IFrameACLSetCompatibilityReport]
