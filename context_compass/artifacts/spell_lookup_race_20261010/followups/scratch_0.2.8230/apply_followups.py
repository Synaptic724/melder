"""Spell-map race follow-ups (0.2.8230): exact-anchor edits; keeps each file's line endings. usage: apply.py <root>"""
import pathlib, sys

ROOT = pathlib.Path(sys.argv[1])


def edit(rel, ops):
    path = ROOT / rel
    data = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in data
    text = data.replace("\r\n", "\n")
    for anchor, new, count in ops:
        found = text.count(anchor)
        if found != count:
            raise SystemExit(f"{rel}: anchor x{found} (want {count}): {anchor[:80]!r}")
        text = text.replace(anchor, new)
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print(f"{rel}: {len(ops)} edits ({'CRLF' if crlf else 'LF'})")


SB = "src/melder/aether/spellbook/spellbook.py"
edit(SB, [
    ("""                registration_started = True
                self._lookup_spells[new_spell._key] = spell_index
                self._spells[spell_index] = new_spell
                self._register_owned_spell_id(new_spell.spell_id, new_spell)
""", """                registration_started = True
                # Publish into the four active maps (_lookup_spells, _spells, and through
                # _register_owned_spell_id _spells_by_id and _spell_id_pool) under the Book lock, as every
                # other writer of `_spells` does (removal, notch park and promote, index destruction,
                # transfer and its rollback), so a walk that holds the lock never meets this insert
                # mid-walk. Narrow on purpose: claim_lookup above and the bind callbacks stay outside it.
                # No new lock-order edge: _register_owned_spell_id always took this lock at this point.
                with self._lock:
                    self._lookup_spells[new_spell._key] = spell_index
                    self._spells[spell_index] = new_spell
                    self._register_owned_spell_id(new_spell.spell_id, new_spell)
""", 1),
    ("""                    for candidate_spell in conduit_spellbook._spells.values():
""", """                    # Another Book's map, read without that Book's lock: walk a one-call snapshot.
                    for candidate_spell in list(conduit_spellbook._spells.values()):
""", 1),
    ("""            Optional[Spell]: The resolved spell, or None if not found.
        \"\"\"

        # Pull the map of SpellIndex? Spell for this conduit
""", """            Optional[Spell]: The resolved spell, or None if not found.

        Threading:
            Lock-free. Walks a one-call snapshot of the contracted map, which grants and revocations change
            while no lock is held here, and probes each index with `SpellIndex._has_spell_unless_cleaned`:
            the lender can clean an index this map still holds, and a cleaned index owns nothing (0.2.8230).
        \"\"\"

        # Pull the map of SpellIndex? Spell for this conduit
""", 1),
    ("""        # Search for a SpellIndex whose version list contains this SHA
        for spell_index, spell in spell_map.items():
            if spell_index.has_spell(spell_id):
                return spell
""", """        # Search for a SpellIndex whose version list contains this SHA
        for spell_index, spell in list(spell_map.items()):
            if spell_index._has_spell_unless_cleaned(spell_id):
                return spell
""", 1),
    ("""                Owning conduit when found, otherwise "None".
""", """                Owning conduit when found, otherwise None: an id no conduit claims - unknown,
                removed, or a lineage between owners while an ownership transfer runs. An
                unknown frame raises ValueError (Aether._find_conduit_by_spell_id; 0.2.8230 -
                before, the miss raised the Aether lookup's ValueError despite this contract).
""", 1),
    ("""        return self._aether._get_conduit_by_spell_id(
""", """        return self._aether._find_conduit_by_spell_id(
""", 1),
])

