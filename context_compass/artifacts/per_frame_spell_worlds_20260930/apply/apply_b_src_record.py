"""Part B source (0.2.8214), record side: the custody key on SpellCrystal, the record, the facade, callers."""
import sys

from apply_support import ApplySession

session = ApplySession(sys.argv[1])

# ----------------------------------------------------------------------------------------------------------------
# SpellCrystal: frame and custody key.
# ----------------------------------------------------------------------------------------------------------------
CRYSTAL = "src/melder/crystallizer/crystals/spell_crystal.py"
session.insert_after(CRYSTAL, r'''        - anchored to the spell's concrete SHA256 identity
''', r'''        - records the spell's frame and its record key (`custody_key`): the
          spell id under process-wide ids, "<spell_id>@<frame>" under
          per-frame ids, where one spell id may be bound in several frames
          (0.2.8214)
''')
session.insert_after(CRYSTAL, r'''        "_spellbook_id",
''', r'''        "_frame_name",
        "_custody_key",
''')
session.replace(CRYSTAL, r'''            site_package_dependency_descent: bool = True,
    ) -> None:
''', r'''            site_package_dependency_descent: bool = True,
            per_frame_custody: bool = False,
    ) -> None:
''')
session.insert_after(CRYSTAL, r'''            - Captures native resolution capability so replay cannot enable a definition.
''', r'''            - Captures the spell's frame (`spell.aetheric_frame`) and keys the
              record by the spell id, or by "<spell_id>@<frame>" when
              `per_frame_custody` is set (0.2.8214).
''')
session.replace(CRYSTAL, r'''                crystallizer facade passes the configuration truth
                (schema default False).

        Returns:
            None.
''', r'''                crystallizer facade passes the configuration truth
                (schema default False).
            per_frame_custody:
                True keys the record entry "<spell_id>@<frame>" (the
                crystallizer facade passes True under per-frame spell ids,
                where one spell id may be bound in several frames); False
                (default) keys it by the spell id alone, as process-wide
                worlds always have been.

        Returns:
            None.
''')
session.insert_after(CRYSTAL, r'''        self._spellbook_id: Optional[str] = spellbook_id
''', r'''        # Record key (0.2.8214): under per-frame spell ids one spell id may
        # be bound in several frames, so custody is keyed per frame; under
        # process-wide ids the spell id is unique and stays the key.
        self._frame_name: str = spell.aetheric_frame
        self._custody_key: str = (
            SpellCrystal.compose_custody_key(self._id, self._frame_name)
            if per_frame_custody
            else self._id
        )
''')
session.insert_after(CRYSTAL, r'''            del self._spellbook_id
''', r'''            del self._frame_name
            del self._custody_key
''')
session.insert_before(CRYSTAL, r'''    @property
    def root_module_name(self) -> str:
''', r'''    @property
    def frame_name(self) -> str:
        """
        Return the name of the frame the spell was bound in.

        Purpose:
            Say which frame's world this custody describes. Under per-frame
            spell ids the same spell id can be bound in several frames, and
            each frame's copy is recorded separately.

        Returns:
            str:
                The owning frame's name (`Spell.aetheric_frame` at capture).
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_name

    @property
    def custody_key(self) -> str:
        """
        Return the key this crystal is recorded under.

        Purpose:
            Address one frame's copy of a spell in the record. Under
            process-wide spell ids a spell id exists once per process, so the
            key is the spell id itself and records of such worlds keep their
            shape; under per-frame ids it is "<spell_id>@<frame_name>", so two
            frames binding the same class keep one crystal each (0.2.8214).

        Returns:
            str:
                The spell id, or "<spell_id>@<frame_name>" when built with
                `per_frame_custody`.
        """
        self.check_cleaned()
        with self._lock:
            return self._custody_key

    @staticmethod
    def compose_custody_key(spell_id: str, frame_name: str) -> str:
        """
        Return the per-frame record key for one spell id bound in one frame.

        Contract:
            The key is "<spell_id>@<frame_name>". A spell id is a SHA256 hex
            digest and never holds "@", so `spell_id_of_custody_key` recovers
            it by splitting at the first "@" even when the frame name holds one.

        Args:
            spell_id:
                The spell's SHA256 identity.
            frame_name:
                The frame the spell was bound in.

        Returns:
            str: The frame-scoped custody key.
        """
        return f"{spell_id}@{frame_name}"

    @staticmethod
    def spell_id_of_custody_key(custody_key: str) -> str:
        """
        Return the spell id one custody key names.

        Contract:
            Splits at the first "@"; a key without one (a process-wide key) is
            the spell id itself. Readers holding the crystal or its payload read
            the spell id there ("id"); this parse serves the tombstones whose
            crystal is already gone.

        Args:
            custody_key:
                A record key: a spell id, or "<spell_id>@<frame_name>".

        Returns:
            str: The spell id.
        """
        return custody_key.split("@", 1)[0]

''')
session.replace(CRYSTAL, r'''            Combines crystal-owned identity/bind-policy fields with a detached
''', r'''            Combines crystal-owned identity (spell id, frame, custody key) and
            bind-policy fields with a detached
''')
session.replace(CRYSTAL, r'''                "id": self._id,
                "root_module_name": self._root_module_name,
''', r'''                "id": self._id,
                "frame_name": self._frame_name,
                "custody_key": self._custody_key,
                "root_module_name": self._root_module_name,
''')

