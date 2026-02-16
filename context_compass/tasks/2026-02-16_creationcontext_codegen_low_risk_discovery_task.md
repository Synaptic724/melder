# Task: CreationContext Codegen Low-Risk Discovery Lane

## Metadata
- Task ID: TASK-2026-02-16-creationcontext-codegen-low-risk-discovery
- Story: STORY-2026-02-16-deep-creation-context-codegen-strategy-discovery
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Identify low-risk, contract-safe efficiency candidates inside
`creation_context_codegen.py` that can be implemented in compact slices.

## Scope Boundaries
- In scope:
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
- Source emission assembly costs and deterministic key/allocation paths.
- Out of scope:
- Runtime semantics changes in `creation_context.py`.
- Public API or call-shape changes.

## Steps / Checklist
- [x] Build a low-risk candidate matrix (at least 3 items) with estimated upside.
- [x] Attach evidence pointers for each candidate and classify expected blast radius.
- [x] Define user-decision guardrails (`DECISION_REQUEST` triggers) per candidate before implementation.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Low-risk candidate matrix with:
  - candidate description,
  - expected gain vector,
  - risk rationale,
  - validation scope.

## Candidate Backlog (Initial Fill)
| Candidate ID | Proposal | Evidence | Expected Upside |
|---|---|---|---|
| CC-L1 | Replace route-key if/elif selector chains with small precomputed dispatch maps for template lookup. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:185-283 | Low but measurable reduction in branch overhead on route selection doors; cleaner maintenance. |
| CC-L2 | Share one internal compile+exec helper between overrides-only and no-overrides-only template compilation paths. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-358 | Low compile-path allocation reduction and reduced duplicate failure-path code. |
| CC-L3 | Reduce emitted-source assembly allocations by reusing static header/footer fragments and minimizing repeated indentation work. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:372-420, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:851-871 | Low compile-time object churn reduction during template source assembly. |
| CC-L4 | Precompute `source_name` format fragments for compile paths to reduce repeated string formatting churn. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:305-341 | Low reduction in compile-miss string allocation overhead. |
| CC-L5 | Prebind route-key specific template selectors in tiny dicts keyed by `(route, fast_flag)` to remove duplicate branch ladders in hooks/no-hooks lanes. | src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:185-283 | Low runtime dispatch simplification with minimal behavior risk. |

Execution order:
1. CC-L1
2. CC-L2
3. CC-L3
4. CC-L4
5. CC-L5

## Ops Reference (Reuse)
1. Pre-test: unit + fast cprofile x2 + overrides cprofile x2.
2. Implement one candidate only.
3. Post-test: same cadence.
4. Compare against retained checkpoint.
5. If any validation fails or delta is non-winning, publish `RESULT: DECISION_REQUEST` and wait for user keep/revert direction.
6. Publish `RESULT: RETAINED` or `RESULT: REVERTED` with artifact path.

## Code-Line Evidence (Initial)
`src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:203-211`
```python
if resolve_route_key == "existing_creation":
    return _TEMPLATE_EXISTING_INSTANCE_OVERRIDES_ONLY
if resolve_route_key == "many":
    return _TEMPLATE_MANY_INSTANCE_OVERRIDES_ONLY
```

`src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:312-317`
```python
exec(
    compile(source, source_name, "exec"),
    {},
    local_namespace,
)
```

`src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-880`
```python
_TEMPLATE_EXISTING_OVERRIDES_ONLY = (
    _compile_creation_context_overrides_only_template(
        resolve_route_key="existing_creation",
        return_created=True,
    )
)
```

## Files / Paths Impacted
- `context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md`
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py` (CC-L1 reverted earlier; CC-L2 compile helper dedupe now applied)

## Validation
- Executed:
  - `$env:PYTHONPATH='src'; python -m pytest tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py -q` -> pass (17 passed, 3 warnings).
  - `$env:PYTHONPATH='src'; python -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` -> pass (run twice).
  - `$env:PYTHONPATH='src'; python -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` -> pass (run twice).
  - `python -m pytest tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py -q` -> pass after CC-L2 patch (17 passed, 3 warnings).
  - `python benchmarks/testing_other_di/run_snapshot_timings.py --iterations 1000 --warmup-iters 100 --snapshot-label wave3_creationcontext_cc_l2_posttest_2026-02-16 --baseline-json benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_snapshot_process_baseline_2026-02-16_snapshot_2026-02-16_12-16-23.json` -> pass.
  - `python benchmarks/testing_other_di/run_snapshot_timings.py --iterations 10000 --warmup-iters 200 --snapshot-label wave3_creationcontext_cc_l2_posttest_10k_2026-02-16 --baseline-json benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_snapshot_process_10k_2026-02-16_snapshot_2026-02-16_12-16-31.json` -> pass.
- Artifacts:
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_prebaseline_2026-02-16.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_prebaseline_summary_2026-02-16.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_posttest_2026-02-16.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_posttest_summary_2026-02-16.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_postrevert_2026-02-16.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_postrevert_summary_2026-02-16.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l2_posttest_2026-02-16_snapshot_2026-02-16_12-26-35.json`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l2_posttest_2026-02-16_snapshot_summary_2026-02-16_12-26-35.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l2_posttest_10k_2026-02-16_snapshot_2026-02-16_12-26-53.json`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l2_posttest_10k_2026-02-16_snapshot_summary_2026-02-16_12-26-53.txt`

