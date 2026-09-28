import threading
from typing import TYPE_CHECKING, Dict

from melder.nexus.rift.codegen_system.namespace.codegen_namespace import (
    CodegenNamespace,
)
from melder.nexus.rift.codegen_system.namespace.strategies.codegen_builtins_strategy import (
    CodegenBuiltinsStrategy,
)
from melder.nexus.rift.codegen_system.namespace.strategies.codegen_command_strategy import (
    CodegenCommandStrategy,
)
from melder.nexus.rift.codegen_system.namespace.strategies.codegen_control_strategy import (
    CodegenControlStrategy,
)
from melder.nexus.rift.codegen_system.namespace.strategies.codegen_room_objects_strategy import (
    CodegenRoomObjectsStrategy,
)
from melder.nexus.rift.codegen_system.namespace.strategies.codegen_target_strategy import (
    CodegenTargetStrategy,
)
from melder.nexus.rift.codegen_system.namespace.strategies.codegen_workstation_strategy import (
    CodegenWorkstationStrategy,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
        CodegenNamespaceConfiguration,
    )
    from melder.nexus.rift.rift import Rift
    from melder.nexus.rift.rift_space.codegen_rift_space import CodegenRiftSpace


class CodegenNamespaceBuilder(Cleanable):
    """
    Internal

    Builder for live codegen namespaces.

    Purpose:
        Assemble one `CodegenNamespace` from explicit namespace configuration
        plus the current room/runtime objects.

    Contract:
        - Consumes namespace strategies instead of hand-building one giant
          globals dict.
        - Keeps policy/configuration separate from the built namespace object.
        - Uses only the current stable namespace contract for this slice.

    Registration:
        MELDER KERNEL - guarded. Owned by `CodegenSystem`.

    Subsystem Context:
        The assembler of `CodegenNamespace` from configuration plus the current
        room and runtime objects, composing the exposure strategy family.

    System Context:
        Consuming STRATEGIES instead of hand-building one giant globals dict is
        the design decision that makes namespace exposure reviewable. Each name
        that reaches generated code has exactly one strategy responsible for it,
        so a question like "how could this code see the workstation" has a
        single answer rather than requiring a read of one long constructor.
        Keeping policy and configuration separate from assembly is the matching
        rule: the builder decides HOW to expose, never WHETHER, so widening
        reach requires a configuration change rather than a builder edit.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Builder for live codegen namespaces. Melder kernel machinery: read it
        to understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_room_objects_strategy",
        "_workstation_strategy",
        "_target_strategy",
        "_command_strategy",
        "_codegen_control_strategy",
        "_builtins_strategy",
    ]

    def __init__(self) -> None:
        """
        Initialize the builder and its minimal strategy set.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._room_objects_strategy: CodegenRoomObjectsStrategy = (
            CodegenRoomObjectsStrategy()
        )
        self._workstation_strategy: CodegenWorkstationStrategy = (
            CodegenWorkstationStrategy()
        )
        self._target_strategy: CodegenTargetStrategy = CodegenTargetStrategy()
        self._command_strategy: CodegenCommandStrategy = CodegenCommandStrategy()
        self._codegen_control_strategy: CodegenControlStrategy = (
            CodegenControlStrategy()
        )
        self._builtins_strategy: CodegenBuiltinsStrategy = (
            CodegenBuiltinsStrategy()
        )

    def cleanup(self) -> None:
        """
        Idempotently clear builder-owned strategy references.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._room_objects_strategy.cleanup()
            self._workstation_strategy.cleanup()
            self._target_strategy.cleanup()
            self._command_strategy.cleanup()
            self._codegen_control_strategy.cleanup()
            self._builtins_strategy.cleanup()
            del self._room_objects_strategy
            del self._workstation_strategy
            del self._target_strategy
            del self._command_strategy
            del self._codegen_control_strategy
            del self._builtins_strategy
        del self._lock

    def build(
            self,
            configuration: CodegenNamespaceConfiguration,
            *,
            rift: Rift,
            space: CodegenRiftSpace,
    ) -> CodegenNamespace:
        """
        Build one live namespace from config and room/runtime state.

        Args:
            configuration:
                Namespace configuration for the request.
            rift:
                Owning `Rift`.
            space:
                Owning `CodegenRiftSpace`.

        Returns:
            CodegenNamespace: Built live namespace.

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
            globals_dict: Dict[str, object] = {}
            globals_dict.update(
                self._room_objects_strategy.build_namespace_entries(
                    configuration,
                    rift=rift,
                    space=space,
                )
            )
            globals_dict.update(
                self._workstation_strategy.build_namespace_entries(
                    configuration,
                    space=space,
                )
            )
            globals_dict.update(
                self._target_strategy.build_namespace_entries(
                    configuration,
                    space=space,
                )
            )
            globals_dict.update(
                self._command_strategy.build_namespace_entries(
                    configuration,
                    space=space,
                )
            )
            globals_dict.update(
                self._codegen_control_strategy.build_namespace_entries(
                    configuration,
                    space=space,
                )
            )
            globals_dict.update(
                self._builtins_strategy.build_namespace_entries(configuration)
            )
            return CodegenNamespace(
                configuration=configuration,
                globals_dict=globals_dict,
                locals_dict={},
                metadata={
                    "exposed_names": configuration.exposed_names,
                },
            )