# ----------------------------------------------------------------------------------------------------------------
# PersistenceProfile: custody keyed by custody key.
# ----------------------------------------------------------------------------------------------------------------
PROFILE = "src/melder/crystallizer/persistence/persistence_profile.py"
session.insert_after(PROFILE, r'''        - The L3 spell node IS the SpellCrystal: it carries both the bind
          signatures (binding_name / spellframe / existence / permissions /
          rebindability) and the module-world custody in one object.
''', r'''        - Spell custody is keyed by `SpellCrystal.custody_key`: the spell id
          under process-wide ids, "<spell_id>@<frame>" under per-frame ids,
          so one spell id bound in several frames keeps one crystal per frame
          (0.2.8214).
''')
session.replace(PROFILE, r'''        self._spell_crystals_by_spell_id: Dict[str, SpellCrystal] = {}
        self._inactive_spell_crystals_by_spell_id: Dict[str, SpellCrystal] = {}
''', r'''        # Custody maps, keyed by SpellCrystal.custody_key: the spell id under
        # process-wide ids, "<spell_id>@<frame>" under per-frame ids (0.2.8214;
        # the map names predate the frame-scoped key).
        self._spell_crystals_by_spell_id: Dict[str, SpellCrystal] = {}
        self._inactive_spell_crystals_by_spell_id: Dict[str, SpellCrystal] = {}
''')
session.replace(PROFILE, r'''        Contract:
            - Replace-on-emit across BOTH locations: any prior crystal for
              the spell_id is cleaned wherever it lived.
''', r'''        Contract:
            - Replace-on-emit across BOTH locations: any prior crystal under
              the same custody key is cleaned wherever it lived; one frame's
              copy never displaces another frame's (0.2.8214).
''')
session.replace(PROFILE, r'''    def record_spell_activity(self, spell_id: str, active: bool) -> None:
''', r'''    def record_spell_activity(self, custody_key: str, active: bool) -> None:
''')
session.replace(PROFILE, r'''        Contract:
            - Tolerates missing custody (activity for a spell the record
              never held): the activity is journaled either way so
              checkpoints capture the transition truthfully.

        Args:
            spell_id:
                The spell whose activity flipped.
''', r'''        Contract:
            - Addresses one custody key, so under per-frame ids only the named
              frame's copy moves (0.2.8214).
            - Tolerates missing custody (activity for a spell the record
              never held): the activity is journaled either way so
              checkpoints capture the transition truthfully.

        Args:
            custody_key:
                The flipped crystal's record key (`SpellCrystal.custody_key`).
''')
session.replace(PROFILE, r'''            if active:
                crystal = self._inactive_spell_crystals_by_spell_id.pop(spell_id, None)
                if crystal is not None:
                    self._spell_crystals_by_spell_id[spell_id] = crystal
            else:
                crystal = self._spell_crystals_by_spell_id.pop(spell_id, None)
                if crystal is not None:
                    self._inactive_spell_crystals_by_spell_id[spell_id] = crystal
            self._journal("spell_activity", spell_id)
''', r'''            if active:
                crystal = self._inactive_spell_crystals_by_spell_id.pop(custody_key, None)
                if crystal is not None:
                    self._spell_crystals_by_spell_id[custody_key] = crystal
            else:
                crystal = self._spell_crystals_by_spell_id.pop(custody_key, None)
                if crystal is not None:
                    self._inactive_spell_crystals_by_spell_id[custody_key] = crystal
            self._journal("spell_activity", custody_key)
''')
session.replace(PROFILE, r'''    def remove_spell_crystal(self, spell_id: str) -> None:
''', r'''    def remove_spell_crystal(self, custody_key: str) -> None:
''')
session.replace(PROFILE, r'''        Contract:
            - Tolerates missing custody; journals "spell_removed" either way.

        Args:
            spell_id:
                The removed spell's SHA256 identity.
''', r'''        Contract:
            - Addresses one custody key, so under per-frame ids only the named
              frame's copy leaves (0.2.8214).
            - Tolerates missing custody; journals "spell_removed" either way.

        Args:
            custody_key:
                The removed crystal's record key (`SpellCrystal.custody_key`).
''')
session.replace(PROFILE, r'''                crystal = location.pop(spell_id, None)
                if crystal is not None and not crystal.cleaned:
                    crystal.cleanup()
            self._journal("spell_removed", spell_id)
''', r'''                crystal = location.pop(custody_key, None)
                if crystal is not None and not crystal.cleaned:
                    crystal.cleanup()
            self._journal("spell_removed", custody_key)
''')
session.replace(PROFILE, r'''        Contract:
            - Caller holds `self._lock`.
            - Displaces + cleans any prior crystal from both locations.
''', r'''        Contract:
            - Caller holds `self._lock`.
            - Displaces + cleans any prior crystal under the same custody key
              from both locations, and journals that key.
''')
session.replace(PROFILE, r'''            previous = location.pop(crystal.id, None)
            if previous is not None and not previous.cleaned:
                previous.cleanup()
        target = (
            self._spell_crystals_by_spell_id
            if active
            else self._inactive_spell_crystals_by_spell_id
        )
        target[crystal.id] = crystal
        self._journal("spell_crystal", crystal.id)
''', r'''            previous = location.pop(crystal.custody_key, None)
            if previous is not None and not previous.cleaned:
                previous.cleanup()
        target = (
            self._spell_crystals_by_spell_id
            if active
            else self._inactive_spell_crystals_by_spell_id
        )
        target[crystal.custody_key] = crystal
        self._journal("spell_crystal", crystal.custody_key)
''')
session.replace(PROFILE, r'''    def get_spell_crystal(self, spell_id: str) -> SpellCrystal:
''', r'''    def get_spell_crystal(
            self,
            spell_id: str,
            frame_name: Optional[str] = None,
    ) -> SpellCrystal:
''')
session.replace(PROFILE, r'''            must not retain long-lived references).

        Args:
            spell_id:
                The spell's SHA256 identity.

        Returns:
            SpellCrystal:
                The currently recorded crystal for the spell.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
            KeyError:
                If no crystal is recorded under `spell_id`; the message
                reports the recorded count so callers can self-correct.
        """
        self.check_cleaned()
        with self._lock:
            crystal = self._spell_crystals_by_spell_id.get(spell_id)
            if crystal is None:
                crystal = self._inactive_spell_crystals_by_spell_id.get(spell_id)
            if crystal is None:
                raise KeyError(
                    "No spell crystal recorded for spell_id {0!r} in "
                    "profile {1!r} ({2} crystals recorded).".format(
                        spell_id,
                        self._profile_name,
                        len(self._spell_crystals_by_spell_id),
                    )
                )
            return crystal
''', r'''            must not retain long-lived references).

        Contract (0.2.8214: custody is keyed per frame under per-frame ids):
            - With `frame_name`, that frame's key ("<spell_id>@<frame_name>")
              answers first.
            - Then the exact key: a bare spell id (a process-wide record,
              where the frame is not part of the key) or a full custody key.
            - Without `frame_name`, a spell id recorded only under
              frame-scoped keys answers with its lowest key, active copies
              before inactive ones; with `frame_name`, another frame's copy
              never answers.

        Args:
            spell_id:
                The spell's SHA256 identity, or a full custody key.
            frame_name:
                Optional frame whose copy is wanted.

        Returns:
            SpellCrystal:
                The currently recorded crystal for the spell.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
            KeyError:
                If no crystal answers; the message reports the recorded count
                so callers can self-correct.
        """
        self.check_cleaned()
        with self._lock:
            keys = [spell_id]
            if frame_name is not None:
                keys.insert(0, SpellCrystal.compose_custody_key(spell_id, frame_name))
            for key in keys:
                crystal = self._spell_crystals_by_spell_id.get(key)
                if crystal is None:
                    crystal = self._inactive_spell_crystals_by_spell_id.get(key)
                if crystal is not None:
                    return crystal
            if frame_name is None:
                prefix = spell_id + "@"
                for location in (
                        self._spell_crystals_by_spell_id,
                        self._inactive_spell_crystals_by_spell_id,
                ):
                    matches = [key for key in location if key.startswith(prefix)]
                    if matches:
                        return location[min(matches)]
            raise KeyError(
                "No spell crystal recorded for spell_id {0!r}{1} in "
                "profile {2!r} ({3} crystals recorded).".format(
                    spell_id,
                    "" if frame_name is None else " in frame {0!r}".format(frame_name),
                    self._profile_name,
                    len(self._spell_crystals_by_spell_id),
                )
            )
''')
session.replace(PROFILE, r'''        Returns:
            Dict[str, Dict[str, object]]:
                spell_id -> crystal describe() payload + custody_state.
''', r'''        Returns:
            Dict[str, Dict[str, object]]:
                custody key (the spell id, or "<spell_id>@<frame>" under
                per-frame ids) -> crystal describe() payload + custody_state.
''')
session.insert_after(PROFILE, r'''            - Members missing custody report under "members_without_
              custody" instead of raising (shortfall honesty; the runner
              refuses those members at graft time).
''', r'''            - Each member's custody is the copy recorded for the index's own
              Book: under per-frame ids another frame's Book may hold the same
              spell id (0.2.8214). The members map stays keyed by spell id.
''')
session.replace(PROFILE, r'''            for spell_id in list(index_payload.get("member_spell_ids", [])):
                crystal = self._spell_crystals_by_spell_id.get(spell_id)
                custody_state = "active"
                if crystal is None:
                    crystal = self._inactive_spell_crystals_by_spell_id.get(
                        spell_id
                    )
                    custody_state = "inactive"
                if crystal is None:
''', r'''            for spell_id in list(index_payload.get("member_spell_ids", [])):
                crystal, custody_state = self._find_book_custody_locked(
                    str(spell_id), index_payload.get("spellbook_id")
                )
                if crystal is None:
''')
session.insert_before(PROFILE, r'''    def describe_mutation_research_record(self) -> Optional[Dict[str, object]]:
''', r'''    def _find_book_custody_locked(
            self,
            spell_id: str,
            spellbook_id: object,
    ) -> Tuple[Optional[SpellCrystal], str]:
        """
        Internal

        Find the custody crystal one Book holds for a spell id, under the held lock.

        Contract:
            - Caller holds `self._lock`.
            - Matches the crystal's spell id and parent edge, active location
              first, so a spell id recorded in several frames (per-frame ids,
              0.2.8214) answers the named Book's copy.
            - Falls back to the exact key (a process-wide record keyed by the
              spell id), whichever Book holds it.

        Args:
            spell_id:
                The member's spell SHA.
            spellbook_id:
                The index's owning Book.

        Returns:
            Tuple[Optional[SpellCrystal], str]:
                The crystal (None when absent) and its location, "active" or
                "inactive".
        """
        for location_name, location in (
                ("active", self._spell_crystals_by_spell_id),
                ("inactive", self._inactive_spell_crystals_by_spell_id),
        ):
            for crystal in location.values():
                if crystal.id == spell_id and crystal.spellbook_id == spellbook_id:
                    return crystal, location_name
        for location_name, location in (
                ("active", self._spell_crystals_by_spell_id),
                ("inactive", self._inactive_spell_crystals_by_spell_id),
        ):
            crystal = location.get(spell_id)
            if crystal is not None:
                return crystal, location_name
        return None, "active"

''')
session.replace(PROFILE, r'''                if kind == "spell_removed":
                    payloads.setdefault(kind, {})[key] = {
                        "spell_id": key,
                        "removed": True,
                    }
                    continue
                if kind == "spell_activity":
                    # Activity transitions have no twin object; capture the
                    # CURRENT truth: which location holds custody now.
                    payloads.setdefault(kind, {})[key] = {
                        "spell_id": key,
                        "active": key in self._spell_crystals_by_spell_id,
''', r'''                if kind == "spell_removed":
                    # The key is the custody key; the crystal is gone, so the
                    # spell id is read from the key (0.2.8214).
                    payloads.setdefault(kind, {})[key] = {
                        "spell_id": SpellCrystal.spell_id_of_custody_key(key),
                        "custody_key": key,
                        "removed": True,
                    }
                    continue
                if kind == "spell_activity":
                    # Activity transitions have no twin object; capture the
                    # CURRENT truth: which location holds custody now.
                    payloads.setdefault(kind, {})[key] = {
                        "spell_id": SpellCrystal.spell_id_of_custody_key(key),
                        "custody_key": key,
                        "active": key in self._spell_crystals_by_spell_id,
''')

