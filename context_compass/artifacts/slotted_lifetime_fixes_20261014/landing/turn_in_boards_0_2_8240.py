"""
Closure sync of both boards for the turn-in of 2026-10-15 (turn_in_0_2_8240.py): remove the three active routes and
their attention details, add one closed anchor per ticket (capped at 12, oldest dropped first), move the closed
tickets' artifact rows to the cleared list with their completed paths. Run from the repository root:
python turn_in_boards_0_2_8240.py <UTC timestamp>
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
CC = pathlib.Path("context_compass")


def region(text: str, name: str) -> tuple:
    begin = f"<!-- BEGIN USER-DEFINED: {name} -->\n"
    end = f"<!-- END USER-DEFINED: {name} -->"
    i = text.index(begin) + len(begin)
    j = text.index(end, i)
    return i, j


# --- attention board -------------------------------------------------------------------------------------------
board = CC / "attention_board.md"
t = board.read_bytes().decode("utf-8")
assert "\r\n" not in t
CLOSED_ROUTES = ("slotted_lifetime_fixes", "many_child_registration", "pool_decay_clock_rounding")

i, j = region(t, "active_items")
rows = t[i:j].splitlines(keepends=True)
kept = [r for r in rows if not any(r.startswith(f"| {w} |") for w in CLOSED_ROUTES)]
assert len(rows) - len(kept) == 3, (len(rows), len(kept))
t = t[:i] + "".join(kept) + t[j:]

i, j = region(t, "active_attention_details")
body = t[i:j]
for w in CLOSED_ROUTES:
    body, n = re.subn(r"- WORK_ITEM: " + re.escape(w) + r"\n(?:  .*\n|    .*\n)*", "", body)
    assert n == 1, (w, n)
t = t[:i] + body + t[j:]

ANCHORS = [
    ("many_child_fix", "tickets/tasks/completed/2026-10-14_fix_many_child_follows_holder_task.md",
     "Landed 0.2.8235 (a slotted holder's many children register with its owner); turned in by owner directive. Next: none."),
    ("many_child_registration", "tickets/epics/completed/2026-10-14_many_child_follows_holder_epic.md",
     "0.2.8235 plus its purge/transfer follow-ups (0.2.8238, slotted lane); turned in by owner directive. Next: none."),
    ("pool_decay_clock_rounding", "tickets/tasks/completed/2026-10-14_fix_pool_decay_fake_clock_rounding_task.md",
     "Test-only fix (no notch): the decay test's clock starts on a whole second; turned in. Next: none."),
    ("slotted_d1_cluster_exit", "tickets/tasks/completed/2026-10-14_investigate_cluster_member_teardown_without_leave_task.md",
     "Landed 0.2.8236 (a root's teardown leaves its cluster); turned in by owner directive. Next: none."),
    ("slotted_d2_team_store", "tickets/tasks/completed/2026-10-14_investigate_cluster_instance_not_rehomed_on_leader_change_task.md",
     "Landed 0.2.8237 (the cluster owns its team store); turned in by owner directive. Next: none."),
    ("slotted_d3_transfer_default", "tickets/tasks/completed/2026-10-14_investigate_stored_instances_dropped_without_disposal_task.md",
     "Landed 0.2.8239-0.2.8240 (transfer moves by default; handover docs); invalidation unchanged. Next: none."),
    ("slotted_d4_transfer_children", "tickets/tasks/completed/2026-10-14_investigate_transfer_leaves_holder_children_behind_task.md",
     "Landed 0.2.8238 (a moved holder's many children move with it); turned in. Next: none."),
    ("slotted_d5_purge_children", "tickets/tasks/completed/2026-10-14_investigate_purge_leaves_holder_children_registered_task.md",
     "Landed 0.2.8238 (purging a holder disposes its children, kept as landed); turned in. Next: none."),
    ("slotted_d6_upgrade", "tickets/tasks/completed/2026-10-14_investigate_upgrade_retained_holders_keep_old_dependencies_task.md",
     "No defect (upgrade_to_normal docstring with 0.2.8236); turned in by owner directive. Next: none."),
    ("slotted_lifetime_fixes", "tickets/epics/completed/2026-10-14_slotted_lifetime_ownership_fixes_epic.md",
     "Landed 0.2.8236-0.2.8240 as structure fixes; runtime model in the docs; turned in by owner directive. Next: none."),
]
i, j = region(t, "closed_anchors")
old_rows = [r for r in t[i:j].splitlines(keepends=True) if r.startswith("| ")]
new_rows = [f"| {w} | done | melder_1 | {ticket} | {note} | {NOW} |\n" for w, ticket, note in ANCHORS]
allrows = old_rows + new_rows
allrows.sort(key=lambda r: r.rstrip().rstrip("|").rsplit("|", 1)[-1].strip())
keep = allrows[-12:]
dropped = allrows[:-12]
t = t[:i] + "".join(r for r in allrows if r in keep) + t[j:]
board.write_bytes(t.encode("utf-8"))
print("attention board: 3 routes removed,", len(new_rows), "anchors added,", len(dropped), "oldest anchors dropped")

# --- artifact board --------------------------------------------------------------------------------------------
art = CC / "artifact_board.md"
t = art.read_bytes().decode("utf-8")
assert "\r\n" not in t
MOVES = {
    "tickets/tasks/2026-10-14_fix_many_child_follows_holder_task.md":
        "tickets/tasks/completed/2026-10-14_fix_many_child_follows_holder_task.md",
    "tickets/tasks/2026-10-14_fix_pool_decay_fake_clock_rounding_task.md":
        "tickets/tasks/completed/2026-10-14_fix_pool_decay_fake_clock_rounding_task.md",
    "tickets/epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md":
        "tickets/epics/completed/2026-10-14_slotted_lifetime_ownership_fixes_epic.md",
}
REASONS = {
    "artifacts/many_child_registration_20261014/": "Evidence of the 0.2.8235 landing: route and specializer probes, red and green runs, emission comparison, full-tree, graph, asset and bundle logs.",
    "artifacts/pool_decay_clock_rounding_20261014/": "The reproducer (100,000 clock origins) and the before/after, suite, rebuild and check runs of the test-only fix.",
    "artifacts/slotted_lifetime_audit_20261014/": "The audit's probe (eleven cases) and its runs, rerun before and after each fix of the lane.",
    "artifacts/slotted_lifetime_fixes_20261014/": "Evidence of the 0.2.8236-0.2.8240 landings: probes, red/green and full-tree runs, the audit probe and emission diff, benchmarks, rebuild logs and every apply, notch, docs, graph and turn-in script.",
}
i, j = region(t, "active_artifacts")
rows = t[i:j].splitlines(keepends=True)
kept, cleared = [], []
for r in rows:
    cells = [c.strip() for c in r.strip().strip("|").split("|")] if r.startswith("| ") else []
    if cells and cells[0] in MOVES and cells[1] in REASONS:
        cleared.append(f"| {MOVES[cells[0]]} | {cells[1]} | retain_as_reference | {REASONS[cells[1]]} | {NOW} |\n")
    else:
        kept.append(r)
assert len(cleared) == 4, len(cleared)
t = t[:i] + "".join(kept) + t[j:]
i, j = region(t, "cleared_artifacts")
body = t[i:j]
for old, new in MOVES.items():
    body = body.replace(f"| {old} | system_docs/patches/completed/", f"| {new} | system_docs/patches/completed/")
t = t[:i] + "".join(cleared) + body + t[j:]
art.write_bytes(t.encode("utf-8"))
print("artifact board: 4 rows cleared; patch rows repointed to completed tickets")
