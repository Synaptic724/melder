"""Rewrite the authored graph prose that described holder ownership of `many` children (0.2.8267).

Usage: python apply_graph_semantics_20261024.py <graph descriptor dir, e.g. .../system_docs/graph>
Run after extract_graph.py; edits only `role` / `responsibilities` text, asserting the old text first.
"""
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1]) / "melder"
CG = "aether/spellbook/spell_compiler/codegen_creation_system/"


def load(rel):
    path = root / rel
    return path, json.loads(path.read_text(encoding="utf-8"))


def save(path, data):
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("wrote", path)


def replace_item(node, old_prefix, new_text):
    items = node["responsibilities"]
    hits = [k for k, item in enumerate(items) if item.startswith(old_prefix)]
    assert len(hits) == 1, (old_prefix, hits)
    items[hits[0]] = new_text


def drop_item(node, old_prefix):
    items = node["responsibilities"]
    hits = [k for k, item in enumerate(items) if item.startswith(old_prefix)]
    assert len(hits) == 1, (old_prefix, hits)
    del items[hits[0]]


# Creations: two disposal shapes; a slotted holder is an ordinary unique entry.
path, d = load("aether/conduit/creations/creations.json")
node = d["nodes"]["melder.aether.conduit.creations.creations.Creations"]
assert node["role"].endswith("a HolderDisposalEntry per slotted holder that adopted many children.")
node["role"] = (
    "Generic scoped live-object registry with disposal metadata kept beside it: a (object, methods) tuple per unique "
    "key, a slotted holder's included, and a ManyDisposalBucket per disposal-bearing many key."
)
replace_item(
    node,
    "records a just-published slotted holder's disposal-bearing many children with the holder (adopt_children, 0.2.8238)",
    "keeps a slotted holder an ordinary unique entry (0.2.8267): its disposal and its purge run only its own methods, "
    "and the many objects built for it stay in their spells' buckets in the store that recorded them - the meld's "
    "innermost scope - so a many purge or live-creation probe of a child's spell counts every child that store holds; "
    "the holder record of 0.2.8238-0.2.8265 is removed",
)
save(path, d)

# SitePlanEmission: one registration rule; the adoption line is gone.
path, d = load(CG + "shared_assets/site_plan_lowering.json")
node = d["nodes"]["melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering.SitePlanEmission"]
replace_item(
    node,
    "registers a disposal-bearing many site in the store that owns its context (holder-owned many children, 0.2.8235)",
    "registers every disposal-bearing many site through many_store, the meld's innermost scope (the spellspace store, "
    "else the conduit store), at the top level and inside a shared site's miss alike (0.2.8267): a function that "
    "registers one emits the store selection (_many_store_prologue) - the plan at its top, a miss after its "
    "unresolved-input check - so a slotted holder's many children belong to the scope that built them, never to the "
    "holder's owner (0.2.8235-0.2.8265 registered them in the holder's store and, from 0.2.8238, recorded them with "
    "the holder); warm _site_plan_executor bodies are unchanged",
)
drop_item(node, "emits c{i}.adopt_children(sid{i}, v{i}, ((sidK, vK), ...)) right after holder i's publication")
save(path, d)

# TransferOfOwnership: a holder's row carries the holder alone.
path, d = load("aether/conduit/conduit_ward/transfer/transfer_of_ownership.json")
node = d["nodes"]["melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership.TransferOfOwnership"]
replace_item(
    node,
    "moves the source root store's entries of every index member to the target's store when move_creations is True",
    "moves the source root store's entries of every index member to the target's store when move_creations is True "
    "(the public verbs' default since 0.2.8239; a holder's row carries the holder alone since 0.2.8267 - the many "
    "objects built for it stay in the store that recorded them) or takes the active member's out when False; disposes "
    "nothing, and hands over stewardship, not a working setup",
)
save(path, d)

# The specializer's decline keeps its reason without holder ownership.
path, d = load(CG + "strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.json")
node = d["nodes"]["melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_no_overrides_compiler"]
replace_item(
    node,
    "decides which graphs the straight-line specializer can express: rows_feed_many_into_non_many_step",
    "decides which graphs the straight-line specializer can express: rows_feed_many_into_non_many_step is True when a "
    "many row feeds a non-many row, whose many child the site plan builds only in the holder's first build; a "
    "straight-line body would build it on every warm call, so such a graph keeps the plain door",
)
save(path, d)

path, d = load(CG + "strategies/generalized/hydration/generalized_hydrator.json")
node = d["nodes"]["melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration.generalized_hydrator"]
replace_item(
    node,
    "optionally installs the singleton warm-tail specializer, which deopts to the normal plan",
    "optionally installs the singleton warm-tail specializer, which deopts to the normal plan; it keeps the plain door "
    "for graphs with no capturable step, a root-only capture on a short-circuiting route, or a many step feeding a "
    "non-many step (whose many child the specialized body would build on every warm call)",
)
save(path, d)
