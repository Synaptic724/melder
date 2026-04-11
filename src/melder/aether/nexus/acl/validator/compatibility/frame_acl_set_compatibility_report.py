from typing import List, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLSetCompatibilityReport(Cleanable):
    """
    Purpose:
        Hold one detached compatibility-validation result for a frame ACL
        bundle.

    Contract:
        - Records warning and error messages produced while validating one
          selected `FrameACLConfiguration` bundle.
        - Stores only detached primitive data and does not own live ACL objects.
        - Supports read-mostly inspection after validation completes.

    Lifecycle:
        Cleanup is idempotent and clears the recorded diagnostics.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_frame_name",
        "_configuration_id",
        "_warnings",
        "_errors",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            configuration_id: str,
    ) -> None:
        """
        Initialize one detached compatibility-validation report.

        Args:
            frame_name:
                Frame name for the validated ACL bundle.
            configuration_id:
                Bundle configuration id that produced this report.

        Returns:
            None.

        Raises:
            ValueError:
                If `frame_name` or `configuration_id` is empty.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not configuration_id:
            raise ValueError("configuration_id cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._frame_name: str = frame_name
        self._configuration_id: str = configuration_id
        self._warnings: List[str] = []
        self._errors: List[str] = []

    def cleanup(self) -> None:
        """
        Idempotently clear the compatibility-validation report.

        Contract:
            - Safe to call more than once.
            - Clears recorded warnings/errors and identity references.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._warnings.clear()
        self._errors.clear()
        self._frame_name = None
        self._configuration_id = None
        self._warnings = None
        self._errors = None
        self._id = None

    @property
    def frame_name(self) -> str:
        """
        Return the frame name associated with this report.

        Returns:
            str: Frame name for the validated bundle.
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def configuration_id(self) -> str:
        """
        Return the validated ACL bundle configuration id.

        Returns:
            str: Validated configuration id.
        """
        self.check_cleaned()
        return self._configuration_id

    @property
    def warnings(self) -> Tuple[str, ...]:
        """
        Return the recorded warning messages.

        Contract:
            Returns a detached tuple snapshot.

        Returns:
            Tuple[str, ...]: Warning messages.
        """
        self.check_cleaned()
        return tuple(self._warnings)

    @property
    def errors(self) -> Tuple[str, ...]:
        """
        Return the recorded error messages.

        Contract:
            Returns a detached tuple snapshot.

        Returns:
            Tuple[str, ...]: Error messages.
        """
        self.check_cleaned()
        return tuple(self._errors)

    @property
    def has_warnings(self) -> bool:
        """
        Return whether the report currently carries warnings.

        Returns:
            bool: True when warning messages exist.
        """
        self.check_cleaned()
        return len(self._warnings) > 0

    @property
    def has_errors(self) -> bool:
        """
        Return whether the report currently carries errors.

        Returns:
            bool: True when error messages exist.
        """
        self.check_cleaned()
        return len(self._errors) > 0

    def add_warning(self, message: str) -> None:
        """
        Record one warning message on the report.

        Args:
            message:
                Human-readable warning message.

        Returns:
            None.

        Raises:
            ValueError:
                If `message` is empty.
        """
        self.check_cleaned()
        if not message:
            raise ValueError("message cannot be empty.")
        self._warnings.append(message)

    def add_error(self, message: str) -> None:
        """
        Record one error message on the report.

        Args:
            message:
                Human-readable error message.

        Returns:
            None.

        Raises:
            ValueError:
                If `message` is empty.
        """
        self.check_cleaned()
        if not message:
            raise ValueError("message cannot be empty.")
        self._errors.append(message)

    def first_error(self) -> Optional[str]:
        """
        Return the first recorded error message when present.

        Returns:
            Optional[str]: First error message, or None.
        """
        self.check_cleaned()
        if len(self._errors) == 0:
            return None
        return self._errors[0]
