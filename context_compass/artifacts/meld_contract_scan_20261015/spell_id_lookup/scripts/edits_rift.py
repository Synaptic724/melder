"""Edits for the Rift room lookups by spell_id (owner, 2026-10-17: "update it all").

`CommandSystem.get_spell_by_id` and `StaticCommandSystem.get_spell_by_id` become `get_spell_by_spell_id`, with the
action name, the raw-access label and the advertised command list. The room lookups that turned a spell_id, or a
source id naming one, into its index and answered with the spell the index has active - or with the live object of
any record of that index - answer exactly that spell. Block hashes are from the 0.2.8251 tree (src unchanged at
0.2.8252 for these files).
"""
from apply_engine import EditEngine

COMMAND = "src/melder/nexus/rift/command_system/command_system.py"
STATIC = "src/melder/nexus/rift/command_system/static_command_system.py"

COMMAND_GET_SPELL_BY_SOURCE_ID = '''    def get_spell_by_source_id(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the Spell a published spell source id names.

        Purpose:
            Hand out the runtime Spell behind one published record, addressed the
            way the frame viewer addresses it: `spellbook_id:spell_id`.

        Contract:
            - Answers exactly the spell the source id names, from its owner's
              Spellbook (`find_spell_by_spell_id`), never another version of its
              SpellIndex; the version an index has active is
              `get_spell_by_index_id`'s answer. Nexus publishes the version an
              index has active, so a published record names that version. Until
              @@SINCE@@ this method resolved the record's index and returned the
              spell the index had active.
            - Enforces raw-runtime access, the frame command gate, the record's
              spell-index ACL and the owner conduit's ACL before touching runtime
              state (`_get_spell_by_record_locked`).
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: The live `Spell` the source id names.

        Raises:
            ValueError:
                If the spell source id is empty, malformed, not published or
                ambiguous in the selected frame, if command ACL denies frame,
                spell or conduit access, if the record has no owner conduit, or
                if the owner's Spellbook no longer holds the spell_id.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_spell_by_source_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            spell_record = self._get_required_published_spell_record_by_source_id(
                spell_source_id,
                frame_name=resolved_frame_name,
            )
            self._assert_raw_runtime_object_access_allowed(
                "get_spell_by_source_id"
            )
            return self._get_spell_by_record_locked(
                spell_record,
                frame_name=resolved_frame_name,
            )
'''

COMMAND_GET_SPELL_BY_SPELL_ID = '''    def get_spell_by_spell_id(
            self,
            spell_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the Spell that owns a spell_id.

        Purpose:
            Hand out the runtime Spell behind one spell_id - the SHA256 `bind`
            and `bind_inactive` return - through the shared command surface.

        Contract:
            - Answers exactly the spell that owns the spell_id, never another
              version of its SpellIndex; the version an index has active is
              `get_spell_by_index_id`'s answer. The spell_id must be published in
              the room's projection of the frame, and Nexus publishes the version
              an index has active, so a parked version's spell_id is refused
              (ValueError), not answered with the active one. Renamed from
              `get_spell_by_id` in @@SINCE@@, whose owner-Book lookup answered a
              parked spell_id with the spell its index had active.
            - Enforces raw-runtime access, the frame command gate and the
              spell-index ACL of the published record before touching runtime
              state, then reads the owner Spellbook's id maps
              (`Spellbook.find_spell_by_spell_id`) without walking its live index
              map.
            - Uses one top-level command action boundary for gate admission and
              memory emission.

        Args:
            spell_id:
                The spell_id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: The live `Spell` that owns the spell_id.

        Raises:
            ValueError:
                If the spell_id is empty, not published or published under more
                than one index in the selected frame, if command ACL denies frame
                or spell access, if no conduit of the frame claims the spell_id,
                if the owner conduit has no Spellbook, or if that Spellbook no
                longer holds the spell_id.
        """
        self.check_cleaned()
        with self._entered_command_action(
                action_name="get_spell_by_spell_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._assert_raw_runtime_object_access_allowed("get_spell_by_spell_id")
            self._assert_frame_command_enabled(resolved_frame_name)
            spell_index_id = self._get_required_published_spell_index_id_by_spell_id(
                spell_id,
                frame_name=resolved_frame_name,
            )
            self._assert_spell_command_enabled(
                spell_index_id,
                frame_name=resolved_frame_name,
            )
            owner_conduit = self._aether._get_conduit_by_spell_id(
                spell_id,
                resolved_frame_name,
            )
            spellbook = owner_conduit._spellbook
            if spellbook is None:
                raise ValueError(
                    "Owner conduit for spell '{0}' has no spellbook.".format(spell_id)
                )
            # The owner Book's id maps answer the spell_id lookup in O(1) - the spell that owns the
            # spell_id, active or parked - without walking its live index map, which a concurrent
            # bind or removal could resize mid-walk.
            spell = spellbook.find_spell_by_spell_id(spell_id)
            if spell is not None:
                return spell
            raise ValueError(
                "Spell id '{0}' was not found in the owner spellbook.".format(spell_id)
            )
'''

