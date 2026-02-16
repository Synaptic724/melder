# Task: Phase12 Overrides High-Risk Segmented Shape Helpers (Slice 1)

## Metadata
- Task ID: TASK-2026-02-16-phase12-overrides-high-risk-segmented-shape-helpers-slice1
- Story: STORY-2026-02-16-deep-phase12-overrides-codegen-strategy-discovery
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Execute one high-risk OV-H1 iteration by segmenting shape-generated override
step bodies into helper call sites to test compile-payload and runtime effects
under the standard benchmark keep/revert gate.

## Scope Boundaries
- In scope:
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- Shape-source generation only (`_build_phase12_overrides_executor_shape_source` lane).
- Out of scope:
- Public API changes.
- No-overrides emitter changes.
- CreationContext external contract changes.

## Steps / Checklist
- [x] Capture pre-test baseline (unit + fast/overrides benchmark cadence).
- [x] Implement OV-H1 slice: segment generated shape steps into helper call sites.
- [x] Run post-test cadence and compare against retained checkpoint.
- [x] Raise `DECISION_REQUEST` on failing/non-winning outcomes; run post-revert validation only if user selects revert.
- [x] Publish explicit outcome note (`RESULT: RETAINED` or `RESULT: REVERTED`) with artifact path.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- One high-risk implementation slice for OV-H1.
- Benchmark artifacts and decision record (user-directed keep/revert).
- Notes documenting measured outcome and next candidate decision.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
- `benchmarks/testing_other_di/profiles/overrides_graphs_melder/`

## Validation
- Completed for this slice.
- Commands run:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (twice prebaseline, once post-revert)
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (twice prebaseline, once post-revert)
- Artifacts:
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_phase12_overrides_highrisk_ovh1_slice1_prebaseline_2026-02-16.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_phase12_overrides_highrisk_ovh1_slice1_posttest_2026-02-16.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_phase12_overrides_highrisk_ovh1_slice1_postrevert_2026-02-16.txt`

## Benchmark Gate (Mandatory)
- Pre-test baseline (before any code edit):
  - Run required unit + benchmark cadence listed above.
  - Capture medians and write baseline artifact/delta context against:
    - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_retained_baseline_checkpoint_2026-02-16.txt`
- Post-test (after candidate edit):
  - Re-run the same unit + benchmark cadence.
  - Emit candidate delta artifact under:
    - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/`
- Decision gate (non-negotiable):
  - If unit or benchmark command fails, raise `DECISION_REQUEST` and wait for user keep/revert direction.
  - If measured delta is non-winning versus retained checkpoint, raise `DECISION_REQUEST` and wait for user keep/revert direction.
  - Emit `RESULT: DECISION_REQUEST` with failure/non-winning evidence and explicit keep/revert options before any state change.
  - If user selects revert, run one full post-revert validation pass:
    - unit suite once, fast cprofile once, overrides cprofile once.
  - Emit post-revert validation artifact and explicit result-announce note
    (`RESULT: REVERTED` + reason + artifact path).
- Retain gate:
  - Retain only candidates that pass validation and satisfy checkpoint criteria.
  - Emit explicit result-announce note
    (`RESULT: RETAINED` + median deltas + artifact path).

## Risks / Rollback Notes
- Risk: helper segmentation may reduce runtime locality and regress fast lanes.
- Mitigation: keep this as one compact slice with strict `DECISION_REQUEST` escalation criteria.
- Rollback: non-winning deltas require `DECISION_REQUEST`; execute revert only on user decision.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: User directed execution order from high risk to low risk; OV-H1 selected as first implementation candidate in overrides lane.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_high_risk_discovery_task.md:34-54, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:267-271
  IMPACT: Iteration sequence is now explicitly high-risk-first for current run.
  NEXT: Run pre-test baseline cadence before code edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: OV-H1 pre-test baseline cadence is complete; unit suite and both fast/overrides cprofile suites passed twice for benchmark baseline capture.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_phase12_overrides_highrisk_ovh1_slice1_prebaseline_2026-02-16.txt:1-1460
  IMPACT: Baseline evidence is now locked for post-test checkpoint comparison and keep/revert gating.
  NEXT: Implement one compact OV-H1 segmentation slice in `phase12_overrides_executor.py`, then run full post-test cadence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Compact OV-H1 slice will segment shape no-override fast-path bodies into helper call sites by routing `use_no_override_fast_path` construction through existing no-overrides constructor helper.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1827-1841, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1908-1921, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1974-1987, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2032-2045, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2091-2104, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:919-979
  IMPACT: This reduces emitted source duplication for no-override shape lanes while preserving no-overrides construction semantics via one shared helper path.
  NEXT: Patch `phase12_overrides_executor.py`, run unit + benchmark post-test cadence, then apply keep/revert gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Post-test gate failed immediately on unit suite; emitted shape-source no longer preserved direct callable invoke text contract expected by unit assertions.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_phase12_overrides_highrisk_ovh1_slice1_posttest_2026-02-16.txt:4-68
  IMPACT: Candidate cannot proceed to benchmark comparison and must be reverted per mandatory gate.
  NEXT: Revert candidate code path and run required post-revert validation pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: RESULT: REVERTED - OV-H1 slice 1 was reverted after post-test unit failure; post-revert validation pass completed successfully.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_phase12_overrides_highrisk_ovh1_slice1_posttest_2026-02-16.txt:4-68, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_phase12_overrides_highrisk_ovh1_slice1_postrevert_2026-02-16.txt:1-986
  IMPACT: Runtime code is restored to pre-slice behavior and this OV-H1 attempt is closed as non-retained.
  NEXT: Open OV-H1 slice 2 with narrower helper segmentation that preserves existing emitted-shape test contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
OV-H1 slice 1 executed under the full gate and was reverted after a post-test
unit failure before benchmark comparison. Prebaseline and post-revert artifacts
are captured, and the runtime file was restored to pre-slice behavior. Next
step is opening a narrower OV-H1 follow-on slice that keeps shape-source unit
expectations intact while still testing helper segmentation.