SI = "src/melder/aether/spellbook/bind/spell_index.py"
edit(SI, [
    ("""        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            bool: True if `spell_id` is in the member set, False otherwise.
        \"\"\"
        self.check_cleaned()
        with self._lock:
            return spell_id in self._spells_in_index
""", """        Threading:
            Reads and writes under `self._lock`, so the result is a coherent
            snapshot rather than a torn read. The cleaned check is repeated under
            that lock, the one `cleanup()` marks the index cleaned and deletes the
            member set under, so a cleanup racing this call raises the documented
            RuntimeError, never AttributeError (0.2.8230).

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`, before and after taking the lock.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            bool: True if `spell_id` is in the member set, False otherwise.
        \"\"\"
        self.check_cleaned()
        with self._lock:
            # Re-check under the lock: a cleanup between the unlocked check and the acquire has
            # already deleted the member set.
            self.check_cleaned()
            return spell_id in self._spells_in_index

    def _has_spell_unless_cleaned(self, spell_id: str) -> bool:
        \"\"\"
        Internal

        Return whether `spell_id` is a member of this index, answering False once
        the index is cleaned.

        Purpose:
            Membership probe for walks over indexes the caller neither owns nor
            locks - a contracted map, a contract detail - which can reach an index
            after its owner cleaned it. A cleaned index owns nothing, so for such a
            walk "not a member" is the truthful answer, where `has_spell` raises.

        Contract:
            - Same membership semantics as `has_spell` (the whole version
              lineage, not only the selected id) while the index is live.
            - Never raises for a cleaned index; returns False.

        Threading:
            Reads the cleaned flag and the member set under `self._lock`, the lock
            `cleanup` holds while it marks the index cleaned and deletes the
            member set, so a concurrent cleanup cannot tear the answer.

        Args:
            spell_id (str): The spell id to check.

        Returns:
            bool: True if this live index's member set contains `spell_id`;
            False otherwise, and False once the index is cleaned.
        \"\"\"
        with self._lock:
            if self._cleaned:
                return False
            return spell_id in self._spells_in_index
""", 1),
])

DT = "src/melder/aether/conduit/conduit_ward/contract/details.py"
edit(DT, [
    ("""        Returns:
            bool: True if the lineage advertises the version, else False.
        \"\"\"
        self.check_cleaned()
        member_ids = self.spell_index._spells_in_index
        if not member_ids:
            return False
        return spell_id in member_ids
""", """        Returns:
            bool: True if the lineage advertises the version, else False; False once the
            owning Book has cleaned the index.

        Threading:
            The index belongs to the Book that owns the lineage, which can clean it while
            this detail still holds it, so membership is read through
            `SpellIndex._has_spell_unless_cleaned` under the index lock (0.2.8230; it read
            the member set unlocked, which raised AttributeError when the cleanup won).
        \"\"\"
        self.check_cleaned()
        return self.spell_index._has_spell_unless_cleaned(spell_id)
""", 2),
])

CD = "src/melder/aether/conduit/conduit.py"
edit(CD, [
    ("""            - LOCAL ONLY. It walks THIS conduit's spellbook lineages, so a spell
              reachable by contract from a peer conduit is NOT found here.
            - Matches by LINEAGE MEMBERSHIP (`SpellIndex.has_spell`), so a superseded
              version id still resolves - and it resolves to the CURRENT permissions,
              not the permissions that version was bound with.
""", """            - LOCAL ONLY. It resolves through THIS conduit's spellbook
              (`Spellbook.find_spell_by_id`), so a spell reachable by contract from a
              peer conduit is NOT found here.
            - Matches by LINEAGE, so a superseded or parked version id still resolves -
              and it resolves to the CURRENT permissions, not the permissions that
              version was bound with.
            - Lock-free (0.2.8230): the lookup answers from the Book's id maps instead of
              walking its live index map under the conduit lock, which a concurrent bind
              or removal could resize mid-walk.
""", 1),
    ("""        self.check_cleaned()
        with self._lock:
            target_spell: Optional[Spell] = None

            # Walk local SpellIndex keys and check which lineage owns this version
            for spell_index, spell in self._spellbook._spells.items():
                if spell_index.has_spell(spell_id):
                    target_spell = spell
                    break
""", """        self.check_cleaned()
        # Resolve the lineage from the Book's id maps: O(1) and no walk of the live index map.
        target_spell: Optional[Spell] = self._spellbook.find_spell_by_id(spell_id)
""", 1),
])

CS = "src/melder/nexus/rift/command_system/command_system.py"
edit(CS, [
    ("""            for spell_index, spell in spellbook._spells.items():
                if spell_index.has_spell(spell_id):
                    return spell
            raise ValueError(
                "Spell id '{0}' was not found in the owner spellbook.".format(spell_id)
""", """            # The owner Book's id maps answer the lineage lookup in O(1), without walking its
            # live index map, which a concurrent bind or removal could resize mid-walk.
            spell = spellbook.find_spell_by_id(spell_id)
            if spell is not None:
                return spell
            raise ValueError(
                "Spell id '{0}' was not found in the owner spellbook.".format(spell_id)
""", 1),
])

