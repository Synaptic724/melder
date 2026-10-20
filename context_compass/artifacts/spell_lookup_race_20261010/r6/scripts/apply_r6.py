"""Apply R6 (find_spell_by_id from the Book's id maps) to a tree; keeps each file's line endings."""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])

NEW_FIND = '''    def find_spell_by_id(self, spell_id: str) -> Spell | None:
        """
        Public API

        Return the local spell whose index owns `spell_id`, or None.

        Purpose:
            Resolve any id in a spell's version lineage back to the live
            `Spell` object that currently represents it.

        Contract:
            - Searches THIS spellbook's registry only. Spells reachable through
              contracted conduits or through other books in the frame are not
              consulted; `inspect_spell` is the frame-wide search.
            - Answers from the Book's id maps and never walks `_spells`. The
              current version id of every owned lineage is a key of
              `_spells_by_id`; every superseded or parked version is a key of
              `_inactive_spells` (a notch parks the outgoing version there,
              index moves and parked disposal keep it in step, and ownership
              transfer migrates the whole lineage). A superseded or parked id
              therefore still resolves - to the live spell of the index that
              holds it, the spell as it exists NOW, not the state that version
              described.
            - O(1): at most three dict reads and one lock-guarded attribute read.
            - Returns None on a miss. This is deliberately unlike the
              `find_spell_index` / `find_spell_key` siblings, which raise on a
              miss; a None here means "no local index claims this id", not
              "lookup failed". A parked version whose index has no active member
              (a fresh index split off by `remove_from_spell_index`) also
              answers None.
            - Pure lookup: creates, registers, and mutates nothing.

        Threading:
            Does not acquire `self._lock`, by design: conjure holds that lock
            while it waits on phase workers and runs conduit hooks, and both can
            call this lookup from another thread. Each map read is one atomic
            dict operation and no live map is iterated, so a concurrent bind,
            removal, notch, index move or transfer can never make this raise or
            skip a registered spell. A notch, and a transfer between its flip
            and its inactive-member migration, move ids between maps in steps;
            a lookup that lands between two steps answers None for that
            lineage, so answers are not linearized against writers. An index
            move only repoints a parked version's index, so a lookup racing it
            answers as before the move or as after it.
            The parked branch reads the parked spell's index through
            `Spell._spell_index_unless_cleaned`, under that spell's own lock, so a
            version disposed concurrently answers None instead of raising.
            The returned `Spell` is a borrowed reference, not a lease: a
            concurrent removal, notch or transfer can retire or move it after
            this returns.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Args:
            spell_id:
                Any id belonging to the target spell's version lineage.

        Returns:
            Optional[Spell]:
                The owning spell, or None when no local index claims the id.

        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        self.check_cleaned()
        # Current version: one atomic read of the active-id map.
        spell = self._spells_by_id.get(spell_id)
        if spell is not None:
            return spell
        # Superseded or parked version: the parked spell names its index, and that
        # index's live spell is the answer. Reading the index under the parked
        # spell's lock turns a concurrent disposal into a miss instead of an error.
        parked = self._inactive_spells.get(spell_id)
        if parked is None:
            return None
        spell_index = parked._spell_index_unless_cleaned()
        if spell_index is None:
            return None
        return self._spells.get(spell_index)
'''

NEW_ACCESSOR = '''    def _spell_index_unless_cleaned(self) -> Optional[SpellIndex]:
        """
        Internal

        Return this spell's SpellIndex, or None once the spell has been cleaned.

        Purpose:
            Let a lock-free reader that already holds this Spell - the parked
            branch of `Spellbook.find_spell_by_id` - read its index without
            racing `cleanup()`, which deletes `spell_index`.

        Contract:
            - Returns the index the spell belongs to while the spell is live, and
              None after `cleanup()` has run. Never raises for a cleaned spell,
              unlike a direct `spell_index` read.
            - Pure read: creates, registers, and mutates nothing.

        Threading:
            Takes `self._lock`, the lock `cleanup()` sets `_cleaned` and deletes
            `spell_index` under, so the check and the read cannot interleave with
            a concurrent cleanup; `cleanup()` keeps `_lock`, so the read works on
            a cleaned spell too. Holds no other lock and calls nothing while it
            holds this one. Index moves repoint `spell_index` under the Spellbook
            lock, not this one; a read racing a move returns the old or the new
            index.

        Returns:
            Optional[SpellIndex]:
                The spell's index, or None when the spell is cleaned.
        """
        with self._lock:
            if self._cleaned:
                return None
            return self.spell_index

'''


def edit(relative: str, transform) -> None:
    path = ROOT / relative
    data = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in data
    text = data.replace("\r\n", "\n") if crlf else data
    if "\r" in text:
        raise SystemExit(f"{relative}: stray CR")
    text = transform(text)
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print(f"{relative}: edited ({'CRLF' if crlf else 'LF'} kept)")


def replace_find(text: str) -> str:
    start_marker = "    def find_spell_by_id(self, spell_id: str) -> Spell | None:\n"
    end_marker = ("            if spell_index.has_spell(spell_id):\n"
                  "                return spell\n\n        return None\n")
    if text.count(start_marker) != 1:
        raise SystemExit("find_spell_by_id start not unique")
    start = text.index(start_marker)
    end = text.index(end_marker, start) + len(end_marker)
    body = text[start:end]
    if "for spell_index, spell in self._spells.items():" not in body or body.count("    def ") != 1:
        raise SystemExit("unexpected find_spell_by_id body")
    return text[:start] + NEW_FIND + text[end:]


def insert_accessor(text: str) -> str:
    anchor = "    def _cleanup_creation_context(self) -> None:\n"
    if text.count(anchor) != 1 or "_spell_index_unless_cleaned" in text:
        raise SystemExit("accessor anchor not unique or accessor present")
    return text.replace(anchor, NEW_ACCESSOR + anchor, 1)


edit("src/melder/aether/spellbook/spellbook.py", replace_find)
def fix_cleanup_lock_doc(text: str) -> str:
    stale = ("            - Sets `_cleaned` before the guarded section exits, then drops the\n"
             "              `_lock` reference itself after the teardown completes.\n")
    fixed = ("            - Sets `_cleaned` before the guarded section exits. `_lock` is kept,\n"
             "              not deleted with the other fields, so a lock-guarded reader such as\n"
             "              `_spell_index_unless_cleaned` can still take it on a cleaned spell.\n")
    if text.count(stale) != 1:
        raise SystemExit("Spell.cleanup lock sentence not unique")
    return text.replace(stale, fixed, 1)


def insert_accessor_and_fix_doc(text: str) -> str:
    return fix_cleanup_lock_doc(insert_accessor(text))


edit("src/melder/aether/spellbook/spell.py", insert_accessor_and_fix_doc)
