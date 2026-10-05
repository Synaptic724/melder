"""Append the owner-store-constant responsibility to the SitePlanEmission descriptor (run after extract_graph.py)."""
import json
import pathlib
import sys

GRAPH = pathlib.Path(sys.argv[1]).resolve()
EDITS = {
    "melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.json": (
        "SitePlanEmission",
        "binds an automatic world's unique-site owner store as a plan constant (owner-store constants, 2026-10-03): "
        "_owner_store_constant admits a unique site whose provider spell is owned by an automatic conduit and has an "
        "owner store; _emit_shared_hit then binds c{i} in the namespace and emits no alias line, while dynamic, "
        "unowned and meld.<store> sites keep the per-creation read and the miss keeps its c{i} parameter",
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
