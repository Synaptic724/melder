import threading
from typing import TYPE_CHECKING, Dict
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
        CodegenNamespaceConfiguration,
    )
    from melder.nexus.rift.rift_space.codegen_rift_space import CodegenRiftSpace


class CodegenCommandStrategy(Cleanable):
    """
    Internal

    Namespace exposure strategy for the room-facing command surface.

    Purpose:
        Expose the existing room-local command object into the codegen
        namespace when enabled by configuration.

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
        It exposes the room-local command object when configuration enables it. Every strategy exposes ONLY what the namespace configuration
        enables, which is what keeps the exposed surface a declared policy
        rather than an emergent consequence of construction order.
        Exposing the room's own command surface means generated code acts through the SAME mediated path a human uses, so ACL enforcement and memory emission apply identically rather than being bypassed by a private route.
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
            space: CodegenRiftSpace,
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
