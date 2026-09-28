"""Update the authored tier of the graph descriptors whose source the 0.2.8203 change set changed.

Only role / responsibilities / owns_state of named nodes change; the mechanical tier is the extractor's.
Written with json.dumps(indent=1) + newline, the extractor's own format, so a re-run leaves it unchanged.
Usage: python edit_graph_descriptors.py <graph descriptor root>
"""
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])


def edit(rel: str, node_id: str, *, role=None, replace=None, add=None, owns_add=None) -> None:
    path = root / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    node = data["nodes"][node_id]
    if role is not None:
        node["role"] = role
    responsibilities = list(node.get("responsibilities") or [])
    for old, new in (replace or {}).items():
        if responsibilities.count(old) != 1:
            raise SystemExit(f"{node_id}: responsibility not found once: {old!r}")
        responsibilities[responsibilities.index(old)] = new
    for line in add or []:
        if line in responsibilities:
            raise SystemExit(f"{node_id}: responsibility already present: {line!r}")
        responsibilities.append(line)
    node["responsibilities"] = responsibilities
    if owns_add:
        owns = list(node.get("owns_state") or [])
        for field in owns_add:
            if field not in owns:
                owns.append(field)
        node["owns_state"] = owns
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("edited", node_id)


CONDUIT = "melder/aether/conduit/conduit.json"
edit(CONDUIT, "melder.aether.conduit.conduit.Conduit", replace={
    "serves warm automatic id melds (plain or with a non-empty dict override payload) straight from Meld's "
    "fast-door entry with ConduitMeld's guard ladder, returning an existing object's bound object without the "
    "door call":
    "serves warm automatic melds by id, by registered name and by class (plain or with a non-empty dict "
    "override payload) straight from Meld's fast-door entries (_fast_meld_doors, _fast_input_doors) with "
    "ConduitMeld's guard ladder, returning an existing object's bound object without the door call",
}, add=[
    "is a dispose scope in `with`: __enter__ takes no lock and __exit__ runs cleanup(), so a lesser returns "
    "to its pool and a root is torn down at block exit (0.2.8203)",
    "creates a lesser for a `with` block through enter_lesser_conduit, which returns create_lesser_conduit's "
    "result unchanged",
    "returns a lesser to its pool descendants first, then SpellSpaces, then its own store, and raises the "
    "collected disposal failures after the shell is pooled; soft cleanup of a pooled lesser is a no-op",
    "finishes permanent teardown when a disposal method fails and then raises the collected disposal groups",
])

SPACE = "melder/aether/conduit/spell_space/spell_space.json"
edit(SPACE, "melder.aether.conduit.spell_space.spell_space", replace={
    "refuse meld when it is not the active scope":
    "refuse meld and purge once released to its pool (one lease flag)",
})
edit(SPACE, "melder.aether.conduit.spell_space.spell_space.SpellSpace", replace={
    "marks one active spellspace scope on a conduit":
    "is one leased spellspace scope on a conduit, pushed on the calling thread's stack when managed",
    "enforces active-scope usage for spellspace-bound meld calls":
    "refuses meld and purge while released to its pool (the _released lease flag); a destroyed space raises "
    "the cleaned RuntimeError",
    "clears spellspace-scoped instances on reset or cleanup":
    "clears spellspace-scoped instances on managed exit or cleanup, finishing its pool return or destroy "
    "when a disposal method fails and then raising the store's group",
}, add=[
    "leaves its thread stack without error when released or destroyed inside its own managed block",
    "serves warm melds by id, by name and by class from its door's fast-door entries",
], owns_add=["_released"])

POOL = "melder/aether/conduit/spell_space/spell_space_pool.json"
edit(POOL, "melder.aether.conduit.spell_space.spell_space_pool.SpellSpacePool", add=[
    "sets a space's released flag on release and clears it on every acquisition",
])

STATE = "melder/aether/conduit/spell_space/spell_space_thread_state.json"
edit(STATE, "melder.aether.conduit.spell_space.spell_space_thread_state.SpellSpaceThreadState", add=[
    "removes an expected top entry without raising, for a space released or destroyed inside its own block",
])

WARD = "melder/aether/conduit/conduit_ward/conduit_ward.json"
edit(WARD, "melder.aether.conduit.conduit_ward.conduit_ward.ConduitWard", replace={
    "retains failed descendant ownership and prevents ancestor pooling until child cleanup succeeds":
    "retains a descendant that could not finish its pool return and prevents ancestor pooling; a child that "
    "finished but raised disposal failures is returned to the pooling parent",
}, add=[
    "raises its lesser children's disposal failures after finishing its own teardown",
])

FRAME = "melder/aether/aetheric_frame/aetheric_frame.json"
edit(FRAME, "melder.aether.aetheric_frame.aetheric_frame.AethericFrame", add=[
    "logs a conduit that raises during frame teardown through the Aether logger and cleans the rest",
])

CLEAN = "melder/utilities/general_base/cleanable.json"
edit(CLEAN, "melder.utilities.general_base.cleanable.Cleanable", replace={
    "provides the cleanup-context helper for deterministic teardown":
    "provides using_cleanup() and async_using_cleanup() helper contexts that clean up at most once and let "
    "cleanup errors propagate",
})
edit(CLEAN, "melder.utilities.general_base.cleanable._CleanupContext", add=[
    "drops its owner reference, calls cleanup() at most once and lets its error propagate without "
    "suppressing the block's exception",
])
edit(CLEAN, "melder.utilities.general_base.cleanable._AsyncCleanupContext",
     role="Async counterpart of the cleanup context, driving async_cleanup().",
     add=[
         "drops its owner reference, awaits async_cleanup() at most once and lets its error propagate without "
         "suppressing the block's exception",
     ])

MELD = "melder/aether/conduit/meld/spellspace_meld.json"
edit(MELD, "melder.aether.conduit.meld.spellspace_meld.SpellSpaceMeld", replace={
    "serves warm automatic id melds from the fast-door entry with ConduitMeld's guard ladder and both arms "
    "(plain and dict override payloads)":
    "serves warm automatic id melds from the fast-door entry with ConduitMeld's guard ladder and both arms "
    "(plain and dict override payloads), and mints the name/class entries (_fast_input_doors) its space reads",
})
