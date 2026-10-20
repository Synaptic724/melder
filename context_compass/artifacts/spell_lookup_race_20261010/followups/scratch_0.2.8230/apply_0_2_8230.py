"""Spell-map race fixes and the id-lookup docs (0.2.8230): exact anchors, each file keeps its EOL. usage: <root>"""
import pathlib, sys

ROOT = pathlib.Path(sys.argv[1])


def edit(rel, ops):
    path = ROOT / rel
    data = path.read_bytes().decode('utf-8')
    crlf = '\r\n' in data
    text = data.replace('\r\n', '\n')
    for anchor, new, count in ops:
        found = text.count(anchor)
        if found != count:
            raise SystemExit(f'{rel}: anchor x{found} (want {count}): {anchor[:80]!r}')
        text = text.replace(anchor, new)
    path.write_bytes((text.replace('\n', '\r\n') if crlf else text).encode('utf-8'))
    print(f"{rel}: {len(ops)} edits ({'CRLF' if crlf else 'LF'})")


edit('src/melder/aether/spellbook/spellbook.py', [('                registration_started = True\n'
  '                self._lookup_spells[new_spell._key] = spell_index\n'
  '                self._spells[spell_index] = new_spell\n'
  '                self._register_owned_spell_id(new_spell.spell_id, new_spell)\n',
  '                registration_started = True\n'
  '                # Publish into the four active maps (_lookup_spells, _spells, and through\n'
  '                # _register_owned_spell_id _spells_by_id and _spell_id_pool) under the Book lock, as every\n'
  '                # other writer of `_spells` does (removal, notch park and promote, index destruction,\n'
  '                # transfer and its rollback), so a walk that holds the lock never meets this insert\n'
  '                # mid-walk. Narrow on purpose: claim_lookup above and the bind callbacks stay outside it.\n'
  '                # No new lock-order edge: _register_owned_spell_id always took this lock at this point.\n'
  '                with self._lock:\n'
  '                    self._lookup_spells[new_spell._key] = spell_index\n'
  '                    self._spells[spell_index] = new_spell\n'
  '                    self._register_owned_spell_id(new_spell.spell_id, new_spell)\n',
  1),
 ('                    for candidate_spell in conduit_spellbook._spells.values():\n',
  "                    # Another Book's map, read without that Book's lock: walk a one-call snapshot.\n"
  '                    for candidate_spell in list(conduit_spellbook._spells.values()):\n',
  1),
 ('            Optional[Spell]: The resolved spell, or None if not found.\n'
  '        """\n'
  '\n'
  '        # Pull the map of SpellIndex? Spell for this conduit\n',
  '            Optional[Spell]: The resolved spell, or None if not found.\n'
  '\n'
  '        Threading:\n'
  '            Lock-free. Walks a one-call snapshot of the contracted map, which grants and revocations change\n'
  '            while no lock is held here, and probes each index with `SpellIndex._has_spell_unless_cleaned`:\n'
  '            the lender can clean an index this map still holds, and a cleaned index owns nothing (0.2.8230).\n'
  '        """\n'
  '\n'
  '        # Pull the map of SpellIndex? Spell for this conduit\n',
  1),
 ('        # Search for a SpellIndex whose version list contains this SHA\n'
  '        for spell_index, spell in spell_map.items():\n'
  '            if spell_index.has_spell(spell_id):\n'
  '                return spell\n',
  '        # Search for a SpellIndex whose version list contains this SHA\n'
  '        for spell_index, spell in list(spell_map.items()):\n'
  '            if spell_index._has_spell_unless_cleaned(spell_id):\n'
  '                return spell\n',
  1)])

