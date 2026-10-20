"""S8: authored graph prose for the refused notch, read against the source before --accept (melder_1).

Spellbook gains one responsibility (a notch whose incoming version fails its structural check is refused with
nothing moved) and its authored edge to MutationResearch says a notch's promotion is recorded once the notch stands.
SpellbookValidationError gains one responsibility (the one-line preface). The other responsibilities of both nodes
were re-read against spellbook.py and spellbook_validation_error.py after the edit; it changes none of them. Writes
the descriptors as the extractor does (indent=1, LF). Usage (repository root): graph_prose_s8.py --check | --apply
"""
import json
import pathlib
import sys

GRAPH = pathlib.Path("context_compass/system_docs/graph/melder")
BOOK = GRAPH / "aether/spellbook/spellbook.json"
BOOK_NODE = "melder.aether.spellbook.spellbook.Spellbook"
ERROR = GRAPH / "utilities/custom_exceptions/spellbook_validation_error.json"
ERROR_NODE = "melder.utilities.custom_exceptions.spellbook_validation_error.SpellbookValidationError"
RESEARCH = "melder.mutation_research.mutation_research.MutationResearch"
BOOK_NEW = ("refuses a notch whose incoming version fails its structural check with nothing moved: _notch_spell runs "
            "phases 1-4 for a version never compiled once it is active, inside the held window "
            "(_check_notched_version), and on a failure puts the structure back before it raises - the seam run back "
            "toward the outgoing version, the lineage's dependencies and topology registered again, a refused "
            "version's own key set back (_revert_refused_notch) - with SpellbookValidationError prefaced by the "
            "refusal line; a standing notch journals its promotion after the check (0.2.8262)")
OLD_WHY = ("The bind, bind_inactive, and notch confirmation seams auto-record world-entry/staged/promoted research "
           "events through a non-constructing peek at the Aether-hosted root (quiet no-op while research is "
           "inactive).")
NEW_WHY = ("The bind, bind_inactive, and notch confirmation seams auto-record world-entry/staged/promoted research "
           "events through a non-constructing peek at the Aether-hosted root (quiet no-op while research is "
           "inactive); a notch's promotion is recorded by its entry once the notch stands, so a refused notch "
           "records nothing (0.2.8262).")
ERROR_NEW = ("puts an optional one-line preface before the message (keyword-only preface=), checked before anything "
             "renders - a non-str, empty or multi-line preface raises TypeError; a refused notch passes the refusal "
             "line (0.2.8262)")


def load(path: pathlib.Path) -> dict:
    """Read a descriptor, refusing CRLF."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path)
    return json.loads(raw.decode("utf-8"))


def main() -> None:
    """Append the two responsibilities and rewrite the edge's why once; write only with --apply."""
    args = sys.argv[1:]
    if args not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    book = load(BOOK)
    items = book["nodes"][BOOK_NODE]["responsibilities"]
    if BOOK_NEW in items:
        raise SystemExit("Spellbook already applied")
    items.append(BOOK_NEW)
    edges = [e for e in book["edges_authored"] if e["from"] == BOOK_NODE and e["to"] == RESEARCH]
    if len(edges) != 1 or edges[0]["why"] != OLD_WHY:
        raise SystemExit("the Spellbook -> MutationResearch edge is not as read")
    edges[0]["why"] = NEW_WHY
    error = load(ERROR)
    error_items = error["nodes"][ERROR_NODE]["responsibilities"]
    if ERROR_NEW in error_items:
        raise SystemExit("SpellbookValidationError already applied")
    error_items.append(ERROR_NEW)
    print(BOOK_NODE, "responsibilities:", len(items), "| edge why rewritten")
    print(ERROR_NODE, "responsibilities:", len(error_items))
    if args[0] == "--apply":
        for path, data in ((BOOK, book), (ERROR, error)):
            text = json.dumps(data, indent=1) + "\n"
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: %s" % path)
        print("applied")


main()
