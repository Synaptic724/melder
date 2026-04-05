import threading
from typing import List

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.nexus.acl.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_configuration_chain import FrameACLConfigurationChain
from melder.aether.nexus.acl.frame_acl_validator import FrameACLValidator


class FrameACLContainer(Cleanable):
    """
    Internal

    Holder for the unique ACL objects for one frame.

    Purpose:
        Keep the one builder object, current configuration, bounded history,
        and validator grouped together for one frame without confusing that ACL
        state with the descriptor's canonical runtime state.

    Contract:
        - One container per frame.
        - Owns one builder object for that frame.
        - Owns the current configuration plus bounded history.
        - Owns one validator object for that frame.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_frame_name",
        "_frame_acl_configuration_chain",
        "_frame_acl_validator",
        "_frame_acl_builder",
    ]

    def __init__(
            self,
            frame_name: str,
            *,
            history_limit: int = 15,
    ) -> None:
        """
        Initialize one frame ACL container.

        Args:
            frame_name:
                Owning frame name.
            history_limit:
                Maximum number of prior configurations retained in history.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not isinstance(history_limit, int) or history_limit < 1:
            raise ValueError("history_limit must be an integer >= 1.")

        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._frame_acl_configuration_chain: FrameACLConfigurationChain = (
            FrameACLConfigurationChain(
                frame_name,
                history_limit=history_limit,
            )
        )
        self._frame_acl_validator: FrameACLValidator = FrameACLValidator(frame_name)
        self._frame_acl_builder: FrameACLBuilder = FrameACLBuilder(self)

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
    def frame_acl_builder(self) -> FrameACLBuilder:
        """
        Return the unique builder object for this frame container.

        Returns:
            FrameACLBuilder: Unique builder object.
        """
        self.check_cleaned()
        return self._frame_acl_builder

    @property
    def frame_acl_configuration(self) -> FrameACLConfiguration:
        """
        Return the current frame ACL configuration.

        Returns:
            FrameACLConfiguration: Current configuration.
        """
        self.check_cleaned()
        return self._frame_acl_configuration_chain.get_current_configuration()

    @property
    def frame_acl_configuration_chain(self) -> FrameACLConfigurationChain:
        """
        Return the frame-scoped ACL configuration chain.

        Returns:
            FrameACLConfigurationChain: Frame-scoped configuration chain.
        """
        self.check_cleaned()
        return self._frame_acl_configuration_chain

    @property
    def frame_acl_validator(self) -> FrameACLValidator:
        """
        Return the frame-scoped ACL validator.

        Returns:
            FrameACLValidator: Frame-scoped validator.
        """
        self.check_cleaned()
        return self._frame_acl_validator

    @property
    def frame_acl_history(self) -> List[FrameACLConfiguration]:
        """
        Return a snapshot of retained configuration history.

        Returns:
            List[FrameACLConfiguration]: Snapshot of prior configurations.
        """
        self.check_cleaned()
        current_configuration_id = (
            self._frame_acl_configuration_chain.current_configuration_id
        )
        return [
            configuration
            for configuration in self._frame_acl_configuration_chain.list_configurations()
            if configuration.configuration_id != current_configuration_id
        ]

    def install_configuration(
            self,
            configuration: FrameACLConfiguration,
    ) -> None:
        """
        Validate and install the next frame ACL configuration revision.

        Args:
            configuration:
                New frame ACL configuration.

        Returns:
            None.
        """
        self.check_cleaned()
        self._frame_acl_validator.validate_configuration(configuration)
        self._frame_acl_configuration_chain.insert_head_configuration(
            configuration,
            select_as_current=True,
        )

    def select_current_configuration(
            self,
            configuration_id: str,
    ) -> FrameACLConfiguration:
        """
        Select one existing configuration in the chain as current.

        Args:
            configuration_id:
                Config id to make current.

        Returns:
            FrameACLConfiguration: Newly selected current configuration.
        """
        self.check_cleaned()
        return self._frame_acl_configuration_chain.select_current_configuration(
            configuration_id
        )

    def rollback_to_configuration(
            self,
            configuration_id: str,
    ) -> FrameACLConfiguration:
        """
        Roll current selection back to one historical config.

        Args:
            configuration_id:
                Config id to make current.

        Returns:
            FrameACLConfiguration: Newly selected current configuration.
        """
        self.check_cleaned()
        return self._frame_acl_configuration_chain.rollback_to_configuration(
            configuration_id
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the container and all owned ACL objects.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frame_acl_builder.cleanup()
            self._frame_acl_validator.cleanup()
            self._frame_acl_configuration_chain.cleanup()
            self._frame_acl_builder = None
            self._frame_acl_validator = None
            self._frame_acl_configuration_chain = None
            self._frame_name = None
        self._lock = None
