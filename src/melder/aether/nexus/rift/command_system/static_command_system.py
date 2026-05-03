from typing import Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)
from melder.spellbook.existence.existence import Existence


class StaticCommandSystem(CommandSystem):
    """
    Internal

    Static-room command surface.

    Purpose:
        Keep the shared command infrastructure while owning the static-safe
        command surface for `StaticRiftSpace`.

    Contract:
        - Inherits all shared selected-target, ACL, and workstation behavior
          from `CommandSystem`.
        - Owns live-only spell runtime retrieval under the shared getter names.
        - Owns static-specific spell status and reuse-only command helpers.
        - Does not expose topology mutation or direct `meld(...)` because those
          methods now live on the capability surface instead of being denied
          after inheritance.
        - Leaves already-bound workstation objects outside post-bind policing.
    """
    __melder_internal__ = _mrg.sentinel
    _STATIC_COMMAND_METHOD_NAMES: tuple[str, ...] = (
        "meld_existing_spell",
        "describe_spell_status_by_source_id",
        "describe_spell_status_by_id",
        "describe_spell_status_by_index_id",
    )

    def _get_spell_by_index_id_locked(
            self,
            spell_index_id: str,
            *,
            frame_name: str,
    ) -> object:
        """
        Resolve one static-room spell runtime object by stable lineage id while
        the command lock is already held.

        Args:
            spell_index_id:
                Stable SpellIndex lineage id to resolve.
            frame_name:
                Resolved hosted frame name.

        Returns:
            object: Already-live spell runtime object.

        Raises:
            ValueError:
                If the lineage id is empty, unpublished, command-disabled, uses
                unsupported static existence, or is not currently live.
        """
        if not spell_index_id:
            raise ValueError("spell_index_id cannot be empty.")
        self._assert_frame_command_enabled(frame_name)
        self._assert_spell_command_enabled(
            spell_index_id,
            frame_name=frame_name,
        )
        descriptor = self._rift._get_required_command_projection(
            frame_name
        ).frame_descriptor
        matching_spell_records = [
            spell_record
            for spell_record in descriptor.spell_records_by_key.values()
            if spell_record.spell_index_id == spell_index_id
        ]
        if len(matching_spell_records) == 0:
            raise ValueError(
                "Spell index id '{0}' was not found in frame '{1}'.".format(
                    spell_index_id,
                    frame_name,
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
                frame_name,
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
                frame_name,
            )
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
        with self._entered_command_action(
                action_name="get_spell_by_source_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            spell_record = self._get_required_published_spell_record_by_source_id(
                spell_source_id,
                frame_name=resolved_frame_name,
            )
            return self._get_spell_by_index_id_locked(
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
        with self._entered_command_action(
                action_name="describe_spell_status_by_source_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            if not spell_source_id:
                raise ValueError("spell_source_id cannot be empty.")
            spellbook_id, spell_id = spell_source_id.split(":", 1)
            descriptor = self._rift._get_required_command_projection(
                resolved_frame_name
            ).frame_descriptor
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
        with self._entered_command_action(
                action_name="describe_spell_status_by_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            descriptor = self._rift._get_required_command_projection(
                resolved_frame_name
            ).frame_descriptor
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
        with self._entered_command_action(
                action_name="describe_spell_status_by_index_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            descriptor = self._rift._get_required_command_projection(
                resolved_frame_name
            ).frame_descriptor
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
        with self._entered_command_action(
                action_name="get_spell_by_index_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            return self._get_spell_by_index_id_locked(
                spell_index_id,
                frame_name=resolved_frame_name,
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
        with self._entered_command_action(
                action_name="get_spell_by_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            spell_index_id = self._get_required_published_spell_index_id_by_spell_id(
                spell_id,
                frame_name=resolved_frame_name,
            )
            return self._get_spell_by_index_id_locked(
                spell_index_id,
                frame_name=resolved_frame_name,
            )

    def meld_existing_spell(
            self,
            conduit_id: str,
            spell_name: Optional[str] = None,
            *,
            spell: Optional[object] = None,
            spellframe: Optional[object] = None,
            binding_name: Optional[str] = None,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one already-live spell runtime object through a selected conduit.

        Purpose:
            Keep the reuse-only spell-activation helper on the static command
            surface without inheriting the broader capability activation set.

        Args:
            conduit_id:
                Conduit id that should perform the reuse-only resolution.
            spell_name:
                Optional logical spell name key.
            spell:
                Optional spell id string or spell object.
            spellframe:
                Optional spellframe / protocol / frame key.
            binding_name:
                Optional binding name for resolution.
            frame_name:
                Optional hosted frame name. When omitted, the room default
                frame is used.

        Returns:
            object: Already-live runtime object returned by the conduit.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="meld_existing_spell",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            conduit = self._get_conduit_by_id_locked(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return conduit.meld_existing_spell(
                spell_name=spell_name,
                spell=spell,
                spellframe=spellframe,
                binding_name=binding_name,
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
            tuple[str, ...]: Shared command names plus static-owned helper
                names in stable presentation order.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="list_supported_command_methods",
                frame_name=None,
        ):
            return self._list_supported_command_methods_tuple() + (
                self._STATIC_COMMAND_METHOD_NAMES
            )
