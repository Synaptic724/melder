"""Graph descriptors for the removal fix and its notch (melder_1, 2026-10-16).

usage (from the repository root): python <this script> <scratch graph dir> [--check]
Takes the re-extracted descriptors of the two src files this lane changed since the last assembly - spellbook.py
(the fix) and __version__.py (the 0.2.8251 notch) - from a scratch extraction over the real src (the extractor owns
their mechanical fields; every other descriptor stays as it is), refusing unless each differs from the real one only
in source_sha256 and span_sha256. Then appends one authored responsibility to the Spellbook node; the node is
accepted afterwards with graph_walker --accept, once its source was re-read. Writes JSON the way the extractor does
(indent=1, LF).
"""
import json
import pathlib
import sys

SCRATCH = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]
G = pathlib.Path("context_compass/system_docs/graph")
FILES = ["melder/aether/spellbook/spellbook.json", "melder/__version__.json"]
RESPONSIBILITY = (
    "removes a borrowed copy by the spell_id it is given: the active copy only when that copy's own spell_id is it, "
    "otherwise the parked copy, raising RuntimeError when it holds neither - never by index membership, so an index "
    "unlink after a notch completes in any member order (_remove_contracted_spell, 0.2.8251)"
)


def diffs(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(path + "/" + k)
            else:
                out.extend(diffs(a[k], b[k], path + "/" + k))
    elif a != b:
        out.append(path)
    return out


for rel in FILES:
    real = json.loads((G / rel).read_text(encoding="utf-8"))
    new = json.loads((SCRATCH / rel).read_text(encoding="utf-8"))
    changed = diffs(real, new)
    assert changed and all(p.endswith("/source_sha256") or p.endswith("/span_sha256") for p in changed), (rel, changed)
    if rel.endswith("spellbook.json"):
        node = new["nodes"]["melder.aether.spellbook.spellbook.Spellbook"]
        assert not any("_remove_contracted_spell" in r for r in node["responsibilities"]), node["responsibilities"]
        node["responsibilities"].append(RESPONSIBILITY)
    if not CHECK:
        (G / rel).write_text(json.dumps(new, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(("checked " if CHECK else "wrote ") + rel, changed)
