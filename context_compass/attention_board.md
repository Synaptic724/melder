# Attention Board

Purpose
- Active-work routing board.
- Attention-only summary for fast re-entry.
- Canonical detail lives in linked tickets.

Attention details rule
- Capture evidence pointers while reading (do not wait for end-of-pass summaries).
- Keep entries short using: `TYPE`, `CLAIM`, `EVIDENCE`, `REREAD`, `NEXT`.
- Use evidence ranges in `EVIDENCE` (`path:start_line-end_line`); for single-line evidence use `start=end`.
- Append newest entries first under the matching active work item.
- Promote durable conclusions into the linked ticket after verification.

## Active Items
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| context_compass artifact reference cleanup | review | codex | none | walk through cleanup outcomes and confirm acceptance for closure | `context_compass/tasks/2026-02-14_context_compass_artifact_reference_cleanup_task.md` | 2026-02-14 | REQUIRED |
| optimize melder epic | in_progress | codex | none | all active optimization stories are now in review state; route acceptance and move approved tickets | `context_compass/epics/2026-02-13_optimize_melder_epic.md` | 2026-02-14 | REQUIRED |
| optimize conjure paths | review | codex | none | confirm acceptance for scheduler-lifecycle/phase-unit/activation-scan tasks, then move approved tickets | `context_compass/stories/2026-02-13_optimize_conjure_paths_story.md` | 2026-02-14 | REQUIRED |
| optimize meld paths | review | codex | none | review/confirm `TASK-2026-02-13-meld-dynamic-gate-fastdoor` acceptance, then close/move as directed | `context_compass/stories/2026-02-13_optimize_meld_paths_story.md` | 2026-02-14 | REQUIRED |
| optimize spellcrafter phases | review | codex | none | rank-1/rank-2 are in review with measured gains; request closure direction | `context_compass/stories/2026-02-13_optimize_spellcrafter_phases_story.md` | 2026-02-14 | REQUIRED |
| optimize creation context codegen | review | codex | none | rank-1/rank-2/rank-3 are implemented; walk outcomes and request closure acceptance | `context_compass/stories/2026-02-13_optimize_creation_context_codegen_story.md` | 2026-02-14 | REQUIRED |

## Active Attention Details
- TYPE: MEASURE
- CLAIM: `TASK-2026-02-14-optimize-phase9-injection-plan-warm-reuse` is implemented and rerun-validated (`3 passed` targeted slice, `1 passed` harness) with reduced phase9 warm slice (`phase_injection_plan_ms` `0.179 -> 0.164`, injection builds `17 -> 15`) and near-neutral total warm impact.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase9_injection_plan_warm_reuse_task.md:6-98`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:6-58`, `context_compass/artifacts/2026-02-14_phase9_injection_plan_warm_reuse_targeted_unit_tests.txt:1-12`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase9_injection_plan_warm_reuse_output.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase9_injection_plan_warm_reuse_output.txt:25-28`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_occurrence_plan_warm_reuse_output.txt:7-9`
- REREAD: REQUIRED
- NEXT: Walk latest phase9 follow-up outcomes with user and confirm closure/move direction.

- TYPE: DECISION
- CLAIM: Phase-testing lane is reopened for one additional follow-up (`TASK-2026-02-14-optimize-phase9-injection-plan-warm-reuse`) because phase9 injection-plan rebuild remains a measurable warm slice.
- EVIDENCE: `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_occurrence_plan_warm_reuse_output.txt:7-7`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_occurrence_plan_warm_reuse_output.txt:25-28`, `context_compass/tasks/completed/2026-02-14_optimize_phase9_injection_plan_warm_reuse_task.md:1-87`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:6-57`
- REREAD: REQUIRED
- NEXT: Implement phase9 injection-plan warm-reuse gate and attach targeted unit + harness artifacts.

- TYPE: MEASURE
- CLAIM: `TASK-2026-02-14-optimize-phase8-occurrence-plan-warm-reuse` is implemented and rerun-validated (`3 passed` targeted slice, `1 passed` harness) with net warm-chain gain (`group_8_11_total_ms` `2.206 -> 2.114`, `phase_execution_plan_ms` `0.988 -> 0.751`).
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase8_occurrence_plan_warm_reuse_task.md:6-98`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:6-56`, `context_compass/artifacts/2026-02-14_phase8_occurrence_plan_warm_reuse_targeted_unit_tests.txt:1-12`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_occurrence_plan_warm_reuse_output.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_occurrence_plan_warm_reuse_output.txt:59-59`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase10_patch_maps_warm_reuse_output.txt:7-9`
- REREAD: REQUIRED
- NEXT: Walk latest phase8 follow-up outcomes with user and confirm closure/move direction.

- TYPE: DECISION
- CLAIM: Phase-testing lane is reopened for one additional follow-up (`TASK-2026-02-14-optimize-phase8-occurrence-plan-warm-reuse`) because phase8 occurrence-plan rebuild is now the dominant warm hotspot.
- EVIDENCE: `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase10_patch_maps_warm_reuse_output.txt:7-7`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase10_patch_maps_warm_reuse_output.txt:17-19`, `context_compass/tasks/completed/2026-02-14_optimize_phase8_occurrence_plan_warm_reuse_task.md:1-87`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:6-56`
- REREAD: REQUIRED
- NEXT: Implement phase8 occurrence-plan warm-reuse gate and attach targeted unit + harness artifacts.

- TYPE: MEASURE
- CLAIM: `TASK-2026-02-14-optimize-phase10-patch-maps-warm-reuse` is implemented and rerun-validated (`3 passed` targeted slice, `1 passed` harness) with strong warm reduction (`phase_patch_maps_ms` `0.743 -> 0.026`, `group_8_11_total_ms` `3.024 -> 2.206`).
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase10_patch_maps_warm_reuse_task.md:6-98`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:6-55`, `context_compass/artifacts/2026-02-14_phase10_patch_maps_warm_reuse_targeted_unit_tests.txt:1-12`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase10_patch_maps_warm_reuse_output.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase10_patch_maps_warm_reuse_output.txt:59-59`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_set_warm_reuse_output.txt:7-9`
- REREAD: REQUIRED
- NEXT: Walk latest phase-testing follow-up outcomes with user and confirm closure/move direction.

