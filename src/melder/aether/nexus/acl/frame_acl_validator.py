from typing import Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration


class FrameACLValidator(Cleanable):
    """
    Internal

    Placeholder validator for one frame-scoped ACL subsystem.

    Purpose:
        Provide one concrete validator object for the frame ACL subsystem so the
        manager/container shape is real before the full ACL rule engine lands.

    Contract:
        - Validates that the configuration belongs to the expected frame.
        - Records the last validated configuration id for diagnostics.
        - Does not attempt to implement the full ACL rule engine in this
          placeholder slice.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_frame_name",
        "_last_validated_configuration_id",
    ]

    def __init__(self, frame_name: str) -> None:
        """
        Initialize one frame-scoped ACL validator.

        Args:
            frame_name:
                Owning frame name.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        self._frame_name: str = frame_name
        self._last_validated_configuration_id: Optional[str] = None

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name.

        Returns:
            str: Owning frame name.
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def last_validated_configuration_id(self) -> Optional[str]:
        """
        Return the last validated configuration id when known.

        Returns:
            Optional[str]: Last validated configuration id.
        """
        self.check_cleaned()
        return self._last_validated_configuration_id

    def validate_configuration(
            self,
            configuration: FrameACLConfiguration,
    ) -> bool:
        """
        Validate one frame ACL configuration against this validator's frame.

        Args:
            configuration:
                Frame ACL configuration to validate.

        Returns:
            bool: True when the configuration belongs to the same frame.

        Raises:
            TypeError: If `configuration` is not a `FrameACLConfiguration`.
            ValueError: If the configuration targets another frame.
        """
        self.check_cleaned()
        if not isinstance(configuration, FrameACLConfiguration):
            raise TypeError("configuration must be a FrameACLConfiguration.")
        if configuration.frame_name != self._frame_name:
            raise ValueError(
                "FrameACLConfiguration targets frame '{0}', expected '{1}'.".format(
                    configuration.frame_name,
                    self._frame_name,
                )
            )
        self._last_validated_configuration_id = configuration.configuration_id
        return True

    def cleanup(self) -> None:
        """
        Idempotently clear validator state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._frame_name = None
        self._last_validated_configuration_id = None
