import threading
from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.utilities.general_base.cleanable import Cleanable


class GeneralViewFrame(Cleanable):
    """
    Purpose:
        Hold frame-scoped viewer helper methods for the `general` profile.

    Contract:
        - Operates only on one bound frame's descriptor + ACL state.
        - Returns ACL-filtered `FrameLink` objects and summaries.
        - Does not expose raw runtime objects.

    Lifecycle:
        Cleanup is idempotent and clears all bound references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_frame_name",
        "_frame_descriptor",
        "_frame_acl_configuration",
        "_compiled_access_surface",
        "_default_detail_level",
    ]

    def __init__(
            self,
            *,
            frame_name: Optional[str],
            frame_descriptor: Optional[FrameDescriptor],
            frame_acl_configuration: Optional[FrameACLConfiguration],
            compiled_access_surface: Optional[CompiledFrameACLAccessSurface],
            default_detail_level: str,
    ) -> None:
        """
        Initialize one frame-scoped viewer helper surface.

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

    def cleanup(self) -> None:
        """
        Idempotently clear the helper surface.

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
        self._lock = None

    def list_frames(self) -> List[str]:
        self.check_cleaned()
        return [self._get_required_frame_name()]

    def describe_views(self) -> List[Dict[str, object]]:
        self.check_cleaned()
        return [
            {
                "frame_name": self._get_required_frame_name(),
                "is_default": True,
                "available_target_count": len(self._build_links()),
                "available_kinds": tuple(
                    sorted(self._get_required_compiled_access_surface().allowed_kinds)
                ),
            }
        ]

    def list_targets(
            self,
            *,
            source_kind: Optional[str] = None,
    ) -> List[FrameLink]:
        self.check_cleaned()
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
            source_kind: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        self.check_cleaned()
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

    def describe_frame(self) -> Dict[str, object]:
        self.check_cleaned()
        compiled_access_surface = self._get_required_compiled_access_surface()
        grouped_links: Dict[str, List[FrameLink]] = {}
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

    def describe_frames(self) -> Dict[str, Dict[str, object]]:
        self.check_cleaned()
        frame_name = self._get_required_frame_name()
        return {
            frame_name: self.describe_frame(),
        }

    def get_required_target_by_source(
            self,
            *,
            source_kind: str,
            source_id: str,
    ) -> FrameLink:
        self.check_cleaned()
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
            "GeneralViewFrame target '{0}:{1}' was not found for frame '{2}'.".format(
                source_kind,
                source_id,
                self._get_required_frame_name(),
            )
        )

    def _build_links(self) -> List[FrameLink]:
        descriptor = self._get_required_frame_descriptor()
        compiled_access_surface = self._get_required_compiled_access_surface()
        frame_name = self._get_required_frame_name()
        links: List[FrameLink] = []
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
                            "lineage_id": spell_record.lineage_id,
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

    def _get_required_frame_name(self) -> str:
        if self._frame_name is None:
            raise ValueError("GeneralViewFrame is not bound to a frame.")
        return self._frame_name

    def _get_required_frame_descriptor(self) -> FrameDescriptor:
        if self._frame_descriptor is None:
            raise ValueError("GeneralViewFrame has no bound FrameDescriptor.")
        return self._frame_descriptor

    def _get_required_compiled_access_surface(self) -> CompiledFrameACLAccessSurface:
        if self._compiled_access_surface is None:
            raise ValueError(
                "GeneralViewFrame has no bound CompiledFrameACLAccessSurface."
            )
        return self._compiled_access_surface
