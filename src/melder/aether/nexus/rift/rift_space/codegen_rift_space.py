from typing import Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)
from melder.aether.nexus.rift.command_system.codegen_command_system import (
    CodegenCommandSystem,
)
from melder.aether.nexus.rift.codegen_system.codegen_system import CodegenSystem
from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.utilities.interfaces.interfaces import ICodegenRiftSpace, IRift, IRiftGate


class CodegenRiftSpace(RiftSpace, ICodegenRiftSpace):
    """

    __slots__ = [
        "_codegen_system",
    ]
    Internal

    Purpose:
        Represent the richer concrete room type for codegen/local-construction
        workflows.

    Contract:
        - Inherits all base room behavior.
        - Fixes `space_kind` to `codegen`.
        - Represents the richer room surface intended for local construction,
          mutable room state, and more open-ended workflows.
        - Currently composes a slim selected runtime-helper surface plus the
          placeholder codegen execution seams.
        - Reserved as the codegen-oriented room rather than a duplicate of the
          broad capability manual-runtime posture.
    """

    __melder_internal__ = _mrg.sentinel
    def __init__(
            self,
            owner_rift_id: str,
            *,
            rift: IRift,
            space_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
            rift_gate: Optional[IRiftGate] = None,
            space_id: Optional[str] = None,
    ) -> None:
        """
        Internal

        Initialize a codegen room.

        Args:
            owner_rift_id:
                Canonical owning Rift id.
            rift:
                Owning `Rift` that manages projection-driven asset updates.
            space_name:
                Optional stable room name.
            metadata:
                Extensible room metadata.
            rift_gate:
                Optional Rift-owned gate bound to this room.
            space_id:
                Optional explicit room id.

        Returns:
            None.

        Contract:
            Delegates all storage and lifecycle behavior to `RiftSpace` while
            fixing the room kind to `codegen` and composing the codegen command
            surface.
        """
        super().__init__(
            owner_rift_id,
            rift=rift,
            space_name=space_name,
            space_kind="codegen",
            metadata=metadata,
            rift_gate=rift_gate,
            space_id=space_id,
        )
        self._codegen_system: CodegenSystem = CodegenSystem(
            rift=rift,
            space=self,
        )
        self._command_system.attach_codegen_system(self._codegen_system)

    def _create_command_system(self, rift: IRift) -> CommandSystem:
        """
        Build the codegen room's command system.

        Returns:
            CommandSystem: Codegen-room command surface.
        """
        return CodegenCommandSystem(
            rift=rift,
            space=self,
            workstation=self._workstation,
        )

    @property
    def codegen_system(self) -> CodegenSystem:
        """
        Return the room-owned internal codegen system.

        Returns:
            CodegenSystem: Room-owned codegen system.
        """
        self.check_cleaned()
        return self._codegen_system

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup the owned codegen system before base room teardown.

        Returns:
            None.
        """
        if self._cleaned:
            return
        if self._codegen_system is not None:
            self._codegen_system.cleanup()
            self._codegen_system = None
        super().cleanup()
