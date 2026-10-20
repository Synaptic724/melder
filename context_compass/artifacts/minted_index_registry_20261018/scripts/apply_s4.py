"""Apply S4's edits (STORY-2026-10-17-minted_index_missing_from_frame_registry) to a source tree.

Usage: apply_s4.py --root <tree> --edits A,B,C,D --notch <version> --check|--apply
  <version> is the notch S4 takes at landing; it replaces {notch} in the new texts, beside the patch id.
  A  spellbook.py `_apply_remove_from_index`: register the minted index in the frame's spell registry the way a
     post-conjure `bind` registers the index it creates (bind's guard and call, the Book's root conduit), and the
     seam's and its entry's docstrings say so.
  B  spellbook.py `_unregister_conduit_spells_from_aether`: the root's teardown unregisters the indexes that hold only
     parked versions too, and its docstring says so.
  C  mutation_research.py `_locate_live_membership`: a version is active when its index selects it and the frame's
     lineage registry tracks it as that index's current version; `residency_view`'s and its docstrings say so.
  D  spell.py `_spell_index_unless_cleaned` (docstring only): its Purpose lists the root's teardown among its readers
     (edit B reads each parked version's index through it).
Every anchor must occur exactly once; a file's line ending (LF, or CRLF throughout, as the working tree holds
mutation_research.py) is kept; nothing is written with --check.
"""
import pathlib
import re
import sys

SPELLBOOK = "src/melder/aether/spellbook/spellbook.py"
RESEARCH = "src/melder/mutation_research/mutation_research.py"
SPELL = "src/melder/aether/spellbook/spell.py"

