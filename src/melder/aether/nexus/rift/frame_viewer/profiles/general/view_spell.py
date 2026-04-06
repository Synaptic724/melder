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

    def describe_spell_payload(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return only the ACL-filtered spell payload body.

        Purpose:
            Give the main viewer operator a stable, payload-focused spell read
            surface without the wider record wrapper.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the shared frame
                helper.

        Returns:
            Dict[str, object]: Spell payload summary.
        """
        self.check_cleaned()
        spell_description = self.describe_spell(
            spell_source_id,
            frame_name=frame_name,
        )
        return {
            "payload_type": spell_description["payload_type"],
            "payload_version": spell_description["payload_version"],
            "visible_sections": spell_description["visible_sections"],
            "payload": spell_description["payload"],
        }

    def describe_spell_detail(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the richer detail posture for one spell when available.

        Purpose:
            Separate the "try to go deep" path from the normal spell summary so
            the operator can ask for richer detail explicitly and still get a
            truthful answer when the detail is unavailable because of the
            payload type or ACL restrictions.

        Contract:
            - When `payload_type` is not `detailed`, returns
              `detail_available=False` with reason `payload_not_detailed`.
            - When the payload is `detailed` but no rich sections are ACL-
              visible, returns `detail_available=False` with reason
              `acl_restricted`.
            - When rich sections are visible, returns only the rich payload
              sections currently present in the payload body.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the shared frame
                helper.

        Returns:
            Dict[str, object]: Rich detail status and payload.
        """
        self.check_cleaned()
        spell_description = self.describe_spell(
            spell_source_id,
            frame_name=frame_name,
        )
        payload_type = spell_description["payload_type"]
        if payload_type != "detailed":
            return {
                "spell_source_id": spell_source_id,
                "payload_type": payload_type,
                "detail_available": False,
                "reason": "payload_not_detailed",
                "visible_sections": spell_description["visible_sections"],
                "payload": {},
            }
        rich_section_names = (
            "class_profile",
            "callable_profile",
            "instance_members",
            "dynamic_access",
        )
        rich_payload = {
            current_section: spell_description["payload"][current_section]
            for current_section in rich_section_names
            if current_section in spell_description["payload"]
        }
        if len(rich_payload) == 0:
            return {
                "spell_source_id": spell_source_id,
                "payload_type": payload_type,
                "detail_available": False,
                "reason": "acl_restricted",
                "visible_sections": spell_description["visible_sections"],
                "payload": {},
            }
        return {
            "spell_source_id": spell_source_id,
            "payload_type": payload_type,
            "detail_available": True,
            "reason": "available",
            "visible_sections": spell_description["visible_sections"],
            "payload": rich_payload,
        }

    def list_spells_by_payload_type(
            self,
            payload_type: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells whose published payload type matches exactly.

        Args:
            payload_type:
                Required spell payload type.
            frame_name:
                Optional frame-name assertion passed through to the shared frame
                helper.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        self.check_cleaned()
        if not payload_type:
            raise ValueError("payload_type cannot be empty.")
        matching_spells: List[FrameLink] = []
        frame_view = self._get_required_frame_view()
        descriptor = frame_view._get_required_frame_descriptor()
        for spell_link in self.list_spells(frame_name=frame_name):
            record_key = spell_link.metadata["record_key"]
            spell_record = descriptor.spell_records_by_key[record_key]
            if spell_record.payload.payload_type == payload_type:
                matching_spells.append(spell_link)
        return matching_spells

    def find_spell_by_binding_name(
            self,
            binding_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells whose binding name matches exactly.

        Args:
            binding_name:
                Exact published binding name.
            frame_name:
                Optional frame-name assertion passed through to the shared frame
                helper.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        self.check_cleaned()
        if not binding_name:
            raise ValueError("binding_name cannot be empty.")
        return [
            spell_link
            for spell_link in self.list_spells(frame_name=frame_name)
            if spell_link.display_name == binding_name
        ]

    def explain_spell_access(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Explain the effective ACL access posture for one spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the shared frame
                helper.

        Returns:
            Dict[str, object]: Spell visibility, section, and detail posture
            explanation.
        """
        self.check_cleaned()
        explanation = self._get_required_frame_view().explain_target_access(
            frame_name=frame_name,
            source_kind="spell",
            source_id=spell_source_id,
        )
        detail = self.describe_spell_detail(
            spell_source_id,
            frame_name=frame_name,
        )
        visible_sections = tuple(explanation["visible_sections"])
        return {
            **explanation,
            "payload_type": detail["payload_type"],
            "detail_available": detail["detail_available"],
            "detail_reason": detail["reason"],
            "binding_payload_visible": "binding_payload" in visible_sections,
            "resolution_payload_visible": "resolution_payload" in visible_sections,
            "metadata_visible": "metadata" in visible_sections,
            "rich_sections_visible": tuple(
                section_name
                for section_name in (
                    "class_profile",
                    "callable_profile",
                    "instance_members",
                    "dynamic_access",
                )
                if section_name in visible_sections
            ),
        }

    def get_spell_payload_section(
            self,
            spell_source_id: str,
            section_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one ACL-visible spell payload section or raise.

        Args:
            spell_source_id:
                Published spell source id.
            section_name:
                Required spell payload section name.
            frame_name:
                Optional frame-name assertion passed through to the shared frame
                helper.

        Returns:
            object: ACL-visible spell payload section value.
        """
        self.check_cleaned()
        if not section_name:
            raise ValueError("section_name cannot be empty.")
        spell_description = self.describe_spell(
            spell_source_id,
            frame_name=frame_name,
        )
        visible_sections = spell_description["visible_sections"]
        if section_name not in visible_sections:
            raise ValueError(
                "Spell payload section '{0}' is not visible for spell '{1}'.".format(
                    section_name,
                    spell_source_id,
                )
            )
        payload = spell_description["payload"]
        if section_name not in payload:
            raise ValueError(
                "Spell payload section '{0}' is not available in the published payload for spell '{1}'.".format(
                    section_name,
                    spell_source_id,
                )
            )
        return payload[section_name]

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
