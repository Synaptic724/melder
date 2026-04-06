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
from typing import Dict, List, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.aether.nexus.rift.frame_viewer.profiles.frame_view_profile import (
    FrameViewProfile,
)
from melder.aether.nexus.rift.frame_viewer.profiles.frame_view_profile_builder import (
    FrameViewProfileBuilder,
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
        "_profile_name",
        "_profile_version",
        "_profile_builder",
        "_active_profiles_by_name",
        "_default_profile_name",
        "_links_by_id",
        "_available_target_ids_by_kind",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            profile_name: Optional[str] = None,
            profile_version: Optional[str] = None,
            profile_builder: Optional[FrameViewProfileBuilder] = None,
            active_profiles_by_name: Optional[Dict[str, FrameViewProfile]] = None,
            default_profile_name: Optional[str] = None,
            links_by_id: Optional[Dict[str, FrameLink]] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Internal

        Initialize one placeholder frame view.

        Args:
            frame_name:
                Frame name this view is scoped to.
            profile_name:
                Optional view profile name applied to this projection.
            profile_version:
                Optional view profile version applied to this projection.
            profile_builder:
                Optional local frame-view profile builder/registry.
            active_profiles_by_name:
                Optional active local profiles hosted on this view.
            default_profile_name:
                Optional default local profile name.
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
        self._profile_name: Optional[str] = profile_name
        self._profile_version: Optional[str] = profile_version
        if profile_builder is not None and not isinstance(
                profile_builder,
                FrameViewProfileBuilder,
        ):
            raise TypeError("profile_builder must be a FrameViewProfileBuilder.")
        self._profile_builder: FrameViewProfileBuilder = (
            profile_builder if profile_builder is not None else FrameViewProfileBuilder()
        )
        self._links_by_id: Dict[str, FrameLink] = dict(links_by_id) if links_by_id else {}
        self._available_target_ids_by_kind: Dict[str, Tuple[str, ...]] = (
            self._build_available_target_ids_by_kind(self._links_by_id)
        )
        if active_profiles_by_name is not None:
            self._active_profiles_by_name: Dict[str, FrameViewProfile] = dict(
                active_profiles_by_name
            )
        else:
            default_profile = self._profile_builder.get_required_profile("general").clone()
            self._active_profiles_by_name = {default_profile.name: default_profile}
        if default_profile_name is not None:
            if not default_profile_name:
                raise ValueError("default_profile_name cannot be empty.")
            if default_profile_name not in self._active_profiles_by_name:
                raise ValueError(
                    "default_profile_name must be present in active_profiles_by_name."
                )
        self._default_profile_name: Optional[str] = (
            default_profile_name
            if default_profile_name is not None
            else (
                next(iter(self._active_profiles_by_name.keys()))
                if len(self._active_profiles_by_name) > 0
                else None
            )
        )
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
            for frame_view_profile in self._active_profiles_by_name.values():
                frame_view_profile.cleanup()
            self._profile_builder.cleanup()
            self._links_by_id.clear()
            self._links_by_id = None
            self._available_target_ids_by_kind.clear()
            self._available_target_ids_by_kind = None
            self._active_profiles_by_name.clear()
            self._active_profiles_by_name = None
            self._default_profile_name = None
            self._profile_builder = None
            self._metadata.clear()
            self._metadata = None
            self._frame_name = None
            self._profile_name = None
            self._profile_version = None
            self._view_id = None
        self._lock = None

    @classmethod
    def from_compiled_access_surface(
            cls,
            *,
            frame_descriptor: FrameDescriptor,
            compiled_access_surface: CompiledFrameACLAccessSurface,
            view_profile: Optional[FrameViewProfile] = None,
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
            view_profile:
                Optional view profile that modifies view defaults only.

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
        if view_profile is not None and not isinstance(view_profile, FrameViewProfile):
            raise TypeError("view_profile must be a FrameViewProfile.")
        links_by_id: Dict[str, FrameLink] = {}
        frame_overview = frame_descriptor.frame_overview
        if "frame" in compiled_access_surface.allowed_kinds:
            if frame_overview is None:
                raise ValueError(
                    "FrameDescriptor must expose frame_overview for frame links."
                )
            frame_link = FrameLink.from_view_subject(
                frame_name=frame_descriptor.frame_name,
                source_kind="frame",
                source_id=frame_overview.frame_id,
                display_name=frame_overview.frame_name,
                metadata={
                    "payload_fields": tuple(compiled_access_surface.frame_payload_fields),
                    "frame_id": frame_overview.frame_id,
                    "config_origin_spellbook_id": (
                        frame_overview.config_origin_spellbook_id
                    ),
                    "payload_profile_name": frame_overview.payload.profile_name,
                },
            )
            links_by_id[frame_link.link_id] = frame_link

        conduit_records_by_id = frame_descriptor.conduit_records_by_id
        conduit_sections_by_id = {
            conduit_id: tuple(sections)
            for conduit_id, sections in (
                compiled_access_surface.conduit_payload_sections_by_id.items()
            )
        }
        if "conduit" in compiled_access_surface.allowed_kinds:
            for conduit_id in compiled_access_surface.visible_conduit_ids:
                try:
                    conduit_record = conduit_records_by_id[conduit_id]
                except KeyError as exc:
                    raise ValueError(
                        "Missing ConduitRecord for compiled conduit id '{0}'.".format(
                            conduit_id
                        )
                    ) from exc
                conduit_link = FrameLink.from_view_subject(
                    frame_name=frame_descriptor.frame_name,
                    source_kind="conduit",
                    source_id=conduit_id,
                    display_name=conduit_record.payload.conduit_name or conduit_id,
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
        spell_sections_by_key = {
            record_key: tuple(sections)
            for record_key, sections in (
                compiled_access_surface.spell_payload_sections_by_key.items()
            )
        }
        if "spell" in compiled_access_surface.allowed_kinds:
            for record_key in compiled_access_surface.visible_spell_keys:
                try:
                    spell_record = spell_records_by_key[record_key]
                except KeyError as exc:
                    raise ValueError(
                        "Missing SpellRecord for compiled spell key '{0}'.".format(
                            record_key
                        )
                    ) from exc
                spell_link = FrameLink.from_view_subject(
                    frame_name=frame_descriptor.frame_name,
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
                        "payload_profile_name": spell_record.payload.profile_name,
                    },
                )
                links_by_id[spell_link.link_id] = spell_link

        return cls(
            frame_name=frame_descriptor.frame_name,
            profile_name=(
                view_profile.name if view_profile is not None else None
            ),
            profile_version=(
                view_profile.version if view_profile is not None else None
            ),
            links_by_id=links_by_id,
            metadata={
                "allowed_kinds": tuple(sorted(compiled_access_surface.allowed_kinds)),
                "frame_payload_fields": tuple(compiled_access_surface.frame_payload_fields),
                "visible_conduit_ids": tuple(compiled_access_surface.visible_conduit_ids),
                "visible_spell_keys": tuple(compiled_access_surface.visible_spell_keys),
                "view_profile_name": (
                    view_profile.name if view_profile is not None else None
                ),
                "view_profile_version": (
                    view_profile.version if view_profile is not None else None
                ),
                "default_detail_level": (
                    view_profile.default_detail_level
                    if view_profile is not None
                    else None
                ),
                "preferred_kind_order": (
                    view_profile.preferred_kind_order
                    if view_profile is not None
                    else tuple()
                ),
                "link_count": len(links_by_id),
                "available_target_count": len(links_by_id),
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
    def profile_name(self) -> Optional[str]:
        """Return the optional applied view profile name."""
        self.check_cleaned()
        return self._profile_name

    @property
    def profile_version(self) -> Optional[str]:
        """Return the optional applied view profile version."""
        self.check_cleaned()
        return self._profile_version

    @property
    def links_by_id(self) -> Dict[str, FrameLink]:
        """Return a detached snapshot of the currently visible links by id."""
        self.check_cleaned()
        with self._lock:
            return dict(self._links_by_id)

    @property
    def available_targets_by_id(self) -> Dict[str, FrameLink]:
        """
        Return the currently available frame targets keyed by target id.

        Contract:
            Returns the same detached snapshot surface as `links_by_id`,
            exposed under the viewer-facing target naming.

        Returns:
            Dict[str, FrameLink]: Available target surface for this frame.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._links_by_id)

    @property
    def available_target_ids_by_kind(self) -> Dict[str, Tuple[str, ...]]:
        """
        Return available target ids grouped by target kind.

        Contract:
            Returns a detached snapshot of the grouped available-target ids.

        Returns:
            Dict[str, Tuple[str, ...]]: Available target ids by kind.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._available_target_ids_by_kind)

    @property
    def active_profiles_by_name(self) -> Dict[str, FrameViewProfile]:
        """
        Return the currently active local view profiles by name.

        Contract:
            Returns a detached snapshot of the active local profile map.

        Returns:
            Dict[str, FrameViewProfile]: Active local view profiles.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._active_profiles_by_name)

    @property
    def default_profile_name(self) -> Optional[str]:
        """
        Return the default local profile name when one exists.

        Returns:
            Optional[str]: Default local profile name.
        """
        self.check_cleaned()
        return self._default_profile_name

    @property
    def metadata(self) -> Dict[str, object]:
        """Return a detached copy of the view metadata map."""
        self.check_cleaned()
        with self._lock:
            return dict(self._metadata)

    def list_available_target_ids(self) -> List[str]:
        """
        Return the current available target ids.

        Contract:
            Returns a snapshot list built from the current visible-link ids.

        Returns:
            List[str]: Available target ids.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._links_by_id.keys())

    def list_available_targets(
            self,
            *,
            source_kind: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return the currently available targets for this frame.

        Args:
            source_kind:
                Optional target kind filter.

        Contract:
            - Returns a detached list of currently visible targets.
            - When `source_kind` is supplied, filters against each link's
              current source-kind label.

        Returns:
            List[FrameLink]: Available frame targets.
        """
        self.check_cleaned()
        with self._lock:
            if source_kind is None:
                return list(self._links_by_id.values())
            if not source_kind:
                raise ValueError("source_kind cannot be empty.")
            return [
                frame_link
                for frame_link in self._links_by_id.values()
                if frame_link.source_kind == source_kind
            ]

    def get_required_available_target(self, target_id: str) -> FrameLink:
        """
        Return one available target by id or raise.

        Args:
            target_id:
                Available target id to resolve.

        Returns:
            FrameLink: Matching available target.
        """
        self.check_cleaned()
        if not target_id:
            raise ValueError("target_id cannot be empty.")
        with self._lock:
            try:
                return self._links_by_id[target_id]
            except KeyError as exc:
                raise ValueError(
                    "FrameView target '{0}' was not found.".format(target_id)
                ) from exc

    def list_active_profile_names(self) -> List[str]:
        """
        Return the active local profile names for this view.

        Returns:
            List[str]: Active local view profile names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._active_profiles_by_name.keys())

    def get_default_profile(self) -> FrameViewProfile:
        """
        Return the default local view profile.

        Returns:
            FrameViewProfile: Default local view profile.
        """
        self.check_cleaned()
        if self._default_profile_name is None:
            raise ValueError("FrameView has no default local profile.")
        return self.get_required_active_profile(self._default_profile_name)

    def set_default_profile(self, profile_name: str) -> None:
        """
        Set the default local profile by name.

        Args:
            profile_name:
                Active local profile name.

        Returns:
            None.
        """
        self.check_cleaned()
        if not profile_name:
            raise ValueError("profile_name cannot be empty.")
        with self._lock:
            if profile_name not in self._active_profiles_by_name:
                raise ValueError(
                    "FrameView profile '{0}' was not found.".format(profile_name)
                )
            self._default_profile_name = profile_name

    def register_active_profile(self, profile: FrameViewProfile) -> None:
        """
        Register or replace one active local view profile.

        Args:
            profile:
                Local profile to activate on this view.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(profile, FrameViewProfile):
            raise TypeError("profile must be a FrameViewProfile.")
        with self._lock:
            existing_profile = self._active_profiles_by_name.get(profile.name)
            if existing_profile is not None and existing_profile is not profile:
                existing_profile.cleanup()
            self._active_profiles_by_name[profile.name] = profile
            if self._default_profile_name is None:
                self._default_profile_name = profile.name

    def get_required_active_profile(self, profile_name: str) -> FrameViewProfile:
        """
        Return one active local profile by name or raise.

        Args:
            profile_name:
                Active profile name to resolve.

        Returns:
            FrameViewProfile: Matching active local profile.
        """
        self.check_cleaned()
        if not profile_name:
            raise ValueError("profile_name cannot be empty.")
        with self._lock:
            try:
                return self._active_profiles_by_name[profile_name]
            except KeyError as exc:
                raise ValueError(
                    "FrameView profile '{0}' was not found.".format(profile_name)
                ) from exc

    def clone(self) -> "FrameView":
        """
        Internal

        Return a detached copy of the frame view and its owned links.

        Purpose:
            Support safe cached projection returns where Nexus stores one
            canonical projected view but callers receive their own cleanup-safe
            copy.

        Returns:
            FrameView: Detached frame-view copy.
        """
        self.check_cleaned()
        with self._lock:
            return FrameView(
                frame_name=self._frame_name,
                profile_name=self._profile_name,
                profile_version=self._profile_version,
                profile_builder=FrameViewProfileBuilder(),
                active_profiles_by_name={
                    profile_name: frame_view_profile.clone()
                    for profile_name, frame_view_profile in (
                        self._active_profiles_by_name.items()
                    )
                },
                default_profile_name=self._default_profile_name,
                links_by_id={
                    link_id: frame_link.clone()
                    for link_id, frame_link in self._links_by_id.items()
                },
                metadata=dict(self._metadata),
            )

    def list_available_targets_in_profile_order(
            self,
            *,
            profile_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[FrameLink]:
        """
        Return available targets ordered by the selected local profile.

        Args:
            profile_name:
                Optional local profile name. When omitted, the default local
                profile is used.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[FrameLink]: Available targets in profile-preferred order.
        """
        self.check_cleaned()
        selected_profile = (
            self.get_required_active_profile(profile_name)
            if profile_name is not None
            else self.get_default_profile()
        )
        available_targets = self.list_available_targets(source_kind=source_kind)
        ordered_targets: List[FrameLink] = []
        handled_target_ids = set()
        for preferred_kind in selected_profile.preferred_kind_order:
            for frame_link in available_targets:
                if frame_link.link_id in handled_target_ids:
                    continue
                if frame_link.source_kind != preferred_kind:
                    continue
                ordered_targets.append(frame_link)
                handled_target_ids.add(frame_link.link_id)
        for frame_link in available_targets:
            if frame_link.link_id in handled_target_ids:
                continue
            ordered_targets.append(frame_link)
        return ordered_targets

    def describe_available_targets(
            self,
            *,
            profile_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """
        Return profile-shaped target descriptions for this frame.

        Args:
            profile_name:
                Optional local profile name. When omitted, the default local
                profile is used.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[Dict[str, object]]: Target descriptions in profile order.
        """
        self.check_cleaned()
        selected_profile = (
            self.get_required_active_profile(profile_name)
            if profile_name is not None
            else self.get_default_profile()
        )
        target_descriptions: List[Dict[str, object]] = []
        for frame_link in self.list_available_targets_in_profile_order(
                profile_name=profile_name,
                source_kind=source_kind,
        ):
            description = {
                "target_id": frame_link.link_id,
                "source_kind": frame_link.source_kind,
                "source_id": frame_link.source_id,
                "display_name": frame_link.display_name,
            }
            if selected_profile.default_detail_level == "detailed":
                description["metadata"] = frame_link.metadata
            target_descriptions.append(description)
        return target_descriptions

    @staticmethod
    def _build_available_target_ids_by_kind(
            links_by_id: Dict[str, FrameLink],
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Build the available target ids grouped by target kind.

        Args:
            links_by_id:
                Available frame targets keyed by target id.

        Returns:
            Dict[str, Tuple[str, ...]]: Target ids grouped by kind.
        """
        target_ids_by_kind: Dict[str, List[str]] = {}
        for target_id, frame_link in links_by_id.items():
            target_ids_by_kind.setdefault(frame_link.source_kind, []).append(target_id)
        return {
            source_kind: tuple(target_ids_by_kind[source_kind])
            for source_kind in sorted(target_ids_by_kind.keys())
        }
