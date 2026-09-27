# Story: Rank source-backed improvements to compiler phases 1-11 and recommend the first tranche

## Metadata
- Completed: 2026-09-26T13:27:19Z
- Closure Basis: owner turn-in of fable_0's finished tickets; the recommended tranche T1 was chosen and shipped.
- Summary: cost_model.md and candidates.md (thirteen ranked candidates); the owner chose T1 = C-H + C-A, deferred
  C-B, and T1 shipped as the signature-determinism story (closed 2026-09-26T13:14:31Z).
- Story ID: STORY-2026-09-26-phase-pipeline-improvement-plan
- Epic: EPIC-2026-08-03-comptime-ir-phase-pipeline
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T07:42:51Z
- Updated: 2026-09-26T13:27:19Z

## User Narrative
As the Melder owner, I want a ranked, evidence-backed plan for improving the conjure pipeline's phases
(what to change, in which order, with what expected effect and how it is measured), so that I can
pick the first implementation tranche without re-reading the compiler.

## Value / MRP Alignment
The survey (STORY-2026-08-03-phase-pipeline-survey) established what phases 1-7 consume, produce,
hold and write. The owner's standing direction is that the pattern is not wrong but slow, and that
the structure should improve now while the Mojo migration stays a year out. This story turns the
survey's facts into improvement candidates that keep the core coherent (MRP): each candidate must
name its mechanism in source, its regime (cold conjure, warm conjure/restore, post-conjure bind,
meld-time local recompile), its expected effect, its scope and risk, its alignment with the
value-only IR direction, and the measurement that accepts or rejects it.

## Ticket Contract
- ENTRY_GATE: STORY-1 records exist under artifacts/ir_phase_survey_20260925/ (in review); the owner
  directed continued work on improving the phases (2026-09-26); the active board row routes here.
- EXECUTION_BOUNDARY: Read-only over `src/melder/aether/spellbook/spell_compiler/**`, the Spellbook
  conjure call sites that drive it, `utilities/synchronization/phase_scheduler.py`, and `tests/`.
  Writes limited to this story, its tasks, the epic's notes and story list, and
  `artifacts/ir_phase_improvement_20260926/`. No `src/`, `tests/` or patch-lane edits. Measurements
  are owner-run; this story specifies them and records the reported output.
- DEPENDENCIES: artifacts/ir_phase_survey_20260925/summary.md and the records it cites; the epic's
  Decision Log rulings (hot paths belong to another agent; module cost ignored; MLIR too far).
- EXIT_GATE: `cost_model.md` and `candidates.md` exist with evidence ranges; the epic carries one
  STRATEGY_DISCUSSION note with the ranking, the recommended first tranche and a single decision ask;
  owner selects a tranche or redirects.
- FAILURE_ESCALATION: BLOCKER if a candidate's mechanism cannot be established from source;
  CONFLICT when a candidate collides with another agent's active lane (override-execution epic,
  missing_dependency_sockets); RISK for any candidate that could reach the meld hot path.

## Requirements (Functional)
- A per-phase cost model from source: passes over the pool, allocations per spell, locks taken,
  registry writes, barriers and scheduler units per conjure, for phases 1-11 and the driver.
- Improvement candidates for phases 1-11 (structure and sequencing), each with mechanism, evidence,
  regime, expected effect, scope, risk, IR alignment and measurement.
- A ranking and a recommended first tranche, presented once as a strategy discussion.

## Requirements (Non-Functional)
- Unknown-first; no performance claim without a measurement or an explicit "unmeasured".
- No design ratification asked mid-story; decisions are packaged once at the end.
- Read the code whole where a candidate depends on it; grep locates only.

## Scope Boundaries
- In scope: phase modules 1-11, the drivers, the phase scheduler's cost surface, the cache-load
  seams already surveyed, phases 8-11 at structure and cost level.
- Out of scope: the meld hot path and scope-cycle door, Creations, ConduitWard, import/boot cost,
  any code change, any schema ratification (STORY-2 ir-schema-design).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directed "figure out how we can improve the phases ... keep working on it"
  (2026-09-26); opened by fable_0 with task 1 routed.
- from_state: in_progress
- to_state: review
- transition_reason: Both tasks in review; cost_model.md and candidates.md exist; the epic carries the single
  STRATEGY_DISCUSSION note with one decision ask (2026-09-26); owner decision pending.
- from_state: review
- to_state: done
- transition_reason: Owner decided T1 (C-H + C-A) earlier on 2026-09-26 and turned in the story with its two tasks
  (2026-09-26T13:27:19Z); records retained as reference.

## Dependencies / Related Work
- tickets/stories/2026-09-25_ir_phase_pipeline_survey_story.md (in review; source of facts)
- tickets/epics/2026-09-24_override_execution_performance_epic.md (updater_0, updater_1, melder_0
  lanes touching phases 8-11 and the emitters; this story is read-only alongside them)

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-09-26-model-phase-pipeline-costs - per-phase cost model from source plus the
  owner-run per-phase timing request tickets/tasks/completed/2026-09-26_model_phase_pipeline_costs_task.md (done 2026-09-26T13:27:19Z)
