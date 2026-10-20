"""S7 (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned): the edits to Spellbook's teardown.

Edits (each anchor must occur exactly once in src/melder/aether/spellbook/spellbook.py under --root):
  A  `_cleanup_spells`' docstring: the parked loop's contract and the threading note.
  B  `_cleanup_spells`: after the active loop, retire every parked version locally and clean the indexes only parked
     versions hold.
  C  `_cleanup_components`' docstring names them.
`{notch}` in the new texts is the version the landing takes. LF kept; the file is read back after writing.
Usage: apply_s7.py --root <tree> --notch 0.2.82NN --check | --apply
"""
import pathlib
import re
import sys

TARGET = "src/melder/aether/spellbook/spellbook.py"

A_OLD = '''        Clean up local spell objects and unregister their spell indexes.

        Contract:
            - Unregisters each local SpellIndex entry from SpellSystemStates.
            - Cleans Spell and SpellIndex instances (best-effort).
            - Logs cleanup errors and continues.

        Returns:
            None.
        """
        for spell_index, spell in self._spells.items():
'''
A_NEW = '''        Clean up local spell objects and unregister their spell indexes.

        Contract:
            - Unregisters each local SpellIndex entry from SpellSystemStates.
            - Cleans Spell and SpellIndex instances (best-effort).
            - Then retires every parked version (`_inactive_spells`) with the
              local teardown the parked branch of `_dispose_spell` runs
              (`_spellbook_cleanup` set, then `Spell.cleanup()`), and cleans
              every index only parked versions hold - one
              `remove_from_spell_index` minted; a shared index was cleaned with
              its active member above. A parked version holds no lineage
              registration, resolution-map entry or frame lookup of its own, and
              the root's teardown has already unregistered its index from the
              frame (`_unregister_conduit_spells_from_aether`), so nothing else
              is owed. (book_teardown_parked, {notch})
            - Logs cleanup errors and continues.

        Threading:
            Runs under the Spellbook lock (`_cleanup_components`); each spell's
            and each index's lock is taken under it, the order the active loop
            and conjure's ownership stamping already take.

        Returns:
            None.
        """
        for spell_index, spell in self._spells.items():
'''
B_OLD = '''            try:
                spell_index.cleanup()
            except Exception as e:
                self._logger.error(
                    f"Error cleaning spell index '{spell_index_label}': {e}",
                    "_cleanup_spells",
                    exc_info=True,
                )

    def cleanup_and_remove_spell(self, spell: Spell | str) -> None:
'''
B_NEW = '''            try:
                spell_index.cleanup()
            except Exception as e:
                self._logger.error(
                    f"Error cleaning spell index '{spell_index_label}': {e}",
                    "_cleanup_spells",
                    exc_info=True,
                )
        # Parked versions and the indexes only they hold (book_teardown_parked, {notch}). The loop above reaches an
        # index through its active member, so until {notch} a parked version - on a shared index, or alone in one
        # `remove_from_spell_index` minted - stayed uncleaned, and its direct `cleanup()` then routed to this
        # torn-down Book and raised. Each version's index is read while the version is live, then the version is
        # retired locally; an index no active member holds is cleaned after its versions.
        parked_only_indexes: dict[str, SpellIndex] = {}
        for spell_id, spell in self._inactive_spells.items():
            try:
                parked_index = spell.spell_index
                if parked_index not in self._spells:
                    parked_only_indexes[parked_index.id] = parked_index
                spell._spellbook_cleanup = True
                spell.cleanup()
            except Exception as e:
                self._logger.error(
                    f"Error cleaning parked spell '{spell_id}': {e}",
                    "_cleanup_spells",
                    exc_info=True,
                )
        for index_id, parked_index in parked_only_indexes.items():
            try:
                parked_index.cleanup()
            except Exception as e:
                self._logger.error(
                    f"Error cleaning parked-only spell index '{index_id}': {e}",
                    "_cleanup_spells",
                    exc_info=True,
                )

    def cleanup_and_remove_spell(self, spell: Spell | str) -> None:
'''
C_OLD = "            - Cleans local spells and SpellIndex instances.\n"
C_NEW = ("            - Cleans local spells and SpellIndex instances, the parked\n"
         "              versions and the indexes only they hold included\n"
         "              (`_cleanup_spells`).\n")
EDITS = (("A", A_OLD, A_NEW), ("B", B_OLD, B_NEW), ("C", C_OLD, C_NEW))


def main() -> None:
    """Apply the edits under --root; write only with --apply."""
    args = sys.argv[1:]
    if len(args) != 5 or args[0] != "--root" or args[2] != "--notch" or args[4] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    root, notch, mode = pathlib.Path(args[1]), args[3], args[4]
    if not re.fullmatch(r"0\.2\.82\d\d", notch):
        raise SystemExit("--notch must read 0.2.82NN")
    path = root / TARGET
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % TARGET)
    text = raw.decode("utf-8")
    for name, old, new in EDITS:
        if text.count(old) != 1:
            raise SystemExit("edit %s: anchor found %d times" % (name, text.count(old)))
        text = text.replace(old, new.replace("{notch}", notch))
    for line in text.split("\n"):
        if len(line) > 120 and "book_teardown_parked" in line:
            raise SystemExit("line over 120: " + line)
    print("%s: %d -> %d lines" % (TARGET, raw.count(b"\n"), text.count("\n")))
    if mode == "--apply":
        path.write_bytes(text.encode("utf-8"))
        if path.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
