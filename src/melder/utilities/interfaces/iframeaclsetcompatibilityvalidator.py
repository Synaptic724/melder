from typing import Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframeaclsetcompatibilityreport import IFrameACLSetCompatibilityReport

@runtime_checkable
class IFrameACLSetCompatibilityValidator(ICleanable, Protocol):
    """
    Frame-local validator for cross-set ACL bundle compatibility.
    """

    frame_name: str
    last_report: Optional[IFrameACLSetCompatibilityReport]
