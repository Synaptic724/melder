import builtins
import threading
from typing import Dict
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces import ICodegenNamespaceConfiguration


class CodegenBuiltinsStrategy(Cleanable):
    """
    Internal

    Namespace exposure strategy for Python builtins.

    Purpose:
        Build the runtime `__builtins__` mapping from the current namespace
        configuration so codegen execution respects the compiled builtin
        denylist.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize the builtins exposure strategy.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Idempotently cleanup the builtins strategy.

        Returns:
            None.
        """
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
    ) -> Dict[str, object]:
        """
        Build builtins namespace entries for one request.

        Args:
            configuration:
                Namespace configuration for the request.

        Returns:
            Dict[str, object]: Builtins namespace entries.

        Raises:
            TypeError:
                If `configuration` is None.
        """
        self.check_cleaned()
        with self._lock:
            if configuration is None:
                raise TypeError("configuration cannot be None.")
            builtins_dict = dict(vars(builtins))
            for builtin_name in configuration.denied_builtin_names:
                builtins_dict.pop(builtin_name, None)
            return {
                "__builtins__": builtins_dict,
            }