# ----------------------------------------------------------------------------------------------------------------
# PersistenceSystem: pass-through.
# ----------------------------------------------------------------------------------------------------------------
SYSTEM = "src/melder/crystallizer/persistence/persistence_system.py"
session.replace(SYSTEM, r'''    def record_spell_activity(self, spell_id: str, active: bool) -> None:
        """
        Mirror one runtime park/promote flip into the ACTIVE profile.

        Args:
            spell_id:
                The spell whose activity flipped.
''', r'''    def record_spell_activity(self, custody_key: str, active: bool) -> None:
        """
        Mirror one runtime park/promote flip into the ACTIVE profile.

        Args:
            custody_key:
                The flipped crystal's record key (the spell id, or
                "<spell_id>@<frame>" under per-frame ids, 0.2.8214).
''')
session.replace(SYSTEM, r'''        self.active_profile.record_spell_activity(spell_id, active=active)
''', r'''        self.active_profile.record_spell_activity(custody_key, active=active)
''')
session.replace(SYSTEM, r'''    def remove_spell_crystal(self, spell_id: str) -> None:
        """
        Evict one spell's custody from the ACTIVE profile.

        Args:
            spell_id:
                The removed spell's SHA256 identity.
''', r'''    def remove_spell_crystal(self, custody_key: str) -> None:
        """
        Evict one spell's custody from the ACTIVE profile.

        Args:
            custody_key:
                The removed crystal's record key (the spell id, or
                "<spell_id>@<frame>" under per-frame ids, 0.2.8214).
''')
session.replace(SYSTEM, r'''        self.active_profile.remove_spell_crystal(spell_id)
''', r'''        self.active_profile.remove_spell_crystal(custody_key)
''')
session.replace(SYSTEM, r'''    def get_spell_crystal(self, spell_id: str) -> SpellCrystal:
        """
        Return the ACTIVE profile's custody crystal for one spell.

        Args:
            spell_id:
                The spell's SHA256 identity.
''', r'''    def get_spell_crystal(
            self,
            spell_id: str,
            frame_name: Optional[str] = None,
    ) -> SpellCrystal:
        """
        Return the ACTIVE profile's custody crystal for one spell.

        Args:
            spell_id:
                The spell's SHA256 identity, or a full custody key.
            frame_name:
                Optional frame whose copy is wanted (see
                `PersistenceProfile.get_spell_crystal`, 0.2.8214).
''')
session.replace(SYSTEM, r'''                If the active profile records no crystal for `spell_id`.
        """
        self.check_cleaned()
        return self.active_profile.get_spell_crystal(spell_id)
''', r'''                If the active profile records no crystal that answers.
        """
        self.check_cleaned()
        return self.active_profile.get_spell_crystal(spell_id, frame_name=frame_name)
''')
session.replace(SYSTEM, r'''                spell_id -> crystal describe() payload + "custody_state".
''', r'''                custody key (the spell id, or "<spell_id>@<frame>" under
                per-frame ids) -> crystal describe() payload + "custody_state".
''')

