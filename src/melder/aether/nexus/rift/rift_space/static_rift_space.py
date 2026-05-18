from typing import Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)
from melder.aether.nexus.rift.command_system.static_command_system import (
    StaticCommandSystem,
)
from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.utilities.interfaces import IStaticRiftSpace, IRiftGate


class StaticRiftSpace(RiftSpace, IStaticRiftSpace):
    """
    Internal

    Purpose:
        Represent the lower-risk concrete room type.

    Contract:
        - Inherits all base room behavior.
        - Fixes `space_kind` to `static`.
        - Represents the lower-risk room surface where declared targets and a
          more stable local structure are the primary operational model.
        - Owns one durable `StaticFrameViewer` asset.
        - Uses the static command posture:
          - live-only spell retrieval
          - no topology mutation
          - no direct create-path spell activation
          - `meld_existing_spell(...)` remains allowed
        - Workstation defaults weak when binds omit `weak_ref`.
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

        Initialize a static room.

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
            fixing the room kind to `static` and composing the static command
            surface.
        """
        super().__init__(
            owner_rift_id,
            rift=rift,
            space_name=space_name,
            space_kind="static",
            metadata=metadata,
            rift_gate=rift_gate,
            space_id=space_id,
        )

    def _create_command_system(self, rift: object) -> CommandSystem:
        """
        Build the static room's command system.

        Returns:
            CommandSystem: Static-room command surface.
        """
        return StaticCommandSystem(
            rift=rift,
            space=self,
            workstation=self._workstation,
        )

    @property
    def command_system(self) -> StaticCommandSystem:
        """
        Return the room-local static command system.

        Returns:
            StaticCommandSystem: Static-room command surface owned by this
            room.
        """
        self.check_cleaned()
        with self._lock:
            return self._command_system

