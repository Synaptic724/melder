"""
Align the slotted_lifetime_ownership_2026_10_14 patch docs with the owner's rulings before they are archived
(EPIC-2026-10-14-slotted_lifetime_ownership_fixes): contract invalidation stays as it is (2026-10-14T23:00Z), the
objective no longer states a dispose-everything rule, and the cluster patch names the cloud's id->name map the code
uses. Each anchor must match once; the docs stay LF ASCII. Run from the repository root.
"""
import pathlib

PATCH = pathlib.Path("context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14")


def edit(name: str, pairs: list) -> None:
    path = PATCH / name
    text = path.read_bytes().decode("utf-8")
    assert "\r\n" not in text, name
    for old, new in pairs:
        assert text.count(old) == 1, (name, old[:60], text.count(old))
        text = text.replace(old, new)
    text.encode("ascii")
    path.write_bytes(text.encode("utf-8"))
    print("aligned", name)


edit("architecture_patch.md", [
    ("- Status: active - written before any src edit (2026-10-14); D3 rescoped by the owner (2026-10-14T22:14Z)\n",
     "- Status: promoted at landing (2026-10-15) and archived; written before any src edit (2026-10-14); D3 rescoped by\n"
     "  the owner (2026-10-14T22:14Z); contract invalidation left as it is by the owner (2026-10-14T23:00Z)\n"),
    ("Apply the owner's rule at every point where an owner ends or changes: a slotted instance and the `many` children\n"
     "built for it are recorded with the object its lifetime names, move with it, and are disposed with it, exactly once.\n",
     "Fix the structure that recorded slotted instances under the wrong owner or left registry state stuck where an owner\n"
     "ends or changes: a slotted instance and the `many` children built for it are recorded with the object its lifetime\n"
     "names and move with it. Melder's infrastructure disposes what its own stores record when they end; it does not\n"
     "police the application objects it hands out, which agents iterate on and clean up (owner ruling 2026-10-14,\n"
     "promoted to src_architecture as \"Runtime Model: Structure Is the Contract\").\n"),
    ("  verb defaults to `move_creations=True` and its docstrings say what each value does. Contract invalidation drops\n"
     "  a retired consumer undisposed and leaves a lesser's consumer in place (b7, l2): pending the owner's ruling.\n",
     "  verb defaults to `move_creations=True` and its docstrings say what each value does. Contract invalidation lets a\n"
     "  retired consumer go undisposed and leaves a lesser's consumer in place (b7, l1, l2): intended behaviour by the\n"
     "  owner's ruling (2026-10-14), no change.\n"),
    ("`retire_singleton_creation` only if the owner rules the invalidation fix in | D4, D5 (D3 pending) |",
     "`retire_singleton_creation` withdrawn (invalidation left as it is) | D4, D5 |"),
    ("| ConduitWard contract invalidation | pending the owner's ruling (b7: a retired consumer is dropped undisposed; l2: a lesser keeps serving its consumer) | D3 (pending) |",
     "| ConduitWard contract invalidation | no change by the owner's ruling (2026-10-14): a consumer a contract change retires is left to the agents (b7) and a lesser keeps its consumer (l1, l2) | D3 (no change) |"),
    ("   leave the source store and are neither moved nor disposed). Contract invalidation: pending the owner's ruling.\n",
     "   leave the source store and are neither moved nor disposed). Contract invalidation is unchanged by the owner's\n"
     "   ruling: the objects it lets go of stay pending for agents to manage.\n"),
    ("llm_support last. The invalidation half of D3 waits for the owner's ruling.\n",
     "llm_support last. The invalidation half of D3 was ruled out (no change, 2026-10-14); a docstring notch (0.2.8240)\n"
     "documents the transfer handover: stewardship, not a working setup.\n"),
])

edit("component_patch_conduit_ward_contracts.md", [
    ("# Component patch: ConduitWard - contract invalidation disposes what it retires (slotted_lifetime_ownership_2026_10_14)\n",
     "# Component patch: ConduitWard - contract invalidation, WITHDRAWN (slotted_lifetime_ownership_2026_10_14)\n"),
    ("Status: PENDING the owner's ruling (2026-10-14). The transfer half of D3 was rescoped to the default flip; this\n"
     "invalidation fix is not applied until the owner decides.\n",
     "Status: WITHDRAWN - no change, by the owner's ruling (2026-10-14T23:00Z): the objects a contract change lets go of\n"
     "stay pending for agents to manage (src_architecture, \"Runtime Model: Structure Is the Contract\"). The text below\n"
     "records the proposal only; it was never applied.\n"),
])

edit("component_patch_creations.md", [
    ("(landed 0.2.8238); D3's invalidation helper pending the owner's ruling.\n",
     "(landed 0.2.8238); D3's invalidation helper withdrawn (owner ruling 2026-10-14: invalidation unchanged).\n"),
    ("- Whole-store disposal (`cleanup`, `clear_all`, `reset_for_pool*`), `purge` and the new retirements dispose a\n",
     "- Whole-store disposal (`cleanup`, `clear_all`, `reset_for_pool*`) and `purge` dispose a\n"),
    ("- PENDING the owner's ruling on contract invalidation (b7, l2): `retire_singleton_creation(spell_id)` - under the\n"
     "  store lock detach one slotted entry (and its holder record), leave `many` keys alone, dispose outside the lock.\n",
     "- WITHDRAWN (owner ruling 2026-10-14: contract invalidation stays as it is): `retire_singleton_creation` is not\n"
     "  added.\n"),
    ("`_dispose_holder_entry` (0.2.8238); `retire_singleton_creation` only if the invalidation fix is ruled in.\n",
     "`_dispose_holder_entry` (0.2.8238).\n"),
    ("- Emitters (site-plan lowering) call `adopt_children`; the ward would call `retire_singleton_creation` (pending).\n",
     "- Emitters (site-plan lowering) call `adopt_children`; the ward is unchanged (invalidation withdrawn).\n"),
])

edit("component_patch_conduit_clusters.md", [
    ("- `ConduitCloud.get_clusters_for_conduit`: scanned every cluster's member set. After: reads the DevOps index\n"
     "  (`get_cluster_objects_for_conduit`) and keeps the clusters the cloud still maps by name - O(1) under exclusive\n"
     "  membership, same list-of-names contract. Join exclusivity and the transfer borrower walk inherit it.\n",
     "- `ConduitCloud.get_clusters_for_conduit`: scanned every cluster's member set. After: reads the DevOps index\n"
     "  (`get_clusters_for_conduit`, cluster ids) and names them through the cloud-owned `_cluster_names_by_id` map,\n"
     "  so a cluster deleted concurrently is never touched (aligned at promotion: the patch first said the cloud read\n"
     "  cluster objects from the registry) - O(1) under exclusive membership, same list-of-names contract. Join\n"
     "  exclusivity and the transfer borrower walk inherit it.\n"),
    ("  `_team_store` slot; `ClusterCreations.bind(store, leader_conduit_id)`, `ClusterCreations.leader_conduit_id`;\n",
     "  `_team_store` slot; the cloud's `_cluster_names_by_id` map; `ClusterCreations.bind(store, leader_conduit_id)`,\n"
     "  `ClusterCreations.leader_conduit_id`;\n"),
])
