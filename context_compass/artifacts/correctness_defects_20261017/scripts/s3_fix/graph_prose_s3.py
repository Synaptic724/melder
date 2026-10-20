"""S3: authored prose of the Conduit, Spellbook and ConduitWard graph nodes for the contract release (melder_0).

Each node gains one responsibility for `cleanup_spell`'s contract release (0.2.8261). The descriptors are written as
the extractor writes them (indent=1, LF); a round trip of each unchanged file must reproduce its bytes first.
Spellbook was AUTHORED at 0.2.8260 and its other 28 responsibilities were re-read against spellbook.py after the edit,
which changes none of them, so it is accepted afterwards (graph_walker --accept). Conduit and ConduitWard were
SEMANTICS_STALE before this lane (HEAD) and stay so: their prose gains the responsibility, a full re-read is not part
of S3. Usage (repository root): graph_prose_s3.py --check | --apply
"""
import json
import pathlib
import sys

BASE = pathlib.Path("context_compass/system_docs/graph/melder/aether")
ADDITIONS = (
    (BASE / "conduit/conduit.json", "melder.aether.conduit.conduit.Conduit",
     "takes a version out of every contract of its Book's root conduit before the Book disposes it: hands the root "
     "ward's _emit_spell_disposed to Spellbook._dispose_spell as release_contracts, from the root or a lesser of its "
     "lineage, and emits an index destroy with no member id when the index went too; the Spellbook's own cleanup_spell "
     "comes here once conjured (cleanup_spell, 0.2.8261)"),
    (BASE / "spellbook/spellbook.json", "melder.aether.spellbook.spellbook.Spellbook",
     "routes cleanup_spell through its root conduit's cleanup_spell once conjured, and _dispose_spell calls the "
     "caller's release_contracts hook with the spell_id after its decision and refusals and before anything is "
     "invalidated or disposed, with no Book lock held; a raising hook disposes nothing and the in-flight mark is "
     "cleared (0.2.8261)"),
    (BASE / "conduit/conduit_ward/conduit_ward.json", "melder.aether.conduit.conduit_ward.conduit_ward.ConduitWard",
     "releases a disposed version from every contract whose owner side holds its Detail - an index link's member "
     "Detail or a version grant, with the borrower's entry, active or parked, and its borrowed id - under its own "
     "lock, before the Book disposes it, and emits each changed contract's record afterwards (_emit_spell_disposed, "
     "0.2.8261)"),
)


def main() -> None:
    """Append each responsibility once; write only with --apply."""
    args = sys.argv[1:]
    if args not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    staged = []
    for path, node, text in ADDITIONS:
        raw = path.read_bytes()
        if b"\r" in raw:
            raise SystemExit(f"CR in {path}")
        data = json.loads(raw.decode("utf-8"))
        if json.dumps(data, indent=1) + "\n" != raw.decode("utf-8"):
            raise SystemExit(f"round trip differs for {path}")
        items = data["nodes"][node]["responsibilities"]
        if text in items:
            raise SystemExit(f"already applied: {node}")
        items.append(text)
        staged.append((path, json.dumps(data, indent=1) + "\n"))
        print(node, "responsibilities:", len(items))
    if args[0] == "--apply":
        for path, out in staged:
            path.write_bytes(out.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != out:
                raise SystemExit(f"read-back mismatch {path}")
        print("applied")


main()
