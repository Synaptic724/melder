from typing import Any, Dict, Iterator, List, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aether import Aether
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile_builder import (
    FrameViewerProfileBuilder,
)
from melder.spellbook.existence.existence import Existence


class StaticFrameViewer(FrameViewer):
    """
    Static-room viewer overlay that filters spell-facing surfaces to live-only.

    Purpose:
        Preserve the generic descriptor-backed viewer host while narrowing the
        static-room spell surface down to already-live spells.

    Contract:
        - Keeps frame and conduit visibility structural.
        - Filters spell-facing queries and spell target projection to
          already-live spells only.
        - Uses the existing no-create live probe/runtime truth and never
          mutates descriptor publication.
        - Rebuilds frame-local selected profiles after each live refresh so
          profile-driven spell target lists stay aligned with the filtered
          spell surface.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = ["_base_compiled_access_surfaces_by_frame_name"]
    _aether = Aether()

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize one static viewer overlay.

        Args:
            **kwargs:
                Forwarded to `FrameViewer`.
        """
        super().__init__(**kwargs)
        self._base_compiled_access_surfaces_by_frame_name: Dict[
            str,
            CompiledFrameACLAccessSurface,
        ] = {
            frame_name: self._clone_compiled_access_surface(compiled_access_surface)
            for frame_name, compiled_access_surface in (
                self._compiled_access_surfaces_by_frame_name.items()
            )
        }
        self.refresh_live_spell_projection()

    @classmethod
    def from_frame_viewer(cls, frame_viewer: FrameViewer) -> "StaticFrameViewer":
        """
        Build one static viewer from an existing viewer host.

        Args:
            frame_viewer:
                Existing viewer host to clone into a static overlay.

        Returns:
            StaticFrameViewer: Static viewer overlay.
        """
        frame_viewer.check_cleaned()
        if isinstance(frame_viewer, StaticFrameViewer):
            source_compiled_access_surfaces = (
                frame_viewer._base_compiled_access_surfaces_by_frame_name
            )
        else:
            source_compiled_access_surfaces = (
                frame_viewer._compiled_access_surfaces_by_frame_name
            )
        return cls(
            profile_builder=FrameViewerProfileBuilder(),
            active_profiles_by_name={
                profile_name: frame_viewer_profile.clone()
                for profile_name, frame_viewer_profile in (
                    frame_viewer._active_profiles_by_name.items()
                )
            },
            default_profile_name=frame_viewer._default_profile_name,
            frame_descriptors_by_name=dict(frame_viewer._frame_descriptors_by_name),
            frame_acl_configurations_by_frame_name=dict(
                frame_viewer._frame_acl_configurations_by_frame_name
            ),
            compiled_access_surfaces_by_frame_name={
                frame_name: frame_viewer._clone_compiled_access_surface(
                    compiled_access_surface
                )
                for frame_name, compiled_access_surface in (
                    source_compiled_access_surfaces.items()
                )
            },
            selected_profile_names_by_frame_name=(
                frame_viewer.selected_profile_names_by_frame_name
            ),
            default_view_frame_name=frame_viewer._default_view_frame_name,
            metadata=dict(frame_viewer._metadata),
        )

    def cleanup(self) -> None:
        """
        Idempotently clear static-viewer-owned overlay state.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            for compiled_access_surface in (
                    self._base_compiled_access_surfaces_by_frame_name.values()
            ):
                compiled_access_surface.cleanup()
            self._base_compiled_access_surfaces_by_frame_name.clear()
            self._base_compiled_access_surfaces_by_frame_name = None
        super().cleanup()

    def clone(self) -> "StaticFrameViewer":
        """
        Return a detached clone of this static viewer overlay.

        Returns:
            StaticFrameViewer: Detached static viewer clone.
        """
        self.check_cleaned()
        with self._lock:
            return StaticFrameViewer.from_frame_viewer(self)

    def execute_method(
            self,
            method_name: str,
            *,
            profile_name: Optional[str] = None,
            **kwargs: Any
    ) -> Any:
        """
        Refresh live spell projection before executing one profile/viewer method.

        Args:
            method_name:
                Exposed profile method name to execute.
            profile_name:
                Optional profile override.
            **kwargs:
                Arguments forwarded to the resolved handler.

        Returns:
            Any: Handler return value.
        """
        self.refresh_live_spell_projection(kwargs.get("frame_name"))
        return super().execute_method(
            method_name,
            profile_name=profile_name,
            **kwargs
        )

    def list_spell_source_ids_for_frame(self, frame_name: str) -> List[str]:
        """
        Return live-only spell source ids for one hosted frame.

        Args:
            frame_name:
                Hosted frame name.

        Returns:
            List[str]: Live-only spell source ids.
        """
        self.refresh_live_spell_projection(frame_name)
        return [
            self._build_spell_source_id(spell_record)
            for spell_record in self._iter_live_spell_records_for_frame(frame_name)
        ]

    def _iter_spell_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Iterator[object]:
        """
        Yield live-only spell records in deterministic hosted order.

        Args:
            frame_name:
                Optional hosted frame name.

        Yields:
            object: Live-only spell records.
        """
        self.refresh_live_spell_projection(frame_name)
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            for spell_record in self._iter_live_spell_records_for_frame(
                    current_frame_name
            ):
                yield spell_record

    def _get_required_spell_record(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, object]:
        """
        Return one live-only spell record plus its frame name or raise.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional hosted frame name to constrain the lookup.

        Returns:
            Tuple[str, object]: `(frame_name, spell_record)` for the resolved
            live spell.
        """
        self.refresh_live_spell_projection(frame_name)
        if not spell_source_id:
            raise ValueError("spell_source_id cannot be empty.")
        spellbook_id, spell_id = self._parse_spell_source_id(spell_source_id)
        matching_records: List[Tuple[str, object]] = []
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            for spell_record in self._iter_live_spell_records_for_frame(
                    current_frame_name
            ):
                if (
                        spell_record.origin_spellbook_id == spellbook_id
                        and spell_record.spell_id == spell_id
                ):
                    matching_records.append((current_frame_name, spell_record))
        if len(matching_records) == 0:
            raise ValueError(
                "Spell source id '{0}' was not found.".format(spell_source_id)
            )
        if len(matching_records) > 1:
            raise ValueError(
                "Spell source id '{0}' is ambiguous across hosted frames.".format(
                    spell_source_id
                )
            )
        return matching_records[0]

    def refresh_live_spell_projection(
            self,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Refresh the live-only spell overlay for one frame or all hosted frames.

        Args:
            frame_name:
                Optional hosted frame name.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            for current_frame_name in self._get_frame_names_for_query(frame_name):
                base_compiled_access_surface = (
                    self._base_compiled_access_surfaces_by_frame_name[
                        current_frame_name
                    ]
                )
                live_spell_records = self._iter_live_spell_records_for_frame(
                    current_frame_name
                )
                live_record_keys = {spell_record.record_key for spell_record in live_spell_records}
                filtered_visible_spell_keys = tuple(
                    record_key
                    for record_key in base_compiled_access_surface.visible_spell_keys
                    if record_key in live_record_keys
                )
                live_spell_index_ids = {
                    spell_record.spell_index_id for spell_record in live_spell_records
                }
                filtered_visible_spell_index_ids = tuple(
                    spell_index_id
                    for spell_index_id in (
                        base_compiled_access_surface.visible_spell_index_ids
                    )
                    if spell_index_id in live_spell_index_ids
                )
                filtered_compiled_access_surface = CompiledFrameACLAccessSurface(
                    frame_name=base_compiled_access_surface.frame_name,
                    configuration_id=base_compiled_access_surface.configuration_id,
                    view_profile_name=base_compiled_access_surface.view_profile_name,
                    view_profile_version=base_compiled_access_surface.view_profile_version,
                    codegen_profile_name=base_compiled_access_surface.codegen_profile_name,
                    codegen_profile_version=base_compiled_access_surface.codegen_profile_version,
                    command_frame_enabled=base_compiled_access_surface.command_frame_enabled,
                    allowed_kinds=base_compiled_access_surface.allowed_kinds,
                    allowed_commands=base_compiled_access_surface.allowed_commands,
                    frame_payload_fields=base_compiled_access_surface.frame_payload_fields,
                    visible_conduit_ids=base_compiled_access_surface.visible_conduit_ids,
                    visible_spell_keys=filtered_visible_spell_keys,
                    visible_spell_index_ids=filtered_visible_spell_index_ids,
                    enabled_conduit_ids=base_compiled_access_surface.enabled_conduit_ids,
                    enabled_spell_index_ids=base_compiled_access_surface.enabled_spell_index_ids,
                    conduit_payload_sections_by_id=(
                        base_compiled_access_surface.conduit_payload_sections_by_id
                    ),
                    spell_payload_sections_by_key=(
                        base_compiled_access_surface.spell_payload_sections_by_key
                    ),
                    metadata=base_compiled_access_surface.metadata,
                )
                current_compiled_access_surface = (
                    self._compiled_access_surfaces_by_frame_name[current_frame_name]
                )
                current_compiled_access_surface.cleanup()
                self._compiled_access_surfaces_by_frame_name[current_frame_name] = (
                    filtered_compiled_access_surface
                )
                selected_profile_name = self.selected_profile_names_by_frame_name.get(
                    current_frame_name,
                    self._default_profile_name,
                )
                current_selected_profile = self._selected_profiles_by_frame_name.get(
                    current_frame_name
                )
                if current_selected_profile is not None:
                    current_selected_profile.cleanup()
                if selected_profile_name is not None:
                    self._selected_profiles_by_frame_name[current_frame_name] = (
                        self._create_bound_profile_for_frame(
                            current_frame_name,
                            selected_profile_name,
                        )
                    )

    def _iter_live_spell_records_for_frame(self, frame_name: str) -> List[object]:
        """
        Return the live visible spell records for one frame.

        Args:
            frame_name:
                Hosted frame name.

        Returns:
            List[object]: Live visible spell records in deterministic order.
        """
        descriptor = self._get_required_frame_descriptor(frame_name)
        base_compiled_access_surface = self._base_compiled_access_surfaces_by_frame_name[
            frame_name
        ]
        live_spell_records: List[object] = []
        for record_key in base_compiled_access_surface.visible_spell_keys:
            spell_record = descriptor.spell_records_by_key.get(record_key)
            if spell_record is None:
                continue
            if self._is_spell_record_live(frame_name, spell_record):
                live_spell_records.append(spell_record)
        return live_spell_records

    def _is_spell_record_live(self, frame_name: str, spell_record: object) -> bool:
        """
        Return whether one published spell record currently has a live object.

        Args:
            frame_name:
                Hosted frame name.
            spell_record:
                Published spell record to probe.

        Returns:
            bool: True when the spell is currently live.
        """
        if spell_record.existence in {
                Existence.many,
                Existence.unique_per_spell_space,
        }:
            return False
        owner_conduit_id = spell_record.owner_conduit_id
        if not owner_conduit_id:
            return False
        owner_conduit = self._get_owner_conduit(frame_name, owner_conduit_id)
        if owner_conduit is None:
            return False
        try:
            return owner_conduit.has_live_creation(spell=spell_record.spell_id)
        except ValueError:
            return False

    def _get_owner_conduit(
            self,
            frame_name: str,
            conduit_id: str,
    ) -> Optional[Any]:
        """
        Resolve one owner conduit, including lesser-conduit fallback.

        Args:
            frame_name:
                Hosted frame name.
            conduit_id:
                Owner conduit id to resolve.

        Returns:
            Optional[Any]: Matching conduit, or None when missing.
        """
        try:
            return self._aether.get_conduit_by_id(conduit_id, frame_name)
        except ValueError:
            if frame_name != "default":
                frame = self._aether._aetheric_frames.get(frame_name)
            else:
                self._aether._ensure_default_frame()
                frame = self._aether._default_frame
            if frame is None:
                return None
            for root_conduit in frame._conduits.values():
                conduit_ward = root_conduit._conduit_ward
                if conduit_ward is None:
                    continue
                lesser_conduit = conduit_ward._get_lesser_conduit(conduit_id)
                if lesser_conduit is not None:
                    return lesser_conduit
        return None
