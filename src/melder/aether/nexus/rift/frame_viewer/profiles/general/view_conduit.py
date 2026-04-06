from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.aether.nexus.rift.frame_viewer.profiles.general.view_frame import (
    GeneralViewFrame,
)
from melder.utilities.general_base.cleanable import Cleanable


class GeneralViewConduit(Cleanable):
    """
    Purpose:
        Hold conduit-scoped viewer helper methods for the `general` profile.

    Contract:
        - Operates on one bound frame through the shared frame helper surface.
        - Returns ACL-filtered conduit links and conduit descriptions only.

    Lifecycle:
        Cleanup is idempotent and clears the helper reference.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_frame_view",
    ]

    def __init__(self, *, frame_view: Optional[GeneralViewFrame]) -> None:
        """
        Initialize one conduit-scoped helper surface.

        Args:
            frame_view:
                Shared frame helper used to source ACL-filtered links.

        Returns:
            None.
        """
        super().__init__()
        self._frame_view: Optional[GeneralViewFrame] = frame_view

    def cleanup(self) -> None:
        """
        Idempotently clear the helper surface.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._frame_view = None

    def list_conduits(self, *, frame_name: Optional[str] = None) -> List[FrameLink]:
        """
        Return ACL-filtered conduit links for the bound frame.

        Args:
            frame_name:
                Optional frame-name assertion passed through to the shared frame
                helper.

        Returns:
            List[FrameLink]: Conduit links for the bound frame.
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
        Return conduit descriptions for the bound frame.

        Args:
            frame_name:
                Optional frame-name assertion passed through to the shared frame
                helper.

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
                Optional frame-name assertion passed through to the shared frame
                helper.

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
        visible_sections = tuple(
            compiled_access_surface.conduit_payload_sections_by_id.get(
                conduit_id,
                tuple(),
            )
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
    ) -> List[FrameLink]:
        """
        Return the ACL-visible spells owned by one conduit.

        Purpose:
            Give the viewer operator a direct conduit-to-spell traversal path
            instead of forcing a full spell scan and manual filtering.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the shared frame
                helper.

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
        filtered_links: List[FrameLink] = []
        for spell_link in spell_links:
            record_key = spell_link.metadata["record_key"]
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
                Optional frame-name assertion passed through to the shared frame
                helper.

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
        return {
            "conduit_id": conduit_id,
            "peer_conduit_ids": tuple(
                conduit_description["payload"].get("peer_conduit_ids", tuple())
            ),
            "spell_count": len(spell_links),
            "spell_source_ids": tuple(
                spell_link.source_id
                for spell_link in spell_links
            ),
        }

    def get_required_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> FrameLink:
        """
        Return one conduit link by conduit id or raise.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the shared frame
                helper.

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

    def _get_required_frame_view(self) -> GeneralViewFrame:
        """
        Return the shared frame helper or raise when unbound.

        Returns:
            GeneralViewFrame: Shared frame helper surface.
        """
        if self._frame_view is None:
            raise ValueError("GeneralViewConduit is not bound to a frame view.")
        return self._frame_view

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
            filtered_payload[current_section] = GeneralViewFrame._normalize_value(
                getattr(payload, current_section)
            )
        return filtered_payload
