# Epic: Optimize CreationContext and Phase12 Codegen Runtime

## Metadata
- Epic ID: EPIC-2026-02-15-creationcontext-phase12-codegen-optimization
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15
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
- [ ] Milestone 1: Current-head hotspot inventory refreshed and ranked.
- [ ] Milestone 2: Rank-1 optimization lane implemented and validated.
- [ ] Milestone 3: Rank-2 optimization lane implemented and validated.
- [ ] Milestone 4: Benchmark + regression summary published with acceptance review.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-15-creationcontext-phase12-codegen-discovery-refresh - Revalidate and rank current-head hotspots (including meld `cProfile` on `test_shallow_all` Melder fast graphs: `solo,shallow,wide,diamond`).
- [ ] Story: STORY-2026-02-15-creationcontext-codegen-runtime-tightening - Implement ranked `CreationContext` runtime optimizations.
- [ ] Story: STORY-2026-02-15-phase12-codegen-runtime-tightening - Implement ranked `Phase12` runtime/helper optimizations.
- [ ] Story: STORY-2026-02-15-creationcontext-phase12-benchmark-regression-validation - Validate performance and contract compatibility.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-02-15-creationcontext-phase12-codegen-discovery-refresh.
- [ ] Task: Complete story STORY-2026-02-15-creationcontext-codegen-runtime-tightening.
- [ ] Task: Complete story STORY-2026-02-15-phase12-codegen-runtime-tightening.
- [ ] Task: Complete story STORY-2026-02-15-creationcontext-phase12-benchmark-regression-validation.
- [ ] Task: Verify Ticket Microcycle enforcement across active stories/tasks.

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

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
New optimization epic is active for `CreationContext` + `Phase12` codegen
runtime improvements. Next step is a current-head discovery refresh that ranks
implementation candidates before any code edits.