- TYPE: DECISION
- CLAIM: Phase-testing lane is reopened for one additional follow-up (`TASK-2026-02-14-optimize-phase10-patch-maps-warm-reuse`) because warm sample still shows phase10 patch-map rebuild as a measurable slice.
- EVIDENCE: `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_set_warm_reuse_output.txt:7-7`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_set_warm_reuse_output.txt:20-22`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_set_warm_reuse_output.txt:26-26`, `context_compass/tasks/completed/2026-02-14_optimize_phase10_patch_maps_warm_reuse_task.md:1-87`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:6-54`
- REREAD: REQUIRED
- NEXT: Implement phase10 patch-map warm-reuse gate and attach targeted unit + harness artifacts.

- TYPE: MEASURE
- CLAIM: `TASK-2026-02-14-optimize-phase11-variant-set-warm-reuse` is implemented and rerun-validated (`6 passed` targeted unit slice, `1 passed` harness) with warm 8-11 reduction (`group_8_11_total_ms` `3.167 -> 3.024`, `phase_execution_plan_ms` `1.383 -> 0.989`).
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase11_variant_set_warm_reuse_task.md:6-98`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:6-54`, `context_compass/artifacts/2026-02-14_phase11_variant_set_warm_reuse_targeted_unit_tests.txt:1-12`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_set_warm_reuse_output.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_set_warm_reuse_output.txt:23-25`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_rebuild_elision_output.txt:7-9`
- REREAD: REQUIRED
- NEXT: Walk final phase-testing follow-up outcomes with user and confirm closure/move direction.

- TYPE: DECISION
- CLAIM: Phase-testing lane is reopened for one additional follow-up (`TASK-2026-02-14-optimize-phase11-variant-set-warm-reuse`) because warm profile still shows measurable phase11 overhead and unchanged-signature flow still derives sibling variants each run.
- EVIDENCE: `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_rebuild_elision_output.txt:17-25`, `src/melder/spellbook/spell_crafter/spell_crafter.py:4100-4188`, `src/melder/spellbook/spell_crafter/spell_crafter.py:4229-4300`, `context_compass/tasks/completed/2026-02-14_optimize_phase11_variant_set_warm_reuse_task.md:1-87`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:6-53`
- REREAD: REQUIRED
- NEXT: Implement the new phase11 task and attach targeted unit + harness rerun artifacts.

- TYPE: MEASURE
- CLAIM: `TASK-2026-02-14-optimize-phase11-plan-rebuild-elision` is now implemented and rerun-validated with captured artifacts (`5 passed` targeted phase11 unit slice, `1 passed` component harness); story checklist is complete and routed to review.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase11_plan_rebuild_elision_task.md:6-147`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:6-6`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:52-52`, `context_compass/artifacts/2026-02-14_phase11_plan_rebuild_elision_targeted_unit_tests.txt:1-12`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_rebuild_elision_output.txt:7-7`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_rebuild_elision_output.txt:59-59`
- REREAD: REQUIRED
- NEXT: Walk phase-testing epic/story outcomes with user and confirm closure/move direction.

- TYPE: DECISION
- CLAIM: Phase-testing backlog is reopened for one additional phase11 follow-up (`TASK-2026-02-14-optimize-phase11-plan-rebuild-elision`) targeting repeated no-overrides full-build overhead still visible after plan-based compile changes.
- EVIDENCE: `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:6-6`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:51-52`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:74-81`, `context_compass/tasks/completed/2026-02-14_optimize_phase11_plan_rebuild_elision_task.md:1-80`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_based_compile_output.txt:17-20`
- REREAD: REQUIRED
- NEXT: Implement the plan-rebuild-elision task and rerun targeted unit + harness validation.

- TYPE: DECISION
- CLAIM: Optimization-wave story routing was normalized: `optimize-conjure-paths`, `optimize-meld-paths`, and `optimize-creation-context-codegen` are now marked `review` to reflect completed implementation checklists.
- EVIDENCE: `context_compass/epics/2026-02-13_optimize_melder_epic.md:123-139`, `context_compass/stories/2026-02-13_optimize_conjure_paths_story.md:6-6`, `context_compass/stories/2026-02-13_optimize_meld_paths_story.md:6-6`, `context_compass/stories/2026-02-13_optimize_creation_context_codegen_story.md:6-6`
- REREAD: REQUIRED
- NEXT: Run user acceptance walk-through for review stories and move approved tickets.

- TYPE: DECISION
- CLAIM: Phase-testing baseline stories were normalized from stale `in_progress` state to `review` and their linked task rows were checked complete, matching the already-reviewed task tickets.
- EVIDENCE: `context_compass/epics/completed/2026-02-14_phase_testing_epic.md:126-142`, `context_compass/stories/completed/2026-02-14_phase_component_cprofile_harness_story.md:6-6`, `context_compass/stories/completed/2026-02-14_phase_component_cprofile_harness_story.md:44-45`, `context_compass/stories/completed/2026-02-14_phase_group_1_4_baseline_story.md:6-6`, `context_compass/stories/completed/2026-02-14_phase_group_1_4_baseline_story.md:42-42`, `context_compass/stories/completed/2026-02-14_phase_group_5_7_conduit_baseline_story.md:6-6`, `context_compass/stories/completed/2026-02-14_phase_group_5_7_conduit_baseline_story.md:43-43`, `context_compass/stories/completed/2026-02-14_phase_group_5_7_local_baseline_story.md:6-6`, `context_compass/stories/completed/2026-02-14_phase_group_5_7_local_baseline_story.md:43-43`, `context_compass/stories/completed/2026-02-14_phase_group_8_11_baseline_story.md:6-6`, `context_compass/stories/completed/2026-02-14_phase_group_8_11_baseline_story.md:44-44`
- REREAD: REQUIRED
- NEXT: Request closure acceptance for the phase-testing story set and move approved tickets.

- TYPE: MEASURE
- CLAIM: The plan-based no-overrides compile follow-up is rerun-validated with fresh artifacts: targeted spell-crafter slice passes (`10 passed`) and harness rerun passes (`1 passed`) with updated warm phase11 output.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase11_plan_based_no_overrides_compile_task.md:69-76`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:51-83`, `context_compass/epics/completed/2026-02-14_phase_testing_epic.md:128-135`, `context_compass/artifacts/2026-02-14_phase11_plan_based_compile_targeted_unit_tests.txt:1-12`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_based_compile_output.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_based_compile_output.txt:59-59`
- REREAD: REQUIRED
- NEXT: Request user acceptance for closure and move task/story/epic as directed.

- TYPE: FACT
- CLAIM: The follow-up fix preserved strict production plan contracts by correcting the test fixture: `_make_phase11_plan_stub` now always includes `root_instance_key` instead of adding defensive runtime introspection to hot-path signature logic.
- EVIDENCE: `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:4234-4265`, `context_compass/tasks/completed/2026-02-14_optimize_phase11_plan_based_no_overrides_compile_task.md:78-85`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:85-92`
- REREAD: REQUIRED
- NEXT: Keep fixture contract alignment for future plan-based compile tests.

