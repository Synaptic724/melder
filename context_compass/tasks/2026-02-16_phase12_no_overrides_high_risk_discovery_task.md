# Task: Phase12 No-Overrides High-Risk Discovery Lane

## Metadata
- Task ID: TASK-2026-02-16-phase12-no-overrides-high-risk-discovery
- Story: STORY-2026-02-16-deep-phase12-no-overrides-codegen-strategy-discovery
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Investigate high-risk/high-reward redesign options for
`phase12_no_overrides_executor.py` that may unlock larger gains but require
stronger controls and explicit decision points.

## Scope Boundaries
- In scope:
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- Large generator architecture alternatives.
- Out of scope:
- Public contract breaks without explicit approval.
- Implementation beyond bounded experiments.

## Steps / Checklist
- [x] Document at least 2 high-risk redesign candidates and their architecture impact.
- [x] Define prerequisite guards (tests, instrumentation, rollback) per candidate.
- [x] Provide recommendation criteria for promotion to implementation.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- High-risk candidate briefs with migration concerns and payoff hypotheses.

## Candidate Backlog (Initial Fill)
| Candidate ID | Proposal | Evidence | Expected Upside |
|---|---|---|---|
| NO-H1 | Replace transient string-generated executor with a vectorized runtime loop over callable and dependency-index arrays (no generated source path). | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1257-1419, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1428-1531 | High compile-time reduction; high runtime model-change risk. |
| NO-H2 | Segment large step-plan emitted executors into chunked helper functions plus dispatcher to cap function size and compile latency. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:469-717 | High win on large plans; higher complexity for exception/diagnostic parity. |
| NO-H3 | Expand transient-unrolled eligibility beyond `Existence.many` by introducing dedicated state carriers for reusable lanes. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:421-435, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:523-717 | Potentially high runtime win; high correctness risk around reuse semantics. |
| NO-H4 | Replace source-string generation with direct code-object/AST construction to cut parser overhead and tighten compile artifacts. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:440-466, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1257-1419 | High compile-latency upside; high implementation and debug complexity. |
| NO-H5 | Introduce optional native fast-path call dispatcher for transient call modes (`CALL0..CALL8`) with Python fallback. | src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1428-1531 | High potential runtime win; high build/distribution risk. |

Execution order:
1. NO-H2
2. NO-H1
3. NO-H4
4. NO-H3
5. NO-H5

## Ops Reference (Reuse)
1. Keep this lane discovery-first; implementation only after explicit decision.
2. If promoted, run full benchmark gate (pre/post + decision-request).
3. Run one candidate per tranche.
4. Record `RESULT` and artifact path in notes before moving to next candidate.

## Files / Paths Impacted
- `context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py` (discovery evidence only unless approved for implementation)

## Validation
- Not run.
- If high-risk experiments are implemented, enforce story benchmark gate and `DECISION_REQUEST` policy.
- Recommended commands:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (twice)
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (twice)

