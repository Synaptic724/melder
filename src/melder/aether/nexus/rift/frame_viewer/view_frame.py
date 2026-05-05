"""
Frame-local helper surface for one selected view projection.

This module owns the selected-frame helper that converts one descriptor plus
one compiled ACL surface into `FrameLink` snapshots and frame-scoped view
summaries.
"""

from contextlib import contextmanager
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.aether.nexus.rift.frame_viewer.view_action_hooks import (
    decorate_public_view_actions,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces import IFrameLink


@decorate_public_view_actions
class ViewFrame(Cleanable):
    """
    Purpose:
        Hold frame-scoped viewer helper methods for one selected frame.

    Contract:
        - Operates only on one selected frame's descriptor and ACL state.
        - Returns ACL-filtered `FrameLink` objects and summaries.
        - Does not expose raw runtime objects.

    Lifecycle:
        Cleanup is idempotent and clears all bound references.
    """

    __melder_internal__ = _mrg.sentinel
    _ast_helper_access: str = "public"
    __agent_purpose__: str = (
        "access: public. Frame-local helper surface for visible targets, "
        "frame summaries, inventory, search, collision detection, and "
        "frame-local access explanations."
    )
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_frame_name",
        "_frame_descriptor",
        "_frame_acl_configuration",
        "_compiled_access_surface",
        "_default_detail_level",
        "_action_hook_scope_factory",
    ]

    def __init__(
            self,
            *,
            frame_name: Optional[str],
            frame_descriptor: Optional[FrameDescriptor],
            frame_acl_configuration: Optional[FrameACLConfiguration],
            compiled_access_surface: Optional[CompiledFrameACLAccessSurface],
            default_detail_level: str,
            action_hook_scope_factory: Optional[Callable[..., Any]] = None,
    ) -> None:
        """
        Initialize one frame-scoped viewer helper surface.

        Contract:
            - Stores borrowed references to one frame's descriptor and compiled
              ACL state for one frame-local helper instance.
            - Does not own the bound descriptor or ACL objects.

        Args:
            frame_name:
                Bound frame name when available.
            frame_descriptor:
                Bound frame descriptor when available.
            frame_acl_configuration:
                Bound frame ACL configuration when available.
            compiled_access_surface:
                Bound compiled ACL surface when available.
            default_detail_level:
                Default description detail posture.

        Returns:
            None.
        """
        super().__init__()
        if not default_detail_level:
            raise ValueError("default_detail_level cannot be empty.")
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: Optional[str] = frame_name
        self._frame_descriptor: Optional[FrameDescriptor] = frame_descriptor
        self._frame_acl_configuration: Optional[FrameACLConfiguration] = (
            frame_acl_configuration
        )
        self._compiled_access_surface: Optional[CompiledFrameACLAccessSurface] = (
            compiled_access_surface
        )
        self._default_detail_level: str = default_detail_level
        self._action_hook_scope_factory: Optional[Callable[..., Any]] = (
            action_hook_scope_factory
        )

    def cleanup(self) -> None:
        """
        Idempotently drop the borrowed frame-state references.

        Contract:
            - Clears only the helper's own references and lock.
            - Never cleans the descriptor or ACL objects because they are
              borrowed runtime inputs.

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
            self._frame_descriptor = None
            self._frame_acl_configuration = None
            self._compiled_access_surface = None
            self._default_detail_level = None
            self._action_hook_scope_factory = None
        self._lock = None

    @contextmanager
    def _entered_view_action(self, *, action_name: str) -> Any:
        """
        Enter one viewer action hook scope through the stored factory.

        Args:
            action_name:
                Stable viewer action name.

        Returns:
            Any: Viewer hook scope context manager.
        """
        self.check_cleaned()
        if self._action_hook_scope_factory is None:
            yield
            return
        with self._action_hook_scope_factory(action_name=action_name):
            yield

    def list_targets(
            self,
            *,
            frame_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[IFrameLink]:
        """
        Return the currently visible targets for the bound frame.

        Contract:
            - Builds links from the bound descriptor plus compiled ACL surface.
            - Optionally filters that visible set down to one source kind.
            - Returns a fresh snapshot for this call.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.
            source_kind:
                Optional target-kind filter (`frame`, `conduit`, or `spell`).

        Returns:
            List[FrameLink]: Ordered ACL-filtered targets.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        targets = self._build_links()
        if source_kind is None:
            return targets
        if not source_kind:
            raise ValueError("source_kind cannot be empty.")
        return [
            frame_link
            for frame_link in targets
            if frame_link.source_kind == source_kind
        ]

    def describe_targets(
            self,
            *,
            frame_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """
        Return summary descriptions for the current visible target snapshot.

        Contract:
            - Preserves the same target visibility as `list_targets(...)`.
            - Includes link metadata only when the helper is in `detailed`
              posture.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[Dict[str, object]]: ACL-filtered target descriptions.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        target_descriptions: List[Dict[str, object]] = []
        for frame_link in self.list_targets(source_kind=source_kind):
            description = {
                "target_id": frame_link.link_id,
                "source_kind": frame_link.source_kind,
                "source_id": frame_link.source_id,
                "display_name": frame_link.display_name,
            }
            if self._default_detail_level == "detailed":
                description["metadata"] = frame_link.metadata
            target_descriptions.append(description)
        return target_descriptions

    def describe_frame(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return a compact summary of the visible frame surface.

        Contract:
            - Summarizes only currently visible target kinds and counts.
            - Merges compiled ACL metadata with the frame's advertised Nexus
              contract when frame overview data is present.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, object]: Frame summary with Nexus-contract metadata.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        compiled_access_surface = self._get_required_compiled_access_surface()
        grouped_links: Dict[str, List[IFrameLink]] = {}
        for frame_link in self._build_links():
            grouped_links.setdefault(frame_link.source_kind, []).append(frame_link)
        descriptor = self._get_required_frame_descriptor()
        frame_overview = descriptor.frame_overview
        frame_nexus_contract = None
        if frame_overview is not None:
            frame_nexus_contract = "{0}:{1}".format(
                frame_overview.nexus_label,
                frame_overview.nexus_version,
            )
        return {
            "frame_name": self._get_required_frame_name(),
            "link_count": len(self._build_links()),
            "available_kinds": tuple(sorted(grouped_links.keys())),
            "link_counts_by_kind": {
                source_kind: len(grouped_links[source_kind])
                for source_kind in grouped_links.keys()
            },
            "metadata": {
                **compiled_access_surface.metadata,
                "frame_nexus_contract": frame_nexus_contract,
            },
        }

    def describe_frame_payload(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the ACL-filtered frame payload for the bound frame.

        Purpose:
            Surface the real `FrameRecord.payload` content the viewer can use
            after the compiled ACL surface has already reduced it to the
            currently visible frame fields.

        Contract:
            - Uses the bound `FrameDescriptor` and compiled ACL surface only.
            - Returns only fields present in
              `CompiledFrameACLAccessSurface.frame_payload_fields`.
            - Raises when the bound frame does not expose `frame_overview`.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, object]: ACL-filtered frame payload description.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        descriptor = self._get_required_frame_descriptor()
        frame_overview = descriptor.frame_overview
        if frame_overview is None:
            raise ValueError(
                "FrameDescriptor must expose frame_overview for frame payload description."
            )
        visible_fields = tuple(
            self._get_required_compiled_access_surface().frame_payload_fields
        )
        return {
            "frame_name": self._get_required_frame_name(),
            "frame_id": frame_overview.frame_id,
            "nexus_label": frame_overview.nexus_label,
            "nexus_version": frame_overview.nexus_version,
            "payload_version": frame_overview.payload.payload_version,
            "visible_fields": visible_fields,
            "payload": self._filter_frame_payload(
                frame_overview.payload,
                visible_fields,
            ),
        }

    def describe_frame_inventory(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return a compact inventory of the bound frame surface.

        Purpose:
            Give the main viewer operator a fast answer to "what is in this
            frame right now?" without forcing a full target dump first.

        Contract:
            - Counts only ACL-visible conduits and spells.
            - Preserves the currently visible target ids and source ids.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, object]: Compact frame inventory summary.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        links = self._build_links()
        conduit_ids = [
            frame_link.source_id
            for frame_link in links
            if frame_link.source_kind == "conduit"
        ]
        spell_ids = [
            frame_link.source_id
            for frame_link in links
            if frame_link.source_kind == "spell"
        ]
        return {
            "frame_name": self._get_required_frame_name(),
            "target_count": len(links),
            "conduit_count": len(conduit_ids),
            "spell_count": len(spell_ids),
            "conduit_ids": tuple(conduit_ids),
            "spell_source_ids": tuple(spell_ids),
        }

    def describe_frame_access_contract(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the bound ACL access contract for the frame surface.

        Purpose:
            Surface the effective view/codegen posture and visible frame payload
            fields so the viewer operator can understand why certain data is or
            is not available.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, object]: Effective ACL access contract summary.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        compiled_access_surface = self._get_required_compiled_access_surface()
        return {
            "frame_name": self._get_required_frame_name(),
            "configuration_id": compiled_access_surface.configuration_id,
            "view_profile_name": compiled_access_surface.view_profile_name,
            "view_profile_version": compiled_access_surface.view_profile_version,
            "codegen_profile_name": (
                compiled_access_surface.codegen_profile_name
            ),
            "codegen_profile_version": (
                compiled_access_surface.codegen_profile_version
            ),
            "allowed_kinds": compiled_access_surface.allowed_kinds,
            "allowed_commands": compiled_access_surface.allowed_commands,
            "frame_payload_fields": compiled_access_surface.frame_payload_fields,
        }

    def describe_frame_brief(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one compact operator-oriented frame summary.

        Purpose:
            Give the operator a smaller "start here" summary than the richer
            frame surface methods while still reflecting visible inventory and
            ACL posture.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, object]: Compact frame-local summary.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        frame_inventory = self.describe_frame_inventory(frame_name=frame_name)
        frame_contract = self.describe_frame_access_contract(frame_name=frame_name)
        return {
            "frame_name": self._get_required_frame_name(),
            "visible_target_count": frame_inventory["target_count"],
            "visible_conduit_count": frame_inventory["conduit_count"],
            "visible_spell_count": frame_inventory["spell_count"],
            "allowed_kinds": frame_contract["allowed_kinds"],
            "frame_payload_field_count": len(frame_contract["frame_payload_fields"]),
        }

    def describe_target_brief(
            self,
            *,
            source_kind: str,
            source_id: str,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one compact summary for a visible target.

        Purpose:
            Give the operator a quick identity/access snapshot for one visible
            target without forcing the richer identity or payload-specific
            methods immediately.

        Args:
            source_kind:
                Required target kind.
            source_id:
                Required target source id.
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, object]: Compact visible target summary.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        frame_link = self.get_required_target_by_source(
            frame_name=frame_name,
            source_kind=source_kind,
            source_id=source_id,
        )
        explanation = self.explain_target_access(
            frame_name=frame_name,
            source_kind=source_kind,
            source_id=source_id,
        )
        visible_payload_keys = tuple()
        if source_kind == "frame":
            visible_payload_keys = tuple(explanation["visible_fields"])
        else:
            visible_payload_keys = tuple(explanation["visible_sections"])
        return {
            "target_id": frame_link.link_id,
            "source_kind": frame_link.source_kind,
            "source_id": frame_link.source_id,
            "display_name": frame_link.display_name,
            "visible": explanation["visible"],
            "reason": explanation["reason"],
            "visible_payload_keys": visible_payload_keys,
        }

    def describe_missing_surface(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return what is currently hidden or absent from the bound frame surface.

        Purpose:
            Help the operator answer "what am I not seeing right now?" by
            comparing descriptor-owned records and payload fields against the
            currently visible ACL-shaped surface.

        Contract:
            - Uses descriptor truth plus the compiled ACL surface only.
            - Distinguishes hidden frame payload fields, hidden conduit/spell
              records, and payload sections not currently visible.
            - Does not expose hidden payload bodies.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, object]: Missing/hidden surface summary.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        descriptor = self._get_required_frame_descriptor()
        compiled_access_surface = self._get_required_compiled_access_surface()
        frame_overview = descriptor.frame_overview
        all_frame_payload_fields = tuple()
        if frame_overview is not None:
            all_frame_payload_fields = self._payload_field_names(
                frame_overview.payload,
                excluded_fields=("payload_version",),
            )
        hidden_frame_payload_fields = tuple(
            current_field
            for current_field in all_frame_payload_fields
            if current_field not in compiled_access_surface.frame_payload_fields
        )
        hidden_conduit_ids = tuple(
            sorted(
                conduit_id
                for conduit_id in descriptor.conduit_records_by_id.keys()
                if conduit_id not in compiled_access_surface.visible_conduit_ids
            )
        )
        hidden_spell_source_ids = tuple(
            sorted(
                self._build_spell_source_id(
                    descriptor.spell_records_by_key[record_key]
                )
                for record_key in descriptor.spell_records_by_key.keys()
                if record_key not in compiled_access_surface.visible_spell_keys
            )
        )
        hidden_conduit_sections_by_id: Dict[str, Tuple[str, ...]] = {}
        for conduit_id, conduit_record in descriptor.conduit_records_by_id.items():
            all_sections = self._payload_field_names(
                conduit_record.payload,
                excluded_fields=("payload_version",),
            )
            visible_sections = tuple(
                compiled_access_surface.conduit_payload_sections_by_id.get(
                    conduit_id,
                    tuple(),
                )
            )
            hidden_conduit_sections_by_id[conduit_id] = tuple(
                current_section
                for current_section in all_sections
                if current_section not in visible_sections
            )
        hidden_spell_sections_by_source_id: Dict[str, Tuple[str, ...]] = {}
        for record_key, spell_record in descriptor.spell_records_by_key.items():
            all_sections = self._payload_field_names(
                spell_record.payload,
                excluded_fields=(
                    "payload_type",
                    "payload_version",
                    "source_profile_name",
                    "source_profile_version",
                ),
            )
            visible_sections = tuple(
                compiled_access_surface.spell_payload_sections_by_key.get(
                    record_key,
                    tuple(),
                )
            )
            hidden_spell_sections_by_source_id[
                self._build_spell_source_id(spell_record)
            ] = tuple(
                current_section
                for current_section in all_sections
                if current_section not in visible_sections
            )
        return {
            "frame_name": self._get_required_frame_name(),
            "hidden_frame_payload_fields": hidden_frame_payload_fields,
            "hidden_conduit_ids": hidden_conduit_ids,
            "hidden_spell_source_ids": hidden_spell_source_ids,
            "hidden_conduit_sections_by_id": hidden_conduit_sections_by_id,
            "hidden_spell_sections_by_source_id": hidden_spell_sections_by_source_id,
        }

    def describe_visible_collisions(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return visible identity collisions for the bound frame.

        Purpose:
            Make visible ambiguity explicit at the frame-local surface so the
            operator can see where multiple visible spells share the same
            binding name, spell name, lineage, or spellframe.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, object]: Visible collision and grouping summary.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        grouped_source_ids_by_binding_name: Dict[str, List[str]] = {}
        grouped_source_ids_by_spell_name: Dict[str, List[str]] = {}
        grouped_source_ids_by_lineage_id: Dict[str, List[str]] = {}
        grouped_source_ids_by_spellframe: Dict[str, List[str]] = {}
        for spell_link, spell_record in self._iter_visible_spell_links_and_records(
                frame_name=frame_name
        ):
            if spell_record.binding_name is not None:
                grouped_source_ids_by_binding_name.setdefault(
                    spell_record.binding_name,
                    [],
                ).append(spell_link.source_id)
            grouped_source_ids_by_spell_name.setdefault(
                spell_record.spell_name,
                [],
            ).append(spell_link.source_id)
            grouped_source_ids_by_lineage_id.setdefault(
                spell_record.spell_index_id,
                [],
            ).append(spell_link.source_id)
            normalized_spellframe = self._normalize_spellframe_value(
                spell_record.spellframe
            )
            if normalized_spellframe is not None:
                grouped_source_ids_by_spellframe.setdefault(
                    normalized_spellframe,
                    [],
                ).append(spell_link.source_id)
        return {
            "binding_name_collisions": self._filter_grouped_collisions(
                grouped_source_ids_by_binding_name
            ),
            "spell_name_collisions": self._filter_grouped_collisions(
                grouped_source_ids_by_spell_name
            ),
            "lineage_groups": self._normalize_grouped_source_ids(
                grouped_source_ids_by_lineage_id
            ),
            "spellframe_groups": self._normalize_grouped_source_ids(
                grouped_source_ids_by_spellframe
            ),
        }

    def describe_visible_surface(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the current visible frame-local surface in one summary.

        Purpose:
            Give the operator a single "what can I actually see right now?"
            entry point over the bound frame without making them manually merge
            inventory, topology, and access-contract calls.

        Contract:
            - Uses only the bound frame descriptor plus the compiled ACL
              surface.
            - Summarizes the currently visible target ids, grouped inventory,
              visible topology, and access contract.
            - Remains frame-local; it never spans multiple hosted frames.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, object]: Summary of the currently visible frame-local
            surface.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        return {
            "frame_name": self._get_required_frame_name(),
            "available_kinds": tuple(
                self.describe_frame()["available_kinds"]
            ),
            "inventory_by_kind": self.describe_visible_inventory_by_kind(
                frame_name=frame_name
            ),
            "visible_target_ids_by_kind": self.list_visible_target_ids_by_kind(
                frame_name=frame_name
            ),
            "visible_root_conduit_ids": tuple(
                conduit_link.source_id
                for conduit_link in self.list_visible_root_conduits(
                    frame_name=frame_name
                )
            ),
            "visible_spell_ownership": self.describe_visible_spell_ownership(
                frame_name=frame_name
            ),
            "access_contract": self.describe_frame_access_contract(
                frame_name=frame_name
            ),
        }

    def describe_visible_inventory_by_kind(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Dict[str, object]]:
        """
        Return visible inventory grouped by target kind.

        Purpose:
            Provide a frame-local grouped inventory over visible targets so the
            operator can see counts, source ids, and names without manually
            regrouping raw links.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, Dict[str, object]]: Inventory grouped by target kind.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        grouped_targets = self.group_targets_by_kind(frame_name=frame_name)
        return {
            source_kind: {
                "count": len(frame_links),
                "target_ids": tuple(
                    frame_link.link_id
                    for frame_link in frame_links
                ),
                "source_ids": tuple(
                    frame_link.source_id
                    for frame_link in frame_links
                ),
                "display_names": tuple(
                    frame_link.display_name
                    for frame_link in frame_links
                ),
            }
            for source_kind, frame_links in grouped_targets.items()
        }

    def describe_frame_topology(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the visible conduit/spell topology for the bound frame.

        Purpose:
            Summarize how the currently visible conduits and spells relate to
            each other so the operator can navigate the frame structure without
            reading each target individually first.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, object]: Visible frame-local topology summary.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        root_conduit_links = self.list_visible_root_conduits(frame_name=frame_name)
        return {
            "frame_name": self._get_required_frame_name(),
            "root_conduit_ids": tuple(
                conduit_link.source_id
                for conduit_link in root_conduit_links
            ),
            "conduit_ids_by_root_id": self.describe_visible_conduit_tree(
                frame_name=frame_name
            ),
            "spell_source_ids_by_conduit_id": self.describe_visible_spell_ownership(
                frame_name=frame_name
            ),
            "visible_spell_source_ids": tuple(
                self.list_visible_spell_source_ids(frame_name=frame_name)
            ),
        }

    def list_visible_target_ids(
            self,
            *,
            frame_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[str]:
        """
        Return visible target ids for the bound frame.

        Purpose:
            Provide a compact id-only view over the currently visible target
            surface.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[str]: Visible target ids in deterministic order.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        return [
            frame_link.link_id
            for frame_link in self.list_targets(
                frame_name=frame_name,
                source_kind=source_kind,
            )
        ]

    def list_visible_target_ids_by_kind(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return visible target ids grouped by target kind.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, Tuple[str, ...]]: Visible target ids grouped by kind.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        return {
            source_kind: tuple(
                frame_link.link_id
                for frame_link in frame_links
            )
            for source_kind, frame_links in self.group_targets_by_kind(
                frame_name=frame_name
            ).items()
        }

    def list_visible_conduit_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return visible conduit ids for the bound frame.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            List[str]: Visible conduit ids in deterministic order.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        return [
            conduit_link.source_id
            for conduit_link in self.list_targets(
                frame_name=frame_name,
                source_kind="conduit",
            )
        ]

    def list_visible_spell_source_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return visible spell source ids for the bound frame.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            List[str]: Visible spell source ids in deterministic order.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        return [
            spell_link.source_id
            for spell_link in self.list_targets(
                frame_name=frame_name,
                source_kind="spell",
            )
        ]

    def list_visible_root_conduits(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[IFrameLink]:
        """
        Return visible conduit links that are also root conduits.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            List[FrameLink]: Visible root conduit links.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        descriptor = self._get_required_frame_descriptor()
        root_conduits: List[IFrameLink] = []
        for conduit_link in self.list_targets(
                frame_name=frame_name,
                source_kind="conduit",
        ):
            conduit_record = descriptor.conduit_records_by_id[conduit_link.source_id]
            if conduit_record.root_conduit_id == conduit_record.conduit_id:
                root_conduits.append(conduit_link)
        return root_conduits

    def list_visible_binding_names(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return visible spell binding names for the bound frame.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            List[str]: Visible binding names in deterministic spell order.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        descriptor = self._get_required_frame_descriptor()
        binding_names: List[str] = []
        for spell_link in self.list_targets(
                frame_name=frame_name,
                source_kind="spell",
        ):
            record_key = spell_link.metadata["record_key"]
            binding_name = descriptor.spell_records_by_key[record_key].binding_name
            if binding_name is None:
                continue
            binding_names.append(binding_name)
        return binding_names

    def list_visible_spell_names(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return visible spell names for the bound frame.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            List[str]: Visible spell names in deterministic spell order.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        descriptor = self._get_required_frame_descriptor()
        return [
            descriptor.spell_records_by_key[spell_link.metadata["record_key"]].spell_name
            for spell_link in self.list_targets(
                frame_name=frame_name,
                source_kind="spell",
            )
        ]

    def list_visible_spellframes(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return visible normalized spellframe values for the bound frame.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            List[str]: Distinct visible spellframe values in deterministic
            order.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        descriptor = self._get_required_frame_descriptor()
        spellframes = []
        seen_spellframes = set()
        for spell_link in self.list_targets(
                frame_name=frame_name,
                source_kind="spell",
        ):
            record_key = spell_link.metadata["record_key"]
            spellframe_name = self._normalize_spellframe_value(
                descriptor.spell_records_by_key[record_key].spellframe
            )
            if spellframe_name is None or spellframe_name in seen_spellframes:
                continue
            spellframes.append(spellframe_name)
            seen_spellframes.add(spellframe_name)
        return spellframes

    def list_visible_lineage_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return visible lineage ids for the bound frame.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            List[str]: Visible lineage ids in deterministic spell order.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        descriptor = self._get_required_frame_descriptor()
        return [
            descriptor.spell_records_by_key[spell_link.metadata["record_key"]].spell_index_id
            for spell_link in self.list_targets(
                frame_name=frame_name,
                source_kind="spell",
            )
        ]

    def describe_visible_spell_ownership(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return visible spell ownership grouped by conduit id.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, Tuple[str, ...]]: Visible spell source ids grouped by
            owner conduit id.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        descriptor = self._get_required_frame_descriptor()
        spells_by_conduit_id: Dict[str, List[str]] = {}
        for spell_link in self.list_targets(
                frame_name=frame_name,
                source_kind="spell",
        ):
            record_key = spell_link.metadata["record_key"]
            owner_conduit_id = descriptor.spell_records_by_key[record_key].owner_conduit_id
            if owner_conduit_id is None:
                continue
            spells_by_conduit_id.setdefault(owner_conduit_id, []).append(
                spell_link.source_id
            )
        return {
            conduit_id: tuple(spell_source_ids)
            for conduit_id, spell_source_ids in spells_by_conduit_id.items()
        }

    def describe_visible_conduit_tree(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return visible conduit ids grouped by root conduit id.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, Tuple[str, ...]]: Visible conduit ids grouped by root
            conduit id.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        descriptor = self._get_required_frame_descriptor()
        conduit_ids_by_root_id: Dict[str, List[str]] = {}
        for conduit_link in self.list_targets(
                frame_name=frame_name,
                source_kind="conduit",
        ):
            conduit_record = descriptor.conduit_records_by_id[conduit_link.source_id]
            conduit_ids_by_root_id.setdefault(
                conduit_record.root_conduit_id,
                [],
            ).append(conduit_link.source_id)
        return {
            root_conduit_id: tuple(conduit_ids)
            for root_conduit_id, conduit_ids in conduit_ids_by_root_id.items()
        }

    def search_targets_contains(
            self,
            text: str,
            *,
            frame_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[IFrameLink]:
        """
        Return visible targets whose identity contains one text fragment.

        Purpose:
            Provide a forgiving search path over visible target display names
            and source ids.

        Args:
            text:
                Case-insensitive text fragment to search for.
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[FrameLink]: Matching visible targets in deterministic order.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        if not text:
            raise ValueError("text cannot be empty.")
        lowered_text = text.lower()
        return [
            frame_link
            for frame_link in self.list_targets(
                frame_name=frame_name,
                source_kind=source_kind,
            )
            if lowered_text in frame_link.display_name.lower()
            or lowered_text in frame_link.source_id.lower()
        ]

    def search_targets_prefix(
            self,
            prefix: str,
            *,
            frame_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible targets whose identity starts with one prefix.

        Args:
            prefix:
                Case-insensitive prefix to match against display names and
                source ids.
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[FrameLink]: Matching visible targets in deterministic order.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        if not prefix:
            raise ValueError("prefix cannot be empty.")
        lowered_prefix = prefix.lower()
        return [
            frame_link
            for frame_link in self.list_targets(
                frame_name=frame_name,
                source_kind=source_kind,
            )
            if frame_link.display_name.lower().startswith(lowered_prefix)
            or frame_link.source_id.lower().startswith(lowered_prefix)
        ]

    def group_targets_by_kind(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, List[IFrameLink]]:
        """
        Return visible targets grouped by target kind.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, List[FrameLink]]: Visible targets grouped by source kind.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        grouped_targets: Dict[str, List[IFrameLink]] = {}
        for frame_link in self.list_targets(frame_name=frame_name):
            grouped_targets.setdefault(frame_link.source_kind, []).append(frame_link)
        return {
            source_kind: grouped_targets[source_kind]
            for source_kind in sorted(grouped_targets.keys())
        }

    def describe_target_identity(
            self,
            *,
            source_kind: str,
            source_id: str,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return a compact identity summary for one visible target.

        Purpose:
            Give the operator a stable identity/provenance snapshot for one
            currently visible target without forcing a wider payload dump.

        Args:
            source_kind:
                Required target kind.
            source_id:
                Required target source id.
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, object]: Visible target identity summary.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        frame_link = self.get_required_target_by_source(
            frame_name=frame_name,
            source_kind=source_kind,
            source_id=source_id,
        )
        descriptor = self._get_required_frame_descriptor()
        if source_kind == "frame":
            frame_overview = descriptor.frame_overview
            return {
                "frame_name": self._get_required_frame_name(),
                "target_id": frame_link.link_id,
                "source_kind": source_kind,
                "source_id": source_id,
                "display_name": frame_link.display_name,
                "frame_id": frame_overview.frame_id if frame_overview is not None else None,
                "nexus_label": (
                    frame_overview.nexus_label if frame_overview is not None else None
                ),
                "nexus_version": (
                    frame_overview.nexus_version if frame_overview is not None else None
                ),
            }
        if source_kind == "conduit":
            conduit_record = descriptor.conduit_records_by_id[source_id]
            return {
                "frame_name": self._get_required_frame_name(),
                "target_id": frame_link.link_id,
                "source_kind": source_kind,
                "source_id": source_id,
                "display_name": frame_link.display_name,
                "root_conduit_id": conduit_record.root_conduit_id,
                "origin_spellbook_id": conduit_record.origin_spellbook_id,
                "nexus_label": conduit_record.nexus_label,
                "nexus_version": conduit_record.nexus_version,
            }
        record_key = frame_link.metadata["record_key"]
        spell_record = descriptor.spell_records_by_key[record_key]
        return {
            "frame_name": self._get_required_frame_name(),
            "target_id": frame_link.link_id,
            "source_kind": source_kind,
            "source_id": source_id,
            "display_name": frame_link.display_name,
            "spell_id": spell_record.spell_id,
            "spell_index_id": spell_record.spell_index_id,
            "owner_conduit_id": spell_record.owner_conduit_id,
            "origin_spellbook_id": spell_record.origin_spellbook_id,
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

    def find_target_by_display_name(
            self,
            display_name: str,
            *,
            frame_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[IFrameLink]:
        """
        Return visible targets whose display name matches exactly.

        Purpose:
            Give the operator a fast exact-name lookup path over the currently
            visible target surface without forcing a manual target scan.

        Args:
            display_name:
                Exact display name to match.
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[FrameLink]: Matching visible targets.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        if not display_name:
            raise ValueError("display_name cannot be empty.")
        return [
            frame_link
            for frame_link in self.list_targets(
                frame_name=frame_name,
                source_kind=source_kind,
            )
            if frame_link.display_name == display_name
        ]

    def explain_target_access(
            self,
            *,
            source_kind: str,
            source_id: str,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Explain whether one target is visible and what ACL data is exposed.

        Purpose:
            Make the effective access posture explicit for one frame, conduit,
            or spell target instead of forcing the operator to infer it from
            missing results or partial payloads.

        Args:
            source_kind:
                Target kind to inspect.
            source_id:
                Target source id to inspect.
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            Dict[str, object]: Visibility and section/field explanation for the
            requested target.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        if not source_kind:
            raise ValueError("source_kind cannot be empty.")
        if not source_id:
            raise ValueError("source_id cannot be empty.")
        compiled_access_surface = self._get_required_compiled_access_surface()
        if source_kind == "frame":
            frame_overview = self._get_required_frame_descriptor().frame_overview
            target_exists = (
                frame_overview is not None
                and frame_overview.frame_id == source_id
            )
            return {
                "source_kind": "frame",
                "source_id": source_id,
                "target_exists": target_exists,
                "visible": "frame" in compiled_access_surface.allowed_kinds,
                "reason": (
                    "visible"
                    if "frame" in compiled_access_surface.allowed_kinds
                    else "not_visible_in_compiled_surface"
                ),
                "visible_fields": compiled_access_surface.frame_payload_fields,
            }
        if source_kind == "conduit":
            target_exists = (
                source_id in self._get_required_frame_descriptor().conduit_records_by_id
            )
            visible = source_id in compiled_access_surface.visible_conduit_ids
            return {
                "source_kind": "conduit",
                "source_id": source_id,
                "target_exists": target_exists,
                "visible": visible,
                "reason": "visible" if visible else "not_visible_in_compiled_surface",
                "visible_sections": (
                    compiled_access_surface.conduit_payload_sections_by_id.get(
                        source_id,
                        tuple(),
                    )
                    if visible
                    else tuple()
                ),
            }
        if source_kind == "spell":
            record_key = self._find_spell_record_key_by_source_id(source_id)
            target_exists = (
                record_key in self._get_required_frame_descriptor().spell_records_by_key
            )
            visible = record_key in compiled_access_surface.visible_spell_keys
            return {
                "source_kind": "spell",
                "source_id": source_id,
                "target_exists": target_exists,
                "visible": visible,
                "reason": "visible" if visible else "not_visible_in_compiled_surface",
                "visible_sections": (
                    compiled_access_surface.spell_payload_sections_by_key.get(
                        record_key,
                        tuple(),
                    )
                    if visible
                    else tuple()
                ),
            }
        raise ValueError("Unsupported source_kind '{0}'.".format(source_kind))

    def get_frame_payload_field(
            self,
            field_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one ACL-visible frame payload field or raise.

        Purpose:
            Provide a fail-fast, field-level access path for agent use when the
            caller needs one specific frame payload field instead of the whole
            filtered payload map.

        Contract:
            - Requires the field to be visible in the compiled ACL surface.
            - Returns the normalized field value from the bound frame payload.

        Args:
            field_name:
                Required frame payload field name.
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            object: ACL-visible frame payload field value.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        if not field_name:
            raise ValueError("field_name cannot be empty.")
        payload_description = self.describe_frame_payload(frame_name=frame_name)
        visible_fields = payload_description["visible_fields"]
        if field_name not in visible_fields:
            raise ValueError(
                "Frame payload field '{0}' is not visible for frame '{1}'.".format(
                    field_name,
                    self._get_required_frame_name(),
                )
            )
        return payload_description["payload"][field_name]

    def get_required_target_by_source(
            self,
            *,
            frame_name: Optional[str] = None,
            source_kind: str,
            source_id: str,
    ) -> IFrameLink:
        """
        Return one ACL-filtered target by source identity or raise.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.
            source_kind:
                Required target kind.
            source_id:
                Required target source identifier.

        Returns:
            FrameLink: Matching ACL-filtered target.
        """
        self.check_cleaned()
        self._assert_optional_frame_name(frame_name)
        if not source_kind:
            raise ValueError("source_kind cannot be empty.")
        if not source_id:
            raise ValueError("source_id cannot be empty.")
        for frame_link in self._build_links():
            if (
                    frame_link.source_kind == source_kind
                    and frame_link.source_id == source_id
            ):
                return frame_link
        raise ValueError(
            "ViewFrame target '{0}:{1}' was not found for frame '{2}'.".format(
                source_kind,
                source_id,
                self._get_required_frame_name(),
            )
        )

    def _build_links(self) -> List[IFrameLink]:
        """
        Build ACL-filtered `FrameLink` objects for the bound frame.

        Contract:
            - Uses the bound `FrameDescriptor` and compiled ACL surface only.
            - Preserves Nexus-contract metadata on the emitted links.
            - Raises when compiled ACL output references missing descriptor
              records.

        Returns:
            List[FrameLink]: ACL-filtered frame/conduit/spell links.
        """
        descriptor = self._get_required_frame_descriptor()
        compiled_access_surface = self._get_required_compiled_access_surface()
        frame_name = self._get_required_frame_name()
        links: List[IFrameLink] = []
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
                            "spell_index_id": spell_record.spell_index_id,
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

    @staticmethod
    def _filter_frame_payload(
            payload: Any,
            visible_fields: tuple[str, ...],
    ) -> Dict[str, object]:
        """
        Build a normalized frame payload map from ACL-visible fields.

        Args:
            payload:
                Bound `FrameDescriptorPayload`.
            visible_fields:
                Frame payload fields currently visible through the ACL surface.

        Returns:
            Dict[str, object]: Normalized visible frame payload fields.
        """
        filtered_payload: Dict[str, object] = {}
        for current_field in visible_fields:
            filtered_payload[current_field] = ViewFrame._normalize_value(
                getattr(payload, current_field)
            )
        return filtered_payload

    @staticmethod
    def _normalize_value(value: object) -> object:
        """
        Return a viewer-safe representation for one payload value.

        Args:
            value:
                Raw payload value.

        Returns:
            object: Normalized scalar/container value.
        """
        if isinstance(value, dict):
            return {
                current_key: ViewFrame._normalize_value(current_value)
                for current_key, current_value in value.items()
            }
        if isinstance(value, list):
            return [
                ViewFrame._normalize_value(current_value)
                for current_value in value
            ]
        if isinstance(value, tuple):
            return tuple(
                ViewFrame._normalize_value(current_value)
                for current_value in value
            )
        if hasattr(value, "name"):
            current_name = getattr(value, "name", None)
            if isinstance(current_name, str):
                return current_name
        return value

    @staticmethod
    def _normalize_spellframe_value(spellframe: object) -> Optional[str]:
        """
        Return one stable string view of a spellframe value.

        Args:
            spellframe:
                Raw spellframe value from a spell record.

        Returns:
            Optional[str]: Normalized spellframe value when present.
        """
        if spellframe is None:
            return None
        if isinstance(spellframe, str):
            return spellframe
        if isinstance(spellframe, type):
            return spellframe.__name__
        return str(spellframe)

    @staticmethod
    def _payload_field_names(
            payload: object,
            *,
            excluded_fields: Tuple[str, ...] = tuple(),
    ) -> Tuple[str, ...]:
        """
        Return the stable field names exposed by one payload object.

        Args:
            payload:
                Payload object whose declared fields should be enumerated.
            excluded_fields:
                Optional payload field names to exclude from the result.

        Returns:
            Tuple[str, ...]: Declared payload field names in deterministic
            order.
        """
        payload_slots = getattr(type(payload), "__slots__", tuple())
        return tuple(
            current_field_name
            for current_field_name in payload_slots
            if current_field_name not in excluded_fields
            and not current_field_name.startswith("_")
        )

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

    def _get_required_frame_name(self) -> str:
        """
        Return the bound frame name or raise when unbound.

        Returns:
            str: Bound frame name.
        """
        if self._frame_name is None:
            raise ValueError("ViewFrame is not bound to a frame.")
        return self._frame_name

    def _get_required_frame_descriptor(self) -> FrameDescriptor:
        """
        Return the bound frame descriptor or raise when unbound.

        Returns:
            FrameDescriptor: Bound descriptor reference.
        """
        if self._frame_descriptor is None:
            raise ValueError("ViewFrame has no bound FrameDescriptor.")
        return self._frame_descriptor

    def _get_required_compiled_access_surface(self) -> CompiledFrameACLAccessSurface:
        """
        Return the bound compiled ACL surface or raise when unbound.

        Returns:
            CompiledFrameACLAccessSurface: Bound compiled ACL surface.
        """
        if self._compiled_access_surface is None:
            raise ValueError(
                "ViewFrame has no bound CompiledFrameACLAccessSurface."
            )
        return self._compiled_access_surface

    @staticmethod
    def _find_spell_record_key_by_source_id(source_id: str) -> tuple[str, str]:
        """
        Convert one published spell source id into a record key tuple.

        Args:
            source_id:
                Published spell source id in `spellbook_id:spell_id` form.

        Returns:
            tuple[str, str]: Spell record key.
        """
        parts = source_id.split(":", 1)
        if len(parts) != 2:
            raise ValueError(
                "spell source_id '{0}' must be in 'spellbook_id:spell_id' form.".format(
                    source_id
                )
            )
        return parts[0], parts[1]

    def _assert_optional_frame_name(self, frame_name: Optional[str]) -> None:
        """
        Validate an optional frame-name argument against the bound frame.

        Args:
            frame_name:
                Optional frame name supplied by a caller.

        Returns:
            None.
        """
        if frame_name is None:
            return
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if frame_name != self._get_required_frame_name():
            raise ValueError(
                "ViewFrame is bound to frame '{0}', not '{1}'.".format(
                    self._get_required_frame_name(),
                    frame_name,
                )
            )

    def _iter_visible_spell_links_and_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[Tuple[IFrameLink, object]]:
        """
        Return visible spell links paired with their descriptor-owned records.

        Args:
            frame_name:
                Optional frame-name assertion. When supplied, it must match the
                bound frame.

        Returns:
            List[Tuple[FrameLink, object]]: Visible spell links paired with
            spell records.
        """
        descriptor = self._get_required_frame_descriptor()
        return [
            (
                spell_link,
                descriptor.spell_records_by_key[spell_link.metadata["record_key"]],
            )
            for spell_link in self.list_targets(
                frame_name=frame_name,
                source_kind="spell",
            )
        ]

    @staticmethod
    def _filter_grouped_collisions(
            grouped_source_ids_by_value: Dict[str, List[str]],
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return only the grouped values that collide.

        Args:
            grouped_source_ids_by_value:
                Grouped source ids by normalized value.

        Returns:
            Dict[str, Tuple[str, ...]]: Collision-only grouped source ids.
        """
        return {
            current_value: tuple(sorted(source_ids))
            for current_value, source_ids in grouped_source_ids_by_value.items()
            if len(source_ids) > 1
        }

    @staticmethod
    def _normalize_grouped_source_ids(
            grouped_source_ids_by_value: Dict[str, List[str]],
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return grouped source ids in deterministic tuple form.

        Args:
            grouped_source_ids_by_value:
                Grouped source ids by normalized value.

        Returns:
            Dict[str, Tuple[str, ...]]: Deterministically normalized groups.
        """
        return {
            current_value: tuple(sorted(source_ids))
            for current_value, source_ids in grouped_source_ids_by_value.items()
        }
