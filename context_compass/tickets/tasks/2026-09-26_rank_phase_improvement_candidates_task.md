# Task: Rank source-backed improvement candidates for phases 1-11 and recommend the first tranche

## Metadata
- Task ID: TASK-2026-09-26-rank-phase-improvement-candidates
- Story: STORY-2026-09-26-phase-pipeline-improvement-plan
- Status: review
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T08:12:47Z
- Updated: 2026-09-26T08:18:17Z

## Objective
Produce `candidates.md`: every improvement candidate for the conjure pipeline's phases 1-11 (structure and
sequencing) with mechanism, evidence, regime, expected effect, scope, risk, IR alignment and the measurement
that accepts or rejects it; rank them per regime; then post ONE STRATEGY_DISCUSSION note on the epic with the
ranking, the recommended first tranche and a single decision ask.

## Ticket Contract
- ENTRY_GATE: Task 1 in review (cost_model.md complete); the active board row routes here.
- EXECUTION_BOUNDARY: Read-only over `spell_compiler/**`, the conjure call sites, the scheduler and `tests/`;
  new reads only where a candidate's mechanism is not yet established (each recorded before use). Writes
  limited to this ticket, the story, the epic's Notes, and `artifacts/ir_phase_improvement_20260926/`.
- DEPENDENCIES: artifacts/ir_phase_improvement_20260926/cost_model.md; artifacts/ir_phase_survey_20260925/
  (summary.md first); the epic's Decision Log rulings (hot paths belong to another agent; module cost
  ignored; MLIR too far; no design ratification asked mid-story).
- EXIT_GATE: `candidates.md` exists with the eight fields per candidate and lane collisions flagged; the epic
  carries one STRATEGY_DISCUSSION note (objective, constraints, known facts, unknowns, options, tradeoffs,
  recommendation, decision ask); status review.
- FAILURE_ESCALATION: BLOCKER if a candidate's mechanism cannot be established from source; CONFLICT when a
  candidate collides with another agent's active lane (override-execution epic; missing_dependency_sockets);
  RISK for any candidate that could reach the meld hot path.

## Scope Boundaries
- In scope: candidates over the driver, the scheduler's use, phases 1-11, the cache seam and the
  invalidation surface; ranking axes = regime (cold conjure, warm conjure, post-conjure bind and local
  recompile, restore) x expected effect x scope/risk x IR alignment.
- Out of scope: any code change; the meld hot path; import/boot cost; schema ratification (STORY-2).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Task 1 reached review at 2026-09-26T08:12:10Z; the owner's standing direction
  ("figure out how we can improve the phases ... keep working on it") continues the lane.
- from_state: in_progress
- to_state: review
- transition_reason: candidates.md complete and the epic carries one STRATEGY_DISCUSSION note with a single
  decision ask (2026-09-26); exit gate met; awaiting the owner's tranche decision.

## Steps / Checklist
- [x] R1: write `candidates.md` from cost_model.md and the survey records (one section per candidate,
      eight fields each; collisions with updater_0/updater_1/melder_0 lanes flagged); new reads only for
      a mechanism not yet on record, noted before use.
- [x] R2: rank per regime; pick the recommended first tranche (small, measurable, inside the epic's
      boundary, no hot-path reach); name the falsifying measurement.
- [x] R3: one STRATEGY_DISCUSSION note on the epic (eight-part structure) with a single decision ask;
      story note; boards; task -> review.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- artifacts/ir_phase_improvement_20260926/candidates.md
- One STRATEGY_DISCUSSION note on tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md

## Files / Paths Impacted
- None under `src/`, `tests/` or `benchmarks/`. This ticket, the story, the epic's Notes, and the artifact
  directory only.

## Validation
- Not run.
- Recommended commands:
  - none for this read-only task; each candidate names its own owner-run measurement.

## Risks / Rollback Notes
- Ranking without measurement is opinion: counted facts and measured rows are kept separate in every
  candidate, and the tranche recommendation names the measurement that would falsify it.
