from typing import Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLValidator(Cleanable):
    """
    Purpose:
        Validate that frame-local ACL configuration nodes are structurally
        compatible with one owning frame.

    Contract:
        - Confirms that a configuration node belongs to the expected frame.
        - Records the last validated configuration id for diagnostics.
        - Does not attempt to implement the full ACL rule engine in this
          placeholder slice.

    Lifecycle:
        Cleanup is idempotent and clears the last-validation marker plus the
        owning frame reference.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_frame_name",
        "_last_validated_configuration_id",
    ]

    def __init__(self, frame_name: str) -> None:
        """
        Initialize one frame-scoped ACL validator.

        Purpose:
            Bind the validator to one owning frame name.

        Contract:
            `frame_name` must be a non-empty stable frame identity.

        Args:
            frame_name:
                Owning frame name.

        Returns:
            None.

        Raises:
            ValueError:
                If `frame_name` is empty.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._frame_name: str = frame_name
        self._last_validated_configuration_id: Optional[str] = None

    def cleanup(self) -> None:
        """
        Idempotently clear validator state.

        Purpose:
            Tear down the validator's frame binding and last-validation marker.

        Contract:
            Safe to call more than once.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._frame_name = None
        self._last_validated_configuration_id = None

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name.

        Purpose:
            Expose the stable frame identity this validator enforces.

        Returns:
            str: Owning frame name.
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def last_validated_configuration_id(self) -> Optional[str]:
        """
        Return the last validated configuration id when known.

        Purpose:
            Expose the most recent successful validation target for diagnostics.

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

        Purpose:
            Confirm that a candidate configuration node belongs to the same
            frame as the validator.

        Args:
            configuration:
                Candidate frame ACL configuration node.

        Returns:
            bool: True when the configuration belongs to the same frame.

        Raises:
            TypeError:
                If `configuration` is not a `FrameACLConfiguration`.
            ValueError:
                If the configuration targets another frame.
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
