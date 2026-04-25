import threading
from typing import Dict

from melder.aether.nexus.rift.codegen_system.namespace.codegen_control_surface import (
    CodegenControlSurface,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import (
    ICodegenNamespaceConfiguration,
    ICodegenRiftSpace,
)


class CodegenControlStrategy(Cleanable):
    """
    Internal

    Namespace exposure strategy for the room-owned codegen object.

    Purpose:
        Expose the room-owned internal codegen system as the `codegen`
        namespace object when enabled by configuration.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
        self._lock = None

    def build_namespace_entries(
            self,
            configuration: ICodegenNamespaceConfiguration,
            *,
            space: ICodegenRiftSpace,
    ) -> Dict[str, object]:
        """
        Build codegen namespace entries for one request.

        Args:
            configuration:
                Namespace configuration for the request.
            space:
                Owning `CodegenRiftSpace`.

        Returns:
            Dict[str, object]: Codegen namespace entries.
        """
        self.check_cleaned()
        with self._lock:
            if configuration is None:
                raise TypeError("configuration cannot be None.")
            if space is None:
                raise TypeError("space cannot be None.")
            if "codegen" not in configuration.exposed_names:
                return {}
            return {
                "codegen": CodegenControlSurface(
                    codegen_system=space.codegen_system,
                    default_frame_name=configuration.frame_name,
                    recursive_codegen_allowed=(
                        configuration.allow_recursive_codegen
                    ),
                ),
            }
