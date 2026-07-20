import threading
from typing import TYPE_CHECKING, Dict
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
        CodegenNamespaceConfiguration,
    )
    from melder.nexus.rift.rift import Rift
    from melder.nexus.rift.rift_space.codegen_rift_space import CodegenRiftSpace


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
        It exposes the stable room and runtime objects that form the initial namespace contract. Every strategy exposes ONLY what the namespace configuration
        enables, which is what keeps the exposed surface a declared policy
        rather than an emergent consequence of construction order.
        Owning room-object exposure ONLY, and nothing else, is what keeps the boundary reviewable - a single strategy widening its scope would quietly become the place everything gets added.
        The strategy split is what makes the namespace auditable: reading which
        strategies ran, and what configuration enabled, answers "what could this
        code reach" without tracing builder code.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Namespace exposure strategy for stable room/runtime objects. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
    )

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
            configuration: CodegenNamespaceConfiguration,
            *,
            rift: Rift,
            space: CodegenRiftSpace,
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
