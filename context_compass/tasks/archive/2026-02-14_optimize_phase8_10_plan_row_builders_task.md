Completed: 2026-02-14
Summary: Accepted in the phase-testing closure pass; implementation and validation artifacts are captured in this task.

# Task: Optimize Phase8-10 Plan Row Builder Hotpath

## Metadata
- Task ID: TASK-2026-02-14-optimize-phase8-10-plan-row-builders
- Story: STORY-2026-02-14-phase-testing-optimization-backlog
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce warm-path cumulative cost across phase8/9/10 plan-row construction and
supporting path-materialization work.

## Scope Boundaries
- In scope:
- Optimize occurrence/injection/patch map row-building helpers used in warm 8-11.
- Preserve phase ordering, semantics, and emitted plan behavior.
- Out of scope:
- Major planner architecture rewrites.
- Execution-plan API changes.

## Steps / Checklist
- [x] Identify dominant row-build/path-format allocations on warm 8-11 path.
- [x] Implement low-risk reductions in repeated path formatting/sorting work.
- [x] Run focused tests for behavior parity.
- [x] Validate by rerunning component harness and comparing warm per-phase totals.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Optimized phase8/9/10 row builder paths.
- Updated measurement notes showing warm-path improvement.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- `src/melder/spellbook/spell_crafter/dag/dag_index.py`

## Validation
- `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k "capture_phase8_11_codegen_ir_exports_sorted_payloads or capture_phase8_11_codegen_ir_signature_stable_across_map_insertion_orders or capture_phase8_11_codegen_ir_signature_changes_on_enriched_payload_semantics or build_phase11_variant_ir_payload_signature_changes_on_variant_label or build_phase11_variant_ir_payload_signature_changes_on_step_semantic_change"` -> `4 passed, 139 deselected`.
- `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` (run 1) -> `1 passed, 3 warnings`; output captured in `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output.txt`.
- `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` (run 2) -> `1 passed, 3 warnings`; output captured in `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run2.txt`.
- `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/dag/test_dag_index.py` (run 1) -> `1 failed, 1 error, 34 passed`; output captured in `context_compass/artifacts/2026-02-14_path_registry_format_cache_dag_index_pytests.txt` (expected first-pass test patching issue, fixed next run).
- `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/dag/test_dag_index.py` (run 2) -> `35 passed`; output captured in `context_compass/artifacts/2026-02-14_path_registry_format_cache_dag_index_pytests_run2.txt`.
- `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k "capture_phase8_11_codegen_ir_exports_sorted_payloads or capture_phase8_11_codegen_ir_signature_stable_across_map_insertion_orders or capture_phase8_11_codegen_ir_signature_changes_on_enriched_payload_semantics or build_phase11_variant_ir_payload_signature_changes_on_variant_label or build_phase11_variant_ir_payload_signature_changes_on_step_semantic_change"` (run 2) -> `4 passed, 147 deselected`; output captured in `context_compass/artifacts/2026-02-14_phase8_10_opt_focused_unit_tests_run2.txt`.
- `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` (run 3) -> `1 passed, 3 warnings`; output captured in `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt`.

