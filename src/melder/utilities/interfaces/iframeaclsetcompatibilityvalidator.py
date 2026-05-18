from typing import Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframeaclconfiguration import IFrameACLConfiguration
from melder.utilities.interfaces.iframeaclsetcompatibilityreport import IFrameACLSetCompatibilityReport

@runtime_checkable
class IFrameACLSetCompatibilityValidator(ICleanable, Protocol):
    """
    Frame-local validator for cross-set ACL bundle compatibility.
    """

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name for this validator.
        """
        ...

    @property
    def last_report(self) -> Optional[IFrameACLSetCompatibilityReport]:
        """
        Return the most recent compatibility report when one exists.
        """
        ...

    def validate_configuration(
            self,
            configuration: IFrameACLConfiguration,
    ) -> IFrameACLSetCompatibilityReport:
        """
        Validate one selected frame ACL bundle for cross-set compatibility.
        """
        ...
