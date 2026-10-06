"""
Open work package C of the injected-provider epic on the owner's pick (option B, 2026-09-30).

Usage: python open_lane.py <context_compass root>
Closes the reproduce task (its DECISION_REQUEST answered), records the pick on the epic, writes the new task
ticket, and syncs the attention and artifact boards. The reproduce task's move into completed/ is the caller's.
"""
import datetime
import pathlib
import sys

CC = pathlib.Path(sys.argv[1])
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
REPRO = "tickets/tasks/2026-09-30_reproduce_injected_provider_direct_meld_task.md"
EPIC = "tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md"
TASK = "tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md"
TASK_DONE_REPRO = "tickets/tasks/completed/2026-09-30_reproduce_injected_provider_direct_meld_task.md"


def swap(text: str, old: str, new: str, label: str) -> str:
    """Replace one exact block or stop."""
    if text.count(old) != 1:
        raise SystemExit(f"{label}: anchor count {text.count(old)}: {old[:90]!r}")
    return text.replace(old, new)


def line_of(text: str, needle: str) -> int:
    """Return the 1-based line of the first line containing `needle`."""
    return next(i for i, line in enumerate(text.split("\n"), 1) if needle in line)


# Reproduce task: record the pick, close it.
repro = (CC / REPRO).read_bytes().decode("utf-8")
if "\r\n" in repro:
    raise SystemExit("reproduce task: unexpected CRLF")
request_start = line_of(repro, "  TYPE: DECISION_REQUEST")
request_end = line_of(repro, "  NEXT: Owner picks A, B or C (or drops it)")
repro = swap(repro, "- Status: review\n", "- Status: done\n", REPRO)
updated = next(line for line in repro.split("\n") if line.startswith("- Updated: "))
repro = swap(
    repro, updated + "\n",
    f"- Updated: {NOW}\n- Completed: {NOW}\n"
    "- Closure Basis: the owner's pick of option B in chat (2026-09-30) and the owner's turn-in of finished work\n"
    "  (\"turn in the [work] you did then work on the next thing\").\n"
    "- Summary: Reproduced on bare Melder (0.2.8212, confirmed on 0.2.8214): a provider bound after conjure and first\n"
    "  built as a consumer's dependency could not be melded directly afterwards. Cause: the consumer's target pass\n"
    "  published only the consumer yet stamped the provider's conduit verdict valid. The owner picked option B;\n"
    f"  work package C continues in {TASK}.\n",
    REPRO,
)
start = repro.index("## State Transition Event\n")
end = repro.index("\n## ", start + 5)
repro = (repro[:start] + "## State Transition Event\n- from_state: review\n- to_state: done\n"
         f"- transition_reason: ({NOW}) the owner picked option B; the repair continues in its own task. Earlier:\n"
         "  in_progress -> review (2026-09-30T16:33:36Z), draft -> in_progress (2026-09-30T16:18:36Z).\n" + repro[end:])
for box in ("- [ ] Steps complete and checked off", "- [ ] Deliverables produced and linked",
            "- [ ] Documentation updated (if needed)", "- [ ] Validation status recorded",
            "- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)",
            "- [ ] Notes quality maintained (`SCORE_0_TO_10` >=",
            "- [ ] Applicable anti-pattern checks are clear or escalated with evidence.",
            "- [ ] Acceptance criteria reviewed with user and confirmed",
            "- [ ] Board sync completed for successor routing or closure anchor update.",
            "- [ ] No status transition without evidence-backed transition reason.",
            "- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.",
            "- [ ] No closure without acceptance confirmation and board-sync completion.",
            "- [ ] No catch-and-retry or guard removal proposed as the repair before the cause is established."):
    if box in repro:
        repro = repro.replace(box, "- [x]" + box[5:])
