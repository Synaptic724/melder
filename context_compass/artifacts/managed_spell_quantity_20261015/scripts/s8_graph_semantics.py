"""S8: graph semantics for parked_versions_wired_at_conjure_2026_10_16 (0.2.8248).

Run from the repository root: python s8_graph_semantics.py [--dry-run]

- The three nodes this lane's diff moved that were AUTHORED against 0.2.8247 (SpellbookCreationSystem,
  SitePlanRuntimeHelpers, Spellbook): the lane's facts written from the changed hunks of their spans, read whole
  (`define_conduit_into_spells`, `raise_missing_managed_pool`, the comment in `bind_inactive`); accepted afterwards
  with graph_walker --accept.
- The two nodes in this lane's files already stale before it (CachingSystem since before 0.2.8246,
  TransferOfOwnership since before 0.2.8240): the lane's facts appended, NOT accepted - their older claims were never
  verified.
Every edit asserts the state it expects, so a second run refuses instead of duplicating. Writes descriptors the way the
extractor does (indent=1, LF).
"""
import json
import pathlib
import sys

GRAPH = pathlib.Path("context_compass/system_docs/graph")
DRY = "--dry-run" in sys.argv

SCS = "melder.aether.spellbook.spellbook_creation_system.SpellbookCreationSystem"
HELPERS = "melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering.SitePlanRuntimeHelpers"
BOOK = "melder.aether.spellbook.spellbook.Spellbook"
CACHE = "melder.utilities.caching_system.caching_system.CachingSystem"
TOO = "melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership.TransferOfOwnership"

# (descriptor, node id, kind, old responsibility or None, new responsibility)
EDITS = [
    ("melder/aether/spellbook/spellbook_creation_system.json", SCS, "replace",
     "wires conduit ownership into local spells and fires conjure hooks",
     "wires conduit ownership into local spells and fires conjure hooks: every active version gets the owner stamp, its"
     " resolution flag cleared and an existing object registered; then, under the same Book lock, every version parked"
     " with bind_inactive before conjure gets the owner stamp alone - what a post-conjure bind_inactive gives it - so it"
     " melds after a notch (define_conduit_into_spells, 0.2.8248); a raising stamp is logged per version"),
    ("melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.json", HELPERS,
     "replace",
     "raise_missing_managed_pool(spell): the named MeldExecutionError of a managed site whose pool cannot be read - its"
     " owner root torn down, or a version staged before conjure (0.2.8245)",
     "raise_missing_managed_pool(spell): the named MeldExecutionError of a managed site whose pool cannot be read - its"
     " owner root torn down, or its owner store holding no pool for the version (0.2.8245); since 0.2.8248 conjure"
     " stamps the versions staged before it, so the message no longer names that cause or the 'stage the version after"
     " conjure' remedy"),
    ("melder/aether/spellbook/spellbook.json", BOOK, "append", None,
     "parks versions with bind_inactive: one parked after conjure is stamped by bind_inactive itself with the owner"
     " stamp an active bind uses, one parked before conjure by SpellbookCreationSystem.define_conduit_into_spells at"
     " conjure with the same stamp and nothing else (0.2.8248), so either melds after a notch"),
    ("melder/utilities/caching_system/caching_system.json", CACHE, "append", None,
     "cache generation 21 retires bundles written before the managed lease codegen (0.2.8245), the explicit retirement"
     " the owner asked for whenever codegen changes (0.2.8248)"),
    ("melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.json", TOO, "append", None,
     "moves a parked member that carries no owner stamp unstamped; since 0.2.8248 conjure stamps the versions staged"
     " before it, so that is only a member whose stamp raised at conjure (logged)"),
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
