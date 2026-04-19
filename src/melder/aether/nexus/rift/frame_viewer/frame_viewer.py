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
from melder.aether.nexus.rift.projection.codegen_projection import CodegenProjection
from melder.aether.nexus.rift.projection.command_projection import CommandProjection
from melder.aether.nexus.rift.projection.frame_projection_set import FrameProjectionSet
from melder.aether.nexus.rift.projection.view_projection import ViewProjection
from melder.aether.nexus.rift.frame_viewer.view_conduit import (
    GeneralViewConduit,
)
from melder.aether.nexus.rift.frame_viewer.view_frame import (
    GeneralViewFrame,
)
from melder.aether.nexus.rift.frame_viewer.view_spell import (
    GeneralViewSpell,
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
        Hold one durable viewer asset that reads current frame truth from the
        Rift-owned projection bundle plus the shipped general helper surface
        used to inspect that state.

    Contract:
        - Holds the current per-frame `FrameProjectionSet` references keyed by
          frame name.
        - Treats descriptor/config/surface state as projection-owned, not
          viewer-owned.
        - Owns the shipped `general` viewer feature surface directly.
        - Owns one small per-frame helper cache for the `general`
          view/frame/conduit/spell surfaces.
        - Exposes descriptor-only multi-frame host methods directly on the
          viewer.
        - Exposes frame-local ACL/payload-aware behavior through the viewer's
          internal helper surfaces without a separate profile layer.
        - Does not expose raw runtime objects or any direct code-execution
          behavior.

    Threading:
        Uses one instance `threading.RLock` to serialize cleanup and multi-step
        helper/cache mutations.

    Lifecycle:
        Cleanup cascades into the viewer-owned helper cache before clearing
        viewer-owned maps and metadata.
    """

    __melder_internal__ = _mrg.sentinel
    _ast_helper_access: str = "public"
    __agent_purpose__: str = (
        "access: public. Multi-frame descriptor host and defaulted shipped "
        "general viewer surface for the Rift viewer path. Use this object to inspect hosted "
        "frames, compare descriptor records, and reach the built-in helper "
        "surface for frame-local methods."
    )
    _SURFACE_NAME: str = "general"
    _SURFACE_VERSION: str = "0.0.1"
    _DEFAULT_GROUPING: str = "frame"
    _DEFAULT_DETAIL_LEVEL: str = "detailed"
    _TOOL_HANDLER_NAMES_BY_NAME: Dict[str, str] = {
        "list_frames": "list_frame_names",
        "list_frame_ids": "list_frame_ids",
        "describe_viewer": "describe_viewer",
        "describe_current_frame": "describe_current_frame",
        "describe_frames_inventory": "describe_frames_inventory",
        "list_nexus_contracts": "list_nexus_contracts",
        "describe_frame_brief": "describe_frame_brief",
        "describe_host_inventory": "describe_host_inventory",
        "compare_frames_brief": "compare_frames_brief",
        "describe_viewer_method_surface": "describe_viewer_method_surface",
        "describe_agent_onboarding_json": "describe_agent_onboarding_json",
        "describe_viewer_agent_purpose_json": "describe_viewer_agent_purpose_json",
        "list_viewer_method_names_ast_json": "list_viewer_method_names_ast_json",
        "describe_viewer_class_surface_ast_json": "describe_viewer_class_surface_ast_json",
        "describe_frame": "describe_frame",
        "describe_frames": "describe_frames",
        "count_frames": "count_frames",
        "count_conduit_records": "count_conduit_records",
        "count_root_conduits": "count_root_conduits",
        "count_spell_records": "count_spell_records",
        "count_spellbooks": "count_spellbooks",
        "list_conduit_record_ids": "list_conduit_record_ids",
        "list_root_conduit_ids": "list_root_conduit_ids",
        "list_origin_spellbook_ids": "list_origin_spellbook_ids",
        "list_spell_record_ids": "list_spell_record_ids",
        "list_spell_record_keys": "list_spell_record_keys",
        "list_spell_names": "list_spell_names",
        "list_binding_names": "list_binding_names",
        "list_lineage_ids": "list_lineage_ids",
        "list_spellframes": "list_spellframes",
        "list_permissions": "list_permissions",
        "list_existence_kinds": "list_existence_kinds",
        "describe_descriptor_inventory": "describe_descriptor_inventory",
        "describe_descriptor_topology": "describe_descriptor_topology",
        "describe_conduit_records": "describe_conduit_records",
        "describe_spell_records": "describe_spell_records",
        "describe_spell_record": "describe_spell_record",
        "list_spells_by_owner_conduit_record": "list_spells_by_owner_conduit",
        "list_spells_by_spellbook_id_record": "list_spells_by_spellbook_id",
        "list_spells_by_permission_record": "list_spells_by_permission",
        "list_spells_by_existence_record": "list_spells_by_existence",
        "list_spells_by_spellframe_record": "list_spells_by_spellframe",
        "compare_frames": "compare_frames",
        "compare_frame_conduits": "compare_frame_conduits",
        "compare_frame_spells": "compare_frame_spells",
        "describe_binding_name_collisions": "describe_binding_name_collisions",
        "describe_spell_name_collisions": "describe_spell_name_collisions",
        "describe_lineage_groups": "describe_lineage_groups",
        "describe_spellframe_groups": "describe_spellframe_groups",
        "describe_spellbook_permission_mismatches": "describe_spellbook_permission_mismatches",
        "describe_spellbook_existence_mismatches": "describe_spellbook_existence_mismatches",
        "compare_spell_records": "compare_spell_records",
        "compare_conduit_records": "compare_conduit_records",
        "describe_visible_surface": "view_frame.describe_visible_surface",
        "describe_missing_surface": "view_frame.describe_missing_surface",
        "describe_frame_brief_local": "view_frame.describe_frame_brief",
        "describe_visible_inventory_by_kind": "view_frame.describe_visible_inventory_by_kind",
        "describe_frame_topology": "view_frame.describe_frame_topology",
        "list_visible_target_ids": "view_frame.list_visible_target_ids",
        "list_visible_target_ids_by_kind": "view_frame.list_visible_target_ids_by_kind",
        "list_visible_conduit_ids": "view_frame.list_visible_conduit_ids",
        "list_visible_spell_source_ids": "view_frame.list_visible_spell_source_ids",
        "list_visible_root_conduits": "view_frame.list_visible_root_conduits",
        "list_visible_binding_names": "view_frame.list_visible_binding_names",
        "list_visible_spell_names": "view_frame.list_visible_spell_names",
        "list_visible_spellframes": "view_frame.list_visible_spellframes",
        "list_visible_lineage_ids": "view_frame.list_visible_lineage_ids",
        "describe_visible_spell_ownership": "view_frame.describe_visible_spell_ownership",
        "describe_visible_conduit_tree": "view_frame.describe_visible_conduit_tree",
        "search_targets_contains": "view_frame.search_targets_contains",
        "search_targets_prefix": "view_frame.search_targets_prefix",
        "group_targets_by_kind": "view_frame.group_targets_by_kind",
        "describe_target_brief": "view_frame.describe_target_brief",
        "describe_target_identity": "view_frame.describe_target_identity",
        "describe_visible_collisions": "view_frame.describe_visible_collisions",
        "describe_frame_payload": "view_frame.describe_frame_payload",
        "describe_frame_inventory": "view_frame.describe_frame_inventory",
        "describe_frame_access_contract": "view_frame.describe_frame_access_contract",
        "get_frame_payload_field": "view_frame.get_frame_payload_field",
        "find_target_by_display_name": "view_frame.find_target_by_display_name",
        "explain_target_access": "view_frame.explain_target_access",
        "list_targets": "view_frame.list_targets",
        "describe_targets": "view_frame.describe_targets",
        "list_conduits": "view_conduit.list_conduits",
        "list_root_conduits": "view_conduit.list_root_conduits",
        "describe_conduits": "view_conduit.describe_conduits",
        "get_conduit": "view_conduit.get_required_conduit",
        "describe_conduit": "view_conduit.describe_conduit",
        "describe_conduit_brief": "view_conduit.describe_conduit_brief",
        "describe_conduit_inventory": "view_conduit.describe_conduit_inventory",
        "describe_conduit_relationships": "view_conduit.describe_conduit_relationships",
        "describe_conduit_missing_sections": "view_conduit.describe_conduit_missing_sections",
        "describe_conduit_crosswalk": "view_conduit.describe_conduit_crosswalk",
        "list_conduit_spells": "view_conduit.list_conduit_spells",
        "describe_conduit_topology": "view_conduit.describe_conduit_topology",
        "compare_conduits": "view_conduit.compare_conduits",
        "is_root_conduit": "view_conduit.is_root_conduit",
        "get_root_conduit_id": "view_conduit.get_root_conduit_id",
        "list_conduits_by_root_id": "view_conduit.list_conduits_by_root_id",
        "list_conduits_by_policy": "view_conduit.list_conduits_by_policy",
        "list_conduits_by_state": "view_conduit.list_conduits_by_state",
        "list_peer_conduits": "view_conduit.list_peer_conduits",
        "list_child_conduits": "view_conduit.list_child_conduits",
        "list_parent_conduit": "view_conduit.get_parent_conduit_id",
        "describe_root_conduit_inventory": "view_conduit.describe_root_conduit_inventory",
        "list_spells": "view_spell.list_spells",
        "describe_spells": "view_spell.describe_spells",
        "get_spell": "view_spell.get_required_spell",
        "describe_spell": "view_spell.describe_spell",
        "describe_spell_brief": "view_spell.describe_spell_brief",
        "describe_spell_inventory": "view_spell.describe_spell_inventory",
        "describe_spell_origin": "view_spell.describe_spell_origin",
        "describe_spell_lineage": "view_spell.describe_spell_lineage",
        "describe_spell_payload": "view_spell.describe_spell_payload",
        "describe_spell_methods": "view_spell.describe_spell_methods",
        "describe_spell_attributes": "view_spell.describe_spell_attributes",
        "describe_spell_dunder_surface": "view_spell.describe_spell_dunder_surface",
        "describe_spell_missing_sections": "view_spell.describe_spell_missing_sections",
        "describe_spell_crosswalk": "view_spell.describe_spell_crosswalk",
        "compare_spells": "view_spell.compare_spells",
        "list_spells_by_owner_conduit": "view_spell.list_spells_by_owner_conduit",
        "list_spells_by_spellbook_id": "view_spell.list_spells_by_spellbook_id",
        "list_spells_by_permission": "view_spell.list_spells_by_permission",
        "list_spells_by_existence": "view_spell.list_spells_by_existence",
        "list_spells_by_spellframe": "view_spell.list_spells_by_spellframe",
    }
    __slots__ = Cleanable.__slots__ + [
        "_viewer_id",
        "_lock",
        "_projection_sets_by_frame_name",
        "_helper_surfaces_by_frame_name",
        "_default_view_frame_name",
        "_rift_gate",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            projection_sets_by_frame_name: Optional[Dict[str, FrameProjectionSet]] = None,
            default_view_frame_name: Optional[str] = None,
            rift_gate: Optional[IRiftGate] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one descriptor-driven frame viewer.

        Args:
            projection_sets_by_frame_name:
                Optional borrowed projection bundles keyed by frame name.
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
        self._projection_sets_by_frame_name: Dict[str, FrameProjectionSet] = dict(
            projection_sets_by_frame_name or {}
        )
        if default_view_frame_name is not None:
            if not default_view_frame_name:
                raise ValueError("default_view_frame_name cannot be empty.")
            if default_view_frame_name not in self._projection_sets_by_frame_name:
                raise ValueError(
                    "default_view_frame_name must be present in projection_sets_by_frame_name."
                )
        self._default_view_frame_name: Optional[str] = (
            default_view_frame_name
            if default_view_frame_name is not None
            else (
                next(iter(self._projection_sets_by_frame_name.keys()))
                if len(self._projection_sets_by_frame_name) > 0
                else None
            )
        )
        self._rift_gate: Optional[IRiftGate] = rift_gate
        self._helper_surfaces_by_frame_name: Dict[
            str,
            Tuple[GeneralViewFrame, GeneralViewConduit, GeneralViewSpell],
        ] = {}
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
            self._clear_helper_cache()
            self._projection_sets_by_frame_name.clear()
            self._metadata.clear()
            self._projection_sets_by_frame_name = None
            self._helper_surfaces_by_frame_name = None
            self._default_view_frame_name = None
            self._rift_gate = None
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
            return {
                frame_name: projection_set.view_projection.frame_descriptor
                for frame_name, projection_set in self._projection_sets_by_frame_name.items()
            }

    @property
    def compiled_access_surfaces_by_frame_name(
            self,
    ) -> Dict[str, CompiledFrameACLAccessSurface]:
        self.check_cleaned()
        with self._lock:
            return {
                frame_name: projection_set.view_projection.compiled_access_surface
                for frame_name, projection_set in self._projection_sets_by_frame_name.items()
            }

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
            return {
                frame_name: projection_set.view_projection.frame_acl_configuration
                for frame_name, projection_set in self._projection_sets_by_frame_name.items()
            }

    @property
    def default_view_frame_name(self) -> Optional[str]:
        self.check_cleaned()
        return self._default_view_frame_name

    @property
    def surface_name(self) -> str:
        self.check_cleaned()
        return self._SURFACE_NAME

    @property
    def surface_version(self) -> str:
        self.check_cleaned()
        return self._SURFACE_VERSION

    @property
    def enabled_helpers(self) -> Tuple[str, ...]:
        self.check_cleaned()
        return tuple(self._TOOL_HANDLER_NAMES_BY_NAME.keys())

    @property
    def default_grouping(self) -> str:
        self.check_cleaned()
        return self._DEFAULT_GROUPING

    @property
    def default_detail_level(self) -> str:
        self.check_cleaned()
        return self._DEFAULT_DETAIL_LEVEL

    @property
    def tool_handler_names_by_name(self) -> Dict[str, str]:
        self.check_cleaned()
        return dict(self._TOOL_HANDLER_NAMES_BY_NAME)

    @property
    def metadata(self) -> Dict[str, object]:
        self.check_cleaned()
        with self._lock:
            return dict(self._metadata)

    def sync_from_projection_sets(
            self,
            projection_sets_by_frame_name: Dict[str, FrameProjectionSet],
            *,
            default_view_frame_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Synchronize hosted frame state in place from room-owned projections.

        Purpose:
            Let one durable viewer asset stay alive while the owning room
            updates its current frame targets and compiled access state.

        Contract:
            - Accepts an empty projection-set map and leaves the viewer valid.
            - Stores only borrowed `FrameProjectionSet` references from the
              owning Rift instead of cloning descriptor/config/surface state
              into a second median layer.
            - Supports only the shipped `general` viewer surface.
            - Preserves the current default frame when it still exists and no
              explicit default override is provided.
            - Clears the helper cache so later calls bind against the
              refreshed projection-owned state.

        Args:
            projection_sets_by_frame_name:
                Current room-owned projection sets keyed by frame name.
            default_view_frame_name:
                Optional explicit default hosted frame name.
            metadata:
                Optional replacement viewer metadata payload.

        Returns:
            None.

        Raises:
            ValueError:
                If `default_view_frame_name` is not hosted by the refreshed
                viewer state.
        """
        self.check_cleaned()
        normalized_projection_sets_by_frame_name = dict(projection_sets_by_frame_name)
        refreshed_frame_names = tuple(normalized_projection_sets_by_frame_name.keys())
        with self._lock:
            previous_default_view_frame_name = self._default_view_frame_name
            refreshed_default_view_frame_name = self._resolve_synced_default_view_frame_name(
                refreshed_frame_names,
                requested_default_view_frame_name=default_view_frame_name,
                previous_default_view_frame_name=previous_default_view_frame_name,
            )
            self._cleanup_hosted_frame_state()
            self._projection_sets_by_frame_name = normalized_projection_sets_by_frame_name
            self._default_view_frame_name = refreshed_default_view_frame_name
            self._metadata = dict(metadata) if metadata is not None else {}

    def _cleanup_hosted_frame_state(self) -> None:
        """
        Cleanup and clear the hosted frame-specific viewer snapshot state.

        Purpose:
            Support in-place viewer synchronization without recreating the
            viewer asset itself.

        Returns:
            None.
        """
        self._clear_helper_cache()
        self._projection_sets_by_frame_name.clear()

    def _clear_helper_cache(self) -> None:
        """
        Cleanup and clear the helper cache.

        Returns:
            None.
        """
        for helper_bundle in self._helper_surfaces_by_frame_name.values():
            for helper in helper_bundle:
                helper.cleanup()
        self._helper_surfaces_by_frame_name.clear()

    @staticmethod
    def _resolve_synced_default_view_frame_name(
            refreshed_frame_names: Tuple[str, ...],
            *,
            requested_default_view_frame_name: Optional[str],
            previous_default_view_frame_name: Optional[str],
    ) -> Optional[str]:
        """
        Resolve the default hosted frame after one sync operation.

        Args:
            refreshed_frame_names:
                Hosted frame names after the sync.
            requested_default_view_frame_name:
                Optional explicit default frame override.
            previous_default_view_frame_name:
                Current default frame before sync.

        Returns:
            Optional[str]: Default frame name after sync, or None when no
            frames are hosted.

        Raises:
            ValueError:
                If the explicit requested default frame is empty or not hosted
                by the refreshed frame set.
        """
        if requested_default_view_frame_name is not None:
            if not requested_default_view_frame_name:
                raise ValueError("default_view_frame_name cannot be empty.")
            if requested_default_view_frame_name not in refreshed_frame_names:
                raise ValueError(
                    "default_view_frame_name must be present in synced frame names."
                )
            return requested_default_view_frame_name
        if previous_default_view_frame_name in refreshed_frame_names:
            return previous_default_view_frame_name
        if len(refreshed_frame_names) == 0:
            return None
        return refreshed_frame_names[0]

    def list_frame_names(self) -> List[str]:
        """
        Return the hosted frame names in deterministic order.

        Returns:
            List[str]: Sorted hosted frame names.
        """
        self.check_cleaned()
        with self._lock:
            return list(sorted(self._projection_sets_by_frame_name.keys()))

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
            if frame_name not in self._projection_sets_by_frame_name:
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
            "surface_name": self.surface_name,
            "surface_version": self.surface_version,
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

    def clone(self) -> "FrameViewer":
        """
        Return a detached copy of the viewer host.

        Purpose:
            Preserve the non-owned projection-set references and metadata while
            starting with an empty helper cache in the clone.

        Returns:
            FrameViewer: Detached viewer clone.
        """
        self.check_cleaned()
        with self._lock:
            return FrameViewer(
                projection_sets_by_frame_name=dict(self._projection_sets_by_frame_name),
                default_view_frame_name=self._default_view_frame_name,
                rift_gate=self._rift_gate,
                metadata=dict(self._metadata),
            )

    def list_enabled_helpers(self) -> Tuple[str, ...]:
        """
        Return the exposed method names for the shipped viewer surface.

        Returns:
            Tuple[str, ...]: Exposed method names for the shipped viewer surface.
        """
        self.check_cleaned()
        return self.enabled_helpers

    def list_available_tools(self) -> Tuple[str, ...]:
        """
        Return the exposed viewer-surface method names.

        Returns:
            Tuple[str, ...]: Exposed viewer-surface method names.
        """
        self.check_cleaned()
        return tuple(self._TOOL_HANDLER_NAMES_BY_NAME.keys())

    def get_view_frame(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> GeneralViewFrame:
        """
        Return the viewer-owned frame helper for one hosted frame.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, the default frame is used.

        Returns:
            GeneralViewFrame: Bound frame helper.
        """
        return self._get_helper_surface_bundle(frame_name=frame_name)[0]

    def get_view_conduit(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> GeneralViewConduit:
        """
        Return the viewer-owned conduit helper for one hosted frame.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, the default frame is used.

        Returns:
            GeneralViewConduit: Bound conduit helper.
        """
        return self._get_helper_surface_bundle(frame_name=frame_name)[1]

    def get_view_spell(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> GeneralViewSpell:
        """
        Return the viewer-owned spell helper for one hosted frame.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, the default frame is used.

        Returns:
            GeneralViewSpell: Bound spell helper.
        """
        return self._get_helper_surface_bundle(frame_name=frame_name)[2]

    @property
    def view_frame(self) -> GeneralViewFrame:
        """Return the frame helper for the current default frame."""
        return self.get_view_frame()

    @property
    def view_conduit(self) -> GeneralViewConduit:
        """Return the conduit helper for the current default frame."""
        return self.get_view_conduit()

    @property
    def view_spell(self) -> GeneralViewSpell:
        """Return the spell helper for the current default frame."""
        return self.get_view_spell()

    def list_frames(self, *args, **kwargs) -> Any:
        """Direct facade for `list_frame_names` on the shipped viewer surface."""
        return self.list_frame_names(*args, **kwargs)

    def list_spells_by_owner_conduit_record(self, *args, **kwargs) -> Any:
        """Direct facade for `list_spells_by_owner_conduit` on the shipped viewer surface."""
        return self.list_spells_by_owner_conduit(*args, **kwargs)

    def list_spells_by_spellbook_id_record(self, *args, **kwargs) -> Any:
        """Direct facade for `list_spells_by_spellbook_id` on the shipped viewer surface."""
        return self.list_spells_by_spellbook_id(*args, **kwargs)

    def list_spells_by_permission_record(self, *args, **kwargs) -> Any:
        """Direct facade for `list_spells_by_permission` on the shipped viewer surface."""
        return self.list_spells_by_permission(*args, **kwargs)

    def list_spells_by_existence_record(self, *args, **kwargs) -> Any:
        """Direct facade for `list_spells_by_existence` on the shipped viewer surface."""
        return self.list_spells_by_existence(*args, **kwargs)

    def list_spells_by_spellframe_record(self, *args, **kwargs) -> Any:
        """Direct facade for `list_spells_by_spellframe` on the shipped viewer surface."""
        return self.list_spells_by_spellframe(*args, **kwargs)

    def describe_visible_surface(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.describe_visible_surface` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_visible_surface(*args, **kwargs)

    def describe_missing_surface(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.describe_missing_surface` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_missing_surface(*args, **kwargs)

    def describe_frame_brief_local(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.describe_frame_brief` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_frame_brief(*args, **kwargs)

    def describe_visible_inventory_by_kind(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.describe_visible_inventory_by_kind` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_visible_inventory_by_kind(*args, **kwargs)

    def describe_frame_topology(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.describe_frame_topology` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_frame_topology(*args, **kwargs)

    def list_visible_target_ids(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.list_visible_target_ids` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_target_ids(*args, **kwargs)

    def list_visible_target_ids_by_kind(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.list_visible_target_ids_by_kind` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_target_ids_by_kind(*args, **kwargs)

    def list_visible_conduit_ids(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.list_visible_conduit_ids` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_conduit_ids(*args, **kwargs)

    def list_visible_spell_source_ids(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.list_visible_spell_source_ids` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_spell_source_ids(*args, **kwargs)

    def list_visible_root_conduits(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.list_visible_root_conduits` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_root_conduits(*args, **kwargs)

    def list_visible_binding_names(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.list_visible_binding_names` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_binding_names(*args, **kwargs)

    def list_visible_spell_names(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.list_visible_spell_names` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_spell_names(*args, **kwargs)

    def list_visible_spellframes(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.list_visible_spellframes` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_spellframes(*args, **kwargs)

    def list_visible_lineage_ids(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.list_visible_lineage_ids` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_lineage_ids(*args, **kwargs)

    def describe_visible_spell_ownership(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.describe_visible_spell_ownership` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_visible_spell_ownership(*args, **kwargs)

    def describe_visible_conduit_tree(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.describe_visible_conduit_tree` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_visible_conduit_tree(*args, **kwargs)

    def search_targets_contains(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.search_targets_contains` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).search_targets_contains(*args, **kwargs)

    def search_targets_prefix(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.search_targets_prefix` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).search_targets_prefix(*args, **kwargs)

    def group_targets_by_kind(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.group_targets_by_kind` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).group_targets_by_kind(*args, **kwargs)

    def describe_target_brief(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.describe_target_brief` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_target_brief(*args, **kwargs)

    def describe_target_identity(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.describe_target_identity` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_target_identity(*args, **kwargs)

    def describe_visible_collisions(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.describe_visible_collisions` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_visible_collisions(*args, **kwargs)

    def describe_frame_payload(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.describe_frame_payload` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_frame_payload(*args, **kwargs)

    def describe_frame_inventory(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.describe_frame_inventory` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_frame_inventory(*args, **kwargs)

    def describe_frame_access_contract(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.describe_frame_access_contract` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_frame_access_contract(*args, **kwargs)

    def get_frame_payload_field(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.get_frame_payload_field` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).get_frame_payload_field(*args, **kwargs)

    def find_target_by_display_name(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.find_target_by_display_name` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).find_target_by_display_name(*args, **kwargs)

    def explain_target_access(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.explain_target_access` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).explain_target_access(*args, **kwargs)

    def list_targets(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.list_targets` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_targets(*args, **kwargs)

    def describe_targets(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_frame.describe_targets` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_targets(*args, **kwargs)

    def list_conduits(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.list_conduits` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_conduits(*args, **kwargs)

    def list_root_conduits(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.list_root_conduits` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_root_conduits(*args, **kwargs)

    def describe_conduits(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.describe_conduits` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduits(*args, **kwargs)

    def get_conduit(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.get_required_conduit` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).get_required_conduit(*args, **kwargs)

    def describe_conduit(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.describe_conduit` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduit(*args, **kwargs)

    def describe_conduit_brief(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.describe_conduit_brief` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_brief(*args, **kwargs)

    def describe_conduit_inventory(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.describe_conduit_inventory` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_inventory(*args, **kwargs)

    def describe_conduit_relationships(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.describe_conduit_relationships` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_relationships(*args, **kwargs)

    def describe_conduit_missing_sections(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.describe_conduit_missing_sections` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_missing_sections(*args, **kwargs)

    def describe_conduit_crosswalk(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.describe_conduit_crosswalk` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_crosswalk(*args, **kwargs)

    def list_conduit_spells(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.list_conduit_spells` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_conduit_spells(*args, **kwargs)

    def describe_conduit_topology(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.describe_conduit_topology` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_topology(*args, **kwargs)

    def compare_conduits(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.compare_conduits` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).compare_conduits(*args, **kwargs)

    def is_root_conduit(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.is_root_conduit` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).is_root_conduit(*args, **kwargs)

    def get_root_conduit_id(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.get_root_conduit_id` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).get_root_conduit_id(*args, **kwargs)

    def list_conduits_by_root_id(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.list_conduits_by_root_id` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_conduits_by_root_id(*args, **kwargs)

    def list_conduits_by_policy(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.list_conduits_by_policy` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_conduits_by_policy(*args, **kwargs)

    def list_conduits_by_state(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.list_conduits_by_state` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_conduits_by_state(*args, **kwargs)

    def list_peer_conduits(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.list_peer_conduits` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_peer_conduits(*args, **kwargs)

    def list_child_conduits(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.list_child_conduits` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_child_conduits(*args, **kwargs)

    def list_parent_conduit(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.get_parent_conduit_id` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).get_parent_conduit_id(*args, **kwargs)

    def describe_root_conduit_inventory(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_conduit.describe_root_conduit_inventory` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_root_conduit_inventory(*args, **kwargs)

    def list_spells(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.list_spells` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).list_spells(*args, **kwargs)

    def describe_spells(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.describe_spells` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spells(*args, **kwargs)

    def get_spell(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.get_required_spell` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).get_required_spell(*args, **kwargs)

    def describe_spell(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.describe_spell` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell(*args, **kwargs)

    def describe_spell_brief(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.describe_spell_brief` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_brief(*args, **kwargs)

    def describe_spell_inventory(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.describe_spell_inventory` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_inventory(*args, **kwargs)

    def describe_spell_origin(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.describe_spell_origin` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_origin(*args, **kwargs)

    def describe_spell_lineage(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.describe_spell_lineage` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_lineage(*args, **kwargs)

    def describe_spell_payload(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.describe_spell_payload` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_payload(*args, **kwargs)

    def describe_spell_methods(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.describe_spell_methods` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_methods(*args, **kwargs)

    def describe_spell_attributes(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.describe_spell_attributes` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_attributes(*args, **kwargs)

    def describe_spell_dunder_surface(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.describe_spell_dunder_surface` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_dunder_surface(*args, **kwargs)

    def describe_spell_missing_sections(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.describe_spell_missing_sections` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_missing_sections(*args, **kwargs)

    def describe_spell_crosswalk(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.describe_spell_crosswalk` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_crosswalk(*args, **kwargs)

    def compare_spells(self, *args, frame_name: Optional[str] = None, **kwargs) -> Any:
        """Direct facade for `view_spell.compare_spells` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).compare_spells(*args, **kwargs)

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

    def has_enabled_helper(self, helper_name: str) -> bool:
        """
        Return whether the shipped viewer surface exposes one method name.

        Args:
            helper_name:
                Exposed viewer method name to inspect.

        Returns:
            bool: True when the shipped viewer surface exposes the method.
        """
        self.check_cleaned()
        if not helper_name:
            raise ValueError("helper_name cannot be empty.")
        return helper_name in self._TOOL_HANDLER_NAMES_BY_NAME

    def execute_method(
            self,
            method_name: str,
            **kwargs,
    ) -> Any:
        """
        Execute one shipped viewer-surface method for the target frame context.

        Args:
            method_name:
                Exposed viewer method name to execute.
            **kwargs:
                Arguments forwarded to the resolved handler.

        Raises:
            ValueError:
                Raised when `method_name` is empty or when the mapped handler
                cannot be resolved.
        """
        self.check_cleaned()
        if not method_name:
            raise ValueError("method_name cannot be empty.")
        handler_name = self._TOOL_HANDLER_NAMES_BY_NAME.get(method_name)
        if not handler_name:
            raise ValueError(
                "FrameViewer surface method '{0}' was not found.".format(method_name)
            )
        selected_frame_name = kwargs.get("frame_name")
        handler = self._resolve_tool_handler(
            handler_name,
            frame_name=selected_frame_name,
        )
        if handler is None or not callable(handler):
            raise ValueError(
                "FrameViewer surface method '{0}' targets missing handler '{1}'.".format(
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

    def _resolve_tool_handler(
            self,
            handler_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Resolve one viewer-surface handler.

        Args:
            handler_name:
                Host method name or dotted helper-path target.
            frame_name:
                Optional hosted frame name for helper-surface methods.

        Returns:
            Optional[Any]: Resolved callable when found.
        """
        if "." not in handler_name:
            return getattr(self, handler_name, None)
        helper_name, method_name = handler_name.split(".", 1)
        if helper_name == "view_frame":
            return getattr(self.get_view_frame(frame_name=frame_name), method_name, None)
        if helper_name == "view_conduit":
            return getattr(
                self.get_view_conduit(frame_name=frame_name),
                method_name,
                None,
            )
        if helper_name == "view_spell":
            return getattr(self.get_view_spell(frame_name=frame_name), method_name, None)
        return None

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

    def _get_helper_surface_bundle(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[GeneralViewFrame, GeneralViewConduit, GeneralViewSpell]:
        """
        Return the helper bundle for one hosted frame, creating it on demand.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            Tuple[GeneralViewFrame, GeneralViewConduit, GeneralViewSpell]:
                Helper bundle for the selected frame.
        """
        selected_frame_name = self._get_required_selected_frame_name(frame_name)
        with self._lock:
            cached_bundle = self._helper_surfaces_by_frame_name.get(selected_frame_name)
            if cached_bundle is not None:
                return cached_bundle
            helper_bundle = self._create_helper_surface_bundle_for_frame(
                selected_frame_name
            )
            self._helper_surfaces_by_frame_name[selected_frame_name] = helper_bundle
            return helper_bundle

    def _get_required_frame_descriptor(self, frame_name: str) -> FrameDescriptor:
        return self._get_required_view_projection(frame_name).frame_descriptor

    def _get_required_compiled_access_surface(
            self,
            frame_name: str,
    ) -> CompiledFrameACLAccessSurface:
        projection_set = self._projection_sets_by_frame_name.get(frame_name)
        if projection_set is None:
            raise ValueError(
                "Compiled access surface for frame '{0}' was not found.".format(
                    frame_name
                )
            )
        return projection_set.view_projection.compiled_access_surface

    def _get_required_frame_acl_configuration(
            self,
            frame_name: str,
    ) -> FrameACLConfiguration:
        projection_set = self._projection_sets_by_frame_name.get(frame_name)
        if projection_set is None:
            raise ValueError(
                "Frame ACL configuration for frame '{0}' was not found.".format(
                    frame_name
                )
            )
        return projection_set.view_projection.frame_acl_configuration

    def _get_required_frame_projection_set(
            self,
            frame_name: str,
    ) -> FrameProjectionSet:
        """
        Return one projection set by frame name or raise.

        Returns:
            FrameProjectionSet: Projection bundle for the frame.
        """
        try:
            return self._projection_sets_by_frame_name[frame_name]
        except KeyError as exc:
            raise ValueError(
                "Frame '{0}' was not found.".format(frame_name)
            ) from exc

    def _get_required_view_projection(self, frame_name: str) -> ViewProjection:
        """
        Return one required view projection by frame name.

        Returns:
            ViewProjection: View projection for the frame.
        """
        return self._get_required_frame_projection_set(frame_name).view_projection

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

    def _create_helper_surface_bundle_for_frame(
            self,
            frame_name: str,
    ) -> Tuple[GeneralViewFrame, GeneralViewConduit, GeneralViewSpell]:
        """
        Create one helper bundle for one hosted frame.

        Args:
            frame_name:
                Hosted frame name.

        Returns:
            Tuple[GeneralViewFrame, GeneralViewConduit, GeneralViewSpell]:
                Helper bundle bound to the hosted frame's projection-owned
                descriptor and ACL state.
        """
        view_frame = GeneralViewFrame(
            frame_name=frame_name,
            frame_descriptor=self._get_required_frame_descriptor(frame_name),
            frame_acl_configuration=self._get_required_frame_acl_configuration(
                frame_name
            ),
            compiled_access_surface=self._get_required_compiled_access_surface(
                frame_name
            ),
            default_detail_level=self.default_detail_level,
        )
        view_conduit = GeneralViewConduit(frame_view=view_frame)
        view_spell = GeneralViewSpell(frame_view=view_frame)
        return view_frame, view_conduit, view_spell

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