COMMAND_GET_SPELL_BY_RECORD_LOCKED = '''    def _get_spell_by_record_locked(
            self,
            spell_record: SpellRecord,
            *,
            frame_name: str,
    ) -> Spell:
        """
        Resolve the Spell one published record names while the command lock is
        already held.

        Purpose:
            The exact counterpart of `_get_spell_by_index_id_locked`: a record
            names one spell by its spell_id, and this returns that spell - active
            or parked - from the Spellbook of the record's owner conduit, never
            the spell the record's SpellIndex has active.

        Contract:
            - Enforces the frame command gate and the spell-index ACL of the
              record's index before touching runtime state, then resolves the
              owner conduit through `_get_conduit_by_id_locked`, which applies the
              conduit ACL.
            - Reads the owner's Spellbook with `find_spell_by_spell_id`, a
              lock-free read of its two id maps; the Spell returned is borrowed.
            - Requires the caller to hold `self._lock`.

        Args:
            spell_record:
                Published spell record whose spell should be returned.
            frame_name:
                Resolved hosted frame name.

        Returns:
            Spell: The spell the record's spell_id names.

        Raises:
            ValueError:
                If command ACL denies frame, spell or conduit access, if the record
                has no owner conduit, if the owner conduit has no Spellbook, or if
                that Spellbook no longer holds the spell_id.
        """
        source_id = "{0}:{1}".format(
            spell_record.origin_spellbook_id,
            spell_record.spell_id,
        )
        self._assert_frame_command_enabled(frame_name)
        self._assert_spell_command_enabled(
            spell_record.spell_index_id,
            frame_name=frame_name,
        )
        owner_conduit_id = spell_record.owner_conduit_id
        if not owner_conduit_id:
            raise ValueError(
                "Spell '{0}' has no owner conduit in frame '{1}'.".format(
                    source_id,
                    frame_name,
                )
            )
        owner_conduit = self._get_conduit_by_id_locked(
            owner_conduit_id,
            frame_name=frame_name,
        )
        spellbook = owner_conduit._spellbook
        if spellbook is None:
            raise ValueError(
                "Owner conduit for spell '{0}' has no spellbook.".format(
                    spell_record.spell_id
                )
            )
        spell = spellbook.find_spell_by_spell_id(spell_record.spell_id)
        if spell is not None:
            return spell
        raise ValueError(
            "Spell '{0}' was not found in the owner spellbook for frame '{1}'.".format(
                source_id,
                frame_name,
            )
        )

'''

