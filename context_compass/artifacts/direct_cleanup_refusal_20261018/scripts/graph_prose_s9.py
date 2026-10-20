"""S9 (0.2.8256): authored prose of the Spellbook and Spell graph nodes, read against the source before --accept.

Spellbook: responsibility 20 said the managed options "become part of the spell id", false since 0.2.8254 (the
settings left the fingerprint); a new responsibility states the 0.2.8256 refusal. Spell: a new responsibility
states what a direct cleanup of such a member does. Writes the descriptors as the extractor does (indent=1, LF).
Usage (repository root): graph_prose_s9.py --check | --apply
"""
import json
import pathlib
import sys

GRAPH = pathlib.Path("context_compass/system_docs/graph/melder/aether/spellbook")
OLD_20 = ("forwards a managed binding's four options through bind and bind_inactive to Bind, where they are validated "
          "and become part of the spell id; a parked managed version keeps its own (0.2.8242)")
NEW_20 = ("forwards a managed binding's four options through bind and bind_inactive to Bind, where they are validated "
          "(0.2.8242); they are the spell's settings, not part of its spell id (0.2.8254), and a parked managed "
          "version keeps its own")
NEW_BOOK = ("refuses the active member of an index that also holds parked versions in cleanup_and_remove_spell - and "
            "so a direct Spell.cleanup() - before anything is unregistered, as _dispose_spell refuses it for "
            "cleanup_spell, every message naming the remedies (notch the index to a parked version, dispose the "
            "parked versions, or move them out with remove_from_spell_index); a sole member is removed with its "
            "index, and Book teardown never meets the check (0.2.8256)")
NEW_SPELL = ("a direct cleanup of the active version of an index that also holds parked versions raises the Book's "
             "refusal and leaves the spell as it was (Spellbook.cleanup_and_remove_spell, 0.2.8256)")


def edit(name: str, node_id: str, apply: bool, change) -> None:
    path = GRAPH / name
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in " + name)
    data = json.loads(raw.decode("utf-8"))
    node = data["nodes"][node_id]
    change(node["responsibilities"])
    text = json.dumps(data, indent=1) + "\n"
    print(name, node_id, "responsibilities:", len(node["responsibilities"]))
    if apply:
        path.write_bytes(text.encode("utf-8"))
        if path.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch " + name)


def book(items: list) -> None:
    if items.count(OLD_20) != 1:
        raise SystemExit("responsibility 20 not found once")
    if NEW_BOOK in items:
        raise SystemExit("already applied")
    items[items.index(OLD_20)] = NEW_20
    items.append(NEW_BOOK)


def spell(items: list) -> None:
    if NEW_SPELL in items:
        raise SystemExit("already applied")
    items.append(NEW_SPELL)


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    apply = mode == "--apply"
    edit("spellbook.json", "melder.aether.spellbook.spellbook.Spellbook", apply, book)
    edit("spell.json", "melder.aether.spellbook.spell.Spell", apply, spell)
    print("applied" if apply else "checked")


main()
