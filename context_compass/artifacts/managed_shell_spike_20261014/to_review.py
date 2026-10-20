"""Task -> review (the owner reads the result); board row and artifact row synced in the same pass."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK = os.path.join(CC, "tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md")
BOARD = os.path.join(CC, "attention_board.md")
ARTS = os.path.join(CC, "artifact_board.md")
TS = now_utc()

# --- the task ---
text, nl = read_text(TASK)
text = replace_once(text, "- Status: in_progress\n", "- Status: review\n", "status")
text = replace_once(
    text,
    "## State Transition Event\n- from_state: draft\n- to_state: in_progress\n"
    "- transition_reason: Opened on the owner's direction (2026-10-14T22:15:12Z).\n",
    "## State Transition Event\n- from_state: in_progress\n- to_state: review\n"
    f"- transition_reason: Seams read, spike measured, DECISION and DECISION_REQUEST written, the epic's\n"
    f"  Decision Log carries the result; the owner reads it and rules on the four points ({TS}).\n"
    "  Previous: draft -> in_progress, opened on the owner's direction (2026-10-14T22:15:12Z).\n",
    "transition")
text = replace_once(text, "- [ ] Run Ticket Microcycle during execution:\n", "- [x] Run Ticket Microcycle during execution:\n", "step4")
text = replace_once(text, "- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.\n",
                    "- [x] Document each meaningful finding immediately in `## Notes` before further investigation.\n", "step5")
text = replace_once(
    text,
    "## Validation\n- Not run.\n- Recommended commands:\n"
    "  - `python -X gil=0 context_compass/artifacts/managed_shell_spike_20261014/<probe>.py` on the VM working copy\n",
    "## Validation\n- Run on the VM (CPython 3.14.7t, `-X gil=0`, caching off): `probe_modes.py` run 2 ALL OK (15/15);\n"
    "  `probe_cost_variants.py`, `probe_plan_shape.py` and `probe_door_modes.py` printed the figures in the MEASURE\n"
    "  notes; logs under `artifacts/managed_shell_spike_20261014/logs/`. No tree test suite was run (no tree change).\n"
    "- Recommended commands:\n"
    "  - `python -X gil=0 context_compass/artifacts/managed_shell_spike_20261014/<probe>.py` on the VM working copy\n"
    "    (`probe_plan_shape.py` and `probe_plan_capture.py` need `tests/experimentation` on the path)\n",
    "validation")
text = replace_once(
    text,
    "## Context / Handoff Summary\nSTATE 2026-10-14T22:15:12Z: IN_PROGRESS. Opened; nothing read yet beyond the epic. "
    "Resume from the latest note's NEXT.\n",
    f"## Context / Handoff Summary\nSTATE {TS}: REVIEW. The seams are read (FACT), the spike ran on the 0.2.8238\n"
    "copy (two MEASURE notes), the shape is decided where the evidence decides it (DECISION) and four rulings are\n"
    "the owner's (DECISION_REQUEST); the epic's Decision Log and Notes carry the result. The prototype and probes\n"
    "stay under the artifacts folder (retain_as_reference). Waiting on the owner's reading; nothing landed in the\n"
    "tree. Resume: the owner's rulings go to the epic's Decision Log (melder_1's patch docs follow), then this\n"
    "task closes.\n",
    "handoff")
text = replace_once(
    text,
    "  `artifacts/managed_shell_spike_20261014/` and `$HOME/work/melder_cc` (prototype module, probes, measurements). "
    "No tree `src/` edit.\n",
    "  `artifacts/managed_shell_spike_20261014/` and `$HOME/work/melder_cc` (prototype module, probes,\n"
    "  measurements). No tree `src/` edit.\n",
    "boundary line")
text = re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=re.MULTILINE)
bad = check_line_lengths(text, exempt=r"^  - (context_compass|src|tickets)/|^    \(`probe_plan")
if bad:
    raise SystemExit(f"task lines over cap: {bad}")
write_text(TASK, text, nl)

# --- the attention board row (status review, mode handoff) ---
board, bnl = read_text(BOARD)
old_row = ("| managed_shell_spike | in_progress | discovery | claude | fable_0 | none | Read the store, door and lowering "
           "seams whole, then the shell/singleton spike on the VM copy with the three modes and measured costs. | The "
           "owner's shell shape proven or refuted with evidence and numbers; the two open points decided or raised. | "
           "Spike measured and the recommendation written, or the owner redirects. | "
           "tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md | 2026-10-14T22:15:12Z | REQUIRED |")
new_row = ("| managed_shell_spike | review | handoff | claude | fable_0 | none | Owner reads the task's MEASURE and "
           "DECISION notes and rules on the four DECISION_REQUEST points; then the task closes. | The shell shape "
           "measured on 0.2.8238 with the minimal change set and four rulings requested. | The owner rules (or "
           "redirects) and the task is turned in. | tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md "
           f"| {TS} | REQUIRED |")
board = replace_once(board, old_row, new_row, "board row")
board = replace_once(
    board,
    "- WORK_ITEM: managed_shell_spike\n  SWITCH_TRIGGER: Spike measured and the recommendation written into the task "
    "and the epic, or the owner\n  redirects.\n",
    "- WORK_ITEM: managed_shell_spike\n  SWITCH_TRIGGER: The owner rules (or redirects) and the task is turned in.\n",
    "details")
write_text(BOARD, board, bnl)

# --- the artifact row ---
arts, anl = read_text(ARTS)
old_art = ("| tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md | artifacts/managed_shell_spike_20261014/ | "
           "design_spike | active | retain_as_reference | The shell/singleton prototype, the captured-plan and door "
           "probes, measurements and logs. | 2026-10-14T22:15:12Z | REQUIRED |")
new_art = ("| tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md | artifacts/managed_shell_spike_20261014/ | "
           "design_spike | active | retain_as_reference | The shell/singleton prototype (`managed_shell.py`), the "
           "modes, cost-variant, captured-plan and door-mode probes, their logs and the note scripts; kept as the "
           f"epic's design evidence. | {TS} | REQUIRED |")
arts = replace_once(arts, old_art, new_art, "artifact row")
write_text(ARTS, arts, anl)
print("review", TS)
