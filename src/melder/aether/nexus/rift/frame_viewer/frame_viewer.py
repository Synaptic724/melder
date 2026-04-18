"""
Internal descriptor-driven FrameViewer surface.
"""

import json
import threading
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

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
from melder.utilities.helpers.class_surface_ast_describer import (
    ClassSurfaceAstDescriber,
)
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import IRiftGate


class FrameViewer(Cleanable):
    """
    Purpose:
        Hold the hosted frame descriptors plus the selected profile/runtime
        context an operator uses to inspect the current Rift-visible frame
        surface.

    Contract:
        - Holds non-owned `FrameDescriptor` references keyed by frame name.
        - Owns detached `CompiledFrameACLAccessSurface` objects keyed by frame
          name.
        - Owns reusable active `FrameViewerProfile` templates and one selected
          bound profile per hosted frame.
        - Exposes descriptor-only multi-frame host methods directly on the
          viewer.
        - Exposes frame-local ACL/payload-aware behavior only through the
          selected bound profile surface.
        - Does not expose raw runtime objects or any direct code-execution
          behavior.

    Threading:
        Uses one instance `threading.RLock` to serialize cleanup and multi-step
        profile/selection mutations.

    Lifecycle:
        Cleanup cascades into owned compiled ACL surfaces, active profile
        templates, and selected bound profiles before clearing viewer-owned
        maps and metadata.
    """

    __melder_internal__ = _mrg.sentinel
    _ast_helper_access: str = "public"
    __agent_purpose__: str = (
        "access: public. Multi-frame descriptor host and selected-profile "
        "router for the Rift viewer surface. Use this object to inspect hosted "
        "frames, compare descriptor records, and reach the selected profile "
        "surface for frame-local methods."
    )
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
        "_rift_gate",
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
            rift_gate: Optional[IRiftGate] = None,
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
            rift_gate:
                Optional Rift gate used to coordinate viewer admission.
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
        self._rift_gate: Optional[IRiftGate] = rift_gate
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
            self._rift_gate = None
            self._metadata = None
            self._viewer_id = None
        self._lock = None

    def bind_rift_gate(self, rift_gate: Optional[IRiftGate]) -> None:
        """
        Bind or replace the optional Rift gate used for viewer admission.

        Args:
            rift_gate:
                Optional Rift gate to bind.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._rift_gate = rift_gate

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
        """
        Select the default hosted frame for subsequent host/profile calls.

        Purpose:
            Move the viewer's default frame pointer so host methods and
            frame-local profile execution can fall back to a known frame when
            callers omit `frame_name`.

        Args:
            frame_name:
                Hosted frame name to promote to the default view.

        Returns:
            None.

        Raises:
            ValueError:
                Raised when `frame_name` is empty or not hosted by this
                viewer.
        """
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

    def describe_frame_brief(self, frame_name: str) -> Dict[str, object]:
        """
        Return one compact descriptor-level frame summary.

        Purpose:
            Give the operator a smaller "start here" frame summary than
            `describe_frame(...)` while staying entirely on descriptor-owned
            host data.

        Contract:
            - Uses only descriptor/record identity and count data.
            - Does not expose payload bodies or ACL-shaped visibility details.
            - Always includes the frame's Nexus contract and top-level record
              counts.

        Args:
            frame_name:
                Hosted frame name to summarize.

        Returns:
            Dict[str, object]: Compact descriptor-level frame summary.
        """
        self.check_cleaned()
        frame_summary = self.describe_frame(frame_name)
        return {
            "frame_name": frame_summary["frame_name"],
            "frame_id": frame_summary["frame_id"],
            "nexus_contract": "{0}:{1}".format(
                frame_summary["nexus_label"],
                frame_summary["nexus_version"],
            ),
            "conduit_record_count": frame_summary["conduit_record_count"],
            "root_conduit_count": frame_summary["root_conduit_count"],
            "spell_record_count": frame_summary["spell_record_count"],
            "is_default": frame_summary["is_default"],
        }

    def describe_host_inventory(self) -> Dict[str, object]:
        """
        Return one compact host-level inventory summary.

        Purpose:
            Give the operator a quick overview of what the `FrameViewer` host
            is carrying without forcing a deeper descriptor walk.

        Contract:
            - Aggregates only descriptor-owned counts, names, and record-level
              identities.
            - Does not expose payload bodies or ACL-shaped detail.

        Returns:
            Dict[str, object]: Compact host-level inventory summary.
        """
        self.check_cleaned()
        return {
            "frame_count": self.count_frames(),
            "default_view_frame_name": self._default_view_frame_name,
            "frame_names": tuple(self.list_frame_names()),
            "frame_ids": tuple(self.list_frame_ids()),
            "conduit_record_count": self.count_conduit_records(),
            "root_conduit_count": self.count_root_conduits(),
            "spell_record_count": self.count_spell_records(),
            "origin_spellbook_count": self.count_spellbooks(),
            "origin_spellbook_ids": tuple(self.list_origin_spellbook_ids()),
            "permissions": tuple(self.list_permissions()),
            "existence_kinds": tuple(self.list_existence_kinds()),
        }

    def describe_viewer(self) -> Dict[str, object]:
        """
        Return one compact summary of the `FrameViewer` host itself.

        Purpose:
            Give the operator one host-level summary of what this viewer is
            currently carrying without walking frame-local helper surfaces.

        Contract:
            - Returns host identity, default routing state, and descriptor-only
              inventory posture.
            - Does not expose payload bodies, ACL-shaped data, or frame-local
              helper output.

        Returns:
            Dict[str, object]: Compact host summary for this viewer.
        """
        self.check_cleaned()
        return {
            "viewer_id": self.viewer_id,
            "frame_count": self.count_frames(),
            "default_view_frame_name": self._default_view_frame_name,
            "default_profile_name": self.profile_name,
            "default_profile_version": self.profile_version,
            "frame_names": tuple(self.list_frame_names()),
            "host_boundary": "descriptor_only",
        }

    def describe_current_frame(self) -> Dict[str, object]:
        """
        Return the descriptor-level summary for the current default frame.

        Purpose:
            Save the operator one extra lookup when the current default frame
            is already the intended host target.

        Contract:
            - Resolves only the current default hosted frame.
            - Uses the same descriptor-only summary contract as
              `describe_frame(...)`.

        Returns:
            Dict[str, object]: Descriptor-level summary for the current frame.
        """
        self.check_cleaned()
        return self.describe_frame(self._get_required_default_frame_name())

    def describe_frames_inventory(self) -> Dict[str, Dict[str, object]]:
        """
        Return one compact per-frame descriptor inventory summary.

        Purpose:
            Give the operator a small inventory table across hosted frames
            without exposing anything deeper than descriptor-owned counts and
            stable record identity.

        Contract:
            - Multi-frame output stays shallow and descriptor-only.
            - Does not expose payload bodies or ACL-shaped visibility detail.
            - Includes only per-frame counts and stable host identity fields.

        Returns:
            Dict[str, Dict[str, object]]: Per-frame compact inventories keyed
            by frame name.
        """
        self.check_cleaned()
        return {
            current_frame_name: {
                "frame_id": self.describe_frame(current_frame_name)["frame_id"],
                "nexus_contract": "{0}:{1}".format(
                    self.describe_frame(current_frame_name)["nexus_label"],
                    self.describe_frame(current_frame_name)["nexus_version"],
                ),
                "conduit_record_count": self.describe_frame(current_frame_name)[
                    "conduit_record_count"
                ],
                "root_conduit_count": self.describe_frame(current_frame_name)[
                    "root_conduit_count"
                ],
                "spell_record_count": self.describe_frame(current_frame_name)[
                    "spell_record_count"
                ],
                "origin_spellbook_count": len(
                    self.list_origin_spellbook_ids(frame_name=current_frame_name)
                ),
                "lineage_count": len(
                    self.list_lineage_ids(frame_name=current_frame_name)
                ),
                "is_default": current_frame_name == self._default_view_frame_name,
            }
            for current_frame_name in self.list_frame_names()
        }

    def describe_viewer_method_surface(self) -> Dict[str, object]:
        """
        Return one curated summary of the host-side viewer method surface.

        Purpose:
            Explain how to use the `FrameViewer` host without forcing the
            operator to read the raw AST-described class surface first.

        Contract:
            - Describes only the curated host-side method groups.
            - Keeps the host boundary explicit: descriptor-only on the viewer,
              frame-local detail through `execute_method(...)`.

        Returns:
            Dict[str, object]: Curated host method-surface summary.
        """
        self.check_cleaned()
        return {
            "host_boundary": "descriptor_only",
            "default_entrypoints": (
                "describe_viewer",
                "describe_host_inventory",
                "describe_current_frame",
                "describe_frames_inventory",
            ),
            "frame_summary_methods": (
                "list_frame_names",
                "describe_frame",
                "describe_frames",
                "describe_frame_brief",
                "describe_current_frame",
            ),
            "comparison_methods": (
                "compare_frames",
                "compare_frames_brief",
                "compare_frame_conduits",
                "compare_frame_spells",
            ),
            "record_methods": (
                "describe_conduit_records",
                "describe_spell_records",
                "describe_spell_record",
            ),
            "frame_local_method_entrypoint": "execute_method",
        }

    def compare_frames(
            self,
            left_frame_name: str,
            right_frame_name: str,
    ) -> Dict[str, object]:
        """
        Compare two hosted frame descriptors at the record-identity level.

        Purpose:
            Give the operator one descriptor-only diff between two hosted
            frames so they can see what differs without manually comparing the
            individual host list methods.

        Contract:
            - Uses descriptor-owned identities, counts, and normalized values
              only.
            - Does not expose payload bodies or ACL-shaped detail.
            - Returns shared sets plus left-only/right-only deltas for the most
              important descriptor-level inventories.

        Args:
            left_frame_name:
                Left hosted frame name.
            right_frame_name:
                Right hosted frame name.

        Returns:
            Dict[str, object]: Descriptor-level comparison summary.
        """
        self.check_cleaned()
        left_descriptor = self._get_required_frame_descriptor(left_frame_name)
        self._get_required_frame_descriptor(right_frame_name)
        left_frame_overview = left_descriptor.frame_overview
        right_frame_overview = self._get_required_frame_descriptor(
            right_frame_name
        ).frame_overview
        return {
            "left_frame_name": left_frame_name,
            "right_frame_name": right_frame_name,
            "same_frame_id": (
                left_frame_overview is not None
                and right_frame_overview is not None
                and left_frame_overview.frame_id == right_frame_overview.frame_id
            ),
            "same_nexus_contract": (
                left_frame_overview is not None
                and right_frame_overview is not None
                and left_frame_overview.nexus_label == right_frame_overview.nexus_label
                and left_frame_overview.nexus_version == right_frame_overview.nexus_version
            ),
            "conduits": self.compare_frame_conduits(
                left_frame_name,
                right_frame_name,
            ),
            "spells": self.compare_frame_spells(
                left_frame_name,
                right_frame_name,
            ),
            "spellbooks": self._compare_sorted_value_sets(
                tuple(self.list_origin_spellbook_ids(frame_name=left_frame_name)),
                tuple(self.list_origin_spellbook_ids(frame_name=right_frame_name)),
            ),
            "permissions": self._compare_sorted_value_sets(
                tuple(self.list_permissions(frame_name=left_frame_name)),
                tuple(self.list_permissions(frame_name=right_frame_name)),
            ),
            "existence_kinds": self._compare_sorted_value_sets(
                tuple(self.list_existence_kinds(frame_name=left_frame_name)),
                tuple(self.list_existence_kinds(frame_name=right_frame_name)),
            ),
            "spellframes": self._compare_sorted_value_sets(
                tuple(self.list_spellframes(frame_name=left_frame_name)),
                tuple(self.list_spellframes(frame_name=right_frame_name)),
            ),
        }

    def compare_frames_brief(
            self,
            left_frame_name: str,
            right_frame_name: str,
    ) -> Dict[str, object]:
        """
        Return one compact descriptor-only comparison summary for two frames.

        Purpose:
            Provide a smaller "what materially differs?" answer than the full
            `compare_frames(...)` payload.

        Contract:
            - Uses only descriptor-level comparison data derived from the full
              frame comparison.
            - Keeps multi-frame output shallow and count-focused.

        Args:
            left_frame_name:
                Left hosted frame name.
            right_frame_name:
                Right hosted frame name.

        Returns:
            Dict[str, object]: Compact descriptor-level frame comparison.
        """
        self.check_cleaned()
        full_comparison = self.compare_frames(left_frame_name, right_frame_name)
        return {
            "left_frame_name": left_frame_name,
            "right_frame_name": right_frame_name,
            "same_frame_id": full_comparison["same_frame_id"],
            "same_nexus_contract": full_comparison["same_nexus_contract"],
            "left_only_conduit_count": len(
                full_comparison["conduits"]["conduit_ids"]["left_only"]
            ),
            "right_only_conduit_count": len(
                full_comparison["conduits"]["conduit_ids"]["right_only"]
            ),
            "left_only_spell_count": len(
                full_comparison["spells"]["spell_source_ids"]["left_only"]
            ),
            "right_only_spell_count": len(
                full_comparison["spells"]["spell_source_ids"]["right_only"]
            ),
            "shared_permission_count": len(full_comparison["permissions"]["shared"]),
            "shared_existence_kind_count": len(
                full_comparison["existence_kinds"]["shared"]
            ),
        }

    def compare_frame_conduits(
            self,
            left_frame_name: str,
            right_frame_name: str,
    ) -> Dict[str, object]:
        """
        Compare the conduit-record inventories of two hosted frames.

        Args:
            left_frame_name:
                Left hosted frame name.
            right_frame_name:
                Right hosted frame name.

        Returns:
            Dict[str, object]: Conduit-record comparison summary.
        """
        self.check_cleaned()
        left_conduit_ids = tuple(
            self.list_conduit_record_ids(frame_name=left_frame_name)
        )
        right_conduit_ids = tuple(
            self.list_conduit_record_ids(frame_name=right_frame_name)
        )
        left_root_conduit_ids = tuple(
            self.list_root_conduit_ids(frame_name=left_frame_name)
        )
        right_root_conduit_ids = tuple(
            self.list_root_conduit_ids(frame_name=right_frame_name)
        )
        return {
            "record_counts": {
                "left": len(left_conduit_ids),
                "right": len(right_conduit_ids),
            },
            "conduit_ids": self._compare_sorted_value_sets(
                left_conduit_ids,
                right_conduit_ids,
            ),
            "root_conduit_ids": self._compare_sorted_value_sets(
                left_root_conduit_ids,
                right_root_conduit_ids,
            ),
        }

    def compare_frame_spells(
            self,
            left_frame_name: str,
            right_frame_name: str,
    ) -> Dict[str, object]:
        """
        Compare the spell-record inventories of two hosted frames.

        Args:
            left_frame_name:
                Left hosted frame name.
            right_frame_name:
                Right hosted frame name.

        Returns:
            Dict[str, object]: Spell-record comparison summary.
        """
        self.check_cleaned()
        left_spell_source_ids = tuple(
            self.list_spell_source_ids_for_frame(left_frame_name)
        )
        right_spell_source_ids = tuple(
            self.list_spell_source_ids_for_frame(right_frame_name)
        )
        left_lineage_ids = tuple(self.list_lineage_ids(frame_name=left_frame_name))
        right_lineage_ids = tuple(self.list_lineage_ids(frame_name=right_frame_name))
        left_spell_names = tuple(self.list_spell_names(frame_name=left_frame_name))
        right_spell_names = tuple(self.list_spell_names(frame_name=right_frame_name))
        left_binding_names = tuple(self.list_binding_names(frame_name=left_frame_name))
        right_binding_names = tuple(self.list_binding_names(frame_name=right_frame_name))
        return {
            "record_counts": {
                "left": len(left_spell_source_ids),
                "right": len(right_spell_source_ids),
            },
            "spell_source_ids": self._compare_sorted_value_sets(
                left_spell_source_ids,
                right_spell_source_ids,
            ),
            "lineage_ids": self._compare_sorted_value_sets(
                left_lineage_ids,
                right_lineage_ids,
            ),
            "spell_names": self._compare_sorted_value_sets(
                left_spell_names,
                right_spell_names,
            ),
            "binding_names": self._compare_sorted_value_sets(
                left_binding_names,
                right_binding_names,
            ),
        }

    def describe_binding_name_collisions(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return binding-name collisions in the selected descriptor scope.

        Purpose:
            Surface visible ambiguity at the record-identity level when the
            same binding name is attached to multiple published spell records.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Tuple[str, ...]]: Binding names mapped to the colliding
            spell source ids.
        """
        self.check_cleaned()
        return self._describe_spell_value_collisions(
            frame_name=frame_name,
            value_getter=lambda spell_record: spell_record.binding_name,
        )

    def describe_spell_name_collisions(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return spell-name collisions in the selected descriptor scope.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Tuple[str, ...]]: Spell names mapped to the colliding
            spell source ids.
        """
        self.check_cleaned()
        return self._describe_spell_value_collisions(
            frame_name=frame_name,
            value_getter=lambda spell_record: spell_record.spell_name,
        )

    def describe_lineage_groups(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return lineage groups in the selected descriptor scope.

        Purpose:
            Surface all published spell source ids grouped by lineage id, even
            when a lineage currently has only one visible member.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Tuple[str, ...]]: Lineage ids mapped to published spell
            source ids.
        """
        self.check_cleaned()
        return self._describe_spell_value_groups(
            frame_name=frame_name,
            value_getter=lambda spell_record: spell_record.spell_index_id,
        )

    def describe_spellframe_groups(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return spellframe groups in the selected descriptor scope.

        Purpose:
            Group published spells by normalized spellframe value so frame-wide
            spellframe overlaps are obvious.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Tuple[str, ...]]: Spellframe values mapped to published
            spell source ids.
        """
        self.check_cleaned()
        return self._describe_spell_value_groups(
            frame_name=frame_name,
            value_getter=lambda spell_record: self._normalize_spellframe_value(
                spell_record.spellframe
            ),
        )

    def describe_spellbook_permission_mismatches(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Dict[str, object]]:
        """
        Return spellbook groups whose permission posture is not uniform.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Dict[str, object]]: Spellbook ids mapped to permission
            mismatch summaries.
        """
        self.check_cleaned()
        return self._describe_spellbook_mismatches(
            frame_name=frame_name,
            value_getter=lambda spell_record: spell_record.permissions.name,
        )

    def describe_spellbook_existence_mismatches(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Dict[str, object]]:
        """
        Return spellbook groups whose existence posture is not uniform.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Dict[str, object]]: Spellbook ids mapped to existence
            mismatch summaries.
        """
        self.check_cleaned()
        return self._describe_spellbook_mismatches(
            frame_name=frame_name,
            value_getter=lambda spell_record: spell_record.existence.name,
        )

    def compare_spell_records(
            self,
            left_spell_source_id: str,
            right_spell_source_id: str,
            *,
            left_frame_name: Optional[str] = None,
            right_frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Compare two published spell records.

        Purpose:
            Give the operator one record-level spell diff without requiring them
            to manually compare multiple identity, provenance, and posture
            methods.

        Args:
            left_spell_source_id:
                Left published spell source id.
            right_spell_source_id:
                Right published spell source id.
            left_frame_name:
                Optional hosted frame constraint for the left spell.
            right_frame_name:
                Optional hosted frame constraint for the right spell.

        Returns:
            Dict[str, object]: Record-level spell comparison summary.
        """
        self.check_cleaned()
        resolved_left_frame_name, left_spell_record = self._get_required_spell_record(
            left_spell_source_id,
            frame_name=left_frame_name,
        )
        resolved_right_frame_name, right_spell_record = self._get_required_spell_record(
            right_spell_source_id,
            frame_name=right_frame_name,
        )
        return {
            "left_source_id": left_spell_source_id,
            "right_source_id": right_spell_source_id,
            "same_frame": resolved_left_frame_name == resolved_right_frame_name,
            "same_origin_spellbook": (
                left_spell_record.origin_spellbook_id
                == right_spell_record.origin_spellbook_id
            ),
            "same_owner_conduit": (
                left_spell_record.owner_conduit_id
                == right_spell_record.owner_conduit_id
            ),
            "same_spell_index_id": (
                left_spell_record.spell_index_id == right_spell_record.spell_index_id
            ),
            "same_spell_name": (
                left_spell_record.spell_name == right_spell_record.spell_name
            ),
            "same_binding_name": (
                left_spell_record.binding_name == right_spell_record.binding_name
            ),
            "same_spellframe": (
                self._normalize_spellframe_value(left_spell_record.spellframe)
                == self._normalize_spellframe_value(right_spell_record.spellframe)
            ),
            "same_permissions": (
                left_spell_record.permissions.name
                == right_spell_record.permissions.name
            ),
            "same_existence": (
                left_spell_record.existence.name
                == right_spell_record.existence.name
            ),
            "same_payload_type": (
                left_spell_record.payload.payload_type
                == right_spell_record.payload.payload_type
            ),
            "same_nexus_contract": (
                left_spell_record.nexus_label == right_spell_record.nexus_label
                and left_spell_record.nexus_version == right_spell_record.nexus_version
            ),
        }

    def compare_conduit_records(
            self,
            left_conduit_id: str,
            right_conduit_id: str,
            *,
            left_frame_name: Optional[str] = None,
            right_frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Compare two published conduit records.

        Args:
            left_conduit_id:
                Left published conduit id.
            right_conduit_id:
                Right published conduit id.
            left_frame_name:
                Optional hosted frame constraint for the left conduit.
            right_frame_name:
                Optional hosted frame constraint for the right conduit.

        Returns:
            Dict[str, object]: Record-level conduit comparison summary.
        """
        self.check_cleaned()
        resolved_left_frame_name, left_conduit_record = self._get_required_conduit_record(
            left_conduit_id,
            frame_name=left_frame_name,
        )
        resolved_right_frame_name, right_conduit_record = self._get_required_conduit_record(
            right_conduit_id,
            frame_name=right_frame_name,
        )
        return {
            "left_conduit_id": left_conduit_id,
            "right_conduit_id": right_conduit_id,
            "same_frame": resolved_left_frame_name == resolved_right_frame_name,
            "same_root_conduit_id": (
                left_conduit_record.root_conduit_id
                == right_conduit_record.root_conduit_id
            ),
            "same_origin_spellbook": (
                left_conduit_record.origin_spellbook_id
                == right_conduit_record.origin_spellbook_id
            ),
            "same_policy": (
                self._normalize_policy_name(left_conduit_record.payload.policy)
                == self._normalize_policy_name(right_conduit_record.payload.policy)
            ),
            "same_conduit_state": (
                left_conduit_record.payload.conduit_state.name
                == right_conduit_record.payload.conduit_state.name
            ),
            "same_peer_conduit_ids": (
                tuple(left_conduit_record.payload.peer_conduit_ids)
                == tuple(right_conduit_record.payload.peer_conduit_ids)
            ),
            "same_nexus_contract": (
                left_conduit_record.nexus_label == right_conduit_record.nexus_label
                and left_conduit_record.nexus_version == right_conduit_record.nexus_version
            ),
        }

    def list_spell_source_ids_for_frame(self, frame_name: str) -> List[str]:
        """
        Return spell source ids for one hosted frame.

        Purpose:
            Provide the canonical published spell identities for one hosted
            descriptor in deterministic order.

        Args:
            frame_name:
                Hosted frame name whose spell source ids should be returned.

        Returns:
            List[str]: Spell source ids for the frame.
        """
        self.check_cleaned()
        descriptor = self._get_required_frame_descriptor(frame_name)
        return [
            self._build_spell_source_id(descriptor.spell_records_by_key[record_key])
            for record_key in sorted(descriptor.spell_records_by_key.keys())
        ]

    def list_frame_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published frame ids for the selected descriptor scope.

        Purpose:
            Surface the stable published frame identifiers without exposing any
            payload body data.

        Contract:
            - Reads only `FrameRecord` identity fields.
            - Returns ids in deterministic frame-order.
            - Omits frames that do not currently expose a `frame_overview`
              record.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns frame ids
                across all hosted descriptors.

        Returns:
            List[str]: Published frame ids in deterministic order.
        """
        self.check_cleaned()
        frame_ids: List[str] = []
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            frame_overview = descriptor.frame_overview
            if frame_overview is None:
                continue
            frame_ids.append(frame_overview.frame_id)
        return frame_ids

    def list_nexus_contracts(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Return the published Nexus dataset contracts for hosted frames.

        Purpose:
            Give the operator a direct host-level view of the record contracts
            currently attached to the selected descriptor scope.

        Contract:
            - Uses only record-level `nexus_label` / `nexus_version`.
            - Does not expose payload body content.
            - Returns one contract entry per frame that currently exposes a
              `frame_overview` record.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns contract
                entries across all hosted frames.

        Returns:
            List[Dict[str, str]]: Nexus contract entries in deterministic frame
            order.
        """
        self.check_cleaned()
        contracts: List[Dict[str, str]] = []
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            frame_overview = descriptor.frame_overview
            if frame_overview is None:
                continue
            contracts.append(
                {
                    "frame_name": current_frame_name,
                    "nexus_label": frame_overview.nexus_label,
                    "nexus_version": frame_overview.nexus_version,
                }
            )
        return contracts

    def count_conduit_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of published conduit records.

        Purpose:
            Surface conduit-record inventory at the descriptor host level
            without reaching into conduit payload bodies.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, counts conduit
                records across all hosted frames.

        Returns:
            int: Published conduit-record count.
        """
        self.check_cleaned()
        return len(self.list_conduit_record_ids(frame_name=frame_name))

    def list_conduit_record_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published conduit record ids for the selected scope.

        Purpose:
            Expose the conduit ids owned by the selected frame descriptor scope
            without surfacing payload details.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns conduit ids
                across all hosted frames.

        Returns:
            List[str]: Conduit ids in deterministic order.
        """
        self.check_cleaned()
        conduit_ids: List[str] = []
        for conduit_record in self._iter_conduit_records(frame_name=frame_name):
            conduit_ids.append(conduit_record.conduit_id)
        return conduit_ids

    def list_root_conduit_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return root conduit ids for the selected descriptor scope.

        Purpose:
            Surface conduit-root topology at the host level using record
            identity only.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns unique root
                conduit ids across all hosted frames.

        Returns:
            List[str]: Deterministically sorted root conduit ids.
        """
        self.check_cleaned()
        root_conduit_ids = {
            conduit_record.root_conduit_id
            for conduit_record in self._iter_conduit_records(frame_name=frame_name)
        }
        return list(sorted(root_conduit_ids))

    def count_spellbooks(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of distinct published origin spellbooks.

        Purpose:
            Surface spellbook provenance breadth at the descriptor host level.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, counts distinct
                spellbook ids across all hosted frames.

        Returns:
            int: Distinct origin spellbook count.
        """
        self.check_cleaned()
        return len(self.list_origin_spellbook_ids(frame_name=frame_name))

    def list_origin_spellbook_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return distinct origin spellbook ids for the selected scope.

        Purpose:
            Expose the spellbook provenance ids attached to the hosted spell
            records.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns distinct
                spellbook ids across all hosted frames.

        Returns:
            List[str]: Distinct spellbook ids in deterministic order.
        """
        self.check_cleaned()
        spellbook_ids = {
            spell_record.origin_spellbook_id
            for spell_record in self._iter_spell_records(frame_name=frame_name)
        }
        return list(sorted(spellbook_ids))

    def list_spell_record_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published spell record ids for the selected scope.

        Purpose:
            Expose spell ids directly from `SpellRecord` ownership without
            surfacing payload bodies.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns spell ids
                across all hosted frames.

        Returns:
            List[str]: Spell ids in deterministic record order.
        """
        self.check_cleaned()
        spell_ids: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            spell_ids.append(spell_record.spell_id)
        return spell_ids

    def list_spell_record_keys(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[Tuple[str, str]]:
        """
        Return canonical spell record keys for the selected scope.

        Purpose:
            Surface the exact `(spellbook_id, spell_id)` storage identities
            attached to the selected descriptors.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns record keys
                across all hosted frames.

        Returns:
            List[Tuple[str, str]]: Spell record keys in deterministic order.
        """
        self.check_cleaned()
        record_keys: List[Tuple[str, str]] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            record_keys.append(spell_record.record_key)
        return record_keys

    def list_spell_names(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published spell names for the selected scope.

        Purpose:
            Expose spell-name inventory directly from `SpellRecord` metadata.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns spell names
                across all hosted frames.

        Returns:
            List[str]: Spell names in deterministic record order.
        """
        self.check_cleaned()
        spell_names: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            spell_names.append(spell_record.spell_name)
        return spell_names

    def list_binding_names(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published binding names for the selected scope.

        Purpose:
            Expose the spell binding identities currently represented in the
            hosted descriptors.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns binding names
                across all hosted frames.

        Returns:
            List[str]: Non-empty binding names in deterministic record order.
        """
        self.check_cleaned()
        binding_names: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            if spell_record.binding_name is None:
                continue
            binding_names.append(spell_record.binding_name)
        return binding_names

    def list_lineage_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return lineage ids for the selected descriptor scope.

        Purpose:
            Expose lineage identity directly from `SpellRecord` metadata.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns lineage ids
                across all hosted frames.

        Returns:
            List[str]: Lineage ids in deterministic record order.
        """
        self.check_cleaned()
        lineage_ids: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            lineage_ids.append(spell_record.spell_index_id)
        return lineage_ids

    def list_spellframes(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return normalized spellframe values for the selected scope.

        Purpose:
            Surface the logical spellframe inventory directly from
            `SpellRecord.spellframe` without exposing payload data.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns unique
                spellframe values across all hosted frames.

        Returns:
            List[str]: Distinct normalized spellframe values in deterministic
            order.
        """
        self.check_cleaned()
        spellframes = {
            self._normalize_spellframe_value(spell_record.spellframe)
            for spell_record in self._iter_spell_records(frame_name=frame_name)
            if self._normalize_spellframe_value(spell_record.spellframe) is not None
        }
        return list(sorted(spellframes))

    def list_permissions(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return distinct spell permission names for the selected scope.

        Purpose:
            Surface the spell permission posture currently represented in the
            hosted descriptors.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns permission
                names across all hosted frames.

        Returns:
            List[str]: Distinct permission names in deterministic order.
        """
        self.check_cleaned()
        permissions = {
            spell_record.permissions.name
            for spell_record in self._iter_spell_records(frame_name=frame_name)
        }
        return list(sorted(permissions))

    def list_existence_kinds(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return distinct spell existence kinds for the selected scope.

        Purpose:
            Surface spell lifetime categories directly from `SpellRecord`
            metadata.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns existence
                kinds across all hosted frames.

        Returns:
            List[str]: Distinct existence-kind names in deterministic order.
        """
        self.check_cleaned()
        existence_kinds = {
            spell_record.existence.name
            for spell_record in self._iter_spell_records(frame_name=frame_name)
        }
        return list(sorted(existence_kinds))

    def describe_descriptor_inventory(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return a descriptor-only inventory summary for the selected scope.

        Purpose:
            Give the operator one compact host-level answer to "what descriptors
            do I have here?" without crossing into payload bodies.

        Contract:
            - Uses only `FrameRecord`, `ConduitRecord`, and `SpellRecord`
              identity/provenance fields.
            - May summarize one frame or the entire hosted viewer scope.
            - Does not expose payload body contents.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, summarizes all hosted
                descriptors together.

        Returns:
            Dict[str, object]: Descriptor-only inventory summary.
        """
        self.check_cleaned()
        frame_names = self._get_frame_names_for_query(frame_name)
        return {
            "frame_count": len(frame_names),
            "frame_names": tuple(frame_names),
            "frame_ids": tuple(self.list_frame_ids(frame_name=frame_name)),
            "conduit_record_count": self.count_conduit_records(frame_name=frame_name),
            "root_conduit_ids": tuple(self.list_root_conduit_ids(frame_name=frame_name)),
            "spell_record_count": self.count_spell_records(frame_name=frame_name),
            "origin_spellbook_count": self.count_spellbooks(frame_name=frame_name),
            "origin_spellbook_ids": tuple(
                self.list_origin_spellbook_ids(frame_name=frame_name)
            ),
            "permissions": tuple(self.list_permissions(frame_name=frame_name)),
            "existence_kinds": tuple(
                self.list_existence_kinds(frame_name=frame_name)
            ),
        }

    def describe_descriptor_topology(self, frame_name: str) -> Dict[str, object]:
        """
        Return descriptor-topology groupings for one hosted frame.

        Purpose:
            Surface the descriptor-owned conduit/spell index structure in one
            place so the operator can understand how records are grouped before
            moving into payload-aware helper methods.

        Contract:
            - Uses only descriptor-owned indexes and record identity fields.
            - Does not expose payload body contents.
            - Requires one concrete hosted frame.

        Args:
            frame_name:
                Hosted frame name whose descriptor topology should be
                summarized.

        Returns:
            Dict[str, object]: Descriptor topology summary for the frame.
        """
        self.check_cleaned()
        descriptor = self._get_required_frame_descriptor(frame_name)
        conduit_ids_by_root_id: Dict[str, List[str]] = {}
        for conduit_record in self._iter_conduit_records(frame_name=frame_name):
            conduit_ids_by_root_id.setdefault(
                conduit_record.root_conduit_id,
                [],
            ).append(conduit_record.conduit_id)
        spell_source_ids_by_conduit_id: Dict[str, List[str]] = {}
        for conduit_id, record_keys in descriptor.spell_keys_by_conduit_id.items():
            for record_key in sorted(record_keys):
                spell_record = descriptor.spell_records_by_key[record_key]
                spell_source_ids_by_conduit_id.setdefault(conduit_id, []).append(
                    self._build_spell_source_id(spell_record)
                )
        spell_record_keys_by_spellbook_id: Dict[str, Tuple[Tuple[str, str], ...]] = {
            spellbook_id: tuple(sorted(record_keys))
            for spellbook_id, record_keys in (
                descriptor.spell_keys_by_spellbook_id.items()
            )
        }
        return {
            "frame_name": frame_name,
            "frame_id": (
                descriptor.frame_overview.frame_id
                if descriptor.frame_overview is not None
                else None
            ),
            "root_conduit_ids": tuple(
                sorted(conduit_ids_by_root_id.keys())
            ),
            "conduit_ids_by_root_id": {
                root_conduit_id: tuple(sorted(conduit_ids))
                for root_conduit_id, conduit_ids in conduit_ids_by_root_id.items()
            },
            "spell_source_ids_by_conduit_id": {
                conduit_id: tuple(spell_source_ids)
                for conduit_id, spell_source_ids in (
                    spell_source_ids_by_conduit_id.items()
                )
            },
            "spell_record_keys_by_spellbook_id": spell_record_keys_by_spellbook_id,
        }

    def describe_conduit_records(self, frame_name: str) -> List[Dict[str, object]]:
        """
        Return descriptor-only conduit record descriptions for one frame.

        Purpose:
            Surface the conduit record identities and lineage grouping owned by
            one frame descriptor without exposing conduit payload bodies.

        Args:
            frame_name:
                Hosted frame name whose conduit records should be described.

        Returns:
            List[Dict[str, object]]: Conduit record descriptions.
        """
        self.check_cleaned()
        descriptor = self._get_required_frame_descriptor(frame_name)
        descriptions: List[Dict[str, object]] = []
        for conduit_record in self._iter_conduit_records(frame_name=frame_name):
            owned_spell_keys = descriptor.spell_keys_by_conduit_id.get(
                conduit_record.conduit_id,
                set(),
            )
            descriptions.append(
                {
                    "frame_name": frame_name,
                    "conduit_id": conduit_record.conduit_id,
                    "root_conduit_id": conduit_record.root_conduit_id,
                    "origin_spellbook_id": conduit_record.origin_spellbook_id,
                    "nexus_label": conduit_record.nexus_label,
                    "nexus_version": conduit_record.nexus_version,
                    "is_root_conduit": (
                        conduit_record.conduit_id == conduit_record.root_conduit_id
                    ),
                    "owned_spell_record_count": len(owned_spell_keys),
                }
            )
        return descriptions

    def describe_spell_records(self, frame_name: str) -> List[Dict[str, object]]:
        """
        Return descriptor-only spell record descriptions for one frame.

        Purpose:
            Surface spell record identities and provenance directly from
            `SpellRecord` without crossing into spell payload bodies.

        Args:
            frame_name:
                Hosted frame name whose spell records should be described.

        Returns:
            List[Dict[str, object]]: Spell record descriptions.
        """
        self.check_cleaned()
        return [
            self.describe_spell_record(
                self._build_spell_source_id(spell_record),
                frame_name=frame_name,
            )
            for spell_record in self._iter_spell_records(frame_name=frame_name)
        ]

    def describe_spell_record(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one descriptor-only spell record description.

        Purpose:
            Give the operator one exact spell-record view built strictly from
            record identity and provenance fields.

        Contract:
            - Uses only `SpellRecord` fields and normalized spellframe values.
            - Does not expose payload body content.
            - When `frame_name` is omitted, searches the hosted frames for a
              unique matching spell source id.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional hosted frame name to constrain the lookup.

        Returns:
            Dict[str, object]: Descriptor-only spell record description.
        """
        self.check_cleaned()
        resolved_frame_name, spell_record = self._get_required_spell_record(
            spell_source_id,
            frame_name=frame_name,
        )
        return {
            "frame_name": resolved_frame_name,
            "source_id": spell_source_id,
            "record_key": spell_record.record_key,
            "spell_id": spell_record.spell_id,
            "spell_index_id": spell_record.spell_index_id,
            "origin_spellbook_id": spell_record.origin_spellbook_id,
            "owner_conduit_id": spell_record.owner_conduit_id,
            "spell_name": spell_record.spell_name,
            "binding_name": spell_record.binding_name,
            "spellframe": self._normalize_spellframe_value(spell_record.spellframe),
            "permissions": spell_record.permissions.name,
            "existence": spell_record.existence.name,
            "payload_type": spell_record.payload.payload_type,
            "payload_version": spell_record.payload.payload_version,
            "nexus_label": spell_record.nexus_label,
            "nexus_version": spell_record.nexus_version,
        }

    def list_spells_by_owner_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids owned by one conduit.

        Purpose:
            Expose spell ownership at the descriptor host level without
            requiring a payload-aware helper path.

        Args:
            conduit_id:
                Required owner conduit id.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        matching_source_ids: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            if spell_record.owner_conduit_id == conduit_id:
                matching_source_ids.append(self._build_spell_source_id(spell_record))
        return matching_source_ids

    def list_spells_by_spellbook_id(
            self,
            spellbook_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids published by one origin spellbook.

        Args:
            spellbook_id:
                Required origin spellbook id.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        if not spellbook_id:
            raise ValueError("spellbook_id cannot be empty.")
        matching_source_ids: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            if spell_record.origin_spellbook_id == spellbook_id:
                matching_source_ids.append(self._build_spell_source_id(spell_record))
        return matching_source_ids

    def list_spells_by_permission(
            self,
            permission: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids with one permission posture.

        Args:
            permission:
                Required permission name.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        if not permission:
            raise ValueError("permission cannot be empty.")
        normalized_permission = permission.lower()
        matching_source_ids: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            if spell_record.permissions.name.lower() == normalized_permission:
                matching_source_ids.append(self._build_spell_source_id(spell_record))
        return matching_source_ids

    def list_spells_by_existence(
            self,
            existence: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids with one existence posture.

        Args:
            existence:
                Required existence-kind name.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        if not existence:
            raise ValueError("existence cannot be empty.")
        normalized_existence = existence.lower()
        matching_source_ids: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            if spell_record.existence.name.lower() == normalized_existence:
                matching_source_ids.append(self._build_spell_source_id(spell_record))
        return matching_source_ids

    def list_spells_by_spellframe(
            self,
            spellframe_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids with one normalized spellframe value.

        Args:
            spellframe_name:
                Required normalized spellframe name.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        if not spellframe_name:
            raise ValueError("spellframe_name cannot be empty.")
        matching_source_ids: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            normalized_spellframe = self._normalize_spellframe_value(
                spell_record.spellframe
            )
            if normalized_spellframe == spellframe_name:
                matching_source_ids.append(self._build_spell_source_id(spell_record))
        return matching_source_ids

    def list_view_profile_names(self) -> List[str]:
        """
        Return the reusable profile names registered on this viewer host.

        Returns:
            List[str]: Sorted reusable profile names.
        """
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
        """
        Return a detached copy of the viewer host.

        Purpose:
            Preserve the non-owned descriptor references while cloning the
            owned compiled ACL surfaces, reusable profiles, selected profile
            bindings, and metadata into a new viewer instance.

        Returns:
            FrameViewer: Detached viewer clone.
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
                rift_gate=self._rift_gate,
                metadata=dict(self._metadata),
            )

    def list_enabled_helpers(self) -> Tuple[str, ...]:
        """
        Return the exposed method names for the default reusable profile.

        Returns:
            Tuple[str, ...]: Exposed method names for the default profile.
        """
        self.check_cleaned()
        return self.enabled_helpers

    def list_available_tools(self) -> Tuple[str, ...]:
        """
        Return the exposed profile-method names for the default profile.

        Purpose:
            Preserve the older helper-surface inventory method while the
            underlying semantics are now method-oriented rather than
            tool-oriented.

        Returns:
            Tuple[str, ...]: Exposed profile-method names for the default
            profile.
        """
        self.check_cleaned()
        if self._default_profile_name is None:
            return tuple()
        return self._active_profiles_by_name[
            self._default_profile_name
        ].list_tool_names()

    def list_active_profile_names(self) -> List[str]:
        """
        Return the reusable profile names registered on the viewer.

        Returns:
            List[str]: Sorted reusable profile names.
        """
        self.check_cleaned()
        with self._lock:
            return list(sorted(self._active_profiles_by_name.keys()))

    def list_viewer_method_names_ast_json(
            self,
            *,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """
        Return a minified JSON list of `FrameViewer` class method names.

        Purpose:
            Give the agent a source-defined list of host methods available on
            the viewer itself without inspecting method bodies or runtime
            internals.

        Args:
            include_private:
                Whether `_private` methods should be included.
            include_dunder:
                Whether `__dunder__` methods should be included.

        Returns:
            str: Minified JSON list of source-defined `FrameViewer` methods.
        """
        self.check_cleaned()
        return ClassSurfaceAstDescriber.list_class_method_names_ast_json(
            self,
            include_private=include_private,
            include_dunder=include_dunder,
        )

    def describe_agent_onboarding_json(self) -> str:
        """
        Return the shared first-time onboarding hint for Melder agents.

        Returns:
            str: Minified JSON onboarding hint for Melder agents.
        """
        self.check_cleaned()
        return ClassSurfaceAstDescriber.describe_agent_onboarding_json()

    def describe_viewer_agent_purpose_json(self) -> str:
        """
        Return the minified JSON agent-purpose surface for the viewer host.

        Returns:
            str: Minified JSON agent-purpose surface for this viewer.
        """
        self.check_cleaned()
        return ClassSurfaceAstDescriber.describe_agent_purpose_json(self)

    def describe_viewer_class_surface_ast_json(
            self,
            *,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """
        Return a minified JSON description of the `FrameViewer` class surface.

        Purpose:
            Expose the source-defined `FrameViewer` class surface, including
            method signatures, properties, and docstrings, for direct agent
            consumption.

        Args:
            include_private:
                Whether `_private` members should be included.
            include_dunder:
                Whether `__dunder__` members should be included.

        Returns:
            str: Minified JSON description of the `FrameViewer` class surface.
        """
        self.check_cleaned()
        return ClassSurfaceAstDescriber.describe_class_surface_ast_json(
            self,
            include_private=include_private,
            include_dunder=include_dunder,
        )

    def list_selected_profile_method_names_ast_json(
            self,
            *,
            frame_name: Optional[str] = None,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """
        Return a minified JSON list of selected-profile class method names.

        Args:
            frame_name:
                Optional hosted frame name whose selected profile should be
                described. When omitted, uses the default frame.
            include_private:
                Whether `_private` methods should be included.
            include_dunder:
                Whether `__dunder__` methods should be included.

        Returns:
            str: Minified JSON list of selected-profile class method names.
        """
        self.check_cleaned()
        selected_profile = self._get_required_selected_profile(frame_name=frame_name)
        return selected_profile.list_class_method_names_ast_json(
            include_private=include_private,
            include_dunder=include_dunder,
        )

    def describe_selected_profile_class_surface_ast_json(
            self,
            *,
            frame_name: Optional[str] = None,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """
        Return a minified JSON description of the selected profile class.

        Args:
            frame_name:
                Optional hosted frame name whose selected profile should be
                described. When omitted, uses the default frame.
            include_private:
                Whether `_private` members should be included.
            include_dunder:
                Whether `__dunder__` members should be included.

        Returns:
            str: Minified JSON description of the selected profile class
            surface.
        """
        self.check_cleaned()
        selected_profile = self._get_required_selected_profile(frame_name=frame_name)
        return selected_profile.describe_class_surface_ast_json(
            include_private=include_private,
            include_dunder=include_dunder,
        )

    def describe_selected_profile_agent_purpose_json(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> str:
        """
        Return the minified JSON agent-purpose surface for the selected profile.

        Args:
            frame_name:
                Optional hosted frame name whose selected profile should be
                described. When omitted, uses the default frame.

        Returns:
            str: Minified JSON agent-purpose surface for the selected profile.
        """
        self.check_cleaned()
        selected_profile = self._get_required_selected_profile(frame_name=frame_name)
        return selected_profile.describe_agent_purpose_json()

    def describe_selected_profile_helper_class_surfaces_ast_json(
            self,
            *,
            frame_name: Optional[str] = None,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """
        Return minified JSON descriptions for the selected profile's helpers.

        Args:
            frame_name:
                Optional hosted frame name whose selected profile helpers
                should be described. When omitted, uses the default frame.
            include_private:
                Whether `_private` helper members should be included.
            include_dunder:
                Whether `__dunder__` helper members should be included.

        Returns:
            str: Minified JSON mapping of helper names to class-surface
            descriptions.
        """
        self.check_cleaned()
        selected_profile = self._get_required_selected_profile(frame_name=frame_name)
        return selected_profile.describe_helper_class_surfaces_ast_json(
            include_private=include_private,
            include_dunder=include_dunder,
        )

    def describe_selected_profile_helper_agent_purposes_json(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> str:
        """
        Return minified JSON agent-purpose surfaces for the selected helpers.

        Args:
            frame_name:
                Optional hosted frame name whose selected profile helpers
                should be described. When omitted, uses the default frame.

        Returns:
            str: Minified JSON mapping of helper names to agent-purpose
            surfaces.
        """
        self.check_cleaned()
        selected_profile = self._get_required_selected_profile(frame_name=frame_name)
        helper_purposes = {
            helper_object_name: json.loads(
                ClassSurfaceAstDescriber.describe_agent_purpose_json(
                    getattr(selected_profile, helper_object_name)
                )
            )
            for helper_object_name in selected_profile.list_helper_object_names()
        }
        return json.dumps(helper_purposes, separators=(",", ":"))

    def describe_selected_ast_surface_json(
            self,
            *,
            frame_name: Optional[str] = None,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """
        Return one minified JSON bundle describing the active AST surfaces.

        Purpose:
            Give the agent one compact JSON payload containing the active
            viewer, selected profile, and helper class surfaces plus the basic
            runtime asset identity for the current frame context.

        Args:
            frame_name:
                Optional hosted frame name whose selected profile should be
                described. When omitted, uses the default frame.
            include_private:
                Whether `_private` class members should be included.
            include_dunder:
                Whether `__dunder__` class members should be included.

        Returns:
            str: Minified JSON bundle for the active AST-described surfaces.
        """
        self.check_cleaned()
        selected_frame_name = self._get_required_selected_frame_name(frame_name)
        selected_profile = self.get_selected_profile_for_frame(selected_frame_name)
        return json.dumps(
            {
                "frame_name": selected_frame_name,
                "profile_name": selected_profile.name,
                "profile_version": selected_profile.version,
                "helper_names": selected_profile.list_helper_object_names(),
                "viewer": json.loads(
                    self.describe_viewer_class_surface_ast_json(
                        include_private=include_private,
                        include_dunder=include_dunder,
                    )
                ),
                "profile": json.loads(
                    selected_profile.describe_class_surface_ast_json(
                        include_private=include_private,
                        include_dunder=include_dunder,
                    )
                ),
                "helpers": json.loads(
                    selected_profile.describe_helper_class_surfaces_ast_json(
                        include_private=include_private,
                        include_dunder=include_dunder,
                    )
                ),
            },
            separators=(",", ":"),
        )

    def register_active_profile(self, profile: FrameViewerProfile) -> None:
        """
        Register or replace one reusable viewer profile template.

        Purpose:
            Add a reusable profile template to the viewer host and refresh any
            currently selected frame bindings that pointed at the same profile
            name.

        Args:
            profile:
                Reusable viewer profile template to register.

        Returns:
            None.

        Raises:
            TypeError:
                Raised when `profile` is not a `FrameViewerProfile`.
        """
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
        """
        Select the default reusable profile template for the viewer host.

        Purpose:
            Change the viewer's default profile template and immediately rebind
            the current default frame to that same profile name.

        Args:
            profile_name:
                Registered reusable profile name.

        Returns:
            None.

        Raises:
            ValueError:
                Raised when `profile_name` is empty or unregistered.
        """
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
        """
        Return whether the default reusable profile exposes one method name.

        Args:
            helper_name:
                Exposed profile-method name to inspect.

        Returns:
            bool: True when the default profile exposes the method.
        """
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
        if self._rift_gate is None:
            return handler(**kwargs)
        self._rift_gate.admit()
        self._rift_gate.register_ticket()
        try:
            return handler(**kwargs)
        finally:
            self._rift_gate.unregister_ticket()

    def get_required_active_profile(self, profile_name: str) -> FrameViewerProfile:
        """
        Return one registered reusable profile template or raise.

        Args:
            profile_name:
                Registered reusable profile name.

        Returns:
            FrameViewerProfile: Reusable profile template.

        Raises:
            ValueError:
                Raised when `profile_name` is empty or unregistered.
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
        Resolve one profile-method handler against the bound profile first, then
        the viewer host.

        Args:
            selected_profile:
                Bound selected profile for the current frame.
            handler_name:
                Profile-method handler name or dotted helper path.
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
                Method name or dotted helper path.

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

    def _get_required_selected_frame_name(
            self,
            frame_name: Optional[str] = None,
    ) -> str:
        """
        Return the requested or default selected frame name.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            str: Selected hosted frame name.
        """
        if frame_name is not None:
            if not frame_name:
                raise ValueError("frame_name cannot be empty.")
            self._get_required_frame_descriptor(frame_name)
            return frame_name
        return self._get_required_default_frame_name()

    def _get_required_selected_profile(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> FrameViewerProfile:
        """
        Return the selected bound profile for the requested frame context.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            FrameViewerProfile: Selected bound profile for the frame.
        """
        selected_frame_name = self._get_required_selected_frame_name(frame_name)
        return self.get_selected_profile_for_frame(selected_frame_name)

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

    def _get_frame_names_for_query(
            self,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the hosted frame names participating in one host query.

        Purpose:
            Normalize one optional frame filter into the deterministic set of
            frame names a multi-descriptor host query should inspect.

        Args:
            frame_name:
                Optional hosted frame name. When provided, only that frame is
                returned after validation.

        Returns:
            Tuple[str, ...]: Deterministic hosted frame names for the query.
        """
        self.check_cleaned()
        if frame_name is not None:
            if not frame_name:
                raise ValueError("frame_name cannot be empty.")
            self._get_required_frame_descriptor(frame_name)
            return (frame_name,)
        return tuple(self.list_frame_names())

    def _iter_conduit_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Iterator[object]:
        """
        Yield conduit records in deterministic hosted order.

        Purpose:
            Provide one internal iteration path for descriptor-host conduit
            queries without duplicating record traversal logic.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, yields conduit
                records across all hosted frames.

        Yields:
            ConduitRecord-like objects in deterministic order.
        """
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            for conduit_id in sorted(descriptor.conduit_records_by_id.keys()):
                yield descriptor.conduit_records_by_id[conduit_id]

    def _iter_spell_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Iterator[object]:
        """
        Yield spell records in deterministic hosted order.

        Purpose:
            Provide one internal iteration path for descriptor-host spell
            queries without duplicating record traversal logic.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, yields spell records
                across all hosted frames.

        Yields:
            SpellRecord-like objects in deterministic order.
        """
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            for record_key in sorted(descriptor.spell_records_by_key.keys()):
                yield descriptor.spell_records_by_key[record_key]

    @staticmethod
    def _build_spell_source_id(spell_record: object) -> str:
        """
        Build the published spell source id for one spell record.

        Args:
            spell_record:
                Spell record whose published source id should be derived.

        Returns:
            str: Published spell source id in `spellbook_id:spell_id` form.
        """
        return "{0}:{1}".format(
            spell_record.origin_spellbook_id,
            spell_record.spell_id,
        )

    @staticmethod
    def _normalize_spellframe_value(spellframe: object) -> Optional[str]:
        """
        Return one stable string view of a spellframe value.

        Purpose:
            Normalize the loose `SpellRecord.spellframe` field into a host-safe
            string representation suitable for descriptor-only summaries and
            filters.

        Args:
            spellframe:
                Raw spellframe value from a spell record.

        Returns:
            Optional[str]: Normalized spellframe string when present.
        """
        if spellframe is None:
            return None
        if isinstance(spellframe, str):
            return spellframe
        if isinstance(spellframe, type):
            return spellframe.__name__
        return str(spellframe)

    def _get_required_spell_record(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, object]:
        """
        Return one spell record plus its frame name or raise.

        Purpose:
            Resolve one published spell source id against the hosted
            descriptors while keeping the lookup behavior explicit and
            deterministic.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional hosted frame name to constrain the lookup.

        Returns:
            Tuple[str, object]: `(frame_name, spell_record)` for the resolved
            record.
        """
        if not spell_source_id:
            raise ValueError("spell_source_id cannot be empty.")
        spellbook_id, spell_id = self._parse_spell_source_id(spell_source_id)
        matching_records: List[Tuple[str, object]] = []
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            record = descriptor.spell_records_by_key.get((spellbook_id, spell_id))
            if record is None:
                continue
            matching_records.append((current_frame_name, record))
        if len(matching_records) == 0:
            raise ValueError(
                "Spell source id '{0}' was not found.".format(spell_source_id)
            )
        if len(matching_records) > 1:
            raise ValueError(
                "Spell source id '{0}' is ambiguous across hosted frames.".format(
                    spell_source_id
                )
            )
        return matching_records[0]

    def _get_required_conduit_record(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, object]:
        """
        Return one conduit record plus its frame name or raise.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name to constrain the lookup.

        Returns:
            Tuple[str, object]: `(frame_name, conduit_record)` for the resolved
            record.
        """
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        matching_records: List[Tuple[str, object]] = []
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            record = descriptor.conduit_records_by_id.get(conduit_id)
            if record is None:
                continue
            matching_records.append((current_frame_name, record))
        if len(matching_records) == 0:
            raise ValueError(
                "Conduit id '{0}' was not found.".format(conduit_id)
            )
        if len(matching_records) > 1:
            raise ValueError(
                "Conduit id '{0}' is ambiguous across hosted frames.".format(
                    conduit_id
                )
            )
        return matching_records[0]

    @staticmethod
    def _parse_spell_source_id(spell_source_id: str) -> Tuple[str, str]:
        """
        Parse one published spell source id into its canonical record key.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.

        Returns:
            Tuple[str, str]: `(spellbook_id, spell_id)` key.
        """
        parts = spell_source_id.split(":", 1)
        if len(parts) != 2:
            raise ValueError(
                "spell_source_id '{0}' must be in 'spellbook_id:spell_id' form.".format(
                    spell_source_id
                )
            )
        return parts[0], parts[1]

    @staticmethod
    def _compare_sorted_value_sets(
            left_values: Tuple[str, ...],
            right_values: Tuple[str, ...],
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return one deterministic shared/left-only/right-only value diff.

        Args:
            left_values:
                Left normalized value tuple.
            right_values:
                Right normalized value tuple.

        Returns:
            Dict[str, Tuple[str, ...]]: Shared and directional set deltas.
        """
        left_set = set(left_values)
        right_set = set(right_values)
        return {
            "shared": tuple(sorted(left_set & right_set)),
            "left_only": tuple(sorted(left_set - right_set)),
            "right_only": tuple(sorted(right_set - left_set)),
        }

    def _describe_spell_value_groups(
            self,
            *,
            frame_name: Optional[str],
            value_getter: Callable[[object], Optional[object]],
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Group spell source ids by one normalized spell-record value.

        Args:
            frame_name:
                Optional hosted frame name filter.
            value_getter:
                Callable that extracts the grouping value from one spell
                record.

        Returns:
            Dict[str, Tuple[str, ...]]: Grouping value mapped to spell source
            ids.
        """
        grouped_source_ids_by_value: Dict[str, List[str]] = {}
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            current_value = value_getter(spell_record)
            if current_value is None:
                continue
            grouped_source_ids_by_value.setdefault(
                str(current_value),
                [],
            ).append(self._build_spell_source_id(spell_record))
        return {
            current_value: tuple(sorted(source_ids))
            for current_value, source_ids in grouped_source_ids_by_value.items()
        }

    def _describe_spell_value_collisions(
            self,
            *,
            frame_name: Optional[str],
            value_getter: Callable[[object], Optional[object]],
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return spell value groups that have more than one published member.

        Args:
            frame_name:
                Optional hosted frame name filter.
            value_getter:
                Callable that extracts the grouping value from one spell
                record.

        Returns:
            Dict[str, Tuple[str, ...]]: Colliding value groups only.
        """
        grouped_source_ids_by_value = self._describe_spell_value_groups(
            frame_name=frame_name,
            value_getter=value_getter,
        )
        return {
            current_value: source_ids
            for current_value, source_ids in grouped_source_ids_by_value.items()
            if len(source_ids) > 1
        }

    def _describe_spellbook_mismatches(
            self,
            *,
            frame_name: Optional[str],
            value_getter: Callable[[object], Optional[object]],
    ) -> Dict[str, Dict[str, object]]:
        """
        Return spellbook groups whose selected value is not uniform.

        Args:
            frame_name:
                Optional hosted frame name filter.
            value_getter:
                Callable that extracts the compared value from one spell record.

        Returns:
            Dict[str, Dict[str, object]]: Spellbook mismatch summaries.
        """
        grouped_records_by_spellbook_id: Dict[str, List[object]] = {}
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            grouped_records_by_spellbook_id.setdefault(
                spell_record.origin_spellbook_id,
                [],
            ).append(spell_record)
        mismatches_by_spellbook_id: Dict[str, Dict[str, object]] = {}
        for spellbook_id, spell_records in grouped_records_by_spellbook_id.items():
            current_values = {
                str(value_getter(spell_record))
                for spell_record in spell_records
                if value_getter(spell_record) is not None
            }
            if len(current_values) <= 1:
                continue
            mismatches_by_spellbook_id[spellbook_id] = {
                "source_ids": tuple(
                    sorted(
                        self._build_spell_source_id(spell_record)
                        for spell_record in spell_records
                    )
                ),
                "values": tuple(sorted(current_values)),
            }
        return mismatches_by_spellbook_id

    @staticmethod
    def _normalize_policy_name(policy: object) -> Optional[str]:
        """
        Return one stable string view of a conduit policy value.

        Args:
            policy:
                Raw conduit policy value.

        Returns:
            Optional[str]: Normalized conduit policy name when present.
        """
        if policy is None:
            return None
        return policy.name

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
        """
        Return a detached compiled ACL surface clone for viewer-owned state.

        Contract:
            - Preserves both visibility and command-enablement fields so cloned
              viewers do not silently lose command ACL state.
            - Copies detached mapping data through the public access-surface
              properties.

        Args:
            compiled_access_surface:
                Source compiled ACL access surface to clone.

        Returns:
            CompiledFrameACLAccessSurface: Detached compiled ACL surface copy.
        """
        return CompiledFrameACLAccessSurface(
            frame_name=compiled_access_surface.frame_name,
            configuration_id=compiled_access_surface.configuration_id,
            view_profile_name=compiled_access_surface.view_profile_name,
            view_profile_version=compiled_access_surface.view_profile_version,
            codegen_profile_name=compiled_access_surface.codegen_profile_name,
            codegen_profile_version=compiled_access_surface.codegen_profile_version,
            command_frame_enabled=compiled_access_surface.command_frame_enabled,
            allowed_kinds=compiled_access_surface.allowed_kinds,
            allowed_commands=compiled_access_surface.allowed_commands,
            frame_payload_fields=compiled_access_surface.frame_payload_fields,
            visible_conduit_ids=compiled_access_surface.visible_conduit_ids,
            visible_spell_keys=compiled_access_surface.visible_spell_keys,
            visible_spell_index_ids=compiled_access_surface.visible_spell_index_ids,
            enabled_conduit_ids=compiled_access_surface.enabled_conduit_ids,
            enabled_spell_index_ids=compiled_access_surface.enabled_spell_index_ids,
            conduit_payload_sections_by_id=(
                compiled_access_surface.conduit_payload_sections_by_id
            ),
            spell_payload_sections_by_key=(
                compiled_access_surface.spell_payload_sections_by_key
            ),
            metadata=compiled_access_surface.metadata,
        )