# ----------------------------------------------------------------------------------------------------------------
# Crystallizer facade: key-aware verbs.
# ----------------------------------------------------------------------------------------------------------------
FACADE = "src/melder/crystallizer/crystallizer.py"
session.replace(FACADE, "from typing import TYPE_CHECKING, Any\n", "from typing import TYPE_CHECKING, Any, Optional\n")
session.replace(FACADE, r'''    def get_spell_crystal(self, spell_id: str) -> SpellCrystal:
''', r'''    def get_spell_crystal(
            self,
            spell_id: str,
            frame_name: Optional[str] = None,
    ) -> SpellCrystal:
''')
session.insert_after(FACADE, r'''            - Returns the SEALED crystal for one spell id, which is a point-in-time
              record and not a live view of the spell.
''', r'''            - Per frame (0.2.8214): under per-frame spell ids one spell id may be
              recorded once per frame. `frame_name` selects that frame's copy;
              without it the lowest custody key answers.
''')
session.replace(FACADE, r'''        Args:
            spell_id:
                The spell's SHA256 identity.

        Returns:
            SpellCrystal:
                The currently recorded crystal for the spell.
''', r'''        Args:
            spell_id:
                The spell's SHA256 identity, or a full custody key.
            frame_name:
                Optional frame whose copy is wanted.

        Returns:
            SpellCrystal:
                The currently recorded crystal for the spell.
''')
session.replace(FACADE, r'''        return self._persistence_system.get_spell_crystal(spell_id)
''', r'''        return self._persistence_system.get_spell_crystal(
            spell_id, frame_name=frame_name
        )
''')
session.replace(FACADE, r'''    def emit_spell_removed(self, spell_id: str) -> None:
''', r'''    def emit_spell_removed(
            self,
            spell_id: str,
            frame_name: Optional[str] = None,
    ) -> None:
''')
session.replace(FACADE, r'''        Contract:
            - NO-OP while the crystallizer is not activated.

        Args:
            spell_id:
                The removed spell's SHA256 identity.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
        """
        self.check_cleaned()
        if not self._activated:
            return
        self._persistence_system.remove_spell_crystal(spell_id)
''', r'''        Contract:
            - NO-OP while the crystallizer is not activated.
            - Addresses one custody key (0.2.8214): the spell id under
              process-wide ids (the frame is ignored), "<spell_id>@<frame>"
              under per-frame ids, so only that frame's copy leaves.

        Args:
            spell_id:
                The removed spell's SHA256 identity.
            frame_name:
                The frame of the Book removing the spell; required under
                per-frame spell ids.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
            ValueError:
                Under per-frame spell ids when `frame_name` is None.
        """
        self.check_cleaned()
        if not self._activated:
            return
        self._persistence_system.remove_spell_crystal(
            self._custody_key_for(spell_id, frame_name)
        )
''')
session.replace(FACADE, r'''    def emit_spell_activity(self, spell_id: str, active: bool) -> None:
''', r'''    def emit_spell_activity(
            self,
            spell_id: str,
            active: bool,
            frame_name: Optional[str] = None,
    ) -> None:
''')
session.insert_after(FACADE, r'''            - Tolerates missing custody (activity for a spell the record
              never held is journaled without a crystal move).
''', r'''            - Addresses one custody key (0.2.8214): the spell id under
              process-wide ids (the frame is ignored), "<spell_id>@<frame>"
              under per-frame ids, so only that frame's copy moves.
''')
session.replace(FACADE, r'''                True = promoted to active; False = parked inactive.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
        """
        self.check_cleaned()
        if not self._activated:
            return
        self._persistence_system.record_spell_activity(spell_id, active=active)
        self._maybe_create_automatic_checkpoint()
        try:
            crystal = self._persistence_system.get_spell_crystal(spell_id)
        except KeyError:
            return
''', r'''                True = promoted to active; False = parked inactive.
            frame_name:
                The frame of the Book that flipped it; required under
                per-frame spell ids.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the crystallizer has been cleaned.
            ValueError:
                Under per-frame spell ids when `frame_name` is None.
        """
        self.check_cleaned()
        if not self._activated:
            return
        custody_key = self._custody_key_for(spell_id, frame_name)
        self._persistence_system.record_spell_activity(custody_key, active=active)
        self._maybe_create_automatic_checkpoint()
        try:
            crystal = self._persistence_system.get_spell_crystal(custody_key)
        except KeyError:
            return
''')
session.insert_before(FACADE, r'''    def emit(self, twin: Cleanable) -> None:
''', r'''    def _custody_key_for(self, spell_id: str, frame_name: Optional[str]) -> str:
        """
        Internal

        Return the record key a spell-level emit verb addresses.

        Contract:
            - Under process-wide spell ids the key is the spell id; the frame
              is optional and ignored.
            - Under per-frame spell ids the key is "<spell_id>@<frame_name>"
              (`SpellCrystal.compose_custody_key`), so only the named frame's
              copy is touched; a missing frame is refused (0.2.8214).
            - Reads the regime from the hosting Aether without a lock
              (`Aether.process_wide_unique_spell_ids`).

        Args:
            spell_id:
                The spell's SHA256 identity.
            frame_name:
                The frame of the Book that emits.

        Returns:
            str: The custody key.

        Raises:
            ValueError:
                Under per-frame spell ids when `frame_name` is None.
        """
        if self._aether.process_wide_unique_spell_ids:
            return spell_id
        if frame_name is None:
            raise ValueError(
                "Under per-frame spell ids a spell id can be bound in several frames and the record keeps "
                "one copy per frame, so frame_name is required to address spell {0!r}. Pass the frame of the "
                "Book that emits (Spellbook passes its own).".format(spell_id)
            )
        return SpellCrystal.compose_custody_key(spell_id, frame_name)

''')
session.replace(FACADE, r'''            when the installed policy enables it; bind-time fingerprints are
            recorded independently of that opt-in.
''', r'''            when the installed policy enables it; bind-time fingerprints are
            recorded independently of that opt-in. The record key follows the
            regime in force: under per-frame spell ids the crystal is keyed
            "<spell_id>@<frame>" (0.2.8214).
''')
session.replace(FACADE, r'''            retain_user_sources=self._configuration.retain_user_sources,
            site_package_dependency_descent=(
                self._configuration.site_package_dependency_descent
            ),
        )
''', r'''            retain_user_sources=self._configuration.retain_user_sources,
            site_package_dependency_descent=(
                self._configuration.site_package_dependency_descent
            ),
            per_frame_custody=not self._aether.process_wide_unique_spell_ids,
        )
''')

