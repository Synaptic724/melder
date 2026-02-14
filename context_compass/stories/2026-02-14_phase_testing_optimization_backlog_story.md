# Story: Phase Testing Optimization Backlog

## Metadata
- Story ID: STORY-2026-02-14-phase-testing-optimization-backlog
- Epic: EPIC-2026-02-14-phase-testing
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## User Narrative
As a Melder maintainer, I want measured phase profile findings converted into
ranked optimization tasks, so that conjure optimization work stays evidence-first.

## Value / MRP Alignment
Converts profiling data into actionable engineering scope with clear
prioritization and reduced speculative work.

## Requirements (Functional)
- Gather baseline profile findings from phase-testing stories.
- Produce ranked optimization candidates with evidence anchors.
- Create scoped follow-up tasks for approved optimization leads.

## Requirements (Non-Functional)
- Unknowns gate remains enforced for all claims.
- No optimization implementation in this backlog-forming story.

## Scope Boundaries
- In scope:
- Synthesis and task creation from measured phase profile data.
- Out of scope:
- Code changes to optimize phase logic.

## Dependencies / Related Work
- `STORY-2026-02-14-phase-component-cprofile-harness`
- `STORY-2026-02-14-phase-group-1-4-baseline`
- `STORY-2026-02-14-phase-group-5-7-conduit-baseline`
- `STORY-2026-02-14-phase-group-5-7-local-baseline`
- `STORY-2026-02-14-phase-group-8-11-baseline`
- `EPIC-2026-02-14-phase-testing`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-14-discovery-phase-testing-optimization-backlog - Build ranked optimization backlog from measured phase profile outputs.
- [ ] Task: TASK-2026-02-14-execute-phase-group-baseline-measurements - Run baseline harness measurements and record outputs for ranking readiness.
- [ ] Task: TASK-2026-02-14-optimize-phase11-codegen-ir-capture - Optimize top warm 8-11 codegen IR hotspot.
- [ ] Task: TASK-2026-02-14-optimize-phase8-10-plan-row-builders - Optimize warm plan row-builder/path-materialization hotspot.
- [ ] Task: TASK-2026-02-14-optimize-phase5-root-blueprints-hotpath - Optimize foundational conduit-wide phase5 hotspot.

## Acceptance Criteria
- Ranked optimization backlog exists with evidence for each candidate.
- Follow-up implementation tasks are scoped and linked.

## Validation / Test Plan
- Validate by traceability from measured profile output to each backlog item.

## UX / API / Data Notes
- Ticketing/planning artifact only.

## Risks / Mitigations
- Risk: optimization candidates drift from measured evidence.
  Mitigation: require profile-output references in each candidate/task.

## Open Questions
- Which acceptance thresholds should gate optimization-task approval?

## Decision Log
- 2026-02-14: Story created from EPIC-2026-02-14-phase-testing.

## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-1 implementation produced measured warm-path improvement (`group_8_11_warm` `34.993ms` -> `27.829ms`) and lower warm cProfile sample time (`0.091s` -> `0.083s`).
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:11-15, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_opt_output.txt:12-15, context_compass/tasks/2026-02-14_optimize_phase11_codegen_ir_capture_task.md:57-89
  IMPACT: Backlog execution has confirmed measurable ROI on the top-ranked candidate.
  NEXT: Continue with rank-2 and rank-3 tasks in order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Measured backlog ranking produced three scoped optimization tasks prioritized by warm 8-11 and conduit 5-7 hotspot signals.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_phase_testing_optimization_backlog_task.md:47-82, context_compass/tasks/2026-02-14_optimize_phase11_codegen_ir_capture_task.md:1-12, context_compass/tasks/2026-02-14_optimize_phase8_10_plan_row_builders_task.md:1-12, context_compass/tasks/2026-02-14_optimize_phase5_root_blueprints_hotpath_task.md:1-12
  IMPACT: Story now has concrete follow-up implementation scope instead of a generic backlog placeholder.
  NEXT: Confirm ranking order with user and begin execution at rank 1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Measurement blocker is cleared; baseline outputs for all required phase tracks are now captured in a durable artifact.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:5-11, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:51-52
  IMPACT: Story can proceed from blocked discovery to ranking/taskization work.
  NEXT: Rank measured hotspots and open scoped optimization tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Optimization-backlog discovery is currently blocked because upstream phase-testing tickets have discovery contracts but no measured profile outputs yet.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_phase_testing_optimization_backlog_task.md:6, context_compass/tasks/2026-02-14_discovery_phase_testing_optimization_backlog_task.md:60
  IMPACT: Story cannot produce final ranked optimization tasks until measurement data is attached.
  NEXT: Unblock after measured outputs are recorded in the phase baseline tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Backlog ranking will be based on measured component profile output, not intuition.
  EVIDENCE: context_compass/epics/2026-02-14_phase_testing_epic.md:12
  IMPACT: Keeps optimization follow-ups tied to evidence and avoids speculative churn.
  NEXT: Execute discovery after baseline stories complete.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story is now in execution-ready backlog state: ranking is complete and three
follow-up optimization tasks are created. Next step is user-confirmed execution
order and implementation starting with rank 1.
