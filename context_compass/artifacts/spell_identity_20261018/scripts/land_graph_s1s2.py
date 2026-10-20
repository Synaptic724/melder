"""S1 and S2 into the source graph (melder_0, 2026-10-18): the two new modules authored, Bind's identity prose fixed.

Authors the module and class nodes of `spell_code_digest.py` (SpellCodeDigest) and `binding_manifest.py`
(BindingManifest), and rewrites the four statements in bind.json that describe the retired fingerprint (two
responsibilities, the spellframe-kind clause and the SpellIndex edge's `why`). No node is accepted here: the prose is
written against the landed source and stays SEMANTICS_STALE until a reader re-verifies and accepts it. `--write`
writes the descriptors; extraction and assembly run after it.
"""
import json
import pathlib
import sys
from typing import Any, Dict

ROOT = pathlib.Path.home() / "mnt/melder_private/context_compass/system_docs/graph/melder/aether/spellbook/bind"

AUTHORED: Dict[str, Dict[str, Dict[str, Any]]] = {
    "spell_code_digest.json": {
        "melder.aether.spellbook.bind.spell_code_digest": {
            "role": "Module holding SpellCodeDigest, the encoder whose SHA256 is a spell_id (0.2.8257).",
            "responsibilities": ["defines SpellCodeDigest and nothing at module scope but imports"],
            "owns_state": [],
            "phases": ["init"],
        },
        "melder.aether.spellbook.bind.spell_code_digest.SpellCodeDigest": {
            "role": "Encodes a registration target's code and data into the text whose SHA256 is its spell_id.",
            "responsibilities": [
                "spell_id(target): the SHA256 of 'v5-code', the interpreter's cache tag and the target's encoding",
                "encodes a class as its module, qualname, metaclass and bases and, for it and every MRO class outside "
                "the standard library, its namespace: functions by code, defaults, annotations, closures, class values",
                "encodes a function by its code object: instructions, loaded constants, argument counts, flags, name "
                "tables and exception table - never line numbers, docstrings or comments",
                "encodes an existing object as its class's code plus its slots and __dict__ by value",
                "names installed third-party code (a module file under a site-packages root) by qualified name and "
                "distribution version instead of digesting it (decision B), and names standard-library classes",
                "takes nothing from the bind call: spellframe, binding name, existence, disposal names, resolvable and "
                "the managed settings belong to the binding manifest",
            ],
            "owns_state": ["_code_memo", "_third_party_memo", "_version_memo", "_distributions"],
            "phases": ["init", "runtime", "cleanup"],
        },
    },
    "binding_manifest.json": {
        "melder.aether.spellbook.bind.binding_manifest": {
            "role": "Module holding BindingManifest, how a spell is kept, and its SHA256 (0.2.8258).",
            "responsibilities": ["defines BindingManifest and nothing at module scope but imports"],
            "owns_state": [],
            "phases": ["init"],
        },
        "melder.aether.spellbook.bind.binding_manifest.BindingManifest": {
            "role": "Value record of a spell's binding - the bind call - whose SHA256 is the binding hash.",
            "responsibilities": [
                "build(...) records the spellframe and its kind, the address (frame and binding keys), existence, "
                "the ordered disposal names, resolvable and the managed settings, equal settings written alike",
                "binding_hash: the SHA256 of a tag and the field lines; it keys the creation caches beside the "
                "spell_id and rides the SpellCrystal (record 4.3.0)",
                "describe() gives the hash and the fields as plain data",
            ],
            "owns_state": [],
            "phases": ["init", "runtime"],
        },
    },
}

BIND_FIXES = {
    "fingerprints binding metadata into structural spell ids with no memory address in any input (address-free repr, "
    "default, signature and init_signature text), so the same object content gets one id in every process":
        "takes each spell_id from SpellCodeDigest.spell_id(target) - the SHA256 of the target's code and, for an "
        "existing object, its data - and nothing from the bind call; spell_id_inspector(spell) answers the same id",
    "validates native resolvable bool before reflection; False uses its own hash domain while True preserves legacy ids":
        "validates native resolvable bool before reflection; resolvable is a binding-manifest field, no part of the "
        "spell_id",
    "the fingerprint does not hash the kind": "the spell_id does not read the kind, a binding-manifest field",
    "Bind creates a SpellIndex lineage key from the structural fingerprint before constructing the Spell record.":
        "Bind creates a SpellIndex lineage key from the spell_id (the code digest) before constructing the Spell "
        "record.",
}


def main() -> None:
    staged: Dict[pathlib.Path, str] = {}
    for name, nodes in AUTHORED.items():
        path = ROOT / name
        data = json.loads(path.read_text(encoding="utf-8"))
        for node_id, fields in nodes.items():
            node = data["nodes"][node_id]
            if node.get("role"):
                sys.exit(f"ALREADY AUTHORED {node_id}")
            node.update(fields)
        staged[path] = json.dumps(data, indent=1, ensure_ascii=False) + "\n"
    bind = ROOT / "bind.json"
    text = bind.read_text(encoding="utf-8")
    for old, new in BIND_FIXES.items():
        hits = [k for k in range(len(text)) if text.startswith(old, k)]
        if len(hits) != 1:
            sys.exit(f"BIND FIX {old[:50]}: {len(hits)}")
        text = text.replace(old, new)
    json.loads(text)
    staged[bind] = text
    if "--write" not in sys.argv:
        print("CHECK OK", sorted(p.name for p in staged))
        return
    for path, content in staged.items():
        path.write_text(content, encoding="utf-8", newline="\n")
        print("wrote", path.name)


if __name__ == "__main__":
    main()
