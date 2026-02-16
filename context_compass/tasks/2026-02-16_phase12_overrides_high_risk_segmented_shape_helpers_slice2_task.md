# Task: Phase12 Overrides High-Risk Segmented Shape Helpers (Slice 2)

## Metadata
- Task ID: TASK-2026-02-16-phase12-overrides-high-risk-segmented-shape-helpers-slice2
- Story: STORY-2026-02-16-deep-phase12-overrides-codegen-strategy-discovery
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Execute a narrowed OV-H1 follow-on slice by segmenting static owner-creations
resolution blocks into helper call sites while preserving shape-source callable
invoke text contracts that failed in slice 1.

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
- [ ] Implement OV-H1 slice 2: segment owner-creations shape blocks into helper call sites.
- [ ] Run post-test cadence and compare against retained checkpoint.
- [ ] Raise `DECISION_REQUEST` on failing/non-winning outcomes; run post-revert validation only if user selects revert.
- [ ] Publish explicit outcome note (`RESULT: RETAINED` or `RESULT: REVERTED`) with artifact path.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- One narrowed high-risk implementation slice for OV-H1.
- Benchmark artifacts and decision record (user-directed keep/revert).
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
- Decision gate (non-negotiable):
  - If unit or benchmark command fails, raise `DECISION_REQUEST` and wait for user keep/revert direction.
  - If measured delta is non-winning versus retained checkpoint, raise `DECISION_REQUEST` and wait for user keep/revert direction.
  - Emit `RESULT: DECISION_REQUEST` with failure/non-winning evidence and explicit keep/revert options before any state change.
  - If user selects revert, run one full post-revert validation pass:
    - unit suite once, fast cprofile once, overrides cprofile once.
  - Emit post-revert validation artifact and explicit result-announce note
    (`RESULT: REVERTED` + reason + artifact path).
- Retain gate:
  - Retain only candidates that pass validation, satisfy checkpoint criteria, and have explicit user keep direction.
  - Emit explicit result-announce note
    (`RESULT: RETAINED` + median deltas + artifact path).

## Risks / Rollback Notes
- Risk: helper extraction can add extra runtime dispatch in hot shape lanes.
- Mitigation: constrain this slice to owner-target block segmentation only.
- Rollback: execute revert only when user selects revert after a `DECISION_REQUEST` note.

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
  CLAIM: Slice 1 reverted due unit failure in shape-source callable invoke contract; slice 2 narrows segmentation target to avoid changing emitted callable invoke blocks.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_high_risk_segmented_shape_helpers_slice1_task.md:121-137
  IMPACT: Follow-on high-risk iteration remains active but constrained to a safer sub-surface of OV-H1.
  NEXT: Capture fresh pre-test baseline for slice 2 before code edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Slice 2 pre-test baseline cadence completed successfully (unit + fast cprofile x2 + overrides cprofile x2).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_phase12_overrides_highrisk_ovh1_slice2_prebaseline_2026-02-16.txt:1-1954
  IMPACT: Baseline is ready for post-test delta comparison under the mandatory decision gate (`DECISION_REQUEST` on failing/non-winning outcomes).
  NEXT: Implement narrowed owner-target helper segmentation in `phase12_overrides_executor.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Ticket policy is updated to raise `DECISION_REQUEST` on failing/non-winning outcomes instead of autonomous revert/retain decisions.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_high_risk_segmented_shape_helpers_slice2_task.md:61-72, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:80-91, context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:131-141
  IMPACT: Post-test failures/non-winning deltas now pause execution for user keep/revert direction before any rollback action.
  NEXT: If slice-2 post-test fails or loses checkpoint, publish `RESULT: DECISION_REQUEST` and wait for user decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the second OV-H1 high-risk slice. It keeps the same benchmark
decision gate (`DECISION_REQUEST` before keep/revert actions) while narrowing helper segmentation scope to owner-target
resolution blocks so prior shape-source callable-invoke text contracts remain
unchanged. Prebaseline cadence is complete and artifacted, so the next step is
the narrowed code patch followed by post-test decision-request execution.
