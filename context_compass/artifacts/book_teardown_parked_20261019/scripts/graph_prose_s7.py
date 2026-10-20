"""S7: authored prose of the Spellbook graph node, read against the source before --accept (melder_1).

Spellbook gains one responsibility: its teardown retires the parked versions and cleans the indexes only they hold
(`_cleanup_spells`). Its other 27 responsibilities were re-read against spellbook.py after the edit; the edit changes
none of them. Writes the descriptor as the extractor does (indent=1, LF).
Usage (repository root): graph_prose_s7.py --check | --apply
"""
import json
import pathlib
import sys

DESCRIPTOR = pathlib.Path("context_compass/system_docs/graph/melder/aether/spellbook/spellbook.json")
NODE = "melder.aether.spellbook.spellbook.Spellbook"
NEW = ("retires every parked version at Book teardown with the local teardown cleanup_spell's parked branch runs "
       "(_spellbook_cleanup set, then Spell.cleanup()) and then cleans every index only parked versions hold, one "
       "remove_from_spell_index minted, after the active loop; each step best-effort and logged (_cleanup_spells, "
       "0.2.8260)")


def main() -> None:
    """Append the responsibility once; write only with --apply."""
    args = sys.argv[1:]
    if args not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    raw = DESCRIPTOR.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in the descriptor")
    data = json.loads(raw.decode("utf-8"))
    items = data["nodes"][NODE]["responsibilities"]
    if NEW in items:
        raise SystemExit("already applied")
    items.append(NEW)
    text = json.dumps(data, indent=1) + "\n"
    print(NODE, "responsibilities:", len(items))
    if args[0] == "--apply":
        DESCRIPTOR.write_bytes(text.encode("utf-8"))
        if DESCRIPTOR.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