TR = "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py"
edit(TR, [
    ("""        owned = spellbook._spells or {}
        for spell_index in owned.keys():
""", """        # One-call snapshots: these maps belong to another Book, read without its lock.
        owned = spellbook._spells or {}
        for spell_index in list(owned):
""", 1),
    ("""        for spell_map in contracted.values():
            for spell_index in spell_map.keys():
""", """        for spell_map in list(contracted.values()):
            for spell_index in list(spell_map):
""", 1),
])

CR = "src/melder/aether/spellbook/spellbook_creation_system.py"
SNAP = ("# One-call snapshot (list(...)): this pass also runs from Conduit.validate_resolution, where no Book lock\n"
        "{i}# keeps a concurrent bind or removal from resizing the live map mid-walk.\n")
edit(CR, [
    ("""            broken_spells = SpellbookCreationSystem._collect_broken_spells(
                spells=spellbook._spells.values(),
            )
""", "            " + SNAP.format(i="            ") + """            broken_spells = SpellbookCreationSystem._collect_broken_spells(
                spells=list(spellbook._spells.values()),
            )
""", 1),
    ("""            if spell_ids is None:
                for spell in spellbook._spells.values():
""", """            if spell_ids is None:
                """ + SNAP.format(i="                ") + """                for spell in list(spellbook._spells.values()):
""", 1),
    ("""        spellbook.check_cleaned()
        if not spellbook._spells:
            return []

        lead_spell = next(iter(spellbook._spells.values()))
""", """        spellbook.check_cleaned()
        # One-call snapshot: next(iter(...)) over the live map raises when a concurrent bind
        # resizes it between the two calls, and these factories also run from
        # Conduit.validate_resolution, where no Book lock keeps binds out.
        spells = list(spellbook._spells.values())
        if not spells:
            return []

        lead_spell = spells[0]
""", 3),
    ("""        eligible_spells = [
            spell
            for spell in spellbook._spells.values()
            if SpellbookCreationSystem._is_spell_plan_phase_eligible(spell)
        ]
""", "        " + SNAP.format(i="        ") + """        eligible_spells = [
            spell
            for spell in list(spellbook._spells.values())
            if SpellbookCreationSystem._is_spell_plan_phase_eligible(spell)
        ]
""", 5),
])

AE = "src/melder/aether/aether.py"
edit(AE, [
    ("""    def _get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Conduit:
        \"\"\"
        Finds the conduit that owns a specific spell ID within a frame.

        Args:
            spell_id (str): The spell ID (SHA256 hash) to search for.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            Conduit: The conduit that owns the spell.

        Raises:
            ValueError: If the frame does not exist or the spell ID is not found.
        \"\"\"
        self.check_cleaned()
        # Select frame
""", """    def _find_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Optional[Conduit]:
        \"\"\"
        Internal

        Find the root conduit that owns a spell id within a frame, or None.

        Purpose:
            The non-raising half of `_get_conduit_by_spell_id`, for callers whose contract answers None for
            an id no conduit claims: `Spellbook._get_conduit_by_spell_id`, and through it
            `Conduit.get_spell_by_id` and `Conduit.get_conduit_by_spell_id` (0.2.8230).

        Contract:
            - Returns None when the frame's registry names no owner for the id - an unknown or removed id, or
              a lineage between owners while an ownership transfer runs - and when the registered owner is
              no longer a live root of the frame.
            - The frame lookup is unchanged: an unknown frame raises ValueError.

        Threading:
            The registry read is locked inside `AethericFrame.find_conduit_id_for_spell`; the root read is one
            dict read. Takes no lock of its own.

        Args:
            spell_id (str): The spell ID (SHA256 hash) to search for.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            Optional[Conduit]: The owning root conduit, or None.

        Raises:
            ValueError: If the frame does not exist.
        \"\"\"
        self.check_cleaned()
        # Select frame
""", 1),
    ("""        # Locked lookup so a concurrent conjure cannot mutate the registry mid-scan.
        conduit_id = frame.find_conduit_id_for_spell(spell_id)
        # Owners are roots: a lesser scope owns only the lifecycle of what it creates.
        if conduit_id is not None:
            return self._get_root_conduit_by_id(conduit_id, aetheric_frame_name)

        self._logger.error(
""", """        # Locked lookup so a concurrent conjure cannot mutate the registry mid-scan.
        conduit_id = frame.find_conduit_id_for_spell(spell_id)
        if conduit_id is None:
            return None
        # Owners are roots: a lesser scope owns only the lifecycle of what it creates. An owner that is
        # no longer a live root of the frame (cleaned in between) is a miss as well.
        return frame._conduits.get(conduit_id)

    def _get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Conduit:
        \"\"\"
        Finds the conduit that owns a specific spell ID within a frame.

        The raising counterpart of `_find_conduit_by_spell_id`, for callers that treat a miss as an
        error (`CommandSystem.get_spell_by_id`).

        Args:
            spell_id (str): The spell ID (SHA256 hash) to search for.
            aetheric_frame_name (str): The name of the frame.

        Returns:
            Conduit: The conduit that owns the spell.

        Raises:
            ValueError: If the frame does not exist or the spell ID is not found.
        \"\"\"
        conduit = self._find_conduit_by_spell_id(spell_id, aetheric_frame_name)
        if conduit is not None:
            return conduit

        self._logger.error(
""", 1),
])