- TYPE: DECISION
- CLAIM: Phase-testing backlog is reopened for one additional phase11 follow-up: remove no-overrides IR payload build from `run_phase_execution_plan` compile-signature path via plan-based compile/signature wiring.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase11_plan_based_no_overrides_compile_task.md:1-79`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:43-51`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:72-80`
- REREAD: REQUIRED
- NEXT: Implement task changes in SpellCrafter/compiler path and rerun targeted unit + harness validations.

- TYPE: DECISION
- CLAIM: Lazy phase8-11 capture follow-up is accepted and moved to completed after rerun validation.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase11_lazy_phase8_11_capture_task_completed.md:1-83`, `context_compass/artifacts/2026-02-14_phase11_lazy_capture_targeted_unit_tests.txt:12-12`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_lazy_capture_output.txt:7-9`
- REREAD: REQUIRED
- NEXT: Route phase-testing backlog story closure and then continue next active phase ticket.

- TYPE: MEASURE
- CLAIM: Lazy phase8-11 capture follow-up rerun remains strong: warm `group_8_11_total_ms` improved `8.124 -> 3.644`, `phase_execution_plan_ms` improved `6.289 -> 1.815`, and warm calls dropped `96062 -> 56255`.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase11_lazy_phase8_11_capture_task_completed.md:1-83`, `src/melder/spellbook/spell_crafter/spell_crafter.py:3759-3768`, `src/melder/spellbook/spell_crafter/spell_crafter.py:1968-2035`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_reuse_output.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_lazy_capture_output.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_lazy_capture_output.txt:9-9`, `context_compass/artifacts/2026-02-14_phase11_lazy_capture_targeted_unit_tests.txt:12-12`
- REREAD: REQUIRED
- NEXT: Keep as the latest phase11 warm anchor while routing backlog closure.

- TYPE: DECISION
- CLAIM: Phase-testing backlog is re-opened for one additional follow-up because warm profile after phase11 variant reuse still shows eager `_capture_phase8_11_codegen_ir*` as the largest phase11 slice.
- EVIDENCE: `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_reuse_output.txt:17-21`, `src/melder/spellbook/spell_crafter/spell_crafter.py:3759-3768`, `context_compass/tasks/completed/2026-02-14_optimize_phase11_lazy_phase8_11_capture_task_completed.md:1-39`
- REREAD: REQUIRED
- NEXT: Keep as historical anchor for why lazy-capture follow-up was opened.

- TYPE: MEASURE
- CLAIM: Phase11 variant-reuse follow-up is now implemented and validated: warm 8-11 totals improved (`group_8_11_total_ms` `9.085 -> 8.124`, `phase_execution_plan_ms` `7.3 -> 6.289`), warm cProfile calls dropped (`108778 -> 96062`), and phase11 plan rebuild calls dropped (`51 -> 17`) for `_build_execution_plan_variant` and `ExecutionPlanBuilder.build`.
- EVIDENCE: `src/melder/spellbook/spell_crafter/spell_crafter.py:3726-3754`, `src/melder/spellbook/spell_crafter/spell_crafter.py:3808-3867`, `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:5578-5719`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:21-22`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_reuse_output.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_variant_reuse_output.txt:26-27`, `context_compass/artifacts/2026-02-14_phase11_variant_reuse_targeted_unit_tests.txt:1-1`, `context_compass/artifacts/2026-02-14_phase11_variant_reuse_targeted_unit_tests.txt:12-12`
- REREAD: REQUIRED
- NEXT: User accepted; task moved to completed and now serves as baseline for the lazy-capture follow-up.

- TYPE: DECISION
- CLAIM: Phase-testing optimization backlog was re-opened for one additional ranked follow-up because the latest warm sample still shows heavy phase11 variant rebuild churn (`51` calls to `_build_execution_plan_variant` and `ExecutionPlanBuilder.build`).
- EVIDENCE: `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:44-49`, `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:71-78`, `context_compass/tasks/completed/2026-02-14_optimize_phase11_execution_plan_variant_reuse_task_completed.md:4-11`, `context_compass/tasks/completed/2026-02-14_optimize_phase11_execution_plan_variant_reuse_task_completed.md:61-69`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:21-23`
- REREAD: REQUIRED
- NEXT: Keep as historical anchor for why the follow-up was opened; current active next step is acceptance/closure routing after implementation.

- TYPE: MEASURE
- CLAIM: Phase-testing rank-2 row-builder task gained a measurable warm improvement after the `PathRegistry.format_path` memoization follow-up pass (`group_8_11_total_ms` `9.804 -> 9.085`, `phase_patch_maps_ms` `1.288 -> 0.573`, calls `120524 -> 108778`).
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase8_10_plan_row_builders_task.md:65-72`, `src/melder/spellbook/spell_crafter/dag/dag_index.py:182-191`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run8.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run8.txt:25-27`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:32-34`
- REREAD: REQUIRED
- NEXT: Walk rank1/rank2/rank3 outcomes with user and confirm closure/move direction for phase-testing backlog tasks.

- TYPE: MEASURE
- CLAIM: SpellCrafter rank-2 signature-hash task moved to review after tuple-hash `steps_rows_signature` update; latest harness shows lower warm overhead and reduced signature serialization churn.
- EVIDENCE: `context_compass/tasks/2026-02-14_optimize_phase11_signature_hash_pipeline_task.md:6-93`, `src/melder/spellbook/spell_crafter/spell_crafter.py:1756-1758`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run7.txt:7-38`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run8.txt:7-41`
- REREAD: REQUIRED
- NEXT: Walk rank-1/rank-2 outcomes with user and confirm close/move direction.

- TYPE: MEASURE
- CLAIM: Conjure activation/validation scan fastpath is implemented and in review with fresh targeted spellbook coverage (`12 passed`) after removing the redundant `_resolve_conjure_policy` duplicate-id recheck.
- EVIDENCE: `context_compass/tasks/2026-02-14_conjure_activation_and_validation_scan_fastpath_task.md:6-69`, `src/melder/spellbook/spellbook_creation_system.py:258-285`, `context_compass/artifacts/2026-02-14_conjure_activation_validation_scan_fastpath_pytests.txt:1-12`
- REREAD: REQUIRED
- NEXT: Confirm acceptance for activation/validation task and route move-to-completed.

- TYPE: MEASURE
- CLAIM: Conjure phase-unit-allocation fastpath is implemented and in review with fresh focused validation (`4 passed` spellbook factory suite + `10 passed` scheduler suite).
- EVIDENCE: `context_compass/tasks/2026-02-14_conjure_phase_unit_allocation_fastpath_task.md:6-77`, `src/melder/spellbook/spellbook_creation_system.py:1560-1619`, `src/melder/spellbook/spellbook_creation_system.py:1622-1719`, `src/melder/spellbook/spellbook_creation_system.py:1761-1883`, `context_compass/artifacts/2026-02-14_conjure_phase_unit_allocation_fastpath_pytests.txt:1-12`, `context_compass/artifacts/2026-02-14_conjure_phase_unit_allocation_fastpath_phase_scheduler_pytests.txt:1-12`
- REREAD: REQUIRED
- NEXT: Confirm acceptance for phase-unit task and route move-to-completed.

- TYPE: MEASURE
- CLAIM: Conduit-resolution scheduler-lifecycle reduction is implemented and in review: phases 5-11 now execute under one scheduler lifecycle with foundational-error snapshot gating for plan-phase skip behavior.
- EVIDENCE: `context_compass/tasks/2026-02-14_conjure_scheduler_lifecycle_reduction_task.md:6-10`, `src/melder/spellbook/spellbook_creation_system.py:740-759`, `src/melder/spellbook/spellbook_creation_system.py:852-933`, `context_compass/artifacts/2026-02-14_conjure_scheduler_lifecycle_single_run_fastpath_pytests.txt:1-12`
- REREAD: REQUIRED
- NEXT: Request acceptance for scheduler-lifecycle task and route remaining conjure tasks to closure.

- TYPE: DECISION
- CLAIM: Phase12 optimization wave is closed for this iteration: rank-1, rank-2, and benchmark-entrypoint repair tasks were moved to completed and the phase12 story was archived after user acceptance and reported override speed gains.
- EVIDENCE: `context_compass/stories/completed/2026-02-13_optimize_phase12_codegen_story.md:1-5`, `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:1-4`, `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:1-4`, `context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:1-4`, `context_compass/artifacts/2026-02-14_user_reported_override_perf_test_overrides_all.txt:1-30`
- REREAD: REQUIRED
- NEXT: Keep routing on remaining active optimization stories.

- TYPE: MEASURE
- CLAIM: Phase12 benchmark-entrypoint repair is implemented and validated as done: stale `meld_runtime` dependency is removed, the script runs on head, and fresh route-matrix artifacts are now available.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:6-6`, `context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:37-43`, `context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:62-68`, `context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_output_repaired.txt:1-3`, `context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_report_repaired.json:19-31`
- REREAD: REQUIRED
- NEXT: none (closed anchor; phase12 wave accepted and archived).