note = f"""
- DATETIME: {NOW}
  TYPE: DECISION
  CLAIM: Owner pick (chat, 2026-09-30): option B - "B: auto-resolve on first meld (Recommended)" - then "before you
    start please make a regression test then fix it" and "or multiple tests". The owner's recollection that the
    mechanism already existed ("we just flag it and it should revalidate ... this was a spellsystemstate before")
    holds: SpellSystemStates keeps the per-conduit verdict and melds revalidate when it is not valid; the defect is
    that the consumer's pass stamps the provider valid without its plan. The failure still reproduces on 0.2.8214
    (runs_0_2_8214/). Work package C continues in {TASK}.
  EVIDENCE:
  - {REPRO}:{request_start}-{request_end}
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs_0_2_8214/diagnostic_cacheoff.txt:1-1
  IMPACT: This task's question is answered and its repair is picked; it closes with its successor opened.
  NEXT: none for this ticket.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9
"""
repro = swap(repro, "\n## Context / Handoff Summary\n", note + "\n## Context / Handoff Summary\n", REPRO)
(CC / REPRO).write_bytes(repro.encode("utf-8"))
print("closed", REPRO, request_start, request_end)

# Epic (CRLF): record the pick and the successor task.
epic = (CC / EPIC).read_bytes().decode("utf-8")
if "\r\n" not in epic:
    raise SystemExit("epic: expected CRLF")
epic_note = f"""
- DATETIME: {NOW}
  TYPE: DECISION
  CLAIM: Owner pick for work package C (chat, 2026-09-30): option B - the consumer's target pass flags each owned
    dependency that has no plan of its own with resolution_required, and that dependency's first direct meld runs
    its own full resolution pass through the deferred lane, returning the instance its scope already holds. No
    caller step, no public trigger (the owner chose B alone), verdicts and the Book validation flag unchanged. The
    owner asked for regression tests first ("make a regression test then fix it", "or multiple tests"). The
    reproduce task is turned in; work package C runs in {TASK}.
  EVIDENCE:
  - {TASK_DONE_REPRO}:{request_start}-{request_end}
  - tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md:552-571
  IMPACT: The repair is fixed to one option; the epic's exit gate now waits on C (red-to-green regressions, notch,
    docs) and D (the owner's wheel delivery to MelderOps).
  NEXT: Regression tests in {TASK}, run red, then the fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""
epic_lf = epic.replace("\r\n", "\n")
epic_lf = swap(epic_lf, "\n## Context / Handoff Summary\n", epic_note + "\n## Context / Handoff Summary\n", EPIC)
epic_updated = next(line for line in epic_lf.split("\n") if line.startswith("- Updated: "))
epic_lf = swap(epic_lf, epic_updated + "\n", f"- Updated: {NOW}\n", EPIC)
epic_lf = epic_lf.rstrip("\n") + (
    "\n\n2026-09-30 (melder_0): the owner picked repair option B; work package C runs in\n"
    f"{TASK} (regression tests first, then the fix).\n"
)
(CC / EPIC).write_bytes(epic_lf.replace("\n", "\r\n").encode("utf-8"))
print("epic updated")

# The work package C task.
TICKET = f"""

# Task: Let a provider bound after conjure be melded directly after it was injected (resolve on first direct meld)

## Metadata
- Task ID: TASK-2026-09-30-resolve-injected-provider-on-first-direct-meld
- Epic: tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md (work package C); follows
  {TASK_DONE_REPRO}
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: {NOW}
- Updated: {NOW}

## Objective
Owner pick (chat, 2026-09-30): option B of the reproduce task's DECISION_REQUEST, with "before you start please
make a regression test then fix it" and "or multiple tests". A provider bound after conjure and first built as a
consumer's dependency must be meldable directly afterwards and return the instance its scope already holds. The
consumer's target-local resolution pass flags each dependency its Book owns that has no plan of its own with
`resolution_required` (the per-spell flag every meld door reads), and the deferred lane runs the spell's full
target pass (phases 5-11) when it has no Phase 5 root blueprint, keeping today's 8-11 pass otherwise. Warm melds,
conduit verdicts and the Book validation flag are unchanged; no caller step and no public trigger.

## Ticket Contract
- ENTRY_GATE: the owner's pick; this board row; the regression tests written and run red before any src edit; the
  patch docs and a mailbox NOTICE before any src edit.
- EXECUTION_BOUNDARY: src/melder/aether/spellbook/spellbook_creation_system.py (the target pass tail) and
  src/melder/aether/conduit/meld/meld.py (the deferred lane), docstrings that state the old rule, their tests, the
  system docs, graph descriptors, the release note and __version__.
