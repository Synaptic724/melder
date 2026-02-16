# Epic: Optimize CreationContext and Phase12 Codegen Runtime

## Metadata
- Epic ID: EPIC-2026-02-15-creationcontext-phase12-codegen-optimization
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-16
- Target Window: 2026-Q1
- Related Program/Initiative: Runtime Performance and Hot-Path Efficiency

## Problem / Opportunity
`CreationContext` and `Phase12` codegen runtime paths already received prior
optimization passes, but we need a fresh, current-head optimization tranche to
reduce hot-path overhead further while preserving behavioral contracts.

## MRP Alignment (Most Reasonable Product)
The MRP is a measurable, contract-safe optimization tranche:
- Revalidate current hotspots first.
- Optimize only the top-ranked, evidence-backed paths.
- Preserve runtime correctness and API behavior.
- Publish before/after validation evidence.

## Goals (Outcomes)
- Refresh hotspot inventory for current-head `CreationContext` and `Phase12` codegen paths.
- Implement ranked optimizations for the highest-impact runtime paths.
- Preserve override precedence, reuse semantics, and gate/validity behavior.
- Produce targeted pytest and benchmark evidence for each optimization slice.

## Non-Goals (Explicit Exclusions)
- Public API redesign for meld/spellbook.
- Broad refactors outside `CreationContext` and `Phase12` codegen surfaces.
- Performance claims without measurable evidence.

## Scope Boundaries
- In scope:
- `CreationContext` runtime specialization/cache/hot-lane behavior.
- `Phase12` emitted-source/runtime helper hot paths.
- Targeted benchmark and test evidence updates tied to optimization slices.
- Out of scope:
- Unrelated spellbook/conduit architecture changes.
- Non-runtime documentation overhauls.

## Success Metrics
- At least one current-head hotspot inventory note with ranked candidates.
- At least two optimization tasks completed with green targeted validation.
- Benchmark evidence showing neutral-or-better runtime impact for touched lanes.

## Requirements (Functional + Non-Functional)
- Functional:
  - Define and execute a ranked optimization queue for `CreationContext` and `Phase12`.
  - Capture explicit keep/remove/defer decisions for each candidate.
- Non-functional:
  - Maintain contract parity and deterministic behavior.
  - Preserve test readability and traceable evidence pointers.
  - Keep changes small and reviewable by lane.

## Constraints / Assumptions
- Constraints:
  - Existing runtime contracts (override precedence, existing-instance guards, and validation gates) must remain unchanged unless explicitly approved.
  - Optimization claims require measured evidence.
- Assumptions:
  - Prior February optimization work provides a baseline but not a full stop for further gains on current head.

## Dependencies / External References
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
- `context_compass/tasks/archive/2026-02-13_discovery_creation_context_codegen_task.md`
- `context_compass/tasks/completed/2026-02-13_discovery_phase12_codegen_task.md`
- `context_compass/tasks/archive/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md`

## Milestones (Track Progress)
- [x] Milestone 1: Current-head hotspot inventory refreshed and ranked.
- [x] Milestone 2: Rank-1 optimization lane implemented and validated.
- [ ] Milestone 3: Rank-2 optimization lane implemented and validated.
- [ ] Milestone 4: Benchmark + regression summary published with acceptance review.

