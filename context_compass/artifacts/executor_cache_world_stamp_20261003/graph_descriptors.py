"""Append the world-stamp responsibilities to the two authored descriptors (run after extract_graph.py)."""
import json
import pathlib
import sys

GRAPH = pathlib.Path(sys.argv[1]).resolve()
EDITS = {
    "melder/utilities/caching_system/caching_system.json": (
        "CachingSystem",
        "carries the executor-tier world stamp in the envelope (generation 19): set_world_stamp records it after "
        "staging and reports a change; a loaded bundle without the field is unstamped and never admits a full hit",
    ),
    "melder/aether/spellbook/spellbook_creation_system.json": (
        "SpellbookCreationSystem",
        "admits an executor-cache full hit only when the bundle's recorded world stamp equals the live structural "
        "world stamp (generation 19); a world that differs by an existing creation or a non-resolvable definition "
        "recompiles phases 8-11 and re-stages the bundle under the new stamp",
    ),
}
for rel, (label, line) in EDITS.items():
    path = GRAPH / rel
    raw = path.read_text(encoding="utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    data = json.loads(raw)
    hits = [n for n in data["nodes"].values() if n["label"] == label]
    assert len(hits) == 1, (rel, label, len(hits))
    node = hits[0]
    assert line not in node["responsibilities"], "already present"
    node["responsibilities"].append(line)
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text.replace("\n", newline), encoding="utf-8", newline="")
    print("edited", rel, node["id"])
