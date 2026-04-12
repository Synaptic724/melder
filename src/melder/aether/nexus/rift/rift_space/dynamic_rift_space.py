from typing import Dict, Optional

from melder.aether.nexus.rift.rift_space.command_system.command_system import (
    CommandSystem,
)
from melder.aether.nexus.rift.rift_space.command_system.dynamic_command_system import (
    DynamicCommandSystem,
)
from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.utilities.interfaces.interfaces import IDynamicRiftSpace, IRiftEventConfiguration


class DynamicRiftSpace(RiftSpace, IDynamicRiftSpace):
    """
    Internal

    Purpose:
        Represent the richer concrete room type for dynamic/local-construction
        workflows.

    Contract:
        - Inherits all base room behavior.
        - Fixes `space_kind` to `dynamic`.
        - Represents the richer room surface intended for local construction,
          mutable room state, and more open-ended workflows.
        - Currently shares the same broad manual runtime command posture as
          capability.
        - Reserved for later codegen-oriented differentiation rather than a
          different current manual-runtime policy.
    """

    def __init__(
            self,
            owner_rift_id: str,
            *,
            space_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
            event_configuration: Optional[IRiftEventConfiguration] = None,
            space_id: Optional[str] = None,
    ) -> None:
        """
        Internal

        Initialize a dynamic room.

        Args:
            owner_rift_id:
                Canonical owning Rift id.
            space_name:
                Optional stable room name.
            metadata:
                Extensible room metadata.
            event_configuration:
                Optional room-level event configuration.
            space_id:
                Optional explicit room id.

        Returns:
            None.

        Contract:
            Delegates all storage and lifecycle behavior to `RiftSpace` while
            fixing the room kind to `dynamic` and composing the dynamic command
            surface.
        """
        super().__init__(
            owner_rift_id,
            space_name=space_name,
            space_kind="dynamic",
            metadata=metadata,
            event_configuration=event_configuration,
            space_id=space_id,
        )

    def _create_command_system(self) -> CommandSystem:
        """
        Build the dynamic room's command system.

        Returns:
            CommandSystem: Dynamic-room command surface.
        """
        return DynamicCommandSystem(
            space=self,
            workstation=self._workstation,
        )
