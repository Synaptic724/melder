import builtins
import threading
from typing import TYPE_CHECKING, Dict
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
        CodegenNamespaceConfiguration,
    )


class CodegenBuiltinsStrategy(Cleanable):
    """
    Internal

    Namespace exposure strategy for Python builtins.

    Purpose:
        Build the runtime `__builtins__` mapping from the current namespace
        configuration so codegen execution respects the compiled builtin
        denylist.

    Threading:
        Stateless exposure strategy; it contributes names to a namespace under
        construction and retains nothing.

    Registration:
        MELDER KERNEL - guarded. Consumed by `CodegenNamespaceBuilder`; never
        user-constructed.

    Subsystem Context:
        One member of the namespace-exposure strategy family. The builder
        composes them instead of hand-building one large globals dict, so each
        exposure decision has exactly one owner.

    System Context:
        It builds the runtime `__builtins__` mapping from the current configuration so execution respects the compiled builtin denylist. Every strategy exposes ONLY what the namespace configuration
        enables, which is what keeps the exposed surface a declared policy
        rather than an emergent consequence of construction order.
        This is the runtime half of builtin control, paired with the static `CodegenBuiltinPolicyStrategy`. Withholding the name is what makes the denial real even where static analysis missed the call.
        The strategy split is what makes the namespace auditable: reading which
        strategies ran, and what configuration enabled, answers "what could this
        code reach" without tracing builder code.
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
        del self._lock

    def build_namespace_entries(
            self,
            configuration: CodegenNamespaceConfiguration,
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
