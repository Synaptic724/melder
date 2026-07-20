import threading
from typing import TYPE_CHECKING, Dict
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.rift.codegen_system.namespace.codegen_control_surface import (
    CodegenControlSurface,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
        CodegenNamespaceConfiguration,
    )
    from melder.nexus.rift.rift_space.codegen_rift_space import CodegenRiftSpace


class CodegenControlStrategy(Cleanable):
    """
    Internal

    Namespace exposure strategy for the room-owned codegen object.

    Purpose:
        Expose the room-owned internal codegen system as the `codegen`
        namespace object when enabled by configuration.

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
        It exposes the room-owned codegen system as the `codegen` namespace object when enabled. Every strategy exposes ONLY what the namespace configuration
        enables, which is what keeps the exposed surface a declared policy
        rather than an emergent consequence of construction order.
        It exposes `CodegenControlSurface` rather than the raw `CodegenSystem`, which is what keeps the engine's internals - validator, compiler, executor - unreachable from generated code.
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
        Initialize the codegen control-surface exposure strategy.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Idempotently cleanup the control-surface exposure strategy.

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
            space: CodegenRiftSpace,
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