STATIC_INDEX_PATH_AND_HELPER = '''    def _get_spell_by_index_id_locked(
            self,
            spell_index_id: str,
            *,
            frame_name: str,
    ) -> object:
        """
        Resolve one static-room spell runtime object by stable spell-index id while
        the command lock is already held.

        Contract:
            - The index path: answers the live object of a published record of
              the index, whichever version that record names. The lookups by
              spell_id and by source id name one version and do not come through
              here; all three share `_meld_live_spell_from_records_locked`.
            - Requires the caller to hold `self._lock`.

        Args:
            spell_index_id:
                Stable SpellIndex id to resolve.
            frame_name:
                Resolved hosted frame name.

        Returns:
            object: Already-live spell runtime object.

        Raises:
            ValueError:
                If the spell-index id is empty, unpublished, command-disabled, uses
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
        return self._meld_live_spell_from_records_locked(
            matching_spell_records,
            subject="Spell index '{0}'".format(spell_index_id),
            frame_name=frame_name,
        )

    def _meld_live_spell_from_records_locked(
            self,
            spell_records: list[SpellRecord],
            *,
            subject: str,
            frame_name: str,
    ) -> object:
        """
        Return the already-live object of the first of `spell_records` that has
        one, while the command lock is already held.

        Purpose:
            One reuse-only loop for the static room's three lookups: by spell index
            id (every record of the index), by spell_id (the records published for
            that spell_id) and by source id (the one record it names). Each record
            is melded by its own spell_id, so the answer is always a version the
            caller named - or, on the index path, one the index's records name.

        Contract:
            - Skips records whose existence keeps no single stored object (`many`,
              `unique_per_spell_space`, `managed_spell_quantity`) and records with
              no owner conduit; melds every other record through its owner root
              with `meld_existing_spell(spell=<the record's spell_id>)`, which
              builds nothing, and skips a record its owner refuses (ValueError: no
              live object).
            - Requires the caller to hold `self._lock`; the frame and spell ACL
              checks are the caller's.

        Args:
            spell_records:
                Published records to try, in order.
            subject:
                What the caller asked for, as the refusals name it (for example
                "Spell index '<id>'" or "Spell id '<id>'").
            frame_name:
                Resolved hosted frame name.

        Returns:
            object: Already-live runtime object of the first record that has one.

        Raises:
            ValueError:
                "<subject> uses unsupported static existence '<name>'." when no
                record had a live object and one of them uses an unsupported
                existence; otherwise "<subject> is not live in frame '<frame>'.".
        """
        for spell_record in spell_records:
            # No single stored object to hand out: `many` builds anew, a spellspace object is request-local, and a
            # managed spell's objects are leased from a pool (2026-10-15).
            if spell_record.existence in {
                    Existence.many,
                    Existence.unique_per_spell_space,
                    Existence.managed_spell_quantity,
            }:
                continue
            owner_conduit_id = spell_record.owner_conduit_id
            if not owner_conduit_id:
                continue
            # Spell owners are roots.
            owner_conduit = self._aether.get_root_conduit_by_id(
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
                for spell_record in spell_records
                if spell_record.existence in {
                    Existence.many,
                    Existence.unique_per_spell_space,
                    Existence.managed_spell_quantity,
                }
            ),
            None,
        )
        if unsupported_spell_record is not None:
            raise ValueError(
                "{0} uses unsupported static existence '{1}'.".format(
                    subject,
                    unsupported_spell_record.existence.name,
                )
            )
        raise ValueError(
            "{0} is not live in frame '{1}'.".format(
                subject,
                frame_name,
            )
        )
'''

STATIC_GET_SPELL_BY_SOURCE_ID = '''    def get_spell_by_source_id(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the already-live object of the spell a published source id names.

        Contract:
            - Melds only the spell the source id names, by its spell_id, through
              its owner root (`meld_existing_spell`, reuse-only); never the live
              object of another version of its index. Until @@SINCE@@ this
              resolved the record's index and returned the live object of any
              published record of it.
            - Enforces the frame command gate and the record's spell-index ACL
              before touching runtime state.

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
                If the spell source id is empty, malformed, not published or
                ambiguous in the selected frame, if command ACL denies frame or
                spell access, if its existence keeps no single stored object, or
                if it is not currently live.
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
            self._assert_frame_command_enabled(resolved_frame_name)
            self._assert_spell_command_enabled(
                spell_record.spell_index_id,
                frame_name=resolved_frame_name,
            )
            return self._meld_live_spell_from_records_locked(
                [spell_record],
                subject="Spell '{0}'".format(spell_source_id),
                frame_name=resolved_frame_name,
            )
'''

