import threading
from typing import Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration


class FrameACLBuilder(Cleanable):
    """
    Internal

    Object-singleton builder for one frame ACL container.

    Purpose:
        Represent the one mutable authoring surface for one frame's ACL
        configuration without pretending to implement the full ACL mutation
        engine in this placeholder slice.

    Contract:
        - One builder object per frame ACL container.
        - Can open one local change session at a time.
        - Builds the next `FrameACLConfiguration` from a JSON payload string.
        - Delegates installation/validation to the owning container.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_container",
        "_change_active",
        "_draft_json_configuration_string",
    ]

    def __init__(self, container: object) -> None:
        """
        Initialize one frame ACL builder for the owning container.

        Args:
            container:
                Owning frame ACL container.
        """
        super().__init__()
        if container is None:
            raise TypeError("container cannot be None.")
        self._lock: threading.RLock = threading.RLock()
        self._container = container
        self._change_active: bool = False
        self._draft_json_configuration_string: Optional[str] = None

    @property
    def change_active(self) -> bool:
        """
        Return whether the builder currently owns one open change session.

        Returns:
            bool: True when a change session is active.
        """
        self.check_cleaned()
        with self._lock:
            return self._change_active

    def begin_change(self) -> None:
        """
        Start one builder-owned change session.

        Returns:
            None.

        Raises:
            RuntimeError: If a change session is already active.
        """
        self.check_cleaned()
        with self._lock:
            if self._change_active:
                raise RuntimeError("FrameACLBuilder already has an active change.")
            current_configuration = self._container.frame_acl_configuration
            self._draft_json_configuration_string = (
                current_configuration.to_json_string()
            )
            self._change_active = True

    def load_json_configuration_string(
            self,
            json_configuration_string: str,
    ) -> None:
        """
        Replace the draft JSON payload string for the active change session.

        Args:
            json_configuration_string:
                JSON payload string for the next configuration revision.

        Returns:
            None.

        Raises:
            RuntimeError: If no change session is active.
            TypeError: If `json_configuration_string` is not a string.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active:
                raise RuntimeError("FrameACLBuilder has no active change.")
            if not isinstance(json_configuration_string, str):
                raise TypeError("json_configuration_string must be a string.")
            self._draft_json_configuration_string = json_configuration_string

    def commit_change(self) -> FrameACLConfiguration:
        """
        Build and install the next frame ACL configuration revision.

        Returns:
            FrameACLConfiguration: Newly installed configuration.

        Raises:
            RuntimeError: If no change session is active.
        """
        self.check_cleaned()
        with self._lock:
            if not self._change_active:
                raise RuntimeError("FrameACLBuilder has no active change.")

            current_configuration = self._container.frame_acl_configuration
            next_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
                current_configuration,
                reason="builder_commit",
            )
            next_configuration.set_json_configuration_string(
                self._draft_json_configuration_string
            )
            next_configuration.finalize()
            self._container.install_configuration(next_configuration)
            self._draft_json_configuration_string = None
            self._change_active = False
            return next_configuration

    def discard_change(self) -> None:
        """
        Discard the current builder-owned change session.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._draft_json_configuration_string = None
            self._change_active = False

    def cleanup(self) -> None:
        """
        Idempotently clear builder state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._lock = None
        self._container = None
        self._change_active = None
        self._draft_json_configuration_string = None
