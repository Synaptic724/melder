import threading
from typing import Dict
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces import (
    ICodegenNamespaceConfiguration,
    ICodegenRiftSpace,
)


class CodegenTargetStrategy(Cleanable):
    """
    Internal

    Namespace exposure strategy for the current room target.

    Purpose:
        Expose the currently selected workstation target into the namespace
        while keeping missing-target behavior non-fatal.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize the target exposure strategy.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Idempotently cleanup the target exposure strategy.

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
            space: ICodegenRiftSpace,
    ) -> Dict[str, object]:
        """
        Build target namespace entries for one request.

        Args:
            configuration:
                Namespace configuration for the request.
            space:
                Owning `CodegenRiftSpace`.

        Returns:
            Dict[str, object]: Target namespace entries.

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
            if "target" not in configuration.exposed_names:
                return {}
            try:
                target = space.workstation.get_target()
            except ValueError:
                target = None
            return {
                "target": target,
            }