# ----------------------------------------------------------------------------------------------------------------
# RecordVersion 4.0.0.
# ----------------------------------------------------------------------------------------------------------------
session.replace("src/melder/crystallizer/persistence/record_version.py", r'''    # Major 2 fenced non-resolvable capability. Major 3 additionally fences child
    # topology: older loaders would otherwise mistake a lesser row for a Book root.
    CURRENT: ClassVar[str] = "3.0.0"
''', r'''    # Major 2 fenced non-resolvable capability. Major 3 additionally fences child
    # topology: older loaders would otherwise mistake a lesser row for a Book root.
    # Major 4 fences frame-scoped custody keys ("<spell_id>@<frame>", per-frame
    # spell ids): an older loader would fold one frame's copy over another's.
    CURRENT: ClassVar[str] = "4.0.0"
''')

# ----------------------------------------------------------------------------------------------------------------
# ImpactEngine: a spell id answers through frame-scoped keys.
# ----------------------------------------------------------------------------------------------------------------
IMPACT = "src/melder/crystallizer/crystal_analysis/impact_engine.py"
session.replace(IMPACT, r'''                spell_id -> crystal describe() payload (+ the seam's
''', r'''                custody key (the spell id, or "<spell_id>@<frame>" under
                per-frame ids) -> crystal describe() payload (+ the seam's
''')
session.insert_after(IMPACT, r'''            - Unknown SHAs answer honestly ("unknown_spell": True).
''', r'''            - A spell id recorded under frame-scoped keys (per-frame ids,
              0.2.8214) answers through its lowest matching key; the radius
              lists custody keys, one per frame's copy.
''')
session.replace(IMPACT, r'''        self.check_cleaned()
        payload = self._custody_by_spell.get(str(spell_id))
        if payload is None:
            return {
''', r'''        self.check_cleaned()
        payload = self._custody_by_spell.get(str(spell_id))
        if payload is None:
            # Per-frame records key custody "<spell_id>@<frame>" (0.2.8214):
            # a bare spell id answers through its lowest matching key.
            matching_keys = [
                custody_key
                for custody_key, candidate in self._custody_by_spell.items()
                if str(candidate.get("id")) == str(spell_id)
            ]
            if matching_keys:
                payload = self._custody_by_spell[min(matching_keys)]
        if payload is None:
            return {
''')

