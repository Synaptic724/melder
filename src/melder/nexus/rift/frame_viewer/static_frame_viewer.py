from typing import TYPE_CHECKING, Any, Iterator, List, Optional, Tuple

from melder.aether.aether import Aether
from melder.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.spellbook.existence.existence import Existence

if TYPE_CHECKING:
    from melder.nexus.frame_descriptor.spell_record import SpellRecord


class StaticFrameViewer(FrameViewer):
    """
    Static-room viewer overlay that filters spell-facing surfaces to live-only.

    Purpose:
        Preserve the generic Rift-backed viewer host while narrowing the
        static-room spell surface down to already-live spells.

    Contract:
        - Inherits the same Rift-backed projection ownership model as
          `FrameViewer`.
        - Keeps frame and conduit visibility structural.
        - Filters spell-facing visibility and spell-record iteration down to
          already-live spells only.
        - Uses the existing no-create live probe/runtime truth and never
          mutates descriptor publication.

    Registration:
        MELDER KERNEL - guarded. Created by `StaticRiftSpace` during room init;
        never constructed directly.

    Subsystem Context:
        The static overlay over `FrameViewer`, and the only viewer swap in the
        room ladder. It keeps the same Rift-backed projection ownership model -
        it narrows WHAT is visible, not WHERE truth comes from.

    System Context:
        The filtering is asymmetric on purpose: frame and conduit visibility
        stay STRUCTURAL, while spell-facing visibility narrows to already-live
        spells. Structure is safe to observe because seeing that a conduit
        exists causes nothing; a spell record is different, because resolving
        one is exactly the create-path a static room must not take.
        This is why it uses the existing NO-CREATE live probe rather than
        attempting resolution and discarding failures. A probe that resolved to
        find out would defeat the room's entire posture, constructing instances
        as a side effect of looking. It also never mutates descriptor
        publication, so a static room cannot change what other Rifts see.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Static-room viewer overlay that filters spell-facing surfaces to "
        "live-only. Melder kernel machinery: read it to understand the runtime, do not drive it "
        "directly."
    )

    __slots__: tuple[()] = ()
    _aether = Aether()

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
        return cls(
            rift=frame_viewer._rift,
            action_hook_scope_factory=frame_viewer._action_hook_scope_factory,
        )

    def clone(self) -> "StaticFrameViewer":
        """
        Return a detached clone of this static viewer overlay.

        Returns:
            StaticFrameViewer: Detached static viewer clone.
        """
        self.check_cleaned()
        with self._lock:
            return StaticFrameViewer.from_frame_viewer(self)

    def _iter_spell_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Iterator[SpellRecord]:
        """
        Yield live-only spell records in deterministic hosted order.

        Args:
            frame_name:
                Optional hosted frame name filter.

        Yields:
            SpellRecord: Live-only spell records.
        """
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            for spell_record in self._iter_live_spell_records_for_frame(
                    current_frame_name
            ):
                yield spell_record

    def list_spell_source_ids_for_frame(self, frame_name: str) -> List[str]:
        """
        Return live-only spell source ids for one hosted frame.

        Args:
            frame_name:
                Hosted frame name.

        Returns:
            List[str]: Live-only spell source ids.
        """
        return [
            self._build_spell_source_id(spell_record)
            for spell_record in self._iter_live_spell_records_for_frame(frame_name)
        ]

    def _get_required_spell_record(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, SpellRecord]:
        """
        Return one live-only spell record plus its frame name or raise.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional hosted frame name to constrain the lookup.

        Returns:
            Tuple[str, SpellRecord]: `(frame_name, spell_record)` for the
            resolved live spell.
        """
        if not spell_source_id:
            raise ValueError("spell_source_id cannot be empty.")
        spellbook_id, spell_id = self._parse_spell_source_id(spell_source_id)
        matching_records: List[Tuple[str, SpellRecord]] = []
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

    def _get_required_compiled_access_surface(
            self,
            frame_name: str,
    ) -> CompiledFrameACLAccessSurface:
        """
        Return the filtered compiled access surface for one frame.

        Args:
            frame_name:
                Hosted frame name.

        Returns:
            CompiledFrameACLAccessSurface: Live-only filtered static-viewer
            surface.
        """
        base_compiled_access_surface = super()._get_required_compiled_access_surface(
            frame_name
        )
        live_spell_records = self._iter_live_spell_records_for_frame(frame_name)
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
            for spell_index_id in base_compiled_access_surface.visible_spell_index_ids
            if spell_index_id in live_spell_index_ids
        )
        return CompiledFrameACLAccessSurface(
            frame_name=base_compiled_access_surface.frame_name,
            configuration_id=base_compiled_access_surface.configuration_id,
            view_profile_name=base_compiled_access_surface.view_profile_name,
            view_profile_version=base_compiled_access_surface.view_profile_version,
            codegen_profile_name=base_compiled_access_surface.codegen_profile_name,
            codegen_profile_version=base_compiled_access_surface.codegen_profile_version,
            codegen_imports_enabled=base_compiled_access_surface.codegen_imports_enabled,
            allowed_import_module_roots=(
                base_compiled_access_surface.allowed_import_module_roots
            ),
            denied_import_module_roots=(
                base_compiled_access_surface.denied_import_module_roots
            ),
            denied_builtin_names=base_compiled_access_surface.denied_builtin_names,
            codegen_unsafe_reflection_allowed=(
                base_compiled_access_surface.codegen_unsafe_reflection_allowed
            ),
            codegen_dunder_access_allowed=(
                base_compiled_access_surface.codegen_dunder_access_allowed
            ),
            codegen_recursive_codegen_allowed=(
                base_compiled_access_surface.codegen_recursive_codegen_allowed
            ),
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

    def _iter_live_spell_records_for_frame(self, frame_name: str) -> List[SpellRecord]:
        """
        Return the live visible spell records for one frame.

        Args:
            frame_name:
                Hosted frame name.

        Returns:
            List[SpellRecord]: Live visible spell records in deterministic
            order.
        """
        descriptor = self._get_required_frame_descriptor(frame_name)
        base_compiled_access_surface = super()._get_required_compiled_access_surface(
            frame_name
        )
        live_spell_records: List[SpellRecord] = []
        for record_key in base_compiled_access_surface.visible_spell_keys:
            spell_record = descriptor.spell_records_by_key.get(record_key)
            if spell_record is None:
                continue
            if self._is_spell_record_live(frame_name, spell_record):
                live_spell_records.append(spell_record)
        return live_spell_records

    def _is_spell_record_live(
            self,
            frame_name: str,
            spell_record: SpellRecord,
    ) -> bool:
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
