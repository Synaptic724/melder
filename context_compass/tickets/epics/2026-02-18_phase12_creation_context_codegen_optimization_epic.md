# Epic: Phase 12 and CreationContext Codegen Optimization

## Metadata
- Epic ID: EPIC-2026-02-18-phase12-creation-context-codegen-optimization
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-18T10:01:21Z
- Updated: 2026-02-18T10:10:22Z
- Target Window: 2026-Q1
- Related Program/Initiative: runtime-performance

## Problem / Opportunity
Phase 12 execution and CreationContext codegen are now the runtime hot path for
instance resolution. We have existing benchmark infrastructure and documented
route-matrix metrics, but no consolidated optimization epic to drive a strict
baseline -> optimize -> remeasure loop focused on this path.

## MRP Alignment (Most Reasonable Product)
The MRP is a stable, measurable, and maintainable codegen runtime where
CreationContext dispatch and Phase 12 executor generation stay fast under
warm-root, spellspace, and override-heavy routes without degrading correctness,
lifecycle guarantees, or API contracts. This avoids tactical one-off changes
that increase complexity without durable performance wins.

## Ticket Contract
- ENTRY_GATE: active board routing points to this epic and scope is user-approved.
- EXECUTION_BOUNDARY: Phase 12 + CreationContext codegen only; no unrelated refactors.
- DEPENDENCIES: architecture/component docs, benchmark runner, and story breakdown.
- EXIT_GATE: required stories accepted, benchmark deltas reported, board/ticket sync complete.
- FAILURE_ESCALATION: raise DECISION_REQUEST for metric regressions, contract ambiguity, or scope expansion.

## Goals (Outcomes)
- Establish a reproducible baseline for codegen routes before optimization.
- Reduce warm-path overhead in Phase 12 and CreationContext dispatch paths.
- Keep generated-executor behavior contract-equivalent to current runtime behavior.
- Produce evidence-backed benchmark deltas and explicit go/no-go gates.

## Non-Goals (Explicit Exclusions)
- Broad DI architecture rewrites outside codegen paths.
- Public API shape changes for `Spellbook`, `Conduit`, or `Meld`.
- Unrelated optimization work in non-codegen subsystems.

## Scope Boundaries
- In scope:
  - `src/melder/aether/conduit/meld/creation_context/*`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_*`
  - benchmark and validation paths needed to measure codegen impact
- Out of scope:
  - large-scale refactors outside the files above
  - policy/process edits unrelated to this optimization program

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user requested active focus on Phase 12 and CreationContext codegen optimization.

## Success Metrics
- Benchmark report generated from `run_codegen_benchmark_deltas.py` before and after changes.
- No regression greater than 5% on core warm routes (`warm_root_ns`, `warm_override_targeted_ns`).
- At least one measurable improvement on a targeted hot route with supporting evidence.
- No behavioral regressions in validation tests covering codegen execution lanes.

## Requirements (Functional + Non-Functional)
- Functional:
  - Preserve Phase 12 executor correctness for no-overrides and overrides lanes.
  - Preserve CreationContext route selection and ownership/creations semantics.
  - Preserve error semantics for missing roots/creations and invalid override paths.
- Non-functional:
  - Optimize for warm-path latency and predictable performance.
  - Keep generated source/compile steps deterministic and reviewable.
  - Keep changes scoped, documented, and test-backed.

## Constraints / Assumptions
- Existing benchmark harness is the canonical performance measurement path.
- Optimization must preserve cleanup and lifecycle contracts.
- Unknown benchmark variability across machines must be handled with repeated samples.
- Discovery and validation benchmark runs should pin process affinity to P-cores
  for comparable route metrics (`--pin-p-cores` / `DI_PIN_P_CORES=1`).

## Benchmark Affinity Discipline
- Use `--pin-p-cores` when running
  `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`.
- Runner behavior:
  - `--pin-p-cores` sets `DI_PIN_P_CORES=1`.
  - Runner calls `get_or_apply_p_core_affinity_from_env()` before sampling.
- Environment toggles:
  - `DI_PIN_P_CORES`: enable/disable pinning.
  - `DI_PIN_P_CORES_STRICT`: strict failure reporting for affinity setup.
- When running from shell, set `PYTHONPATH='.;src'` so both `melder` and
  `benchmarks.p_core_affinity` imports resolve.

## Experiment Metric Policy
- Do not use median values for experiment decisions in this epic.
- Use mean values computed from raw sample arrays in report payloads:
  - `samples_ns.*` for global cold/warm/mixed metrics
  - `route_samples_ns.*` for per-route metrics
- Exclude `warm_spellspace_ns` from decision metrics and optimization scoring.
- Keep spellspace metrics available for visibility/debugging only.

## Dependencies / External References
- `src/melder/aether/conduit/meld/meld.py:347-387`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py:282-331`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py:1085-1235`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:112-180`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:19-87`
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1235-1314`
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:370-375`
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1248-1254`
- `benchmarks/p_core_affinity/p_core_affinity.py:373-385`
- `context_compass/system_docs/src_architecture.md:518-521`
- `context_compass/system_docs/src_components.md:1496-1503`