edit('src/melder/aether/spellbook/bind/spell_index.py', [('        Threading:\n'
  '            Reads and writes under `self._lock`, so the result is a coherent\n'
  '            snapshot rather than a torn read.\n'
  '\n'
  '        Lifecycle / Cleanup:\n'
  '            Guarded by `check_cleaned()`.\n'
  '\n'
  '        Raises:\n'
  '            RuntimeError: If the object has been cleaned.\n'
  '\n'
  '        Returns:\n'
  '            bool: True if `spell_id` is in the member set, False otherwise.\n'
  '        """\n'
  '        self.check_cleaned()\n'
  '        with self._lock:\n'
  '            return spell_id in self._spells_in_index\n',
  '        Threading:\n'
  '            Reads and writes under `self._lock`, so the result is a coherent\n'
  '            snapshot rather than a torn read. The cleaned check is repeated under\n'
  '            that lock, the one `cleanup()` marks the index cleaned and deletes the\n'
  '            member set under, so a cleanup racing this call raises the documented\n'
  '            RuntimeError, never AttributeError (0.2.8230).\n'
  '\n'
  '        Lifecycle / Cleanup:\n'
  '            Guarded by `check_cleaned()`, before and after taking the lock.\n'
  '\n'
  '        Raises:\n'
  '            RuntimeError: If the object has been cleaned.\n'
  '\n'
  '        Returns:\n'
  '            bool: True if `spell_id` is in the member set, False otherwise.\n'
  '        """\n'
  '        self.check_cleaned()\n'
  '        with self._lock:\n'
  '            # Re-check under the lock: a cleanup between the unlocked check and the acquire has\n'
  '            # already deleted the member set.\n'
  '            self.check_cleaned()\n'
  '            return spell_id in self._spells_in_index\n'
  '\n'
  '    def _has_spell_unless_cleaned(self, spell_id: str) -> bool:\n'
  '        """\n'
  '        Internal\n'
  '\n'
  '        Return whether `spell_id` is a member of this index, answering False once\n'
  '        the index is cleaned.\n'
  '\n'
  '        Purpose:\n'
  '            Membership probe for walks over indexes the caller neither owns nor\n'
  '            locks - a contracted map, a contract detail - which can reach an index\n'
  '            after its owner cleaned it. A cleaned index owns nothing, so for such a\n'
  '            walk "not a member" is the truthful answer, where `has_spell` raises.\n'
  '\n'
  '        Contract:\n'
  '            - Same membership semantics as `has_spell` (the whole version\n'
  '              lineage, not only the selected id) while the index is live.\n'
  '            - Never raises for a cleaned index; returns False.\n'
  '\n'
  '        Threading:\n'
  '            Reads the cleaned flag and the member set under `self._lock`, the lock\n'
  '            `cleanup` holds while it marks the index cleaned and deletes the\n'
  '            member set, so a concurrent cleanup cannot tear the answer.\n'
  '\n'
  '        Args:\n'
  '            spell_id (str): The spell id to check.\n'
  '\n'
  '        Returns:\n'
  "            bool: True if this live index's member set contains `spell_id`;\n"
  '            False otherwise, and False once the index is cleaned.\n'
  '        """\n'
  '        with self._lock:\n'
  '            if self._cleaned:\n'
  '                return False\n'
  '            return spell_id in self._spells_in_index\n',
  1)])

edit('src/melder/aether/conduit/conduit_ward/contract/details.py', [('        Returns:\n'
  '            bool: True if the lineage advertises the version, else False.\n'
  '        """\n'
  '        self.check_cleaned()\n'
  '        member_ids = self.spell_index._spells_in_index\n'
  '        if not member_ids:\n'
  '            return False\n'
  '        return spell_id in member_ids\n',
  '        Returns:\n'
  '            bool: True if the lineage advertises the version, else False; False once the\n'
  '            owning Book has cleaned the index.\n'
  '\n'
  '        Threading:\n'
  '            The index belongs to the Book that owns the lineage, which can clean it while\n'
  '            this detail still holds it, so membership is read through\n'
  '            `SpellIndex._has_spell_unless_cleaned` under the index lock (0.2.8230; it read\n'
  '            the member set unlocked, which raised AttributeError when the cleanup won).\n'
  '        """\n'
  '        self.check_cleaned()\n'
  '        return self.spell_index._has_spell_unless_cleaned(spell_id)\n',
  2)])

edit('src/melder/aether/conduit/conduit.py', [("            - LOCAL ONLY. It walks THIS conduit's spellbook lineages, so a spell\n"
  '              reachable by contract from a peer conduit is NOT found here.\n'
  '            - Matches by LINEAGE MEMBERSHIP (`SpellIndex.has_spell`), so a superseded\n'
  '              version id still resolves - and it resolves to the CURRENT permissions,\n'
  '              not the permissions that version was bound with.\n',
  "            - LOCAL ONLY. It resolves through THIS conduit's spellbook\n"
  '              (`Spellbook.find_spell_by_id`), so a spell reachable by contract from a\n'
  '              peer conduit is NOT found here.\n'
  '            - Matches by LINEAGE, so a superseded or parked version id still resolves -\n'
  '              and it resolves to the CURRENT permissions, not the permissions that\n'
  '              version was bound with.\n'
  "            - Lock-free (0.2.8230): the lookup answers from the Book's id maps instead of\n"
  '              walking its live index map under the conduit lock, which a concurrent bind\n'
  '              or removal could resize mid-walk.\n',
  1),
 ('        self.check_cleaned()\n'
  '        with self._lock:\n'
  '            target_spell: Optional[Spell] = None\n'
  '\n'
  '            # Walk local SpellIndex keys and check which lineage owns this version\n'
  '            for spell_index, spell in self._spellbook._spells.items():\n'
  '                if spell_index.has_spell(spell_id):\n'
  '                    target_spell = spell\n'
  '                    break\n',
  '        self.check_cleaned()\n'
  "        # Resolve the lineage from the Book's id maps: O(1) and no walk of the live index map.\n"
  '        target_spell: Optional[Spell] = self._spellbook.find_spell_by_id(spell_id)\n',
  1)])

