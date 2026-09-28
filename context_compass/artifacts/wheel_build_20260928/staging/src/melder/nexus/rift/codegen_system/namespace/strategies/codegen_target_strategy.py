import threading
from typing import TYPE_CHECKING, Dict

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
        CodegenNamespaceConfiguration,
    )
    from melder.nexus.rift.rift_space.codegen_rift_space import CodegenRiftSpace


class CodegenTargetStrategy(Cleanable):
    """
    Internal

    Namespace exposure strategy for the current room target.

    Purpose:
        Expose the currently selected workstation target into the namespace
        while keeping missing-target behavior non-fatal.

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
        It exposes the currently selected workstation target, keeping a missing target non-fatal. Every strategy exposes ONLY what the namespace configuration
        enables, which is what keeps the exposed surface a declared policy
        rather than an emergent consequence of construction order.
        Non-fatal absence is correct because a room legitimately has no active target much of the time; raising would make the presence of a target a precondition for running any generated code at all.
        The strategy split is what makes the namespace auditable: reading which
        strategies ran, and what configuration enabled, answers "what could this
        code reach" without tracing builder code.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Namespace exposure strategy for the current room target. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """

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
            configuration: CodegenNamespaceConfiguration,
            *,
            space: CodegenRiftSpace,
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
