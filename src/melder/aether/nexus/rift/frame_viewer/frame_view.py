"""
Internal FrameView placeholder.

Purpose:
    Represent one filtered/frame-scoped view over `FrameLink` objects.

Responsibilities:
    - Hold references to the links visible for one frame/perspective.
    - Carry light view metadata while avoiding raw runtime-object ownership.

Endgame:
    `FrameView` should eventually represent the diff/filter layer between
    Nexus-owned frame-surface truth and the final `FrameViewer` experience.
"""

from typing import Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameView(Cleanable):
    """
    Internal

    Placeholder frame-scoped view object.

    Purpose:
        Hold references to visible `FrameLink` objects for one frame or one
        applied perspective over a frame.

    Contract:
        - Holds references to links only, not raw runtime objects.
        - Cleanup is idempotent and clears owned references.

    Lifecycle:
        Placeholder only. Future ownership is expected to sit close to the
        consuming `FrameViewer`.

    TODO(HLD):
        This object is intended to become the filtered/diff layer over Nexus
        truth:

        - A `FrameView` should own references to the visible `FrameLink`
          objects for one frame or one applied perspective over a frame.
        - It should not duplicate the full canonical store if that can be
          avoided; it should hold the representational result the viewer needs.
        - It should be the place where the "what can be seen right now from
          this perspective?" diff lives.
        - One `FrameViewer` may later consume multiple `FrameView` objects at
          once to build multiple interactive areas across contracts that span
          more than one frame.
        - This object should not own:
            * raw runtime object access
            * ACL evaluation logic
            * viewer query strategies
            * orchestration state
        - This object should stay simple enough that high-churn lower updates
          can refresh it without turning it into a second full repository.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_view_id",
        "_frame_name",
        "_links_by_id",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            links_by_id: Optional[Dict[str, FrameLink]] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Internal

        Initialize one placeholder frame view.

        Args:
            frame_name:
                Frame name this view is scoped to.
            links_by_id:
                Optional map of visible links keyed by link id.
            metadata:
                Optional free-form view metadata.

        Returns:
            None.
        """
        super().__init__()
        self._view_id: str = IDBuilder.create_id()
        self._frame_name: str = frame_name
        self._links_by_id: Dict[str, FrameLink] = dict(links_by_id) if links_by_id else {}
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    @property
    def view_id(self) -> str:
        """Return the canonical view id."""
        self.check_cleaned()
        return self._view_id

    @property
    def frame_name(self) -> str:
        """Return the frame name this view is scoped to."""
        self.check_cleaned()
        return self._frame_name

    @property
    def links_by_id(self) -> Dict[str, FrameLink]:
        """Return the currently visible links by id."""
        self.check_cleaned()
        return self._links_by_id

    @property
    def metadata(self) -> Dict[str, object]:
        """Return the view metadata map."""
        self.check_cleaned()
        return self._metadata

    def cleanup(self) -> None:
        """
        Internal

        Idempotently clear view-owned state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._links_by_id.clear()
        self._links_by_id = None
        self._metadata.clear()
        self._metadata = None
        self._frame_name = None
        self._view_id = None