edit('src/melder/nexus/rift/command_system/command_system.py', [('            for spell_index, spell in spellbook._spells.items():\n'
  '                if spell_index.has_spell(spell_id):\n'
  '                    return spell\n'
  '            raise ValueError(\n'
  '                "Spell id \'{0}\' was not found in the owner spellbook.".format(spell_id)\n',
  "            # The owner Book's id maps answer the lineage lookup in O(1), without walking its\n"
  '            # live index map, which a concurrent bind or removal could resize mid-walk.\n'
  '            spell = spellbook.find_spell_by_id(spell_id)\n'
  '            if spell is not None:\n'
  '                return spell\n'
  '            raise ValueError(\n'
  '                "Spell id \'{0}\' was not found in the owner spellbook.".format(spell_id)\n',
  1)])

edit('src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py', [('        owned = spellbook._spells or {}\n        for spell_index in owned.keys():\n',
  '        # One-call snapshots: these maps belong to another Book, read without its lock.\n'
  '        owned = spellbook._spells or {}\n'
  '        for spell_index in list(owned):\n',
  1),
 ('        for spell_map in contracted.values():\n            for spell_index in spell_map.keys():\n',
  '        for spell_map in list(contracted.values()):\n            for spell_index in list(spell_map):\n',
  1)])

edit('src/melder/aether/spellbook/spellbook_creation_system.py', [('            broken_spells = SpellbookCreationSystem._collect_broken_spells(\n'
  '                spells=spellbook._spells.values(),\n'
  '            )\n',
  '            # One-call snapshot (list(...)): this pass also runs from Conduit.validate_resolution, where no Book '
  'lock\n'
  '            # keeps a concurrent bind or removal from resizing the live map mid-walk.\n'
  '            broken_spells = SpellbookCreationSystem._collect_broken_spells(\n'
  '                spells=list(spellbook._spells.values()),\n'
  '            )\n',
  1),
 ('            if spell_ids is None:\n                for spell in spellbook._spells.values():\n',
  '            if spell_ids is None:\n'
  '                # One-call snapshot (list(...)): this pass also runs from Conduit.validate_resolution, where no '
  'Book lock\n'
  '                # keeps a concurrent bind or removal from resizing the live map mid-walk.\n'
  '                for spell in list(spellbook._spells.values()):\n',
  1),
 ('        spellbook.check_cleaned()\n'
  '        if not spellbook._spells:\n'
  '            return []\n'
  '\n'
  '        lead_spell = next(iter(spellbook._spells.values()))\n',
  '        spellbook.check_cleaned()\n'
  '        # One-call snapshot: next(iter(...)) over the live map raises when a concurrent bind\n'
  '        # resizes it between the two calls, and these factories also run from\n'
  '        # Conduit.validate_resolution, where no Book lock keeps binds out.\n'
  '        spells = list(spellbook._spells.values())\n'
  '        if not spells:\n'
  '            return []\n'
  '\n'
  '        lead_spell = spells[0]\n',
  3),
 ('        eligible_spells = [\n'
  '            spell\n'
  '            for spell in spellbook._spells.values()\n'
  '            if SpellbookCreationSystem._is_spell_plan_phase_eligible(spell)\n'
  '        ]\n',
  '        # One-call snapshot (list(...)): this pass also runs from Conduit.validate_resolution, where no Book lock\n'
  '        # keeps a concurrent bind or removal from resizing the live map mid-walk.\n'
  '        eligible_spells = [\n'
  '            spell\n'
  '            for spell in list(spellbook._spells.values())\n'
  '            if SpellbookCreationSystem._is_spell_plan_phase_eligible(spell)\n'
  '        ]\n',
  5)])