- TYPE: MEASURE
- CLAIM: Phase12 rank-2 helper-callpath tightening is implemented and validated as done (`47 passed` focused blueprint suite), adding helper-bypass and precedence guardrail coverage while preserving contract behavior.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:6-6`, `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:24-28`, `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:38-46`, `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:63-69`, `context_compass/artifacts/2026-02-14_phase12_override_helper_callpath_tightening_blueprint_pytests.txt:1-1`, `context_compass/artifacts/2026-02-14_phase12_override_helper_callpath_tightening_blueprint_pytests.txt:12-12`
- REREAD: REQUIRED
- NEXT: none (closed anchor; phase12 wave accepted and archived).

- TYPE: MEASURE
- CLAIM: Phase12 rank-1 shape-specialized source task is implemented and validated as done: CreationContext now reuses override source/code artifacts by plan signature, blueprint tests cover shape-emitter contracts, and targeted suites passed (`62 passed`).
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:6-6`, `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:24-29`, `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:41-49`, `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:66-72`, `context_compass/artifacts/2026-02-14_phase12_override_shape_specialized_source_targeted_pytests.txt:1-1`, `context_compass/artifacts/2026-02-14_phase12_override_shape_specialized_source_targeted_pytests.txt:12-12`
- REREAD: REQUIRED
- NEXT: none (closed anchor; phase12 wave accepted and archived).

- TYPE: DECISION
- CLAIM: Phase12 discovery is complete and converted into ranked follow-up tasks: rank-1 shape-specialized override source, rank-2 helper callpath tightening, and benchmark-entrypoint repair as measurement unblock; existing route-matrix artifacts still show targeted override route as the highest warm-cost lane.
- EVIDENCE: `context_compass/tasks/2026-02-13_discovery_phase12_codegen_task.md:157-164`, `context_compass/stories/completed/2026-02-13_optimize_phase12_codegen_story.md:63-70`, `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:1-70`, `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:1-68`, `context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:1-66`, `benchmarks/testing_other_di/results/codegen_benchmark_report_smoke_v2_pass12.json:19-31`, `context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_output_env_root_src.txt:17-21`
- REREAD: REQUIRED
- NEXT: Walk discovery outcomes with user, confirm closure acceptance, then execute rank-1 Phase12 optimization task.

- TYPE: MEASURE
- CLAIM: CreationContext rank-3 prefilter caching is implemented and validated: miss-path compile now reuses step-target/path-metadata caches via internal helper plumbing, focused unit suites passed (`17` + `40` tests), and harness reruns remained warm-neutral/slightly-better (`10.31` / `10.631` ms) with stable warm profile shape.
- EVIDENCE: `context_compass/tasks/2026-02-14_optimize_creation_context_override_prefilter_caching_task.md:70-127`, `context_compass/stories/2026-02-13_optimize_creation_context_codegen_story.md:47-89`, `context_compass/artifacts/2026-02-14_creation_context_override_prefilter_caching_creation_context_unit_tests.txt:12-12`, `context_compass/artifacts/2026-02-14_creation_context_override_prefilter_caching_phase12_overrides_unit_tests.txt:12-12`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_creation_context_override_prefilter_caching_output.txt:7-38`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_creation_context_override_prefilter_caching_output_run2.txt:7-38`
- REREAD: REQUIRED
- NEXT: Walk through rank-1/rank-2/rank-3 outcomes and request user acceptance for story closure.

- TYPE: MEASURE
- CLAIM: CreationContext rank-2 miss-compile reuse is implemented and validated: miss-path specialization now reuses step-count source/code-object artifacts, focused unit suites passed (`16` + `38` tests), and harness reruns remained warm-neutral (`10.793` / `10.621` ms with unchanged warm profile shape).
- EVIDENCE: `context_compass/tasks/2026-02-14_optimize_creation_context_override_miss_compile_reuse_task.md:70-118`, `context_compass/stories/2026-02-13_optimize_creation_context_codegen_story.md:47-83`, `context_compass/artifacts/2026-02-14_creation_context_override_miss_compile_reuse_creation_context_unit_tests.txt:12-12`, `context_compass/artifacts/2026-02-14_creation_context_override_miss_compile_reuse_phase12_overrides_unit_tests.txt:12-12`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_creation_context_override_miss_compile_reuse_output.txt:7-38`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_creation_context_override_miss_compile_reuse_output_run2.txt:7-38`
- REREAD: REQUIRED
- NEXT: Request user acceptance for rank-2 keep-vs-iterate, then start rank-3 (`TASK-2026-02-14-optimize-creation-context-override-prefilter-caching`).

- TYPE: MEASURE
- CLAIM: CreationContext rank-1 override-shape preprocessing task is implemented and validated, and active-surface `meld_runtime` terminology has been normalized to `CreationContext`; focused regression suites passed (`31`, `1`, and `2` tests).
- EVIDENCE: `context_compass/tasks/2026-02-14_optimize_creation_context_override_shape_preprocessing_task.md:82-109`, `context_compass/stories/2026-02-13_optimize_creation_context_codegen_story.md:46-77`, `context_compass/artifacts/2026-02-14_meld_runtime_rename_conduit_facade_tests.txt:12-12`, `context_compass/artifacts/2026-02-14_meld_runtime_rename_test_meld_2_targeted.txt:12-12`, `context_compass/artifacts/2026-02-14_meld_runtime_rename_test_meld_cleanup_targeted.txt:12-12`
- REREAD: REQUIRED
- NEXT: Request user acceptance for rank-1 keep-vs-iterate, then start rank-2 (`TASK-2026-02-14-optimize-creation-context-override-miss-compile-reuse`).

