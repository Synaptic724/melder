"""
Internal FrameView placeholder.

Purpose:
    Represent one filtered/frame-scoped view over `FrameLink` objects.

Responsibilities:
    - Hold references to the links visible for one frame/perspective.
    - Carry light view metadata while avoiding raw runtime-object ownership.

Endgame:
    `FrameView` should eventually represent the diff/filter layer between
    Nexus-owned frame-surface truth and the final `FrameViewer` experience.
"""

import threading
from typing import Dict, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.aether.nexus.rift.frame_link.frame_link_contract import FrameLinkContract
from melder.aether.nexus.rift.frame_link.profiles.frame_link_contract_profile import (
    FrameLinkContractProfile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameView(Cleanable):
    """
    Internal

    Placeholder frame-scoped view object.

    Purpose:
        Hold references to visible `FrameLink` objects for one frame or one
        applied perspective over a frame.

    Contract:
        - Holds references to links only, not raw runtime objects.
        - Cleanup is idempotent and clears owned references.

    Lifecycle:
        Placeholder only. Future ownership is expected to sit close to the
        consuming `FrameViewer`.

    TODO(HLD):
        This object is intended to become the filtered/diff layer over Nexus
        truth:

        - A `FrameView` should own references to the visible `FrameLink`
          objects for one frame or one applied perspective over a frame.
        - It should not duplicate the full canonical store if that can be
          avoided; it should hold the representational result the viewer needs.
        - It should be the place where the "what can be seen right now from
          this perspective?" diff lives.
        - One `FrameViewer` may later consume multiple `FrameView` objects at
          once to build multiple interactive areas across contracts that span
          more than one frame.
        - This object should not own:
            * raw runtime object access
            * ACL evaluation logic
            * viewer query strategies
            * orchestration state
        - This object should stay simple enough that high-churn lower updates
          can refresh it without turning it into a second full repository.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_view_id",
        "_lock",
        "_frame_name",
        "_links_by_id",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            links_by_id: Optional[Dict[str, FrameLink]] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Internal

        Initialize one placeholder frame view.

        Args:
            frame_name:
                Frame name this view is scoped to.
            links_by_id:
                Optional map of visible links keyed by link id.
            metadata:
                Optional free-form view metadata.

        Returns:
            None.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        self._view_id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._links_by_id: Dict[str, FrameLink] = dict(links_by_id) if links_by_id else {}
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Internal

        Idempotently clear view-owned state.

        Threading:
            Uses the instance lock because cleanup cascades through owned links
            and grouped metadata state in one pass in a nogil runtime.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for frame_link in self._links_by_id.values():
                frame_link.cleanup()
            self._links_by_id.clear()
            self._links_by_id = None
            self._metadata.clear()
            self._metadata = None
            self._frame_name = None
            self._view_id = None
        self._lock = None

    @classmethod
    def from_compiled_access_surface(
            cls,
            *,
            frame_descriptor: FrameDescriptor,
            compiled_access_surface: CompiledFrameACLAccessSurface,
            contract_profile: Optional[FrameLinkContractProfile] = None,
    ) -> "FrameView":
        """
        Internal

        Build one `FrameView` from descriptor truth plus compiled ACL access
        output.

        Purpose:
            Provide the first real bridge from the compiled ACL contract layer
            into the frame-surface objects without requiring the full
            Nexus-side canonical holding-zone implementation first.

        Args:
            frame_descriptor:
                Descriptor truth for the target frame.
            compiled_access_surface:
                Derived ACL access surface for the same frame.
            contract_profile:
                Optional downstream frame-link contract profile used to narrow
                the projected contract.

        Returns:
            FrameView: Derived frame-scoped view containing view-safe links.
        """
        if not isinstance(frame_descriptor, FrameDescriptor):
            raise TypeError("frame_descriptor must be a FrameDescriptor.")
        if not isinstance(compiled_access_surface, CompiledFrameACLAccessSurface):
            raise TypeError(
                "compiled_access_surface must be a CompiledFrameACLAccessSurface."
            )
        if frame_descriptor.frame_name != compiled_access_surface.frame_name:
            raise ValueError(
                "compiled_access_surface targets frame '{0}', expected '{1}'.".format(
                    compiled_access_surface.frame_name,
                    frame_descriptor.frame_name,
                )
            )
        if (
                contract_profile is not None
                and not isinstance(contract_profile, FrameLinkContractProfile)
        ):
            raise TypeError(
                "contract_profile must be a FrameLinkContractProfile."
            )
        effective_contract = FrameLinkContract.from_compiled_access_surface(
            compiled_access_surface,
            contract_profile=contract_profile,
        )
        links_by_id: Dict[str, FrameLink] = {}
        frame_overview = frame_descriptor.frame_overview
        if "frame" in effective_contract.allowed_kinds:
            if frame_overview is None:
                raise ValueError(
                    "FrameDescriptor must expose frame_overview for frame links."
                )
            frame_link = FrameLink.from_contract_subject(
                frame_name=frame_descriptor.frame_name,
                source_kind="frame",
                source_id=frame_overview.frame_id,
                display_name=frame_overview.frame_name,
                contract=effective_contract,
                metadata={
                    "payload_fields": cls._resolve_frame_payload_fields(
                        effective_contract,
                        compiled_access_surface,
                    ),
                    "frame_id": frame_overview.frame_id,
                    "config_origin_spellbook_id": (
                        frame_overview.config_origin_spellbook_id
                    ),
                    "payload_profile_name": frame_overview.payload.profile_name,
                },
            )
            links_by_id[frame_link.link_id] = frame_link

        conduit_records_by_id = frame_descriptor.conduit_records_by_id
        conduit_sections_by_id = cls._resolve_conduit_sections_by_id(
            effective_contract,
            compiled_access_surface,
        )
        if "conduit" in effective_contract.allowed_kinds:
            for conduit_id in compiled_access_surface.visible_conduit_ids:
                try:
                    conduit_record = conduit_records_by_id[conduit_id]
                except KeyError as exc:
                    raise ValueError(
                        "Missing ConduitRecord for compiled conduit id '{0}'.".format(
                            conduit_id
                        )
                    ) from exc
                conduit_link = FrameLink.from_contract_subject(
                    frame_name=frame_descriptor.frame_name,
                    source_kind="conduit",
                    source_id=conduit_id,
                    display_name=conduit_record.payload.conduit_name or conduit_id,
                    contract=effective_contract,
                    metadata={
                        "payload_sections": conduit_sections_by_id.get(
                            conduit_id,
                            tuple(),
                        ),
                        "root_conduit_id": conduit_record.root_conduit_id,
                        "origin_spellbook_id": conduit_record.origin_spellbook_id,
                        "payload_profile_name": conduit_record.payload.profile_name,
                    },
                )
                links_by_id[conduit_link.link_id] = conduit_link

        spell_records_by_key = frame_descriptor.spell_records_by_key
        spell_sections_by_key = cls._resolve_spell_sections_by_key(
            effective_contract,
            compiled_access_surface,
        )
        if "spell" in effective_contract.allowed_kinds:
            for record_key in compiled_access_surface.visible_spell_keys:
                try:
                    spell_record = spell_records_by_key[record_key]
                except KeyError as exc:
                    raise ValueError(
                        "Missing SpellRecord for compiled spell key '{0}'.".format(
                            record_key
                        )
                    ) from exc
                spell_link = FrameLink.from_contract_subject(
                    frame_name=frame_descriptor.frame_name,
                    source_kind="spell",
                    source_id="{0}:{1}".format(record_key[0], record_key[1]),
                    display_name=(
                        spell_record.binding_name
                        or spell_record.spell_name
                        or spell_record.spell_id
                    ),
                    contract=effective_contract,
                    metadata={
                        "record_key": record_key,
                        "spell_id": spell_record.spell_id,
                        "lineage_id": spell_record.lineage_id,
                        "owner_conduit_id": spell_record.owner_conduit_id,
                        "payload_sections": spell_sections_by_key.get(
                            record_key,
                            tuple(),
                        ),
                        "payload_profile_name": spell_record.payload.profile_name,
                    },
                )
                links_by_id[spell_link.link_id] = spell_link

        return cls(
            frame_name=frame_descriptor.frame_name,
            links_by_id=links_by_id,
            metadata={
                "contract_id": effective_contract.contract_id,
                "allowed_kinds": effective_contract.allowed_kinds,
                "allowed_commands": effective_contract.allowed_commands,
                "link_count": len(links_by_id),
            },
        )

    @property
    def view_id(self) -> str:
        """Return the canonical view id."""
        self.check_cleaned()
        return self._view_id

    @property
    def frame_name(self) -> str:
        """Return the frame name this view is scoped to."""
        self.check_cleaned()
        return self._frame_name

    @property
    def links_by_id(self) -> Dict[str, FrameLink]:
        """Return the currently visible links by id."""
        self.check_cleaned()
        with self._lock:
            return dict(self._links_by_id)

    @property
    def metadata(self) -> Dict[str, object]:
        """Return the view metadata map."""
        self.check_cleaned()
        with self._lock:
            return dict(self._metadata)

    @staticmethod
    def _resolve_frame_payload_fields(
            effective_contract: FrameLinkContract,
            compiled_access_surface: CompiledFrameACLAccessSurface,
    ) -> Tuple[str, ...]:
        """
        Return the effective visible frame payload fields for the view.

        Args:
            effective_contract:
                Effective frame-link contract.
            compiled_access_surface:
                Source compiled ACL access surface.

        Returns:
            Tuple[str, ...]: Effective visible frame payload fields.
        """
        return tuple(
            effective_contract.metadata.get(
                "frame_payload_fields",
                compiled_access_surface.frame_payload_fields,
            )
        )

    @staticmethod
    def _resolve_conduit_sections_by_id(
            effective_contract: FrameLinkContract,
            compiled_access_surface: CompiledFrameACLAccessSurface,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return the effective visible conduit sections by id.

        Args:
            effective_contract:
                Effective frame-link contract.
            compiled_access_surface:
                Source compiled ACL access surface.

        Returns:
            Dict[str, Tuple[str, ...]]: Effective visible conduit sections.
        """
        sections_by_id = effective_contract.metadata.get(
            "conduit_payload_sections_by_id",
            compiled_access_surface.conduit_payload_sections_by_id,
        )
        return {
            conduit_id: tuple(sections)
            for conduit_id, sections in sections_by_id.items()
        }

    @staticmethod
    def _resolve_spell_sections_by_key(
            effective_contract: FrameLinkContract,
            compiled_access_surface: CompiledFrameACLAccessSurface,
    ) -> Dict[Tuple[str, str], Tuple[str, ...]]:
        """
        Return the effective visible spell sections by key.

        Args:
            effective_contract:
                Effective frame-link contract.
            compiled_access_surface:
                Source compiled ACL access surface.

        Returns:
            Dict[Tuple[str, str], Tuple[str, ...]]: Effective visible spell
            sections.
        """
        sections_by_key = effective_contract.metadata.get(
            "spell_payload_sections_by_key",
            compiled_access_surface.spell_payload_sections_by_key,
        )
        return {
            record_key: tuple(sections)
            for record_key, sections in sections_by_key.items()
        }