edit('src/melder/aether/spellbook/spellbook.py', [('    ) -> Conduit | None:\n'
  '        """\n'
  '        Internal\n'
  '\n'
  '        Resolve the conduit that owns the supplied spell id through Aether.\n',
  '    ) -> Conduit:\n'
  '        """\n'
  '        Internal\n'
  '\n'
  '        Resolve the conduit that owns the supplied spell id through Aether.\n',
  1),
 ('        Returns:\n'
  '            Optional[Conduit]:\n'
  '                Owning conduit when found, otherwise "None".\n'
  '        """\n'
  '        if aetheric_frame_name == "default":\n',
  '        Returns:\n'
  '            Conduit:\n'
  '                The root conduit that owns the spell id.\n'
  '\n'
  '        Raises:\n'
  '            ValueError: If no conduit in the frame claims the id - unknown or removed, bound in\n'
  '                another frame, its owner cleaned, or a lineage between owners while an ownership\n'
  '                transfer runs - or the frame does not exist (`Aether._get_conduit_by_spell_id`).\n'
  '                It always raised; until 0.2.8230 this docstring promised None.\n'
  '        """\n'
  '        if aetheric_frame_name == "default":\n',
  1),
 ('        Returns:\n'
  '            Optional[Spell]:\n'
  '                Matching spell when found, otherwise "None".\n'
  '        """\n'
  '        owner = self._get_conduit_by_spell_id(spell_id, aetheric_frame_name)\n',
  '        Returns:\n'
  '            Optional[Spell]:\n'
  "                The live spell of the lineage holding the id, or None when the owning conduit's\n"
  '                Spellbook does not resolve it (`Spellbook.find_spell_by_id`).\n'
  '\n'
  '        Raises:\n'
  '            ValueError: If no conduit in the frame claims the id, or the frame does not exist\n'
  '                (`_get_conduit_by_spell_id`).\n'
  '            RuntimeError: If the owning conduit has no spellbook.\n'
  '        """\n'
  '        owner = self._get_conduit_by_spell_id(spell_id, aetheric_frame_name)\n',
  1)])

edit('src/melder/aether/conduit/conduit.py', [('    def get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> '
  'Optional["Conduit"]:\n',
  '    def get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> "Conduit":\n',
  1),
 ('        Contract:\n'
  "            - Resolves through the spellbook's Aether-wide lookup, so it can find a\n"
  "              conduit in ANOTHER frame - it is not scoped to this conduit's frame\n"
  '              unless you pass one.\n'
  '            - Runs under the conduit lock.\n'
  '\n'
  '        Args:\n'
  '            spell_id (str): The unique identifier of the spell.\n'
  '            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".\n'
  '\n'
  '        Returns:\n'
  '            Optional[Conduit]: The conduit that registered the spell, or None if not found.\n'
  '\n'
  '        Raises:\n'
  '            RuntimeError: If the Conduit is cleaned.\n'
  '        """\n',
  '        Contract:\n'
  '            - Searches ONE frame: this conduit\'s Spellbook frame by default ("default"\n'
  '              means that frame), or the frame you name. An id bound only in another\n'
  '              frame is not found unless you name that frame.\n'
  '            - A miss RAISES; it never returns None. The `get_*` lookups raise ValueError on\n'
  '              a miss and the `find_*` lookups return None (owner decision 2026-10-11; the\n'
  '              convention of the Aether conduit and frame lookups). Until 0.2.8230 this\n'
  '              docstring and the annotation promised None, which the method never returned.\n'
  '            - Runs under the conduit lock.\n'
  '\n'
  '        Args:\n'
  '            spell_id (str): The unique identifier of the spell.\n'
  '            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".\n'
  '\n'
  '        Returns:\n'
  '            Conduit: The root conduit that owns the spell.\n'
  '\n'
  '        Raises:\n'
  '            RuntimeError: If the Conduit is cleaned.\n'
  '            ValueError: If no conduit in the frame claims the id - unknown or removed, bound in\n'
  '                another frame, its owner cleaned, or a lineage between owners while an\n'
  '                ownership transfer runs - or the frame does not exist.\n'
  '        """\n',
  1),
 ("          2) Searches that conduit's spellbook for a SpellIndex whose lineage contains\n"
  '             this version ID.\n'
  '          3) Returns the corresponding Spell instance if found.\n',
  "          2) Resolves the id in that conduit's spellbook (`Spellbook.find_spell_by_id`):\n"
  '             the live spell of the lineage that contains this version ID.\n'
  '          3) Returns that Spell instance.\n',
  1),
 ('        Returns:\n'
  '            Optional[Spell]: The spell object if found, otherwise None.\n'
  '\n'
  '        Raises:\n'
  '            RuntimeError: If the Conduit is cleaned.\n'
  '        """\n'
  '        self.check_cleaned()\n'
  '        return self._spellbook._get_spell_by_id_via_aether(\n',
  '        Returns:\n'
  "            Optional[Spell]: The spell object, or None when the owner's spellbook does not\n"
  '            resolve the id to a live spell.\n'
  '\n'
  '        Raises:\n'
  '            RuntimeError: If the Conduit is cleaned, or the owning conduit has no spellbook.\n'
  '            ValueError: If no conduit in the frame claims the id - unknown or removed, bound in\n'
  '                another frame, its owner cleaned, or a lineage between owners while an\n'
  '                ownership transfer runs - or the frame does not exist. A miss raises, as the\n'
  '                `get_*` lookups do (owner decision 2026-10-11); until 0.2.8230 this docstring\n'
  '                promised None.\n'
  '        """\n'
  '        self.check_cleaned()\n'
  '        return self._spellbook._get_spell_by_id_via_aether(\n',
  1)])

