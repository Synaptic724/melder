"""Part B source (0.2.8214), restore side: stage 1 refusal and stage 6 per-Book custody replay."""
import sys

from apply_support import ApplySession

session = ApplySession(sys.argv[1])
ENGINE = "src/melder/crystallizer/crystal_loader_system/restore_engine.py"

session.insert_after(ENGINE, r'''from melder.crystallizer.crystal_analysis.conduit_hierarchy import ConduitHierarchy
''', r'''from melder.crystallizer.crystals.spell_crystal import SpellCrystal
''')
session.replace(ENGINE, r'''        "_custody_inactive",
        "_live_books",
''', r'''        "_custody_inactive",
        "_spell_translation",
        "_live_books",
''')
session.insert_after(ENGINE, r'''        self._custody_active: Dict[str, Dict[str, object]] = {}
        self._custody_inactive: Dict[str, Dict[str, object]] = {}
''', r'''        # Recorded-to-live spell ids per Book: (recorded spellbook id,
        # recorded spell id) -> live id, written by the binds (0.2.8214). One
        # spell id rebuilt in two Books (per-frame ids) may bind to two new
        # ids, so selections, parked members and contract grants translate
        # through their own Book. Writes are per-key disjoint across the
        # parallel driver's Book units (same law as the live-handle maps).
        self._spell_translation: Dict[Tuple[str, str], str] = {}
''')
session.insert_after(ENGINE, r'''        del self._custody_inactive
''', r'''        del self._spell_translation
''')
session.insert_before(ENGINE, r'''            - A payload without the regime (an older record) rebuilds the
              default regime and reports the key missing.
''', r'''            - Refusal (0.2.8214): when the live regime is fixed process-wide
              and the record, kept under per-frame ids, binds one spell id in
              two frames, the stage raises before anything is built (the
              second frame's bind could only collide).
''')
session.replace(ENGINE, r'''            if recorded_regime is not None and bool(recorded_regime) != live_regime:
                self._report_recorded_regime_not_in_force(
''', r'''            if recorded_regime is not None and bool(recorded_regime) != live_regime:
                if live_regime and self._record_binds_one_spell_in_two_frames():
                    raise RuntimeError(
                        "This record binds one spell id in two frames, which only per-frame spell ids "
                        "allow, and the live world already runs process-wide ids (a configured Aether or "
                        "a live frame fixed them). Restore it where the Aether is not configured and holds "
                        "no frame, or configure process_wide_unique_spell_ids=False before the first frame "
                        "is born. Nothing was built."
                    )
                self._report_recorded_regime_not_in_force(
''')
session.insert_before(ENGINE, r'''    def _replay_crystallizer_policy(self) -> None:
''', r'''    def _record_binds_one_spell_in_two_frames(self) -> bool:
        """
        Internal

        Say whether the folded custody binds one spell id in more than one frame.

        Contract:
            - Reads the folded custody only (both locations).
            - An entry's frame is its payload "frame_name", else its Book's
              recorded frame, else "default"; its spell id is the payload "id",
              else the key's spell id.
            - Only a record kept under per-frame ids can answer True: a
              process-wide record holds each spell id once.

        Returns:
            bool: True when some spell id has custody in two or more frames.
        """
        frames_by_spell: Dict[str, Set[str]] = {}
        for store in (self._custody_active, self._custody_inactive):
            for custody_key, payload in store.items():
                frames_by_spell.setdefault(
                    self._recorded_spell_id(custody_key, payload), set()
                ).add(self._custody_frame(payload))
        return any(len(frames) > 1 for frames in frames_by_spell.values())

    def _custody_frame(self, payload: Dict[str, object]) -> str:
        """
        Internal

        Return the frame one folded custody entry belongs to.

        Args:
            payload:
                The folded custody payload.

        Returns:
            str: The payload "frame_name", else its Book's recorded frame, else
            "default" (payloads before 0.2.8214 carry no frame).
        """
        frame_name = payload.get("frame_name")
        if frame_name is None:
            book = self._books.get(str(payload.get("spellbook_id")), {})
            frame_name = book.get("frame_name", "default")
        return str(frame_name)

    @staticmethod
    def _recorded_spell_id(custody_key: str, payload: Dict[str, object]) -> str:
        """
        Internal

        Return the recorded spell id of one folded custody entry.

        Contract:
            The payload's "id" answers; a payload without it (a hand-made
            window) falls back to the key's spell id, which is the key itself
            under process-wide ids (0.2.8214).

        Args:
            custody_key:
                The entry's record key.
            payload:
                The folded custody payload.

        Returns:
            str: The recorded spell id.
        """
        return str(payload.get("id", SpellCrystal.spell_id_of_custody_key(custody_key)))

''')
session.replace(ENGINE, r'''        bind_order = self._book_bind_order(spellbook_id)
        for spell_id in bind_order:
            if spell_id in self._custody_active:
                self._bind_one_active(
                    spellbook, spell_id,
                    self._custody_active[spell_id],
                )
        conduit = self._conjure_for_book(spellbook_id, spellbook)
        for spell_id in bind_order:
            if spell_id in self._custody_inactive:
                self._bind_one_staged(
                    spellbook, conduit, spell_id,
                    self._custody_inactive[spell_id],
                )
''', r'''        bind_order = self._book_bind_order(spellbook_id)
        for custody_key in bind_order:
            if custody_key in self._custody_active:
                self._bind_one_active(
                    spellbook_id, spellbook, custody_key,
                    self._custody_active[custody_key],
                )
        conduit = self._conjure_for_book(spellbook_id, spellbook)
        for custody_key in bind_order:
            if custody_key in self._custody_inactive:
                self._bind_one_staged(
                    spellbook_id, spellbook, conduit, custody_key,
                    self._custody_inactive[custody_key],
                )
''')
session.replace(ENGINE, r'''    def _book_bind_order(self, spellbook_id: str) -> List[str]:
        """
        Return one book's recorded bind order, custody-filtered.

        Args:
            spellbook_id:
                Recorded book identity.

        Returns:
            List[str]:
                Spell SHAs in recorded bind order that still hold folded
                custody under this book; custody without a bind_order slot
                appends afterwards (deterministic, sorted).
        """
        payload = self._books.get(spellbook_id, {})
        ordered = [str(entry) for entry in list(payload.get("bind_order", []))]
        owned = {
            spell_id
            for store in (self._custody_active, self._custody_inactive)
            for spell_id, crystal in store.items()
            if crystal.get("spellbook_id") == spellbook_id
        }
        sequence = [spell_id for spell_id in ordered if spell_id in owned]
        sequence.extend(sorted(owned.difference(sequence)))
        return sequence
''', r'''    def _book_bind_order(self, spellbook_id: str) -> List[str]:
        """
        Return one book's recorded bind order as its custody keys.

        Contract:
            The Book's bind_order names spell ids; each maps to this Book's own
            custody key (0.2.8214: under per-frame ids the key is
            "<spell_id>@<frame>", and another Book may hold the same spell id).

        Args:
            spellbook_id:
                Recorded book identity.

        Returns:
            List[str]:
                Custody keys in recorded bind order that still hold folded
                custody under this book; custody without a bind_order slot
                appends afterwards (deterministic, sorted).
        """
        payload = self._books.get(spellbook_id, {})
        ordered = [str(entry) for entry in list(payload.get("bind_order", []))]
        keys_by_spell: Dict[str, List[str]] = {}
        for store in (self._custody_active, self._custody_inactive):
            for custody_key, crystal in store.items():
                if crystal.get("spellbook_id") == spellbook_id:
                    keys_by_spell.setdefault(
                        self._recorded_spell_id(custody_key, crystal), []
                    ).append(custody_key)
        sequence: List[str] = []
        for spell_id in ordered:
            for custody_key in sorted(keys_by_spell.get(spell_id, [])):
                if custody_key not in sequence:
                    sequence.append(custody_key)
        owned = {
            custody_key
            for custody_keys in keys_by_spell.values()
            for custody_key in custody_keys
        }
        sequence.extend(sorted(owned.difference(sequence)))
        return sequence
''')
session.replace(ENGINE, r'''    def _bind_one_active(
            self,
            spellbook: Any,
            spell_id: str,
            crystal: Dict[str, object],
    ) -> None:
''', r'''    def _bind_one_active(
            self,
            spellbook_id: str,
            spellbook: Any,
            custody_key: str,
            crystal: Dict[str, object],
    ) -> None:
''')
session.replace(ENGINE, r'''            Preserve recorded capability; only legacy absence defaults to True.

        Args:
            spellbook:
                The live rebuilt Spellbook.
            spell_id:
                Recorded spell SHA; receiving policy determines the new bind ID.
            crystal:
                The folded custody payload.

        Returns:
            None.
        """
        target = self._hydrate_target(spell_id, crystal)
        if target is None:
            return
''', r'''            Preserve recorded capability; only legacy absence defaults to True.
            The spell id comes from the payload, the custody key names
            shortfalls, and identities map per Book (0.2.8214).

        Args:
            spellbook_id:
                Recorded Book identity (translation and index owner edge).
            spellbook:
                The live rebuilt Spellbook.
            custody_key:
                The folded custody key (the spell id, or "<spell_id>@<frame>");
                receiving policy determines the new bind ID.
            crystal:
                The folded custody payload.

        Returns:
            None.
        """
        spell_id = self._recorded_spell_id(custody_key, crystal)
        target = self._hydrate_target(custody_key, crystal)
        if target is None:
            return
''')
session.replace(ENGINE, r'''        self._report.record_built("spell_active")
        if new_spell_id != spell_id:
            self._report.map_identity(spell_id, new_spell_id)
        live_spell = spellbook.find_spell_by_id(new_spell_id)
        recorded_index_id = self._index_id_for_member(spell_id)
''', r'''        self._report.record_built("spell_active")
        self._map_spell_identity(spellbook_id, spell_id, new_spell_id)
        live_spell = spellbook.find_spell_by_id(new_spell_id)
        recorded_index_id = self._index_id_for_member(spellbook_id, spell_id)
''')
session.replace(ENGINE, r'''    def _bind_one_staged(
            self,
            spellbook: Any,
            conduit: Optional[Any],
            spell_id: str,
            crystal: Dict[str, object],
    ) -> None:
''', r'''    def _bind_one_staged(
            self,
            spellbook_id: str,
            spellbook: Any,
            conduit: Optional[Any],
            custody_key: str,
            crystal: Dict[str, object],
    ) -> None:
''')
session.replace(ENGINE, r'''            Preserve the parked version's own resolution capability.

        Args:
            spellbook:
                The live rebuilt Spellbook.
            conduit:
                The live conduit hosting `bind_inactive`.
            spell_id:
                Recorded spell SHA; receiving policy determines the new bind ID.
            crystal:
                The folded custody payload.

        Returns:
            None.
        """
        if conduit is None:
            self._report.add_shortfall(
                "spell_crystal", spell_id,
                "staged_member_requires_conduit_none_recorded",
            )
            return
        recorded_index_id = self._index_id_for_member(spell_id)
        anchor = self._live_index_for(spellbook, recorded_index_id)
        if anchor is None:
            self._report.add_shortfall(
                "spell_crystal", spell_id,
                "staged_member_anchor_index_not_rebuilt: {0}".format(
                    recorded_index_id
                ),
            )
            return
        target = self._hydrate_target(spell_id, crystal)
''', r'''            Preserve the parked version's own resolution capability.
            The anchor index is found within this Book, the custody key names
            shortfalls, and identities map per Book (0.2.8214).

        Args:
            spellbook_id:
                Recorded Book identity (translation and index owner edge).
            spellbook:
                The live rebuilt Spellbook.
            conduit:
                The live conduit hosting `bind_inactive`.
            custody_key:
                The folded custody key (the spell id, or "<spell_id>@<frame>");
                receiving policy determines the new bind ID.
            crystal:
                The folded custody payload.

        Returns:
            None.
        """
        spell_id = self._recorded_spell_id(custody_key, crystal)
        if conduit is None:
            self._report.add_shortfall(
                "spell_crystal", custody_key,
                "staged_member_requires_conduit_none_recorded",
            )
            return
        recorded_index_id = self._index_id_for_member(spellbook_id, spell_id)
        anchor = self._live_index_for(spellbook, recorded_index_id)
        if anchor is None:
            self._report.add_shortfall(
                "spell_crystal", custody_key,
                "staged_member_anchor_index_not_rebuilt: {0}".format(
                    recorded_index_id
                ),
            )
            return
        target = self._hydrate_target(custody_key, crystal)
''')
session.replace(ENGINE, r'''        if new_spell_id != spell_id:
            self._report.map_identity(spell_id, new_spell_id)
        self._report.record_built("spell_staged")
''', r'''        self._map_spell_identity(spellbook_id, spell_id, new_spell_id)
        self._report.record_built("spell_staged")
''')
session.replace(ENGINE, r'''            Translate changed bind identities and resolve the exact owned member,
            including parked members, rather than the index's active projection.
''', r'''            Translate changed bind identities and resolve the exact owned member,
            including parked members, rather than the index's active projection.
            Translation is this Book's own (0.2.8214).
''')
session.replace(ENGINE, r'''            live_selected_id = self._report.translate(str(selected)) or str(selected)
''', r'''            live_selected_id = self._translate_spell(spellbook_id, str(selected))
''')
session.replace(ENGINE, r'''    def _index_id_for_member(self, spell_id: str) -> Optional[str]:
        """
        Find the recorded index holding one member SHA.

        Args:
            spell_id:
                Member spell SHA.

        Returns:
            Optional[str]:
                The recorded index ULID, or None when unrecorded.
        """
        for index_id, payload in self._indexes.items():
            if spell_id in list(payload.get("member_spell_ids", [])):
''', r'''    def _map_spell_identity(
            self,
            spellbook_id: str,
            spell_id: str,
            new_spell_id: str,
    ) -> None:
        """
        Internal

        Record one Book's recorded-to-live spell identity.

        Contract:
            - A changed id goes to the report's identity map (as before) and to
              the per-Book translation; an unchanged id needs neither.
            - Per Book (0.2.8214): one spell id rebuilt in two Books may bind
              to two new ids, and each Book's references must follow its own.

        Args:
            spellbook_id:
                Recorded Book the bind replayed for.
            spell_id:
                Recorded spell id.
            new_spell_id:
                Id the live bind returned.

        Returns:
            None.
        """
        if new_spell_id == spell_id:
            return
        self._report.map_identity(spell_id, new_spell_id)
        self._spell_translation[(spellbook_id, spell_id)] = new_spell_id

    def _translate_spell(self, spellbook_id: str, spell_id: str) -> str:
        """
        Internal

        Return the live id of one recorded spell id within one Book.

        Args:
            spellbook_id:
                Recorded Book whose rebuilt world is meant.
            spell_id:
                Recorded spell id.

        Returns:
            str: The live id; the recorded id when the bind kept it.
        """
        return self._spell_translation.get((spellbook_id, spell_id), spell_id)

    def _index_id_for_member(self, spellbook_id: str, spell_id: str) -> Optional[str]:
        """
        Find the recorded index of one Book that holds one member SHA.

        Contract:
            Searches only the indexes the Book owns (0.2.8214: under per-frame
            ids another Book may hold an index with the same member id).

        Args:
            spellbook_id:
                Recorded Book identity (index owner edge).
            spell_id:
                Member spell SHA.

        Returns:
            Optional[str]:
                The recorded index ULID, or None when unrecorded.
        """
        for index_id, payload in self._indexes.items():
            if payload.get("spellbook_id") != spellbook_id:
                continue
            if spell_id in list(payload.get("member_spell_ids", [])):
''')
session.replace(ENGINE, r'''            Member lookup follows changed Spell IDs in the existing report map.
''', r'''            Member lookup follows changed Spell IDs within the index's own Book
            (0.2.8214).
''')
session.replace(ENGINE, r'''        recorded = self._indexes.get(recorded_index_id, {})
        selected = recorded.get("selected_spell_id")
        candidates = list(recorded.get("member_spell_ids", []))
        if selected is not None:
            candidates.insert(0, selected)
        for member_id in candidates:
            live_member_id = self._report.translate(str(member_id)) or str(member_id)
''', r'''        recorded = self._indexes.get(recorded_index_id, {})
        book_id = str(recorded.get("spellbook_id"))
        selected = recorded.get("selected_spell_id")
        candidates = list(recorded.get("member_spell_ids", []))
        if selected is not None:
            candidates.insert(0, selected)
        for member_id in candidates:
            live_member_id = self._translate_spell(book_id, str(member_id))
''')
session.replace(ENGINE, r'''        for granter, details_key in (
                (side_a, "details_a"),
                (side_b, "details_b"),
        ):
            for detail in list(payload.get(details_key, [])):
''', r'''        for granter, granter_key, details_key in (
                (side_a, "conduit_a_id", "details_a"),
                (side_b, "conduit_b_id", "details_b"),
        ):
            # Detail spell ids translate within the granting side's Book
            # (0.2.8214: one spell id may be rebuilt in several Books).
            granter_book_id = str(
                self._conduits.get(str(payload.get(granter_key)), {}).get("spellbook_id")
            )
            for detail in list(payload.get(details_key, [])):
''')
session.replace(ENGINE, r'''                live_spell_id = self._report.translate(recorded_spell_id) or recorded_spell_id
''', r'''                live_spell_id = self._translate_spell(granter_book_id, recorded_spell_id)
''')
session.replace(ENGINE, r'''    def _hydrate_target(
            self,
            spell_id: str,
            crystal: Dict[str, object],
    ) -> Optional[Any]:
''', r'''    def _hydrate_target(
            self,
            custody_key: str,
            crystal: Dict[str, object],
    ) -> Optional[Any]:
''')
session.replace(ENGINE, r'''        Args:
            spell_id:
                Recorded spell SHA (shortfall key).
            crystal:
                The folded custody payload.

        Returns:
            Optional[Any]:
                The live class/function target, or None (shortfall filed).
        """
        if str(crystal.get("rebindability")) != "hydratable":
            self._report.add_shortfall(
                "spell_crystal", spell_id,
''', r'''        Args:
            custody_key:
                The folded custody key (shortfall key); its spell id anchors
                the module-world rebuild lanes (0.2.8214).
            crystal:
                The folded custody payload.

        Returns:
            Optional[Any]:
                The live class/function target, or None (shortfall filed).
        """
        spell_id = self._recorded_spell_id(custody_key, crystal)
        if str(crystal.get("rebindability")) != "hydratable":
            self._report.add_shortfall(
                "spell_crystal", custody_key,
''')
session.replace(ENGINE, r'''                "spell_crystal", spell_id,
                "hydration_failed ({0}.{1}): {2}".format(
''', r'''                "spell_crystal", custody_key,
                "hydration_failed ({0}.{1}): {2}".format(
''')
session.replace(ENGINE, r'''            - Detail Spell IDs follow recorded-to-live translation when a bind
              changed its signature; unchanged SHAs remain direct. Conduit
              endpoints translate through the same existing identity map.
''', r'''            - Detail Spell IDs follow recorded-to-live translation when a bind
              changed its signature, within the granting conduit's Book
              (0.2.8214); unchanged SHAs remain direct. Conduit endpoints
              translate through the existing identity map.
''')

long_lines = session.long_added_lines()
if long_lines:
    raise AssertionError("lines over 120:\n" + "\n".join(long_lines))
for path in session.write():
    print(path)
