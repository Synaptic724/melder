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
        """
        Return the hosted frame names in deterministic order.

        Returns:
            List[str]: Sorted hosted frame names.
        """
        self.check_cleaned()
        with self._lock:
            return list(sorted(self._frame_descriptors_by_name.keys()))

    def count_frames(self) -> int:
        """
        Return the number of hosted frame descriptors.

        Returns:
            int: Hosted frame count.
        """
        self.check_cleaned()
        return len(self.list_frame_names())

    def set_default_view(self, frame_name: str) -> None:
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        with self._lock:
            if frame_name not in self._frame_descriptors_by_name:
                raise ValueError("Frame '{0}' was not found.".format(frame_name))
            self._default_view_frame_name = frame_name

    def describe_available_views(self) -> List[Dict[str, object]]:
        """
        Return a simple host-level description of the hosted frames.

        Contract:
            This is a host-only descriptor surface. It does not expose payload
            data or ACL-shaped visibility details.

        Returns:
            List[Dict[str, object]]: Hosted frame descriptions.
        """
        self.check_cleaned()
        described_frames: List[Dict[str, object]] = []
        for frame_name in self.list_frame_names():
            described_frames.append(
                {
                    "frame_name": frame_name,
                    "is_default": frame_name == self._default_view_frame_name,
                }
            )
        return described_frames

    def count_root_conduits(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of root conduit records.

        Args:
            frame_name:
                Optional frame name. When omitted, counts across all hosted
                frames.

        Returns:
            int: Root conduit record count.
        """
        self.check_cleaned()
        frame_names = [frame_name] if frame_name is not None else self.list_frame_names()
        total_count = 0
        for current_frame_name in frame_names:
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            total_count += len(
                {
                    conduit_record.root_conduit_id
                    for conduit_record in descriptor.conduit_records_by_id.values()
                }
            )
        return total_count

    def count_spell_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of spell records.

        Args:
            frame_name:
                Optional frame name. When omitted, counts across all hosted
                frames.

        Returns:
            int: Spell record count.
        """
        self.check_cleaned()
        frame_names = [frame_name] if frame_name is not None else self.list_frame_names()
        total_count = 0
        for current_frame_name in frame_names:
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            total_count += len(descriptor.spell_records_by_key)
        return total_count

    def describe_frame(self, frame_name: str) -> Dict[str, object]:
        """
        Return a descriptor-level summary for one hosted frame.

        Contract:
            This host-level summary is limited to descriptor structure and
            published record identity. It does not expose payload bodies or
            ACL-shaped payload visibility.

        Args:
            frame_name:
                Hosted frame name to summarize.

        Returns:
            Dict[str, object]: Descriptor-level frame summary.
        """
        self.check_cleaned()
        descriptor = self._get_required_frame_descriptor(frame_name)
        frame_overview = descriptor.frame_overview
        return {
            "frame_name": frame_name,
            "frame_id": frame_overview.frame_id if frame_overview is not None else None,
            "nexus_label": (
                frame_overview.nexus_label if frame_overview is not None else None
            ),
            "nexus_version": (
                frame_overview.nexus_version if frame_overview is not None else None
            ),
            "conduit_record_count": len(descriptor.conduit_records_by_id),
            "root_conduit_count": len(
                {
                    conduit_record.root_conduit_id
                    for conduit_record in descriptor.conduit_records_by_id.values()
                }
            ),
            "spell_record_count": len(descriptor.spell_records_by_key),
            "is_default": frame_name == self._default_view_frame_name,
        }

    def describe_frames(self) -> Dict[str, Dict[str, object]]:
        """
        Return descriptor-level summaries for all hosted frames.

        Returns:
            Dict[str, Dict[str, object]]: Hosted frame summaries keyed by frame
            name.
        """
        self.check_cleaned()
        return {
            current_frame_name: self.describe_frame(current_frame_name)
            for current_frame_name in self.list_frame_names()
        }

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

    def execute_method(
            self,
            method_name: str,
            *,
            profile_name: Optional[str] = None,
            **kwargs,
    ) -> Any:
        """
        Execute one selected-profile method for the target frame context.

        Purpose:
            Provide one narrow dispatch seam for profile-owned method surfaces
            without re-exposing ACL/payload methods directly on the
            `FrameViewer` host.

        Contract:
            - Resolves the selected bound profile for the requested frame.
            - Looks up the exposed profile method name on that profile.
            - Allows the profile mapping to target either bound helper methods
              or simple host descriptor methods on `FrameViewer`.
            - Raises when the requested profile method is not exposed or when
              the mapped handler cannot be resolved.

        Args:
            method_name:
                Exposed profile method name to execute.
            profile_name:
                Optional explicit profile name override.
            **kwargs:
                Arguments forwarded to the resolved handler.

        Returns:
            Any: Handler return value.

        Raises:
            ValueError:
                Raised when `method_name` is empty, no active profiles exist,
                the requested profile method is not exposed, or the mapped
                handler cannot be resolved.
        """
        self.check_cleaned()
        if not method_name:
            raise ValueError("method_name cannot be empty.")
        if len(self._active_profiles_by_name) == 0:
            raise ValueError("FrameViewer has no active profiles.")
        selected_frame_name = kwargs.get("frame_name") or self._default_view_frame_name
        selected_profile = self._resolve_profile(
            profile_name,
            selected_frame_name,
        )
        handler_name = selected_profile.get_required_tool_handler_name(method_name)
        handler = self._resolve_tool_handler(
            selected_profile,
            handler_name,
            viewer=self,
        )
        if handler is None or not callable(handler):
            raise ValueError(
                "FrameViewer profile method '{0}' targets missing handler '{1}'.".format(
                    method_name,
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

    @staticmethod
    def _resolve_tool_handler(
            selected_profile: FrameViewerProfile,
            handler_name: str,
            viewer: Optional["FrameViewer"] = None,
    ) -> Optional[Any]:
        """
        Resolve one tool handler against the bound profile first, then viewer.

        Args:
            selected_profile:
                Bound selected profile for the current frame.
            handler_name:
                Tool handler name or dotted helper path.
            viewer:
                Optional viewer host fallback.

        Returns:
            Optional[Any]: Resolved callable when found.
        """
        resolved = FrameViewer._resolve_callable_path(selected_profile, handler_name)
        if resolved is not None:
            return resolved
        if viewer is None:
            return None
        return FrameViewer._resolve_callable_path(viewer, handler_name)

    @staticmethod
    def _resolve_callable_path(root_object: Any, handler_name: str) -> Optional[Any]:
        """
        Resolve one callable path from a root object.

        Args:
            root_object:
                Root object to traverse.
            handler_name:
                Handler name or dotted helper path.

        Returns:
            Optional[Any]: Resolved callable when found.
        """
        current_object = root_object
        for current_part in handler_name.split("."):
            current_object = getattr(current_object, current_part, None)
            if current_object is None:
                return None
        return current_object

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