## Risks / Rollback Notes
- Risk: low-risk label can hide behavior-coupled assumptions.
- Mitigation: require concrete source evidence and keep UNKNOWN discipline.
- Rollback: if implemented candidate is non-winning, raise `DECISION_REQUEST` per story gate and wait for user keep/revert direction.

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
  CLAIM: Opened low-risk discovery lane for CreationContext codegen so iterations can pull compact, contract-safe candidates from a pre-scoped queue.
  EVIDENCE: context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:1-123
  IMPACT: Eliminates ad-hoc search churn and keeps iteration entry deterministic.
  NEXT: Populate candidate matrix with at least 3 low-risk options and evidence pointers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Initial low-risk candidate backlog is populated with three compact options focused on selector dispatch, compile helper deduplication, and source assembly allocation trimming.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:185-283, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-358, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:372-420
  IMPACT: Low-risk lane is now immediately executable without additional discovery passes.
  NEXT: Execute CC-L1 first under the story benchmark gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: User approved one compact low-risk CreationContext iteration; this tranche selects candidate `CC-L1` (route-key selector dispatch maps) for implementation-first validation.
  EVIDENCE: context_compass/tasks/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:38-46, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:185-283
  IMPACT: Active execution scope is now one bounded code patch plus full pre/post benchmark cadence.
  NEXT: Capture pre-test baseline cadence, patch `CC-L1`, then run post-test and publish `RESULT` or `RESULT: DECISION_REQUEST`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: CC-L1 pre-test baseline cadence completed (unit + fast x2 + overrides x2) and baseline summary artifact recorded for comparison.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_prebaseline_2026-02-16.txt:1-1942, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_prebaseline_summary_2026-02-16.txt:1-23
  IMPACT: Baseline checkpoint for this iteration is fixed and post-test deltas are directly comparable.
  NEXT: Run post-test cadence after CC-L1 selector-dispatch patch and compute checkpoint deltas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: CC-L1 post-test cadence passed all commands and produced mixed deltas: improved several overrides lanes vs prebaseline but regressed fast `wide` and remained non-winning versus the retained checkpoint on multiple fast lanes.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_posttest_2026-02-16.txt:1-14, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_posttest_summary_2026-02-16.txt:1-32, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_retained_baseline_checkpoint_2026-02-16.txt:1-20
  IMPACT: Candidate is not a clear retained winner under epic gate criteria because checkpoint regressions remain (for example fast `wide`: +6.602 ms, +5.98%).
  NEXT: Raise `RESULT: DECISION_REQUEST` for user keep/revert direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION_REQUEST
  CLAIM: RESULT: DECISION_REQUEST - CC-L1 has green tests but non-winning checkpoint deltas; user keep/revert decision is required before any state change.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_posttest_summary_2026-02-16.txt:24-32, context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:132-147
  IMPACT: Execution is intentionally paused to preserve user-directed policy (no autonomous rollback on non-win).
  NEXT: User selects one:
    1) keep CC-L1 and continue to next low-risk candidate,
    2) revert CC-L1 and run the one-pass post-revert validation cadence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: RESULT: REVERTED - User directed revert of CC-L1; selector-dispatch map changes were removed from `creation_context_codegen.py`.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:195-283, context_compass/tasks/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:162-171
  IMPACT: Runtime returns to pre-CC-L1 code shape and this candidate is closed as reverted.
  NEXT: Run one-pass post-revert validation and record artifact before proceeding to the next process improvement track.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Post-revert validation cadence completed successfully (unit + fast x1 + overrides x1) and artifacts were captured.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_postrevert_2026-02-16.txt:1-9, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l1_postrevert_summary_2026-02-16.txt:1-26
  IMPACT: Revert is now validated and execution can move to benchmark-process improvements.
  NEXT: Open and route a dedicated benchmark snapshot-process task (separate from cProfile) with high-repeat averaging (1000 default, 10000 optional).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Active execution for benchmark process improvements has moved to `TASK-2026-02-16-codegen-snapshot-average-process` so this low-risk code lane can pause while we establish averaged pre/post snapshots.
  EVIDENCE: context_compass/tasks/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:188-193, context_compass/tasks/2026-02-16_codegen_snapshot_average_process_task.md:1-102, context_compass/attention_board.md:16-28
  IMPACT: Subsequent codegen keep/revert decisions can use stable averaged snapshots (including 10000-run optional mode) instead of single-run variance.
  NEXT: Implement and validate the new snapshot runner, then resume this lane with averaged pre/post comparisons.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Resuming this low-risk lane on candidate `CC-L2` (compile+exec helper dedupe) with the averaged snapshot process as the mandatory pre/post gate.
  EVIDENCE: context_compass/tasks/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md:39-46, benchmarks/testing_other_di/run_snapshot_timings.py:240-342, benchmarks/testing_other_di/run_snapshot_timings.py:592-682
  IMPACT: Next candidate evaluation will use stable averaged metrics instead of cProfile single-run variance while keeping the same fast/override lane coverage.
  NEXT: Record one evidence note for CC-L2 duplication pattern, then apply compact code patch and run pre/post averaged snapshots.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: `creation_context_codegen.py` duplicates the same compile+exec pattern in two neighboring template-compile functions, making CC-L2 a compact refactor with low behavior risk.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-324, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:329-367
  IMPACT: A shared internal helper can remove duplicated compile/error plumbing while preserving emitted-source logic and runtime behavior.
  NEXT: Implement a single `_compile_template_from_source(...)` helper and route both compile functions through it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: CC-L2 is implemented: both compile entrypoints now route through a shared `_compile_creation_context_template_source(...)` helper that keeps identical compile/exec error semantics while removing duplicate plumbing.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-320, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:323-357, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:360-390
  IMPACT: Compile-path maintenance cost is lower and behavior stays aligned across overrides-only and no-overrides-only template compilation.
  NEXT: Run unit + averaged snapshot post-test cadence against prebaseline artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Post-test validation is green for CC-L2: CreationContext unit suite passed and averaged snapshots show improved fast-lane aggregate mean with mixed per-lane deltas.
  EVIDENCE: tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:1-30, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l2_posttest_2026-02-16_snapshot_summary_2026-02-16_12-26-35.txt:1-52, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l2_posttest_10k_2026-02-16_snapshot_summary_2026-02-16_12-26-53.txt:1-52
  IMPACT: 10k comparison shows fast-cycle aggregate improvement (-2.60%), combined mean improvement (-2.37%), but a small fast `wide` regression (+0.68%) and an overrides `solo` regression (+10.68% on very small absolute time).
  NEXT: Raise `RESULT: DECISION_REQUEST` for explicit keep/revert direction before proceeding to CC-L3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION_REQUEST
  CLAIM: RESULT: DECISION_REQUEST - CC-L2 delivers non-overrides aggregate gains on averaged 10k snapshots but includes small mixed regressions in specific lanes; explicit user keep/revert direction is required.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l2_posttest_10k_2026-02-16_snapshot_summary_2026-02-16_12-26-53.txt:42-52, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l2_posttest_2026-02-16_snapshot_summary_2026-02-16_12-26-35.txt:42-52
  IMPACT: Execution pauses at decision gate per ticket policy, avoiding autonomous retain/revert on mixed outcomes.
  NEXT: User chooses one:
    1) keep CC-L2 and proceed to CC-L3,
    2) revert CC-L2 and record post-revert snapshot.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Clean rerun (after external benchmark contention stopped) confirms CC-L2 non-overrides gains on all fast cycle graphs versus 10k baseline; overrides lane remains mixed but `solo` is now improved (negative delta), indicating the earlier `solo` regression was unstable.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l2_posttest_10k_rerun_clean_2026-02-16_snapshot_summary_2026-02-16_12-32-46.txt:42-52, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_creationcontext_cc_l2_posttest_10k_2026-02-16_snapshot_summary_2026-02-16_12-26-53.txt:42-52
  IMPACT: Decision quality improves: fast non-overrides direction is consistently favorable, while override-lane variance is concentrated in tiny absolute-time lanes.
  NEXT: Keep `DECISION_REQUEST` state and ask user keep/revert using this clean rerun as primary evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the low-risk lane in the CreationContext discovery queue. It
should produce implementation-ready candidates that preserve current contracts
and use the existing benchmark decision gate (`DECISION_REQUEST` on non-winning/failing outcomes) if code changes are attempted. Current state: `CC-L2` is implemented and validated with averaged snapshots; waiting on explicit keep/revert direction.