# Public docstrings whose behaviour the Aether find changes (0.2.8230).
edit(CD, [
    ("""        Returns:
            Optional[Conduit]: The conduit that registered the spell, or None if not found.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        \"\"\"
        self.check_cleaned()
        with self._lock:
            return self._spellbook._get_conduit_by_spell_id(
""", """        Returns:
            Optional[Conduit]: The conduit that registered the spell, or None when no conduit
            claims the id - unknown, removed, or a lineage between owners while an ownership
            transfer runs (0.2.8230; before, that miss raised ValueError).

        Raises:
            RuntimeError: If the Conduit is cleaned.
            ValueError: If the named frame does not exist.
        \"\"\"
        self.check_cleaned()
        with self._lock:
            return self._spellbook._get_conduit_by_spell_id(
""", 1),
    ("""        Returns:
            Optional[Spell]: The spell object if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        \"\"\"
        self.check_cleaned()
        return self._spellbook._get_spell_by_id_via_aether(
""", """        Returns:
            Optional[Spell]: The spell object if found, otherwise None - also when no conduit
            claims the id (0.2.8230; before, that miss raised ValueError).

        Raises:
            RuntimeError: If the Conduit is cleaned.
            ValueError: If the named frame does not exist.
        \"\"\"
        self.check_cleaned()
        return self._spellbook._get_spell_by_id_via_aether(
""", 1),
])
edit(SB, [
    ("""        Returns:
            Optional[Spell]:
                Matching spell when found, otherwise "None".
        \"\"\"
        owner = self._get_conduit_by_spell_id(spell_id, aetheric_frame_name)
""", """        Returns:
            Optional[Spell]:
                Matching spell when found, otherwise None - also when no conduit claims the id
                (0.2.8230; before, that miss raised the Aether lookup's ValueError).

        Raises:
            ValueError: If the named frame does not exist.
            RuntimeError: If the owning conduit has no spellbook.
        \"\"\"
        owner = self._get_conduit_by_spell_id(spell_id, aetheric_frame_name)
""", 1),
])

# The find carries the frame lookup the raising lookup used to own: name it in the log, and say where
# spell ownership resolves now.
edit(AE, [
    ("""                self._logger.error(
                    f"Aetheric frame '{aetheric_frame_name}' does not exist.",
                    "_get_conduit_by_spell_id",
                    exc_info=True
                )
""", """                self._logger.error(
                    f"Aetheric frame '{aetheric_frame_name}' does not exist.",
                    "_find_conduit_by_spell_id",
                    exc_info=True
                )
""", 1),
    ("""              `get_conduit_by_id`. Spell ownership resolves here (`_get_conduit_by_spell_id`) because
              only roots own spells.
""", """              `get_conduit_by_id`. Spell ownership resolves through the same root map
              (`_find_conduit_by_spell_id`) because only roots own spells.
""", 1),
])
