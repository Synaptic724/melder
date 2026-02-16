# Task: Phase12 Overrides Cold-Path Helper Extraction (Compact Slice 1)

## Metadata
- Task ID: TASK-2026-02-16-phase12-overrides-cold-path-helper-extraction
- Story: STORY-2026-02-16-deep-phase12-overrides-codegen-strategy-discovery
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Implement one compact optimization slice that reduces generated override executor
source size by extracting cold/error-heavy invoke/kwargs branches to shared
helpers while preserving inline fast paths and existing runtime contracts.

## Scope Boundaries
- In scope:
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- Generated-source helpers around kwargs/invoke/error-heavy lanes.
- Targeted unit tests for overrides executor generation/behavior.
- Out of scope:
- No-overrides emitter changes.
- Public API changes.
- Multi-lane refactors beyond the selected compact slice.

## Steps / Checklist
- [x] Capture pre-test baseline (unit + fast/overrides benchmark cadence).
- [x] Implement compact cold/error-path extraction in override shape emitter.
- [x] Run post-test cadence and compare median deltas vs retained checkpoint.
- [x] If validation fails or delta is non-winning, revert immediately and run post-revert validation pass.
- [x] Publish explicit outcome note (`RESULT: RETAINED` or `RESULT: REVERTED`) with artifact path.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- One compact code change slice for rank-1 strategy.
- Benchmark artifact(s) and delta report under
  `benchmarks/testing_other_di/profiles/overrides_graphs_melder/`.
- Ticket notes with explicit keep/revert outcome announcement.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
- `benchmarks/testing_other_di/profiles/overrides_graphs_melder/`

## Validation
- Executed:
  - Unit suite: `tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py` passed in pre/post/post-revert runs.
  - Benchmark cadence:
    - pre-test: fast cprofile x2, overrides cprofile x2.
    - post-test: fast cprofile x2, overrides cprofile x2.
    - post-revert: fast cprofile x1, overrides cprofile x1.
- Commands used:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (run twice sequentially)
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (run twice sequentially)
- Artifacts:
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave2_phase12_overrides_coldpath_slice1_prebaseline_2026-02-16.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave2_phase12_overrides_coldpath_slice1_prebaseline_summary_2026-02-16.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave2_phase12_overrides_coldpath_slice1_posttest_2026-02-16.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave2_phase12_overrides_coldpath_slice1_posttest_summary_2026-02-16.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave2_phase12_overrides_coldpath_slice1_postrevert_validation_2026-02-16.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave2_phase12_overrides_coldpath_slice1_postrevert_summary_2026-02-16.txt`
- Comparison checkpoint:
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_retained_baseline_checkpoint_2026-02-16.txt`

## Benchmark Gate (Mandatory)
- Pre-test baseline (before any code edit):
  - Run the required unit + benchmark cadence listed above.
  - Capture medians and write baseline artifact/delta context against:
    - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_retained_baseline_checkpoint_2026-02-16.txt`
- Post-test (after candidate edit):
  - Re-run the same unit + benchmark cadence.
  - Emit a candidate delta artifact under:
    - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/`
- Revert gate (non-negotiable):
  - If unit or benchmark command fails, revert candidate immediately.
  - If measured delta is non-winning versus retained checkpoint, revert candidate immediately.
  - After revert, run one full post-revert validation pass:
    - unit suite once, fast cprofile once, overrides cprofile once.
  - Emit post-revert validation artifact and explicit result-announce note
    (`RESULT: REVERTED` + reason + artifact path).
- Retain gate:
  - Retain only candidates that pass validation and satisfy checkpoint comparison criteria.
  - Emit explicit result-announce note
    (`RESULT: RETAINED` + median deltas + artifact path).

## Risks / Rollback Notes
- Risk: helper extraction can accidentally shift hot-path behavior.
- Mitigation: keep inline fast path logic intact and move only cold/error branches.
- Rollback: immediate revert if validation fails or non-winning deltas are observed.

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
  TYPE: PLAN
  CLAIM: First implementation slice from the deep overrides strategy ranking targets cold/error-path extraction while preserving inline fast paths and benchmark keep/revert discipline.
  EVIDENCE: context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:87-108, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:172-188
  IMPACT: Starts implementation with the highest-priority low-risk compact lane and explicit rollback constraints.
  NEXT: Run pre-test baseline cadence and capture artifact before editing code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Pre-test baseline cadence completed and medians were recorded against the retained checkpoint before code edits.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave2_phase12_overrides_coldpath_slice1_prebaseline_summary_2026-02-16.txt:1-25
  IMPACT: Candidate evaluation started with explicit baseline context and checkpoint deltas.
  NEXT: Run post-test cadence after candidate edit and evaluate keep/revert outcome.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Post-test checkpoint comparison was non-winning, with major fast-lane regression (`fast_timings_shallow` +13.375ms, +12.79%) despite mixed override-lane deltas.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave2_phase12_overrides_coldpath_slice1_posttest_summary_2026-02-16.txt:1-25
  IMPACT: Candidate violates keep criteria and cannot be retained.
  NEXT: Revert candidate immediately and run required post-revert validation pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: RESULT: REVERTED - rank-1 cold-path helper extraction candidate was reverted due non-winning checkpoint deltas.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave2_phase12_overrides_coldpath_slice1_posttest_summary_2026-02-16.txt:1-25, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1572-1610, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:790-794
  IMPACT: Runtime source is restored to pre-candidate behavior and the slice is recorded as rejected.
  NEXT: Capture post-revert validation artifact and announce final revert result in story notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Post-revert validation pass completed (unit once + fast cprofile once + overrides cprofile once) and artifact recorded.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave2_phase12_overrides_coldpath_slice1_postrevert_summary_2026-02-16.txt:1-25, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave2_phase12_overrides_coldpath_slice1_postrevert_validation_2026-02-16.txt:1-1932
  IMPACT: Revert gate requirements are fully satisfied and the task has an auditable outcome trail.
  NEXT: Select the next compact candidate (same rank with narrower scope, or rank-2 metadata caching).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Compact implementation task opened from the deep overrides strategy story.
Rank-1 candidate was executed, benchmarked, and reverted as non-winning.
Pre/post/post-revert artifacts are recorded. Next action is choosing the next
compact candidate lane under the same benchmark gate.
