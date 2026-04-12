from typing import Dict, Optional

from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.aether.nexus.rift.rift_space.command_system.command_system import (
    CommandSystem,
)
from melder.aether.nexus.rift.rift_space.command_system.static_command_system import (
    StaticCommandSystem,
)
from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.utilities.interfaces.interfaces import IStaticRiftSpace, IRiftEventConfiguration


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
        - Wraps attached viewers into `StaticFrameViewer`.
        - Uses the static command posture:
          - live-only spell retrieval
          - no topology mutation
          - no direct create-path spell activation
          - `meld_existing_spell(...)` remains allowed
        - Workstation defaults weak when binds omit `weak_ref`.
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

        Initialize a static room.

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
            fixing the room kind to `static` and composing the static command
            surface.
        """
        super().__init__(
            owner_rift_id,
            space_name=space_name,
            space_kind="static",
            metadata=metadata,
            event_configuration=event_configuration,
            space_id=space_id,
        )

    def _create_command_system(self) -> CommandSystem:
        """
        Build the static room's command system.

        Returns:
            CommandSystem: Static-room command surface.
        """
        return StaticCommandSystem(
            space=self,
            workstation=self._workstation,
        )

    def attach_frame_viewer(self, frame_viewer: FrameViewer) -> None:
        """
        Attach the static viewer variant for this room.

        Args:
            frame_viewer:
                Viewer to attach to this space.

        Returns:
            None.
        """
        if isinstance(frame_viewer, StaticFrameViewer):
            static_frame_viewer = frame_viewer
        else:
            static_frame_viewer = StaticFrameViewer.from_frame_viewer(frame_viewer)
        super().attach_frame_viewer(static_frame_viewer)