## Stories (Required to Complete)
- [x] Story: STORY-2026-02-15-creationcontext-phase12-codegen-discovery-refresh - Revalidate and rank current-head hotspots (including meld `cProfile` on `test_shallow_all` Melder fast graphs: `solo,shallow,wide,diamond`).
- [ ] Story: STORY-2026-02-15-creationcontext-codegen-runtime-tightening - Implement ranked `CreationContext` runtime optimizations.
- [x] Story: STORY-2026-02-15-phase12-codegen-runtime-tightening - Implement ranked `Phase12` runtime/helper optimizations.
- [ ] Story: STORY-2026-02-15-creationcontext-phase12-benchmark-regression-validation - Validate performance and contract compatibility.
- [ ] Story: STORY-2026-02-16-deep-creation-context-codegen-strategy-discovery - Deep generator strategy discovery for `creation_context_codegen.py`.
- [ ] Story: STORY-2026-02-16-deep-phase12-no-overrides-codegen-strategy-discovery - Deep generator strategy discovery for `phase12_no_overrides_executor.py`.
- [ ] Story: STORY-2026-02-16-deep-phase12-overrides-codegen-strategy-discovery - Deep generator strategy discovery for `phase12_overrides_executor.py`.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-02-15-creationcontext-phase12-codegen-discovery-refresh.
- [ ] Task: Complete story STORY-2026-02-15-creationcontext-codegen-runtime-tightening.
- [x] Task: Complete story STORY-2026-02-15-phase12-codegen-runtime-tightening.
- [ ] Task: Complete story STORY-2026-02-15-creationcontext-phase12-benchmark-regression-validation.
- [ ] Task: Verify Ticket Microcycle enforcement across active stories/tasks.
- [ ] Task: Complete story STORY-2026-02-16-deep-creation-context-codegen-strategy-discovery.
- [ ] Task: Complete story STORY-2026-02-16-deep-phase12-no-overrides-codegen-strategy-discovery.
- [ ] Task: Complete story STORY-2026-02-16-deep-phase12-overrides-codegen-strategy-discovery.
- [x] Task: Turn in `TASK-2026-02-16-creationcontext-codegen-medium-risk-discovery`.
- [x] Task: Turn in `TASK-2026-02-16-phase12-no-overrides-medium-risk-discovery`.
- [x] Task: Turn in `TASK-2026-02-16-phase12-overrides-medium-risk-discovery`.

## Acceptance Criteria (Epic Done)
- Discovery refresh produces ranked, evidence-backed candidate list.
- Implemented optimizations keep runtime contracts stable and tests green.
- Benchmark/report artifacts are attached and reviewed with user.
- User confirms acceptance criteria for closure.

## Risks / Mitigations
- Risk: hot-path tweaks regress override/runtime correctness.
  Mitigation: preserve and extend targeted contract tests before/after each slice.
- Risk: optimizing stale hotspots wastes effort.
  Mitigation: run discovery refresh first and rank by current-head evidence.
- Risk: scope creep into unrelated performance lanes.
  Mitigation: keep scope limited to `CreationContext` + `Phase12` codegen paths.

## Validation / Test Approach
- Discovery validation through source evidence notes and ranked matrix.
- Implementation validation via targeted pytest suites for creation context and
  phase12 blueprint/runtime behavior.
- Benchmark validation via route-matrix or equivalent current-head performance
  harness output.

