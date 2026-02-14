# Epic: Phase Testing (Component CProfile)

## Metadata
- Epic ID: EPIC-2026-02-14-phase-testing
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14
- Target Window: 2026-Q1
- Related Program/Initiative: Conjure Optimization Wave

## Problem / Opportunity
Current profiling around conjure phases is mixed with scheduler orchestration
(phase registration, queueing, worker lifecycle, UnitOfWork/Future barriers).
That makes it hard to isolate pure phase execution costs and optimize phase
logic directly.

## MRP Alignment (Most Reasonable Product)
We need a stable component-level profiling harness that measures phase logic in
isolation and remains reproducible under `cProfile` (single-threaded,
deterministic). This creates a reliable optimization foundation before deeper
runtime changes.

## Goals (Outcomes)
- Build a component test suite that profiles phase methods directly.
- Exclude `PhaseScheduler`, worker threads, and `UnitOfWork` from measured paths.
- Support boolean-gated phase chaining so we can profile grouped pipelines.
- Produce repeatable printed profile output suitable for task-level optimization.
- Cover grouped baselines for all conjure phase families (1-4, 5-7, 8-11).

## Non-Goals (Explicit Exclusions)
- Replacing production phase scheduling contracts.
- Changing runtime semantics during this planning pass.
- Integration benchmarking of full conjure flows in this epic setup step.

## Scope Boundaries
- In scope:
- Component test harness and profiling utilities for direct phase invocation.
- Grouped profiling tracks for phases 1-4 and phases 5-7.
- Grouped profiling track for phases 8-11.
- Target-local (single-spell) 5-7 profiling track.
- Out of scope:
- Multithreaded scheduler profiling.
- Phase 8-11 optimization execution (can be added after discovery).

## Success Metrics
- Epic has discovery-first stories/tasks for each phase-group profile track.
- Harness requirements are explicit: no scheduler, no workers, no UnitOfWork.
- Story outputs produce actionable optimization candidates with evidence.

## Requirements (Functional + Non-Functional)
- Component tests must run with `pytest` and support `cProfile`.
- Profiling path must be single-threaded.
- Harness must allow toggling grouped chains via explicit booleans.
- Printed output must include per-group timing/profile summaries.

## Constraints / Assumptions
- Constraints:
- Preserve current phase contracts and call ordering semantics per group.
- Keep changes scoped to component test harness/docs/tickets at first.
- Assumptions:
- Existing spell fixtures/deep-layer graphs remain available.

