"""Open the managed-shell investigation task under the managed_spell_quantity epic; board, epic and artifact rows."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TS = now_utc()
TASK_REL = "tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md"
EPIC_REL = "tickets/epics/2026-10-14_managed_spell_quantity_epic.md"
ART = "artifacts/managed_shell_spike_20261014/"

TASK = f"""# Task: Investigate the managed-shell design for `managed_spell_quantity` (three modes) with a VM spike

## Metadata
- Task ID: TASK-2026-10-14-investigate_managed_shell_design
- Story: none (epic-level investigation; Epic: EPIC-2026-10-14-managed_spell_quantity)
- Status: in_progress
- Owner: user
- Agent Name: fable_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: {TS}
- Updated: {TS}

## Objective
Answer, with source evidence and a working-copy spike, whether the owner's shell shape - a `ManagedShell` stored in
the owner store under the spell id, three modes (`limited_quantity`, `elastic`, `queue`), `ReleaseManagedSpell` as
the one way back hosting a `with`, `Conduit.managed_spell_meld("target")` over meld + release, a reset list at bind -
can be built with minimal change to the kernel and the same features; name the exact seams and their costs.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; the owner's direction in chat (2026-10-14, "could you investigate this
  idea? ... keep it simple and see what happens"); investigation and a spike on the VM working copy only.
- EXECUTION_BOUNDARY: reads of `existence.py`, `creations.py`, `conduit_creations.py`, the meld doors
  (`conduit_meld.py`, `spellspace_meld.py`, the warm lane of `conduit.py`), `spell.py` ownership stamping,
  `scope_ordering_strategy.py`, `abstract_elastic_pool.py`, `site_plan_lowering.py`; the spike lives under
  `{ART}` and `$HOME/work/melder_cc` (prototype module, probes, measurements). No tree `src/` edit.
