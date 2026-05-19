"""
Conduit-scoped helper surface for one selected frame view.

This module provides ACL-filtered conduit inspection and conduit-to-spell
navigation over the currently selected frame helper.
"""

from contextlib import contextmanager
import threading
from typing import Any, Dict, List, Optional, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.rift.frame_link.frame_link import FrameLink
from melder.nexus.rift.frame_viewer.view_frame import (
    ViewFrame,
)
from melder.nexus.rift.frame_viewer.view_action_hooks import (
    decorate_public_view_actions,
)
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.iconduitrecord import IConduitRecord
from melder.utilities.interfaces.iframelink import IFrameLink


@decorate_public_view_actions
class ViewConduit(Cleanable):
    """
    Purpose:
        Hold conduit-scoped viewer helper methods for one selected frame.

    Contract:
        - Operates through a borrowed `ViewFrame` helper bound to one selected
          frame.
        - Returns ACL-filtered conduit links and conduit descriptions only.

    Lifecycle:
        Cleanup is idempotent and clears the helper reference.
    """

    __melder_internal__ = _mrg.sentinel
    _ast_helper_access: str = "public"
    __agent_purpose__: str = (
        "access: public. Conduit-local helper surface for conduit identity, "
        "inventory, relationships, crosswalks, and conduit-to-spell views "
        "inside one selected frame."
    )
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_frame_view",
    ]

    _cleaned: bool

    def __init__(self, *, frame_view: Optional[ViewFrame]) -> None:
        """
        Initialize one conduit-scoped helper surface.

        Contract:
            - Holds only a borrowed reference to the selected-frame helper.
            - Does not own the bound descriptor or ACL state directly.

        Args:
            frame_view:
                Selected-frame helper used to source ACL-filtered links.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._frame_view: Optional[ViewFrame] = frame_view

    def cleanup(self) -> None:
        """
        Idempotently drop the borrowed frame-helper reference.

        Contract:
            - Safe to call more than once.
            - Runs grouped teardown under the helper-owned instance lock.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            del self._frame_view
            del self._lock

    @contextmanager
    def _entered_view_action(self, *, action_name: str) -> Any:
        """
        Enter one viewer action hook scope through the selected frame helper.

        Args:
            action_name:
                Stable viewer action name.

        Returns:
            Any: Viewer hook scope context manager.
        """
        self.check_cleaned()
        with self._get_required_frame_view()._entered_view_action(
                action_name=action_name,
        ):
            yield

    def list_conduits(self, *, frame_name: Optional[str] = None) -> List[IFrameLink]:
        """
        Return the currently visible conduit links for the selected frame.

        Contract:
            - Delegates visibility decisions to the borrowed frame helper and
              its
              compiled ACL surface.
            - Returns a fresh link snapshot for this call.

        Args:
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Conduit links for the selected frame.
        """
        self.check_cleaned()
        return self._get_required_frame_view().list_targets(
            frame_name=frame_name,
            source_kind="conduit",
        )

    def describe_conduits(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """
        Return record-aware descriptions for every visible conduit.

        Contract:
            - Materializes one `describe_conduit(...)` result per currently
              visible conduit.
            - Preserves the active ACL filtering on payload sections.

        Args:
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[Dict[str, object]]: Conduit descriptions.
        """
        self.check_cleaned()
        return [
            self.describe_conduit(
                frame_link.source_id,
                frame_name=frame_name,
            )
            for frame_link in self.list_conduits(frame_name=frame_name)
        ]

    def describe_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return a record-aware conduit description for one conduit.

        Purpose:
            Surface one `ConduitRecord` through the currently active ACL
            sections instead of only returning the flattened `FrameLink`
            metadata view.

        Contract:
            - Requires the conduit to be visible in the compiled ACL surface.
            - Returns only the conduit payload sections currently visible for
              that conduit id.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: ACL-filtered conduit description.
        """
        self.check_cleaned()
        conduit_link = self.get_required_conduit(
            conduit_id,
            frame_name=frame_name,
        )
        frame_view = self._get_required_frame_view()
        descriptor = frame_view._get_required_frame_descriptor()
        compiled_access_surface = frame_view._get_required_compiled_access_surface()
        conduit_record = descriptor.conduit_records_by_id[conduit_id]
        visible_sections = self._get_required_string_tuple(
            compiled_access_surface.conduit_payload_sections_by_id.get(
                conduit_id,
                tuple(),
            ),
            field_name="visible_sections",
        )
        return {
            "target_id": conduit_link.link_id,
            "source_kind": conduit_link.source_kind,
            "source_id": conduit_link.source_id,
            "display_name": conduit_link.display_name,
            "nexus_label": conduit_record.nexus_label,
            "nexus_version": conduit_record.nexus_version,
            "root_conduit_id": conduit_record.root_conduit_id,
            "origin_spellbook_id": conduit_record.origin_spellbook_id,
            "payload_version": conduit_record.payload.payload_version,
            "visible_sections": visible_sections,
            "payload": self._filter_conduit_payload(
                conduit_record.payload,
                visible_sections,
            ),
        }

    def list_conduit_spells(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[IFrameLink]:
        """
        Return the ACL-visible spells owned by one conduit.

        Purpose:
            Give the viewer operator a direct conduit-to-spell traversal path
            instead of forcing a full spell scan and manual filtering.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: ACL-visible spells owned by the conduit.
        """
        self.check_cleaned()
        self.get_required_conduit(conduit_id, frame_name=frame_name)
        spell_links = self._get_required_frame_view().list_targets(
            frame_name=frame_name,
            source_kind="spell",
        )
        descriptor = self._get_required_frame_view()._get_required_frame_descriptor()
        filtered_links: List[IFrameLink] = []
        for spell_link in spell_links:
            record_key = self._get_required_record_key(
                spell_link.metadata["record_key"]
            )
            spell_record = descriptor.spell_records_by_key[record_key]
            if spell_record.owner_conduit_id == conduit_id:
                filtered_links.append(spell_link)
        return filtered_links

    def describe_conduit_topology(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the visible topology around one conduit.

        Purpose:
            Show the conduit's peer links plus the visible spells currently
            owned by that conduit in one compact description.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Visible conduit topology summary.
        """
        self.check_cleaned()
        conduit_description = self.describe_conduit(
            conduit_id,
            frame_name=frame_name,
        )
        spell_links = self.list_conduit_spells(
            conduit_id,
            frame_name=frame_name,
        )
        payload = self._get_required_payload_map(conduit_description["payload"])
        return {
            "conduit_id": conduit_id,
            "peer_conduit_ids": self._get_required_string_tuple(
                payload.get("peer_conduit_ids", tuple()),
                field_name="peer_conduit_ids",
            ),
            "spell_count": len(spell_links),
            "spell_source_ids": tuple(
                spell_link.source_id
                for spell_link in spell_links
            ),
        }

    def describe_conduit_brief(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one compact operator-oriented conduit summary.

        Purpose:
            Give the operator a smaller "start here" conduit summary than the
            richer inventory and relationship methods.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Compact conduit summary.
        """
        self.check_cleaned()
        conduit_description = self.describe_conduit(
            conduit_id,
            frame_name=frame_name,
        )
        spell_links = self.list_conduit_spells(
            conduit_id,
            frame_name=frame_name,
        )
        return {
            "conduit_id": conduit_id,
            "display_name": conduit_description["display_name"],
            "is_root_conduit": self.is_root_conduit(
                conduit_id,
                frame_name=frame_name,
            ),
            "visible_section_count": len(
                self._get_required_string_tuple(
                    conduit_description["visible_sections"],
                    field_name="visible_sections",
                )
            ),
            "visible_spell_count": len(spell_links),
        }

    def describe_conduit_missing_sections(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the conduit payload sections not currently visible.

        Purpose:
            Make the conduit-local "what is hidden?" answer explicit instead of
            forcing the operator to infer it from missing payload keys.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Missing conduit-section summary.
        """
        self.check_cleaned()
        conduit_record = self._get_required_conduit_record(
            conduit_id,
            frame_name=frame_name,
        )
        conduit_description = self.describe_conduit(
            conduit_id,
            frame_name=frame_name,
        )
        all_sections = self._get_required_frame_view()._payload_field_names(
            conduit_record.payload,
            excluded_fields=("payload_version",),
        )
        visible_sections = self._get_required_string_tuple(
            conduit_description["visible_sections"],
            field_name="visible_sections",
        )
        return {
            "conduit_id": conduit_id,
            "visible_sections": visible_sections,
            "hidden_sections": tuple(
                current_section
                for current_section in all_sections
                if current_section not in visible_sections
            ),
        }

    def describe_conduit_crosswalk(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the related visible objects around one conduit.

        Purpose:
            Give the operator one direct conduit crosswalk from the conduit to
            its root, peers, owned spells, and frame context.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Conduit crosswalk summary.
        """
        self.check_cleaned()
        conduit_record = self._get_required_conduit_record(
            conduit_id,
            frame_name=frame_name,
        )
        return {
            "frame_name": self._get_required_frame_view()._get_required_frame_name(),
            "conduit_id": conduit_id,
            "root_conduit_id": conduit_record.root_conduit_id,
            "peer_conduit_ids": self.list_peer_conduit_ids(
                conduit_id,
                frame_name=frame_name,
            ),
            "peer_conduits": tuple(
                peer_link.source_id
                for peer_link in self.list_peer_conduits(
                    conduit_id,
                    frame_name=frame_name,
                )
            ),
            "spell_source_ids": self.list_spell_source_ids_for_conduit(
                conduit_id,
                frame_name=frame_name,
            ),
            "binding_names": self.list_binding_names_for_conduit(
                conduit_id,
                frame_name=frame_name,
            ),
            "spell_names": self.list_spell_names_for_conduit(
                conduit_id,
                frame_name=frame_name,
            ),
        }

    def describe_conduit_inventory(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return a compact inventory summary for one conduit.

        Purpose:
            Give the operator one quick conduit-local inventory view covering
            owned spells, peer links, and visible payload sections.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Compact conduit inventory summary.
        """
        self.check_cleaned()
        conduit_description = self.describe_conduit(
            conduit_id,
            frame_name=frame_name,
        )
        spell_links = self.list_conduit_spells(
            conduit_id,
            frame_name=frame_name,
        )
        payload = self._get_required_payload_map(conduit_description["payload"])
        peer_conduit_ids: Tuple[str, ...] = self._get_required_string_tuple(
            payload.get("peer_conduit_ids", tuple()),
            field_name="peer_conduit_ids",
        )
        return {
            "conduit_id": conduit_id,
            "is_root_conduit": self.is_root_conduit(
                conduit_id,
                frame_name=frame_name,
            ),
            "root_conduit_id": self.get_root_conduit_id(
                conduit_id,
                frame_name=frame_name,
            ),
            "visible_sections": conduit_description["visible_sections"],
            "peer_conduit_ids": peer_conduit_ids,
            "peer_count": len(peer_conduit_ids),
            "spell_count": len(spell_links),
            "spell_source_ids": tuple(
                spell_link.source_id
                for spell_link in spell_links
            ),
        }

    def describe_conduit_relationships(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the visible relationship posture for one conduit.

        Purpose:
            Make the conduit's root grouping, peer links, and owned visible
            spells explicit in one relationship-oriented view.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Visible conduit relationship summary.
        """
        self.check_cleaned()
        self.get_required_conduit(conduit_id, frame_name=frame_name)
        return {
            "conduit_id": conduit_id,
            "is_root_conduit": self.is_root_conduit(
                conduit_id,
                frame_name=frame_name,
            ),
            "root_conduit_id": self.get_root_conduit_id(
                conduit_id,
                frame_name=frame_name,
            ),
            "peer_conduit_ids": self.list_peer_conduit_ids(
                conduit_id,
                frame_name=frame_name,
            ),
            "peer_conduits": tuple(
                peer_link.source_id
                for peer_link in self.list_peer_conduits(
                    conduit_id,
                    frame_name=frame_name,
                )
            ),
            "spell_source_ids": self.list_spell_source_ids_for_conduit(
                conduit_id,
                frame_name=frame_name,
            ),
        }

    def compare_conduits(
            self,
            left_conduit_id: str,
            right_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Compare two visible conduits inside the bound frame.

        Args:
            left_conduit_id:
                Left visible conduit id.
            right_conduit_id:
                Right visible conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Visible conduit comparison summary.
        """
        self.check_cleaned()
        left_conduit_record = self._get_required_conduit_record(
            left_conduit_id,
            frame_name=frame_name,
        )
        right_conduit_record = self._get_required_conduit_record(
            right_conduit_id,
            frame_name=frame_name,
        )
        left_spell_source_ids = self.list_spell_source_ids_for_conduit(
            left_conduit_id,
            frame_name=frame_name,
        )
        right_spell_source_ids = self.list_spell_source_ids_for_conduit(
            right_conduit_id,
            frame_name=frame_name,
        )
        return {
            "left_conduit_id": left_conduit_id,
            "right_conduit_id": right_conduit_id,
            "same_root_conduit_id": (
                left_conduit_record.root_conduit_id
                == right_conduit_record.root_conduit_id
            ),
            "same_policy": (
                self._normalize_policy_name(left_conduit_record.payload.policy)
                == self._normalize_policy_name(right_conduit_record.payload.policy)
            ),
            "same_conduit_state": (
                left_conduit_record.payload.conduit_state.name
                == right_conduit_record.payload.conduit_state.name
            ),
            "peer_conduit_ids": self._compare_sorted_value_sets(
                tuple(left_conduit_record.payload.peer_conduit_ids),
                tuple(right_conduit_record.payload.peer_conduit_ids),
            ),
            "visible_spell_source_ids": self._compare_sorted_value_sets(
                left_spell_source_ids,
                right_spell_source_ids,
            ),
        }

    def list_root_conduits(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[IFrameLink]:
        """
        Return visible conduit links that are root conduits.

        Args:
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Visible root conduit links.
        """
        self.check_cleaned()
        frame_view = self._get_required_frame_view()
        return frame_view.list_visible_root_conduits(frame_name=frame_name)

    def is_root_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> bool:
        """
        Return whether one visible conduit is its own root.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            bool: True when the conduit is a root conduit.
        """
        self.check_cleaned()
        conduit_record = self._get_required_conduit_record(
            conduit_id,
            frame_name=frame_name,
        )
        return conduit_record.conduit_id == conduit_record.root_conduit_id

    def get_root_conduit_id(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> str:
        """
        Return the root conduit id for one visible conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            str: Root conduit id for the conduit.
        """
        self.check_cleaned()
        conduit_record = self._get_required_conduit_record(
            conduit_id,
            frame_name=frame_name,
        )
        return conduit_record.root_conduit_id

    def list_conduits_by_root_id(
            self,
            root_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[IFrameLink]:
        """
        Return visible conduits grouped under one root conduit id.

        Args:
            root_conduit_id:
                Required root conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Visible conduits whose root lineage matches.
        """
        self.check_cleaned()
        if not root_conduit_id:
            raise ValueError("root_conduit_id cannot be empty.")
        matching_conduits: List[IFrameLink] = []
        for conduit_link in self.list_conduits(frame_name=frame_name):
            conduit_record = self._get_required_conduit_record(
                conduit_link.source_id,
                frame_name=frame_name,
            )
            if conduit_record.root_conduit_id == root_conduit_id:
                matching_conduits.append(conduit_link)
        return matching_conduits

    def list_conduits_by_policy(
            self,
            policy_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[IFrameLink]:
        """
        Return visible conduits with one conduit policy value.

        Args:
            policy_name:
                Required conduit policy name.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Visible conduits whose payload policy matches.
        """
        self.check_cleaned()
        if not policy_name:
            raise ValueError("policy_name cannot be empty.")
        normalized_policy_name = policy_name.lower()
        matching_conduits: List[IFrameLink] = []
        for conduit_link in self.list_conduits(frame_name=frame_name):
            conduit_record = self._get_required_conduit_record(
                conduit_link.source_id,
                frame_name=frame_name,
            )
            current_policy_name = self._normalize_policy_name(
                conduit_record.payload.policy
            )
            if current_policy_name is None:
                continue
            if current_policy_name.lower() == normalized_policy_name:
                matching_conduits.append(conduit_link)
        return matching_conduits

    def list_conduits_by_state(
            self,
            state_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[IFrameLink]:
        """
        Return visible conduits with one conduit-state value.

        Args:
            state_name:
                Required conduit-state name.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Visible conduits whose payload state matches.
        """
        self.check_cleaned()
        if not state_name:
            raise ValueError("state_name cannot be empty.")
        normalized_state_name = state_name.lower()
        matching_conduits: List[IFrameLink] = []
        for conduit_link in self.list_conduits(frame_name=frame_name):
            conduit_record = self._get_required_conduit_record(
                conduit_link.source_id,
                frame_name=frame_name,
            )
            current_state_name = conduit_record.payload.conduit_state.name
            if current_state_name.lower() == normalized_state_name:
                matching_conduits.append(conduit_link)
        return matching_conduits

    def list_peer_conduits(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[IFrameLink]:
        """
        Return visible peer conduit links for one conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Visible peer conduit links.
        """
        self.check_cleaned()
        peer_conduit_ids = set(
            self.list_peer_conduit_ids(
                conduit_id,
                frame_name=frame_name,
            )
        )
        return [
            conduit_link
            for conduit_link in self.list_conduits(frame_name=frame_name)
            if conduit_link.source_id in peer_conduit_ids
        ]

    def list_peer_conduit_ids(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return visible peer conduit ids for one conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Tuple[str, ...]: Visible peer conduit ids in deterministic order.
        """
        self.check_cleaned()
        conduit_record = self._get_required_conduit_record(
            conduit_id,
            frame_name=frame_name,
        )
        visible_conduit_ids = set(
            conduit_link.source_id
            for conduit_link in self.list_conduits(frame_name=frame_name)
        )
        return tuple(
            peer_conduit_id
            for peer_conduit_id in conduit_record.payload.peer_conduit_ids
            if peer_conduit_id in visible_conduit_ids
        )

    def list_spell_source_ids_for_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return visible spell source ids owned by one conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Tuple[str, ...]: Visible spell source ids owned by the conduit.
        """
        self.check_cleaned()
        return tuple(
            spell_link.source_id
            for spell_link in self.list_conduit_spells(
                conduit_id,
                frame_name=frame_name,
            )
        )

    def list_binding_names_for_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return visible spell binding names owned by one conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Tuple[str, ...]: Visible binding names owned by the conduit.
        """
        self.check_cleaned()
        frame_view = self._get_required_frame_view()
        descriptor = frame_view._get_required_frame_descriptor()
        binding_names: List[str] = []
        for spell_link in self.list_conduit_spells(
                conduit_id,
                frame_name=frame_name,
        ):
            record_key = self._get_required_record_key(
                spell_link.metadata["record_key"]
            )
            binding_name = descriptor.spell_records_by_key[record_key].binding_name
            if binding_name is None:
                continue
            binding_names.append(binding_name)
        return tuple(binding_names)

    def list_spell_names_for_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return visible spell names owned by one conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Tuple[str, ...]: Visible spell names owned by the conduit.
        """
        self.check_cleaned()
        frame_view = self._get_required_frame_view()
        descriptor = frame_view._get_required_frame_descriptor()
        return tuple(
            descriptor.spell_records_by_key[
                self._get_required_record_key(
                    spell_link.metadata["record_key"]
                )
            ].spell_name
            for spell_link in self.list_conduit_spells(
                conduit_id,
                frame_name=frame_name,
            )
        )

    def describe_conduit_access_summary(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one compact access/inventory summary for a conduit.

        Purpose:
            Combine the conduit access explanation, relationship view, and
            compact inventory so the operator can decide quickly whether to go
            deeper on that conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Compact conduit access summary.
        """
        self.check_cleaned()
        return {
            "conduit_id": conduit_id,
            "access": self.explain_conduit_access(
                conduit_id,
                frame_name=frame_name,
            ),
            "inventory": self.describe_conduit_inventory(
                conduit_id,
                frame_name=frame_name,
            ),
            "relationships": self.describe_conduit_relationships(
                conduit_id,
                frame_name=frame_name,
            ),
        }

    def find_conduit_by_name(
            self,
            conduit_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[IFrameLink]:
        """
        Return visible conduits whose display name matches exactly.

        Args:
            conduit_name:
                Exact conduit display name.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Matching visible conduit links.
        """
        self.check_cleaned()
        if not conduit_name:
            raise ValueError("conduit_name cannot be empty.")
        return [
            conduit_link
            for conduit_link in self.list_conduits(frame_name=frame_name)
            if conduit_link.display_name == conduit_name
        ]

    def explain_conduit_access(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Explain the effective ACL access posture for one conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Conduit visibility and section explanation.
        """
        self.check_cleaned()
        explanation = self._get_required_frame_view().explain_target_access(
            frame_name=frame_name,
            source_kind="conduit",
            source_id=conduit_id,
        )
        visible_sections = self._get_required_string_tuple(
            explanation["visible_sections"],
            field_name="visible_sections",
        )
        return {
            **explanation,
            "payload_visible": (
                "conduit_name" in visible_sections
                or "conduit_state" in visible_sections
            ),
            "policy_visible": "policy" in visible_sections,
            "peer_links_visible": "peer_conduit_ids" in visible_sections,
        }

    def get_conduit_payload_field(
            self,
            conduit_id: str,
            field_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one ACL-visible conduit payload field or raise.

        Args:
            conduit_id:
                Published conduit id.
            field_name:
                Required conduit payload field name.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            object: ACL-visible conduit payload field value.
        """
        self.check_cleaned()
        if not field_name:
            raise ValueError("field_name cannot be empty.")
        conduit_description = self.describe_conduit(
            conduit_id,
            frame_name=frame_name,
        )
        visible_sections = self._get_required_string_tuple(
            conduit_description["visible_sections"],
            field_name="visible_sections",
        )
        if field_name not in visible_sections:
            raise ValueError(
                "Conduit payload field '{0}' is not visible for conduit '{1}'.".format(
                    field_name,
                    conduit_id,
                )
            )
        payload = self._get_required_payload_map(conduit_description["payload"])
        return payload[field_name]

    def get_required_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> IFrameLink:
        """
        Return one conduit link by conduit id or raise.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            FrameLink: Matching conduit link.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        return self._get_required_frame_view().get_required_target_by_source(
            frame_name=frame_name,
            source_kind="conduit",
            source_id=conduit_id,
        )

    def _get_required_frame_view(self) -> ViewFrame:
        """
        Return the borrowed frame helper or raise when unbound.

        Returns:
            ViewFrame: Borrowed frame helper surface.
        """
        if self._frame_view is None:
            raise ValueError("ViewConduit is not bound to a frame view.")
        return self._frame_view

    @staticmethod
    def _get_required_record_key(record_key: object) -> Tuple[str, str]:
        """
        Return one validated spell-record key.

        Args:
            record_key:
                Candidate spell-record key from frame-link metadata.

        Returns:
            Tuple[str, str]: Validated `(origin_spellbook_id, spell_id)` key.
        """
        if (
                not isinstance(record_key, tuple)
                or len(record_key) != 2
                or not isinstance(record_key[0], str)
                or not isinstance(record_key[1], str)
        ):
            raise TypeError(
                "spell_link.metadata['record_key'] must be a tuple[str, str]."
            )
        return record_key[0], record_key[1]

    @staticmethod
    def _get_required_string_tuple(
            values: object,
            *,
            field_name: str,
    ) -> Tuple[str, ...]:
        """
        Return one validated tuple of string values.

        Args:
            values:
                Candidate iterable of string values.
            field_name:
                User-facing field name used in validation errors.

        Returns:
            Tuple[str, ...]: Validated string tuple.
        """
        if not isinstance(values, (tuple, list)):
            raise TypeError(
                "{0} must be a tuple[str, ...].".format(field_name)
            )
        normalized_values: List[str] = []
        for current_value in values:
            if not isinstance(current_value, str):
                raise TypeError(
                    "{0} must contain only strings.".format(field_name)
                )
            normalized_values.append(current_value)
        return tuple(normalized_values)

    @staticmethod
    def _get_required_payload_map(payload: object) -> Dict[str, object]:
        """
        Return one validated conduit payload mapping.

        Args:
            payload:
                Candidate conduit payload map.

        Returns:
            Dict[str, object]: Validated conduit payload map.
        """
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict[str, object].")
        normalized_payload: Dict[str, object] = {}
        for current_key, current_value in payload.items():
            if not isinstance(current_key, str):
                raise TypeError("payload keys must be strings.")
            normalized_payload[current_key] = current_value
        return normalized_payload

    def _get_required_conduit_record(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> IConduitRecord:
        """
        Return one descriptor-owned conduit record or raise.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            IConduitRecord: Descriptor-owned conduit record.
        """
        self.get_required_conduit(conduit_id, frame_name=frame_name)
        descriptor = self._get_required_frame_view()._get_required_frame_descriptor()
        return descriptor.conduit_records_by_id[conduit_id]

    @staticmethod
    def _normalize_policy_name(policy: Optional[Policies]) -> Optional[str]:
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

    @staticmethod
    def _filter_conduit_payload(
            payload: object,
            visible_sections: tuple[str, ...],
    ) -> Dict[str, object]:
        """
        Build a normalized conduit payload map from ACL-visible sections.

        Args:
            payload:
                Bound `ConduitDescriptorPayload`.
            visible_sections:
                ACL-visible conduit payload section names.

        Returns:
            Dict[str, object]: Normalized visible conduit payload fields.
        """
        filtered_payload: Dict[str, object] = {}
        for current_section in visible_sections:
            filtered_payload[current_section] = ViewFrame._normalize_value(
                getattr(payload, current_section)
            )
        return filtered_payload

