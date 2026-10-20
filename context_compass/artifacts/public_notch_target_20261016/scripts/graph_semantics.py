"""Graph semantics for public_notch_target_2026_10_16 (0.2.8249).

Run from the repository root: python <this file> [--dry-run]

- `Conduit` was already SEMANTICS_STALE before this lane (its stamp predates earlier conduit.py lanes), so, as S8 did
  for nodes already stale, the lane's fact is appended and the node is NOT accepted: its older claims were not
  re-verified here.
Every edit asserts the state it expects, so a second run refuses instead of duplicating. Writes descriptors the way the
extractor does (indent=1, LF).
"""
import json
import pathlib
import sys

GRAPH = pathlib.Path("context_compass/system_docs/graph")
DRY = "--dry-run" in sys.argv
CONDUIT = "melder.aether.conduit.conduit.Conduit"

EDITS = [
    ("melder/aether/conduit/conduit.json", CONDUIT, "append", None,
     "names a notch's target by spell_id - the id bind or bind_inactive returned - or by spell, exactly one; resolves an"
     " id through the Book's _get_owned_spell to the exact owned version, active or parked; and refuses a version the"
     " Book does not own or one of another index before the notch transaction and again inside its seal, so a refused"
     " notch moves nothing (notch_spell, _resolve_notch_target, _owned_notch_target, 0.2.8249)"),
]


def main() -> None:
    """Apply every edit, refusing any whose expected state does not hold."""
    touched = {}
    for rel, node_id, kind, old, new in EDITS:
        path = GRAPH / rel
        data = touched.get(path) or json.loads(path.read_text(encoding="utf-8"))
        node = data["nodes"][node_id]
        items = list(node.get("responsibilities") or [])
        if new in items:
            raise SystemExit(f"already applied: {node_id}")
        if kind == "replace":
            if items.count(old) != 1:
                raise SystemExit(f"{node_id}: expected one responsibility {old[:60]!r}")
            items[items.index(old)] = new
        else:
            items.append(new)
        node["responsibilities"] = items
        touched[path] = data
        print(("DRY " if DRY else "") + f"{kind:7} {node_id}")
    if not DRY:
        for path, data in touched.items():
            path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("descriptors", len(touched))


if __name__ == "__main__":
    main()
