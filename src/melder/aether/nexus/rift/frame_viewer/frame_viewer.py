"""
Internal FrameViewer placeholder.

Purpose:
    Represent the final consumer/query surface for one or more `FrameView`
    objects.

Responsibilities:
    - Hold one or more views.
    - Provide placeholder query/read helpers over those views.
    - Stay separate from direct runtime-object acquisition and execution.

Endgame:
    `FrameViewer` should eventually own the query strategies and interaction
    methods the agent uses to understand the frame surface while real object
    acquisition still happens through `Rift` / conduit binding paths.
"""

from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.rift.frame_viewer.frame_view import FrameView
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameViewer(Cleanable):
    """
    Internal

    Placeholder final consumer for frame-surface views.

    Purpose:
        Hold one or more `FrameView` objects and expose the first narrow set of
        query/read helpers while the full HLD continues to settle.

    Contract:
        - Owns views and viewer-local metadata only.
        - Does not expose raw runtime objects.
        - Does not own binding or direct execution behavior.

    Lifecycle:
        Placeholder only. Future ownership is expected to sit inside the
        `Rift`-side workspace/query layer.

    TODO(HLD):
        This is intended to be the final query/read experience for the agent:

        - `FrameViewer` should own the methods and strategies that let the
          agent search, filter, inspect, and explain the contents of one or
          more `FrameView` objects.
        - It should be able to consume multiple frame views at once and build
          multiple interactive areas from them.
        - It should not own:
            * canonical Nexus truth
            * ACL evaluation logic
            * raw object acquisition
            * direct code execution or binding
        - The viewer is for understanding and selection only.
          After selection, real object acquisition still belongs to the
          Rift/conduit bind path, and first-class work happens in workspace.
        - This object is therefore the final output consumer for frame-surface
          data, not the owner of the underlying runtime objects.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_viewer_id",
        "_views_by_frame_name",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            views_by_frame_name: Optional[Dict[str, FrameView]] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Internal

        Initialize one placeholder frame viewer.

        Args:
            views_by_frame_name:
                Optional frame-name -> FrameView map.
            metadata:
                Optional viewer-local metadata.

        Returns:
            None.
        """
        super().__init__()
        self._viewer_id: str = IDBuilder.create_id()
        self._views_by_frame_name: Dict[str, FrameView] = (
            dict(views_by_frame_name) if views_by_frame_name else {}
        )
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    @property
    def viewer_id(self) -> str:
        """Return the canonical viewer id."""
        self.check_cleaned()
        return self._viewer_id

    @property
    def views_by_frame_name(self) -> Dict[str, FrameView]:
        """Return the currently attached views."""
        self.check_cleaned()
        return self._views_by_frame_name

    @property
    def metadata(self) -> Dict[str, object]:
        """Return the viewer metadata map."""
        self.check_cleaned()
        return self._metadata

    def add_view(self, frame_view: FrameView) -> None:
        """
        Internal

        Register one frame view on this viewer.

        Args:
            frame_view:
                View to register.

        Returns:
            None.
        """
        self.check_cleaned()
        self._views_by_frame_name[frame_view.frame_name] = frame_view

    def get_view(self, frame_name: str) -> FrameView:
        """
        Internal

        Return one registered frame view by frame name.

        Args:
            frame_name:
                Frame name to resolve.

        Returns:
            FrameView: Registered view.
        """
        self.check_cleaned()
        try:
            return self._views_by_frame_name[frame_name]
        except KeyError as exc:
            raise ValueError("FrameView '{0}' was not found.".format(frame_name)) from exc

    def list_frame_names(self) -> List[str]:
        """
        Internal

        Return the attached frame names.

        Returns:
            List[str]: Snapshot of frame names.
        """
        self.check_cleaned()
        return list(self._views_by_frame_name.keys())

    def cleanup(self) -> None:
        """
        Internal

        Idempotently clear viewer-owned state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._views_by_frame_name.clear()
        self._views_by_frame_name = None
        self._metadata.clear()
        self._metadata = None
        self._viewer_id = None