EDITS = {
    "A": [
        (SPELLBOOK, "remove entry contract",
         "            - Otherwise the spell leaves `source_index` (which keeps its remaining\n"
         "              members) and becomes the sole member of a fresh inactive index. No\n"
         "              index is destroyed.\n",
         "            - Otherwise the spell leaves `source_index` (which keeps its remaining\n"
         "              members) and becomes the sole member of a fresh inactive index, which\n"
         "              is registered with the frame as `bind` registers the index it creates,\n"
         "              so the frame's lookups by spell_id find the spell there. No index is\n"
         "              destroyed.\n"),
        (SPELLBOOK, "seam summary",
         "        (`_inactive_spells`, `_spell_ids`, id pools, Nexus, fast-door, Creations)\n"
         "        is untouched. No index is destroyed -- the source keeps its remaining\n"
         "        members; the separated spell gets a fresh inactive index.\n",
         "        (`_inactive_spells`, `_spell_ids`, id pools, Nexus, fast-door, Creations)\n"
         "        is untouched. No index is destroyed -- the source keeps its remaining\n"
         "        members; the separated spell gets a fresh inactive index, registered with\n"
         "        the frame as `bind` registers the index it creates.\n"),
        (SPELLBOOK, "seam steps",
         "            3. Otherwise mint a fresh `SpellIndex` seeded with this spell id, remove\n"
         "               the spell from `source_index`, and repoint `spell.spell_index`.\n",
         "            3. Otherwise mint a fresh `SpellIndex` seeded with this spell id, remove\n"
         "               the spell from `source_index`, and repoint `spell.spell_index`.\n"
         "            4. Register the fresh index in the frame's spell registry the way a\n"
         "               post-conjure `bind` registers the index it creates: the same guard\n"
         "               (the Book is conjured) and the same call, under the Book's root\n"
         "               conduit. The frame's lookups by spell_id (the Aether conduit lookup,\n"
         "               a grant or transfer by spell_id, bind's collision guard,\n"
         "               MutationResearch residency) walk that registry. Until {notch}\n"
         "               (minted_index_registry) the index was never registered, so they all\n"
         "               missed the version, parked or later notched active there.\n"),
        (SPELLBOOK, "seam threading",
         "        Raises:\n"
         "            RuntimeError: If `spell` is not owned here, is active, or is not a\n"
         "                member of `source_index`.\n"
         "        \"\"\"\n"
         "        self.check_cleaned()\n"
         "        if spell._spellbook is not self:\n"
         "            self._logger.error(\n"
         "                f\"remove_from_spell_index: spell {spell.spell_id} is not owned by this spellbook.\",\n",
         "        Raises:\n"
         "            RuntimeError: If `spell` is not owned here, is active, or is not a\n"
         "                member of `source_index`.\n"
         "\n"
         "        Threading:\n"
         "            The move runs under the Book lock; the registration takes the frame\n"
         "            lock alone, after the Book lock is released, as bind's registration\n"
         "            and `_destroy_spell_index`'s unregistration do. No lock-order edge.\n"
         "        \"\"\"\n"
         "        self.check_cleaned()\n"
         "        if spell._spellbook is not self:\n"
         "            self._logger.error(\n"
         "                f\"remove_from_spell_index: spell {spell.spell_id} is not owned by this spellbook.\",\n"),
        (SPELLBOOK, "seam registration",
         "        with self._lock:\n"
         "            new_index = SpellIndex(initial_id=spell_id)\n"
         "            source_index.remove_member(spell_id)\n"
         "            spell.spell_index = new_index\n"
         "        if self._crystallizer.activated:\n",
         "        with self._lock:\n"
         "            new_index = SpellIndex(initial_id=spell_id)\n"
         "            source_index.remove_member(spell_id)\n"
         "            spell.spell_index = new_index\n"
         "        # Register the fresh index with the frame the way a post-conjure bind registers the index it creates: the\n"
         "        # same guard and the same call, under the Book's root conduit, so every lookup that walks the frame's\n"
         "        # spell registry finds the spell. Frame lock alone, after the Book lock. `_destroy_spell_index`\n"
         "        # unregisters the index when it empties, and the root's teardown with the rest\n"
         "        # (`_unregister_conduit_spells_from_aether`) (minted_index_registry, {notch}).\n"
         "        if self._conjured and self._conduit is not None:\n"
         "            Spellbook._aether._register_single_spell_index(\n"
         "                self._get_required_conduit_surface()._id,\n"
         "                new_index,\n"
         "                self._aetheric_frame_name,\n"
         "            )\n"
         "        if self._crystallizer.activated:\n"),
    ],
    "B": [
        (SPELLBOOK, "teardown unregistration",
         "        Remove this Spellbook's local spell indices from Aether for one conduit.\n"
         "\n"
         "        Args:\n"
         "            conduit_id:\n"
         "                Conduit id whose local spell indices should be removed from the\n"
         "                shared Aether registry.\n"
         "\n"
         "        Returns:\n"
         "            None.\n"
         "        \"\"\"\n"
         "        with self._lock:\n"
         "            spell_set = set(self._spells.keys())\n"
         "        if spell_set:\n",
         "        Remove this Spellbook's local spell indices from Aether for one conduit.\n"
         "\n"
         "        Contract:\n"
         "            - Removes every index this Book has registered: the indexes of its\n"
         "              active spells and, since {notch} (minted_index_registry), an index\n"
         "              that holds only parked versions (the one `remove_from_spell_index`\n"
         "              mints), so the frame keeps no entry for the torn-down root.\n"
         "\n"
         "        Args:\n"
         "            conduit_id:\n"
         "                Conduit id whose local spell indices should be removed from the\n"
         "                shared Aether registry.\n"
         "\n"
         "        Returns:\n"
         "            None.\n"
         "\n"
         "        Threading:\n"
         "            Collects the indexes under the Book lock, reading each parked\n"
         "            version's index through its cleanup-safe read (Book -> spell, the\n"
         "            order Book teardown takes), and removes them with the frame lock\n"
         "            alone after the Book lock is released.\n"
         "        \"\"\"\n"
         "        with self._lock:\n"
         "            spell_set = set(self._spells.keys())\n"
         "            # A parked version's index joins the set: an index that holds only parked versions - the one\n"
         "            # remove_from_spell_index mints - is registered too (minted_index_registry, {notch}). An index\n"
         "            # shared with an active version is already in it; a version cleaned meanwhile is skipped.\n"
         "            for parked_spell in self._inactive_spells.values():\n"
         "                parked_index = parked_spell._spell_index_unless_cleaned()\n"
         "                if parked_index is not None:\n"
         "                    spell_set.add(parked_index)\n"
         "        if spell_set:\n"),
    ],
    "C": [
        (RESEARCH, "residency verdicts",
         "            - `runtime` verdicts: `active` (some index's selected member),\n"
         "              `parked` (a live index member, not selected), `stored`\n",
         "            - `runtime` verdicts: `active` (some index's selected member that\n"
         "              its lineage tracks as current), `parked` (any other live index\n"
         "              member - a version moved into an index of its own stays parked\n"
         "              until a notch, though that index selects it), `stored`\n"),
        (RESEARCH, "membership contract",
         "            - Scans EVERY live frame: a selected (active) membership\n"
         "              anywhere wins over any unselected membership, honoring the\n"
         "              residency contract's active-if-any verdict rule.\n"
         "            - When no frame selects the identity, the first live unselected\n"
         "              membership (frame iteration order) is reported as parked.\n",
         "            - Scans EVERY live frame: an active membership anywhere wins\n"
         "              over any parked one, honoring the residency contract's\n"
         "              active-if-any verdict rule.\n"
         "            - Active means the index selects the identity AND the frame's\n"
         "              lineage registry tracks it as that index's current version\n"
         "              (`SpellSystemStates.get_by_index_id(...).current_spell_id`). The\n"
         "              index `remove_from_spell_index` mints selects its parked member\n"
         "              (activation takes a notch) and no lineage tracks that member\n"
         "              until a notch registers it, so it reads parked\n"
         "              (minted_index_registry, {notch}). The state is read by index id:\n"
         "              `get_by_spell_id` also answers a version a notch moved away from.\n"
         "            - When no frame holds the identity active, the first live\n"
         "              membership (frame iteration order) is reported as parked.\n"),
        (RESEARCH, "membership test",
         "            try:\n"
         "                if frame.cleaned:\n"
         "                    continue\n"
         "                index = frame.find_index_for_spell(spell_id)\n"
         "            except Exception:\n"
         "                continue\n"
         "            if index is None or index.cleaned:\n"
         "                continue\n"
         "            if index.selected_spell_id == spell_id:\n"
         "                return frame_name, index.id, True\n",
         "            try:\n"
         "                if frame.cleaned:\n"
         "                    continue\n"
         "                index = frame.find_index_for_spell(spell_id)\n"
         "                state = (\n"
         "                    None if index is None\n"
         "                    else frame.spell_system_states.get_by_index_id(index.id)\n"
         "                )\n"
         "                tracked = state is not None and state.current_spell_id == spell_id\n"
         "            except Exception:\n"
         "                continue\n"
         "            if index is None or index.cleaned:\n"
         "                continue\n"
         "            if tracked and index.selected_spell_id == spell_id:\n"
         "                return frame_name, index.id, True\n"),
    ],
    "D": [
        (SPELL, "cleanup-safe index read readers",
         "            racing `cleanup()`, which deletes `spell_index` - the parked branch\n"
         "            of `Spellbook._find_contracted_spell_by_id`, and the explicit index\n"
         "            steps that turn a spell found by spell_id into the spell its index\n"
         "            has active (the ownership transfer's spell_id handles and the\n"
         "            contract dependency walks). Until 0.2.8253 its first reader was the\n"
         "            parked branch of `Spellbook.find_spell_by_id`.\n",
         "            racing `cleanup()`, which deletes `spell_index` - the parked branch\n"
         "            of `Spellbook._find_contracted_spell_by_id`, the explicit index\n"
         "            steps that turn a spell found by spell_id into the spell its index\n"
         "            has active (the ownership transfer's spell_id handles and the\n"
         "            contract dependency walks), and the root's teardown, which\n"
         "            unregisters each parked version's index from the frame\n"
         "            (`Spellbook._unregister_conduit_spells_from_aether`,\n"
         "            minted_index_registry, {notch}). Until 0.2.8253 its first reader\n"
         "            was the parked branch of `Spellbook.find_spell_by_id`.\n"),
    ],
}


