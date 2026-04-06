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

import threading
from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.aether.nexus.rift.frame_viewer.frame_view import FrameView
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile import (
    FrameViewerProfile,
)
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
        "_lock",
        "_profile_name",
        "_profile_version",
        "_views_by_frame_name",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            profile_name: Optional[str] = None,
            profile_version: Optional[str] = None,
            views_by_frame_name: Optional[Dict[str, FrameView]] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Internal

        Initialize one placeholder frame viewer.

        Args:
            views_by_frame_name:
                Optional frame-name -> FrameView map.
            profile_name:
                Optional viewer profile name applied to this projection.
            profile_version:
                Optional viewer profile version applied to this projection.
            metadata:
                Optional viewer-local metadata.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._viewer_id: str = IDBuilder.create_id()
        self._profile_name: Optional[str] = profile_name
        self._profile_version: Optional[str] = profile_version
        self._views_by_frame_name: Dict[str, FrameView] = (
            dict(views_by_frame_name) if views_by_frame_name else {}
        )
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Internal

        Idempotently clear viewer-owned state.

        Threading:
            Uses the instance lock because cleanup cascades through grouped
            view and metadata state in a nogil runtime.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for frame_view in self._views_by_frame_name.values():
                frame_view.cleanup()
            self._views_by_frame_name.clear()
            self._views_by_frame_name = None
            self._metadata.clear()
            self._metadata = None
            self._profile_name = None
            self._profile_version = None
            self._viewer_id = None
        self._lock = None

    @property
    def viewer_id(self) -> str:
        """Return the canonical viewer id."""
        self.check_cleaned()
        return self._viewer_id

    @property
    def views_by_frame_name(self) -> Dict[str, FrameView]:
        """Return the currently attached views."""
        self.check_cleaned()
        with self._lock:
            return dict(self._views_by_frame_name)

    @property
    def profile_name(self) -> Optional[str]:
        """Return the optional applied viewer profile name."""
        self.check_cleaned()
        return self._profile_name

    @property
    def profile_version(self) -> Optional[str]:
        """Return the optional applied viewer profile version."""
        self.check_cleaned()
        return self._profile_version

    @property
    def metadata(self) -> Dict[str, object]:
        """Return the viewer metadata map."""
        self.check_cleaned()
        with self._lock:
            return dict(self._metadata)

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
        if not isinstance(frame_view, FrameView):
            raise TypeError("frame_view must be a FrameView.")
        with self._lock:
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
        with self._lock:
            try:
                return self._views_by_frame_name[frame_name]
            except KeyError as exc:
                raise ValueError(
                    "FrameView '{0}' was not found.".format(frame_name)
                ) from exc

    def list_frame_names(self) -> List[str]:
        """
        Internal

        Return the attached frame names.

        Returns:
            List[str]: Snapshot of frame names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._views_by_frame_name.keys())

    def list_links(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Internal

        Return visible links from one view or from every attached view.

        Args:
            frame_name:
                Optional single-frame scope. When omitted, links from every
                attached view are returned.

        Returns:
            List[FrameLink]: Visible links in deterministic frame/link order.
        """
        self.check_cleaned()
        with self._lock:
            if frame_name is not None:
                return list(self.get_view(frame_name).links_by_id.values())
            ordered_links: List[FrameLink] = []
            for current_frame_name in sorted(self._views_by_frame_name.keys()):
                frame_view = self._views_by_frame_name[current_frame_name]
                for link_id in sorted(frame_view.links_by_id.keys()):
                    ordered_links.append(frame_view.links_by_id[link_id])
            return ordered_links

    def list_links_by_kind(
            self,
            source_kind: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Internal

        Return visible links filtered by source kind.

        Args:
            source_kind:
                Source kind to keep.
            frame_name:
                Optional single-frame scope. When omitted, every attached view
                is considered.

        Returns:
            List[FrameLink]: Visible links with the requested source kind.
        """
        self.check_cleaned()
        if not source_kind:
            raise ValueError("source_kind cannot be empty.")
        return [
            link
            for link in self.list_links(frame_name=frame_name)
            if link.source_kind == source_kind
        ]

    def list_links_grouped_by_frame(self) -> Dict[str, List[FrameLink]]:
        """
        Internal

        Return visible links grouped by frame name.

        Returns:
            Dict[str, List[FrameLink]]: Deterministic frame-name keyed link map.
        """
        self.check_cleaned()
        with self._lock:
            return {
                frame_name: list(self.list_links(frame_name=frame_name))
                for frame_name in sorted(self._views_by_frame_name.keys())
            }

    def list_links_grouped_by_kind(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, List[FrameLink]]:
        """
        Internal

        Return visible links grouped by source kind.

        Args:
            frame_name:
                Optional single-frame scope. When omitted, every attached view
                is considered.

        Returns:
            Dict[str, List[FrameLink]]: Deterministic source-kind keyed link map.
        """
        self.check_cleaned()
        grouped_links: Dict[str, List[FrameLink]] = {}
        for frame_link in self.list_links(frame_name=frame_name):
            grouped_links.setdefault(frame_link.source_kind, []).append(frame_link)
        return {
            source_kind: grouped_links[source_kind]
            for source_kind in sorted(grouped_links.keys())
        }

    def list_display_names(
            self,
            *,
            frame_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[str]:
        """
        Internal

        Return visible display names from the current projected links.

        Args:
            frame_name:
                Optional single-frame scope.
            source_kind:
                Optional source-kind filter.

        Returns:
            List[str]: Deterministic visible display names.
        """
        self.check_cleaned()
        if source_kind is None:
            return [frame_link.display_name for frame_link in self.list_links(
                frame_name=frame_name
            )]
        return [
            frame_link.display_name
            for frame_link in self.list_links_by_kind(
                source_kind,
                frame_name=frame_name,
            )
        ]

    def count_links(
            self,
            *,
            frame_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> int:
        """
        Internal

        Return the number of visible links under the requested scope.

        Args:
            frame_name:
                Optional single-frame scope.
            source_kind:
                Optional source-kind filter.

        Returns:
            int: Visible link count.
        """
        self.check_cleaned()
        if source_kind is None:
            return len(self.list_links(frame_name=frame_name))
        return len(
            self.list_links_by_kind(
                source_kind,
                frame_name=frame_name,
            )
        )

    def describe_frame(self, frame_name: str) -> Dict[str, object]:
        """
        Internal

        Return one deterministic summary of the projected view for a frame.

        Args:
            frame_name:
                Frame name to summarize.

        Returns:
            Dict[str, object]: Summary of the projected frame view.
        """
        self.check_cleaned()
        frame_view = self.get_view(frame_name)
        grouped_links = self.list_links_grouped_by_kind(frame_name=frame_name)
        return {
            "frame_name": frame_name,
            "link_count": len(frame_view.links_by_id),
            "available_kinds": tuple(sorted(grouped_links.keys())),
            "link_counts_by_kind": {
                source_kind: len(grouped_links[source_kind])
                for source_kind in grouped_links.keys()
            },
            "metadata": frame_view.metadata,
        }

    def describe_frames(self) -> Dict[str, Dict[str, object]]:
        """
        Internal

        Return deterministic summaries for every attached frame view.

        Returns:
            Dict[str, Dict[str, object]]: Frame-name keyed summary map.
        """
        self.check_cleaned()
        return {
            frame_name: self.describe_frame(frame_name)
            for frame_name in sorted(self.list_frame_names())
        }

    def get_required_link_by_source(
            self,
            *,
            frame_name: str,
            source_kind: str,
            source_id: str,
    ) -> FrameLink:
        """
        Internal

        Return one visible link by frame, kind, and source id or raise.

        Args:
            frame_name:
                Owning frame name.
            source_kind:
                Source kind to resolve.
            source_id:
                Stable source identifier to resolve.

        Returns:
            FrameLink: Matching visible link.
        """
        self.check_cleaned()
        if not source_kind:
            raise ValueError("source_kind cannot be empty.")
        if not source_id:
            raise ValueError("source_id cannot be empty.")
        for frame_link in self.list_links(frame_name=frame_name):
            if (
                    frame_link.source_kind == source_kind
                    and frame_link.source_id == source_id
            ):
                return frame_link
        raise ValueError(
            "FrameLink '{0}:{1}' was not found in frame '{2}'.".format(
                source_kind,
                source_id,
                frame_name,
            )
        )

    def clone(self) -> "FrameViewer":
        """
        Internal

        Return a detached copy of the viewer and its projected views.

        Purpose:
            Support safe cached viewer returns where Nexus keeps one canonical
            projected viewer but callers receive cleanup-safe copies.

        Returns:
            FrameViewer: Detached viewer copy.
        """
        self.check_cleaned()
        with self._lock:
            return FrameViewer(
                views_by_frame_name={
                    frame_name: frame_view.clone()
                    for frame_name, frame_view in self._views_by_frame_name.items()
                },
                profile_name=self._profile_name,
                profile_version=self._profile_version,
                metadata=dict(self._metadata),
            )
