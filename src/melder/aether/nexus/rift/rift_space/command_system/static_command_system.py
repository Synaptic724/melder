from typing import Optional

from melder.aether.nexus.rift.rift_space.command_system.command_system import (
    CommandSystem,
)
from melder.spellbook.existence.existence import Existence


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

    def _assert_topology_mutation_allowed(
            self,
            method_name: str,
    ) -> None:
        """
        Deny runtime topology mutation through the static command surface.

        Args:
            method_name:
                Shared topology-mutation method being attempted.

        Returns:
            None.

        Raises:
            ValueError:
                Always, because static rooms do not allow runtime structure
                creation or rewiring through the command surface.
        """
        raise ValueError(
            "Static command surface does not allow topology mutation method '{0}'.".format(
                method_name
            )
        )

    def _assert_spell_activation_allowed(
            self,
            method_name: str,
    ) -> None:
        """
        Deny direct conduit-level spell activation in static rooms.

        Args:
            method_name:
                Shared spell-activation method being attempted.

        Returns:
            None.

        Raises:
            ValueError:
                Always, because static rooms must use the published live-only
                spell surface instead of direct raw conduit activation.
        """
        if method_name == "meld":
            raise ValueError(
                "Static command surface does not allow spell activation method '{0}'.".format(
                    method_name
                )
            )

    def list_clusters(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> tuple[str, ...]:
        """
        Deny cluster listing through the static command surface.

        Args:
            conduit_id:
                Ignored conduit id from the shared command signature.
            frame_name:
                Ignored frame name from the shared command signature.

        Returns:
            tuple[str, ...]: Never returns successfully.

        Raises:
            ValueError:
                Always, because static rooms do not expose cluster topology.
        """
        _ = conduit_id
        _ = frame_name
        raise ValueError(
            "Static command surface does not allow cluster query method 'list_clusters'."
        )

    def get_spell_by_source_id(
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
        return self.get_spell_by_index_id(
            spell_record.spell_index_id,
            frame_name=resolved_frame_name,
        )

    def describe_spell_status_by_source_id(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> dict:
        """
        Return static availability status for one published spell source id.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            dict: Static spell status payload.
        """
        resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
        if not spell_source_id:
            raise ValueError("spell_source_id cannot be empty.")
        spellbook_id, spell_id = spell_source_id.split(":", 1)
        viewer = self._space.get_required_frame_viewer()
        descriptor = viewer._get_required_frame_descriptor(resolved_frame_name)
        matching_spell_records = [
            spell_record
            for spell_record in descriptor.spell_records_by_key.values()
            if (
                spell_record.origin_spellbook_id == spellbook_id
                and spell_record.spell_id == spell_id
            )
        ]
        if len(matching_spell_records) == 0:
            return {
                "frame_name": resolved_frame_name,
                "spell_source_id": spell_source_id,
                "is_published": False,
                "is_command_enabled": False,
                "is_static_supported": False,
                "is_live": False,
                "is_available": False,
                "reason": "not_published",
            }
        if len(matching_spell_records) > 1:
            return {
                "frame_name": resolved_frame_name,
                "spell_source_id": spell_source_id,
                "is_published": True,
                "is_command_enabled": False,
                "is_static_supported": False,
                "is_live": False,
                "is_available": False,
                "reason": "ambiguous_spell_source_id",
            }
        return self._describe_static_spell_status(
            matching_spell_records[0],
            frame_name=resolved_frame_name,
        )

    def describe_spell_status_by_id(
            self,
            spell_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> dict:
        """
        Return static availability status for one current spell id.

        Args:
            spell_id:
                Current spell id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            dict: Static spell status payload.
        """
        resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
        viewer = self._space.get_required_frame_viewer()
        descriptor = viewer._get_required_frame_descriptor(resolved_frame_name)
        matching_spell_records = [
            spell_record
            for spell_record in descriptor.spell_records_by_key.values()
            if spell_record.spell_id == spell_id
        ]
        if len(matching_spell_records) == 0:
            return {
                "frame_name": resolved_frame_name,
                "spell_id": spell_id,
                "is_published": False,
                "is_command_enabled": False,
                "is_static_supported": False,
                "is_live": False,
                "is_available": False,
                "reason": "not_published",
            }
        if len(matching_spell_records) > 1:
            return {
                "frame_name": resolved_frame_name,
                "spell_id": spell_id,
                "is_published": True,
                "is_command_enabled": False,
                "is_static_supported": False,
                "is_live": False,
                "is_available": False,
                "reason": "ambiguous_spell_id",
            }
        return self._describe_static_spell_status(
            matching_spell_records[0],
            frame_name=resolved_frame_name,
        )

    def describe_spell_status_by_index_id(
            self,
            spell_index_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> dict:
        """
        Return static availability status for one stable spell lineage id.

        Args:
            spell_index_id:
                Stable SpellIndex lineage id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            dict: Static spell status payload.
        """
        resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
        viewer = self._space.get_required_frame_viewer()
        descriptor = viewer._get_required_frame_descriptor(resolved_frame_name)
        matching_spell_records = [
            spell_record
            for spell_record in descriptor.spell_records_by_key.values()
            if spell_record.spell_index_id == spell_index_id
        ]
        if len(matching_spell_records) == 0:
            return {
                "frame_name": resolved_frame_name,
                "spell_index_id": spell_index_id,
                "is_published": False,
                "is_command_enabled": False,
                "is_static_supported": False,
                "is_live": False,
                "is_available": False,
                "reason": "not_published",
            }
        if len(matching_spell_records) > 1:
            return {
                "frame_name": resolved_frame_name,
                "spell_index_id": spell_index_id,
                "is_published": True,
                "is_command_enabled": False,
                "is_static_supported": False,
                "is_live": False,
                "is_available": False,
                "reason": "ambiguous_spell_index_id",
            }
        return self._describe_static_spell_status(
            matching_spell_records[0],
            frame_name=resolved_frame_name,
        )

    def get_spell_by_index_id(
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
            if spell_record.existence in {
                    Existence.many,
                    Existence.unique_per_spell_space,
            }:
                continue
            owner_conduit_id = spell_record.owner_conduit_id
            if not owner_conduit_id:
                continue
            owner_conduit = self._aether._get_conduit_by_id(
                owner_conduit_id,
                resolved_frame_name,
            )
            try:
                return owner_conduit.meld_existing_spell(
                    spell=spell_record.spell_id,
                )
            except ValueError:
                continue
        unsupported_spell_record = next(
            (
                spell_record
                for spell_record in matching_spell_records
                if spell_record.existence in {
                    Existence.many,
                    Existence.unique_per_spell_space,
                }
            ),
            None,
        )
        if unsupported_spell_record is not None:
            raise ValueError(
                "Spell lineage '{0}' uses unsupported static existence '{1}'.".format(
                    spell_index_id,
                    unsupported_spell_record.existence.name,
                )
            )
        raise ValueError(
            "Spell lineage '{0}' is not live in frame '{1}'.".format(
                spell_index_id,
                resolved_frame_name,
            )
        )

    def get_spell_by_id(
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
        return self.get_spell_by_index_id(
            spell_index_id,
            frame_name=resolved_frame_name,
        )

    def _describe_static_spell_status(
            self,
            spell_record: object,
            *,
            frame_name: str,
    ) -> dict:
        """
        Build one static spell status payload from a published spell record.

        Args:
            spell_record:
                Published spell record to inspect.
            frame_name:
                Hosted frame name.

        Returns:
            dict: Static spell status payload.
        """
        is_command_enabled = False
        try:
            self._assert_frame_command_enabled(frame_name)
            self._assert_spell_command_enabled(
                spell_record.spell_index_id,
                frame_name=frame_name,
            )
            is_command_enabled = True
        except ValueError:
            is_command_enabled = False
        is_static_supported = spell_record.existence not in {
            Existence.many,
            Existence.unique_per_spell_space,
        }
        is_live = False
        owner_conduit_id = spell_record.owner_conduit_id
        if owner_conduit_id:
            owner_conduit = self._aether._get_conduit_by_id(
                owner_conduit_id,
                frame_name,
            )
            is_live = owner_conduit.has_live_creation(spell=spell_record.spell_id)
        if not is_command_enabled:
            reason = "command_disabled"
        elif not is_static_supported:
            reason = "unsupported_static_existence"
        elif not is_live:
            reason = "not_live"
        else:
            reason = "available"
        return {
            "frame_name": frame_name,
            "spell_source_id": "{0}:{1}".format(
                spell_record.origin_spellbook_id,
                spell_record.spell_id,
            ),
            "spell_id": spell_record.spell_id,
            "spell_index_id": spell_record.spell_index_id,
            "spell_name": spell_record.spell_name,
            "binding_name": spell_record.binding_name,
            "existence": spell_record.existence.name,
            "is_published": True,
            "is_command_enabled": is_command_enabled,
            "is_static_supported": is_static_supported,
            "is_live": is_live,
            "is_available": (
                is_command_enabled and is_static_supported and is_live
            ),
            "reason": reason,
        }

    def list_supported_command_methods(self) -> tuple[str, ...]:
        """
        Return the public command methods supported by static rooms.

        Returns:
            tuple[str, ...]: Supported public command method names for static
                command usage.
        """
        denied_methods = {
            "create_lesser_conduit",
            "create_cluster",
            "delete_cluster",
            "join_cluster",
            "leave_cluster",
            "list_clusters",
            "link",
            "sever_link",
            "meld",
        }
        return tuple(
            method_name
            for method_name in super().list_supported_command_methods()
            if method_name not in denied_methods
        )