- DEPENDENCIES: the reproduce task (cause, matrix, probe); the epic's relayed owner contract (no caller step).
- EXIT_GATE: the regression tests red, then green; the epic's diagnostic probe passes on the tree; the meld,
  spellbook, conduit and aether suites green; docs, graph, release note, notch 0.2.8215, assets and LLM bundles
  with --check OK.
- FAILURE_ESCALATION: a DECISION_REQUEST if the fix needs anything beyond the two files (RiskManager, verdict
  semantics, a public API); BLOCKER if the VM cannot run the suites.

## Scope Boundaries
- In scope: option B; regression tests over the reproduce task's matrix plus unit tests of the flag and the lane.
- Out of scope: option A (truthful verdicts at local Phase 6), a public validation trigger, MelderOps
  revalidation (work package D, after the owner's wheel delivery).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: ({NOW}) the owner's pick in chat; ticket, board row and artifact rows created before the
  regression tests.

## Steps / Checklist
- [ ] Regression tests over the matrix (named and unnamed lesser, root, sibling lessers, unique and many providers,
      a root holding a spell at conjure, system caching on, the SpellSpace door; controls provider first and binds
      before conjure), run red.
- [ ] Patch docs and the mailbox NOTICE.
- [ ] Unit tests for the flag and the deferred lane, run red.
- [ ] Implement B (target-pass tail flags; the deferred lane runs the full pass without a Phase 5 root).
- [ ] Green: new tests, meld, spellbook, conduit and aether suites; the epic's probe.
- [ ] System docs, graph descriptors, release note, one notch, assets and LLM bundles last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The regression tests, source change B with unit tests, patch docs promoted into the system docs, release note,
  notch.

## Files / Paths Impacted
- src/melder/aether/spellbook/spellbook_creation_system.py, src/melder/aether/conduit/meld/meld.py,
  src/melder/__version__.py; tests (new component regressions, unit tests); system docs, graph descriptors,
  release note.

## Validation
- Not run.
- Recommended commands:
  - recorded in the MEASURE notes as they run

## Risks / Rollback Notes
- A dependency flagged and then given its own plan by another path pays one redundant pass on its first direct
  meld (correct, one compile). Rollback: revert the two edits; the flag and the lane are internal.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No src edit before the red regression tests, the patch docs and the NOTICE.
- [ ] No removal of the builder guard, no catch-and-retry.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/injected_provider_first_direct_meld_20260930/
  - artifacts/injected_provider_direct_meld_20260930/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the owner's turn-in of this ticket.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: {NOW}
  TYPE: DECISION
  CLAIM: Owner pick (chat): option B, regression tests first ("make a regression test then fix it", "or multiple
    tests"). Re-read on 0.2.8214 before the tests: the failure still reproduces (diagnostic fails; provider-first
    and binds-before-conjure pass). The meld doors enter the validation lane only while the Book flag is raised,
    then call the deferred lane when the spell's resolution_required is set; _execute_admitted re-enters the
    deferred lane while that flag is set; the deferred lane runs only phases 8-11, which skip a spell without a
    Phase 5 root blueprint; the full target pass has one runtime caller (the validation lane); the builder refuses
    a constructed spell whose codegen payload is None; local Phase 6 stamps every node of the pass's index valid.
  EVIDENCE:
  - {TASK_DONE_REPRO}:{request_start}-{request_end}
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs_0_2_8214/diagnostic_cacheoff.txt:1-1
  - src/melder/aether/conduit/meld/conduit_meld.py:558-562
  - src/melder/aether/conduit/meld/spellspace_meld.py:524-528
  - src/melder/aether/conduit/meld/meld.py:826-891
  - src/melder/aether/conduit/meld/meld.py:893-948
  - src/melder/aether/conduit/meld/meld.py:966-1019
  - src/melder/aether/conduit/meld/meld.py:1141-1202
  - src/melder/aether/spellbook/spellbook_creation_system.py:1654-1825
  - src/melder/aether/spellbook/spellbook_creation_system.py:2323-2355
  - src/melder/aether/spellbook/spellbook_creation_system.py:2740-2779
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:69-152
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:644-684
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py:220-267
  IMPACT: B needs two edits: flag the pass's plan-less owned dependencies at the target pass tail, and route a
    flagged spell without a Phase 5 root blueprint through the full target pass in the deferred lane.
  NEXT: Write the component regression tests over the matrix and run them red in the VM mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Opened {NOW} on the owner's pick (option B, regression tests first). Next: component regression tests over the
reproduce task's matrix, run red; then patch docs, NOTICE, unit tests, the fix, green, docs, notch 0.2.8215,
release note, rebuild.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
"""
if (CC / TASK).exists():
    raise SystemExit("task ticket already exists")
(CC / TASK).write_bytes(TICKET.encode("utf-8"))
print("wrote", TASK)

# Attention board: the injected row routes to the new task; the reproduce task becomes an anchor.
board = (CC / "attention_board.md").read_bytes().decode("utf-8")
old_row = next(line for line in board.split("\n") if line.startswith("| injected_dependency_direct_resolution |"))
new_row = (
    "| injected_dependency_direct_resolution | in_progress | implementation | claude | melder_0 | none | Write the "
    "component regression tests over the reproduce matrix and run them red, then patch docs, NOTICE and the fix. | A "
    "provider bound after conjure melds directly after injection and returns its scope's instance (option B); one "
    "notch. | Landed with tests red-to-green, docs, notch and rebuild; lane in review for the owner's turn-in. | "
    f"{TASK} | {NOW} | REQUIRED |"
)
board = swap(board, old_row, new_row, "attention_board.md")
old_detail = ("- injected_dependency_direct_resolution: SWITCH_TRIGGER is the task's DECISION_REQUEST (the owner picks a\n"
              "  repair); read-only in src/ until then. RESUME_HIERARCHY:\n"
              "  tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md ->\n"
              "  tickets/tasks/2026-09-30_reproduce_injected_provider_direct_meld_task.md.\n")
board = swap(board, old_detail,
             "- injected_dependency_direct_resolution: SWITCH_TRIGGER is landing option B (regression tests red then\n"
             "  green, docs, notch, rebuild) or a DECISION_REQUEST if the fix needs more than the two files.\n"
             "  RESUME_HIERARCHY: tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md ->\n"
             f"  {TASK}.\n", "attention_board.md")
anchor_row = (
    f"| injected_provider_reproduction | done | melder_0 | {TASK_DONE_REPRO} | Reproduced on bare Melder (no host, "
    "cache on or off, any scope or lifetime); cause: the consumer's target pass stamps the provider valid without its "
    f"plan; the owner picked option B. Next: {TASK}. | {NOW} |"
)
begin = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
board = swap(board, begin, begin + anchor_row + "\n", "attention_board.md")
region_start = board.index(begin) + len(begin)
region_end = board.index("<!-- END USER-DEFINED: closed_anchors -->")
rows = [line for line in board[region_start:region_end].split("\n") if line.startswith("|")]
rows.sort(key=lambda line: line.rstrip(" |").rsplit("| ", 1)[1], reverse=True)
board = board[:region_start] + "\n".join(rows[:12]) + "\n" + board[region_end:]
(CC / "attention_board.md").write_bytes(board.encode("utf-8"))
print("attention board synced")

# Artifact board: the probe row follows the new task; the lane's own folder gets a row.
artifacts = (CC / "artifact_board.md").read_bytes().decode("utf-8")
old_probe = next(line for line in artifacts.split("\n")
                 if line.startswith("| tickets/tasks/2026-09-30_reproduce_injected_provider_direct_meld_task.md |"))
new_probe = (f"| {TASK} | artifacts/injected_provider_direct_meld_20260930/ | probe_evidence | active | retain_as_reference | "
             "Bare-Melder probe and runs (0.2.8212 and runs_0_2_8214/); the acceptance probe for option B. | "
             f"{NOW} | REQUIRED |")
artifacts = swap(artifacts, old_probe, new_probe, "artifact_board.md")
lane_row = (f"| {TASK} | artifacts/injected_provider_first_direct_meld_20260930/ | implementation_evidence | active | "
            "retain_as_reference | Apply scripts, red/green and suite logs for option B. | "
            f"{NOW} | REQUIRED |\n")
begin_active = "<!-- BEGIN USER-DEFINED: active_artifacts -->\n"
artifacts = swap(artifacts, begin_active, begin_active + lane_row, "artifact_board.md")
(CC / "artifact_board.md").write_bytes(artifacts.encode("utf-8"))
print("artifact board synced", NOW)
