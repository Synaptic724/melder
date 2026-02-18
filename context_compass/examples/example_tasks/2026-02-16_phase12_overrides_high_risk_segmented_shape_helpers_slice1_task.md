

# Task: Phase12 Overrides High-Risk Segmented Shape Helpers (Slice 1)

## Metadata
- Task ID: TASK-2026-02-16-phase12-overrides-high-risk-segmented-shape-helpers-slice1
- Story: STORY-2026-02-16-deep-phase12-overrides-codegen-strategy-discovery
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16T12:24:07Z
- Retention Role: example_kept_3_per_folder
- Retained At: 2026-02-16T12:24:07Z
- Retention Scope: kept_as_example_after_archive_completed_cleanup

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
- [ ] Implement OV-H1 slice: segment generated shape steps into helper call sites.
- [ ] Run post-test cadence and compare against retained checkpoint.
- [ ] Revert immediately if failing or non-winning; run post-revert validation pass.
- [ ] Publish explicit outcome note (`RESULT: RETAINED` or `RESULT: REVERTED`) with artifact path.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- One high-risk implementation slice for OV-H1.
- Benchmark artifacts and keep/revert decision record.
- Notes documenting measured outcome and next candidate decision.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
- `benchmarks/testing_other_di/profiles/overrides_graphs_melder/`

## Validation
- Not run yet.
- Required commands:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (twice)
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (twice)

## Benchmark Gate (Mandatory)
- Pre-test baseline (before any code edit):
  - Run required unit + benchmark cadence listed above.
  - Capture medians and write baseline artifact/delta context against:
    - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_retained_baseline_checkpoint_2026-02-16.txt`
- Post-test (after candidate edit):
  - Re-run the same unit + benchmark cadence.
  - Emit candidate delta artifact under:
    - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/`
- Revert gate (non-negotiable):
  - If unit or benchmark command fails, revert candidate immediately.
  - If measured delta is non-winning versus retained checkpoint, revert candidate immediately.
  - After revert, run one full post-revert validation pass:
    - unit suite once, fast cprofile once, overrides cprofile once.
  - Emit post-revert validation artifact and explicit result-announce note
    (`RESULT: REVERTED` + reason + artifact path).
- Retain gate:
  - Retain only candidates that pass validation and satisfy checkpoint criteria.
  - Emit explicit result-announce note
    (`RESULT: RETAINED` + median deltas + artifact path).

## Risks / Rollback Notes
- Risk: helper segmentation may reduce runtime locality and regress fast lanes.
- Mitigation: keep this as one compact slice with strict revert criteria.
- Rollback: mandatory immediate revert on non-winning deltas.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
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

## Context / Handoff Summary
This task is the first high-risk implementation iteration in the overrides
queue (OV-H1). It must execute under the standard benchmark keep/revert gate
and produce an explicit retained/reverted result.



