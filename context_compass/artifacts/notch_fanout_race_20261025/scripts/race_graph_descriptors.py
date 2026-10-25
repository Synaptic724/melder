"""Graph descriptors for the notch fan-out race (melder_0, 2026-10-25; TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout).

Same procedure as codegen_room_policy_20261025/scripts/d20_graph_descriptors.py: mirror at /tmp/m0race_graph after the
design-2 edits, authored tiers compared, prose brought to the source re-read 2026-10-25T14:xxZ. Conduit, Spellbook and
NotchTransactionStrategy gain one responsibility each; ConduitWard's change is a comment, so its descriptor takes the
mechanical refresh only. Usage: race_graph_descriptors.py --check | --apply
"""
import json
import pathlib
import sys
from typing import Callable, List

REPO = pathlib.Path.home() / "mnt/melder_private/context_compass/system_docs/graph/melder"
MIRROR = pathlib.Path("/tmp/m0race_graph/graph/melder")
AUTHORED_NODE = ("role", "responsibilities", "owns_state", "phases", "semantics_authored_against", "include")
AUTHORED_FILE = ("edges_authored", "nodes_retired")
T = "(design 2, 0.2.8275)"
EDITS = {
 "aether/conduit/conduit.json": ("melder.aether.conduit.conduit.Conduit",
  "runs a notch's borrower fan-out inside the notch's transaction window, as Spellbook._notch_spell's after-switch "
  "hook, with its ward links' lineages sealed and frozen (linked_root_conduit_ids); on a failed fan-out moves the "
  "borrowers back after the Book's reversal (_undo_borrower_fan_out) so a notch stands whole or not at all " + T),
 "aether/spellbook/spellbook.json": ("melder.aether.spellbook.spellbook.Spellbook",
  "runs a notch's after_switch hook after the structural check inside the guarded section, so an error from it takes "
  "the refused-notch reversal " + T),
 "aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.json": (
  "melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.notch_transaction_strategy.NotchTransactionStrategy",
  "adds the acting conduit's linked_root_conduit_ids to the conduits it seals EXCLUSIVE and quiesces, so every lineage "
  "the borrower fan-out moves is parked while it runs " + T),
 "aether/conduit/conduit_ward/conduit_ward.json": (None, None),
}


def append_once(items: List[str], text: str) -> None:
    if text in items:
        raise SystemExit("already applied: " + text[:60])
    items.append(text)


def add_edge_once(d: dict, edge: dict) -> None:
    if any(e.get("from") == edge["from"] and e.get("to") == edge["to"] and e.get("relation") == edge["relation"]
           for e in d["edges_authored"]):
        raise SystemExit("edge already present: " + edge["from"][:40] + " -> " + edge["to"][:40])
    d["edges_authored"].append(dict(edge))


def one(rel: str, change: Callable[[dict], None], apply: bool) -> None:
    repo_path, mirror_path = REPO / rel, MIRROR / rel
    repo_raw, mirror_raw = repo_path.read_bytes(), mirror_path.read_bytes()
    for raw in (repo_raw, mirror_raw):
        if b"\r" in raw:
            raise SystemExit("CR in " + rel)
    repo, mirror = json.loads(repo_raw.decode("utf-8")), json.loads(mirror_raw.decode("utf-8"))
    for raw, parsed in ((repo_raw, repo), (mirror_raw, mirror)):
        if (json.dumps(parsed, indent=1) + "\n").encode("utf-8") != raw:
            raise SystemExit("not in the extractor's format: " + rel)
    if set(repo["nodes"]) != set(mirror["nodes"]):
        raise SystemExit("node sets differ in " + rel)
    for nid, node in repo["nodes"].items():
        for field in AUTHORED_NODE:
            if node.get(field) != mirror["nodes"][nid].get(field):
                raise SystemExit(f"authored field {field} of {nid} differs between repository and mirror")
    for field in AUTHORED_FILE:
        if repo.get(field) != mirror.get(field):
            raise SystemExit(f"authored file field {field} differs in {rel}")
    change(mirror)
    text = json.dumps(mirror, indent=1) + "\n"
    print(rel, "->", len(text.splitlines()), "lines")
    if not apply:
        return
    if repo_path.read_bytes() != repo_raw:
        raise SystemExit("RACE " + rel)
    repo_path.write_bytes(text.encode("utf-8"))
    if repo_path.read_bytes().decode("utf-8") != text:
        raise SystemExit("read-back mismatch " + rel)


def make(rel):
    node_id, text = EDITS[rel]
    def change(d):
        if node_id is not None:
            append_once(d["nodes"][node_id]["responsibilities"], text)
    return change


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    apply = sys.argv[1] == "--apply"
    for rel in EDITS:
        one(rel, make(rel), apply)
    print("applied" if apply else "checked")


if __name__ == "__main__":
    main()
