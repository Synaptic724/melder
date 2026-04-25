import threading
from typing import Dict

from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace import (
    CodegenNamespace,
)
from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)
from melder.aether.nexus.rift.codegen_system.namespace.strategies.codegen_command_strategy import (
    CodegenCommandStrategy,
)
from melder.aether.nexus.rift.codegen_system.namespace.strategies.codegen_room_objects_strategy import (
    CodegenRoomObjectsStrategy,
)
from melder.aether.nexus.rift.codegen_system.namespace.strategies.codegen_target_strategy import (
    CodegenTargetStrategy,
)
from melder.aether.nexus.rift.codegen_system.namespace.strategies.codegen_workstation_strategy import (
    CodegenWorkstationStrategy,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import (
    ICodegenNamespace,
    ICodegenNamespaceConfiguration,
    ICodegenRiftSpace,
    IRift,
)


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
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_room_objects_strategy",
        "_workstation_strategy",
        "_command_strategy",
        "_target_strategy",
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
        self._command_strategy: CodegenCommandStrategy = CodegenCommandStrategy()
        self._target_strategy: CodegenTargetStrategy = CodegenTargetStrategy()

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
            self._command_strategy.cleanup()
            self._target_strategy.cleanup()
            self._room_objects_strategy = None
            self._workstation_strategy = None
            self._command_strategy = None
            self._target_strategy = None
        self._lock = None

    def build(
            self,
            configuration: ICodegenNamespaceConfiguration,
            *,
            rift: IRift,
            space: ICodegenRiftSpace,
    ) -> ICodegenNamespace:
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
                self._command_strategy.build_namespace_entries(
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
            return CodegenNamespace(
                configuration=configuration,
                globals_dict=globals_dict,
                locals_dict={},
                metadata={
                    "exposed_names": configuration.exposed_names,
                },
            )
