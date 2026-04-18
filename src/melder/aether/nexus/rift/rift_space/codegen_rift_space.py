from typing import Dict, Optional

from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)
from melder.aether.nexus.rift.command_system.codegen_command_system import (
    CodegenCommandSystem,
)
from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.utilities.interfaces.interfaces import ICodegenRiftSpace, IRiftEventSystem, IRiftGate


class CodegenRiftSpace(RiftSpace, ICodegenRiftSpace):
    """
    Internal

    Purpose:
        Represent the richer concrete room type for codegen/local-construction
        workflows.

    Contract:
        - Inherits all base room behavior.
        - Fixes `space_kind` to `codegen`.
        - Represents the richer room surface intended for local construction,
          mutable room state, and more open-ended workflows.
        - Currently shares the same broad manual runtime command posture as
          capability.
        - Reserved as the codegen-oriented room rather than a different current
          manual-runtime policy.
    """

    def __init__(
            self,
            owner_rift_id: str,
            *,
            space_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
            rift_gate: Optional[IRiftGate] = None,
            event_system: Optional[IRiftEventSystem] = None,
            space_id: Optional[str] = None,
    ) -> None:
        """
        Internal

        Initialize a codegen room.

        Args:
            owner_rift_id:
                Canonical owning Rift id.
            space_name:
                Optional stable room name.
            metadata:
                Extensible room metadata.
            rift_gate:
                Optional Rift-owned gate bound to this room.
            event_system:
                Optional room-local event system.
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
            space_name=space_name,
            space_kind="codegen",
            metadata=metadata,
            rift_gate=rift_gate,
            event_system=event_system,
            space_id=space_id,
        )

    def _create_command_system(self) -> CommandSystem:
        """
        Build the codegen room's command system.

        Returns:
            CommandSystem: Codegen-room command surface.
        """
        return CodegenCommandSystem(
            space=self,
            workstation=self._workstation,
        )