# ----------------------------------------------------------------------------------------------------------------
# LoadAdmission retarget: custody follows the target frame.
# ----------------------------------------------------------------------------------------------------------------
ADMISSION = "src/melder/crystallizer/crystal_loader_system/load_admission.py"
session.insert_after(ADMISSION, r'''from melder.crystallizer.crystal_loader_system.load_plan import LoadPlan
''', r'''from melder.crystallizer.crystals.spell_crystal import SpellCrystal
''')
session.insert_before(ADMISSION, r'''            - Inputs are never mutated: touched kinds are shallow-copied
              per payload before rewrite.
''', r'''            - Spell custody payloads rewrite their `frame_name` too; a
              frame-scoped custody key ("<spell_id>@<frame>", per-frame ids)
              is rebuilt for the target and its entry re-keyed, while a
              process-wide key (the bare spell id) stays (0.2.8214).
''')
session.replace(ADMISSION, r'''            if kind_payloads:
                rewritten[kind] = kind_payloads
        return rewritten
''', r'''            if kind_payloads:
                rewritten[kind] = kind_payloads
        custody = dict(rewritten.get("spell_crystal", {}))
        if custody:
            retargeted: Dict[str, object] = {}
            for key, payload in custody.items():
                adjusted = dict(payload)
                if "frame_name" in adjusted:
                    adjusted["frame_name"] = target_frame_name
                spell_id = str(adjusted.get("id", SpellCrystal.spell_id_of_custody_key(key)))
                if key != spell_id:
                    key = SpellCrystal.compose_custody_key(spell_id, target_frame_name)
                    adjusted["custody_key"] = key
                retargeted[key] = adjusted
            rewritten["spell_crystal"] = retargeted
        return rewritten
''')