- TYPE: DECISION
- CLAIM: CreationContext discovery is complete and translated into three ranked execution tasks: (1) override shape preprocessing, (2) override miss compile reuse, (3) override prefilter caching.
- EVIDENCE: `context_compass/tasks/2026-02-13_discovery_creation_context_codegen_task.md:25-97`, `context_compass/stories/2026-02-13_optimize_creation_context_codegen_story.md:44-109`, `context_compass/tasks/2026-02-14_optimize_creation_context_override_shape_preprocessing_task.md:1-63`, `context_compass/tasks/2026-02-14_optimize_creation_context_override_miss_compile_reuse_task.md:1-64`, `context_compass/tasks/2026-02-14_optimize_creation_context_override_prefilter_caching_task.md:1-62`
- REREAD: REQUIRED
- NEXT: Discovery accepted and rank-1 executed; use newest rank-1 measure note above to route keep-vs-iterate and rank-2 start.

- TYPE: MEASURE
- CLAIM: SpellCrafter rank-3 row-builder contract-fastpath task is implemented and validated with two harness reruns; warm `group_8_11_total_ms` measured `11.047` then `10.266`, and warm cProfile sample stabilized at `0.034s` with `122060` calls versus pre-rank3 rank-2 samples at `0.036s` with `123618` calls.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase8_10_codegen_row_builder_contract_fastpath_task.md:1-105`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_contract_fastpath_output.txt:7-38`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_contract_fastpath_output_run2.txt:7-38`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run6.txt:7-38`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run7.txt:7-38`
- REREAD: REQUIRED
- NEXT: Rank-3 accepted and closed; continue with creation-context discovery and finalize remaining SpellCrafter closure decisions.

- TYPE: MEASURE
- CLAIM: SpellCrafter rank-2 signature-pipeline work is implemented with regression-rollback evidence; final dispatch keeps schema stable and reduces `_pickle.dumps` calls (`996 -> 724`) with near-neutral warm metrics versus rank-1 anchor (`group_8_11_total_ms` `10.567` -> `10.552/10.833`, warm cProfile `0.035s` -> `0.036s`).
- EVIDENCE: `context_compass/tasks/2026-02-14_optimize_phase11_signature_hash_pipeline_task.md:61-131`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output_run2.txt:7-38`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run6.txt:7-39`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run7.txt:7-39`
- REREAD: REQUIRED
- NEXT: Get user keep-vs-iterate/closure direction for rank-2.

- TYPE: MEASURE
- CLAIM: SpellCrafter rank-1 dirty-capture implementation is complete and in review; warm 8-11 totals dropped from ~`26ms` to ~`10.6ms` across two reruns with lower warm cProfile sample (`~0.081/0.082s` -> `0.035s`).
- EVIDENCE: `context_compass/tasks/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md:60-90`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output_run2.txt:7-9`
- REREAD: REQUIRED
- NEXT: Get user acceptance for rank-1 and continue with rank-2 task (`TASK-2026-02-14-optimize-phase11-signature-hash-pipeline`).

- TYPE: FACT
- CLAIM: SpellCrafter discovery is complete and now queued with three ranked follow-up optimization tasks; top priority is reducing phase8-11 capture-frequency recomputation.
- EVIDENCE: `context_compass/tasks/2026-02-13_discovery_spellcrafter_phases_task.md:63-113`, `context_compass/stories/2026-02-13_optimize_spellcrafter_phases_story.md:43-55`, `context_compass/tasks/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md:1-76`, `context_compass/tasks/2026-02-14_optimize_phase11_signature_hash_pipeline_task.md:1-76`, `context_compass/tasks/completed/2026-02-14_optimize_phase8_10_codegen_row_builder_contract_fastpath_task.md:1-105`
- REREAD: REQUIRED
- NEXT: Start rank-1 SpellCrafter follow-up implementation task and capture baseline-vs-after evidence.

- TYPE: MEASURE
- CLAIM: Rank-3 phase5 task is revalidated with clean reruns; focused phase5 suites passed and warm conduit 5-7 metrics remain below the pre-rank3 anchor with expected run-to-run noise.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase5_root_blueprints_hotpath_task.md:59-99`, `context_compass/artifacts/2026-02-14_phase5_opt_builder_unit_tests_rerun_clean.txt:12-12`, `context_compass/artifacts/2026-02-14_phase5_opt_spell_crafter_unit_tests_rerun_clean.txt:12-12`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output.txt:4-4`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:4-4`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output.txt:4-4`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run2.txt:4-4`
- REREAD: REQUIRED
- NEXT: Request user acceptance for rank1/rank2/rank3 and decide closure vs extra iteration.

- TYPE: MEASURE
- CLAIM: Rank-2 optimization task is implemented and validated; warm 8-11 total is mixed across two reruns (`27.932ms` and `25.438ms`) versus rank1 anchor (`27.829ms`), while warm cProfile sample improved from `0.083s` to `0.081s`/`0.080s`.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase8_10_plan_row_builders_task.md:98-105`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_opt_output.txt:12-15`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output.txt:7-9`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run2.txt:7-9`
- REREAD: REQUIRED
- NEXT: Get user keep-vs-iterate/closure direction for rank-2.

- TYPE: FACT
- CLAIM: Rank-1 optimization task is now implemented and validated; warm 8-11 sample dropped from `34.993ms` to `27.829ms`, and warm cProfile sample dropped from `0.091s` to `0.083s`.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_optimize_phase11_codegen_ir_capture_task.md:57-89`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:11-15`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_opt_output.txt:12-15`
- REREAD: REQUIRED
- NEXT: Start `TASK-2026-02-14-optimize-phase8-10-plan-row-builders`.

- TYPE: FACT
- CLAIM: Optimization backlog ranking is complete and three scoped follow-up tasks were created from measured phase-testing outputs.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_discovery_phase_testing_optimization_backlog_task.md:47-82`, `context_compass/tasks/completed/2026-02-14_optimize_phase11_codegen_ir_capture_task.md:1-12`, `context_compass/tasks/completed/2026-02-14_optimize_phase8_10_plan_row_builders_task.md:1-12`, `context_compass/tasks/completed/2026-02-14_optimize_phase5_root_blueprints_hotpath_task.md:1-12`
- REREAD: REQUIRED
- NEXT: Start rank-1 optimization implementation task.

- TYPE: FACT
- CLAIM: Harness validation and baseline measurement execution are complete; a durable artifact now contains 1-4, 5-7 conduit/local, and 8-11 measurements plus warm 8-11 cProfile output.
- EVIDENCE: `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:5-14`, `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:51-52`
- REREAD: REQUIRED
- NEXT: Continue `TASK-2026-02-14-discovery-phase-testing-optimization-backlog` with ranked hotspot candidates and follow-up task creation.

