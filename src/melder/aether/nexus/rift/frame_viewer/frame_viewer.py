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
from typing import Any, Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.aether.nexus.rift.frame_viewer.frame_view import FrameView
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile import (
    FrameViewerProfile,
)
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile_builder import (
    FrameViewerProfileBuilder,
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
        "_profile_builder",
        "_active_profiles_by_name",
        "_available_views_by_frame_name",
        "_default_view_frame_name",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            profile_builder: Optional[FrameViewerProfileBuilder] = None,
            active_profiles_by_name: Optional[Dict[str, FrameViewerProfile]] = None,
            available_views_by_frame_name: Optional[Dict[str, FrameView]] = None,
            default_view_frame_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Internal

        Initialize one placeholder frame viewer.

        Args:
            profile_builder:
                Optional local viewer-profile builder/registry.
            active_profiles_by_name:
                Optional active local viewer profiles.
            available_views_by_frame_name:
                Optional assigned/available frame views.
            default_view_frame_name:
                Optional default assigned view frame name.
            metadata:
                Optional viewer-local metadata.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._viewer_id: str = IDBuilder.create_id()
        if profile_builder is not None and not isinstance(
                profile_builder,
                FrameViewerProfileBuilder,
        ):
            raise TypeError("profile_builder must be a FrameViewerProfileBuilder.")
        self._profile_builder: FrameViewerProfileBuilder = (
            profile_builder if profile_builder is not None else FrameViewerProfileBuilder()
        )
        self._available_views_by_frame_name: Dict[str, FrameView] = (
            dict(available_views_by_frame_name) if available_views_by_frame_name else {}
        )
        if default_view_frame_name is not None:
            if not default_view_frame_name:
                raise ValueError("default_view_frame_name cannot be empty.")
            if default_view_frame_name not in self._available_views_by_frame_name:
                raise ValueError(
                    "default_view_frame_name must be present in available_views_by_frame_name."
                )
        self._default_view_frame_name: Optional[str] = (
            default_view_frame_name
            if default_view_frame_name is not None
            else (
                next(iter(self._available_views_by_frame_name.keys()))
                if len(self._available_views_by_frame_name) > 0
                else None
            )
        )
        if active_profiles_by_name is not None:
            self._active_profiles_by_name: Dict[str, FrameViewerProfile] = dict(
                active_profiles_by_name
            )
        else:
            default_profile = self._profile_builder.get_required_profile("general").clone()
            self._active_profiles_by_name = {default_profile.name: default_profile}
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
            for frame_view in self._available_views_by_frame_name.values():
                frame_view.cleanup()
            for frame_viewer_profile in self._active_profiles_by_name.values():
                frame_viewer_profile.cleanup()
            self._profile_builder.cleanup()
            self._available_views_by_frame_name.clear()
            self._available_views_by_frame_name = None
            self._default_view_frame_name = None
            self._active_profiles_by_name.clear()
            self._active_profiles_by_name = None
            self._profile_builder = None
            self._metadata.clear()
            self._metadata = None
            self._viewer_id = None
        self._lock = None

    @property
    def viewer_id(self) -> str:
        """Return the canonical viewer id."""
        self.check_cleaned()
        return self._viewer_id

    @property
    def available_views_by_frame_name(self) -> Dict[str, FrameView]:
        """
        Return the currently assigned/available views by frame name.

        Returns:
            Dict[str, FrameView]: Assigned available views.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._available_views_by_frame_name)

    @property
    def default_view_frame_name(self) -> Optional[str]:
        """
        Return the default assigned view frame name when one exists.

        Returns:
            Optional[str]: Default assigned view frame name.
        """
        self.check_cleaned()
        return self._default_view_frame_name

    @property
    def profile_name(self) -> Optional[str]:
        """Return the default active viewer profile name."""
        self.check_cleaned()
        if len(self._active_profiles_by_name) == 0:
            return None
        return sorted(self._active_profiles_by_name.keys())[0]

    @property
    def profile_version(self) -> Optional[str]:
        """Return the default active viewer profile version."""
        self.check_cleaned()
        if len(self._active_profiles_by_name) == 0:
            return None
        return self._active_profiles_by_name[self.profile_name].version

    @property
    def enabled_helpers(self) -> tuple[str, ...]:
        """Return the enabled helper ids exposed by the default active profile."""
        self.check_cleaned()
        if len(self._active_profiles_by_name) == 0:
            return tuple()
        return self._active_profiles_by_name[self.profile_name].enabled_helpers

    @property
    def default_grouping(self) -> Optional[str]:
        """Return the default grouping mode from the default active profile."""
        self.check_cleaned()
        if len(self._active_profiles_by_name) == 0:
            return None
        return self._active_profiles_by_name[self.profile_name].default_grouping

    @property
    def default_detail_level(self) -> Optional[str]:
        """Return the default detail posture from the default active profile."""
        self.check_cleaned()
        if len(self._active_profiles_by_name) == 0:
            return None
        return self._active_profiles_by_name[self.profile_name].default_detail_level

    @property
    def profile(self) -> Optional[FrameViewerProfile]:
        """
        Return the hosted viewer profile clone when present.

        Returns:
            Optional[FrameViewerProfile]: Hosted selected viewer profile.
        """
        self.check_cleaned()
        if len(self._active_profiles_by_name) == 0:
            return None
        return self._active_profiles_by_name[self.profile_name]

    @property
    def active_profiles_by_name(self) -> Dict[str, FrameViewerProfile]:
        """
        Return the currently active local viewer profiles by name.

        Returns:
            Dict[str, FrameViewerProfile]: Active hosted viewer profiles.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._active_profiles_by_name)

    @property
    def metadata(self) -> Dict[str, object]:
        """Return the viewer metadata map."""
        self.check_cleaned()
        with self._lock:
            return dict(self._metadata)

    def add_available_view(self, frame_view: FrameView) -> None:
        """
        Register one assigned/available frame view on this viewer.

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
            self._available_views_by_frame_name[frame_view.frame_name] = frame_view
            if self._default_view_frame_name is None:
                self._default_view_frame_name = frame_view.frame_name

    def get_available_view(self, frame_name: str) -> FrameView:
        """
        Return one assigned/available frame view by frame name.

        Args:
            frame_name:
                Frame name to resolve.

        Returns:
            FrameView: Registered view.
        """
        self.check_cleaned()
        with self._lock:
            try:
                return self._available_views_by_frame_name[frame_name]
            except KeyError as exc:
                raise ValueError(
                    "FrameView '{0}' was not found.".format(frame_name)
                ) from exc

    def get_default_view(self) -> FrameView:
        """
        Return the default assigned view.

        Returns:
            FrameView: Default assigned view.
        """
        self.check_cleaned()
        if self._default_view_frame_name is None:
            raise ValueError("FrameViewer has no default assigned view.")
        return self.get_available_view(self._default_view_frame_name)

    def set_default_view(self, frame_name: str) -> None:
        """
        Set the default assigned view by frame name.

        Args:
            frame_name:
                Assigned frame name to make default.

        Returns:
            None.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        with self._lock:
            if frame_name not in self._available_views_by_frame_name:
                raise ValueError(
                    "FrameViewer view '{0}' was not found.".format(frame_name)
                )
            self._default_view_frame_name = frame_name

    def describe_available_views(self) -> List[Dict[str, object]]:
        """
        Return summaries for the currently assigned views.

        Returns:
            List[Dict[str, object]]: Assigned view summaries.
        """
        self.check_cleaned()
        described_views: List[Dict[str, object]] = []
        for frame_name in self.list_frame_names():
            frame_view = self.get_available_view(frame_name)
            described_views.append(
                {
                    "frame_name": frame_name,
                    "is_default": frame_name == self._default_view_frame_name,
                    "available_target_count": len(frame_view.available_targets_by_id),
                    "available_kinds": tuple(
                        sorted(frame_view.available_target_ids_by_kind.keys())
                    ),
                    "default_profile_name": frame_view.default_profile_name,
                    "active_profile_names": frame_view.list_active_profile_names(),
                }
            )
        return described_views

    def list_frame_names(self) -> List[str]:
        """
        Internal

        Return the attached frame names.

        Returns:
            List[str]: Snapshot of frame names.
        """
        self.check_cleaned()
        self._require_helper_enabled("list_frame_names")
        with self._lock:
            return list(self._available_views_by_frame_name.keys())

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
        self._require_helper_enabled("list_links")
        with self._lock:
            if frame_name is not None:
                return list(self.get_available_view(frame_name).links_by_id.values())
            ordered_links: List[FrameLink] = []
            for current_frame_name in sorted(self._available_views_by_frame_name.keys()):
                frame_view = self._available_views_by_frame_name[current_frame_name]
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
        self._require_helper_enabled("list_links_by_kind")
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
        self._require_helper_enabled("list_links_grouped_by_frame")
        with self._lock:
            return {
                frame_name: list(self.list_links(frame_name=frame_name))
                for frame_name in sorted(self._available_views_by_frame_name.keys())
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
        self._require_helper_enabled("list_links_grouped_by_kind")
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
        self._require_helper_enabled("list_display_names")
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
        self._require_helper_enabled("count_links")
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
        self._require_helper_enabled("describe_frame")
        frame_view = self.get_available_view(frame_name)
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
        self._require_helper_enabled("describe_frames")
        return {
            frame_name: self.describe_frame(frame_name)
            for frame_name in sorted(self.list_frame_names())
        }

    def list_available_targets(
            self,
            *,
            frame_name: Optional[str] = None,
            profile_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return available targets from one assigned view in profile order.

        Args:
            frame_name:
                Optional assigned frame name. When omitted, the default
                assigned view is used.
            profile_name:
                Optional local view profile name used for ordering.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[FrameLink]: Available targets in view-profile order.
        """
        self.check_cleaned()
        selected_view = (
            self.get_available_view(frame_name)
            if frame_name is not None
            else self.get_default_view()
        )
        return selected_view.list_available_targets_in_profile_order(
            profile_name=profile_name,
            source_kind=source_kind,
        )

    def list_view_profile_names(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return the active view-profile names for one assigned view.

        Args:
            frame_name:
                Optional assigned frame name. When omitted, the default
                assigned view is used.

        Returns:
            List[str]: Active local view-profile names.
        """
        self.check_cleaned()
        selected_view = (
            self.get_available_view(frame_name)
            if frame_name is not None
            else self.get_default_view()
        )
        return selected_view.list_active_profile_names()

    def set_default_view_profile(
            self,
            profile_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Set the default local view profile for one assigned view.

        Args:
            profile_name:
                Active local view profile name.
            frame_name:
                Optional assigned frame name. When omitted, the default
                assigned view is used.

        Returns:
            None.
        """
        self.check_cleaned()
        selected_view = (
            self.get_available_view(frame_name)
            if frame_name is not None
            else self.get_default_view()
        )
        selected_view.set_default_profile(profile_name)

    def describe_available_targets(
            self,
            *,
            frame_name: Optional[str] = None,
            profile_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """
        Return profile-shaped target descriptions from one assigned view.

        Args:
            frame_name:
                Optional assigned frame name. When omitted, the default
                assigned view is used.
            profile_name:
                Optional local view profile name used for shaping.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[Dict[str, object]]: Profile-shaped target descriptions.
        """
        self.check_cleaned()
        selected_view = (
            self.get_available_view(frame_name)
            if frame_name is not None
            else self.get_default_view()
        )
        return selected_view.describe_available_targets(
            profile_name=profile_name,
            source_kind=source_kind,
        )

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
        self._require_helper_enabled("get_required_link_by_source")
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
                profile_builder=FrameViewerProfileBuilder(),
                active_profiles_by_name={
                    profile_name: frame_viewer_profile.clone()
                    for profile_name, frame_viewer_profile in (
                        self._active_profiles_by_name.items()
                    )
                },
                available_views_by_frame_name={
                    frame_name: frame_view.clone()
                    for frame_name, frame_view in (
                        self._available_views_by_frame_name.items()
                    )
                },
                default_view_frame_name=self._default_view_frame_name,
                metadata=dict(self._metadata),
            )

    def list_enabled_helpers(self) -> tuple[str, ...]:
        """
        Internal

        Return the helper ids exposed by the selected profile.

        Returns:
            tuple[str, ...]: Enabled helper ids.
        """
        self.check_cleaned()
        return self.enabled_helpers

    def list_available_tools(self) -> tuple[str, ...]:
        """
        Return the tool ids exposed by the selected profile.

        Returns:
            tuple[str, ...]: Exposed tool ids.
        """
        self.check_cleaned()
        if len(self._active_profiles_by_name) == 0:
            return tuple()
        return self._active_profiles_by_name[self.profile_name].list_tool_names()

    def list_active_profile_names(self) -> List[str]:
        """
        Return the currently active viewer profile names.

        Returns:
            List[str]: Active viewer profile names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._active_profiles_by_name.keys())

    def register_active_profile(self, profile: FrameViewerProfile) -> None:
        """
        Register or replace one active local viewer profile.

        Args:
            profile:
                Hosted profile to activate.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(profile, FrameViewerProfile):
            raise TypeError("profile must be a FrameViewerProfile.")
        with self._lock:
            existing_profile = self._active_profiles_by_name.get(profile.name)
            if existing_profile is not None and existing_profile is not profile:
                existing_profile.cleanup()
            self._active_profiles_by_name[profile.name] = profile

    def has_enabled_helper(self, helper_name: str) -> bool:
        """
        Internal

        Return whether one helper id is exposed by the selected profile.

        Args:
            helper_name:
                Helper id to inspect.

        Returns:
            bool: True when the helper is enabled.
        """
        self.check_cleaned()
        if not helper_name:
            raise ValueError("helper_name cannot be empty.")
        if len(self._active_profiles_by_name) == 0:
            return False
        return self._active_profiles_by_name[self.profile_name].has_tool(helper_name)

    def execute_tool(
            self,
            tool_name: str,
            *,
            profile_name: Optional[str] = None,
            **kwargs,
    ) -> Any:
        """
        Execute one profile-owned tool over the hosted views.

        Args:
            tool_name:
                Tool id exposed by the selected profile.
            profile_name:
                Optional active profile name. When omitted, the default active
                profile is used.
            **kwargs:
                Keyword arguments forwarded to the host-side handler.

        Returns:
            Any: Tool result.
        """
        self.check_cleaned()
        if not tool_name:
            raise ValueError("tool_name cannot be empty.")
        if len(self._active_profiles_by_name) == 0:
            raise ValueError("FrameViewer has no active profiles.")
        selected_profile_name = profile_name or self.profile_name
        selected_profile = self.get_required_active_profile(selected_profile_name)
        handler_name = selected_profile.get_required_tool_handler_name(tool_name)
        handler = getattr(self, handler_name, None)
        if handler is None or not callable(handler):
            raise ValueError(
                "FrameViewer tool '{0}' targets missing handler '{1}'.".format(
                    tool_name,
                    handler_name,
                )
            )
        return handler(**kwargs)

    def get_required_active_profile(self, profile_name: str) -> FrameViewerProfile:
        """
        Return one active local viewer profile by name or raise.

        Args:
            profile_name:
                Active profile name to resolve.

        Returns:
            FrameViewerProfile: Matching active hosted profile.
        """
        self.check_cleaned()
        if not profile_name:
            raise ValueError("profile_name cannot be empty.")
        with self._lock:
            try:
                return self._active_profiles_by_name[profile_name]
            except KeyError as exc:
                raise ValueError(
                    "FrameViewer profile '{0}' was not found.".format(profile_name)
                ) from exc

    def _require_helper_enabled(self, helper_name: str) -> None:
        """
        Internal

        Fail fast when the selected profile does not expose one helper.

        Args:
            helper_name:
                Helper id that must be enabled.

        Returns:
            None.
        """
        if len(self._active_profiles_by_name) == 0:
            return
        default_profile = self._active_profiles_by_name[self.profile_name]
        if default_profile.has_tool(helper_name):
            return
        if helper_name in default_profile.tool_handler_names_by_name.values():
            return
        raise ValueError(
            "FrameViewer helper '{0}' is not enabled by profile '{1}'.".format(
                helper_name,
                default_profile.name,
            )
        )