## Milestones (Track Progress)
- [ ] Milestone 1: Baseline and hotspot map complete from route-matrix benchmark outputs.
- [ ] Milestone 2: CreationContext codegen optimizations implemented and verified.
- [ ] Milestone 3: Phase 12 executor codegen optimizations implemented and verified.
- [ ] Milestone 4: Post-change benchmark report and acceptance decision completed.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-18-codegen-baseline-and-hotspot-map - establish measurements and gates.
- [ ] Story: STORY-2026-02-18-creation-context-codegen-optimization - optimize context compile/dispatch path.
- [ ] Story: STORY-2026-02-18-phase12-executor-codegen-optimization - optimize generated executor lanes.
- [ ] Story: STORY-2026-02-18-codegen-validation-and-benchmark-closeout - validate behavior and perf deltas.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-02-18-codegen-baseline-and-hotspot-map.
- [ ] Task: Complete story STORY-2026-02-18-creation-context-codegen-optimization.
- [ ] Task: Complete story STORY-2026-02-18-phase12-executor-codegen-optimization.
- [ ] Task: Complete story STORY-2026-02-18-codegen-validation-and-benchmark-closeout.
- [ ] Task: Keep architecture/components docs aligned with codegen runtime changes.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- All required stories are completed and explicitly accepted.
- Baseline and post-change benchmark reports are attached or referenced.
- Performance gates are evaluated with explicit pass/fail outcomes and rationale.
- Codegen behavior remains contract-correct for no-overrides and overrides lanes.
- `attention_board.md` and ticket summaries are synchronized at closure.

## Risks / Mitigations
- Risk: micro-optimizations may improve one route while regressing others.
  - Mitigation: use route-matrix reporting and enforce multi-route gates.
- Risk: generated source changes may alter runtime semantics subtly.
  - Mitigation: keep contract tests focused on executor behavior and errors.
