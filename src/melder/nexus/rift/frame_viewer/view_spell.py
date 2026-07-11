"""
Spell-scoped helper surface for one selected frame view.

This module provides ACL-filtered spell inspection, payload reads, spell-index
queries, and spell comparison behavior over the currently selected frame
helper.
"""

from contextlib import contextmanager
import threading
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.rift.frame_viewer.view_frame import (
    ViewFrame,
)
from melder.nexus.rift.frame_viewer.view_action_hooks import (
    decorate_public_view_actions,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.profiles.class_profile import (
    ClassProfile,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.profiles.method_profile import (
    MethodProfile,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.frame_descriptor.spell_record import SpellRecord
    from melder.nexus.rift.frame_link.frame_link import FrameLink


@decorate_public_view_actions
class ViewSpell(Cleanable):
    """
    Purpose:
        Hold spell-scoped viewer helper methods for one selected frame.

    Contract:
        - Operates through a borrowed `ViewFrame` helper bound to one selected
          frame.
        - Returns ACL-filtered spell links and spell descriptions only.

    Lifecycle:
        Cleanup is idempotent and clears the helper reference.
    """

    __melder_internal__ = _mrg.sentinel
    _ast_helper_access: str = "public"
    __agent_purpose__: str = (
        "access: public. Spell-local helper surface for spell identity, "
        "origin, spell-index grouping, filtering, detailed payload access, dunder-member "
        "visibility, and spell crosswalk/comparison flows inside one selected "
        "frame."
    )
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_frame_view",
    ]

    _cleaned: bool

    def __init__(self, *, frame_view: Optional[ViewFrame]) -> None:
        """
        Initialize one spell-scoped helper surface.

        Contract:
            - Holds only a borrowed reference to the selected-frame helper.
            - Reads descriptor and ACL state indirectly through that helper.

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
            self._frame_view = None

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

    def list_spells(self, *, frame_name: Optional[str] = None) -> List[FrameLink]:
        """
        Return the currently visible spell links for the selected frame.

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
            List[FrameLink]: Spell links for the selected frame.
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
        Return record-aware descriptions for every visible spell.

        Contract:
            - Materializes one `describe_spell(...)` result per currently
              visible spell link.
            - Preserves the active ACL filtering and payload-type degradation
              semantics of the spell helper.

        Args:
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

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
                Optional frame-name assertion passed through to the selected-
                frame helper.

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
        record_key = self._get_required_record_key(
            spell_link.metadata["record_key"]
        )
        spell_record = descriptor.spell_records_by_key[record_key]
        visible_sections = self._get_required_visible_sections(
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
            "spell_index_id": spell_record.spell_index_id,
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
                Optional frame-name assertion passed through to the selected-
                frame helper.

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
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Rich detail status and payload.
        """
        self.check_cleaned()
        spell_description = self.describe_spell(
            spell_source_id,
            frame_name=frame_name,
        )
        payload_type = spell_description["payload_type"]
        visible_sections = self._get_required_visible_sections(
            spell_description["visible_sections"]
        )
        payload = self._get_required_payload_map(spell_description["payload"])
        if payload_type != "detailed":
            return {
                "spell_source_id": spell_source_id,
                "payload_type": payload_type,
                "detail_available": False,
                "reason": "payload_not_detailed",
                "visible_sections": visible_sections,
                "payload": {},
            }
        rich_section_names = (
            "class_profile",
            "callable_profile",
            "instance_members",
            "dynamic_access",
        )
        rich_payload = {
            current_section: payload[current_section]
            for current_section in rich_section_names
            if current_section in payload
        }
        if len(rich_payload) == 0:
            return {
                "spell_source_id": spell_source_id,
                "payload_type": payload_type,
                "detail_available": False,
                "reason": "acl_restricted",
                "visible_sections": visible_sections,
                "payload": {},
            }
        return {
            "spell_source_id": spell_source_id,
            "payload_type": payload_type,
            "detail_available": True,
            "reason": "available",
            "visible_sections": visible_sections,
            "payload": rich_payload,
        }

    def describe_spell_brief(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one compact operator-oriented spell summary.

        Purpose:
            Give the operator a smaller spell summary than the richer identity,
            access, and detail methods when they just need the essentials.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Compact spell summary.
        """
        self.check_cleaned()
        spell_description = self.describe_spell(
            spell_source_id,
            frame_name=frame_name,
        )
        return {
            "source_id": spell_source_id,
            "display_name": spell_description["display_name"],
            "payload_type": spell_description["payload_type"],
            "visible_section_count": len(
                self._get_required_visible_sections(
                    spell_description["visible_sections"]
                )
            ),
            "detail_reason": self.describe_spell_detail(
                spell_source_id,
                frame_name=frame_name,
            )["reason"],
        }

    def describe_spell_missing_sections(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the spell payload sections not currently visible or published.

        Purpose:
            Make the spell-local "what is missing and why?" answer explicit
            instead of forcing the operator to infer it from absent detail
            fields.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Missing spell-section summary.
        """
        self.check_cleaned()
        spell_record = self._get_required_spell_record(
            spell_source_id,
            frame_name=frame_name,
        )
        spell_description = self.describe_spell(
            spell_source_id,
            frame_name=frame_name,
        )
        all_sections = self._get_required_frame_view()._payload_field_names(
            spell_record.payload,
            excluded_fields=(
                "payload_type",
                "payload_version",
                "source_profile_name",
                "source_profile_version",
            ),
        )
        visible_sections = self._get_required_visible_sections(
            spell_description["visible_sections"]
        )
        payload = self._get_required_payload_map(spell_description["payload"])
        published_sections = tuple(sorted(payload.keys()))
        return {
            "source_id": spell_source_id,
            "visible_sections": visible_sections,
            "published_sections": published_sections,
            "hidden_sections": tuple(
                current_section
                for current_section in all_sections
                if current_section not in visible_sections
            ),
            "not_published_sections": tuple(
                current_section
                for current_section in visible_sections
                if current_section not in published_sections
            ),
        }

    def describe_spell_identity(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the stable identity fields for one visible spell.

        Purpose:
            Give the operator a narrow identity view over one spell record
            without forcing a wider payload or access-contract dump first.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Stable identity fields for the visible spell.
        """
        self.check_cleaned()
        spell_record = self._get_required_spell_record(
            spell_source_id,
            frame_name=frame_name,
        )
        return {
            "source_id": spell_source_id,
            "record_key": spell_record.record_key,
            "spell_id": spell_record.spell_id,
            "spell_index_id": spell_record.spell_index_id,
            "spell_name": spell_record.spell_name,
            "binding_name": spell_record.binding_name,
            "spellframe": self._normalize_spellframe_value(spell_record.spellframe),
            "permissions": spell_record.permissions.name,
            "existence": spell_record.existence.name,
            "payload_type": spell_record.payload.payload_type,
            "payload_version": spell_record.payload.payload_version,
        }

    def describe_spell_research(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the research annotation for one visible spell.

        Purpose:
            Join the viewer's runtime truth with the MutationResearch record:
            whether this spell's identity is formally declared research, which
            lane holds it, and its query-time residency verdict - alongside
            the identity the operator already sees.

        Contract:
            - Non-constructing peek: the viewer never births the MR root.
            - Honest unavailability: an absent or inactive root returns
              `research_available=False` with a named reason instead of
              raising - viewing a spell must never fail on research state.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: `source_id`, `spell_id`, and either the
            residency payload (declared/lane/runtime/custody) or the
            unavailability reason.
        """
        self.check_cleaned()
        identity = self.describe_spell_identity(
            spell_source_id,
            frame_name=frame_name,
        )
        spell_id = identity["spell_id"]
        from melder.aether.aether import Aether

        aether = Aether._instance
        research = (
            aether._mutation_research if aether is not None else None
        )
        if research is None or research.cleaned or not research.activated:
            return {
                "source_id": spell_source_id,
                "spell_id": spell_id,
                "research_available": False,
                "reason": "mutation_research_not_active",
            }
        residency = research.residency_view(spell_id)
        residency["source_id"] = spell_source_id
        residency["research_available"] = True
        return residency

    def describe_spell_source(
            self,
            spell_source_id: str,
            *,
            module_name: Optional[str] = None,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the recorded source of one visible spell's module world.

        Purpose:
            Foresight read for the operator: the actual code behind the spell
            they are looking at - recorded custody text first (synthetic
            always recorded; user text when retained), live-disk fallback
            with a drift marker, honest text_unavailable otherwise.

        Contract:
            - Non-constructing peek: routes through the SAME MutationResearch
              door as `describe_spell_research`; the viewer never births the
              MR root.
            - Honest unavailability: an absent or inactive root returns
              `research_available=False` with a named reason instead of
              raising - viewing a spell must never fail on research state.

        Args:
            spell_source_id:
                Published spell source id.
            module_name:
                Optional single module of the world to return.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: `source_id`, `spell_id`, and either the
            per-module source payload or the unavailability reason.
        """
        self.check_cleaned()
        identity = self.describe_spell_identity(
            spell_source_id,
            frame_name=frame_name,
        )
        spell_id = identity["spell_id"]
        from melder.aether.aether import Aether

        aether = Aether._instance
        research = (
            aether._mutation_research if aether is not None else None
        )
        if research is None or research.cleaned or not research.activated:
            return {
                "source_id": spell_source_id,
                "spell_id": spell_id,
                "research_available": False,
                "reason": "mutation_research_not_active",
            }
        source = research.source_view(spell_id, module_name=module_name)
        source["source_id"] = spell_source_id
        source["research_available"] = True
        return source

    def describe_spell_origin(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the publication-origin fields for one visible spell.

        Purpose:
            Surface where the spell came from in frame/spellbook/conduit terms
            so the operator can reason about provenance before reading payload
            sections.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Publication-origin fields for the visible spell.
        """
        self.check_cleaned()
        spell_record = self._get_required_spell_record(
            spell_source_id,
            frame_name=frame_name,
        )
        return {
            "frame_name": spell_record.frame_name,
            "origin_spellbook_id": spell_record.origin_spellbook_id,
            "owner_conduit_id": spell_record.owner_conduit_id,
            "nexus_label": spell_record.nexus_label,
            "nexus_version": spell_record.nexus_version,
            "source_profile_name": spell_record.payload.source_profile_name,
            "source_profile_version": spell_record.payload.source_profile_version,
        }

    def describe_spell_index(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return spell-index grouping information for one visible spell.

        Purpose:
            Expose all visible and descriptor-local siblings that share the
            same spell-index id so the operator can understand the spell's
            index context inside the current frame.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Spell-index grouping summary for the spell.
        """
        self.check_cleaned()
        spell_record = self._get_required_spell_record(
            spell_source_id,
            frame_name=frame_name,
        )
        descriptor = self._get_required_frame_view()._get_required_frame_descriptor()
        visible_spell_source_ids = set(
            spell_link.source_id
            for spell_link in self.list_spells(frame_name=frame_name)
        )
        related_source_ids: List[str] = []
        visible_related_source_ids: List[str] = []
        for current_spell_record in descriptor.spell_records_by_key.values():
            if current_spell_record.spell_index_id != spell_record.spell_index_id:
                continue
            current_source_id = self._build_spell_source_id(current_spell_record)
            related_source_ids.append(current_source_id)
            if current_source_id in visible_spell_source_ids:
                visible_related_source_ids.append(current_source_id)
        return {
            "source_id": spell_source_id,
            "spell_index_id": spell_record.spell_index_id,
            "related_source_ids": tuple(sorted(related_source_ids)),
            "visible_related_source_ids": tuple(sorted(visible_related_source_ids)),
        }

    def describe_spell_binding(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the binding-facing summary for one visible spell.

        Purpose:
            Keep the spell's binding identity and optional binding payload
            together in one focused summary.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Binding-facing spell summary.
        """
        self.check_cleaned()
        spell_record = self._get_required_spell_record(
            spell_source_id,
            frame_name=frame_name,
        )
        spell_description = self.describe_spell(
            spell_source_id,
            frame_name=frame_name,
        )
        visible_sections = self._get_required_visible_sections(
            spell_description["visible_sections"]
        )
        payload = self._get_required_payload_map(spell_description["payload"])
        binding_payload_visible = "binding_payload" in visible_sections
        return {
            "source_id": spell_source_id,
            "spell_name": spell_record.spell_name,
            "binding_name": spell_record.binding_name,
            "spellframe": self._normalize_spellframe_value(spell_record.spellframe),
            "binding_payload_visible": binding_payload_visible,
            "binding_payload": payload.get("binding_payload"),
        }

    def describe_spell_resolution(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the resolution-facing summary for one visible spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Resolution-facing spell summary.
        """
        self.check_cleaned()
        spell_description = self.describe_spell(
            spell_source_id,
            frame_name=frame_name,
        )
        visible_sections = self._get_required_visible_sections(
            spell_description["visible_sections"]
        )
        payload = self._get_required_payload_map(spell_description["payload"])
        resolution_payload_visible = (
            "resolution_payload" in visible_sections
        )
        resolution_payload = payload.get("resolution_payload")
        requirement_count = None
        if isinstance(resolution_payload, dict):
            requirements = resolution_payload.get("requirements")
            if isinstance(requirements, list):
                requirement_count = len(requirements)
        return {
            "source_id": spell_source_id,
            "resolution_payload_visible": resolution_payload_visible,
            "resolution_payload": resolution_payload,
            "requirement_count": requirement_count,
        }

    def describe_spell_metadata(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the metadata section for one visible spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Metadata visibility summary for the spell.
        """
        self.check_cleaned()
        spell_description = self.describe_spell(
            spell_source_id,
            frame_name=frame_name,
        )
        visible_sections = self._get_required_visible_sections(
            spell_description["visible_sections"]
        )
        payload = self._get_required_payload_map(spell_description["payload"])
        metadata_visible = "metadata" in visible_sections
        return {
            "source_id": spell_source_id,
            "metadata_visible": metadata_visible,
            "metadata": payload.get("metadata", {}),
        }

    def describe_spell_class_profile(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the class-profile posture for one visible spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Class-profile availability and normalized data.
        """
        self.check_cleaned()
        return self._describe_detail_section(
            spell_source_id,
            section_name="class_profile",
            frame_name=frame_name,
        )

    def describe_spell_callable_profile(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the callable-profile posture for one visible spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Callable-profile availability and normalized
            data.
        """
        self.check_cleaned()
        return self._describe_detail_section(
            spell_source_id,
            section_name="callable_profile",
            frame_name=frame_name,
        )

    def describe_spell_instance_members(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the instance-member posture for one visible spell.

        Contract:
            Dunder members are preserved when the published detailed payload
            included them; this method does not hide or strip them.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Instance-member availability and normalized
            data.
        """
        self.check_cleaned()
        return self._describe_detail_section(
            spell_source_id,
            section_name="instance_members",
            frame_name=frame_name,
        )

    def describe_spell_dynamic_access(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the dynamic-access posture for one visible spell.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Dynamic-access availability and normalized data.
        """
        self.check_cleaned()
        return self._describe_detail_section(
            spell_source_id,
            section_name="dynamic_access",
            frame_name=frame_name,
        )

    def list_spell_dunder_member_names(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return dunder member names visible in detailed spell data.

        Purpose:
            Make dunder visibility explicit in detailed mode instead of leaving
            it implicit inside larger payload maps.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Tuple[str, ...]: Distinct visible dunder member names.
        """
        self.check_cleaned()
        dunder_description = self.describe_spell_dunder_members(
            spell_source_id,
            frame_name=frame_name,
        )
        dunder_names: set[str] = set()
        dunder_names.update(
            self._get_required_visible_sections(
                dunder_description["class_member_names"]
            )
        )
        dunder_names.update(
            self._get_required_visible_sections(
                dunder_description["class_method_names"]
            )
        )
        dunder_names.update(
            self._get_required_visible_sections(
                dunder_description["instance_member_names"]
            )
        )
        return tuple(sorted(dunder_names))

    def describe_spell_dunder_members(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the visible dunder members surfaced by detailed spell data.

        Purpose:
            Give the operator one explicit place to inspect the dunder-facing
            portion of the published detailed spell data.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Visible dunder-member summary.
        """
        self.check_cleaned()
        class_profile_view = self.describe_spell_class_profile(
            spell_source_id,
            frame_name=frame_name,
        )
        instance_member_view = self.describe_spell_instance_members(
            spell_source_id,
            frame_name=frame_name,
        )
        class_profile_payload = self._get_required_payload_map(
            class_profile_view["payload"]
        )
        instance_member_payload = self._get_required_payload_map(
            instance_member_view["payload"]
        )
        return {
            "source_id": spell_source_id,
            "detail_available": (
                class_profile_view["detail_available"]
                or instance_member_view["detail_available"]
            ),
            "class_member_names": self._get_required_visible_sections(
                class_profile_payload.get("dunder_member_names", tuple())
            ),
            "class_method_names": self._get_required_visible_sections(
                class_profile_payload.get("dunder_method_names", tuple())
            ),
            "instance_member_names": tuple(
                current_name
                for current_name in instance_member_payload.keys()
                if self._is_dunder_name(current_name)
            ),
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
                Optional frame-name assertion passed through to the selected-
                frame helper.

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
            record_key = self._get_required_record_key(
                spell_link.metadata["record_key"]
            )
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
                Optional frame-name assertion passed through to the selected-
                frame helper.

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

    def list_spells_by_owner_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells owned by one conduit.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        return [
            spell_link
            for spell_link, spell_record in self._iter_visible_spell_links_and_records(
                frame_name=frame_name
            )
            if spell_record.owner_conduit_id == conduit_id
        ]

    def list_spells_by_spellbook_id(
            self,
            spellbook_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells published by one spellbook id.

        Args:
            spellbook_id:
                Required origin spellbook id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        self.check_cleaned()
        if not spellbook_id:
            raise ValueError("spellbook_id cannot be empty.")
        return [
            spell_link
            for spell_link, spell_record in self._iter_visible_spell_links_and_records(
                frame_name=frame_name
            )
            if spell_record.origin_spellbook_id == spellbook_id
        ]

    def list_spells_by_index_id(
            self,
            spell_index_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells sharing one spell-index id.

        Args:
            spell_index_id:
                Required spell-index id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        self.check_cleaned()
        if not spell_index_id:
            raise ValueError("spell_index_id cannot be empty.")
        return [
            spell_link
            for spell_link, spell_record in self._iter_visible_spell_links_and_records(
                frame_name=frame_name
            )
            if spell_record.spell_index_id == spell_index_id
        ]

    def list_spells_by_permission(
            self,
            permission_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells with one permission posture.

        Args:
            permission_name:
                Required permission name.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        self.check_cleaned()
        if not permission_name:
            raise ValueError("permission_name cannot be empty.")
        normalized_permission_name = permission_name.lower()
        return [
            spell_link
            for spell_link, spell_record in self._iter_visible_spell_links_and_records(
                frame_name=frame_name
            )
            if spell_record.permissions.name.lower() == normalized_permission_name
        ]

    def list_spells_by_existence(
            self,
            existence_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells with one existence posture.

        Args:
            existence_name:
                Required existence-kind name.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        self.check_cleaned()
        if not existence_name:
            raise ValueError("existence_name cannot be empty.")
        normalized_existence_name = existence_name.lower()
        return [
            spell_link
            for spell_link, spell_record in self._iter_visible_spell_links_and_records(
                frame_name=frame_name
            )
            if spell_record.existence.name.lower() == normalized_existence_name
        ]

    def list_spells_by_spell_name(
            self,
            spell_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells whose spell name matches exactly.

        Args:
            spell_name:
                Required spell name.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        self.check_cleaned()
        if not spell_name:
            raise ValueError("spell_name cannot be empty.")
        return [
            spell_link
            for spell_link, spell_record in self._iter_visible_spell_links_and_records(
                frame_name=frame_name
            )
            if spell_record.spell_name == spell_name
        ]

    def list_spells_by_spellframe(
            self,
            spellframe_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells with one normalized spellframe value.

        Args:
            spellframe_name:
                Required normalized spellframe name.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        self.check_cleaned()
        if not spellframe_name:
            raise ValueError("spellframe_name cannot be empty.")
        return [
            spell_link
            for spell_link, spell_record in self._iter_visible_spell_links_and_records(
                frame_name=frame_name
            )
            if self._normalize_spellframe_value(spell_record.spellframe)
            == spellframe_name
        ]

    def search_spells_contains(
            self,
            text: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells whose identity contains one text fragment.

        Args:
            text:
                Case-insensitive text fragment to match.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        self.check_cleaned()
        if not text:
            raise ValueError("text cannot be empty.")
        lowered_text = text.lower()
        return [
            spell_link
            for spell_link, spell_record in self._iter_visible_spell_links_and_records(
                frame_name=frame_name
            )
            if lowered_text in spell_link.display_name.lower()
            or lowered_text in spell_link.source_id.lower()
            or lowered_text in spell_record.spell_name.lower()
            or (
                spell_record.binding_name is not None
                and lowered_text in spell_record.binding_name.lower()
            )
        ]

    def search_spells_prefix(
            self,
            prefix: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return visible spells whose identity starts with one prefix.

        Args:
            prefix:
                Case-insensitive prefix to match.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[FrameLink]: Matching visible spell links.
        """
        self.check_cleaned()
        if not prefix:
            raise ValueError("prefix cannot be empty.")
        lowered_prefix = prefix.lower()
        return [
            spell_link
            for spell_link, spell_record in self._iter_visible_spell_links_and_records(
                frame_name=frame_name
            )
            if spell_link.display_name.lower().startswith(lowered_prefix)
            or spell_link.source_id.lower().startswith(lowered_prefix)
            or spell_record.spell_name.lower().startswith(lowered_prefix)
            or (
                spell_record.binding_name is not None
                and spell_record.binding_name.lower().startswith(lowered_prefix)
            )
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
                Optional frame-name assertion passed through to the selected-
                frame helper.

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
        visible_sections = self._get_required_visible_sections(
            explanation["visible_sections"]
        )
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

    def describe_spell_access_summary(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one compact access/identity/detail summary for a spell.

        Purpose:
            Give the operator one high-signal spell summary that combines
            record identity, provenance, ACL posture, and detailed payload
            availability in one place.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Compact spell access summary.
        """
        self.check_cleaned()
        return {
            "identity": self.describe_spell_identity(
                spell_source_id,
                frame_name=frame_name,
            ),
            "origin": self.describe_spell_origin(
                spell_source_id,
                frame_name=frame_name,
            ),
            "access": self.explain_spell_access(
                spell_source_id,
                frame_name=frame_name,
            ),
            "detail": self.describe_spell_detail(
                spell_source_id,
                frame_name=frame_name,
            ),
        }

    def describe_spell_crosswalk(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return the related visible objects around one spell.

        Purpose:
            Give the operator one direct spell crosswalk from the spell to its
            conduit, root conduit, peer conduits, spellbook, spell index, and
            visible sibling spells.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Spell crosswalk summary.
        """
        self.check_cleaned()
        spell_record = self._get_required_spell_record(
            spell_source_id,
            frame_name=frame_name,
        )
        frame_view = self._get_required_frame_view()
        descriptor = frame_view._get_required_frame_descriptor()
        owner_conduit_id = spell_record.owner_conduit_id
        root_conduit_id = None
        peer_conduit_ids: tuple[str, ...] = tuple()
        if owner_conduit_id is not None:
            conduit_record = descriptor.conduit_records_by_id[owner_conduit_id]
            root_conduit_id = conduit_record.root_conduit_id
            peer_conduit_ids = tuple(conduit_record.payload.peer_conduit_ids)
        return {
            "frame_name": spell_record.frame_name,
            "source_id": spell_source_id,
            "origin_spellbook_id": spell_record.origin_spellbook_id,
            "owner_conduit_id": owner_conduit_id,
            "root_conduit_id": root_conduit_id,
            "peer_conduit_ids": peer_conduit_ids,
            "spell_index_id": spell_record.spell_index_id,
            "related_visible_source_ids": self.describe_spell_index(
                spell_source_id,
                frame_name=frame_name,
            )["visible_related_source_ids"],
            "permissions": spell_record.permissions.name,
            "existence": spell_record.existence.name,
            "payload_type": spell_record.payload.payload_type,
        }

    def compare_spells(
            self,
            left_spell_source_id: str,
            right_spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Compare two visible spells inside the bound frame.

        Args:
            left_spell_source_id:
                Left visible spell source id.
            right_spell_source_id:
                Right visible spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Visible spell comparison summary.
        """
        self.check_cleaned()
        left_spell_record = self._get_required_spell_record(
            left_spell_source_id,
            frame_name=frame_name,
        )
        right_spell_record = self._get_required_spell_record(
            right_spell_source_id,
            frame_name=frame_name,
        )
        left_spell_description = self.describe_spell(
            left_spell_source_id,
            frame_name=frame_name,
        )
        right_spell_description = self.describe_spell(
            right_spell_source_id,
            frame_name=frame_name,
        )
        return {
            "left_source_id": left_spell_source_id,
            "right_source_id": right_spell_source_id,
            "same_owner_conduit": (
                left_spell_record.owner_conduit_id
                == right_spell_record.owner_conduit_id
            ),
            "same_origin_spellbook": (
                left_spell_record.origin_spellbook_id
                == right_spell_record.origin_spellbook_id
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
            "visible_sections": self._compare_sorted_value_sets(
                self._get_required_visible_sections(
                    left_spell_description["visible_sections"]
                ),
                self._get_required_visible_sections(
                    right_spell_description["visible_sections"]
                ),
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
                Optional frame-name assertion passed through to the selected-
                frame helper.

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
        visible_sections = self._get_required_visible_sections(
            spell_description["visible_sections"]
        )
        if section_name not in visible_sections:
            raise ValueError(
                "Spell payload section '{0}' is not visible for spell '{1}'.".format(
                    section_name,
                    spell_source_id,
                )
            )
        payload = self._get_required_payload_map(spell_description["payload"])
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
                Optional frame-name assertion passed through to the selected-
                frame helper.

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

    def _get_required_frame_view(self) -> ViewFrame:
        """
        Return the borrowed frame helper or raise when unbound.

        Returns:
            ViewFrame: Borrowed frame helper surface.
        """
        if self._frame_view is None:
            raise ValueError("ViewSpell is not bound to a frame view.")
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
    def _get_required_visible_sections(
            visible_sections: object,
    ) -> Tuple[str, ...]:
        """
        Return one validated visible-section tuple.

        Args:
            visible_sections:
                Candidate visible-section payload.

        Returns:
            Tuple[str, ...]: Validated visible section names.
        """
        if not isinstance(visible_sections, (tuple, list)):
            raise TypeError("visible_sections must be a tuple[str, ...].")
        normalized_sections: List[str] = []
        for current_section in visible_sections:
            if not isinstance(current_section, str):
                raise TypeError("visible_sections must contain only strings.")
            normalized_sections.append(current_section)
        return tuple(normalized_sections)

    @staticmethod
    def _get_required_payload_map(payload: object) -> Dict[str, object]:
        """
        Return one validated spell payload mapping.

        Args:
            payload:
                Candidate spell payload map.

        Returns:
            Dict[str, object]: Validated spell payload map.
        """
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict[str, object].")
        normalized_payload: Dict[str, object] = {}
        for current_key, current_value in payload.items():
            if not isinstance(current_key, str):
                raise TypeError("payload keys must be strings.")
            normalized_payload[current_key] = current_value
        return normalized_payload

    def _get_required_spell_record(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> SpellRecord:
        """
        Return one descriptor-owned spell record or raise.

        Args:
            spell_source_id:
                Published spell source id.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            SpellRecord: Descriptor-owned spell record.
        """
        spell_link = self.get_required_spell(
            spell_source_id,
            frame_name=frame_name,
        )
        descriptor = self._get_required_frame_view()._get_required_frame_descriptor()
        record_key = self._get_required_record_key(
            spell_link.metadata["record_key"]
        )
        return descriptor.spell_records_by_key[record_key]

    def _iter_visible_spell_links_and_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[Tuple[FrameLink, SpellRecord]]:
        """
        Return visible spell links paired with their descriptor-owned records.

        Args:
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            List[Tuple[FrameLink, SpellRecord]]: Visible spell links paired with
            their backing spell records.
        """
        descriptor = self._get_required_frame_view()._get_required_frame_descriptor()
        return [
            (
                spell_link,
                descriptor.spell_records_by_key[
                    self._get_required_record_key(
                        spell_link.metadata["record_key"]
                    )
                ],
            )
            for spell_link in self.list_spells(frame_name=frame_name)
        ]

    def _describe_detail_section(
            self,
            spell_source_id: str,
            *,
            section_name: str,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one detailed payload section with availability semantics.

        Args:
            spell_source_id:
                Published spell source id.
            section_name:
                Required detailed payload section name.
            frame_name:
                Optional frame-name assertion passed through to the selected-
                frame helper.

        Returns:
            Dict[str, object]: Detailed section availability and normalized
            payload.
        """
        spell_description = self.describe_spell(
            spell_source_id,
            frame_name=frame_name,
        )
        payload_type = spell_description["payload_type"]
        visible_sections = self._get_required_visible_sections(
            spell_description["visible_sections"]
        )
        detailed_only_sections = {
            "class_profile",
            "callable_profile",
            "instance_members",
            "dynamic_access",
        }
        if payload_type != "detailed" and section_name in detailed_only_sections:
            return {
                "source_id": spell_source_id,
                "payload_type": payload_type,
                "detail_available": False,
                "reason": "payload_not_detailed",
                "visible_sections": visible_sections,
                "payload": {},
            }
        if section_name not in visible_sections:
            return {
                "source_id": spell_source_id,
                "payload_type": payload_type,
                "detail_available": False,
                "reason": "acl_restricted",
                "visible_sections": visible_sections,
                "payload": {},
            }
        spell_record = self._get_required_spell_record(
            spell_source_id,
            frame_name=frame_name,
        )
        raw_value = getattr(spell_record.payload, section_name)
        normalized_value = self._normalize_detail_section_value(
            section_name,
            raw_value,
        )
        if normalized_value is None:
            return {
                "source_id": spell_source_id,
                "payload_type": payload_type,
                "detail_available": False,
                "reason": "not_published",
                "visible_sections": visible_sections,
                "payload": {},
            }
        if isinstance(normalized_value, dict) and len(normalized_value) == 0:
            return {
                "source_id": spell_source_id,
                "payload_type": payload_type,
                "detail_available": False,
                "reason": "not_published",
                "visible_sections": visible_sections,
                "payload": {},
            }
        return {
            "source_id": spell_source_id,
            "payload_type": payload_type,
            "detail_available": True,
            "reason": "available",
            "visible_sections": visible_sections,
            "payload": normalized_value,
        }

    def _normalize_detail_section_value(
            self,
            section_name: str,
            value: Any,
    ) -> Optional[object]:
        """
        Return a viewer-safe representation for one detailed payload section.

        Args:
            section_name:
                Detailed payload section name.
            value:
                Raw section value from the descriptor payload.

        Returns:
            Optional[object]: Normalized section value when available.
        """
        if value is None:
            return None
        if section_name == "class_profile":
            return self._normalize_class_profile_value(value)
        if section_name == "callable_profile":
            return self._normalize_callable_profile_value(value)
        if section_name == "instance_members":
            return self._normalize_instance_members_value(value)
        if section_name == "dynamic_access":
            return ViewFrame._normalize_value(value)
        return ViewFrame._normalize_value(value)

    def _normalize_class_profile_value(self, class_profile: Any) -> Optional[object]:
        """
        Return a viewer-safe representation of one class-profile payload.

        Args:
            class_profile:
                Raw class-profile payload.

        Returns:
            Optional[object]: Normalized class-profile representation.
        """
        if class_profile is None:
            return None
        if isinstance(class_profile, dict):
            normalized_class_profile = ViewFrame._normalize_value(class_profile)
            if not isinstance(normalized_class_profile, dict):
                return normalized_class_profile
            member_names, method_names = self._extract_class_profile_name_sets(
                normalized_class_profile
            )
            normalized_class_profile["member_names"] = member_names
            normalized_class_profile["method_names"] = method_names
            normalized_class_profile["dunder_member_names"] = tuple(
                current_name
                for current_name in member_names
                if self._is_dunder_name(current_name)
            )
            normalized_class_profile["dunder_method_names"] = tuple(
                current_name
                for current_name in method_names
                if self._is_dunder_name(current_name)
            )
            return normalized_class_profile
        if isinstance(class_profile, ClassProfile):
            members = class_profile.members or {}
            methods = class_profile.methods or {}
            member_names = tuple(sorted(members.keys()))
            method_names = tuple(sorted(methods.keys()))
            return {
                "name": class_profile.name,
                "qualname": class_profile.qualname,
                "module": class_profile.module,
                "mro": tuple(class_profile.mro or []),
                "bases": tuple(class_profile.bases or []),
                "annotations": ViewFrame._normalize_value(
                    class_profile.annotations
                ),
                "protocols": ViewFrame._normalize_value(
                    class_profile.protocols
                ),
                "slots": tuple(class_profile.slots or []),
                "origin_file": class_profile.origin_file,
                "origin_line": class_profile.origin_line,
                "origin_end_line": class_profile.origin_end_line,
                "source_preview": class_profile.source_preview,
                "docstring_summary": class_profile.docstring_summary,
                "behavior_summary": class_profile.behavior_summary,
                "tags": tuple(class_profile.tags or []),
                "is_dataclass": class_profile.is_dataclass,
                "decorated": class_profile.decorated,
                "member_names": member_names,
                "method_names": method_names,
                "dunder_member_names": tuple(
                    current_name
                    for current_name in member_names
                    if self._is_dunder_name(current_name)
                ),
                "dunder_method_names": tuple(
                    current_name
                    for current_name in method_names
                    if self._is_dunder_name(current_name)
                ),
                "members": ViewFrame._normalize_value(members),
                "methods": {
                    method_name: self._normalize_callable_profile_value(method_profile)
                    for method_name, method_profile in methods.items()
                },
                "dynamic_access": ViewFrame._normalize_value(
                    class_profile.dynamic_access
                ),
            }
        return ViewFrame._normalize_value(class_profile)

    def _normalize_callable_profile_value(
            self,
            callable_profile: Any,
    ) -> Optional[object]:
        """
        Return a viewer-safe representation of one callable-profile payload.

        Args:
            callable_profile:
                Raw callable-profile payload.

        Returns:
            Optional[object]: Normalized callable-profile representation.
        """
        if callable_profile is None:
            return None
        if isinstance(callable_profile, dict):
            return ViewFrame._normalize_value(callable_profile)
        if isinstance(callable_profile, MethodProfile):
            return {
                "name": callable_profile.name,
                "qualname": callable_profile.qualname,
                "module": callable_profile.module,
                "signature": callable_profile.signature,
                "parameters": ViewFrame._normalize_value(
                    callable_profile.parameters
                ),
                "start_line": callable_profile.start_line,
                "end_line": callable_profile.end_line,
                "docstring_summary": callable_profile.docstring_summary,
                "behavior_summary": callable_profile.behavior_summary,
                "tags": tuple(callable_profile.tags or []),
                "uninspectable": callable_profile.uninspectable,
                "func": callable_profile.func,
                "method": callable_profile.method,
                "builtin": callable_profile.builtin,
                "classmethod": callable_profile.classmethod,
                "staticmethod": callable_profile.staticmethod,
                "generator": callable_profile.generator,
                "async_gen": callable_profile.async_gen,
                "coroutine": callable_profile.coroutine,
                "lambda_fn": callable_profile.lambda_fn,
                "abstract": callable_profile.abstract,
            }
        return ViewFrame._normalize_value(callable_profile)

    @staticmethod
    def _normalize_instance_members_value(instance_members: Any) -> Optional[object]:
        """
        Return a viewer-safe representation of one instance-members payload.

        Args:
            instance_members:
                Raw instance-members payload.

        Returns:
            Optional[object]: Normalized instance-members representation.
        """
        if instance_members is None:
            return None
        return ViewFrame._normalize_value(instance_members)

    @staticmethod
    def _extract_class_profile_name_sets(
            normalized_class_profile: Dict[str, Any],
    ) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        """
        Extract member and method names from a normalized class-profile mapping.

        Args:
            normalized_class_profile:
                Normalized class-profile mapping.

        Returns:
            Tuple[Tuple[str, ...], Tuple[str, ...]]: `(member_names,
            method_names)` extracted from the mapping.
        """
        member_names: tuple[str, ...] = tuple()
        method_names: tuple[str, ...] = tuple()
        members = normalized_class_profile.get("members")
        methods = normalized_class_profile.get("methods")
        if isinstance(members, dict):
            member_names = tuple(sorted(members.keys()))
        elif isinstance(members, (list, tuple)):
            member_names = tuple(
                sorted(
                    str(current_name)
                    for current_name in members
                )
            )
        if isinstance(methods, dict):
            method_names = tuple(sorted(methods.keys()))
        elif isinstance(methods, (list, tuple)):
            method_names = tuple(
                sorted(
                    str(current_name)
                    for current_name in methods
                )
            )
        return member_names, method_names

    @staticmethod
    def _is_dunder_name(name: str) -> bool:
        """
        Return whether one member name is a dunder name.

        Args:
            name:
                Candidate member name.

        Returns:
            bool: True when the name starts and ends with double underscores.
        """
        return name.startswith("__") and name.endswith("__")

    @staticmethod
    def _build_spell_source_id(spell_record: SpellRecord) -> str:
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
            filtered_payload[current_section] = ViewFrame._normalize_value(
                current_value
            )
        return filtered_payload

