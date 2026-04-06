from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.aether.nexus.rift.frame_viewer.profiles.general.view_frame import (
    GeneralViewFrame,
)
from melder.utilities.general_base.cleanable import Cleanable


class GeneralViewSpell(Cleanable):
    """
    Purpose:
        Hold spell-scoped viewer helper methods for the `general` profile.

    Contract:
        - Operates on one bound frame through the shared frame helper surface.
        - Returns ACL-filtered spell links and spell descriptions only.

    Lifecycle:
        Cleanup is idempotent and clears the helper reference.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_frame_view",
    ]

    def __init__(self, *, frame_view: Optional[GeneralViewFrame]) -> None:
        """
        Initialize one spell-scoped helper surface.

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

    def list_spells(self, *, frame_name: Optional[str] = None) -> List[FrameLink]:
        """
        Return ACL-filtered spell links for the bound frame.

        Args:
            frame_name:
                Optional frame-name assertion passed through to the shared frame
                helper.

        Returns:
            List[FrameLink]: Spell links for the bound frame.
        """
        self.check_cleaned()
        return self._get_required_frame_view().list_targets(
            frame_name=frame_name,
            source_kind="spell",
        )

    def describe_spells(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """
        Return spell descriptions for the bound frame.

        Args:
            frame_name:
                Optional frame-name assertion passed through to the shared frame
                helper.

        Returns:
            List[Dict[str, object]]: Spell descriptions.
        """
        self.check_cleaned()
        return [
            self.describe_spell(
                frame_link.source_id,
                frame_name=frame_name,
            )
            for frame_link in self.list_spells(frame_name=frame_name)
        ]

    def describe_spell(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return a record-aware spell description for one spell.

        Purpose:
            Surface one `SpellRecord` through the currently active ACL sections
            while gracefully degrading when the published spell payload is only
            `general` and therefore lacks richer `detailed` payload content.

        Contract:
            - Requires the spell to be visible in the compiled ACL surface.
            - Returns only the spell payload sections currently visible for the
              spell record key.
            - Omits richer fields when the payload does not actually publish
              them, even if a more permissive ACL would have allowed them.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional frame-name assertion passed through to the shared frame
                helper.

        Returns:
            Dict[str, object]: ACL-filtered spell description.
        """
        self.check_cleaned()
        spell_link = self.get_required_spell(
            spell_source_id,
            frame_name=frame_name,
        )
        frame_view = self._get_required_frame_view()
        descriptor = frame_view._get_required_frame_descriptor()
        compiled_access_surface = frame_view._get_required_compiled_access_surface()
        record_key = spell_link.metadata["record_key"]
        spell_record = descriptor.spell_records_by_key[record_key]
        visible_sections = tuple(
            compiled_access_surface.spell_payload_sections_by_key.get(
                record_key,
                tuple(),
            )
        )
        return {
            "target_id": spell_link.link_id,
            "source_kind": spell_link.source_kind,
            "source_id": spell_link.source_id,
            "display_name": spell_link.display_name,
            "nexus_label": spell_record.nexus_label,
            "nexus_version": spell_record.nexus_version,
            "spell_id": spell_record.spell_id,
            "lineage_id": spell_record.lineage_id,
            "owner_conduit_id": spell_record.owner_conduit_id,
            "payload_type": spell_record.payload.payload_type,
            "payload_version": spell_record.payload.payload_version,
            "source_profile_name": spell_record.payload.source_profile_name,
            "source_profile_version": spell_record.payload.source_profile_version,
            "visible_sections": visible_sections,
            "payload": self._filter_spell_payload(
                spell_record.payload,
                visible_sections,
            ),
        }

    def get_required_spell(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> FrameLink:
        """
        Return one spell link by published source id or raise.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the shared frame
                helper.

        Returns:
            FrameLink: Matching spell link.
        """
        self.check_cleaned()
        if not spell_source_id:
            raise ValueError("spell_source_id cannot be empty.")
        return self._get_required_frame_view().get_required_target_by_source(
            frame_name=frame_name,
            source_kind="spell",
            source_id=spell_source_id,
        )

    def _get_required_frame_view(self) -> GeneralViewFrame:
        """
        Return the shared frame helper or raise when unbound.

        Returns:
            GeneralViewFrame: Shared frame helper surface.
        """
        if self._frame_view is None:
            raise ValueError("GeneralViewSpell is not bound to a frame view.")
        return self._frame_view

    @staticmethod
    def _filter_spell_payload(
            payload: object,
            visible_sections: tuple[str, ...],
    ) -> Dict[str, object]:
        """
        Build a normalized spell payload map from ACL-visible sections.

        Purpose:
            Preserve ACL filtering while avoiding failures when the published
            spell payload does not include richer `detailed` fields.

        Args:
            payload:
                Bound `SpellDescriptorPayload`.
            visible_sections:
                ACL-visible spell payload section names.

        Returns:
            Dict[str, object]: Normalized visible spell payload fields.
        """
        filtered_payload: Dict[str, object] = {}
        for current_section in visible_sections:
            current_value = getattr(payload, current_section)
            if current_value is None:
                continue
            if isinstance(current_value, dict) and len(current_value) == 0:
                continue
            filtered_payload[current_section] = GeneralViewFrame._normalize_value(
                current_value
            )
        return filtered_payload
