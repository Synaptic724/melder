from typing import Dict, Optional

from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)
from melder.aether.nexus.rift.command_system.static_command_system import (
    StaticCommandSystem,
)
from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.utilities.interfaces.interfaces import IStaticRiftSpace, IRiftGate


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
            rift_gate: Optional[IRiftGate] = None,
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
            space_name=space_name,
            space_kind="static",
            metadata=metadata,
            rift_gate=rift_gate,
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

    def _build_frame_viewer(
            self,
            *,
            viewer_profile_name: str = "general",
            selected_profile_names_by_frame_name: Optional[Dict[str, str]] = None,
            default_view_frame_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> FrameViewer:
        """
        Build the room viewer using the static viewer wrapper.

        Purpose:
            Ensure static rooms always assemble and return a
            `StaticFrameViewer` while the generic builder remains in the base
            room.

        Contract:
            - Builds the generic viewer through the base room builder.
            - Wraps that generic viewer through
              `StaticFrameViewer.from_frame_viewer(...)`.
            - Cleans the intermediate generic viewer before returning the
              static overlay.

        Returns:
            FrameViewer: Static viewer for this room.
        """
        frame_viewer = super()._build_frame_viewer(
            viewer_profile_name=viewer_profile_name,
            selected_profile_names_by_frame_name=selected_profile_names_by_frame_name,
            default_view_frame_name=default_view_frame_name,
            metadata=metadata,
        )
        static_frame_viewer = StaticFrameViewer.from_frame_viewer(frame_viewer)
        frame_viewer.cleanup()
        return static_frame_viewer
