from typing import Dict, Optional

from melder.aether.nexus.rift.rift_space.command_system.capability_command_system import (
    CapabilityCommandSystem,
)
from melder.aether.nexus.rift.rift_space.command_system.command_system import (
    CommandSystem,
)
from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.utilities.interfaces.interfaces import (
    ICapabilityRiftSpace,
    IRiftEventConfiguration,
)


class CapabilityRiftSpace(RiftSpace, ICapabilityRiftSpace):
    """
    Internal

    Purpose:
        Represent the middle-ground concrete room type for broad manual runtime
        access without codegen.

    Contract:
        - Inherits all base room behavior.
        - Fixes `space_kind` to `capability`.
        - Exists as the non-codegen manual runtime posture between strict
          static and later codegen-oriented dynamic work.
        - Allows broad manual object/runtime work through the composed command
          surface.
        - Does not override underlying Melder frame/runtime truth.
        - Uses the generic viewer posture.
        - Workstation defaults strong when binds omit `weak_ref`.
        - Keeps deeper conduit APIs object-oriented once callers obtain the
          conduit object instead of mirroring every lower method into command.
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

        Initialize a capability room.

        Purpose:
            Materialize one `RiftSpace` instance whose room kind is fixed to
            the capability posture.

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
            - Delegates all storage and lifecycle behavior to `RiftSpace`.
            - Fixes the persisted room kind to `capability` so later room
              selection and serialization can distinguish it from `static` and
              `dynamic` rooms.
            - Composes the broad manual capability command surface for this
              room.
        """
        super().__init__(
            owner_rift_id,
            space_name=space_name,
            space_kind="capability",
            metadata=metadata,
            event_configuration=event_configuration,
            space_id=space_id,
        )

    def _create_command_system(self) -> CommandSystem:
        """
        Build the capability room's command system.

        Returns:
            CommandSystem: Capability-room command surface.
        """
        return CapabilityCommandSystem(
            space=self,
            workstation=self._workstation,
        )