- TYPE: FACT
- CLAIM: Execution tasks were created for harness implementation and baseline measurement runs, providing a concrete unblock path for phase-testing ranking.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_implement_phase_component_cprofile_harness_task.md:1`, `context_compass/tasks/completed/2026-02-14_execute_phase_group_baseline_measurements_task.md:1`
- REREAD: REQUIRED
- NEXT: Implement `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` and run it with `pytest -q -s`.

- TYPE: FACT
- CLAIM: Phase-testing optimization-backlog discovery is blocked until measured outputs are attached; readiness gate and ranking schema are documented.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_discovery_phase_testing_optimization_backlog_task.md:6`, `context_compass/tasks/completed/2026-02-14_discovery_phase_testing_optimization_backlog_task.md:28`
- REREAD: REQUIRED
- NEXT: Confirm acceptance for discovery tickets, then implement/run harness baselines to produce measured artifacts.

- TYPE: FACT
- CLAIM: Phase 8-11 baseline discovery is documented and in review with per-spell chain contract, warm/cold variants, and execution-plan metric outputs.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_discovery_phase_group_8_11_baseline_task.md:1`, `context_compass/stories/completed/2026-02-14_phase_group_8_11_baseline_story.md:1`
- REREAD: REQUIRED
- NEXT: Execute `TASK-2026-02-14-discovery-phase-testing-optimization-backlog`.

- TYPE: FACT
- CLAIM: Local 5-7 baseline discovery is documented and in review with target-scoped chain and scoped-size reporting contract.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_discovery_phase_group_5_7_local_baseline_task.md:1`, `context_compass/stories/completed/2026-02-14_phase_group_5_7_local_baseline_story.md:1`
- REREAD: REQUIRED
- NEXT: Execute `TASK-2026-02-14-discovery-phase-group-8-11-baseline`.

- TYPE: FACT
- CLAIM: Conduit-wide 5-7 baseline discovery is documented and in review with lead-spell frame-scoped direct-call sequencing and ranking output fields.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_discovery_phase_group_5_7_conduit_baseline_task.md:1`, `context_compass/stories/completed/2026-02-14_phase_group_5_7_conduit_baseline_story.md:1`
- REREAD: REQUIRED
- NEXT: Execute `TASK-2026-02-14-discovery-phase-group-5-7-local-baseline`.

- TYPE: FACT
- CLAIM: Phase 1-4 baseline discovery is documented and in review with full-spellbook default scope, optional single-spell diagnostic slice, and explicit warm/cold variant contract.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_discovery_phase_group_1_4_baseline_task.md:1`, `context_compass/stories/completed/2026-02-14_phase_group_1_4_baseline_story.md:1`
- REREAD: REQUIRED
- NEXT: Execute `TASK-2026-02-14-discovery-phase-group-5-7-conduit-baseline`.

- TYPE: FACT
- CLAIM: Harness discovery contract is documented and in review: four direct-call phase groups with no scheduler path, production-order gating, and standardized profile output schema.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_discovery_phase_component_cprofile_harness_task.md:34`, `context_compass/stories/completed/2026-02-14_phase_component_cprofile_harness_story.md:1`
- REREAD: REQUIRED
- NEXT: Confirm acceptance for `TASK-2026-02-14-discovery-phase-component-cprofile-harness`, then execute `TASK-2026-02-14-discovery-phase-group-1-4-baseline`.

- TYPE: FACT
- CLAIM: Artifact reference cleanup is implemented: legacy artifact links remapped to canonical index, placeholder files removed, and global reference scan is clean.
- EVIDENCE: `context_compass/tasks/2026-02-14_context_compass_artifact_reference_cleanup_task.md:1`, `context_compass/artifacts/README.md:1`
- REREAD: REQUIRED
- NEXT: Confirm acceptance and close the cleanup task.

- TYPE: FACT
- CLAIM: New user-directed migration requires renaming `codex_todo` to `context_compass`, adding generalized core/profile structure, and adding microcycle-config toggles.
- EVIDENCE: `context_compass/tasks/completed/2026-02-14_context_compass_rename_and_profile_config_task.md:1`, `context_compass/stories/completed/2026-02-14_context_compass_core_profile_packaging_story.md:1`
- REREAD: REQUIRED
- NEXT: none (accepted and closed; keep as historical anchor).

- TYPE: FACT
- CLAIM: Onboarding hardening patch is implemented across AGENTS/workflow/skills/behavioral docs/templates with microcycle gates, UNKNOWN-first defaults, and board-first routing.
- EVIDENCE: `context_compass/AGENTS.MD:437`, `context_compass/WORKFLOW.md:72`, `context_compass/agent_onboarding/agent/general/skills/context_window_budget.md:1`, `context_compass/templates/task_template.md:22`
- REREAD: REQUIRED
- NEXT: none (accepted and closed; keep as historical anchor).

- TYPE: FACT
- CLAIM: Onboarding docs contain routing drift where `00_overview.md` is referenced as active state while compaction policy already declares `attention_board.md` canonical.
- EVIDENCE: `context_compass/CONTEXT_COMPACTION.md:8`, `context_compass/agent_onboarding/agent/general/skills/context_protocol.md:12`, `context_compass/agent_onboarding/agent/general/behavioral_guidelines/onboarding_summary.md:23`
- REREAD: REQUIRED
- NEXT: Keep as historical anchor; normalization has been implemented in the active onboarding hardening task.

- TYPE: FACT
- CLAIM: Phase-testing discovery scope now includes an explicit 8-11 baseline story/task, and missing discovery task files were created for spellcrafter, creation_context codegen, and phase12 codegen stories.
- EVIDENCE: `context_compass/epics/completed/2026-02-14_phase_testing_epic.md:1`, `context_compass/stories/completed/2026-02-14_phase_group_8_11_baseline_story.md:1`, `context_compass/tasks/completed/2026-02-14_discovery_phase_group_8_11_baseline_task.md:1`, `context_compass/tasks/2026-02-13_discovery_spellcrafter_phases_task.md:1`, `context_compass/tasks/2026-02-13_discovery_creation_context_codegen_task.md:1`, `context_compass/tasks/2026-02-13_discovery_phase12_codegen_task.md:1`
- REREAD: REQUIRED
- NEXT: Execute discovery tasks in phase-group order and append evidence-backed hotspots into linked story/task notes.

- TYPE: FACT
- CLAIM: Created `EPIC-2026-02-14-phase-testing` with discovery-first stories/tasks for direct phase component profiling (`cProfile`) without `PhaseScheduler`, workers, or `UnitOfWork`.
- EVIDENCE: `context_compass/epics/completed/2026-02-14_phase_testing_epic.md:1`, `context_compass/stories/completed/2026-02-14_phase_component_cprofile_harness_story.md:1`, `context_compass/tasks/completed/2026-02-14_discovery_phase_component_cprofile_harness_task.md:1`
- REREAD: REQUIRED
- NEXT: Execute harness discovery task and lock toggle matrix for phase groups.

- TYPE: FACT
- CLAIM: Confirmed two foundational 5-7 tracks exist: conduit-wide and target-local; target-local uses single local-scope phase registrations per phase.
- EVIDENCE: `src/melder/spellbook/spellbook_creation_system.py:1063`, `src/melder/spellbook/spellbook_creation_system.py:1206`, `src/melder/spellbook/spellbook_creation_system.py:1165`
- REREAD: REQUIRED
- NEXT: Keep separate component baseline stories for conduit-wide 5-7 and local 5-7.

- TYPE: FACT
- CLAIM: Removed redundant conjure duplicate-id recheck from `_resolve_conjure_policy`; bind front-door duplicate SHA guard remains intact.
- EVIDENCE: `src/melder/spellbook/spellbook_creation_system.py:280`, `src/melder/spellbook/spellbook_creation_system.py:285`, `src/melder/spellbook/spellbook.py:2496`
- REREAD: REQUIRED
- NEXT: Confirm acceptance and continue `TASK-2026-02-14-conjure-activation-and-validation-scan-fastpath`.

- TYPE: FACT
- CLAIM: Implemented conjure phase-unit-allocation fastpath by consolidating eight per-spell phase factories behind one shared helper with preserved labels/metadata/args behavior.
- EVIDENCE: `src/melder/spellbook/spellbook_creation_system.py:1481`, `src/melder/spellbook/spellbook_creation_system.py:1666`, `tests/unit/melder/spellbook/test_spellbook.py:1343`, `tests/unit/melder/spellbook/test_spellbook.py:2111`
- REREAD: REQUIRED
- NEXT: Confirm task acceptance and move to activation/validation scan fastpath.

- TYPE: FACT
- CLAIM: Fixed `PhaseScheduler` worker-loop empty-queue exception handling (`QueueEmpty`) and added a regression test proving workers survive sparse long phases before phase-2.
- EVIDENCE: `src/melder/utilities/synchronization/phase_scheduler.py:5`, `src/melder/utilities/synchronization/phase_scheduler.py:399`, `tests/unit/melder/utilities/synchronization/test_phase_scheduler.py:185`
- REREAD: REQUIRED
- NEXT: Continue conjure scheduler-path optimization discovery using this regression as a safety guard.

- TYPE: FACT
- CLAIM: Added `active_documentation` skill and enforced `## Notes` sections across active epic/story/task tickets.
- EVIDENCE: `context_compass/agent_onboarding/agent/general/skills/active_documentation.md:1`, `context_compass/agent_onboarding/agent/general/SKILLS.md:20`, `context_compass/WORKFLOW.md:31`, `context_compass/epics/2026-02-13_optimize_melder_epic.md:122`, `context_compass/stories/2026-02-13_optimize_conjure_paths_story.md:115`, `context_compass/tasks/2026-02-13_discovery_conjure_paths_task.md:133`
- REREAD: REQUIRED
- NEXT: Use per-ticket `Notes` as the primary in-flight evidence log while continuing optimization tasks.