# ----------------------------------------------------------------------------------------------------------------
# Spellbook: spell-level emits name their frame.
# ----------------------------------------------------------------------------------------------------------------
BOOK = "src/melder/aether/spellbook/spellbook.py"
session.replace(BOOK, r'''                self._crystallizer.emit_spell_removed(target_spell_id)
''', r'''                self._crystallizer.emit_spell_removed(
                    target_spell_id, frame_name=self._aetheric_frame_name
                )
''')
session.replace(BOOK, r'''            self._crystallizer.emit_spell_activity(spell_id, active=False)
''', r'''            self._crystallizer.emit_spell_activity(
                spell_id, active=False, frame_name=self._aetheric_frame_name
            )
''')
session.replace(BOOK, r'''            self._crystallizer.emit_spell_activity(spell_id, active=True)
''', r'''            self._crystallizer.emit_spell_activity(
                spell_id, active=True, frame_name=self._aetheric_frame_name
            )
''')
session.replace(BOOK, r'''                    self._crystallizer.emit_spell_removed(spell_id)
''', r'''                    self._crystallizer.emit_spell_removed(
                        spell_id, frame_name=self._aetheric_frame_name
                    )
''')

session.replace("src/melder/__version__.py", '__version__ = "0.2.8213"\n', '__version__ = "0.2.8214"\n')

long_lines = session.long_added_lines()
if long_lines:
    raise AssertionError("lines over 120:\n" + "\n".join(long_lines))
for path in session.write():
    print(path)
