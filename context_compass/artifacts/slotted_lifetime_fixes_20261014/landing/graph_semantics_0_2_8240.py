"""
Author the slotted_lifetime lane's lines on the graph nodes it changed (0.2.8236-0.2.8240), on descriptors written
by extract_graph (indent=1 JSON with a trailing newline). Run after extract_graph and before assemble_graph.
(EPIC-2026-10-14-slotted_lifetime_ownership_fixes)

Usage: python graph_semantics_0_2_8240.py <context_compass/system_docs/graph>
"""
import json
import pathlib
import sys
from typing import Dict, List, Optional

GRAPH = pathlib.Path(sys.argv[1])


def author(rel: str, node_id: str, *, role: Optional[str] = None, replace: List[tuple] = (), add: List[str] = (),
           owns_state_add: List[str] = (), fresh: Optional[Dict[str, object]] = None) -> None:
    """Rewrite one node's authored fields in place; every replaced entry must exist exactly once."""
    path = GRAPH / rel
    raw = path.read_bytes().decode("utf-8")
    data = json.loads(raw)
    assert json.dumps(data, indent=1, ensure_ascii=False) + "\n" == raw, f"{rel}: unexpected formatting"
    node = data["nodes"][node_id]
    if fresh is not None:
        assert not node.get("role") and not node.get("responsibilities"), f"{node_id} already authored"
        node.update(fresh)
    if role is not None:
        node["role"] = role
    for old, new in replace:
        assert node["responsibilities"].count(old) == 1, old
        node["responsibilities"][node["responsibilities"].index(old)] = new
    for line in add:
        assert line not in node.setdefault("responsibilities", [])
        node["responsibilities"].append(line)
    for field in owns_state_add:
        state = node.setdefault("owns_state", [])
        assert field not in state, field
        state.append(field)
    path.write_bytes((json.dumps(data, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print("authored", node_id)


CREATIONS = "melder.aether.conduit.creations."
author(
    "melder/aether/conduit/creations/creations.json", CREATIONS + "creations.HolderDisposalEntry",
    fresh={
        "include": True,
        "role": "Cleanup-only record of one slotted holder and the disposal-bearing many children adopted for it "
                "(0.2.8238).",
        "responsibilities": [
            "item is the holder the store holds under the holder's spell id; methods is the holder Spell's ordered "
            "disposal list, borrowed (empty when the holder declares none, the record then exists for its children)",
            "children lists (child, child_methods) pairs in build order; a child is in exactly one place, its spell's "
            "many bucket or one holder record",
            "disposal runs the holder's methods, then each child's, newest child first, so a holder whose own disposal "
            "uses a child still finds it open",
            "every field is borrowed: the owning Creations store detaches the record and disposes from it; the record "
            "owns nothing and needs no cleanup",
        ],
        "owns_state": ["item", "methods", "children"],
        "phases": ["runtime", "cleanup"],
    },
)
author(
    "melder/aether/conduit/creations/creations.json", CREATIONS + "creations.Creations",
    role="Generic scoped live-object registry with disposal metadata kept beside it: a (object, methods) tuple per "
         "unique key, a ManyDisposalBucket per disposal-bearing many key, a HolderDisposalEntry per slotted holder "
         "that adopted many children.",
    add=["records a just-published slotted holder's disposal-bearing many children with the holder (adopt_children, "
         "0.2.8238): moves them out of their spells' buckets into the holder's HolderDisposalEntry, so purge, "
         "extract/restore and whole-store disposal reach them through the holder's key with one dict read; a many "
         "purge or live-creation probe of a child's spell counts only children no holder adopted"],
)
author(
    "melder/aether/conduit/creations/cluster_creations.json", CREATIONS + "cluster_creations.ClusterCreations",
    role="Facade over the cluster's team store, bound while a leader is elected; references, never owns.",
    add=["records the elected leader's id as the purge authority for the team store, whose owner id is the "
         "cluster's (0.2.8237)"],
)
author(
    "melder/aether/conduit/creations/cluster_creations.json", CREATIONS + "cluster_creations",
    role="Facade a member root resolves the cluster's team store through.",
    replace=[("give members one stable handle while the real store moves with the leader",
              "give members one stable handle to the cluster's team store, which stays with the cluster across leader "
              "changes (0.2.8237)")],
)
CLUSTER = "melder.aether.conduit.conduit_cluster."
author(
    "melder/aether/conduit/conduit_cluster.json", CLUSTER + "ConduitCluster",
    add=[
        "owns the cluster's team store (_team_store, 0.2.8237): binds every member root's ClusterCreations facade to "
        "it with the elected leader's id at election and on join, unbinds at unelect and a leader's exit, keeps its "
        "instances across leader changes, and disposes it once in cleanup, raising the failures as an ExceptionGroup",
        "runs every leave as one ordered exit (release_member, 0.2.8236): unelect first when the leaver leads, "
        "unshare both directions while its share record exists, then remove the membership; drop_member makes the "
        "same changes without transactions for a root torn down with its frame or whose exit failed",
    ],
    owns_state_add=["_team_store"],
)
author(
    "melder/aether/conduit/conduit_cluster.json", CLUSTER[:-1],
    role="Frame-local membership group with leaderless spell sharing plus an optional team store the cluster owns, "
         "served while a leader is elected.",
)
author(
    "melder/aether/aetheric_frame/conduit_cloud.json", "melder.aether.aetheric_frame.conduit_cloud.ConduitCloud",
    add=["runs an explicit cluster leave through ConduitCluster.release_member and answers get_clusters_for_conduit "
         "from the frame's membership index through _cluster_names_by_id (0.2.8236); delete_cluster raises the "
         "deleted cluster's disposal failures after removing it (0.2.8237)"],
    owns_state_add=["_cluster_names_by_id"],
)
author(
    "melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.json",
    "melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership.TransferOfOwnership",
    add=["moves the source root store's entries of every index member to the target's store when move_creations is "
         "True (the public verbs' default since 0.2.8239; a holder's row carries its adopted children) or takes the "
         "active member's out when False; disposes nothing, and hands over stewardship, not a working setup"],
)
author(
    "melder/aether/conduit/conduit.json", "melder.aether.conduit.conduit.Conduit",
    add=["leaves its cluster as the first step of a root's teardown (_leave_cluster_for_teardown, 0.2.8236): the "
         "cluster's ordered exit while the frame is live, drop_member during frame teardown or after a failed exit"],
)
author(
    "melder/aether/conduit/meld/conduit_meld.json", "melder.aether.conduit.meld.conduit_meld.ConduitMeld",
    add=["grants purge of a unique_per_conduit_cluster instance to the elected leader recorded on its cluster facade, "
         "since the team store's owner id is the cluster's (0.2.8237)"],
)
author(
    "melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.json",
    "melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering.SitePlanEmission",
    add=["emits c{i}.adopt_children(sid{i}, v{i}, ((sidK, vK), ...)) right after holder i's publication in its miss, "
         "naming exactly the disposal-bearing many children registered in c{i} for it (holder records, 0.2.8238); "
         "warm _site_plan_executor bodies are unchanged"],
)
