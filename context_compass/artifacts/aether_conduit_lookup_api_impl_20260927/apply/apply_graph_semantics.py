"""Authored-tier updates for the aether_conduit_lookup_api lane (graph descriptors, melder_0, 2026-09-27).

Adds one responsibility per changed node describing this lane's behaviour. Formatting is verified to round-trip
(json indent=1 plus a trailing newline) before any write, so only the added lines change.

Usage: python apply_graph_semantics.py <graph descriptor root (…/graph/melder)>
"""
import json
import os
import sys

ROOT = sys.argv[1]

ADDITIONS = {
    ("aether/aether.json", "melder.aether.aether.Aether"):
        "answers frame-scoped conduit lookups: root maps (*_root_*), the frame Cloud's named scopes "
        "(get_conduit_by_name) and every live conduit via root-ward lineage snapshots (get_conduit_by_id)",
    ("aether/aetheric_frame/conduit_cloud.json", "melder.aether.aetheric_frame.conduit_cloud.ConduitCloud"):
        "lists its named conduits as a tuple snapshot under its lock (list_conduits)",
    ("aether/conduit/conduit_ward/conduit_ward.json", "melder.aether.conduit.conduit_ward.conduit_ward.ConduitWard"):
        "resolves attached lessers by id over per-level dict.copy() snapshots of its child map, skipping "
        "children whose ward was torn down",
    ("aether/conduit/conduit_ward/transfer/transfer_of_ownership.json",
     "melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership.TransferOfOwnership"):
        "sweeps ROOT conduits only (Aether root-named lookups) for impacted lineages; lessers own nothing "
        "but the lifecycle of what they create",
    ("nexus/rift/command_system/command_system.json", "melder.nexus.rift.command_system.command_system.CommandSystem"):
        "resolves conduit ids through Aether's live-conduit lookup after its ACL gates, keeping its frame "
        "and not-found errors",
    ("nexus/rift/command_system/static_command_system.json",
     "melder.nexus.rift.command_system.static_command_system.StaticCommandSystem"):
        "resolves spell owners through Aether's root lookup (owners are roots)",
    ("nexus/rift/frame_viewer/static_frame_viewer.json",
     "melder.nexus.rift.frame_viewer.static_frame_viewer.StaticFrameViewer"):
        "resolves spell owners through Aether's live-conduit lookup, None on a miss",
}

for (relative, node_id), text in ADDITIONS.items():
    path = os.path.join(ROOT, relative)
    with open(path, encoding="utf-8", newline="") as handle:
        original = handle.read()
    data = json.loads(original)
    assert json.dumps(data, indent=1) + "\n" == original, f"{relative}: formatting does not round-trip"
    node = data["nodes"][node_id]
    responsibilities = node.setdefault("responsibilities", [])
    if text not in responsibilities:
        responsibilities.append(text)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(json.dumps(data, indent=1) + "\n")
    print("updated", node_id)