def main() -> None:
    """Apply the chosen edit groups in memory; write only with --apply."""
    args = sys.argv[1:]
    if (len(args) != 7 or args[0] != "--root" or args[2] != "--edits" or args[4] != "--notch"
            or args[6] not in ("--check", "--apply")):
        raise SystemExit(__doc__)
    root = pathlib.Path(args[1])
    groups = [group for group in args[3].split(",") if group]
    notch = args[5]
    if not re.fullmatch(r"0\.2\.82\d\d", notch):
        raise SystemExit("--notch must read 0.2.82NN, got %r" % notch)
    texts = {}
    endings = {}
    for group in groups:
        for rel, label, old, new in EDITS[group]:
            new = new.replace("{notch}", notch)
            if rel not in texts:
                raw = (root / rel).read_bytes()
                crlf = raw.count(b"\r\n")
                if crlf not in (0, raw.count(b"\n")):
                    raise SystemExit("mixed line endings in %s" % rel)
                endings[rel] = "\r\n" if crlf else "\n"
                texts[rel] = raw.decode("utf-8").replace("\r\n", "\n")
            for line in new.split("\n"):
                if len(line) > 120:
                    raise SystemExit("%s: line over 120 chars (%d)" % (label, len(line)))
            count = texts[rel].count(old)
            if count != 1:
                raise SystemExit("%s/%s: anchor found %d times" % (group, label, count))
            texts[rel] = texts[rel].replace(old, new)
    print("all anchors found:", ",".join(groups))
    if args[6] == "--apply":
        for rel, text in texts.items():
            data = text.replace("\n", endings[rel]).encode("utf-8")
            (root / rel).write_bytes(data)
            if (root / rel).read_bytes() != data:
                raise SystemExit("read-back mismatch: %s" % rel)
            print("applied", rel, "(CRLF kept)" if endings[rel] == "\r\n" else "(LF)")


main()
