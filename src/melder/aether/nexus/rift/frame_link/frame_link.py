"""
Internal FrameLink placeholder.

Purpose:
    Represent one view-safe frame target entry.
"""

import threading
from typing import Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import IFrameLink


class FrameLink(Cleanable, IFrameLink):
    """
    Internal

    Purpose:
        Hold the minimum stable identity for one frame-scoped available target.

    Contract:
        - Does not expose raw frame/runtime objects.
        - Holds only stable ids/names plus derived metadata.
        - Cleanup is idempotent and clears owned references.

    Lifecycle:
        Built by `FrameViewer` as part of the available-target surface for one
        assigned frame.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_link_id",
        "_lock",
        "_frame_name",
        "_source_kind",
        "_source_id",
        "_display_name",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            source_kind: str,
            source_id: str,
            display_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one view-safe frame target entry.

        Args:
            frame_name:
                Owning frame name.
            source_kind:
                Kind name for the target object (`frame`, `conduit`, `spell`).
            source_id:
                Stable source identifier.
            display_name:
                Optional viewer-facing display name.
            metadata:
                Optional free-form metadata.

        Returns:
            None.

        Contract:
            - Copies incoming metadata into a link-owned mutable dict.
            - Derives `display_name` from `source_id` when callers do not
              supply one.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not source_kind:
            raise ValueError("source_kind cannot be empty.")
        if not source_id:
            raise ValueError("source_id cannot be empty.")
        self._link_id: str = "{0}:{1}:{2}".format(
            frame_name,
            source_kind,
            source_id,
        )
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._source_kind: str = source_kind
        self._source_id: str = source_id
        self._display_name: str = display_name or source_id
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Idempotently clear link-owned state.

        Contract:
            - Clears owned metadata and identity references.
            - Leaves the link unusable after cleanup.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frame_name = None
            self._source_kind = None
            self._source_id = None
            self._display_name = None
            self._metadata.clear()
            self._metadata = None
            self._link_id = None
        self._lock = None

    @classmethod
    def from_view_subject(
            cls,
            *,
            frame_name: str,
            source_kind: str,
            source_id: str,
            display_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> "FrameLink":
        """
        Build one `FrameLink` from one view-safe subject identity.

        Args:
            frame_name:
                Owning frame name.
            source_kind:
                Kind label such as `frame`, `conduit`, or `spell`.
            source_id:
                Stable source identifier for the target.
            display_name:
                Optional viewer-facing display name.
            metadata:
                Optional derived view metadata.

        Returns:
            FrameLink: New view-safe frame target entry.
        """
        return cls(
            frame_name=frame_name,
            source_kind=source_kind,
            source_id=source_id,
            display_name=display_name,
            metadata=metadata,
        )

    @property
    def link_id(self) -> str:
        """Return the canonical target-entry id for this view-safe link."""
        self.check_cleaned()
        return self._link_id

    @property
    def frame_name(self) -> str:
        """Return the owning frame name for this target entry."""
        self.check_cleaned()
        return self._frame_name

    @property
    def source_kind(self) -> str:
        """Return the source kind label for this target entry."""
        self.check_cleaned()
        return self._source_kind

    @property
    def source_id(self) -> str:
        """Return the stable source identifier for this target entry."""
        self.check_cleaned()
        return self._source_id

    @property
    def display_name(self) -> str:
        """Return the viewer-facing display name for this target entry."""
        self.check_cleaned()
        return self._display_name

    @property
    def metadata(self) -> Dict[str, object]:
        """Return a detached copy of the target metadata map."""
        self.check_cleaned()
        return dict(self._metadata)

    def clone(self) -> "FrameLink":
        """
        Return a detached copy of this target entry.

        Returns:
            FrameLink: Detached target-entry copy.
        """
        self.check_cleaned()
        return FrameLink(
            frame_name=self._frame_name,
            source_kind=self._source_kind,
            source_id=self._source_id,
            display_name=self._display_name,
            metadata=dict(self._metadata),
        )
