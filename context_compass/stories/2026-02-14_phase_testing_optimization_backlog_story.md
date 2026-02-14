# Story: Phase Testing Optimization Backlog

## Metadata
- Story ID: STORY-2026-02-14-phase-testing-optimization-backlog
- Epic: EPIC-2026-02-14-phase-testing
- Status: review
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
- [x] Task: TASK-2026-02-14-discovery-phase-testing-optimization-backlog - Build ranked optimization backlog from measured phase profile outputs.
- [x] Task: TASK-2026-02-14-execute-phase-group-baseline-measurements - Run baseline harness measurements and record outputs for ranking readiness.
- [x] Task: TASK-2026-02-14-optimize-phase11-codegen-ir-capture - Optimize top warm 8-11 codegen IR hotspot.
- [x] Task: TASK-2026-02-14-optimize-phase8-10-plan-row-builders - Optimize warm plan row-builder/path-materialization hotspot.
- [x] Task: TASK-2026-02-14-optimize-phase5-root-blueprints-hotpath - Optimize foundational conduit-wide phase5 hotspot.
- [x] Task: TASK-2026-02-14-optimize-phase11-execution-plan-variant-reuse - Reuse phase11 plan structure across override variants to cut repeated builder work.

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
  CLAIM: The re-opened phase11 variant-reuse follow-up is now implemented and validated; warm 8-11 totals improved (`group_8_11_total_ms` `9.085 -> 8.124`, `phase_execution_plan_ms` `7.3 -> 6.289`), warm cProfile calls dropped (`108778 -> 96062`), and phase11 plan rebuild calls dropped (`51 -> 17`) per warm sample.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:3726-3754, src/melder/spellbook/spell_crafter/spell_crafter.py:3808-3867, tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:5578-5719, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:21-22, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_reuse_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_reuse_output.txt:26-27, context_compass/artifacts/2026-02-14_phase11_variant_reuse_targeted_unit_tests.txt:1-1, context_compass/artifacts/2026-02-14_phase11_variant_reuse_targeted_unit_tests.txt:12-12
  IMPACT: All ranked backlog tasks plus the follow-up slice are now implemented with fresh validation evidence.
  NEXT: Walk through backlog outcomes with user and confirm closure/move direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Re-opened the story for a ranked follow-up because the latest warm 8-11 profile still shows repeated phase11 variant plan rebuilding (`_build_execution_plan_variant` + `ExecutionPlanBuilder.build`) as a top cumulative hotspot (`51` calls per warm sample).
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:17-23, src/melder/spellbook/spell_crafter/spell_crafter.py:3726-3743
  IMPACT: Rank-1/2/3 wins are preserved, but one additional low-risk optimization slice remains for phase11 variant construction overhead.
  NEXT: Execute `TASK-2026-02-14-optimize-phase11-execution-plan-variant-reuse` with behavior-parity tests and harness rerun.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-2 row-builder follow-up pass is now in review with measurable warm-path gains after `PathRegistry.format_path` memoization: `group_8_11_total_ms` improved `9.804 -> 9.085`, `phase_patch_maps_ms` improved `1.288 -> 0.573`, function calls dropped `120524 -> 108778`, and patch-map helper cumulative time dropped (`build_override_patch_map` `0.006 -> 0.004`, `_get_path_spec_key` `0.005 -> 0.002`).
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_phase8_10_plan_row_builders_task.md:65-72, src/melder/spellbook/spell_crafter/dag/dag_index.py:182-191, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run8.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run8.txt:25-27, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:32-34
  IMPACT: Rank-2 now has a clear warm improvement signal and remains closure-ready pending user acceptance direction.
  NEXT: Walk rank1/rank2/rank3 outcomes with user and confirm closure/move direction for in-review tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-3 phase5 revalidation is complete with clean reruns; focused unit tests passed and warm conduit 5-7 timings remain below the pre-rank3 anchor with expected run-to-run noise.
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_phase5_root_blueprints_hotpath_task.md:59-99, context_compass/artifacts/2026-02-14_phase5_opt_builder_unit_tests_rerun_clean.txt:12-12, context_compass/artifacts/2026-02-14_phase5_opt_spell_crafter_unit_tests_rerun_clean.txt:12-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output.txt:4-4, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:4-4, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output.txt:4-4, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run2.txt:4-4
  IMPACT: All ranked backlog optimization tasks are now implemented and in review.
  NEXT: Walk through rank1/rank2/rank3 outcomes with user and confirm closure direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-2 implementation is complete and validated; two harness reruns show mixed warm totals (`27.932ms`, `25.438ms`) against the rank1 anchor (`27.829ms`) while warm cProfile sample improved to `0.081s`/`0.080s` from `0.083s`.
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_phase8_10_plan_row_builders_task.md:98-105, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_opt_output.txt:12-15, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run2.txt:7-9
  IMPACT: Rank-2 slice is safe and in review, but warm-total gain is noisy at this sample size.
  NEXT: Get user direction to keep-or-iterate rank-2, then execute rank-3 task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

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
Story optimization execution delivered validated rank1/rank2/rank3 outcomes,
then re-opened for one additional ranked follow-up focused on phase11 variant
rebuild churn observed in the latest warm sample (`_build_execution_plan_variant`
and `ExecutionPlanBuilder.build` at 51 calls each). The follow-up is now
implemented and validated with reduced warm totals/calls and reduced phase11
builder call frequency. Next step is user acceptance and move-to-completed
routing.
