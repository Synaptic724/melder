"""Route meld_contract_scan to TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
The closure sync of TASK-2026-10-15-make_meld_state_checks_follow_spell_state (done 2026-10-16T09:36:46Z) with its
successor: attention_board.md - the active row and its detail entry move to the successor, one closed anchor is
added and the oldest dropped (12 kept); artifact_board.md - the lane folder's row moves to the successor, the closed
ticket gets a cleared row, and the archived patch lane's cleared row names the completed path. Every edit is an
exact-text replacement that must match once; both boards are re-read here, just before writing, and read back.
--check writes nothing.
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
OLD = "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
DONE = "tickets/tasks/completed/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
NEW = "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"
CLOSED_AT = "2026-10-16T09:36:46Z"
EXIT = "The owner-approved change lands with tests, docs, notch and rebuild, or the owner redirects."

ATTENTION = [
    (
        "| meld_contract_scan | review | handoff | claude | melder_1 | owner: accept rule 1 (0.2.8247); decide items"
        " (2)-(3) | Owner accepts rule 1 (0.2.8247) and answers items (2)-(3): should the contract check run only when"
        " the melded spell's state calls for it? | resolvable=False spells never hold the meld gate open; the contract"
        " check runs only when the melded spell's state calls for it. | The owner accepts 0.2.8247 and answers items"
        f" (2)-(3), or the owner redirects. | {OLD} | 2026-10-16T01:51:00Z | REQUIRED |\n",
        "| meld_contract_scan | in_progress | discovery | claude | melder_1 | none | Re-read the meld's contract check"
        " and every change of a borrower's contracted copy whole, then write the patch docs. | A satisfied"
        " SpellContract is not checked on every meld; a provider change (a notch) marks its consumers for a recheck at"
        f" their next meld. | {EXIT} | {NEW} | {NOW} | REQUIRED |\n",
    ),
    (
        "- WORK_ITEM: meld_contract_scan\n"
        "  SWITCH_TRIGGER: The owner accepts 0.2.8247 and answers items (2)-(3), or the owner redirects.\n"
        "  RESUME_HIERARCHY:\n"
        f"    - {OLD}\n",
        "- WORK_ITEM: meld_contract_scan\n"
        f"  SWITCH_TRIGGER: {EXIT}\n"
        "  RESUME_HIERARCHY:\n"
        f"    - {NEW}\n",
    ),
    (
        "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
        "| slotted_d4_transfer_children | done | melder_1 |"
        " tickets/tasks/completed/2026-10-14_investigate_transfer_leaves_holder_children_behind_task.md | Landed"
        " 0.2.8238 (a moved holder's many children move with it); turned in. Next: none. | 2026-10-15T01:38:07Z |\n",
        "<!-- BEGIN USER-DEFINED: closed_anchors -->\n",
    ),
    (
        "| managed_ownership_transfer | done | melder_0 |"
        " tickets/stories/completed/2026-10-15_managed_ownership_transfer_story.md | Landed 0.2.8246 (S6 of"
        " EPIC-2026-10-14-managed_spell_quantity: the owner stamp follows a transfer's lineage both ways,"
        " `discard_managed_quantity`). Next: S7 docs. | 2026-10-15T21:00:54Z |\n"
        "<!-- END USER-DEFINED: closed_anchors -->\n",
        "| managed_ownership_transfer | done | melder_0 |"
        " tickets/stories/completed/2026-10-15_managed_ownership_transfer_story.md | Landed 0.2.8246 (S6 of"
        " EPIC-2026-10-14-managed_spell_quantity: the owner stamp follows a transfer's lineage both ways,"
        " `discard_managed_quantity`). Next: S7 docs. | 2026-10-15T21:00:54Z |\n"
        f"| non_resolvable_book_flag | done | melder_1 | {DONE} | Landed 0.2.8247 (a resolvable=False lineage no longer"
        " holds its Book's validation flag); owner accepted. Next: rule 2 in"
        f" TASK-2026-10-16-recheck_contract_consumers_when_provider_changes. | {CLOSED_AT} |\n"
        "<!-- END USER-DEFINED: closed_anchors -->\n",
    ),
]

FOLDER_NEXT_OLD = (
    "Git-history and ticket-search logs, the gate probes and their runs (the predecessor's trace), the open and closure"
    " scripts; the fix lane's apply scripts (apply_*.py, CRLF-preserving), probes (design, borrower notch-back,"
    " before/after), suite, mutation and probe runs (runs/), and Note scripts; the 0.2.8247 landing's doc, graph and"
    " release-note scripts, the landed-tree suite, probe and example runs and the rebuild logs."
)
FOLDER_NEXT_NEW = (
    "The lane's shared folder: the trace's logs, gate probes and runs; rule 1's (0.2.8247) apply scripts, probes,"
    " suite, mutation and probe runs, doc, graph and release-note scripts and rebuild logs; the open, closure and"
    " board scripts. Rule 2's design evidence starts here (probe_design_baseline.py: the borrower contract consumer);"
    " its probes and runs land beside it."
)
ARTIFACT = [
    (
        f"| {OLD} | artifacts/meld_contract_scan_20261015/ | investigation_evidence | active | retain_as_reference |"
        f" {FOLDER_NEXT_OLD} | 2026-10-16T01:42:28Z | REQUIRED |\n",
        f"| {NEW} | artifacts/meld_contract_scan_20261015/ | investigation_evidence | active | retain_as_reference |"
        f" {FOLDER_NEXT_NEW} | {NOW} | REQUIRED |\n",
    ),
    (
        "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
        f"| {OLD} | system_docs/patches/completed/meld_state_gate_2026_10_15/ | promote_to_documentation |",
        "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
        f"| {DONE} | artifacts/meld_contract_scan_20261015/ | retain_as_reference | Rule 1 closed (0.2.8247,"
        " owner-accepted); the folder stays rowed under"
        " TASK-2026-10-16-recheck_contract_consumers_when_provider_changes as its evidence."
        f" | {CLOSED_AT} |\n"
        f"| {DONE} | system_docs/patches/completed/meld_state_gate_2026_10_15/ | promote_to_documentation |",
    ),
]


def apply(path, edits):
    """Apply exact-text edits to one LF board; each old text must occur exactly once."""
    board = pathlib.Path(path)
    text = board.read_bytes().decode("ascii")
    assert "\r" not in text, path
    for old, new in edits:
        assert text.count(old) == 1, (path, text.count(old), old[:80])
        text = text.replace(old, new)
    if not CHECK:
        board.write_bytes(text.encode("ascii"))
        assert board.read_bytes().decode("ascii") == text, path
    return text


attention = apply("attention_board.md", ATTENTION)
artifact = apply("artifact_board.md", ARTIFACT)

# Invariants: no active row routes to the old or the completed path; the detail entry matches the row; 12 anchors.
active = attention.split("<!-- BEGIN USER-DEFINED: active_items -->\n")[1].split("<!-- END USER-DEFINED")[0]
details = attention.split("<!-- BEGIN USER-DEFINED: active_attention_details -->\n")[1].split("<!-- END")[0]
anchors = attention.split("<!-- BEGIN USER-DEFINED: closed_anchors -->\n")[1].split("<!-- END")[0]
for row in active.strip("\n").split("\n"):
    ticket = row.split(" | ")[9]
    assert "/completed/" not in ticket and ticket != OLD, row[:80]
    assert pathlib.Path(ticket).is_file() or CHECK and ticket == NEW, ticket
assert f"  SWITCH_TRIGGER: {EXIT}\n  RESUME_HIERARCHY:\n    - {NEW}\n" in details
assert len(anchors.strip("\n").split("\n")) == 12, len(anchors.strip("\n").split("\n"))
assert OLD not in active and OLD not in details
art_active = artifact.split("<!-- BEGIN USER-DEFINED: active_artifacts -->\n")[1].split("<!-- END")[0]
assert f"| {OLD} |" not in artifact and f"| {NEW} | artifacts/meld_contract_scan_20261015/ |" in art_active
print("checked" if CHECK else "written", NOW)
