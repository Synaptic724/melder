# Task: Phase12 Overrides Low-Risk Discovery Lane

## Metadata
- Task ID: TASK-2026-02-16-phase12-overrides-low-risk-discovery
- Story: STORY-2026-02-16-deep-phase12-overrides-codegen-strategy-discovery
- Status: blocked
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-17

## Objective
Identify low-risk override codegen candidates that can improve efficiency while
preserving existing override precedence and runtime contracts.

## Scope Boundaries
- In scope:
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- Compile-prep and generated-source micro-structure candidates.
- Out of scope:
- Public API shape changes.
- High-blast-radius architecture rewrites.

## Steps / Checklist
- [x] Produce at least 3 low-risk candidates with source-backed evidence.
- [x] Define expected benchmark direction and rollback criteria per candidate.
- [x] Rank candidates by effort, risk, and estimated payoff.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Low-risk override-candidate matrix with implementation boundaries.

## Candidate Backlog (Initial Fill)
| Candidate ID | Proposal | Evidence | Expected Upside |
|---|---|---|---|
| OV-L1 | In shape metadata build, prefer row-exported static flags and skip spell object attribute probing when row fields are already present. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:609-748 | Low compile-prep attribute-read reduction. |
| OV-L2 | Hoist `required_fields` tuple outside per-row hydration in `_hydrate_steps_from_rows(...)` to avoid per-iteration tuple recreation. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2397-2441 | Low compile-prep allocation reduction. |
| OV-L3 | Add fast-empty short-circuit in `_build_step_override_targets(...)` when `override_targets_by_spell_id` is empty. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2516-2587 | Low branch/loop overhead reduction for no-target plans. |
| OV-L4 | Deduplicate repeated root-positional override merge emission blocks in kwargs source generator to shrink generated source size. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:983-1308 | Low compile-size reduction with minimal runtime risk. |
| OV-L5 | Avoid unnecessary contract payload tuple/dict conversions when `has_contract_payload` is false in row-to-step metadata paths. | src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:609-748, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2397-2486 | Low compile-prep allocation reduction. |

Execution order:
1. OV-L2
2. OV-L1
3. OV-L3
4. OV-L4
5. OV-L5

## Ops Reference (Reuse)
1. Pre-test benchmark cadence (unit + fast x2 + overrides x2).
2. Implement one low-risk candidate only.
3. Post-test same cadence + compare checkpoint.
4. Revert immediately on non-winning/failing outcome.
5. Record `RESULT` note with artifact path before next candidate.

## Files / Paths Impacted
- `context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py` (discovery evidence only unless approved for implementation)

## Validation
- Not run.
- If implementation is attempted, enforce story benchmark gate.
- Recommended commands:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (twice)
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (twice)

