import threading
from typing import Dict
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable
from melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import CodegenNamespaceConfiguration
from melder.utilities.interfaces.icodegenriftspace import ICodegenRiftSpace


class CodegenCommandStrategy(Cleanable):
    """
    Internal

    Namespace exposure strategy for the room-facing command surface.

    Purpose:
        Expose the existing room-local command object into the codegen
        namespace when enabled by configuration.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize the command exposure strategy.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Idempotently cleanup the command exposure strategy.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
        del self._lock

    def build_namespace_entries(
            self,
            configuration: CodegenNamespaceConfiguration,
            *,
            space: ICodegenRiftSpace,
    ) -> Dict[str, object]:
        """
        Build command namespace entries for one request.

        Args:
            configuration:
                Namespace configuration for the request.
            space:
                Owning `CodegenRiftSpace`.

        Returns:
            Dict[str, object]: Command namespace entries.

        Raises:
            TypeError:
                If `configuration` or `space` is None.
        """
        self.check_cleaned()
        with self._lock:
            if configuration is None:
                raise TypeError("configuration cannot be None.")
            if space is None:
                raise TypeError("space cannot be None.")
            if "command" not in configuration.exposed_names:
                return {}
            return {
                "command": space.command_system,
            }
