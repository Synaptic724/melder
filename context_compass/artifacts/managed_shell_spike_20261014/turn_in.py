"""Turn in TASK-2026-10-14-investigate_managed_shell_design: closure lines, move, board and artifact sync."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
ACTIVE = "tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md"
DONE = "tickets/tasks/completed/2026-10-14_investigate_managed_shell_design_task.md"
TASK = os.path.join(CC, ACTIVE)
EPIC = os.path.join(CC, "tickets/epics/2026-10-14_managed_spell_quantity_epic.md")
BOARD = os.path.join(CC, "attention_board.md")
ARTS = os.path.join(CC, "artifact_board.md")
TS = now_utc()

# --- the task ---
text, nl = read_text(TASK)
title = "# Task: Investigate the managed-shell design for `managed_spell_quantity` (three modes) with a VM spike\n"
text = replace_once(
    text, title,
    title + f"\n- Completed: {TS}\n"
    "- Summary: The owner's shell shape investigated on the 0.2.8238 copy and reshaped with him in chat: the Spell\n"
    "  keeps the options, `ManagedSpellQuantity(deque)` of idle objects in the root's Creations, `ReleaseManagedSpell`\n"
    "  keyed by class to `(holder, spell_id)`, release = optional reset + append; measured 90-265 ns per lease cycle.\n"
    "  The settled shape, seam map, numbers and implementation plan are in the epic's Notes (2026-10-14T23:45:47Z).\n"
    "  No source landed (no notch); the spike is retained under the epic.\n",
    "title")
text = replace_once(text, "- Status: review\n", "- Status: done\n", "status")
text = replace_once(
    text,
    "## State Transition Event\n- from_state: in_progress\n- to_state: review\n",
    f"## State Transition Event\n- from_state: review\n- to_state: done\n"
    f"- transition_reason: The owner read the result, ruled the four points and the deque shape, and handed\n"
    f"  implementation to the next agent (chat 2026-10-14); the epic carries the handoff notes ({TS}).\n"
    "- previous: from_state: in_progress\n- to_state: review\n",
    "transition")
for line in ("- [ ] Steps complete and checked off\n", "- [ ] Deliverables produced and linked\n",
             "- [ ] Documentation updated (if needed)\n", "- [ ] Validation status recorded\n",
             "- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)\n",
             "- [ ] Applicable anti-pattern checks are clear or escalated with evidence.\n",
             "- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n",
             "- [ ] Board sync completed for successor routing or closure anchor update.\n",
             "- [ ] No status transition without evidence-backed transition reason.\n",
             "- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.\n",
             "- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.\n",
             "- [ ] No tree edit from an investigation task.\n"):
    text = replace_once(text, line, line.replace("- [ ]", "- [x]", 1), line)
text = replace_once(text, "- [ ] Notes quality maintained (`SCORE_0_TO_10` >=\n", "- [x] Notes quality maintained (`SCORE_0_TO_10` >=\n", "notes q")
text = replace_once(
    text,
    "- Independent Review: none yet\n",
    "- Independent Review: the owner, in chat (2026-10-14): the four points ruled, the deque shape chosen; accepted\n"
    "  as the reserved-owner disposition (\"I'll get opus to do the rest\")\n",
    "review")
text = re.sub(r"^STATE 2026-10-14T23:08:03Z: REVIEW\.", f"STATE {TS}: DONE (was REVIEW).", text, count=1,
              flags=re.MULTILINE)
text = re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=re.MULTILINE)
bad = check_line_lengths(text, exempt=r"^  - (context_compass|src|tickets)/|^    \(`probe_plan")
if bad:
    raise SystemExit(f"task lines over cap: {bad}")
write_text(TASK, text, nl)
os.replace(TASK, os.path.join(CC, DONE))

# --- the epic: my evidence pointers at the active path follow the move ---
epic, enl = read_text(EPIC)
n = epic.count(ACTIVE + ":")
epic = epic.replace(ACTIVE + ":", DONE + ":")
write_text(EPIC, epic, enl)

# --- attention board: remove the row and its details entry, add the closed anchor (cap 12) ---
board, bnl = read_text(BOARD)
row_start = board.index("| managed_shell_spike | review | handoff |")
row_end = board.index("\n", row_start) + 1
board = board[:row_start] + board[row_end:]
board = replace_once(
    board,
    "- WORK_ITEM: managed_shell_spike\n  SWITCH_TRIGGER: The owner rules (or redirects) and the task is turned in.\n"
    "  RESUME_HIERARCHY:\n    - tickets/epics/2026-10-14_managed_spell_quantity_epic.md\n"
    "    - tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md\n",
    "", "details entry")
oldest = ("| codecov_upload_tls | done | melder_1 | tickets/tasks/completed/2026-10-05_diagnose_codecov_upload_tls_failure_task.md "
          "| Codecov TLS diagnosis and PyPI-uploader retry (no notch); turned in by owner directive. Next: none. | 2026-10-12T21:14:45Z |\n")
board = replace_once(board, oldest, "", "oldest anchor")
anchor = (f"| managed_shell_spike | done | fable_0 | {DONE} | Shell/deque investigation for managed_spell_quantity (no notch); "
          f"the settled shape and plan are in the epic's Notes. Next: implementation by the owner's next agent. | {TS} |\n")
board = replace_once(board, "<!-- END USER-DEFINED: closed_anchors -->", anchor + "<!-- END USER-DEFINED: closed_anchors -->", "anchors end")
write_text(BOARD, board, bnl)

# --- artifact board: the task row -> cleared (retained), one active row under the epic ---
arts, anl = read_text(ARTS)
row_start = arts.index("| tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md | artifacts/managed_shell_spike_20261014/ |")
row_end = arts.index("\n", row_start) + 1
arts = arts[:row_start] + arts[row_end:]
epic_row = ("| tickets/epics/2026-10-14_managed_spell_quantity_epic.md | artifacts/managed_shell_spike_20261014/ | design_spike | "
            "active | retain_as_reference | The deque-holder probe (the settled shape), the earlier shell prototype and its probes, the "
            f"captured-plan and door probes, logs and note scripts; the epic's design and benchmark evidence. | {TS} | REQUIRED |\n")
arts = replace_once(arts, "<!-- END USER-DEFINED: active_artifacts -->", epic_row + "<!-- END USER-DEFINED: active_artifacts -->", "active end")
cleared = (f"| {DONE} | artifacts/managed_shell_spike_20261014/ | retain_as_reference | Investigation closed; the folder stays "
           f"rowed under EPIC-2026-10-14-managed_spell_quantity as its design evidence. | {TS} |\n")
arts = replace_once(arts, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n", "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n" + cleared, "cleared head")
write_text(ARTS, arts, anl)
print("turned in", TS, "| epic pointers moved:", n)