- Risk: optimization scope may expand into unrelated runtime subsystems.
  - Mitigation: enforce execution boundary and escalate scope expansion decisions.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Run codegen benchmark report before and after optimization:
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 9 --warmup-count 1 --pin-p-cores`
- Run targeted pytest suites for codegen and creation-context behavior.
- Record validation truthfully; report `Not run` when execution is skipped.

## Rollout / Adoption Plan
- Execute in story tranches: baseline first, then isolated codegen changes.
- Review each tranche with benchmark deltas before moving to next tranche.
- Publish final closeout summary with route-level results and residual risks.

## Open Questions
- Should we prioritize warm-route median reduction or weighted route score first?
- Do we need separate gates for override specialization cache hit/miss behavior?
- Which route regressions are acceptable when offset by larger wins elsewhere?

## Decision Log
- 2026-02-18: Scope fixed to Phase 12 executor codegen and CreationContext codegen.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-02-18T10:01:21Z
  TYPE: DECISION
  CLAIM: This epic is the active optimization program for Phase 12 and CreationContext codegen.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:347-387
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:282-331
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:112-180
  IMPACT: Subsequent optimization work remains scoped to codegen hot paths with measurable outputs.
  NEXT: Create the first story for baseline capture and hotspot mapping.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:08:30Z
  TYPE: FACT
  CLAIM: Meld hot path duplicates CreationContext acquisition in both hook and no-hook branches.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:346-350
  - src/melder/aether/conduit/meld/meld.py:372-375
  IMPACT: Duplicate branch/control flow in the hottest resolve path is a concrete optimization target.
  NEXT: Evaluate a single acquisition path and measure warm-route delta before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:18:10Z
  TYPE: MEASURE
  CLAIM: Discovery benchmark shows warm spellspace/mixed routes dominate warm latency versus warm root.
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18.json:33-37
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18.json:40-44
  IMPACT: Highest-yield optimization opportunities are in spellspace/mixed route dispatch, not root-only dispatch.
  NEXT: Trace CreationContext route/override dispatch paths that are unique to spellspace and mixed routes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:04:53Z
  TYPE: DECISION
  CLAIM: Benchmark discovery and validation for this epic should run with P-core affinity pinning.
  EVIDENCE:
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:370-375
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1248-1254
  - benchmarks/p_core_affinity/p_core_affinity.py:373-385
  IMPACT: Route-matrix comparisons are less noisy and more comparable across optimization tranches.
  NEXT: Use `--pin-p-cores` on subsequent benchmark runs and capture affinity status in reports.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:05:49Z
  TYPE: MEASURE
  CLAIM: P-core pinned discovery confirms warm spellspace and mixed routes are the dominant warm-path costs.
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned.json:105-107
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned.json:145-149
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned.json:209-218
  IMPACT: Priority ops should target spellspace no-overrides template and Phase 12 step executor work in mixed/spellspace paths.
  NEXT: Build a story focused on spellspace/mixed hot-path reductions in CreationContext + Phase 12 executor lanes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:06:22Z
  TYPE: HYPOTHESIS
  CLAIM: Spellspace hot-path cost is likely driven by repeated active-spellspace lookup and spellspace bucket access/registration in generated lanes.
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned.json:587-596
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned.json:616-617
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:521-527
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:920-925
  IMPACT: A focused change that hoists/reuses spellspace context in compiled lanes may reduce dominant warm-route overhead.
  NEXT: Prototype a spellspace-context hoist in codegen emitters and benchmark `warm_spellspace_ns` + `warm_mixed_ns`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:10:22Z
  TYPE: DECISION
  CLAIM: Experiment scoring for this epic now uses means (not medians) and excludes spellspace route data.
  EVIDENCE:
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:654-658
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:860-865
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned.json:653-677
  IMPACT: Future optimization decisions align to mean-based route behavior and ignore non-target spellspace signal.
  NEXT: Recompute tracked baseline/after ratios using means from raw samples excluding `warm_spellspace_ns`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:10:22Z
  TYPE: MEASURE
  CLAIM: Mean-based pinned discovery (excluding spellspace route) reports warm_mixed as the dominant optimization route.
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned.json:653-666
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned.json:668-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned.json:681-695
  IMPACT: Optimization priority should remain mixed route first, then targeted overrides, then root micro-ops.
  NEXT: Use these mean baselines for the first implementation tranche acceptance check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:19:20Z
  TYPE: DECISION
  CLAIM: De-prioritize branch-structure exploration and focus optimization work only on CreationContext and Phase 12 codegen operations.
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:166-336
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:390-671
  IMPACT: Next implementation tranche is constrained to generated executor lanes and override dispatch internals, not branch-level experiments.
  NEXT: Prioritize phase12/codegen ops by mean route weight (excluding `warm_spellspace_ns`) and cumulative profiler cost.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:19:55Z
  TYPE: MEASURE
  CLAIM: Mean route weighting excluding spellspace confirms warm_mixed (23100 ns mean) > warm_override_targeted (6700 ns) > warm_override_root_args (6133.33 ns) > warm_root (600 ns), and pinned deep profiles isolate phase12/codegen hotspots in override dispatch and generated executors.
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:1066-1084
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:217-336
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:427-434
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:595-616
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:665-665
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:565-739
  - src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2610-2735
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1054-1289
  - src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:268-416
  IMPACT: Priority ops are `_execute_with_overrides`, generated `<melder_phase12_overrides_executor>._phase12_executor`, `patch_maps` target resolution/apply, and no-overrides executor creation/reuse helpers.
  NEXT: Create the first optimization story with this op order and benchmark each tranche with pinned mean metrics excluding spellspace.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:24:00Z
  TYPE: DECISION
  CLAIM: Epic execution has transitioned to story/task microcycles for baseline and hotspot mapping, with active board routing moved to the new story.
  EVIDENCE:
  - tickets/stories/2026-02-18_codegen_baseline_and_hotspot_map_story.md:1-122
  - tickets/tasks/2026-02-18_codegen_phase12_baseline_mean_profile_task.md:1-99
  - tickets/tasks/2026-02-18_codegen_phase12_hotspot_op_priority_map_task.md:1-105
  - attention_board.md:38-48
  IMPACT: Work proceeds through concrete story/task deliverables, enabling immediate selection of a first implementation target.
  NEXT: Finalize ranked phase12/codegen op order in story notes and start the first implementation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:25:20Z
  TYPE: PLAN
  CLAIM: Baseline/hotspot mapping selected `CreationContext._execute_with_overrides` as first implementation target and active routing moved to implementation mode.
  EVIDENCE:
  - tickets/stories/2026-02-18_codegen_baseline_and_hotspot_map_story.md:125-134
  - tickets/tasks/2026-02-18_codegen_phase12_hotspot_op_priority_map_task.md:112-121
  - attention_board.md:38-48
  IMPACT: Next tranche can execute a narrow change in override dispatch with direct pinned benchmark feedback.
  NEXT: Implement override-dispatch micro-optimizations and rerun pinned benchmark deltas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:28:45Z
  TYPE: MEASURE
  CLAIM: First override-dispatch implementation tranche improved root-args override means but left targeted/mixed outcomes not clearly improved, so a second tranche is required.
  EVIDENCE:
  - tickets/tasks/2026-02-18_creation_context_override_dispatch_micro_optimization_task.md:107-126
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_cc_override_dispatch.json:652-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_cc_override_dispatch_r2.json:652-671
  IMPACT: Program priority remains override path optimization, now focusing on patch-map + overrides-executor internals.
  NEXT: Execute tranche 2 optimization and remeasure pinned non-spellspace means.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:36:22Z
  TYPE: DECISION
  CLAIM: User directed reverting tranche 1 and tranche 2 optimization code; epic execution continues from reverted baseline.
  EVIDENCE:
  - tickets/tasks/2026-02-18_creation_context_override_dispatch_micro_optimization_task.md:122-141
  - tickets/tasks/2026-02-18_targeted_override_patchmap_micro_optimization_task.md:115-134
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:611-614
  - src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:302-323
  IMPACT: Previous tranche code is not retained; next optimization attempt must come from a fresh hotspot slice.
  NEXT: Start overrides-executor hotspot tranche and benchmark deltas from pinned baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:39:48Z
  TYPE: MEASURE
  CLAIM: Tranche 3 overrides-executor kwargs fast-path also regressed mixed route and was reverted.
  EVIDENCE:
  - tickets/tasks/2026-02-18_overrides_executor_kwargs_fastpath_task.md:99-128
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_overrides_executor_tranche3.json:652-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_overrides_executor_tranche3_r2.json:652-671
  IMPACT: All attempted tranches to date are reverted; next attempt shifts to no-args invocation hot path.
  NEXT: Execute no-args invocation fast-path tranche and rerun pinned means.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:42:12Z
  TYPE: MEASURE
  CLAIM: Tranche 4 no-args invocation fast path also regressed route means and was reverted.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase12_invoke_no_args_fastpath_task.md:106-125
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_invoke_fastpath_tranche4.json:652-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_invoke_fastpath_tranche4_r2.json:652-671
  IMPACT: Four tranches are reverted; next iteration should increase measurement confidence before editing.
  NEXT: Run higher-sample pinned route baseline and re-rank ops.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Epic created and routed for active work. Focus is limited to Phase 12 and
CreationContext codegen optimization with benchmark-first execution. Next step
is creating the baseline/hotspot story and routing execution through it. Latest
priority order uses mean metrics (excluding spellspace) and targets phase12
override dispatch/codegen ops before any branch-level experimentation.
