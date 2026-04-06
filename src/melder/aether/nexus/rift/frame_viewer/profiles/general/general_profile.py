from typing import Dict

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile import (
    FrameViewerProfile,
)
from melder.aether.nexus.rift.frame_viewer.profiles.general.view_conduit import (
    GeneralViewConduit,
)
from melder.aether.nexus.rift.frame_viewer.profiles.general.view_frame import (
    GeneralViewFrame,
)
from melder.aether.nexus.rift.frame_viewer.profiles.general.view_spell import (
    GeneralViewSpell,
)


class GeneralFrameViewerProfile(FrameViewerProfile):
    """
    Purpose:
        Represent the standard `general` viewer profile.

    Contract:
        - Composes one `view_frame`, `view_conduit`, and `view_spell` helper
          surface.
        - Stays bound by reference to one frame's descriptor + ACL state.
        - Routes tool ids to helper-object methods through dotted handler paths.

    Lifecycle:
        Cleanup is idempotent and cascades into the helper objects before the
        inherited profile cleanup clears the binding state.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = FrameViewerProfile.__slots__ + [
        "_view_frame",
        "_view_conduit",
        "_view_spell",
    ]

    def __init__(self) -> None:
        """
        Initialize the standard `general` viewer profile template.

        Returns:
            None.
        """
        super().__init__(
            "general",
            version="0.0.1",
            required_nexus_label="default",
            required_nexus_version="0.0.1",
            tool_handler_names_by_name=self._default_tool_handler_map(),
            default_grouping="frame",
            default_detail_level="detailed",
        )
        self._view_frame: GeneralViewFrame = GeneralViewFrame(
            frame_name=None,
            frame_descriptor=None,
            frame_acl_configuration=None,
            compiled_access_surface=None,
            default_detail_level=self.default_detail_level,
        )
        self._view_conduit: GeneralViewConduit = GeneralViewConduit(
            frame_view=self._view_frame,
        )
        self._view_spell: GeneralViewSpell = GeneralViewSpell(
            frame_view=self._view_frame,
        )

    @property
    def view_frame(self) -> GeneralViewFrame:
        self.check_cleaned()
        return self._view_frame

    @property
    def view_conduit(self) -> GeneralViewConduit:
        self.check_cleaned()
        return self._view_conduit

    @property
    def view_spell(self) -> GeneralViewSpell:
        self.check_cleaned()
        return self._view_spell

    def bind_to_frame(
            self,
            *,
            frame_name: str,
            frame_descriptor: FrameDescriptor,
            frame_acl_configuration: FrameACLConfiguration,
            compiled_access_surface: CompiledFrameACLAccessSurface,
    ) -> None:
        super().bind_to_frame(
            frame_name=frame_name,
            frame_descriptor=frame_descriptor,
            frame_acl_configuration=frame_acl_configuration,
            compiled_access_surface=compiled_access_surface,
        )
        self._rebuild_helper_surfaces()

    def clone(self) -> "GeneralFrameViewerProfile":
        self.check_cleaned()
        return GeneralFrameViewerProfile()

    def cleanup(self) -> None:
        if self._cleaned:
            return
        if self._view_spell is not None:
            self._view_spell.cleanup()
            self._view_spell = None
        if self._view_conduit is not None:
            self._view_conduit.cleanup()
            self._view_conduit = None
        if self._view_frame is not None:
            self._view_frame.cleanup()
            self._view_frame = None
        super().cleanup()

    def _rebuild_helper_surfaces(self) -> None:
        if self._view_spell is not None:
            self._view_spell.cleanup()
        if self._view_conduit is not None:
            self._view_conduit.cleanup()
        if self._view_frame is not None:
            self._view_frame.cleanup()
        self._view_frame = GeneralViewFrame(
            frame_name=self.bound_frame_name,
            frame_descriptor=self.frame_descriptor,
            frame_acl_configuration=self.frame_acl_configuration,
            compiled_access_surface=self.compiled_access_surface,
            default_detail_level=self.default_detail_level,
        )
        self._view_conduit = GeneralViewConduit(frame_view=self._view_frame)
        self._view_spell = GeneralViewSpell(frame_view=self._view_frame)

    @staticmethod
    def _default_tool_handler_map() -> Dict[str, str]:
        return {
            "list_frames": "view_frame.list_frames",
            "describe_views": "view_frame.describe_views",
            "describe_frame": "view_frame.describe_frame",
            "describe_frames": "view_frame.describe_frames",
            "list_targets": "view_frame.list_targets",
            "describe_targets": "view_frame.describe_targets",
            "list_conduits": "view_conduit.list_conduits",
            "describe_conduits": "view_conduit.describe_conduits",
            "get_conduit": "view_conduit.get_required_conduit",
            "list_spells": "view_spell.list_spells",
            "describe_spells": "view_spell.describe_spells",
            "get_spell": "view_spell.get_required_spell",
        }


def create_general_profile() -> GeneralFrameViewerProfile:
    """
    Build the standard `general` viewer profile.

    Returns:
        GeneralFrameViewerProfile: Standard general viewer profile.
    """
    return GeneralFrameViewerProfile()
