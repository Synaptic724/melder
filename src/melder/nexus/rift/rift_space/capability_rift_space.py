from typing import Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.rift.command_system.capability_command_system import (
    CapabilityCommandSystem,
)
from melder.nexus.rift.command_system.command_system import (
    CommandSystem,
)
from melder.nexus.rift.rift_space.rift_space import RiftSpace
from melder.utilities.interfaces.iriftgate import IRiftGate


class CapabilityRiftSpace(RiftSpace):
    """
    Internal

    Purpose:
        Represent the middle-ground concrete room type for broad manual runtime
        access without codegen.

    Contract:
        - Inherits all base room behavior.
        - Fixes `space_kind` to `capability`.
        - Exists as the non-codegen manual runtime posture between strict
          static and later codegen-oriented work.
        - Allows broad manual object/runtime work through the composed command
          surface.
        - Does not override underlying Melder frame/runtime truth.
        - Uses the generic viewer posture.
        - Workstation defaults strong when binds omit `weak_ref`.
        - Keeps deeper conduit APIs object-oriented once callers obtain the
          conduit object instead of mirroring every lower method into command.
    """

    __melder_internal__ = _mrg.sentinel
    def __init__(
            self,
            owner_rift_id: str,
            *,
            rift: object,
            space_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
            rift_gate: Optional[IRiftGate] = None,
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
            - Delegates all storage and lifecycle behavior to `RiftSpace`.
            - Fixes the persisted room kind to `capability` so later room
              selection and serialization can distinguish it from `static` and
              `codegen` rooms.
            - Composes the broad manual capability command surface for this
              room.
        """
        super().__init__(
            owner_rift_id,
            rift=rift,
            space_name=space_name,
            space_kind="capability",
            metadata=metadata,
            rift_gate=rift_gate,
            space_id=space_id,
        )

    def _create_command_system(self, rift: object) -> CommandSystem:
        """
        Build the capability room's command system.

        Returns:
            CommandSystem: Capability-room command surface.
        """
        return CapabilityCommandSystem(
            rift=rift,
            space=self,
            workstation=self._workstation,
        )

    @property
    def command_system(self) -> CapabilityCommandSystem:
        """
        Return the room-local capability command system.

        Returns:
            CapabilityCommandSystem: Capability-room command surface owned by
            this room.
        """
        self.check_cleaned()
        with self._lock:
            return self._command_system