## Risks / Rollback Notes
- Risk: high-risk redesign can destabilize generated executor contracts.
- Mitigation: keep this lane discovery-only until explicit promotion decision.
- Rollback: design-stage only; code-stage uses `DECISION_REQUEST` escalation on failure/non-win.

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
  CLAIM: Opened high-risk no-overrides discovery lane to isolate deep redesign concepts from regular compact optimization loops.
  EVIDENCE: context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md:1-123
  IMPACT: Enables deliberate evaluation of high-upside options without disrupting medium/low iteration cadence.
  NEXT: Build candidate briefs with explicit migration and rollback plans.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: STRATEGY_DISCUSSION
  CLAIM: High-risk no-overrides lane is loaded with five redesign candidates and a conservative execution order that prioritizes segmented generator changes before runtime model replacement.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:421-435, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:469-717, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1257-1531
  IMPACT: High-risk path is now fully documented for future escalation without additional rediscovery.
  NEXT: Keep lane parked until user explicitly promotes high-risk experimentation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: NO-H2 segmented step-plan emission with conditional segmented-only namespace promotion is unit-green (`28 passed`) and improves materially versus the initial NO-H2 attempt, but still regresses fast-lane 15s averages versus baseline.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:50-52, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:450-466, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:486-627, tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py:336-390, benchmarks/testing_other_di/profiles/baselines/no_h2_postfix_validation_2026-02-16.txt:3-32
  IMPACT: Candidate behavior is verified and performance evidence is available for keep/revert gating.
  NEXT: Escalate decision gate with explicit baseline deltas and user direction request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION_REQUEST
  CLAIM: RESULT: DECISION_REQUEST - NO-H2 postfix run is mixed (fast lane +5.233% slower, overrides lane -6.103% faster, combined +4.240% slower vs 15s baseline), so retention is not supported by aggregate signal.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/no_h2_postfix_validation_2026-02-16.txt:13-20, benchmarks/testing_other_di/profiles/baselines/no_h2_postfix_validation_2026-02-16.txt:22-32
  IMPACT: High-risk lane should not auto-retain this slice; branch state needs explicit keep/revert direction.
  NEXT: User chooses keep, revert, or one additional refinement pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Current fast/overrides benchmark graphs do not activate NO-H2 segmented step-plan emission: all observed no-overrides executors are small (`max_steps=2`, `ge16=0`), and overrides payload lanes do not use no-overrides executors in these graphs.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:53-54, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:492-497, benchmarks/testing_other_di/test_shallow_all.py:1126-1141, benchmarks/testing_other_di/test_overrides_all.py:573-577, benchmarks/testing_other_di/profiles/baselines/no_h2_runtime_activation_check_2026-02-16.txt:1-8
  IMPACT: Observed benchmark delta swings are likely dominated by run-to-run timing variance rather than direct segmented-helper runtime effects in these benchmark lanes.
  NEXT: Treat keep/revert decision as benchmark-noise-sensitive and avoid claiming deterministic causal speed gains from NO-H2 in current lane coverage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Additional fast-only 15s rerun remained regressive versus the canonical 15s baseline (`mean sample_avg_ms +6.543%`) and slightly worse than the prior postfix pass (`+1.245%`), with largest regressions still concentrated in timings lanes.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/fast/benchmark_results_15s_2026-02-16.jsonl:1-8, benchmarks/testing_other_di/profiles/baselines/fast/benchmark_results_15s_no_h2_postfix_2026-02-16.jsonl:1-8, benchmarks/testing_other_di/profiles/baselines/fast/benchmark_results_15s_no_h2_postfix_repeat1_2026-02-16.jsonl:1-8, benchmarks/testing_other_di/profiles/baselines/no_h2_fast_extra_run_summary_2026-02-16.txt:1-24
  IMPACT: One more repeat did not produce a baseline-winning fast signal; decision posture remains non-retain under aggregate baseline comparison.
  NEXT: Keep NO-H2 decision gate open for explicit user keep/revert direction or pivot to next candidate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: RESULT: REVERTED - user selected revert for NO-H2 after non-winning fast baseline comparisons; NO-H2 segmented-helper code/test additions were removed and revert validation is green.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/no_h2_postfix_validation_2026-02-16.txt:13-32, benchmarks/testing_other_di/profiles/baselines/no_h2_fast_extra_run_summary_2026-02-16.txt:1-24, benchmarks/testing_other_di/profiles/baselines/no_h2_revert_validation_2026-02-16.txt:1-10
  IMPACT: Branch state is restored to pre-NO-H2 runtime behavior and high-risk lane can advance.
  NEXT: Move to NO-H1 and run 10k prebaseline before edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Benchmark policy for this lane is standardized to 10k before/after comparison runs for decision gates.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/no_h2_revert_validation_2026-02-16.txt:12-15
  IMPACT: Reduces decision churn from short-window variance and keeps gate behavior consistent across upcoming candidates.
  NEXT: Apply the 10k pre/post gate for NO-H1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the high-risk lane for no-overrides strategy discovery. It should
capture deep options and decision criteria before any implementation work.
