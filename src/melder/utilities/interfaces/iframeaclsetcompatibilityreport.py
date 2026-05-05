from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable

@runtime_checkable
class IFrameACLSetCompatibilityReport(ICleanable, Protocol):
    """
    Detached compatibility-validation report for one ACL bundle.
    """

    frame_name: str
    configuration_id: str
    has_warnings: bool
    has_errors: bool