## Risks / Rollback Notes
- Risk: even low-risk edits can regress fast lanes.
- Mitigation: keep compact and benchmark-gated with checkpoint comparisons.
- Rollback: raise `DECISION_REQUEST` on non-winning/failing deltas; revert only on user decision.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-17
  TYPE: DECISION
  CLAIM: User clarified that benchmark tooling code must not change; `spellspace` exclusion is reporting-only for assistant summaries and does not modify `run_codegen_benchmark_deltas.py`.
  EVIDENCE: benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:770-790, benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1125-1147
  IMPACT: Route-matrix script behavior remains unchanged; future reported split breakdowns from this agent will omit spellspace values.
  NEXT: Continue OV-L3 discussion with reported lanes limited to `warm_root`, `override_args`, `override_targeted`, and `mixed`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: DECISION
  CLAIM: User directed that `spellspace` must be removed from benchmark route calculations going forward; active work shifts from OV-L3 keep/revert gating to benchmark route-matrix policy update.
  EVIDENCE: benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:760-790, benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1125-1147
  IMPACT: Route baseline pass/fail decisions and printed split-lane summaries must stop using `warm_spellspace`.
  NEXT: Patch `run_codegen_benchmark_deltas.py` to remove `warm_spellspace` from route matrix sampling, baseline-delta calculations, and summary output; then run one pinned report to validate new output shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Opened low-risk overrides discovery lane to keep a ready list of compact candidates after the first reverted slice.
  EVIDENCE: context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:1-214
  IMPACT: Supports faster retries with clear risk bounds and less re-scoping overhead.
  NEXT: Populate low-risk override matrix and choose first candidate for gated implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Low-risk overrides lane now contains five compact candidates focused on metadata/prep overhead and generated-source-size trimming.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:609-748, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:983-1308, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2397-2587
  IMPACT: Overrides low-risk retries can proceed without additional broad discovery passes.
  NEXT: Execute OV-L2 first and capture checkpoint deltas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: PLAN
  CLAIM: User-directed move-to-next routing is now activating this lane, with OV-L2 selected as the first implementation candidate.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_low_risk_discovery_task.md:43-44, context_compass/tasks/2026-02-16_phase12_overrides_high_risk_discovery_task.md:373-380
  IMPACT: Overrides low-risk queue is the active execution target and no longer parked in `ready`.
  NEXT: Capture OV-L2 prebaseline artifacts (unit + pinned codegen report) before code edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: MEASURE
  CLAIM: OV-L2 prebaseline gate is captured with unit green (`75 passed, 3 warnings`) and pinned codegen benchmark medians (`cold=6725500ns`, `warm=500ns`, `mixed=21300ns`) plus route medians (`warm_root=500ns`, `spellspace=20600ns`, `override_args=2600ns`, `override_targeted=2900ns`, `mixed=19900ns`) with affinity reason `pinned`.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/ov_l2_prebaseline_validation_2026-02-17.txt:1-31, benchmarks/testing_other_di/profiles/baselines/ov_l2_prebaseline_codegen_report_2026-02-17.json:127-149
  IMPACT: OV-L2 now has a locked before-state checkpoint for post-test keep/revert evaluation.
  NEXT: Implement one compact OV-L2 slice, then run post-test unit + pinned codegen benchmark compare against `ov_l2_prebaseline_codegen_report_2026-02-17.json`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: FACT
  CLAIM: Implemented OV-L2 by hoisting `_hydrate_steps_from_rows(...)` `required_fields` tuple outside the per-row loop, removing repeated tuple construction while preserving field-validation behavior.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2437-2456
  IMPACT: Compile-prep hydration now avoids per-row allocation churn for required-field metadata.
  NEXT: Run OV-L2 post-test gate (unit + pinned codegen compare) against `ov_l2_prebaseline_codegen_report_2026-02-17.json`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: MEASURE
  CLAIM: OV-L2 post-test gate is complete with unit green (`75 passed, 3 warnings`) and pinned codegen compare medians (`cold=6726300ns`, `warm=500ns`, `mixed=23200ns`); baseline deltas passed thresholds (`cold_ratio=1.0001`, `warm_ratio=1.0000`, `mixed_ratio=1.0892`) and route baseline deltas also passed (`warm_root=1.0000`, `spellspace=0.9854`, `override_args=0.9615`, `override_targeted=0.9655`, `mixed=1.0352`).
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/ov_l2_posttest_validation_2026-02-17.txt:1-43, benchmarks/testing_other_di/profiles/baselines/ov_l2_posttest_codegen_report_2026-02-17.json:127-199
  IMPACT: OV-L2 is functionally valid and threshold-pass, but speed outcome is mixed because mixed lane regressed versus prebaseline.
  NEXT: Escalate explicit keep/revert decision request before advancing to OV-L1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: DECISION_REQUEST
  CLAIM: RESULT: DECISION_REQUEST - OV-L2 required-fields hoist is functionally valid and benchmark-threshold-pass, but benchmark-non-winning for speed objective due mixed-lane regression (`mixed_ratio=1.0892`); recommended action is revert unless this tradeoff is explicitly accepted.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/ov_l2_posttest_validation_2026-02-17.txt:26-36, benchmarks/testing_other_di/profiles/baselines/ov_l2_posttest_codegen_report_2026-02-17.json:140-143
  IMPACT: Overrides low-risk lane is paused at keep/revert gate before queue advancement.
  NEXT: User chooses keep or revert for OV-L2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: DECISION
  CLAIM: RESULT: REVERTED - user selected explicit revert for OV-L2; required-fields tuple hoist was removed and `_hydrate_steps_from_rows(...)` now recreates `required_fields` inside the row loop.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2438-2455
  IMPACT: OV-L2 non-winning slice is removed and overrides low-risk routing is unblocked.
  NEXT: Continue execution order at OV-L1 prebaseline capture.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: MEASURE
  CLAIM: OV-L2 rollback validation is complete with unit green (`75 passed, 3 warnings`) and pinned baseline-compare medians (`cold=6460600ns`, `warm=500ns`, `mixed=21100ns`) where baseline and route baseline gates both passed (`cold_ratio=0.9606`, `warm_ratio=1.0000`, `mixed_ratio=0.9906`, route ratios <= 1.0).
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/ov_l2_revert_validation_2026-02-17.txt:1-22, benchmarks/testing_other_di/profiles/baselines/ov_l2_postrevert_codegen_report_2026-02-17.json:127-199
  IMPACT: Reverted checkpoint is validated and benchmark-improved versus OV-L2 prebaseline.
  NEXT: Run OV-L1 prebaseline gate (unit + pinned codegen compare report) before any OV-L1 code edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: MEASURE
  CLAIM: OV-L1 prebaseline gate is captured with unit green (`75 passed, 3 warnings`) and pinned codegen benchmark medians (`cold=7806200ns`, `warm=500ns`, `mixed=24300ns`), with aggregate and route gates both passing.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/ov_l1_prebaseline_validation_2026-02-17.txt:1-22, benchmarks/testing_other_di/profiles/baselines/ov_l1_prebaseline_codegen_report_2026-02-17.json:111-220
  IMPACT: OV-L1 now has a locked before-state checkpoint for post-test keep/revert evaluation.
  NEXT: Implement one compact OV-L1 slice and run post-test unit + pinned compare against `ov_l1_prebaseline_codegen_report_2026-02-17.json`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: FACT
  CLAIM: Implemented OV-L1 by preferring row-exported static flags (`is_existing_unique_creation`, `is_callable_spell`, `has_disposal_methods`) in `_build_shape_source_step_metadata(...)` and probing `spell_lookup` only for missing static values.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:694-742, tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py:474-499
  IMPACT: Shape metadata build can skip spell attribute probing when row static metadata is already present.
  NEXT: Run OV-L1 post-test gate (unit + pinned compare) versus `ov_l1_prebaseline_codegen_report_2026-02-17.json`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: MEASURE
  CLAIM: OV-L1 post-test gate is complete with unit green (`76 passed, 3 warnings`) and pinned codegen compare medians (`cold=6730100ns`, `warm=500ns`, `mixed=22600ns`); baseline deltas are aggregate-winning (`cold_ratio=0.8621`, `warm_ratio=1.0000`, `mixed_ratio=0.9300`) and route baseline ratios are also winning/flat (`warm_root=1.0000`, `spellspace=0.9062`, `override_args=0.9259`, `override_targeted=1.0000`, `mixed=0.9858`).
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/ov_l1_posttest_validation_2026-02-17.txt:1-22, benchmarks/testing_other_di/profiles/baselines/ov_l1_posttest_codegen_report_2026-02-17.json:127-199
  IMPACT: OV-L1 currently meets keep criteria under pinned-core benchmark policy.
  NEXT: Escalate explicit keep/revert decision request before advancing to OV-L3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: DECISION_REQUEST
  CLAIM: RESULT: DECISION_REQUEST - OV-L1 row-static-flag precedence slice is functionally valid and benchmark-winning versus prebaseline; recommended action is keep.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/ov_l1_posttest_validation_2026-02-17.txt:15-18, benchmarks/testing_other_di/profiles/baselines/ov_l1_posttest_codegen_report_2026-02-17.json:141-143, benchmarks/testing_other_di/profiles/baselines/ov_l1_posttest_codegen_report_2026-02-17.json:191-195
  IMPACT: Overrides low-risk lane is paused at keep/revert gate before queue advancement.
  NEXT: User chooses keep or revert for OV-L1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: MEASURE
  CLAIM: Additional pinned split-lane rerun confirms OV-L1 wins on separated `fast` and `override` lanes without relying on collective mixed metric (`fast.warm_root=1.0000`, `fast.spellspace=0.9196`, `override.args=0.9630`, `override.targeted=0.9310`).
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/ov_l1_posttest_split_validation_2026-02-17.txt:1-16, benchmarks/testing_other_di/profiles/baselines/ov_l1_posttest_split_codegen_report_2026-02-17.json:166-196
  IMPACT: Decision quality is now backed by explicit fast-vs-override breakdown instead of aggregate-only interpretation.
  NEXT: Hold at OV-L1 keep/revert gate for user decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: DECISION
  CLAIM: RESULT: RETAINED - user approved keep for OV-L1 after split-lane rerun; row-static-flag precedence remains active.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/ov_l1_posttest_split_validation_2026-02-17.txt:6-14, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:694-742
  IMPACT: OV-L1 decision gate is closed and low-risk queue is unblocked.
  NEXT: Continue execution order at OV-L3 prebaseline capture.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: MEASURE
  CLAIM: OV-L3 prebaseline gate is captured with unit green (`76 passed, 3 warnings`) and pinned codegen benchmark medians (`cold=6652800ns`, `warm=500ns`, `mixed=22600ns`) with aggregate and route gates passing.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/ov_l3_prebaseline_validation_2026-02-17.txt:1-22, benchmarks/testing_other_di/profiles/baselines/ov_l3_prebaseline_codegen_report_2026-02-17.json:127-160
  IMPACT: OV-L3 now has a locked before-state checkpoint for post-test keep/revert evaluation.
  NEXT: Implement OV-L3 compact slice and run post-test compare against `ov_l3_prebaseline_codegen_report_2026-02-17.json`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: FACT
  CLAIM: Implemented OV-L3 by adding an early empty-map short-circuit in `_build_step_override_targets(...)`, so empty `override_targets_by_spell_id` returns per-step empty tuples without step/path-metadata probing.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2578-2586, tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py:990-1018
  IMPACT: Compile-time override target preparation avoids unnecessary per-step work for the common empty-target case.
  NEXT: Run OV-L3 post-test gate (unit + pinned compare) versus `ov_l3_prebaseline_codegen_report_2026-02-17.json`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: MEASURE
  CLAIM: OV-L3 post-test gate is unit green (`77 passed, 3 warnings`) with split-lane benchmark variability across three pinned compares: route baseline passed in one run and failed in two runs due `fast.warm_root` (`1.2500`) while `override.args`/`override.targeted` were mostly flat-to-winning (`0.9615-1.0000` / `0.9643-1.0357`) and `fast.spellspace` stayed near flat (`0.9761-1.0335`); cold compile ratios were mildly regressive (`1.0097-1.0225`).
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/ov_l3_posttest_validation_2026-02-17.txt:1-65, benchmarks/testing_other_di/profiles/baselines/ov_l3_posttest_codegen_report_2026-02-17.json:166-197, benchmarks/testing_other_di/profiles/baselines/ov_l3_posttest_split_codegen_report_2026-02-17.json:166-196, benchmarks/testing_other_di/profiles/baselines/ov_l3_posttest_split2_codegen_report_2026-02-17.json:166-197
  IMPACT: OV-L3 has mixed split-lane outcome with route-gate instability concentrated in timer-floor `warm_root` variance.
  NEXT: Escalate keep/revert decision request with split-lane evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-17
  TYPE: DECISION_REQUEST
  CLAIM: RESULT: DECISION_REQUEST - OV-L3 empty-target short-circuit is functionally valid, but split-lane benchmarks are mixed because route baseline failed in 2/3 reruns (driven by `fast.warm_root=1.2500` against a `400ns` baseline floor); recommended action is keep if we treat this warm-root quantization as noise, otherwise revert for strict route-gate adherence.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/ov_l3_posttest_validation_2026-02-17.txt:21-63, benchmarks/testing_other_di/profiles/baselines/ov_l3_posttest_codegen_report_2026-02-17.json:171-183, benchmarks/testing_other_di/profiles/baselines/ov_l3_posttest_split2_codegen_report_2026-02-17.json:171-183
  IMPACT: Overrides low-risk lane is paused at explicit keep/revert gate before advancing to OV-L4.
  NEXT: User chooses keep or revert for OV-L3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the active low-risk lane in the overrides discovery queue.