- TYPE: FACT
- CLAIM: Conjure discovery completed with ranked hotspots; three follow-up implementation tasks were created and queued in story order.
- EVIDENCE: `context_compass/tasks/2026-02-13_discovery_conjure_paths_task.md:1`, `context_compass/tasks/2026-02-14_conjure_scheduler_lifecycle_reduction_task.md:1`, `context_compass/tasks/2026-02-14_conjure_phase_unit_allocation_fastpath_task.md:1`, `context_compass/tasks/2026-02-14_conjure_activation_and_validation_scan_fastpath_task.md:1`, `context_compass/stories/2026-02-13_optimize_conjure_paths_story.md:1`
- REREAD: REQUIRED
- NEXT: Confirm discovery acceptance, then start scheduler lifecycle reduction task.

- TYPE: FACT
- CLAIM: Conjure discovery task was activated with ticket-first evidence logging and has now been completed.
- EVIDENCE: `context_compass/tasks/2026-02-13_discovery_conjure_paths_task.md:1`, `context_compass/stories/2026-02-13_optimize_conjure_paths_story.md:1`
- REREAD: REQUIRED
- NEXT: Execute first follow-up optimization task in the same story.

- TYPE: FACT
- CLAIM: `TASK-2026-02-13-meld-dynamic-gate-fastdoor` implementation is complete and in review; `Conduit.meld` now uses local alias fastdoor while preserving close/wait/ticket invariants.
- EVIDENCE: `src/melder/aether/conduit/conduit.py:2345`, `tests/unit/melder/aether/conduit/test_conduit_facade.py:746`, `tests/unit/melder/aether/conduit/test_conduit_facade.py:779`, `context_compass/tasks/2026-02-13_meld_dynamic_gate_fastdoor_task.md:1`
- REREAD: REQUIRED
- NEXT: Ask user to confirm acceptance, then move task to completed.

- TYPE: FACT
- CLAIM: `TASK-2026-02-13-meld-validation-gate-microprofile` is accepted and closed; story flow now advances to dynamic gate fastdoor optimization.
- EVIDENCE: `context_compass/tasks/completed/2026-02-13_meld_validation_gate_microprofile_task.md:1`, `context_compass/tasks/2026-02-13_meld_dynamic_gate_fastdoor_task.md:1`, `context_compass/stories/2026-02-13_optimize_meld_paths_story.md:126`
- REREAD: REQUIRED
- NEXT: Execute dynamic gate invariants/discovery and implement fastdoor optimization.

- TYPE: FACT
- CLAIM: `TASK-2026-02-13-meld-validation-gate-microprofile` implementation is complete; Meld now caches per-frame change-control managers while preserving per-call dirty-root checks.
- EVIDENCE: `src/melder/aether/conduit/meld/meld.py:130`, `src/melder/aether/conduit/meld/meld.py:459`, `tests/unit/melder/aether/conduit/meld/test_meld.py:1515`, `context_compass/tasks/completed/2026-02-13_meld_validation_gate_microprofile_task.md:1`
- REREAD: REQUIRED
- NEXT: Use as closed anchor while executing dynamic gate fastdoor task.

- TYPE: FACT
- CLAIM: `TASK-2026-02-13-meld-override-shape-hotpath` is completed and user-accepted; work now proceeds to validation-gate microprofile.
- EVIDENCE: `context_compass/tasks/completed/2026-02-13_meld_override_shape_hotpath_task.md:1`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:571`, `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:388`, `context_compass/tasks/completed/2026-02-13_meld_validation_gate_microprofile_task.md:1`
- REREAD: REQUIRED
- NEXT: Execute baseline profiling and safe micro-optimizations in `TASK-2026-02-13-meld-validation-gate-microprofile`.

- TYPE: FACT
- CLAIM: `TASK-2026-02-13-meld-override-shape-hotpath` implementation is complete with cache-hit short-circuiting of grouped-target collection in `CreationContext` while preserving specialization-key semantics.
- EVIDENCE: `src/melder/aether/conduit/meld/creation_context/creation_context.py:571`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:582`, `src/melder/aether/conduit/meld/creation_context/creation_context.py:653`, `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:189`, `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:388`, `context_compass/tasks/completed/2026-02-13_meld_override_shape_hotpath_task.md:1`
- REREAD: REQUIRED
- NEXT: Keep implementation notes linked while executing the next task.

