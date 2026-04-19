"""
Internal descriptor-driven FrameViewer surface.
"""
import threading
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.rift.projection.frame_projection_set import FrameProjectionSet
from melder.aether.nexus.rift.projection.view_projection import ViewProjection
from melder.aether.nexus.rift.frame_viewer.view_conduit import (
    ViewConduit,
)
from melder.aether.nexus.rift.frame_viewer.view_frame import (
    ViewFrame,
)
from melder.aether.nexus.rift.frame_viewer.view_multiframe import (
    ViewMultiFrame,
)
from melder.aether.nexus.rift.frame_viewer.view_spell import (
    ViewSpell,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.class_surface_ast_describer import (
    ClassSurfaceAstDescriber,
)
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import IFrameLink, IRiftGate


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
          internal helper surfaces without a separate profile layer or generic
          dispatch entrypoint.
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
        "access: public. Multi-frame descriptor host for the Rift viewer path. Use this object to inspect hosted "
        "frames, compare descriptor records, and call the explicit viewer methods for frame-local behavior."
    )
    __slots__ = Cleanable.__slots__ + [
        "_viewer_id",
        "_lock",
        "_projection_sets_by_frame_name",
        "_view_multiframe",
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
        self._view_multiframe: ViewMultiFrame = ViewMultiFrame(
            viewer=self,
        )
        self._helper_surfaces_by_frame_name: Dict[
            str,
            Tuple[ViewFrame, ViewConduit, ViewSpell],
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
            self._view_multiframe.cleanup()
            self._clear_helper_cache()
            self._projection_sets_by_frame_name.clear()
            self._metadata.clear()
            self._projection_sets_by_frame_name = None
            self._view_multiframe = None
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
    def default_grouping(self) -> str:
        self.check_cleaned()
        return "frame"

    @property
    def default_detail_level(self) -> str:
        self.check_cleaned()
        return "detailed"

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
        return self.get_view_multiframe().list_frame_names()

    def count_frames(self) -> int:
        """
        Return the number of hosted frame descriptors.

        Returns:
            int: Hosted frame count.
        """
        self.check_cleaned()
        return self.get_view_multiframe().count_frames()

    def set_default_view(self, frame_name: str) -> None:
        """
        Select the default hosted frame for subsequent host/profile calls.

        Purpose:
            Move the viewer's default frame pointer so host methods and
            frame-local helper execution can fall back to a known frame when
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
        return self.get_view_multiframe().count_root_conduits(frame_name=frame_name)

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
        return self.get_view_multiframe().count_spell_records(frame_name=frame_name)

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
        return self.get_view_multiframe().describe_frame(frame_name)

    def describe_frames(self) -> Dict[str, Dict[str, object]]:
        """
        Return descriptor-level summaries for all hosted frames.

        Returns:
            Dict[str, Dict[str, object]]: Hosted frame summaries keyed by frame
            name.
        """
        self.check_cleaned()
        return self.get_view_multiframe().describe_frames()

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
        return self.get_view_multiframe().describe_frame_brief(frame_name)

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
        return self.get_view_multiframe().describe_host_inventory()

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
        return self.get_view_multiframe().describe_current_frame()

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
        return self.get_view_multiframe().describe_frames_inventory()

    def describe_viewer_method_surface(self) -> Dict[str, object]:
        """
        Return one curated summary of the host-side viewer method surface.

        Purpose:
            Explain how to use the `FrameViewer` host without forcing the
            operator to read the raw AST-described class surface first.

        Contract:
            - Describes only the curated host-side method groups.
            - Keeps the host boundary explicit: descriptor-oriented viewer
              methods on the host, with explicit helper-backed methods exposed
              directly on the viewer surface.

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
            "frame_local_method_entrypoints": (
                "describe_visible_surface",
                "list_targets",
                "describe_conduits",
                "describe_spells",
            ),
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
        return self.get_view_multiframe().compare_frames(left_frame_name, right_frame_name)

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
        return self.get_view_multiframe().compare_frames_brief(left_frame_name, right_frame_name)

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
        return self.get_view_multiframe().compare_frame_conduits(left_frame_name, right_frame_name)

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
        return self.get_view_multiframe().compare_frame_spells(left_frame_name, right_frame_name)

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
        return self.get_view_multiframe().describe_binding_name_collisions(frame_name=frame_name)

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
        return self.get_view_multiframe().describe_spell_name_collisions(frame_name=frame_name)

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
        return self.get_view_multiframe().describe_lineage_groups(frame_name=frame_name)

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
        return self.get_view_multiframe().describe_spellframe_groups(frame_name=frame_name)

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
        return self.get_view_multiframe().describe_spellbook_permission_mismatches(frame_name=frame_name)

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
        return self.get_view_multiframe().describe_spellbook_existence_mismatches(frame_name=frame_name)

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
        return self.get_view_multiframe().compare_spell_records(left_spell_source_id, right_spell_source_id, left_frame_name=left_frame_name, right_frame_name=right_frame_name)

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
        return self.get_view_multiframe().compare_conduit_records(left_conduit_id, right_conduit_id, left_frame_name=left_frame_name, right_frame_name=right_frame_name)

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
        return self.get_view_multiframe().list_spell_source_ids_for_frame(frame_name)

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
        return self.get_view_multiframe().list_frame_ids(frame_name=frame_name)

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
        return self.get_view_multiframe().list_nexus_contracts(frame_name=frame_name)

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
        return self.get_view_multiframe().count_conduit_records(frame_name=frame_name)

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
        return self.get_view_multiframe().list_conduit_record_ids(frame_name=frame_name)

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
        return self.get_view_multiframe().list_root_conduit_ids(frame_name=frame_name)

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
        return self.get_view_multiframe().count_spellbooks(frame_name=frame_name)

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
        return self.get_view_multiframe().list_origin_spellbook_ids(frame_name=frame_name)

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
        return self.get_view_multiframe().list_spell_record_ids(frame_name=frame_name)

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
        return self.get_view_multiframe().list_spell_record_keys(frame_name=frame_name)

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
        return self.get_view_multiframe().list_spell_names(frame_name=frame_name)

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
        return self.get_view_multiframe().list_binding_names(frame_name=frame_name)

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
        return self.get_view_multiframe().list_lineage_ids(frame_name=frame_name)

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
        return self.get_view_multiframe().list_spellframes(frame_name=frame_name)

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
        return self.get_view_multiframe().list_permissions(frame_name=frame_name)

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
        return self.get_view_multiframe().list_existence_kinds(frame_name=frame_name)

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
        return self.get_view_multiframe().describe_descriptor_inventory(frame_name=frame_name)

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
        return self.get_view_multiframe().describe_descriptor_topology(frame_name)

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
        return self.get_view_multiframe().describe_conduit_records(frame_name)

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
        return self.get_view_multiframe().describe_spell_records(frame_name)

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
        return self.get_view_multiframe().describe_spell_record(spell_source_id, frame_name=frame_name)

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
        return self.get_view_multiframe().list_spells_by_owner_conduit(conduit_id, frame_name=frame_name)

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
        return self.get_view_multiframe().list_spells_by_spellbook_id(spellbook_id, frame_name=frame_name)

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
        return self.get_view_multiframe().list_spells_by_permission(permission, frame_name=frame_name)

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
        return self.get_view_multiframe().list_spells_by_existence(existence, frame_name=frame_name)

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
        return self.get_view_multiframe().list_spells_by_spellframe(spellframe_name, frame_name=frame_name)

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



    def get_view_frame(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> ViewFrame:
        """
        Return the viewer-owned frame helper for one hosted frame.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, the default frame is used.

        Returns:
            ViewFrame: Bound frame helper.
        """
        return self._get_helper_surface_bundle(frame_name=frame_name)[0]

    def get_view_conduit(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> ViewConduit:
        """
        Return the viewer-owned conduit helper for one hosted frame.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, the default frame is used.

        Returns:
            ViewConduit: Bound conduit helper.
        """
        return self._get_helper_surface_bundle(frame_name=frame_name)[1]

    def get_view_spell(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> ViewSpell:
        """
        Return the viewer-owned spell helper for one hosted frame.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, the default frame is used.

        Returns:
            ViewSpell: Bound spell helper.
        """
        return self._get_helper_surface_bundle(frame_name=frame_name)[2]

    def get_view_multiframe(self) -> ViewMultiFrame:
        """
        Return the viewer-owned multi-frame helper.

        Returns:
            ViewMultiFrame: Borrowed helper for cross-frame and
            descriptor-hosted inventory/comparison logic.
        """
        self.check_cleaned()
        return self._view_multiframe

    @property
    def view_frame(self) -> ViewFrame:
        """Return the frame helper for the current default frame."""
        return self.get_view_frame()

    @property
    def view_conduit(self) -> ViewConduit:
        """Return the conduit helper for the current default frame."""
        return self.get_view_conduit()

    @property
    def view_spell(self) -> ViewSpell:
        """Return the spell helper for the current default frame."""
        return self.get_view_spell()

    @property
    def view_multiframe(self) -> ViewMultiFrame:
        """Return the multi-frame helper owned by this viewer."""
        return self.get_view_multiframe()

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
    ) -> Tuple[ViewFrame, ViewConduit, ViewSpell]:
        """
        Return the helper bundle for one hosted frame, creating it on demand.

        Args:
            frame_name:
                Optional hosted frame name override.

        Returns:
            Tuple[ViewFrame, ViewConduit, ViewSpell]:
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

    def list_frames(self) -> List[str]:
        """Direct facade for `list_frame_names` on the shipped viewer surface."""
        return self.list_frame_names()

    def list_spells_by_owner_conduit_record(self, conduit_id: str, *, frame_name: Optional[str] = None) -> List[str]:
        """Direct facade for `list_spells_by_owner_conduit` on the shipped viewer surface."""
        return self.list_spells_by_owner_conduit(conduit_id)

    def list_spells_by_spellbook_id_record(self, spellbook_id: str, *, frame_name: Optional[str] = None) -> List[str]:
        """Direct facade for `list_spells_by_spellbook_id` on the shipped viewer surface."""
        return self.list_spells_by_spellbook_id(spellbook_id)

    def list_spells_by_permission_record(self, permission: str, *, frame_name: Optional[str] = None) -> List[str]:
        """Direct facade for `list_spells_by_permission` on the shipped viewer surface."""
        return self.list_spells_by_permission(permission)

    def list_spells_by_existence_record(self, existence: str, *, frame_name: Optional[str] = None) -> List[str]:
        """Direct facade for `list_spells_by_existence` on the shipped viewer surface."""
        return self.list_spells_by_existence(existence)

    def list_spells_by_spellframe_record(self, spellframe_name: str, *, frame_name: Optional[str] = None) -> List[str]:
        """Direct facade for `list_spells_by_spellframe` on the shipped viewer surface."""
        return self.list_spells_by_spellframe(spellframe_name)

    def describe_visible_surface(self, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_frame.describe_visible_surface` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_visible_surface(frame_name=frame_name)

    def describe_missing_surface(self, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_frame.describe_missing_surface` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_missing_surface(frame_name=frame_name)

    def describe_frame_brief_local(self, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_frame.describe_frame_brief` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_frame_brief(frame_name=frame_name)

    def describe_visible_inventory_by_kind(self, *, frame_name: Optional[str] = None) -> Dict[str, Dict[str, object]]:
        """Direct facade for `view_frame.describe_visible_inventory_by_kind` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_visible_inventory_by_kind(frame_name=frame_name)

    def describe_frame_topology(self, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_frame.describe_frame_topology` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_frame_topology(frame_name=frame_name)

    def list_visible_target_ids(self, *, frame_name: Optional[str] = None, source_kind: Optional[str] = None) -> List[str]:
        """Direct facade for `view_frame.list_visible_target_ids` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_target_ids(frame_name=frame_name, source_kind=source_kind)

    def list_visible_target_ids_by_kind(self, *, frame_name: Optional[str] = None) -> Dict[str, Tuple[str, ...]]:
        """Direct facade for `view_frame.list_visible_target_ids_by_kind` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_target_ids_by_kind(frame_name=frame_name)

    def list_visible_conduit_ids(self, *, frame_name: Optional[str] = None) -> List[str]:
        """Direct facade for `view_frame.list_visible_conduit_ids` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_conduit_ids(frame_name=frame_name)

    def list_visible_spell_source_ids(self, *, frame_name: Optional[str] = None) -> List[str]:
        """Direct facade for `view_frame.list_visible_spell_source_ids` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_spell_source_ids(frame_name=frame_name)

    def list_visible_root_conduits(self, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_frame.list_visible_root_conduits` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_root_conduits(frame_name=frame_name)

    def list_visible_binding_names(self, *, frame_name: Optional[str] = None) -> List[str]:
        """Direct facade for `view_frame.list_visible_binding_names` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_binding_names(frame_name=frame_name)

    def list_visible_spell_names(self, *, frame_name: Optional[str] = None) -> List[str]:
        """Direct facade for `view_frame.list_visible_spell_names` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_spell_names(frame_name=frame_name)

    def list_visible_spellframes(self, *, frame_name: Optional[str] = None) -> List[str]:
        """Direct facade for `view_frame.list_visible_spellframes` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_spellframes(frame_name=frame_name)

    def list_visible_lineage_ids(self, *, frame_name: Optional[str] = None) -> List[str]:
        """Direct facade for `view_frame.list_visible_lineage_ids` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_visible_lineage_ids(frame_name=frame_name)

    def describe_visible_spell_ownership(self, *, frame_name: Optional[str] = None) -> Dict[str, Tuple[str, ...]]:
        """Direct facade for `view_frame.describe_visible_spell_ownership` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_visible_spell_ownership(frame_name=frame_name)

    def describe_visible_conduit_tree(self, *, frame_name: Optional[str] = None) -> Dict[str, Tuple[str, ...]]:
        """Direct facade for `view_frame.describe_visible_conduit_tree` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_visible_conduit_tree(frame_name=frame_name)

    def search_targets_contains(self, text: str, *, frame_name: Optional[str] = None, source_kind: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_frame.search_targets_contains` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).search_targets_contains(text, frame_name=frame_name, source_kind=source_kind)

    def search_targets_prefix(self, prefix: str, *, frame_name: Optional[str] = None, source_kind: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_frame.search_targets_prefix` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).search_targets_prefix(prefix, frame_name=frame_name, source_kind=source_kind)

    def group_targets_by_kind(self, *, frame_name: Optional[str] = None) -> Dict[str, List[IFrameLink]]:
        """Direct facade for `view_frame.group_targets_by_kind` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).group_targets_by_kind(frame_name=frame_name)

    def describe_target_brief(self, *, source_kind: str, source_id: str, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_frame.describe_target_brief` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_target_brief(frame_name=frame_name, source_kind=source_kind, source_id=source_id)

    def describe_target_identity(self, *, source_kind: str, source_id: str, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_frame.describe_target_identity` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_target_identity(frame_name=frame_name, source_kind=source_kind, source_id=source_id)

    def describe_visible_collisions(self, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_frame.describe_visible_collisions` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_visible_collisions(frame_name=frame_name)

    def describe_frame_payload(self, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_frame.describe_frame_payload` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_frame_payload(frame_name=frame_name)

    def describe_frame_inventory(self, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_frame.describe_frame_inventory` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_frame_inventory(frame_name=frame_name)

    def describe_frame_access_contract(self, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_frame.describe_frame_access_contract` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_frame_access_contract(frame_name=frame_name)

    def get_frame_payload_field(self, field_name: str, *, frame_name: Optional[str] = None) -> object:
        """Direct facade for `view_frame.get_frame_payload_field` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).get_frame_payload_field(field_name, frame_name=frame_name)

    def find_target_by_display_name(self, display_name: str, *, frame_name: Optional[str] = None, source_kind: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_frame.find_target_by_display_name` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).find_target_by_display_name(display_name, frame_name=frame_name, source_kind=source_kind)

    def explain_target_access(self, *, source_kind: str, source_id: str, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_frame.explain_target_access` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).explain_target_access(frame_name=frame_name, source_kind=source_kind, source_id=source_id)

    def list_targets(self, *, frame_name: Optional[str] = None, source_kind: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_frame.list_targets` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).list_targets(frame_name=frame_name, source_kind=source_kind)

    def describe_targets(self, *, frame_name: Optional[str] = None, source_kind: Optional[str] = None) -> List[Dict[str, object]]:
        """Direct facade for `view_frame.describe_targets` on the shipped viewer surface."""
        return self.get_view_frame(frame_name=frame_name).describe_targets(frame_name=frame_name, source_kind=source_kind)

    def list_conduits(self, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_conduit.list_conduits` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_conduits(frame_name=frame_name)

    def list_root_conduits(self, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_conduit.list_root_conduits` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_root_conduits(frame_name=frame_name)

    def describe_conduits(self, *, frame_name: Optional[str] = None) -> List[Dict[str, object]]:
        """Direct facade for `view_conduit.describe_conduits` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduits(frame_name=frame_name)

    def get_conduit(self, conduit_id: str, *, frame_name: Optional[str] = None) -> IFrameLink:
        """Direct facade for `view_conduit.get_required_conduit` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).get_required_conduit(conduit_id, frame_name=frame_name)

    def describe_conduit(self, conduit_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_conduit.describe_conduit` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduit(conduit_id, frame_name=frame_name)

    def describe_conduit_brief(self, conduit_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_conduit.describe_conduit_brief` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_brief(conduit_id, frame_name=frame_name)

    def describe_conduit_inventory(self, conduit_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_conduit.describe_conduit_inventory` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_inventory(conduit_id, frame_name=frame_name)

    def describe_conduit_relationships(self, conduit_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_conduit.describe_conduit_relationships` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_relationships(conduit_id, frame_name=frame_name)

    def describe_conduit_missing_sections(self, conduit_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_conduit.describe_conduit_missing_sections` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_missing_sections(conduit_id, frame_name=frame_name)

    def describe_conduit_crosswalk(self, conduit_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_conduit.describe_conduit_crosswalk` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_crosswalk(conduit_id, frame_name=frame_name)

    def list_conduit_spells(self, conduit_id: str, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_conduit.list_conduit_spells` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_conduit_spells(conduit_id, frame_name=frame_name)

    def describe_conduit_topology(self, conduit_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_conduit.describe_conduit_topology` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).describe_conduit_topology(conduit_id, frame_name=frame_name)

    def compare_conduits(self, left_conduit_id: str, right_conduit_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_conduit.compare_conduits` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).compare_conduits(left_conduit_id, right_conduit_id, frame_name=frame_name)

    def is_root_conduit(self, conduit_id: str, *, frame_name: Optional[str] = None) -> bool:
        """Direct facade for `view_conduit.is_root_conduit` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).is_root_conduit(conduit_id, frame_name=frame_name)

    def get_root_conduit_id(self, conduit_id: str, *, frame_name: Optional[str] = None) -> str:
        """Direct facade for `view_conduit.get_root_conduit_id` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).get_root_conduit_id(conduit_id, frame_name=frame_name)

    def list_conduits_by_root_id(self, root_conduit_id: str, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_conduit.list_conduits_by_root_id` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_conduits_by_root_id(root_conduit_id, frame_name=frame_name)

    def list_conduits_by_policy(self, policy_name: str, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_conduit.list_conduits_by_policy` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_conduits_by_policy(policy_name, frame_name=frame_name)

    def list_conduits_by_state(self, state_name: str, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_conduit.list_conduits_by_state` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_conduits_by_state(state_name, frame_name=frame_name)

    def list_peer_conduits(self, conduit_id: str, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_conduit.list_peer_conduits` on the shipped viewer surface."""
        return self.get_view_conduit(frame_name=frame_name).list_peer_conduits(conduit_id, frame_name=frame_name)

    def list_spells(self, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_spell.list_spells` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).list_spells(frame_name=frame_name)

    def describe_spells(self, *, frame_name: Optional[str] = None) -> List[Dict[str, object]]:
        """Direct facade for `view_spell.describe_spells` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spells(frame_name=frame_name)

    def get_spell(self, spell_source_id: str, *, frame_name: Optional[str] = None) -> IFrameLink:
        """Direct facade for `view_spell.get_required_spell` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).get_required_spell(spell_source_id, frame_name=frame_name)

    def describe_spell(self, spell_source_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_spell.describe_spell` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell(spell_source_id, frame_name=frame_name)

    def describe_spell_brief(self, spell_source_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_spell.describe_spell_brief` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_brief(spell_source_id, frame_name=frame_name)

    def describe_spell_origin(self, spell_source_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_spell.describe_spell_origin` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_origin(spell_source_id, frame_name=frame_name)

    def describe_spell_lineage(self, spell_source_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_spell.describe_spell_lineage` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_lineage(spell_source_id, frame_name=frame_name)

    def describe_spell_payload(self, spell_source_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_spell.describe_spell_payload` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_payload(spell_source_id, frame_name=frame_name)

    def describe_spell_missing_sections(self, spell_source_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_spell.describe_spell_missing_sections` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_missing_sections(spell_source_id, frame_name=frame_name)

    def describe_spell_crosswalk(self, spell_source_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_spell.describe_spell_crosswalk` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).describe_spell_crosswalk(spell_source_id, frame_name=frame_name)

    def compare_spells(self, left_spell_source_id: str, right_spell_source_id: str, *, frame_name: Optional[str] = None) -> Dict[str, object]:
        """Direct facade for `view_spell.compare_spells` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).compare_spells(left_spell_source_id, right_spell_source_id, frame_name=frame_name)

    def list_spells_by_owner_conduit(self, conduit_id: str, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_spell.list_spells_by_owner_conduit` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).list_spells_by_owner_conduit(conduit_id, frame_name=frame_name)

    def list_spells_by_spellbook_id(self, spellbook_id: str, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_spell.list_spells_by_spellbook_id` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).list_spells_by_spellbook_id(spellbook_id, frame_name=frame_name)

    def list_spells_by_permission(self, permission_name: str, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_spell.list_spells_by_permission` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).list_spells_by_permission(permission_name, frame_name=frame_name)

    def list_spells_by_existence(self, existence_name: str, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_spell.list_spells_by_existence` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).list_spells_by_existence(existence_name, frame_name=frame_name)

    def list_spells_by_spellframe(self, spellframe_name: str, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """Direct facade for `view_spell.list_spells_by_spellframe` on the shipped viewer surface."""
        return self.get_view_spell(frame_name=frame_name).list_spells_by_spellframe(spellframe_name, frame_name=frame_name)

    def list_viewer_method_names_ast_json(
            self,
            *,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """Return a minified JSON list of `FrameViewer` class method names."""
        self.check_cleaned()
        return ClassSurfaceAstDescriber.list_class_method_names_ast_json(
            self,
            include_private=include_private,
            include_dunder=include_dunder,
        )

    def describe_agent_onboarding_json(self) -> str:
        """Return the shared first-time onboarding hint for Melder agents."""
        self.check_cleaned()
        return ClassSurfaceAstDescriber.describe_agent_onboarding_json()

    def describe_viewer_agent_purpose_json(self) -> str:
        """Return the minified JSON agent-purpose surface for the viewer host."""
        self.check_cleaned()
        return ClassSurfaceAstDescriber.describe_agent_purpose_json(self)

    def describe_viewer_class_surface_ast_json(
            self,
            *,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """Return a minified JSON description of the `FrameViewer` class surface."""
        self.check_cleaned()
        return ClassSurfaceAstDescriber.describe_class_surface_ast_json(
            self,
            include_private=include_private,
            include_dunder=include_dunder,
        )

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

    def _create_helper_surface_bundle_for_frame(
            self,
            frame_name: str,
    ) -> Tuple[ViewFrame, ViewConduit, ViewSpell]:
        """
        Create one helper bundle for one hosted frame.

        Args:
            frame_name:
                Hosted frame name.

        Returns:
            Tuple[ViewFrame, ViewConduit, ViewSpell]:
                Helper bundle bound to the hosted frame's projection-owned
                descriptor and ACL state.
        """
        view_frame = ViewFrame(
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
        view_conduit = ViewConduit(frame_view=view_frame)
        view_spell = ViewSpell(frame_view=view_frame)
        return view_frame, view_conduit, view_spell
