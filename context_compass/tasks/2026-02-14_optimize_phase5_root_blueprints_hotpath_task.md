# Task: Optimize Phase5 Root Blueprints Baseline Hotpath

## Metadata
- Task ID: TASK-2026-02-14-optimize-phase5-root-blueprints-hotpath
- Story: STORY-2026-02-14-phase-testing-optimization-backlog
- Status: review
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce conduit-wide phase5 root-blueprints cost while preserving foundational
5-7 semantics.

## Scope Boundaries
- In scope:
- Target phase5 root-blueprints computation and attachment path.
- Preserve phase6/7 validation/change-control behavior.
- Out of scope:
- Changing conduit validity gating semantics.
- Local 5-7 flow redesign.

## Steps / Checklist
- [x] Profile root-blueprints internals and identify high-cost loops.
- [x] Implement low-risk reductions in repeated snapshot/attachment work.
- [x] Add/update tests that prove phase5 behavior remains unchanged.
- [x] Validate via component harness rerun for conduit 5-7 cold/warm variants.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Optimized phase5 root-blueprints path.
- Updated conduit 5-7 measurements with before/after comparison.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py`

## Validation
- `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/system/test_spell_system_root_blueprint_builder.py` -> `27 passed`; output captured in `context_compass/artifacts/2026-02-14_phase5_opt_builder_unit_tests_rerun_clean.txt`.
- `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k "run_phase_root_blueprints"` -> `9 passed, 134 deselected`; output captured in `context_compass/artifacts/2026-02-14_phase5_opt_spell_crafter_unit_tests_rerun_clean.txt`.
- `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` (clean run 1) -> `1 passed, 3 warnings`; output captured in `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output.txt`.
- `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` (clean run 2) -> `1 passed, 3 warnings`; output captured in `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt`.

## Risks / Rollback Notes
- Risk: phase5 refactors could break downstream phase6/7 assumptions.
- Rollback: revert phase5 changes and keep existing foundational flow.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Phase-testing routing docs are now synchronized to clean phase5 rerun evidence (story, epic, and attention board all reference rerun-clean artifacts).
  EVIDENCE: context_compass/stories/2026-02-14_phase_testing_optimization_backlog_story.md:73-73, context_compass/epics/2026-02-14_phase_testing_epic.md:128-128, context_compass/attention_board.md:29-29
  IMPACT: Re-entry pointers now direct future iterations to uncontested measurements instead of contested prior runs.
  NEXT: Share rerun outcomes with the user and request acceptance/next-wave direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Keep only the first rank-3 optimization (remove traversal-time dependency sorting); do not keep the later sorted-dependency cache experiment.
  EVIDENCE: src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:37-37, src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:149-233
  IMPACT: Current code state is simplified and deterministic, avoiding extra cache state while preserving the phase5 micro-optimization that survived validation.
  NEXT: Treat earlier ticket note about a builder-local sorted-dependency cache as historical/superseded and base review on current source state plus clean reruns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Clean harness rerun #2 passed and, combined with rerun #1, shows phase5 warm timings below the pre-rank3 anchor (`group_5_7_total_ms`: `4.465/4.648` vs `4.797/4.827`; `phase_root_blueprints_ms`: `3.991/4.169` vs `4.281/4.256`), with expected run-to-run noise.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output.txt:4-4, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output.txt:59-59, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:4-4, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:59-59, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output.txt:4-4, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run2.txt:4-4
  IMPACT: Revalidation request is satisfied with uncontested data; phase5 rank-3 slice remains non-regressing with modest warm-path improvement.
  NEXT: Update validation bullets and story/epic/board pointers to these clean artifacts, then return task to `review`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Clean harness rerun #1 passed and reported conduit phase5 timings at `group_5_7_total_ms=4.425/4.465` with `phase_root_blueprints_ms=3.895/3.991` (cold/warm).
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output.txt:3-3, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output.txt:4-4, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output.txt:59-59
  IMPACT: Provides first uncontested post-contamination performance sample for rank-3 phase5 state.
  NEXT: Run clean harness rerun #2 and compare spread before finalizing review evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Clean rerun validation passed for focused phase5 spell-crafter coverage (`run_phase_root_blueprints`: `9 passed, 134 deselected`).
  EVIDENCE: context_compass/artifacts/2026-02-14_phase5_opt_spell_crafter_unit_tests_rerun_clean.txt:12-12
  IMPACT: Confirms root-blueprint execution behavior remains stable in spell-crafter orchestration paths for the current rank-3 code state.
  NEXT: Run two uncontested component harness passes and compare `group_5_7_total_ms` / `phase_root_blueprints_ms` against prior anchors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Clean rerun validation passed for focused root-blueprint-builder unit suite (`27 passed`), replacing prior potentially contested results.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase5_opt_builder_unit_tests_rerun_clean.txt:12-12
  IMPACT: Confirms the kept rank-3 code state is functionally stable at the builder-unit boundary under uncontested execution.
  NEXT: Run the focused `run_phase_root_blueprints` spell-crafter unit suite and append evidence before harness reruns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conduit-wide 5-7 runs are consistently dominated by phase5 root-blueprints time in both cold and warm variants.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:7-8, src/melder/spellbook/spell_crafter/spell_crafter.py:2980-3245
  IMPACT: This task is ranked third as a targeted foundational optimization candidate with clear phase attribution.
  NEXT: Instrument phase5 internals to isolate dominant sub-steps before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Phase5 blueprint compilation repeatedly invokes `_build_single_root_dag` for roots and per-spell fallbacks, and each DAG build currently sorts dependency ids during reachability discovery even though final node/edge ordering is already stabilized by later sorted passes.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:3-4, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:7-8, src/melder/spellbook/spell_crafter/spell_crafter.py:3008-3110, src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:39-89, src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:90-149, src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:150-233
  IMPACT: Sorting in the inner reachability walk is a low-risk candidate for removal because it appears redundant relative to downstream deterministic ordering and may reduce repeated Phase5 traversal overhead.
  NEXT: Implement a deterministic-safe fastpath in `_build_single_root_dag` that removes redundant dependency sorting in traversal and validate unchanged behavior with focused tests and harness runs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Implemented rank-3 slice by removing redundant per-node dependency sorting in `_build_single_root_dag` reachability traversal while preserving deterministic output via existing sorted node/edge materialization passes.
  EVIDENCE: src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:150-235
  IMPACT: Reduces inner-loop overhead across repeated phase5 DAG builds without changing blueprint contracts.
  NEXT: Validate with focused root-blueprint/phase5 unit tests and harness reruns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: [SUPERSEDED BY CLEAN RERUNS] Initial validation pass showed non-regression with directional warm improvement, but these measurements were later treated as potentially contested.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase5_opt_builder_unit_tests.txt:12-12, context_compass/artifacts/2026-02-14_phase5_opt_spell_crafter_unit_tests.txt:12-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output.txt:4-4, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run2.txt:4-4, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_output.txt:4-4, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_output_run2.txt:4-4
  IMPACT: Kept only as historical trace; clean reruns now provide authoritative measurement evidence.
  NEXT: Use clean rerun artifacts for acceptance and performance comparison.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Phase5 still performs repeated dependency sorting inside `_build_single_root_dag` edge materialization for every root/per-spell blueprint build call, and `run_phase_root_blueprints` invokes both root-map and per-spell fallback blueprint builds in one pass.
  EVIDENCE: src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:39-89, src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:90-149, src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:150-235, src/melder/spellbook/spell_crafter/spell_crafter.py:3008-3110
  IMPACT: A builder-local sorted-dependency cache can remove repeated sorts across blueprint builds without changing DAG semantics.
  NEXT: Add builder-local sorted dependency cache keyed by dependency-map identity and route both root-map and fallback builds through the cache, then rerun validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: [SUPERSEDED: REVERTED] A second rank-3 cache iteration was prototyped but is not present in the current source state.
  EVIDENCE: src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:37-37, src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:149-233
  IMPACT: Historical note only; final delivered implementation keeps only traversal-sort removal.
  NEXT: Refer to current code evidence and clean rerun notes for acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Validation measurements taken during the prior pass may be contaminated because user and agent tests were running concurrently.
  EVIDENCE: user instruction in session (2026-02-14): "sorry I ran tests at the same time as you please rerun yours"
  IMPACT: All optimization claims from that pass must be revalidated with clean reruns.
  NEXT: Re-run focused phase5 unit tests and harness outputs with uncontested execution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Rank-3 phase5 optimization slice is implemented with one kept code change:
remove dependency sorting inside `_build_single_root_dag` traversal while
preserving downstream deterministic ordering. Clean reruns were executed in
uncontested conditions (`phase5_opt_builder_unit_tests_rerun_clean`,
`phase5_opt_spell_crafter_unit_tests_rerun_clean`, and two clean harness
outputs). Warm conduit 5-7 timings remain below the pre-rank3 anchor with
expected run-to-run noise. Task is in review pending user acceptance.