- TYPE: FACT
- CLAIM: `TASK-2026-02-13-meld-input-resolution-keypath` is completed and user-accepted.
- EVIDENCE: `context_compass/tasks/completed/2026-02-13_meld_input_resolution_keypath_task.md:1`, `src/melder/aether/conduit/meld/meld.py:308`, `tests/unit/melder/aether/conduit/meld/test_meld.py:758`
- REREAD: REQUIRED
- NEXT: Move to `TASK-2026-02-13-meld-override-shape-hotpath`.

- TYPE: FACT
- CLAIM: Implemented non-string meld input keypath optimization by removing redundant pre-hash lookup work and preserving id-fallback semantics.
- EVIDENCE: `src/melder/aether/conduit/meld/meld.py:308`, `src/melder/aether/conduit/meld/meld.py:311`, `src/melder/aether/conduit/meld/meld.py:315`, `tests/unit/melder/aether/conduit/meld/test_meld.py:758`, `tests/unit/melder/aether/conduit/meld/test_meld.py:796`
- REREAD: REQUIRED
- NEXT: Keep as completed anchor evidence; active execution is validation-gate microprofile.

- TYPE: FACT
- CLAIM: `TASK-2026-02-13-meld-contract-defaults-caching` was closed as out-of-scope for the current wave by user direction.
- EVIDENCE: `context_compass/tasks/completed/2026-02-13_meld_contract_defaults_caching_task.md:1`, `context_compass/stories/2026-02-13_optimize_meld_paths_story.md:124`
- REREAD: REQUIRED
- NEXT: Keep focus on remaining meld optimization tasks.

- TYPE: FACT
- CLAIM: Meld discovery leads are now converted into two active implementation tasks plus two completed tasks and one out-of-scope task.
- EVIDENCE: `context_compass/tasks/completed/2026-02-13_meld_contract_defaults_caching_task.md:1`, `context_compass/tasks/completed/2026-02-13_meld_input_resolution_keypath_task.md:1`, `context_compass/tasks/completed/2026-02-13_meld_override_shape_hotpath_task.md:1`, `context_compass/tasks/2026-02-13_meld_dynamic_gate_fastdoor_task.md:1`, `context_compass/tasks/completed/2026-02-13_meld_validation_gate_microprofile_task.md:1`, `context_compass/stories/2026-02-13_optimize_meld_paths_story.md:124`
- REREAD: REQUIRED
- NEXT: Execute remaining tasks in order: validation-gate -> dynamic-gate.

- TYPE: FACT
- CLAIM: Meld-path discovery is documented with Conduit->Meld->CreationContext flow, ranked hotspots, and follow-up implementation tasks.
- EVIDENCE: `context_compass/stories/2026-02-13_optimize_meld_paths_story.md:42`
- REREAD: REQUIRED
- NEXT: Active next implementation task is `TASK-2026-02-13-meld-validation-gate-microprofile`.

- TYPE: FACT
- CLAIM: New optimization wave scaffold exists as one epic plus five discovery-first stories with one discovery task per story.
- EVIDENCE: `context_compass/epics/2026-02-13_optimize_melder_epic.md:1`, `context_compass/stories/2026-02-13_optimize_conjure_paths_story.md:1`, `context_compass/stories/2026-02-13_optimize_meld_paths_story.md:1`, `context_compass/stories/2026-02-13_optimize_spellcrafter_phases_story.md:1`, `context_compass/stories/2026-02-13_optimize_creation_context_codegen_story.md:1`, `context_compass/stories/completed/2026-02-13_optimize_phase12_codegen_story.md:1`
- REREAD: REQUIRED
- NEXT: Execute discovery tasks and expand each story with implementation tasks ranked by measured impact/risk.

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| phase testing epic | done | codex | none | none | `context_compass/epics/completed/2026-02-14_phase_testing_epic.md` | 2026-02-14 | HELPFUL |
| phase11 lazy phase8-11 capture | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_optimize_phase11_lazy_phase8_11_capture_task_completed.md` | 2026-02-14 | HELPFUL |
| phase11 execution-plan variant reuse | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_optimize_phase11_execution_plan_variant_reuse_task_completed.md` | 2026-02-14 | HELPFUL |
| context_compass documentation integrity audit | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_context_compass_documentation_integrity_audit_task.md` | 2026-02-14 | HELPFUL |
| context_compass packaging migration | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_context_compass_rename_and_profile_config_task.md` | 2026-02-14 | HELPFUL |
| onboarding policy hardening | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_onboarding_policy_ticket_note_enforcement_task.md` | 2026-02-14 | HELPFUL |
| optimize phase12 codegen story | done | codex | none | none | `context_compass/stories/completed/2026-02-13_optimize_phase12_codegen_story.md` | 2026-02-14 | HELPFUL |
| phase12 rank-1 override shape specialized source | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md` | 2026-02-14 | HELPFUL |
| phase12 rank-2 override helper callpath tightening | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md` | 2026-02-14 | HELPFUL |
| phase12 benchmark entrypoint repair | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md` | 2026-02-14 | HELPFUL |
| spellcrafter rank-3 row-builder contract fastpath | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_optimize_phase8_10_codegen_row_builder_contract_fastpath_task.md` | 2026-02-14 | HELPFUL |
| meld dynamic gate fastdoor | review | codex | none | waiting for user acceptance | `context_compass/tasks/2026-02-13_meld_dynamic_gate_fastdoor_task.md` | 2026-02-14 | HELPFUL |
| meld validation gate microprofile | done | codex | none | none | `context_compass/tasks/completed/2026-02-13_meld_validation_gate_microprofile_task.md` | 2026-02-14 | HELPFUL |
| meld override shape hotpath | done | codex | none | none | `context_compass/tasks/completed/2026-02-13_meld_override_shape_hotpath_task.md` | 2026-02-14 | HELPFUL |
| meld input resolution keypath | done | codex | none | none | `context_compass/tasks/completed/2026-02-13_meld_input_resolution_keypath_task.md` | 2026-02-13 | HELPFUL |
| meld contract defaults caching | blocked_out_of_scope | codex | user de-scoped this area for now | none | `context_compass/tasks/completed/2026-02-13_meld_contract_defaults_caching_task.md` | 2026-02-13 | HELPFUL |
| mutation research runtime wiring | blocked_out_of_scope | codex | user de-scoped this area for now | none | `context_compass/stories/2026-02-13_mutation_research_runtime_wiring_story.md` | 2026-02-13 | HELPFUL |
| resolution style matrix source of truth | closed | codex | none | none | `context_compass/stories/completed/2026-02-13_resolution_style_matrix_source_of_truth_story_completed.md` | 2026-02-13 | HELPFUL |
| spellstate advanced flag producers | closed | codex | none | none | `context_compass/stories/completed/2026-02-13_spellstate_advanced_flag_producers_story_completed.md` | 2026-02-13 | HELPFUL |
| revalidate src_architecture document | closed | codex | none | none | `context_compass/epics/2026-02-13_revalidate_src_architecture_document_epic.md` | 2026-02-13 | HELPFUL |
| revalidate src_components document | closed | codex | none | none | `context_compass/epics/2026-02-13_revalidate_src_components_document_epic.md` | 2026-02-13 | HELPFUL |

