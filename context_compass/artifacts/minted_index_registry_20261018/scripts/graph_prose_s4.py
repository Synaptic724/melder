"""S4: authored prose of the Spellbook and MutationResearch graph nodes, read against the source before --accept.

Spellbook gains a responsibility for the minted index's registration and its removal at the root's teardown;
MutationResearch's residency responsibility gains the lineage condition. Spell's change is a docstring (edit D), so
its prose stands and its node is only re-read and accepted. Writes the descriptors as the extractor does
(indent=1, LF).
Usage (repository root): graph_prose_s4.py --notch 0.2.82NN --check | --apply
"""
import json
import pathlib
import re
import sys

GRAPH = pathlib.Path("context_compass/system_docs/graph/melder")
NEW_BOOK = ("registers the index remove_from_spell_index mints in the frame's spell registry as a post-conjure bind "
            "registers the index it creates (bind's guard and call, under the Book's root conduit), and the root's "
            "teardown (_unregister_conduit_spells_from_aether) unregisters the indexes that hold only parked versions "
            "with the rest, so the frame's lookups by spell_id find a version moved into an index of its own ({N})")
OLD_RESIDENCY = ("residency_view = the query-time active/parked/stored join (frame scan + custody probe; total read)")
NEW_RESIDENCY = ("residency_view = the query-time active/parked/stored join (frame scan + custody probe; total read); "
                 "a version is active only when its index selects it and the frame's lineage registry tracks it as "
                 "that index's current version, so a version moved into an index of its own reads parked until a "
                 "notch ({N})")


def edit(rel: str, node_id: str, apply: bool, change) -> None:
    path = GRAPH / rel
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in " + rel)
    data = json.loads(raw.decode("utf-8"))
    node = data["nodes"][node_id]
    change(node["responsibilities"])
    text = json.dumps(data, indent=1) + "\n"
    print(rel, node_id, "responsibilities:", len(node["responsibilities"]))
    if apply:
        path.write_bytes(text.encode("utf-8"))
        if path.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch " + rel)


def main() -> None:
    args = sys.argv[1:]
    if len(args) != 3 or args[0] != "--notch" or args[2] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    notch = args[1]
    if not re.fullmatch(r"0\.2\.82\d\d", notch):
        raise SystemExit("--notch must read 0.2.82NN")
    apply = args[2] == "--apply"
    new_book = NEW_BOOK.replace("{N}", notch)
    new_residency = NEW_RESIDENCY.replace("{N}", notch)

    def book(items: list) -> None:
        if new_book in items:
            raise SystemExit("Spellbook already applied")
        items.append(new_book)

    def research(items: list) -> None:
        if items.count(OLD_RESIDENCY) != 1:
            raise SystemExit("residency responsibility not found once")
        items[items.index(OLD_RESIDENCY)] = new_residency

    edit("aether/spellbook/spellbook.json", "melder.aether.spellbook.spellbook.Spellbook", apply, book)
    edit("mutation_research/mutation_research.json", "melder.mutation_research.mutation_research.MutationResearch",
         apply, research)
    print("applied" if apply else "checked")


main()
