"""S1: authored graph prose for the destroy seam, read against the source before --accept (melder_1).

Spellbook gains one responsibility: destroying an index a parked member left empty touches no other spell's binding
signature. Its other responsibilities were re-read against spellbook.py after the edit; the edit changes none of
them. Writes the descriptor as the extractor does (indent=1, LF). Usage (repository root): graph_prose_s1.py
--check | --apply
"""
import json
import pathlib
import sys

BOOK = pathlib.Path("context_compass/system_docs/graph/melder/aether/spellbook/spellbook.json")
BOOK_NODE = "melder.aether.spellbook.spellbook.Spellbook"
BOOK_NEW = ("destroys an index a parked member left empty without touching another spell's binding signature: "
            "_destroy_spell_index drops the Book route only when it routes the key to that index and releases only "
            "the departing member's frame claim, by spell_id, so staging, an index move back and a lone parked "
            "disposal keep the active version's claim and route (0.2.8263)")


def main() -> None:
    """Append the responsibility once; write only with --apply."""
    args = sys.argv[1:]
    if args not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    raw = BOOK.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % BOOK)
    book = json.loads(raw.decode("utf-8"))
    items = book["nodes"][BOOK_NODE]["responsibilities"]
    if BOOK_NEW in items:
        raise SystemExit("Spellbook already applied")
    items.append(BOOK_NEW)
    print(BOOK_NODE, "responsibilities:", len(items))
    if args[0] == "--apply":
        text = json.dumps(book, indent=1) + "\n"
        BOOK.write_bytes(text.encode("utf-8"))
        if BOOK.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