- DEPENDENCIES: EPIC-2026-10-14-managed_spell_quantity (the decided design; melder_1's lane keeps the patch docs);
  0.2.8235/0.2.8238 (children follow the holder).
- EXIT_GATE: FACT notes on every seam with `path:start-end`; the spike runs the three modes through a captured plan
  and a hand-wired door on the working copy with measured acquire/release costs; a DECISION or DECISION_REQUEST on
  the two open points (out-record representation; binding mutation paths); the epic's Decision Log carries the
  owner's direction; the owner reads the result.
- FAILURE_ESCALATION: DECISION_REQUEST when the shell cannot keep an existing member's behaviour or the warm door's
  shape; BLOCKER if a release path cannot stay off the existing lock chains.

## Scope Boundaries
- In scope: reading the seams, a standalone shell + singleton prototype, a captured-plan and door experiment,
  measurements, the written assessment.
- Out of scope: any tree `src/` or `tests/` change; patch docs and stories (melder_1's lane); MelderOps.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened on the owner's direction ({TS}).

## Steps / Checklist
- [ ] Read the seams whole: the Existence enum and the resolution matrix, Creations publish/purge/cleanup and the
      disposal walk, ConduitCreations, the warm lane and the creation-context doors, `_add_owned_conduit`, Phase 6
      ranks, the elastic pool base; one FACT note per seam.
- [ ] Spike on the working copy: `ManagedShell` (three modes), `ReleaseManagedSpell` (weak index, `with`), a
      captured plan with one site rewritten to `sh.acquire()` + reserve/publish miss, a hand-wired door; measure.
- [ ] DECISION / DECISION_REQUEST notes: out-record representation, binding mutation paths, the door route.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The seam map with evidence; the spike module and probes under the artifacts folder; measured costs; the
  written recommendation for the patch docs.

## Files / Paths Impacted
- {ART} (prototype, probes, logs)
- tickets/epics/2026-10-14_managed_spell_quantity_epic.md (Decision Log and Notes, additive)

## Validation
- Not run.
- Recommended commands:
  - `python -X gil=0 context_compass/artifacts/managed_shell_spike_20261014/<probe>.py` on the VM working copy

## Risks / Rollback Notes
- The spike is scratch; nothing lands. Risk: the shell changes what `store._creations.get(sid)` returns for a
  managed spell, so every reader of a store must be found (purge, extract, transfer, teardown, the doors).

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.
- [ ] No tree edit from an investigation task.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - {ART}
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: kept as the epic's design evidence.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the managed shell in the owner store; the three modes; the release singleton; the door and plan seams
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): fable_0 (synaptic_python_developer); the whole ticket and the spike; initial
  revision {TS}
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: {TS}
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened on the owner's direction (chat 2026-10-14): investigate the shell shape - the managed object
    "managed in creations as a special interface", a shell in the Creations store that "pulls out the object
    required in the
    required ways or inserts it back", looked up by spell id like today, root-owned; `ReleaseManagedSpell` as the
    one way back, hosting a `with`; `Conduit.managed_spell_meld("target")`; protocol and mixins dropped; a reset
    list at bind; the three modes `limited_quantity`, `elastic`, `queue`; "the most minimal change ... the same
    features ... keep it simple and see what happens". The assessment that preceded it (chat, 2026-10-14) named four
    gaps: the out-record representation, the miss ordering (reserve before children), binding mutation paths, and
    injection into slotted holders.
  EVIDENCE:
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:1-120
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:238-275
  IMPACT: Reading order fixed: the store and its readers first (what a shell in the store touches), then the doors,
    then the lowering, then the spike.
  NEXT: read `creations.py` whole in chunks and list every reader of `_creations` values.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE {TS}: IN_PROGRESS. Opened; nothing read yet beyond the epic. Resume from the latest note's NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
"""
bad = check_line_lengths(TASK, exempt=r"^(  - |- `|\||  `)")
if bad:
    raise SystemExit(f"task lines over cap: {bad}")
path = os.path.join(CC, TASK_REL)
assert not os.path.exists(path)
write_text(path, TASK, "\n")
print("task written")

# --- epic: Decision Log entry + tasks line + note (additive) ---
epic = os.path.join(CC, EPIC_REL)
text, nl = read_text(epic)
decision = (
    "- 2026-10-14 (chat with fable_0): the simplest path - `ReleaseManagedSpell` is the one way back and hosts a\n"
    "  `with`; a new `Conduit.managed_spell_meld(\"target\")` is the meld-plus-release form; protocol and mixins\n"
    "  dropped; the object is \"managed in creations as a special interface\": a shell in the Creations store, looked\n"
    "  up by spell id like today, that pulls the object out in the mode's way or puts it back; the root owns it; a\n"
    "  reset list at bind (`managed_spell_reset_methods=[]`); the three modes `limited_quantity`, `elastic`,\n"
    "  `queue`; \"we need the most minimal change here and the same features and keep it easy\". fable_0 opened\n"
    "  TASK-2026-10-14-investigate_managed_shell_design to investigate it with a VM spike (\"see what happens\").\n"
)
text = replace_once(
    text,
    "- 2026-10-14: pools stay with root scopes - the root that owns the binding",
    decision + "- 2026-10-14: pools stay with root scopes - the root that owns the binding",
    "decision log head")
text = replace_once(
    text,
    "- [ ] Task: Benchmark meld, lease and release costs on the reference VM before and after each milestone.\n",
    "- [ ] Task: TASK-2026-10-14-investigate_managed_shell_design (fable_0) - the owner's shell shape investigated\n"
    f"      with a VM spike; feeds the patch docs. {TASK_REL}\n"
    "- [ ] Task: Benchmark meld, lease and release costs on the reference VM before and after each milestone.\n",
    "epic tasks")
note = (
    f"- DATETIME: {TS}\n"
    "  AUTHOR: fable_0\n"
    "  AUTHOR_ROLE: synaptic_python_developer\n"
    "  TYPE: DECISION\n"
    "  CLAIM: Owner direction recorded (Decision Log, 2026-10-14, chat with fable_0): the shell-in-creations shape with\n"
    "    one way back and the three modes; investigation opened as TASK-2026-10-14-investigate_managed_shell_design\n"
    "    (fable_0), a read-and-spike lane that does not touch the tree. fable_0's review of this epic (chat,\n"
    "    2026-10-14) stands as its independent review: the decided core holds against 0.2.8238; four points to settle\n"
    "    before the patch docs - what the out-record holds (recommended: a weak index whose callback frees the\n"
    "    place), reserve-before-children in a managed miss, binding mutation paths (notch, cleanup_spell, transfer),\n"
    "    and injection into slotted holders (a lease for the holder's life; limited pools exhaust).\n"
    "  EVIDENCE:\n"
    f"  - {TASK_REL}:1-60\n"
    "  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:238-275\n"
    "  IMPACT: melder_1 keeps the lane (patch docs and stories); the task's findings feed Milestone 1.\n"
    "  NEXT: the investigation task's seam reads and spike; the owner answers (a)-(j) and the four points.\n"
    "  REREAD: REQUIRED\n"
    "  SCORE_0_TO_10: 8\n\n"
)
for block in (decision, note):
    bad = check_line_lengths(block, exempt=r"^  - tickets/")
    if bad:
        raise SystemExit(f"epic lines over cap: {bad}")
text = replace_once(text, "\n## Closure Confirmation\n", "\n" + note + "## Closure Confirmation\n", "epic notes end")
text = replace_once(
    text, "- Independent Review: none yet\n",
    "- Independent Review: fable_0 (synaptic_python_developer); the design as of 2026-10-14T17:19:37Z; verdict in the\n"
    f"  DECISION note of {TS}; independent of the author's lane\n", "epic review")
write_text(epic, text, nl)
print("epic updated")

# --- attention board ---
bp = os.path.join(CC, "attention_board.md")
board, nl = read_text(bp)
row = (
    "| managed_shell_spike | in_progress | discovery | claude | fable_0 | none | Read the store, door and lowering seams "
    "whole, then the shell/singleton spike on the VM copy with the three modes and measured costs. | The owner's shell "
    "shape proven or refuted with evidence and numbers; the two open points decided or raised. | Spike measured and "
    f"the recommendation written, or the owner redirects. | {TASK_REL} | {TS} | REQUIRED |\n"
)
board = replace_once(board, "<!-- END USER-DEFINED: active_items -->\n", row + "<!-- END USER-DEFINED: active_items -->\n",
                     "active items end")
details = (
    "- WORK_ITEM: managed_shell_spike\n"
    "  SWITCH_TRIGGER: Spike measured and the recommendation written into the task and the epic, or the owner\n"
    "  redirects.\n"
    "  RESUME_HIERARCHY:\n"
    "    - tickets/epics/2026-10-14_managed_spell_quantity_epic.md\n"
    f"    - {TASK_REL}\n"
)
board = replace_once(board, "<!-- END USER-DEFINED: active_attention_details -->\n",
                     details + "<!-- END USER-DEFINED: active_attention_details -->\n", "details end")
write_text(bp, board, nl)
print("board updated")

# --- artifact board ---
ap = os.path.join(CC, "artifact_board.md")
art, nl = read_text(ap)
arow = (
    f"| {TASK_REL} | {ART} | design_spike | active | retain_as_reference | The shell/singleton prototype, the "
    f"captured-plan and door probes, measurements and logs. | {TS} | REQUIRED |\n"
)
art = replace_once(art, "<!-- BEGIN USER-DEFINED: active_artifacts -->\n",
                   "<!-- BEGIN USER-DEFINED: active_artifacts -->\n" + arow, "active artifacts begin")
write_text(ap, art, nl)
print("artifact board updated", TS)
