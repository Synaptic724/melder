from typing import Optional

from melder.aether.nexus.rift.rift_space.command_system.command_system import (
    CommandSystem,
)


class StaticCommandSystem(CommandSystem):
    """
    Internal

    Static-room command surface.

    Purpose:
        Keep the shared command API while restricting raw runtime-object
        exposure for `StaticRiftSpace`.

    Contract:
        - Inherits all shared selected-target, ACL, and workstation behavior
          from `CommandSystem`.
        - Allows the shared command getter names to remain intact while
          specializing spell runtime retrieval to live-only behavior.
        - Uses current runtime creation storage only and never creates through
          the generic spell getters.
        - Leaves already-bound workstation objects outside post-bind policing.
    """

    def _assert_raw_runtime_object_access_allowed(
            self,
            method_name: str,
    ) -> None:
        """
        Allow the shared raw getter names in static rooms.

        Args:
            method_name:
                Public command-system method attempting raw runtime-object
                exposure.

        Returns:
            None.
        """
        _ = method_name

    def get_spell_object_by_source_id(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one already-live spell runtime object using a published spell source id.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Already-live spell runtime object.

        Raises:
            ValueError:
                If the spell is not published in the selected frame or is not
                currently live.
        """
        viewer = self._space.get_required_frame_viewer()
        resolved_frame_name, spell_record = viewer._get_required_spell_record(
            spell_source_id,
            frame_name=frame_name,
        )
        return self.get_spell_object_by_index_id(
            spell_record.spell_index_id,
            frame_name=resolved_frame_name,
        )

    def get_spell_object_by_index_id(
            self,
            spell_index_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one already-live spell runtime object by stable spell lineage id.

        Args:
            spell_index_id:
                Stable SpellIndex lineage id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Already-live spell runtime object.

        Raises:
            ValueError:
                If the spell lineage is not published in the selected frame or
                does not currently have a live creation.
        """
        self.check_cleaned()
        with self._lock:
            if not spell_index_id:
                raise ValueError("spell_index_id cannot be empty.")
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._assert_frame_command_enabled(resolved_frame_name)
            self._assert_spell_command_enabled(
                spell_index_id,
                frame_name=resolved_frame_name,
            )
            viewer = self._space.get_required_frame_viewer()
            descriptor = viewer._get_required_frame_descriptor(resolved_frame_name)
            matching_spell_records = [
                spell_record
                for spell_record in descriptor.spell_records_by_key.values()
                if spell_record.spell_index_id == spell_index_id
            ]
            if len(matching_spell_records) == 0:
                raise ValueError(
                    "Spell index id '{0}' was not found in frame '{1}'.".format(
                        spell_index_id,
                        resolved_frame_name,
                    )
                )
            for spell_record in matching_spell_records:
                owner_conduit_id = spell_record.owner_conduit_id
                if not owner_conduit_id:
                    continue
                owner_conduit = self.get_conduit_object_by_id(
                    owner_conduit_id,
                    frame_name=resolved_frame_name,
                )
                spell_runtime_object = (
                    owner_conduit._get_live_spell_runtime_object_by_index_id(
                        spell_index_id
                    )
                )
                if spell_runtime_object is not None:
                    return spell_runtime_object
            raise ValueError(
                "Spell lineage '{0}' is not live in frame '{1}'.".format(
                    spell_index_id,
                    resolved_frame_name,
                )
            )

    def get_spell_object_by_id(
            self,
            spell_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one already-live spell runtime object by current spell id.

        Args:
            spell_id:
                Current spell id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Already-live spell runtime object.

        Raises:
            ValueError:
                If the spell is not published in the selected frame or does
                not currently have a live creation.
        """
        resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
        spell_index_id = self._get_required_published_spell_index_id_by_spell_id(
            spell_id,
            frame_name=resolved_frame_name,
        )
        return self.get_spell_object_by_index_id(
            spell_index_id,
            frame_name=resolved_frame_name,
        )
