"""Author the graph semantics touched by shared_context_rebuild_2026_09_26 (scratch descriptors only).

Usage: python author_graph.py <descriptor_root>
Each change was written after reading the class source in full on 2026-09-26.
"""
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
CC = "melder.aether.conduit.meld.creation_context"


def load(rel: str) -> tuple[pathlib.Path, dict]:
    path = root / rel
    return path, json.loads(path.read_bytes())


def save(path: pathlib.Path, data: dict) -> None:
    path.write_bytes((json.dumps(data, indent=1) + "\n").encode())
    print("authored", path.name)


def add_edge(data: dict, edge: dict) -> None:
    edges = data.get("edges_authored") or []
    if not any(e["from"] == edge["from"] and e["to"] == edge["to"] for e in edges):
        edges.append(edge)
    data["edges_authored"] = edges


# ---------------------------------------------------------------- CreationContextFactory
path, d = load("melder/aether/conduit/meld/creation_context/creation_context_factory.json")
n = d["nodes"][f"{CC}.creation_context_factory.CreationContextFactory"]
n["responsibilities"] = [
    "returns a published spell-owned CreationContext without locking, or elects one cold builder per spell "
    "through the spell's CounterSwitch",
    "on a failed build records the cause on the spell and releases the pending claim so waiting callers "
    "raise instead of hanging",
    "resolves or creates the shared spell-index CreationGate through the frame-owned CreationGateController "
    "and hands it to Spell (resolve_spell_index_gate)",
]
n["owns_state"] = ["_dynamic_environment", "_creation_gate_controller", "_created_spell_index_ids"]
for e in d["edges_authored"]:
    if e["to"] == f"{CC}.creation_context_builder.CreationContextBuilder":
        e["relation"] = "uses"
        e["strength"] = "soft"
        e["phase"] = ["runtime"]
        e["why"] = ("CreationContextFactory calls the stateless static CreationContextBuilder.build; it holds no "
                    "builder instance (corrected 2026-09-26: an earlier edge claimed ownership of one).")
    if e["to"].endswith("CreationGateController"):
        e["why"] = ("CreationContextFactory borrows the frame-owned CreationGateController to resolve or create "
                    "the shared gate for a spell's stable index id.")
save(path, d)

# ---------------------------------------------------------------- CreationContextRebuild
path, d = load("melder/aether/conduit/meld/creation_context/creation_context_rebuild.json")
m = d["nodes"][f"{CC}.creation_context_rebuild"]
m["include"] = True
m["role"] = "Rare-path rebuild window for spells whose shared CreationContext is being replaced."
m["responsibilities"] = ["hosts CreationContextRebuild, the producer-side window Meld enters around rebuilds"]
m["phases"] = ["runtime"]
c = d["nodes"][f"{CC}.creation_context_rebuild.CreationContextRebuild"]
c["include"] = True
c["role"] = ("Producer window that freezes and drains a spell's index gate while phases replace its plan and "
             "context, then publishes the rebuilt context before reopening.")
c["responsibilities"] = [
    "takes each affected gate's transition lock in index-id order, records its posture, closes it and "
    "drains admitted tickets",
    "clears the spell's recorded context failure on entry",
    "on success publishes a context for spells whose phase-11 plan is present, leaving plan-less spells "
    "unpublished without touching resolution flags",
    "on failure records the cause on unpublished spells and idles their CounterSwitch; the error propagates",
    "restores gate posture and releases locks in reverse order; never cleans a gate",
]
c["owns_state"] = ["_spells", "_held_gates", "_finalize_contexts"]
c["phases"] = ["runtime", "cleanup"]
d["edges_authored"] = d.get("edges_authored") or []
add_edge(d, {
    "from": f"{CC}.creation_context_rebuild.CreationContextRebuild",
    "to": "melder.utilities.synchronization.creation_gate.CreationGate",
    "relation": "borrows", "cardinality": "one_to_many", "phase": ["runtime"], "strength": "borrowed",
    "why": ("Freezes, drains and reopens the spells' index gates and holds their transition locks for one "
            "operation; the frame's CreationGateController owns the gates."),
})
add_edge(d, {
    "from": f"{CC}.creation_context_rebuild.CreationContextRebuild",
    "to": "melder.aether.spellbook.spell.Spell",
    "relation": "borrows", "cardinality": "one_to_many", "phase": ["runtime"], "strength": "borrowed",
    "why": ("Reads each spell's gate and plan and writes its context, switch and failure fields during one "
            "rebuild; the Spellbook owns the spells."),
})
save(path, d)

# ---------------------------------------------------------------- Meld
path, d = load("melder/aether/conduit/meld/meld.json")
n = d["nodes"]["melder.aether.conduit.meld.meld.Meld"]
extra = [
    "runs a dynamic spell's structural, resolution and deferred rebuilds inside a CreationContextRebuild "
    "window entered before the spell lock (_rebuild_window)",
    "executes a dynamic meld under one spell-index ticket held from before the context read until the "
    "executor returns (_execute_admitted)",
]
n["responsibilities"] = [r for r in n["responsibilities"] if r not in extra] + extra
add_edge(d, {
    "from": "melder.aether.conduit.meld.meld.Meld",
    "to": f"{CC}.creation_context_rebuild.CreationContextRebuild",
    "relation": "uses", "cardinality": "one_to_many", "phase": ["runtime"], "strength": "soft",
    "why": ("Meld creates one short-lived CreationContextRebuild per conduit-local rebuild of a dynamic spell "
            "so admitted melds drain before phases replace the shared plan and context."),
})
save(path, d)

# ---------------------------------------------------------------- ConduitMeld / SpellSpaceMeld
for rel, nid in (("melder/aether/conduit/meld/conduit_meld.json", "melder.aether.conduit.meld.conduit_meld.ConduitMeld"),
                 ("melder/aether/conduit/meld/spellspace_meld.json", "melder.aether.conduit.meld.spellspace_meld.SpellSpaceMeld")):
    path, d = load(rel)
    n = d["nodes"][nid]
    line = ("admits a dynamic spell through its spell-index gate before reading the context (both lanes, via "
            "Meld._execute_admitted); automatic spells keep the unticketed lane and fast-door memo")
    if line not in n["responsibilities"]:
        n["responsibilities"].append(line)
    save(path, d)

# ---------------------------------------------------------------- Spell
path, d = load("melder/aether/spellbook/spell.json")
n = d["nodes"]["melder.aether.spellbook.spell.Spell"]
line = ("keeps a borrowed spell-index CreationGate under dynamic ownership and the cause of its last failed "
        "context build")
if line not in n["responsibilities"]:
    n["responsibilities"].append(line)
if "_creation_context_failure" not in n["owns_state"]:
    n["owns_state"].append("_creation_context_failure")
add_edge(d, {
    "from": "melder.aether.spellbook.spell.Spell",
    "to": "melder.utilities.synchronization.creation_gate.CreationGate",
    "relation": "borrows", "cardinality": "many_to_one", "phase": ["runtime"], "strength": "borrowed",
    "why": ("Spell keeps the frame controller's gate for its index (dynamic only) so meld doors admit before "
            "reading the context; it drops the reference with its factory and never cleans the gate."),
})
save(path, d)