## Benchmark Gate (Mandatory For Optimization Slices)
- Every optimization slice under this epic must follow:
  - Pre-test baseline cadence (before edit):
    - targeted unit suite(s) for touched module,
    - `benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py` run twice sequentially,
    - `benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py` run twice sequentially.
  - Post-test cadence (after edit): rerun the same suites.
  - Delta comparison against retained checkpoint:
    - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_retained_baseline_checkpoint_2026-02-16.txt`
- Decision rule:
  - If any validation command fails, raise `DECISION_REQUEST` and wait for user keep/revert direction.
  - If candidate delta is non-winning versus retained checkpoint, raise `DECISION_REQUEST` and wait for user keep/revert direction.
  - Emit `RESULT: DECISION_REQUEST` with failing/non-winning evidence and explicit keep/revert options before any state change.
  - If user selects revert, run one full post-revert validation pass and emit a validation artifact.
- Keep rule:
  - Retain only candidates that are validation-green, checkpoint-winning per lane criteria, and explicitly approved by user direction.
- Announcement rule:
  - Every optimization slice must publish one explicit outcome note in the active task/story:
    - `RESULT: DECISION_REQUEST` + reason + evidence + keep/revert options,
    - `RESULT: RETAINED` + median deltas + artifact path, or
    - `RESULT: REVERTED` + reason + artifact path.

## Rollout / Adoption Plan
- Run discovery refresh first.
- Execute rank-1 and rank-2 slices in separate reviewable tasks.
- Consolidate benchmark/regression evidence.
- Close epic after user acceptance.

## Open Questions
- Which current-head lane dominates warm runtime cost after previous February optimizations?
- Which helper/caching paths remain highest ROI without contract risk?
- Do any benchmark harness updates need repair before trustworthy deltas?

## Decision Log
- 2026-02-15: Epic created per user direction to start a new optimization lane focused on `CreationContext` and `Phase12` codegen runtime behavior.
- 2026-02-15: User directed discovery to use `test_shallow_all` and prioritize meld-targeted `cProfile` evidence for hotspot ranking.

## Notes
- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Per user direction, all medium-risk discovery tickets were turned in and marked done (`creationcontext`, `phase12-no-overrides`, `phase12-overrides`), and epic task checkboxes were updated for those ticket IDs.
  EVIDENCE: context_compass/tasks/2026-02-16_creationcontext_codegen_medium_risk_discovery_task.md:1-132, context_compass/tasks/2026-02-16_phase12_no_overrides_medium_risk_discovery_task.md:1-90, context_compass/tasks/2026-02-16_phase12_overrides_medium_risk_discovery_task.md:1-99, context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:103-114
  IMPACT: Epic tracking now reflects medium-ticket turn-in completion while deep stories remain open for remaining low/high execution work.
  NEXT: Continue execution from high-risk queue.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: Opened the first implementation story (`STORY-2026-02-15-phase12-codegen-runtime-tightening`) and wave-1 task to move from profiling into hotspot-led runtime optimization.
  EVIDENCE: context_compass/stories/2026-02-15_phase12_codegen_runtime_tightening_story.md:1-82, context_compass/tasks/completed/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md:1-79
  IMPACT: Epic execution has entered implementation mode with a scoped, measurable optimization lane.
  NEXT: Route attention board to the wave-1 optimization task and implement the first patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Prior discovery and optimization artifacts already provide concrete baseline signals for this new epic: creation-context override preprocessing/caching costs and phase12 helper/runtime callpath tightening are evidenced and validated in prior lanes.
  EVIDENCE: context_compass/tasks/archive/2026-02-13_discovery_creation_context_codegen_task.md:4-4, context_compass/tasks/archive/2026-02-13_discovery_creation_context_codegen_task.md:90-90, context_compass/tasks/completed/2026-02-13_discovery_phase12_codegen_task.md:202-203, context_compass/tasks/archive/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:6-6, context_compass/tasks/archive/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:130-131
  IMPACT: We can start with a focused refresh/ranking pass instead of broad speculative repo scans.
  NEXT: Create discovery-refresh story/task and route active execution to it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: `test_shallow_all` already exposes Melder-only runtime hooks where root and spellspace calls route through `conduit.meld(...)`, making it a valid harness for meld-focused profiling.
  EVIDENCE: benchmarks/testing_other_di/test_shallow_all.py:1076-1158, benchmarks/testing_other_di/test_shallow_all.py:1127-1141, benchmarks/testing_other_di/test_shallow_all.py:1602-1630
  IMPACT: We can produce meld-targeted `cProfile` evidence without inventing a new benchmark harness.
  NEXT: Create and execute a discovery task that captures and ranks meld hotpath profiles from `test_shallow_all` (Melder/shallow).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: Initial profiling scope is restricted to the first `test_shallow_all` lane (`test_single_resolve_smoke` + `test_single_resolve_timings`) and explicitly excludes long-running threaded stress tests.
  EVIDENCE: benchmarks/testing_other_di/test_shallow_all.py:1583-1630, benchmarks/testing_other_di/test_shallow_all.py:1702-1888
  IMPACT: Profiling iterations stay fast and targeted to meld hotpaths, reducing noise from stress-harness overhead.
  NEXT: Run meld-focused `cProfile` capture on the first-test lane only (`melder` + `shallow`) and rank hotspots.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: User narrowed profiling to melder-only fast graph combinations from the first lane (`solo`, `shallow`, `wide`, `diamond`), excluding `deep`.
  EVIDENCE: benchmarks/testing_other_di/test_shallow_all.py:598-607, benchmarks/testing_other_di/test_shallow_all.py:616-632, benchmarks/testing_other_di/test_shallow_all.py:1583-1630
  IMPACT: Discovery scope is now explicit for fast-iteration cProfile runs and avoids slow-graph distortion.
  NEXT: Create and run a dedicated melder fast-graph cProfile pytest suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Three finished in-progress tasks were closed and moved to `tasks/completed` (`profile_meld_hotpath_with_test_shallow_all`, `profile_melder_overrides_graph_callchain`, `optimize_phase12_creationcontext_codegen_wave1`).
  EVIDENCE: context_compass/tasks/completed/2026-02-15_profile_meld_hotpath_with_test_shallow_all_task.md:1-20, context_compass/tasks/completed/2026-02-15_profile_melder_overrides_graph_callchain_task.md:1-20, context_compass/tasks/completed/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md:1-20
  IMPACT: Epic active scope is now narrowed to story-level closure and next-wave routing decisions.
  NEXT: Review remaining in-progress stories and either close them or open a new implementation wave task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Closed and moved two finished in-progress stories to `stories/completed` (`creationcontext_phase12_codegen_discovery_refresh`, `phase12_codegen_runtime_tightening`), while keeping the epic open.
  EVIDENCE: context_compass/stories/completed/2026-02-15_creationcontext_phase12_codegen_discovery_refresh_story.md:1-20, context_compass/stories/completed/2026-02-15_phase12_codegen_runtime_tightening_story.md:1-20, context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:88-92
  IMPACT: Epic stays active because required story lanes for creationcontext runtime tightening and benchmark/regression validation remain open.
  NEXT: Decide whether to open the remaining required stories/tasks now or de-scope epic acceptance criteria.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Opened three new deep discovery stories (one per codegen module) to investigate unconsidered generator-level strategy opportunities.
  EVIDENCE: context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:1-36, context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md:1-36, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:1-36
  IMPACT: Epic scope now includes deeper codegen-strategy discovery lanes beyond wave-1 runtime micro-slices.
  NEXT: Drive option ranking and experiment planning in these three stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Enforced a mandatory benchmark gate for all optimization slices under this epic: pre-test baseline, post-test comparison, and `DECISION_REQUEST` escalation on failing tests or non-winning deltas.
  EVIDENCE: context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:132-147, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_retained_baseline_checkpoint_2026-02-16.txt:1-20
  IMPACT: Keeps future codegen optimization work aligned with the same benchmark cadence while moving keep/revert decisions to explicit user direction.
  NEXT: Apply this gate in every new implementation task opened under the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: User-direction policy is encoded into active optimization tickets: failures/non-winning deltas now require `RESULT: DECISION_REQUEST` and explicit user keep/revert direction before any rollback/retain action.
  EVIDENCE: context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:131-141, context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:80-90, context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md:80-90, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:81-91, context_compass/tasks/2026-02-16_phase12_overrides_high_risk_segmented_shape_helpers_slice2_task.md:61-72
  IMPACT: Autonomous keep/revert decisions are removed from active codegen optimization execution flow.
  NEXT: For the next post-test outcome, publish `RESULT: DECISION_REQUEST` when failure/non-win is detected and pause for user decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Optimization epic remains active after closing three tasks to
`tasks/completed` and two stories to `stories/completed`. Remaining required
lanes are creationcontext runtime tightening and benchmark/regression
validation, plus newly opened deep generator-strategy discovery stories for the
three core codegen modules.