- Another lane edits `spell_compiler/**` now (melder_0); ranges are dated and re-verified before reuse.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No candidate promoted on a name, a docstring or a grep hit; no mid-stream design questions.

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
  - artifacts/ir_phase_improvement_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Story closure; the chosen tranche's patch docs draw from it.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: improvement candidates; ranking per regime; first tranche; decision ask.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T08:12:47Z
  TYPE: PLAN
  CLAIM: Candidates are drawn from cost_model.md section 6 and the survey's D1-D6; each is written with
    the eight fields before ranking. Ranking axes: regime, expected effect (measured or counted), scope
    and risk, IR/Mojo alignment. The first tranche must be small, measurable with the existing harnesses,
    inside the epic's boundary and free of hot-path reach. Presentation happens once, on the epic.
  EVIDENCE:
  - artifacts/ir_phase_improvement_20260926/cost_model.md:1-121
  - artifacts/ir_phase_survey_20260925/summary.md:1-142
  IMPACT: Keeps the story's promise of one decision ask with no mid-stream design questions.
  NEXT: R1: write candidates.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T08:17:33Z
  TYPE: FACT
  CLAIM: R1 and R2 done: candidates.md (286 lines) holds thirteen candidates C-A..C-M with the eight
    fields and a collision flag each, a per-regime ranking table, the recommended first tranche and the
    parked list. Two invariants bound the ranking: a Spellbook conjures once, so "warm conjure" is a new
    book in a new process and no memo below the creation cache can hit (C-D dropped for that reason);
    hot paths are out of scope. Ranking: cold conjure C-A (dead pool-sized signature in phase 8), C-J
    (LPT chunking at workers>1), C-C (phase-3 DAG to rows); warm conjure C-G (snapshot) then C-C, C-B,
    C-E; local recompile C-B, C-K, C-C; correctness C-H. Recommended T1 = C-H + C-A + C-B (small,
    measurable with the breakdown harness, inside the boundary, no hot-path reach, and the
    prerequisites of C-G). Lane collisions: phase 8 (updater_1, melder_0), shared_compiler_executions.py
    and possibly spellbook_creation_system.py (melder_0), caching_system.py generation (C-G, C-H).
  EVIDENCE:
  - artifacts/ir_phase_improvement_20260926/candidates.md:1-286
  - artifacts/ir_phase_improvement_20260926/cost_model.md:1-121
  - artifacts/ir_phase_survey_20260925/summary.md:1-142
  IMPACT: The owner can pick a tranche from one file; every effect claim is labelled measured, counted or
    hypothesis, and each candidate names the measurement that would falsify it.
  NEXT: R3: one STRATEGY_DISCUSSION note on the epic with the single decision ask; story note; boards;
    task -> review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T08:18:17Z
  TYPE: FACT
  CLAIM: R3 done: the epic carries the STRATEGY_DISCUSSION note (objective, constraints, known facts,
    unknowns, three options T1/T1'/T1'', tradeoffs, recommendation T1 = C-H + C-A + C-B, one decision ask).
    Task 2 exit gate met; story exit gate met pending the owner's decision.
  EVIDENCE:
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md
  - artifacts/ir_phase_improvement_20260926/candidates.md:230-286
  IMPACT: The lane now waits on one owner decision; no further reading is planned here.
  NEXT: Owner picks T1, T1', T1'' or redirects.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-09-26T08:12:47Z: opened; task 1 in review. Resume at R1 (candidates.md). Fact base: cost_model.md and the
survey records; do not re-read surveyed source.
STATE 2026-09-26T08:17:33Z: R1-R2 done (candidates.md). Resume at R3: epic STRATEGY_DISCUSSION note, story note, boards,
task -> review.
STATE 2026-09-26T08:18:17Z: task 2 in REVIEW; the story waits on the owner's tranche decision (epic strategy note).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
