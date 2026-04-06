"""
Internal descriptor-driven FrameViewer surface.
"""

import threading
from typing import Any, Dict, List, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
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

    Purpose:
        Hold descriptor truth plus compiled ACL surfaces and expose the
        query/selection methods the agent uses.

    Contract:
        - Holds non-owned `FrameDescriptor` references keyed by frame name.
        - Owns detached `CompiledFrameACLAccessSurface` objects keyed by frame
          name.
        - Owns active `FrameViewerProfile` objects and one default active
          profile pointer.
        - Exposes only ACL-filtered frame/conduit/spell targets.
        - Does not expose raw runtime objects or code execution behavior.
    """

    __melder_internal__ = _mrg.sentinel
    _DEFAULT_KIND_ORDER: Tuple[str, ...] = ("frame", "conduit", "spell")
    __slots__ = Cleanable.__slots__ + [
        "_viewer_id",
        "_lock",
        "_profile_builder",
        "_active_profiles_by_name",
        "_default_profile_name",
        "_frame_descriptors_by_name",
        "_frame_acl_configurations_by_frame_name",
        "_compiled_access_surfaces_by_frame_name",
        "_selected_profiles_by_frame_name",
        "_default_view_frame_name",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            profile_builder: Optional[FrameViewerProfileBuilder] = None,
            active_profiles_by_name: Optional[Dict[str, FrameViewerProfile]] = None,
            default_profile_name: Optional[str] = None,
            frame_descriptors_by_name: Optional[Dict[str, FrameDescriptor]] = None,
            frame_acl_configurations_by_frame_name: Optional[
                Dict[str, FrameACLConfiguration]
            ] = None,
            compiled_access_surfaces_by_frame_name: Optional[
                Dict[str, CompiledFrameACLAccessSurface]
            ] = None,
            selected_profile_names_by_frame_name: Optional[Dict[str, str]] = None,
            default_view_frame_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one descriptor-driven frame viewer.

        Args:
            profile_builder:
                Optional local viewer-profile builder/registry.
            active_profiles_by_name:
                Optional active local viewer profiles.
            default_profile_name:
                Optional default active viewer profile name.
            frame_descriptors_by_name:
                Optional non-owned descriptor references keyed by frame name.
            frame_acl_configurations_by_frame_name:
                Optional non-owned frame ACL configurations keyed by frame name.
            compiled_access_surfaces_by_frame_name:
                Optional owned compiled ACL surfaces keyed by frame name.
            selected_profile_names_by_frame_name:
                Optional selected profile names keyed by frame name.
            default_view_frame_name:
                Optional default selected frame name.
            metadata:
                Optional viewer-local metadata.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._viewer_id: str = IDBuilder.create_id()
        if profile_builder is not None and not isinstance(
                profile_builder,
                FrameViewerProfileBuilder,
        ):
            raise TypeError("profile_builder must be a FrameViewerProfileBuilder.")
        self._profile_builder = (
            profile_builder if profile_builder is not None else FrameViewerProfileBuilder()
        )
        self._frame_descriptors_by_name: Dict[str, FrameDescriptor] = dict(
            frame_descriptors_by_name or {}
        )
        self._frame_acl_configurations_by_frame_name: Dict[
            str,
            FrameACLConfiguration,
        ] = dict(frame_acl_configurations_by_frame_name or {})
        self._compiled_access_surfaces_by_frame_name: Dict[
            str,
            CompiledFrameACLAccessSurface,
        ] = dict(compiled_access_surfaces_by_frame_name or {})
        if (
                set(self._frame_descriptors_by_name.keys())
                != set(self._compiled_access_surfaces_by_frame_name.keys())
                or set(self._frame_descriptors_by_name.keys())
                != set(self._frame_acl_configurations_by_frame_name.keys())
        ):
            raise ValueError(
                "frame descriptor, ACL configuration, and compiled access surface maps must have matching keys."
            )
        if default_view_frame_name is not None:
            if not default_view_frame_name:
                raise ValueError("default_view_frame_name cannot be empty.")
            if default_view_frame_name not in self._frame_descriptors_by_name:
                raise ValueError(
                    "default_view_frame_name must be present in frame_descriptors_by_name."
                )
        self._default_view_frame_name: Optional[str] = (
            default_view_frame_name
            if default_view_frame_name is not None
            else (
                next(iter(self._frame_descriptors_by_name.keys()))
                if len(self._frame_descriptors_by_name) > 0
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
        if default_profile_name is not None:
            if not default_profile_name:
                raise ValueError("default_profile_name cannot be empty.")
            if default_profile_name not in self._active_profiles_by_name:
                raise ValueError(
                    "default_profile_name must be present in active_profiles_by_name."
                )
        self._default_profile_name: Optional[str] = (
            default_profile_name
            if default_profile_name is not None
            else (
                next(iter(self._active_profiles_by_name.keys()))
                if len(self._active_profiles_by_name) > 0
                else None
            )
        )
        self._selected_profiles_by_frame_name: Dict[str, FrameViewerProfile] = {}
        for frame_name in self._frame_descriptors_by_name.keys():
            selected_profile_name = (
                selected_profile_names_by_frame_name.get(frame_name)
                if selected_profile_names_by_frame_name is not None
                else self._default_profile_name
            )
            if selected_profile_name is None:
                continue
            self._selected_profiles_by_frame_name[frame_name] = (
                self._create_bound_profile_for_frame(
                    frame_name,
                    selected_profile_name,
                )
            )
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Idempotently clear viewer-owned state.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for compiled_access_surface in (
                    self._compiled_access_surfaces_by_frame_name.values()
            ):
                compiled_access_surface.cleanup()
            for frame_viewer_profile in self._active_profiles_by_name.values():
                frame_viewer_profile.cleanup()
            self._profile_builder.cleanup()
            self._frame_descriptors_by_name.clear()
            self._frame_acl_configurations_by_frame_name.clear()
            self._compiled_access_surfaces_by_frame_name.clear()
            self._active_profiles_by_name.clear()
            for selected_profile in self._selected_profiles_by_frame_name.values():
                selected_profile.cleanup()
            self._selected_profiles_by_frame_name.clear()
            self._metadata.clear()
            self._profile_builder = None
            self._frame_descriptors_by_name = None
            self._frame_acl_configurations_by_frame_name = None
            self._compiled_access_surfaces_by_frame_name = None
            self._active_profiles_by_name = None
            self._selected_profiles_by_frame_name = None
            self._default_profile_name = None
            self._default_view_frame_name = None
            self._metadata = None
            self._viewer_id = None
        self._lock = None

    @property
    def viewer_id(self) -> str:
        self.check_cleaned()
        return self._viewer_id

    @property
    def frame_descriptors_by_name(self) -> Dict[str, FrameDescriptor]:
        self.check_cleaned()
        with self._lock:
            return dict(self._frame_descriptors_by_name)

    @property
    def compiled_access_surfaces_by_frame_name(
            self,
    ) -> Dict[str, CompiledFrameACLAccessSurface]:
        self.check_cleaned()
        with self._lock:
            return dict(self._compiled_access_surfaces_by_frame_name)

    @property
    def frame_acl_configurations_by_frame_name(
            self,
    ) -> Dict[str, FrameACLConfiguration]:
        """
        Return the hosted frame ACL configurations keyed by frame name.

        Returns:
            Dict[str, FrameACLConfiguration]:
                Detached snapshot of hosted frame ACL configurations.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._frame_acl_configurations_by_frame_name)

    @property
    def default_view_frame_name(self) -> Optional[str]:
        self.check_cleaned()
        return self._default_view_frame_name

    @property
    def profile_name(self) -> Optional[str]:
        self.check_cleaned()
        if self._default_view_frame_name is None:
            return self._default_profile_name
        selected_profile = self._selected_profiles_by_frame_name.get(
            self._default_view_frame_name
        )
        if selected_profile is None:
            return self._default_profile_name
        return selected_profile.name

    @property
    def profile_version(self) -> Optional[str]:
        self.check_cleaned()
        if self._default_profile_name is None:
            return None
        return self._active_profiles_by_name[self._default_profile_name].version

    @property
    def enabled_helpers(self) -> Tuple[str, ...]:
        self.check_cleaned()
        if self._default_profile_name is None:
            return tuple()
        return self._active_profiles_by_name[
            self._default_profile_name
        ].enabled_helpers

    @property
    def default_grouping(self) -> Optional[str]:
        self.check_cleaned()
        if self._default_profile_name is None:
            return None
        return self._active_profiles_by_name[
            self._default_profile_name
        ].default_grouping

    @property
    def default_detail_level(self) -> Optional[str]:
        self.check_cleaned()
        if self._default_profile_name is None:
            return None
        return self._active_profiles_by_name[
            self._default_profile_name
        ].default_detail_level

    @property
    def profile(self) -> Optional[FrameViewerProfile]:
        self.check_cleaned()
        if self._default_view_frame_name is not None:
            return self._selected_profiles_by_frame_name.get(
                self._default_view_frame_name
            )
        if self._default_profile_name is None:
            return None
        return self._active_profiles_by_name[self._default_profile_name]

    @property
    def active_profiles_by_name(self) -> Dict[str, FrameViewerProfile]:
        self.check_cleaned()
        with self._lock:
            return dict(self._active_profiles_by_name)

    @property
    def selected_profile_names_by_frame_name(self) -> Dict[str, str]:
        """
        Return the selected viewer-profile names keyed by frame name.

        Returns:
            Dict[str, str]: Selected viewer-profile names by frame.
        """
        self.check_cleaned()
        with self._lock:
            return {
                frame_name: profile.name
                for frame_name, profile in self._selected_profiles_by_frame_name.items()
            }

    @property
    def metadata(self) -> Dict[str, object]:
        self.check_cleaned()
        with self._lock:
            return dict(self._metadata)

    def list_frame_names(self) -> List[str]:
        self.check_cleaned()
        with self._lock:
            return list(sorted(self._frame_descriptors_by_name.keys()))

    def set_default_view(self, frame_name: str) -> None:
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        with self._lock:
            if frame_name not in self._frame_descriptors_by_name:
                raise ValueError("Frame '{0}' was not found.".format(frame_name))
            self._default_view_frame_name = frame_name

    def describe_available_views(self) -> List[Dict[str, object]]:
        self.check_cleaned()
        described_frames: List[Dict[str, object]] = []
        for frame_name in self.list_frame_names():
            compiled_access_surface = self._get_required_compiled_access_surface(
                frame_name
            )
            described_frames.append(
                {
                    "frame_name": frame_name,
                    "is_default": frame_name == self._default_view_frame_name,
                    "available_target_count": len(self._build_links_for_frame(frame_name)),
                    "available_kinds": tuple(
                        sorted(compiled_access_surface.allowed_kinds)
                    ),
                }
            )
        return described_frames

    def list_links(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        self.check_cleaned()
        if frame_name is not None:
            return self._build_links_for_frame(frame_name)
        ordered_links: List[FrameLink] = []
        for current_frame_name in self.list_frame_names():
            ordered_links.extend(self._build_links_for_frame(current_frame_name))
        return ordered_links

    def list_links_by_kind(
            self,
            source_kind: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        self.check_cleaned()
        if not source_kind:
            raise ValueError("source_kind cannot be empty.")
        return [
            link
            for link in self.list_links(frame_name=frame_name)
            if link.source_kind == source_kind
        ]

    def list_links_grouped_by_frame(self) -> Dict[str, List[FrameLink]]:
        self.check_cleaned()
        return {
            frame_name: self._build_links_for_frame(frame_name)
            for frame_name in self.list_frame_names()
        }

    def list_links_grouped_by_kind(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, List[FrameLink]]:
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
        self.check_cleaned()
        if source_kind is None:
            return [
                frame_link.display_name
                for frame_link in self.list_links(frame_name=frame_name)
            ]
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
        self.check_cleaned()
        compiled_access_surface = self._get_required_compiled_access_surface(frame_name)
        grouped_links = self.list_links_grouped_by_kind(frame_name=frame_name)
        descriptor = self._get_required_frame_descriptor(frame_name)
        frame_payload_profile = None
        if descriptor.frame_overview is not None:
            frame_payload_profile = "{0}:{1}".format(
                descriptor.frame_overview.payload.profile_name,
                descriptor.frame_overview.payload.profile_version,
            )
        return {
            "frame_name": frame_name,
            "link_count": len(self._build_links_for_frame(frame_name)),
            "available_kinds": tuple(sorted(grouped_links.keys())),
            "link_counts_by_kind": {
                source_kind: len(grouped_links[source_kind])
                for source_kind in grouped_links.keys()
            },
            "metadata": {
                **compiled_access_surface.metadata,
                "frame_payload_profile": frame_payload_profile,
            },
        }

    def describe_frames(self) -> Dict[str, Dict[str, object]]:
        self.check_cleaned()
        return {
            frame_name: self.describe_frame(frame_name)
            for frame_name in self.list_frame_names()
        }

    def list_available_targets(
            self,
            *,
            frame_name: Optional[str] = None,
            profile_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[FrameLink]:
        self.check_cleaned()
        selected_frame_name = frame_name or self._get_required_default_frame_name()
        selected_profile = self._resolve_profile(profile_name, selected_frame_name)
        available_targets = self.list_links(frame_name=selected_frame_name)
        if source_kind is not None:
            if not source_kind:
                raise ValueError("source_kind cannot be empty.")
            available_targets = [
                frame_link
                for frame_link in available_targets
                if frame_link.source_kind == source_kind
            ]
        ordered_targets: List[FrameLink] = []
        handled_target_ids = set()
        for preferred_kind in self._kind_order_for_profile(selected_profile):
            for frame_link in available_targets:
                if frame_link.link_id in handled_target_ids:
                    continue
                if frame_link.source_kind != preferred_kind:
                    continue
                ordered_targets.append(frame_link)
                handled_target_ids.add(frame_link.link_id)
        for frame_link in available_targets:
            if frame_link.link_id in handled_target_ids:
                continue
            ordered_targets.append(frame_link)
        return ordered_targets

    def list_view_profile_names(self) -> List[str]:
        self.check_cleaned()
        return self.list_active_profile_names()

    def set_default_view_profile(
            self,
            profile_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Set the selected viewer profile for one frame.

        Args:
            profile_name:
                Active viewer profile name.
            frame_name:
                Optional target frame. When omitted, uses the default frame.

        Returns:
            None.
        """
        target_frame_name = frame_name or self._get_required_default_frame_name()
        self.set_selected_profile_for_frame(target_frame_name, profile_name)

    def describe_available_targets(
            self,
            *,
            frame_name: Optional[str] = None,
            profile_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        self.check_cleaned()
        selected_frame_name = frame_name or self._get_required_default_frame_name()
        selected_profile = self._resolve_profile(profile_name, selected_frame_name)
        target_descriptions: List[Dict[str, object]] = []
        for frame_link in self.list_available_targets(
                frame_name=frame_name,
                profile_name=profile_name,
                source_kind=source_kind,
        ):
            description = {
                "target_id": frame_link.link_id,
                "source_kind": frame_link.source_kind,
                "source_id": frame_link.source_id,
                "display_name": frame_link.display_name,
            }
            if selected_profile.default_detail_level == "detailed":
                description["metadata"] = frame_link.metadata
            target_descriptions.append(description)
        return target_descriptions

    def get_required_link_by_source(
            self,
            *,
            frame_name: str,
            source_kind: str,
            source_id: str,
    ) -> FrameLink:
        self.check_cleaned()
        if not source_kind:
            raise ValueError("source_kind cannot be empty.")
        if not source_id:
            raise ValueError("source_id cannot be empty.")
        for frame_link in self.list_links(frame_name=frame_name):
            if frame_link.source_kind == source_kind and frame_link.source_id == source_id:
                return frame_link
        raise ValueError(
            "FrameLink '{0}:{1}' was not found in frame '{2}'.".format(
                source_kind,
                source_id,
                frame_name,
            )
        )

    def clone(self) -> "FrameViewer":
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
                default_profile_name=self._default_profile_name,
                frame_descriptors_by_name=dict(self._frame_descriptors_by_name),
                frame_acl_configurations_by_frame_name=dict(
                    self._frame_acl_configurations_by_frame_name
                ),
                compiled_access_surfaces_by_frame_name={
                    frame_name: self._clone_compiled_access_surface(
                        compiled_access_surface
                    )
                    for frame_name, compiled_access_surface in (
                        self._compiled_access_surfaces_by_frame_name.items()
                    )
                },
                selected_profile_names_by_frame_name=self.selected_profile_names_by_frame_name,
                default_view_frame_name=self._default_view_frame_name,
                metadata=dict(self._metadata),
            )

    def list_enabled_helpers(self) -> Tuple[str, ...]:
        self.check_cleaned()
        return self.enabled_helpers

    def list_available_tools(self) -> Tuple[str, ...]:
        self.check_cleaned()
        if self._default_profile_name is None:
            return tuple()
        return self._active_profiles_by_name[
            self._default_profile_name
        ].list_tool_names()

    def list_active_profile_names(self) -> List[str]:
        self.check_cleaned()
        with self._lock:
            return list(sorted(self._active_profiles_by_name.keys()))

    def register_active_profile(self, profile: FrameViewerProfile) -> None:
        self.check_cleaned()
        if not isinstance(profile, FrameViewerProfile):
            raise TypeError("profile must be a FrameViewerProfile.")
        with self._lock:
            existing_profile = self._active_profiles_by_name.get(profile.name)
            if existing_profile is not None and existing_profile is not profile:
                existing_profile.cleanup()
            self._active_profiles_by_name[profile.name] = profile
            if self._default_profile_name is None:
                self._default_profile_name = profile.name
            for frame_name, selected_profile in list(
                    self._selected_profiles_by_frame_name.items()
            ):
                if selected_profile.name != profile.name:
                    continue
                selected_profile.cleanup()
                self._selected_profiles_by_frame_name[frame_name] = (
                    self._create_bound_profile_for_frame(frame_name, profile.name)
                )

    def set_default_profile(self, profile_name: str) -> None:
        self.check_cleaned()
        if not profile_name:
            raise ValueError("profile_name cannot be empty.")
        with self._lock:
            if profile_name not in self._active_profiles_by_name:
                raise ValueError(
                    "FrameViewer profile '{0}' was not found.".format(profile_name)
                )
            self._default_profile_name = profile_name
            if self._default_view_frame_name is not None:
                selected_profile = self._selected_profiles_by_frame_name.get(
                    self._default_view_frame_name
                )
                if selected_profile is not None:
                    selected_profile.cleanup()
                self._selected_profiles_by_frame_name[self._default_view_frame_name] = (
                    self._create_bound_profile_for_frame(
                        self._default_view_frame_name,
                        profile_name,
                    )
                )

    def get_selected_profile_for_frame(self, frame_name: str) -> FrameViewerProfile:
        """
        Return the selected bound profile for one frame or raise.

        Args:
            frame_name:
                Hosted frame name.

        Returns:
            FrameViewerProfile: Selected bound profile for the frame.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        try:
            return self._selected_profiles_by_frame_name[frame_name]
        except KeyError as exc:
            raise ValueError(
                "FrameViewer has no selected profile for frame '{0}'.".format(
                    frame_name
                )
            ) from exc

    def set_selected_profile_for_frame(
            self,
            frame_name: str,
            profile_name: str,
    ) -> None:
        """
        Select and bind one profile for one hosted frame.

        Args:
            frame_name:
                Hosted frame name.
            profile_name:
                Active viewer profile name to bind.

        Returns:
            None.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not profile_name:
            raise ValueError("profile_name cannot be empty.")
        self._get_required_frame_descriptor(frame_name)
        with self._lock:
            selected_profile = self._selected_profiles_by_frame_name.get(frame_name)
            if selected_profile is not None:
                selected_profile.cleanup()
            self._selected_profiles_by_frame_name[frame_name] = (
                self._create_bound_profile_for_frame(frame_name, profile_name)
            )

    def has_enabled_helper(self, helper_name: str) -> bool:
        self.check_cleaned()
        if not helper_name:
            raise ValueError("helper_name cannot be empty.")
        if self._default_profile_name is None:
            return False
        return self._active_profiles_by_name[self._default_profile_name].has_tool(
            helper_name
        )

    def execute_tool(
            self,
            tool_name: str,
            *,
            profile_name: Optional[str] = None,
            **kwargs,
    ) -> Any:
        self.check_cleaned()
        if not tool_name:
            raise ValueError("tool_name cannot be empty.")
        if len(self._active_profiles_by_name) == 0:
            raise ValueError("FrameViewer has no active profiles.")
        selected_frame_name = kwargs.get("frame_name") or self._default_view_frame_name
        selected_profile = self._resolve_profile(
            profile_name,
            selected_frame_name,
        )
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
        if self._default_profile_name is None:
            return
        default_profile = self._active_profiles_by_name[self._default_profile_name]
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

    def _resolve_profile(
            self,
            profile_name: Optional[str],
            frame_name: Optional[str],
    ) -> FrameViewerProfile:
        if len(self._active_profiles_by_name) == 0:
            raise ValueError("FrameViewer has no active profiles.")
        if frame_name is not None:
            if profile_name is None:
                return self.get_selected_profile_for_frame(frame_name)
            return self._create_bound_profile_for_frame(frame_name, profile_name)
        selected_profile_name = profile_name or self._default_profile_name
        if selected_profile_name is None:
            raise ValueError("FrameViewer has no default active profile.")
        return self.get_required_active_profile(selected_profile_name)

    def _get_required_default_frame_name(self) -> str:
        if self._default_view_frame_name is None:
            raise ValueError("FrameViewer has no default selected frame.")
        return self._default_view_frame_name

    def _get_required_frame_descriptor(self, frame_name: str) -> FrameDescriptor:
        try:
            return self._frame_descriptors_by_name[frame_name]
        except KeyError as exc:
            raise ValueError(
                "Frame '{0}' was not found.".format(frame_name)
            ) from exc

    def _get_required_compiled_access_surface(
            self,
            frame_name: str,
    ) -> CompiledFrameACLAccessSurface:
        try:
            return self._compiled_access_surfaces_by_frame_name[frame_name]
        except KeyError as exc:
            raise ValueError(
                "Compiled access surface for frame '{0}' was not found.".format(
                    frame_name
                )
            ) from exc

    def _get_required_frame_acl_configuration(
            self,
            frame_name: str,
    ) -> FrameACLConfiguration:
        try:
            return self._frame_acl_configurations_by_frame_name[frame_name]
        except KeyError as exc:
            raise ValueError(
                "Frame ACL configuration for frame '{0}' was not found.".format(
                    frame_name
                )
            ) from exc

    def _build_links_for_frame(self, frame_name: str) -> List[FrameLink]:
        descriptor = self._get_required_frame_descriptor(frame_name)
        compiled_access_surface = self._get_required_compiled_access_surface(
            frame_name
        )
        links: List[FrameLink] = []
        frame_overview = descriptor.frame_overview
        if "frame" in compiled_access_surface.allowed_kinds:
            if frame_overview is None:
                raise ValueError(
                    "FrameDescriptor must expose frame_overview for frame links."
                )
            links.append(
                FrameLink.from_view_subject(
                    frame_name=frame_name,
                    source_kind="frame",
                    source_id=frame_overview.frame_id,
                    display_name=frame_overview.frame_name,
                    metadata={
                        "payload_fields": tuple(
                            compiled_access_surface.frame_payload_fields
                        ),
                        "frame_id": frame_overview.frame_id,
                        "nexus_label": frame_overview.nexus_label,
                        "nexus_version": frame_overview.nexus_version,
                        "config_origin_spellbook_id": (
                            frame_overview.config_origin_spellbook_id
                        ),
                        "payload_version": frame_overview.payload.payload_version,
                    },
                )
            )
        conduit_records_by_id = descriptor.conduit_records_by_id
        conduit_sections_by_id = (
            compiled_access_surface.conduit_payload_sections_by_id
        )
        if "conduit" in compiled_access_surface.allowed_kinds:
            for conduit_id in sorted(compiled_access_surface.visible_conduit_ids):
                try:
                    conduit_record = conduit_records_by_id[conduit_id]
                except KeyError as exc:
                    raise ValueError(
                        "Missing ConduitRecord for compiled conduit id '{0}'.".format(
                            conduit_id
                        )
                    ) from exc
                links.append(
                    FrameLink.from_view_subject(
                        frame_name=frame_name,
                        source_kind="conduit",
                        source_id=conduit_id,
                        display_name=conduit_record.payload.conduit_name or conduit_id,
                        metadata={
                            "payload_sections": conduit_sections_by_id.get(
                                conduit_id,
                                tuple(),
                            ),
                            "nexus_label": conduit_record.nexus_label,
                            "nexus_version": conduit_record.nexus_version,
                            "root_conduit_id": conduit_record.root_conduit_id,
                            "origin_spellbook_id": conduit_record.origin_spellbook_id,
                            "payload_version": conduit_record.payload.payload_version,
                        },
                    )
                )
        spell_records_by_key = descriptor.spell_records_by_key
        spell_sections_by_key = compiled_access_surface.spell_payload_sections_by_key
        if "spell" in compiled_access_surface.allowed_kinds:
            for record_key in sorted(compiled_access_surface.visible_spell_keys):
                try:
                    spell_record = spell_records_by_key[record_key]
                except KeyError as exc:
                    raise ValueError(
                        "Missing SpellRecord for compiled spell key '{0}'.".format(
                            record_key
                        )
                    ) from exc
                links.append(
                    FrameLink.from_view_subject(
                        frame_name=frame_name,
                        source_kind="spell",
                        source_id="{0}:{1}".format(record_key[0], record_key[1]),
                        display_name=(
                            spell_record.binding_name
                            or spell_record.spell_name
                            or spell_record.spell_id
                        ),
                        metadata={
                            "record_key": record_key,
                            "spell_id": spell_record.spell_id,
                            "lineage_id": spell_record.lineage_id,
                            "owner_conduit_id": spell_record.owner_conduit_id,
                            "payload_sections": spell_sections_by_key.get(
                                record_key,
                                tuple(),
                            ),
                            "nexus_label": spell_record.nexus_label,
                            "nexus_version": spell_record.nexus_version,
                            "payload_type": spell_record.payload.payload_type,
                            "payload_version": spell_record.payload.payload_version,
                            "source_profile_name": (
                                spell_record.payload.source_profile_name
                            ),
                            "source_profile_version": (
                                spell_record.payload.source_profile_version
                            ),
                        },
                    )
                )
        return links

    def _kind_order_for_profile(
            self,
            profile: FrameViewerProfile,
    ) -> Tuple[str, ...]:
        return self._DEFAULT_KIND_ORDER

    def _create_bound_profile_for_frame(
            self,
            frame_name: str,
            profile_name: str,
    ) -> FrameViewerProfile:
        """
        Create one bound profile clone for one hosted frame.

        Args:
            frame_name:
                Hosted frame name.
            profile_name:
                Active viewer profile name to clone and bind.

        Returns:
            FrameViewerProfile: Bound profile clone.
        """
        template_profile = self.get_required_active_profile(profile_name)
        return template_profile.clone_bound_to_frame(
            frame_name=frame_name,
            frame_descriptor=self._get_required_frame_descriptor(frame_name),
            frame_acl_configuration=self._get_required_frame_acl_configuration(
                frame_name
            ),
            compiled_access_surface=self._get_required_compiled_access_surface(
                frame_name
            ),
        )

    @staticmethod
    def _clone_compiled_access_surface(
            compiled_access_surface: CompiledFrameACLAccessSurface,
    ) -> CompiledFrameACLAccessSurface:
        return CompiledFrameACLAccessSurface(
            frame_name=compiled_access_surface.frame_name,
            configuration_id=compiled_access_surface.configuration_id,
            view_profile_name=compiled_access_surface.view_profile_name,
            view_profile_version=compiled_access_surface.view_profile_version,
            codegen_profile_name=compiled_access_surface.codegen_profile_name,
            codegen_profile_version=compiled_access_surface.codegen_profile_version,
            allowed_kinds=compiled_access_surface.allowed_kinds,
            allowed_commands=compiled_access_surface.allowed_commands,
            frame_payload_fields=compiled_access_surface.frame_payload_fields,
            visible_conduit_ids=compiled_access_surface.visible_conduit_ids,
            visible_spell_keys=compiled_access_surface.visible_spell_keys,
            conduit_payload_sections_by_id=(
                compiled_access_surface.conduit_payload_sections_by_id
            ),
            spell_payload_sections_by_key=(
                compiled_access_surface.spell_payload_sections_by_key
            ),
            metadata=compiled_access_surface.metadata,
        )
