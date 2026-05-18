import threading
from typing import Dict
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.icodegennamespaceconfiguration import ICodegenNamespaceConfiguration
from melder.utilities.interfaces.icodegenriftspace import ICodegenRiftSpace
from melder.utilities.interfaces.irift import IRift


class CodegenRoomObjectsStrategy(Cleanable):
    """
    Internal

    Namespace exposure strategy for stable room/runtime objects.

    Purpose:
        Expose the stable room/runtime objects that belong in the initial
        codegen namespace contract.

    Contract:
        - Exposes only names enabled by the namespace configuration.
        - Owns room-object exposure only:
          `viewer`.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize the room-objects strategy.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Idempotently cleanup the strategy.

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
            configuration: ICodegenNamespaceConfiguration,
            *,
            rift: IRift,
            space: ICodegenRiftSpace,
    ) -> Dict[str, object]:
        """
        Build room-object namespace entries for one request.

        Args:
            configuration:
                Namespace configuration for the request.
            rift:
                Owning `Rift`.
            space:
                Owning `CodegenRiftSpace`.

        Returns:
            Dict[str, object]: Room-object namespace entries.

        Raises:
            TypeError:
                If `configuration`, `rift`, or `space` is None.
        """
        self.check_cleaned()
        with self._lock:
            if configuration is None:
                raise TypeError("configuration cannot be None.")
            if rift is None:
                raise TypeError("rift cannot be None.")
            if space is None:
                raise TypeError("space cannot be None.")
            namespace_entries: Dict[str, object] = {}
            exposed_names = configuration.exposed_names
            if "viewer" in exposed_names:
                namespace_entries["viewer"] = space.frame_viewer
            return namespace_entries
