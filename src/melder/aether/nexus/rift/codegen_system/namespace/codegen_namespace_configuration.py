import threading
from typing import Dict, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ICodegenNamespaceConfiguration


class CodegenNamespaceConfiguration(Cleanable, ICodegenNamespaceConfiguration):
    """
    Internal

    Namespace exposure policy for one codegen request.

    Purpose:
        Represent the policy/configuration view of which stable names the
        codegen runtime intends to expose before any live namespace objects are
        assembled.

    Contract:
        - Keeps stable namespace-name exposure explicit.
        - Separates policy/configuration from the live namespace object.
        - Returns exposed names in stable first-class order.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_frame_name",
        "_include_rift",
        "_include_space",
        "_include_viewer",
        "_include_workstation",
        "_include_command",
        "_include_target",
        "_include_frame_name",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            include_rift: bool = True,
            include_space: bool = True,
            include_viewer: bool = True,
            include_workstation: bool = True,
            include_command: bool = True,
            include_target: bool = True,
            include_frame_name: bool = True,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one namespace configuration.

        Args:
            frame_name:
                Target frame name for this configuration.
            include_rift:
                Whether to expose `rift`.
            include_space:
                Whether to expose `space`.
            include_viewer:
                Whether to expose `viewer`.
            include_workstation:
                Whether to expose `workstation`.
            include_command:
                Whether to expose `command`.
            include_target:
                Whether to expose `target`.
            include_frame_name:
                Whether to expose `frame_name`.
            metadata:
                Optional configuration metadata.

        Returns:
            None.

        Raises:
            ValueError:
                If `frame_name` is empty.
        """
        super().__init__()
        if not isinstance(frame_name, str) or not frame_name:
            raise ValueError("frame_name cannot be empty.")
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._include_rift: bool = include_rift
        self._include_space: bool = include_space
        self._include_viewer: bool = include_viewer
        self._include_workstation: bool = include_workstation
        self._include_command: bool = include_command
        self._include_target: bool = include_target
        self._include_frame_name: bool = include_frame_name
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Idempotently clear namespace-configuration-owned state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frame_name = None
            self._include_rift = None
            self._include_space = None
            self._include_viewer = None
            self._include_workstation = None
            self._include_command = None
            self._include_target = None
            self._include_frame_name = None
            self._metadata.clear()
            self._metadata = None
        self._lock = None

    @classmethod
    def create_default(
            cls,
            *,
            frame_name: str,
            metadata: Optional[Dict[str, object]] = None,
    ) -> "CodegenNamespaceConfiguration":
        """
        Build the current stable default namespace contract.

        Args:
            frame_name:
                Target frame name for the configuration.
            metadata:
                Optional configuration metadata.

        Returns:
            CodegenNamespaceConfiguration: Default configuration.
        """
        return cls(
            frame_name=frame_name,
            metadata=metadata,
        )

    @property
    def frame_name(self) -> str:
        """
        Return the target frame name for this namespace configuration.

        Returns:
            str: Target frame name.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_name

    @property
    def exposed_names(self) -> Tuple[str, ...]:
        """
        Return the stable ordered namespace names enabled by this config.

        Returns:
            Tuple[str, ...]: Enabled namespace names.
        """
        self.check_cleaned()
        with self._lock:
            enabled_names = []
            if self._include_rift:
                enabled_names.append("rift")
            if self._include_space:
                enabled_names.append("space")
            if self._include_viewer:
                enabled_names.append("viewer")
            if self._include_workstation:
                enabled_names.append("workstation")
            if self._include_command:
                enabled_names.append("command")
            if self._include_target:
                enabled_names.append("target")
            if self._include_frame_name:
                enabled_names.append("frame_name")
            return tuple(enabled_names)

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return a detached configuration metadata copy.

        Returns:
            Dict[str, object]: Detached metadata copy.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._metadata)