- [x] Task: TASK-2026-09-26-rank-phase-improvement-candidates - candidates, ranking, first-tranche
  recommendation tickets/tasks/completed/2026-09-26_rank_phase_improvement_candidates_task.md (done 2026-09-26T13:27:19Z)
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during discovery.

## Acceptance Criteria
- `artifacts/ir_phase_improvement_20260926/cost_model.md`: one row per phase and driver stage with
  evidence ranges; measured timings recorded when the owner supplies them, else "unmeasured".
- `artifacts/ir_phase_improvement_20260926/candidates.md`: every candidate carries the eight fields
  above; candidates that touch another lane are flagged.
- One STRATEGY_DISCUSSION note on the epic with the ranking and one decision ask.
- Owner selects a tranche or redirects.

## Validation / Test Plan
- Source reads are the evidence. Timings are owner-run: "Not run." until reported.

## UX / API / Data Notes
- None. Read-only.

## Risks / Mitigations
- Another lane is editing `spell_compiler/**` now (melder_0). Mitigation: cite ranges with dates;
  re-verify with `git diff -w` before relying on a range; flag collisions as CONFLICT.
- Ranking without measurement is opinion. Mitigation: the cost model separates counted facts
  (passes, allocations, locks) from expected effects, and the tranche recommendation names the
  measurement that would falsify it.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.
- [x] No candidate promoted on a name, a docstring or a grep hit.

## Open Questions
- Which regime the owner weights most (cold conjure on a fresh process, restore of a large world,
  post-conjure binds in dynamic mode); recorded as a ranking axis, decided with the tranche.

## Decision Log
- 2026-09-26: Opened on owner direction to keep working on improving the phases; STORY-1 stays in review.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/ir_phase_improvement_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Owner decision at story closure; the chosen tranche's patch docs draw from it.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: per-phase cost; improvement candidates; ranking; first tranche.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-26T07:42:51Z
  TYPE: PLAN
  CLAIM: Two tasks. Task 1 builds the per-phase cost model from source (survey records plus the phase
    scheduler, phases 8 and 11 at structure level, and the allocation/lock surface of the DAG and
    graph objects) and specifies one owner-run per-phase timing command. Task 2 writes the candidate
    list, ranks it, and produces the single strategy discussion on the epic.
  EVIDENCE:
  - artifacts/ir_phase_survey_20260925/summary.md:1-142
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md
  IMPACT: Converts the survey into the decision the owner asked for without further scope questions.
  NEXT: Task 1: read phase_scheduler.py (two chunks), compiler_phase_8.py, compiler_phase_11.py,
    dag_node.py; write cost_model.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T08:13:02Z
  TYPE: FACT
  CLAIM: Task 1 in review: cost_model.md (121 lines) carries a counted row per stage, the two owner-run
    MEASURE sources and the measurement command. Cross-task facts for task 2: cold conjure is dominated by
    the 8-11 rebuilds (~70% of phase time, June); warm conjure still runs 1-7 (~45% of the profiled
    conjure) plus a one-time strategy import; phase 8's per-root pool-sized signature cannot hit on the
    conjure path; the phase-3 DAG object has one production reader; phases 5 and 7 duplicate the CCM
    rebuild. Task 2 opened and routed.
  EVIDENCE:
  - artifacts/ir_phase_improvement_20260926/cost_model.md:1-121
  - tickets/tasks/2026-09-26_model_phase_pipeline_costs_task.md
  - tickets/tasks/2026-09-26_rank_phase_improvement_candidates_task.md
  IMPACT: The ranking has a per-regime cost basis; the story stays on one decision ask.
  NEXT: Task 2 R1: candidates.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T08:18:17Z
  TYPE: FACT
  CLAIM: Story in review: task 2 delivered candidates.md (thirteen candidates, per-regime ranking, T1
    recommendation) and the epic's strategy note. Exit gate met; the owner's tranche decision is the
    only pending action in this lane.
  EVIDENCE:
  - artifacts/ir_phase_improvement_20260926/candidates.md:1-286
  - tickets/tasks/2026-09-26_rank_phase_improvement_candidates_task.md
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md
  IMPACT: Closure sync follows the decision (both tasks and the story).
  NEXT: Owner decides T1 / T1' / T1'' or redirects.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
STATE 2026-09-26T07:42:51Z: opened; task 1 in progress. Resume from task 1's latest STATE line. The survey
records under artifacts/ir_phase_survey_20260925/ are the fact base; do not re-read surveyed source.
STATE 2026-09-26T08:13:02Z: task 1 in REVIEW (cost_model.md); task 2 in progress at R1. Resume from task 2's
latest STATE line.
STATE 2026-09-26T08:18:17Z: story in REVIEW; both tasks in review; waiting on the owner's tranche decision.
STATE 2026-09-26T13:27:19Z: DONE. Owner turned in the story; T1 chosen and shipped; records retained under
artifacts/ir_phase_improvement_20260926/ (retain_as_reference).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