## Dependencies / External References
- `src/melder/spellbook/spell.py`
- `src/melder/spellbook/spellbook_creation_system.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `benchmarks/testing_other_di/test_melder_hotpath_profiles.py`
- `context_compass/WORKFLOW.md`

## Milestones (Track Progress)
- [ ] Milestone 1: Define and validate component profiling harness contract.
- [ ] Milestone 2: Capture baseline profile outputs for 1-4, 5-7, and 8-11 groups.
- [ ] Milestone 3: Convert baseline findings into ranked optimization tasks.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-14-phase-component-cprofile-harness - Build direct-call component cprofile harness with toggleable phase chains.
- [ ] Story: STORY-2026-02-14-phase-group-1-4-baseline - Baseline profile for structural phases 1-4 using direct phase calls.
- [ ] Story: STORY-2026-02-14-phase-group-5-7-conduit-baseline - Baseline profile for conduit-wide foundational phases 5-7.
- [ ] Story: STORY-2026-02-14-phase-group-5-7-local-baseline - Baseline profile for target-local foundational phases 5-7.
- [ ] Story: STORY-2026-02-14-phase-group-8-11-baseline - Baseline profile for conduit plan phases 8-11 using direct phase calls.
- [ ] Story: STORY-2026-02-14-phase-testing-optimization-backlog - Convert baseline findings into optimization leads/tasks.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-02-14-phase-component-cprofile-harness.
- [ ] Task: Complete story STORY-2026-02-14-phase-group-1-4-baseline.
- [ ] Task: Complete story STORY-2026-02-14-phase-group-5-7-conduit-baseline.
- [ ] Task: Complete story STORY-2026-02-14-phase-group-5-7-local-baseline.
- [ ] Task: Complete story STORY-2026-02-14-phase-group-8-11-baseline.
- [ ] Task: Complete story STORY-2026-02-14-phase-testing-optimization-backlog.

## Acceptance Criteria (Epic Done)
- Component harness exists and runs without `PhaseScheduler`/workers/UnitOfWork.
- Baseline profiles exist for grouped phase tracks (1-4, 5-7, 8-11) with reproducible output.
- Optimization backlog tasks are created from measured data.

## Risks / Mitigations
- Risk: component harness drifts from production execution semantics.
  Mitigation: keep group ordering and call boundaries explicitly mapped to
  existing phase facade methods.
- Risk: conflating conduit-wide and local 5-7 behavior.
  Mitigation: keep separate stories/tracks for conduit-wide vs target-local.

## Validation / Test Approach
- `pytest` component tests with `cProfile` instrumentation.
- Deterministic, single-threaded execution only.
- No benchmark timing claims without recorded output.

## Rollout / Adoption Plan
- Implement discovery story first (harness contract + path mapping).
- Capture baseline profiles per story group.
- Promote measured hotspots into optimization implementation tasks.

## Open Questions
- Should local target 8-11 baseline be tracked as a separate story after conduit-wide 8-11 discovery?
- What canonical fixture set should be used for default profile runs?

## Decision Log
- 2026-02-14: User requested a dedicated phase-testing epic using component
  cprofile paths with no scheduler/worker/unit-of-work runtime.
- 2026-02-14: Added an explicit conduit-wide 8-11 discovery baseline story so
  the phase-testing discovery plan covers all conjure phase groups.

## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Latest phase11 follow-up (`TASK-2026-02-14-optimize-phase11-variant-set-warm-reuse`) is implemented and rerun-validated with warm-path reduction (`group_8_11_total_ms` `3.167 -> 3.024`, `phase_execution_plan_ms` `1.383 -> 0.989`) and green targeted validation (`6 passed` + `1 passed` harness).
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_phase11_variant_set_warm_reuse_task.md:6-98, context_compass/artifacts/2026-02-14_phase11_variant_set_warm_reuse_targeted_unit_tests.txt:1-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_set_warm_reuse_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_set_warm_reuse_output.txt:23-25, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_rebuild_elision_output.txt:7-9
  IMPACT: Phase-testing optimization backlog checklist is complete and back in review mode pending user acceptance/closure routing.
  NEXT: Walk phase-testing outcomes with user and confirm move-to-completed direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Epic execution is reopened for one additional phase11 follow-up (`TASK-2026-02-14-optimize-phase11-variant-set-warm-reuse`) because current warm profile still shows measurable phase11 execution-plan overhead and unchanged-signature flow still derives sibling variants on each call.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_rebuild_elision_output.txt:17-25, src/melder/spellbook/spell_crafter/spell_crafter.py:4100-4188, src/melder/spellbook/spell_crafter/spell_crafter.py:4229-4300, context_compass/stories/2026-02-14_phase_testing_optimization_backlog_story.md:6-6, context_compass/tasks/2026-02-14_optimize_phase11_variant_set_warm_reuse_task.md:1-87
  IMPACT: Phase-testing lane remains in active optimization execution rather than closure routing.
  NEXT: Implement and validate the new phase11 follow-up task, then reassess closure readiness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Final phase11 follow-up (`TASK-2026-02-14-optimize-phase11-plan-rebuild-elision`) is now implemented and rerun-validated; backlog story checklist is complete and routed to `review`.
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_phase11_plan_rebuild_elision_task.md:6-147, context_compass/stories/2026-02-14_phase_testing_optimization_backlog_story.md:6-6, context_compass/stories/2026-02-14_phase_testing_optimization_backlog_story.md:52-52, context_compass/artifacts/2026-02-14_phase11_plan_rebuild_elision_targeted_unit_tests.txt:1-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_rebuild_elision_output.txt:7-7, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_rebuild_elision_output.txt:59-59
  IMPACT: Epic optimization scope is fully implemented for this wave and now awaits acceptance/closure routing.
  NEXT: Walk through epic/story outcomes with user and confirm move-to-completed direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Phase-testing backlog is reopened for one additional phase11 follow-up (`TASK-2026-02-14-optimize-phase11-plan-rebuild-elision`) because warm profile after plan-based compile still shows one full no-overrides plan build per spell.
  EVIDENCE: context_compass/stories/2026-02-14_phase_testing_optimization_backlog_story.md:6-6, context_compass/stories/2026-02-14_phase_testing_optimization_backlog_story.md:51-52, context_compass/stories/2026-02-14_phase_testing_optimization_backlog_story.md:74-81, context_compass/tasks/2026-02-14_optimize_phase11_plan_rebuild_elision_task.md:1-80, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_based_compile_output.txt:17-20
  IMPACT: Epic remains in active execution while this final follow-up is implemented and revalidated.
  NEXT: Execute the new phase11 plan-rebuild-elision task and rerun targeted unit + harness validations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Phase-baseline story state is stale: `phase-component-cprofile-harness`, `phase-group-1-4-baseline`, `phase-group-5-7-conduit-baseline`, `phase-group-5-7-local-baseline`, and `phase-group-8-11-baseline` remain `in_progress` with unchecked task rows even though their linked tasks are already `review` with executed checklists.
  EVIDENCE: context_compass/stories/2026-02-14_phase_component_cprofile_harness_story.md:6-6, context_compass/stories/2026-02-14_phase_component_cprofile_harness_story.md:44-45, context_compass/stories/2026-02-14_phase_group_1_4_baseline_story.md:6-6, context_compass/stories/2026-02-14_phase_group_1_4_baseline_story.md:42-42, context_compass/stories/2026-02-14_phase_group_5_7_conduit_baseline_story.md:6-6, context_compass/stories/2026-02-14_phase_group_5_7_conduit_baseline_story.md:43-43, context_compass/stories/2026-02-14_phase_group_5_7_local_baseline_story.md:6-6, context_compass/stories/2026-02-14_phase_group_5_7_local_baseline_story.md:43-43, context_compass/stories/2026-02-14_phase_group_8_11_baseline_story.md:6-6, context_compass/stories/2026-02-14_phase_group_8_11_baseline_story.md:44-44, context_compass/tasks/2026-02-14_discovery_phase_component_cprofile_harness_task.md:6-6, context_compass/tasks/2026-02-14_implement_phase_component_cprofile_harness_task.md:6-6, context_compass/tasks/2026-02-14_discovery_phase_group_1_4_baseline_task.md:6-6, context_compass/tasks/2026-02-14_discovery_phase_group_5_7_conduit_baseline_task.md:6-6, context_compass/tasks/2026-02-14_discovery_phase_group_5_7_local_baseline_task.md:6-6, context_compass/tasks/2026-02-14_discovery_phase_group_8_11_baseline_task.md:6-6
  IMPACT: Epic routing can mis-prioritize active implementation versus review-only closure work.
  NEXT: Align affected story statuses/checklists to `review` and preserve acceptance gates in closure sections.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Aligned the five phase-baseline stories to `review` and marked their linked checklist task rows complete so phase-testing routing reflects actual implementation state.
  EVIDENCE: context_compass/stories/2026-02-14_phase_component_cprofile_harness_story.md:6-6, context_compass/stories/2026-02-14_phase_component_cprofile_harness_story.md:44-45, context_compass/stories/2026-02-14_phase_group_1_4_baseline_story.md:6-6, context_compass/stories/2026-02-14_phase_group_1_4_baseline_story.md:42-42, context_compass/stories/2026-02-14_phase_group_5_7_conduit_baseline_story.md:6-6, context_compass/stories/2026-02-14_phase_group_5_7_conduit_baseline_story.md:43-43, context_compass/stories/2026-02-14_phase_group_5_7_local_baseline_story.md:6-6, context_compass/stories/2026-02-14_phase_group_5_7_local_baseline_story.md:43-43, context_compass/stories/2026-02-14_phase_group_8_11_baseline_story.md:6-6, context_compass/stories/2026-02-14_phase_group_8_11_baseline_story.md:44-44
  IMPACT: Phase-testing lane is now consistently in review/closure mode across backlog + baseline stories.
  NEXT: Walk through acceptance for phase-testing story set and move approved tickets to completed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: The final active phase11 follow-up (`TASK-2026-02-14-optimize-phase11-plan-based-no-overrides-compile`) is now implemented and rerun-validated: targeted spell-crafter slice passes (`10 passed`) and harness rerun passes (`1 passed`) with refreshed warm profile output.
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_phase11_plan_based_no_overrides_compile_task.md:45-54, context_compass/artifacts/2026-02-14_phase11_plan_based_compile_targeted_unit_tests.txt:1-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_based_compile_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_based_compile_output.txt:59-59
  IMPACT: Phase-testing optimization implementation scope is now fully delivered and waiting on acceptance/closure routing.
  NEXT: Walk epic/story outcomes with user and request closure direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Lazy phase8-11 capture follow-up is accepted and moved to completed after fresh rerun validation.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_optimize_phase11_lazy_phase8_11_capture_task_completed.md:1-83, context_compass/artifacts/2026-02-14_phase11_lazy_capture_targeted_unit_tests.txt:12-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_lazy_capture_output.txt:7-9
  IMPACT: Phase-testing follow-up lane is fully complete; next action is closure routing for backlog story/epic.
  NEXT: Confirm story/epic closeout direction and move accepted tickets to completed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Lazy phase8-11 capture follow-up is implemented and validated with strong warm gains: `group_8_11_total_ms` improved `8.124 -> 4.041`, `phase_execution_plan_ms` improved `6.289 -> 2.166`, warm calls dropped `96062 -> 56255`, and eager `_capture_phase8_11_codegen_ir*` calls no longer dominate warm top-30 profile.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_optimize_phase11_lazy_phase8_11_capture_task_completed.md:1-83, src/melder/spellbook/spell_crafter/spell_crafter.py:3759-3768, src/melder/spellbook/spell_crafter/spell_crafter.py:1968-2035, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_reuse_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_reuse_output.txt:17-21, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_lazy_capture_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_lazy_capture_output.txt:17-23, context_compass/artifacts/2026-02-14_phase11_lazy_capture_targeted_unit_tests.txt:1-1, context_compass/artifacts/2026-02-14_phase11_lazy_capture_targeted_unit_tests.txt:12-12
  IMPACT: Phase-testing follow-up lane delivered another measurable warm reduction and is ready for acceptance/closure routing.
  NEXT: Walk through backlog outcomes with user and confirm close/move direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Phase-testing backlog is re-opened for one additional follow-up after variant reuse because warm profile still shows eager phase8-11 capture overhead as the top phase11 slice.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_reuse_output.txt:17-21, src/melder/spellbook/spell_crafter/spell_crafter.py:3759-3768, context_compass/tasks/completed/2026-02-14_optimize_phase11_lazy_phase8_11_capture_task_completed.md:1-39
  IMPACT: Epic remains in active execution while the lazy-capture follow-up is implemented and remeasured.
  NEXT: Execute `TASK-2026-02-14-optimize-phase11-lazy-phase8-11-capture`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: User accepted the phase11 variant-reuse follow-up outcomes and the task was moved to completed.
  EVIDENCE: user instruction in session (2026-02-14): "yeah looks good keep moving", context_compass/tasks/completed/2026-02-14_optimize_phase11_execution_plan_variant_reuse_task_completed.md:1-10, context_compass/tasks/completed/2026-02-14_optimize_phase11_execution_plan_variant_reuse_task_completed.md:61-70
  IMPACT: Phase-testing backlog follow-up implementation lane is complete and can move toward closure routing.
  NEXT: Keep epic active for now while continuing other active optimization stories and closure sequencing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Phase11 variant-reuse follow-up is implemented and validated; warm 8-11 totals improved (`group_8_11_total_ms` `9.085 -> 8.124`, `phase_execution_plan_ms` `7.3 -> 6.289`), warm cProfile calls dropped (`108778 -> 96062`), and warm phase11 plan rebuild calls dropped (`51 -> 17`) for `_build_execution_plan_variant` and `ExecutionPlanBuilder.build`.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:3726-3754, src/melder/spellbook/spell_crafter/spell_crafter.py:3808-3867, tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:5578-5719, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:21-22, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_reuse_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_reuse_output.txt:26-27, context_compass/artifacts/2026-02-14_phase11_variant_reuse_targeted_unit_tests.txt:1-1, context_compass/artifacts/2026-02-14_phase11_variant_reuse_targeted_unit_tests.txt:12-12
  IMPACT: The reopened phase-testing follow-up now has measured improvement and can move to acceptance/closure routing.
  NEXT: Review backlog outcomes with user and confirm close/move direction for phase-testing story/task set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Phase-testing backlog execution is re-opened for one additional ranked follow-up task targeting phase11 variant rebuild churn (`TASK-2026-02-14-optimize-phase11-execution-plan-variant-reuse`).
  EVIDENCE: context_compass/stories/2026-02-14_phase_testing_optimization_backlog_story.md:44-49, context_compass/stories/2026-02-14_phase_testing_optimization_backlog_story.md:71-78, context_compass/tasks/completed/2026-02-14_optimize_phase11_execution_plan_variant_reuse_task_completed.md:1-37, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:21-23
  IMPACT: Epic remains in active execution mode until the new follow-up task is implemented and remeasured.
  NEXT: Execute the new phase11 variant-reuse task and re-evaluate closure routing with fresh warm profile evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-2 row-builder task received a follow-up memoization pass and remains in review with measurable warm-path gains: `group_8_11_total_ms` improved `9.804 -> 9.085`, `phase_patch_maps_ms` improved `1.288 -> 0.573`, function calls dropped `120524 -> 108778`, and patch-map helper cumulative time dropped (`build_override_patch_map` `0.006 -> 0.004`, `_get_path_spec_key` `0.005 -> 0.002`).
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_phase8_10_plan_row_builders_task.md:65-72, src/melder/spellbook/spell_crafter/dag/dag_index.py:182-191, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run8.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run8.txt:25-27, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:32-34
  IMPACT: Phase-testing execution lane now has improved rank-2 hotspot metrics and is ready for acceptance/closure routing.
  NEXT: Review rank1/rank2/rank3 outcomes with user and confirm closure direction for the backlog story tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-3 phase5 task is revalidated with clean reruns; focused phase5 suites passed and warm conduit 5-7 metrics remain below the pre-rank3 anchor with expected run-to-run noise.
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_phase5_root_blueprints_hotpath_task.md:59-99, context_compass/artifacts/2026-02-14_phase5_opt_builder_unit_tests_rerun_clean.txt:12-12, context_compass/artifacts/2026-02-14_phase5_opt_spell_crafter_unit_tests_rerun_clean.txt:12-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output.txt:4-4, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:4-4, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output.txt:4-4, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run2.txt:4-4
  IMPACT: Ranked optimization backlog execution is complete; epic now needs acceptance/closure decisions and any next-wave follow-up scoping.
  NEXT: Review rank1/rank2/rank3 outcomes with user and confirm closure direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-2 optimization task is implemented and validated; harness reruns report mixed warm totals (`27.932ms` and `25.438ms`) against rank1 anchor (`27.829ms`) with warm cProfile sample reduced from `0.083s` to `0.081s`/`0.080s`.
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_phase8_10_plan_row_builders_task.md:98-105, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_opt_output.txt:12-15, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run2.txt:7-9
  IMPACT: Epic execution progressed through rank-2 with no regressions, but warm-total impact is noisy and needs keep-vs-iterate direction.
  NEXT: Confirm rank-2 acceptance direction, then execute rank-3 task (`TASK-2026-02-14-optimize-phase5-root-blueprints-hotpath`).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-1 optimization execution is validated with measured warm 8-11 improvement (`34.993ms` -> `27.829ms`) and reduced warm cProfile sample (`0.091s` -> `0.083s`).
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:11-15, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_opt_output.txt:12-15, context_compass/tasks/2026-02-14_optimize_phase11_codegen_ir_capture_task.md:57-89
  IMPACT: Epic has moved from planning/ranking into verified optimization execution outcomes.
  NEXT: Execute rank-2 task (`TASK-2026-02-14-optimize-phase8-10-plan-row-builders`).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Phase-testing backlog ranking is complete and produced three scoped optimization tasks (phase11 IR capture, phase8-10 row builders, phase5 root-blueprints).
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_phase_testing_optimization_backlog_task.md:47-82, context_compass/tasks/2026-02-14_optimize_phase11_codegen_ir_capture_task.md:1-12, context_compass/tasks/2026-02-14_optimize_phase8_10_plan_row_builders_task.md:1-12, context_compass/tasks/2026-02-14_optimize_phase5_root_blueprints_hotpath_task.md:1-12
  IMPACT: Epic has moved from discovery-only to execution-ready optimization scope.
  NEXT: Confirm task execution order and start rank-1 optimization task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Component harness run now provides measured outputs across all planned phase groups plus a warm 8-11 cProfile sample.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:5-14, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:51-52
  IMPACT: Epic can progress from discovery contracts to evidence-backed optimization backlog ranking.
  NEXT: Execute backlog ranking and generate scoped optimization tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Optimization-backlog discovery is blocked on missing measured outputs from baseline phase tasks; readiness gate and ranking schema are documented.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_phase_testing_optimization_backlog_task.md:6, context_compass/tasks/2026-02-14_discovery_phase_testing_optimization_backlog_task.md:28
  IMPACT: Epic now waits on measurement implementation/runs to transition from discovery contracts to ranked optimization task generation.
  NEXT: Implement harness/profile runs and attach measured outputs in baseline tasks to unblock backlog ranking.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: 8-11 baseline discovery is complete and in review with explicit sequence, variant, and output contracts.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_phase_group_8_11_baseline_task.md:1, context_compass/stories/2026-02-14_phase_group_8_11_baseline_story.md:1
  IMPACT: All planned baseline discovery tracks are now documented and review-ready under this epic.
  NEXT: Execute `TASK-2026-02-14-discovery-phase-testing-optimization-backlog` to convert baseline contracts/results into ranked follow-up tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Local 5-7 baseline discovery is complete and in review with explicit target policy and scoped-work output contract.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_phase_group_5_7_local_baseline_task.md:1, context_compass/stories/2026-02-14_phase_group_5_7_local_baseline_story.md:1
  IMPACT: Discovery progression can move to 8-11 baseline while preserving separate conduit-vs-local 5-7 artifacts.
  NEXT: Execute `TASK-2026-02-14-discovery-phase-group-8-11-baseline`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conduit-wide 5-7 baseline discovery is complete and in review with lead-spell frame-scoped execution contract and ranking output schema.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_phase_group_5_7_conduit_baseline_task.md:1, context_compass/stories/2026-02-14_phase_group_5_7_conduit_baseline_story.md:1
  IMPACT: Discovery sequence can proceed to local 5-7 while preserving closeout-ready evidence for conduit 5-7.
  NEXT: Execute `TASK-2026-02-14-discovery-phase-group-5-7-local-baseline`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: 1-4 baseline discovery is complete and in review, with explicit full-spellbook default scope plus warm/cold variant contract.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_phase_group_1_4_baseline_task.md:1, context_compass/stories/2026-02-14_phase_group_1_4_baseline_story.md:1
  IMPACT: Phase-testing discovery flow can continue to conduit 5-7 baseline while awaiting acceptance for 1-4 discovery closeout.
  NEXT: Execute `TASK-2026-02-14-discovery-phase-group-5-7-conduit-baseline`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Harness discovery output is complete and under review, with explicit direct-call group contracts (`1-4`, `5-7 conduit`, `5-7 local`, `8-11 conduit`) and standardized profiling output schema.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_phase_component_cprofile_harness_task.md:34, context_compass/stories/2026-02-14_phase_component_cprofile_harness_story.md:1
  IMPACT: Epic phase-discovery flow is now unblocked for ordered baseline tasks once harness discovery is accepted.
  NEXT: Confirm acceptance for harness discovery task, then run discovery for phase group 1-4.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: There are two 5-7 families today: conduit-wide foundational phases and target-local foundational phases.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1063, src/melder/spellbook/spellbook_creation_system.py:1206
  IMPACT: The new component suite should baseline both families separately.
  NEXT: Execute discovery stories for harness and both 5-7 profile tracks.

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Target-local 5-7 phases are single-unit registrations in current scheduler wiring.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1165, src/melder/spellbook/spellbook_creation_system.py:1192
  IMPACT: Confirms a direct-call local 5-7 component profile track is meaningful and bounded.
  NEXT: Capture equivalent direct-call path in component harness design.

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conduit plan phases are an explicit grouped chain (occurrence, injection, patch maps, execution plan) in creation-system orchestration.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1111, src/melder/spellbook/spellbook_creation_system.py:1121, src/melder/spellbook/spell.py:1067, src/melder/spellbook/spell.py:1140
  IMPACT: A dedicated 8-11 baseline story is required for all-phase coverage.
  NEXT: Execute 8-11 discovery task after harness and 1-4/5-7 discovery setup is locked.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic created for component-level phase profiling with explicit isolation from
scheduler and worker orchestration overhead. Planned flow is discovery-first
across harness design, 1-4 baseline, conduit-wide 5-7 baseline, target-local
5-7 baseline, conduit-wide 8-11 baseline, then optimization backlog generation.
Execution delivered rank1/rank2/rank3 optimization tasks plus four phase11
follow-ups (variant reuse, lazy capture, plan-based no-overrides compile, and
plan-rebuild elision). The latest follow-up (`TASK-2026-02-14-optimize-phase11-variant-set-warm-reuse`)
is now also implemented and rerun-validated with warm-path improvement.
Next step is user acceptance and closure routing for the backlog story/epic.
