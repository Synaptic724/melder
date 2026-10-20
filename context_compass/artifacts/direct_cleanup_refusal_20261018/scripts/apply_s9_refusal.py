"""S9's src edits for the owner's pick (2026-10-18): `cleanup_and_remove_spell` refuses the active member of an index
that also holds parked versions, `_dispose_spell`'s refusal names the same remedies, and the docstrings of
`cleanup_and_remove_spell`, `cleanup_spell` and `Spell.cleanup` say so.

Modes:
  --check   every anchor occurs exactly once in the repository files (read-only)
  --diff    write patched copies under /tmp/cc_res/s9_preview and print a unified diff (read-only for the repo)
  --apply   write the repository files (only after the owner's word on these exact edits); LF kept; read back
"""
import difflib
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[4]
SPELLBOOK = REPO / "src/melder/aether/spellbook/spellbook.py"
SPELL = REPO / "src/melder/aether/spellbook/spell.py"
PREVIEW = pathlib.Path("/tmp/cc_res/s9_preview")

SPELLBOOK_EDITS = [
    ("E1 the check", """            if target_spell._cleaned:
                return

            target_spell_index = target_spell.spell_index
            target_lookup_key = target_spell.key
""", """            if target_spell._cleaned:
                return

            target_spell_index = target_spell.spell_index
            # The active member of an index that still holds parked versions is refused, as cleanup_spell refuses
            # it: removing it here would clean the index under those versions, where no later call reaches them.
            # Book teardown and the parked disposal never route here - they set _spellbook_cleanup first - so this
            # refuses only a caller's removal (direct_cleanup_refusal, 0.2.8256).
            if not target_spell_index.is_sole_member(target_spell_id):
                refusal = (
                    f"Spellbook cannot remove spell {target_spell_id}: it is the active member of a multi-member "
                    f"index, and disposing it would leave the index's parked versions without an active one. Notch "
                    f"the index to one of them, dispose them with cleanup_spell, or move them out with "
                    f"remove_from_spell_index first."
                )
                self._logger.error(refusal, "cleanup_and_remove_spell", exc_info=True)
                raise RuntimeError(refusal)
            target_lookup_key = target_spell.key
"""),
    ("E2 Contract", """            - Accepts either a live `Spell` or its current `spell_id`.
            - Supports only locally owned spells in this Spellbook.
""", """            - Accepts either a live `Spell` or its current `spell_id`.
            - Supports only locally owned spells in this Spellbook.
            - Refuses the active member of an index that also holds parked
              versions (`SpellIndex.is_sole_member` False) before anything is
              unregistered, as `cleanup_spell` refuses it, and changes nothing.
              The sole member of an index is removed with its index. Book
              teardown and the parked disposal never reach this method.
"""),
    ("E3 Raises", """            RuntimeError:
                If the spell is not found locally or is not owned by this
                Spellbook.
""", """            RuntimeError:
                If the spell is not found locally or is not owned by this
                Spellbook.
            RuntimeError:
                If the spell is the active member of an index that also holds
                parked versions; nothing changes. Notch the index to one of
                them, dispose them with `cleanup_spell`, or move them out with
                `remove_from_spell_index` first.
"""),
    ("E4 Threading", """            Resolves the spell, unregisters its index and drops it from `_spells`
            and `_lookup_spells` under the Spellbook lock; releases the lock for
""", """            Resolves the spell, refuses an active member whose index holds
            parked versions (the index's membership is read under the index
            lock inside the Spellbook lock - Spellbook -> index, the order
            `_dispose_spell` takes, so no new edge), unregisters its index and
            drops it from `_spells` and `_lookup_spells` under the Spellbook
            lock; releases the lock for
"""),
    ("E5 cleanup_spell's message", """                raise RuntimeError(
                    f"cleanup_spell: spell {spell_id} is the active member of a multi-member "
                    f"index; notch away from it before disposing it."
                )
""", """                raise RuntimeError(
                    f"cleanup_spell: spell {spell_id} is the active member of a multi-member index, and disposing "
                    f"it would leave the index's parked versions without an active one. Notch the index to one of "
                    f"them, dispose them with cleanup_spell, or move them out with remove_from_spell_index first."
                )
"""),
    ("E6 cleanup_spell's Contract", """            - The ACTIVE member of a MULTI-member index cannot be disposed
              directly (it would leave the index headless); notch away from it
              first. The sole member of an index may always be disposed -- the
              index is destroyed with it.
""", """            - The ACTIVE member of a MULTI-member index cannot be disposed
              (it would leave the index's parked versions without an active
              one): notch the index to one of them, dispose them with
              `cleanup_spell`, or move them out with `remove_from_spell_index`
              first. `cleanup_and_remove_spell`, and so a direct
              `Spell.cleanup()`, refuses it the same way. The sole member of an
              index may always be disposed -- the index is destroyed with it.
"""),
]
SPELL_EDITS = [
    ("E7 Spell.cleanup's Raises", """            RuntimeError: On a direct call, from
                `Spellbook.cleanup_and_remove_spell`: the spell is not its Book's
                current active version (a parked version, for one), or the Book
                has been cleaned and did not clean this spell.
""", """            RuntimeError: On a direct call, from
                `Spellbook.cleanup_and_remove_spell`: the spell is not its Book's
                current active version (a parked version, for one); it is the
                active version of an index that also holds parked versions
                (nothing changes: notch the index to one of them, dispose them
                with `cleanup_spell`, or move them out with
                `remove_from_spell_index` first); or the Book has been cleaned
                and did not clean this spell.
"""),
]


def patched(path: pathlib.Path, edits: list) -> tuple:
    """Return (original text, patched text) for one file; every anchor must occur exactly once."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path.name)
    original = raw.decode("utf-8")
    text = original
    for label, old, new in edits:
        count = text.count(old)
        if count != 1:
            raise SystemExit("%s: anchor %s found %d times" % (path.name, label, count))
        for line in new.split("\n"):
            if len(line) > 120:
                raise SystemExit("%s: %s has a line over 120 chars" % (path.name, label))
        text = text.replace(old, new)
    return original, text


def main() -> None:
    """Check, preview or apply the edits."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--diff", "--apply"):
        raise SystemExit(__doc__)
    plan = [(SPELLBOOK, SPELLBOOK_EDITS), (SPELL, SPELL_EDITS)]
    results = [(path,) + patched(path, edits) for path, edits in plan]
    print("all anchors found")
    if sys.argv[1] == "--diff":
        PREVIEW.mkdir(parents=True, exist_ok=True)
        for path, original, text in results:
            rel = str(path.relative_to(REPO))
            (PREVIEW / path.name).write_text(text, encoding="utf-8", newline="\n")
            sys.stdout.writelines(difflib.unified_diff(original.splitlines(keepends=True),
                                                       text.splitlines(keepends=True), "a/" + rel, "b/" + rel))
    if sys.argv[1] == "--apply":
        for path, original, text in results:
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch in %s" % path.name)
        print("applied")


main()