OV-L2 prebaseline artifacts are captured in
`benchmarks/testing_other_di/profiles/baselines/ov_l2_prebaseline_validation_2026-02-17.txt`
and `benchmarks/testing_other_di/profiles/baselines/ov_l2_prebaseline_codegen_report_2026-02-17.json`.
OV-L2 implementation is complete, post-test artifacts are captured in
`benchmarks/testing_other_di/profiles/baselines/ov_l2_posttest_validation_2026-02-17.txt`
and `benchmarks/testing_other_di/profiles/baselines/ov_l2_posttest_codegen_report_2026-02-17.json`,
then reverted per user decision with rollback validation captured in
`benchmarks/testing_other_di/profiles/baselines/ov_l2_revert_validation_2026-02-17.txt`
and `benchmarks/testing_other_di/profiles/baselines/ov_l2_postrevert_codegen_report_2026-02-17.json`.
OV-L1 prebaseline artifacts are captured in
`benchmarks/testing_other_di/profiles/baselines/ov_l1_prebaseline_validation_2026-02-17.txt`
and `benchmarks/testing_other_di/profiles/baselines/ov_l1_prebaseline_codegen_report_2026-02-17.json`.
OV-L1 implementation now prefers row static flags before spell probing and has
targeted unit coverage for probe bypass behavior.
OV-L1 post-test artifacts are captured in
`benchmarks/testing_other_di/profiles/baselines/ov_l1_posttest_validation_2026-02-17.txt`
and `benchmarks/testing_other_di/profiles/baselines/ov_l1_posttest_codegen_report_2026-02-17.json`.
Additional split-lane rerun artifacts are captured in
`benchmarks/testing_other_di/profiles/baselines/ov_l1_posttest_split_validation_2026-02-17.txt`
and `benchmarks/testing_other_di/profiles/baselines/ov_l1_posttest_split_codegen_report_2026-02-17.json`.
OV-L1 is retained. OV-L3 prebaseline artifacts are captured in
`benchmarks/testing_other_di/profiles/baselines/ov_l3_prebaseline_validation_2026-02-17.txt`
and `benchmarks/testing_other_di/profiles/baselines/ov_l3_prebaseline_codegen_report_2026-02-17.json`.
OV-L3 post-test artifacts are captured in
`benchmarks/testing_other_di/profiles/baselines/ov_l3_posttest_validation_2026-02-17.txt`,
`benchmarks/testing_other_di/profiles/baselines/ov_l3_posttest_codegen_report_2026-02-17.json`,
`benchmarks/testing_other_di/profiles/baselines/ov_l3_posttest_split_codegen_report_2026-02-17.json`,
and `benchmarks/testing_other_di/profiles/baselines/ov_l3_posttest_split2_codegen_report_2026-02-17.json`.
Active execution is now paused at explicit keep/revert decision gate for OV-L3.
