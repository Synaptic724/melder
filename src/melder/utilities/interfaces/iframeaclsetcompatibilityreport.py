from typing import Optional, Protocol, Tuple, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable

@runtime_checkable
class IFrameACLSetCompatibilityReport(ICleanable, Protocol):
    """
    Detached compatibility-validation report for one ACL bundle.
    """

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name for this report.
        """
        ...

    @property
    def configuration_id(self) -> str:
        """
        Return the validated ACL bundle configuration id.
        """
        ...

    @property
    def warnings(self) -> Tuple[str, ...]:
        """
        Return the recorded warning messages.
        """
        ...

    @property
    def errors(self) -> Tuple[str, ...]:
        """
        Return the recorded error messages.
        """
        ...

    @property
    def has_warnings(self) -> bool:
        """
        Return whether this report currently carries warnings.
        """
        ...

    @property
    def has_errors(self) -> bool:
        """
        Return whether this report currently carries errors.
        """
        ...

    def add_warning(self, message: str) -> None:
        """
        Record one warning message on the report.
        """
        ...

    def add_error(self, message: str) -> None:
        """
        Record one error message on the report.
        """
        ...

    def first_error(self) -> Optional[str]:
        """
        Return the first recorded error when one exists.
        """
        ...