## Risks / Rollback Notes
- Risk: changing row-build internals can alter ordering-sensitive outputs.
- Rollback: revert helper-level changes and keep current ordering contracts.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed
## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Parent routing docs are now synchronized with the latest rank-2 follow-up measurements so compaction re-entry points to the improved warm-path evidence and updated closure direction.
  EVIDENCE: context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:71-78, context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md:145-151, context_compass/epics/completed/2026-02-14_phase_testing_epic.md:126-133, context_compass/epics/completed/2026-02-14_phase_testing_epic.md:264-269, context_compass/attention_board.md:19-19, context_compass/attention_board.md:27-31
  IMPACT: Phase-testing tickets/board now preserve the latest measured state without requiring re-derivation after compaction.
  NEXT: Walk the updated rank1/rank2/rank3 outcomes with the user and confirm closure/move direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: PathRegistry format-path memoization pass reduced warm patch-map overhead in latest harness rerun: `group_8_11_total_ms` improved `9.804 -> 9.085`, `phase_patch_maps_ms` improved `1.288 -> 0.573`, total function calls dropped `120524 -> 108778`, and patch-map helper cumulative costs dropped (`build_override_patch_map` `0.006 -> 0.004`, `_get_path_spec_key` `0.005 -> 0.002`).
  EVIDENCE: src/melder/spellbook/spell_crafter/dag/dag_index.py:36-46, src/melder/spellbook/spell_crafter/dag/dag_index.py:182-191, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run8.txt:7-27, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:7-34
  IMPACT: Rank-2 phase8-10 lane now has measurable warm-path improvement on the targeted patch-map slice after the follow-up pass.
  NEXT: Keep task in review and walk closure direction with user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Dag-index validation now passes after switching the new cache test to class-level monkeypatch compatible with `PathRegistry.__slots__`.
  EVIDENCE: tests/unit/melder/spellbook/spell_crafter/dag/test_dag_index.py:37-50, context_compass/artifacts/2026-02-14_path_registry_format_cache_dag_index_pytests.txt:3-109, context_compass/artifacts/2026-02-14_path_registry_format_cache_dag_index_pytests_run2.txt:12-12
  IMPACT: Cache behavior regression coverage is now stable and compaction-safe.
  NEXT: Preserve the class-level patching pattern for slotted runtime classes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: First validation pass for the new `PathRegistry.format_path` cache test failed because `PathRegistry` uses `__slots__`, so instance-level monkeypatch of `materialize_path` is read-only.
  EVIDENCE: context_compass/artifacts/2026-02-14_path_registry_format_cache_dag_index_pytests.txt:3-109, tests/unit/melder/spellbook/spell_crafter/dag/test_dag_index.py:37-45
  IMPACT: Test needs class-level monkeypatch strategy to validate cache behavior without mutating a slotted instance attribute.
  NEXT: Update the test to monkeypatch `PathRegistry.materialize_path` on the class and rerun dag-index tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: After the phase11 tuple-hash update, warm 8-11 still spends meaningful cumulative time in patch-map key/row work (`build_override_patch_map`, `_get_path_spec_key`, `_build_override_target_rows`) with repeated `format_path/materialize_path` calls.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run8.txt:7-36, src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:636-681, src/melder/spellbook/spell_crafter/spell_crafter.py:1497-1553, src/melder/spellbook/spell_crafter/dag/dag_index.py:154-183
  IMPACT: Rank-2 row-builder lane still has a measurable hot slice worth one more scoped optimization pass.
  NEXT: Add `PathRegistry.format_path` memoization and rerun focused phase-crafter tests plus component harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Warm 8-11 totals still show substantial cost in occurrence/injection/patch phases, and cProfile highlights row-build/path-materialization helpers as recurring cumulative contributors.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:11-11, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:26-29, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:41-47, src/melder/spellbook/spell_crafter/spell_crafter.py:3405-3521
  IMPACT: This task is ranked second as a medium-risk, broad-impact warm-path optimization slice.
  NEXT: Profile helper-level allocations for path formatting and sorting inside phase8-10 row-build paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Rank-2 hotspot focus is confirmed: `_build_override_target_rows` is the top helper-level contributor under 8-11 capture, and repeated `format_path/materialize_path` plus per-helper sorting are still active cost centers in the same trace.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:30-30, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:45-48, src/melder/spellbook/spell_crafter/spell_crafter.py:1201-1247, src/melder/spellbook/spell_crafter/spell_crafter.py:1390-1501, src/melder/spellbook/spell_crafter/spell_crafter.py:1502-1573, src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:634-672, src/melder/spellbook/spell_crafter/dag/dag_index.py:154-183
  IMPACT: A low-risk optimization can target path formatting memoization and duplicate grouping work in phase10 while preserving patch-map semantics.
  NEXT: Implement one scoped reduction in path-format churn and grouped-target rebuilds, then rerun focused tests and harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: PLAN
  CLAIM: Implement scoped Phase10 reductions first: add PatchMapBuilder-local `param_path_id -> formatted_path` memoization reused across override+mutation map builds, reuse one grouped mutation patch build for `*name` and `**name`, and skip list sorting in row builders when list size is `< 2`.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:634-713, src/melder/spellbook/spell_crafter/spell_crafter.py:1201-1247, src/melder/spellbook/spell_crafter/spell_crafter.py:1390-1501, src/melder/spellbook/spell_crafter/spell_crafter.py:1502-1573
  IMPACT: Targets measured helper costs without changing phase contracts or public APIs.
  NEXT: Apply code edits in `patch_maps.py` and `spell_crafter.py`, then run focused unit tests and harness regression.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Implemented scoped rank-2 changes: PatchMapBuilder now memoizes formatted path keys and reuses grouped mutation patch generation once per param-name group, and phase8/9/10 IR row helpers now skip sort calls when row lists have fewer than two entries.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:636-659, src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:660-697, src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:698-741, src/melder/spellbook/spell_crafter/spell_crafter.py:1201-1247, src/melder/spellbook/spell_crafter/spell_crafter.py:1248-1279, src/melder/spellbook/spell_crafter/spell_crafter.py:1388-1499, src/melder/spellbook/spell_crafter/spell_crafter.py:1500-1572, src/melder/spellbook/spell_crafter/spell_crafter.py:1573-1628
  IMPACT: Reduces repeated path-materialization and redundant sort overhead in the measured helper region without changing output schemas.
  NEXT: Run focused tests covering patch-map/plan semantics, then rerun component harness and compare warm 8-11 outputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Focused tests passed and harness reruns show no behavioral regressions with mixed warm-path performance movement: post-rank2 run-1 `group_8_11_total_ms=27.932` and run-2 `group_8_11_total_ms=25.438` versus rank1 anchor `27.829`; warm cProfile sample moved from `0.083s` (rank1) to `0.081s`/`0.080s`.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase8_10_opt_focused_unit_tests.txt:1-1, context_compass/artifacts/2026-02-14_phase8_10_opt_focused_unit_tests.txt:12-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_opt_output.txt:12-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_opt_output.txt:15-15, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output.txt:7-7, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output.txt:9-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run2.txt:7-7, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run2.txt:9-9
  IMPACT: Changes are validated and safe, but absolute warm-total gain is noisy at this sample size; decision point is whether to keep this slice as-is or continue tuning rank-2.
  NEXT: Move task to review and request user acceptance direction (keep vs iterate) before rank-3 execution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Rank-2 optimization slice is implemented and now includes a follow-up
`PathRegistry.format_path` cache pass with fresh measurements. Latest warm run
shows improved patch-map cost and lower total calls (`group_8_11_total_ms`
`9.804 -> 9.085`, `phase_patch_maps_ms` `1.288 -> 0.573`, calls
`120524 -> 108778`). Task remains in review pending user closure direction.