STATIC_GET_SPELL_BY_SPELL_ID = '''    def get_spell_by_spell_id(
            self,
            spell_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the already-live object of the spell that owns a spell_id.

        Contract:
            - Melds only the records published for that spell_id (one per
              Spellbook that publishes it), each by the spell_id, through its
              owner root (`meld_existing_spell`, reuse-only); never the live object
              of another version of its index. Renamed from `get_spell_by_id` in
              @@SINCE@@, which resolved the spell_id's index and returned the live
              object of any published record of it.
            - Enforces the frame command gate and the spell-index ACL before
              touching runtime state.

        Args:
            spell_id:
                The spell_id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Already-live spell runtime object.

        Raises:
            ValueError:
                If the spell_id is empty, not published or published under more
                than one index in the selected frame, if command ACL denies frame
                or spell access, if its existence keeps no single stored object, or
                if it is not currently live.
        """
        with self._entered_command_action(
                action_name="get_spell_by_spell_id",
                frame_name=frame_name,
        ), self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            spell_index_id = self._get_required_published_spell_index_id_by_spell_id(
                spell_id,
                frame_name=resolved_frame_name,
            )
            self._assert_frame_command_enabled(resolved_frame_name)
            self._assert_spell_command_enabled(
                spell_index_id,
                frame_name=resolved_frame_name,
            )
            descriptor = self._rift._get_required_command_projection(
                resolved_frame_name
            ).frame_descriptor
            matching_spell_records = [
                spell_record
                for spell_record in descriptor.spell_records_by_key.values()
                if spell_record.spell_id == spell_id
            ]
            return self._meld_live_spell_from_records_locked(
                matching_spell_records,
                subject="Spell id '{0}'".format(spell_id),
                frame_name=resolved_frame_name,
            )
'''


def register(engine: EditEngine) -> None:
    # Typing-only imports for the new record helper's annotations.
    engine.anchor(
        COMMAND,
        "    from melder.aether.conduit.conduit import Conduit\n",
        "    from melder.aether.conduit.conduit import Conduit\n"
        "    from melder.aether.spellbook.spell import Spell\n",
    )
    engine.anchor(
        COMMAND,
        "    from melder.nexus.rift.rift import Rift\n",
        "    from melder.nexus.frame_descriptor.spell_record import SpellRecord\n"
        "    from melder.nexus.rift.rift import Rift\n",
    )
    engine.block(
        COMMAND,
        "CommandSystem.get_spell_by_source_id",
        "c8e9734550f5bf1fadc7cdd1a729c59f37bac486e4f35e3cf7cfe7b70c1b9e51",
        COMMAND_GET_SPELL_BY_SOURCE_ID,
    )
    engine.block(
        COMMAND,
        "CommandSystem.get_spell_by_id",
        "17fd3fb9de103834aa86cfc4a05624c18a6a3500cac3fb8487b89d9e2b3bb718",
        COMMAND_GET_SPELL_BY_SPELL_ID,
    )
    # The exact record helper sits after the index path it mirrors.
    engine.anchor(
        COMMAND,
        "    def _get_target_method_locked(\n",
        COMMAND_GET_SPELL_BY_RECORD_LOCKED + "    def _get_target_method_locked(\n",
    )
    # The advertised base command list.
    engine.anchor(
        COMMAND,
        '            "get_spell_by_id",\n',
        '            "get_spell_by_spell_id",\n',
    )
    engine.block(
        STATIC,
        "StaticCommandSystem._get_spell_by_index_id_locked",
        "423d609717c6296c6a15eba668296bcc2e31777f7c1ef5f32d5d43f6cb30589c",
        STATIC_INDEX_PATH_AND_HELPER,
    )
    engine.block(
        STATIC,
        "StaticCommandSystem.get_spell_by_source_id",
        "cf1de46f3a4e4d3aba90ad926be80c188a25310fe9603cc53f918ea013f4152d",
        STATIC_GET_SPELL_BY_SOURCE_ID,
    )
    engine.block(
        STATIC,
        "StaticCommandSystem.get_spell_by_id",
        "9f13a038ca8aec2c369f6f3ecbfa680c418abacfeb721885ef3d6f25abc17c92",
        STATIC_GET_SPELL_BY_SPELL_ID,
    )
