# Task: Optimize Phase12 and CreationContext Codegen Wave 1

## Metadata
- Task ID: TASK-2026-02-15-optimize-phase12-creationcontext-codegen-wave1
- Story: STORY-2026-02-15-phase12-codegen-runtime-tightening
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Implement the first hotspot-led codegen runtime optimization patch for
Phase12/CreationContext and validate with targeted profiler suites.

## Scope Boundaries
- In scope:
- Hotpath edits in `phase12_no_overrides_executor.py`,
  `phase12_overrides_executor.py`, and `creation_context.py` only if required.
- Targeted reruns of fast-graph and override cprofile suites.
- Out of scope:
- Public API changes.
- Broad refactors outside measured hotspot callpaths.

## Steps / Checklist
- [x] Confirm top hotspot helper targets from `.summary.txt` + call-chain artifacts.
- [x] Apply minimal optimization patch on selected helper path(s).
- [x] Re-run targeted cprofile pytest suites and compare key lanes.
- [x] Record measured deltas and behavior observations.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Wave-1 runtime optimization code patch.
- Updated profiler artifacts for fast and overrides lanes.
- Notes entry documenting before/after observations.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py` (only if needed)
- `context_compass/tasks/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md`

## Validation
- Ran:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s`
- Result:
  - `8 passed, 1 warning in 0.78s` (fast graphs)
  - `8 passed, 1 warning in 0.38s` (override graphs)

## Risks / Rollback Notes
- Risk: speed change in one lane regresses another lane.
  Rollback: keep patch isolated, then compare both suites before finalizing.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: Next isolated experiment targets `_invoke_spell_with_kwargs` no-args path by calling `spell.spell(**kwargs)` directly when `__args__` is absent, avoiding empty-args container setup and starred-args dispatch on the common path.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1607-1644, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.hotspots.json:68-75
  IMPACT: This focuses on a remaining top helper hotspot while keeping override mapping and kwargs construction unchanged.
  NEXT: Patch only the no-args branch in `_invoke_spell_with_kwargs`, run two repeated 5-run shallow samples, and keep/revert strictly by measured delta.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: The `_build_kwargs_with_overrides -> _build_kwargs_no_overrides` empty-override short-circuit experiment regressed shallow repeated timings and was reverted; two 5-run samples averaged `37.9463ms` and `38.2707ms`, both worse than the retained-state baseline (`37.5374ms` on the same settings).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:111-115, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:124-133
  IMPACT: The shared-builder shortcut is not a net win on this lane despite cleaner logic reuse.
  NEXT: Keep current retained state and pivot next experiment to `_invoke_spell_with_kwargs`/call-site specialization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: Next isolated experiment is to short-circuit `_build_kwargs_with_overrides` to `_build_kwargs_no_overrides` when `override_values` is empty, reusing existing no-override logic and removing override-specific checks from the majority non-targeted step calls.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1355-1391, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1467-1604, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:893-1024
  IMPACT: This should reduce helper-loop overhead for steps without targeted/runtime overrides while preserving existing kwargs semantics through the shared no-overrides builder.
  NEXT: Implement the short-circuit, run two repeated 5-run shallow timing samples, and keep/revert based on measured delta.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Final retained state (direct Phase10 patch-map apply + prior patch-map caching fast path, with helper micro-patches reverted) stays green in both suites and keeps shallow repeated timings below the old baseline (`37.1622, 38.8529, 37.4028, 37.3712, 36.8981 ms`; avg `37.5374 ms` vs pre-wrapper baseline `38.7638 ms`).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:52-56, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:111-123, benchmarks/testing_other_di/profiles/fast_graphs_melder/benchmark_results.jsonl:90-97
  IMPACT: Current accepted optimization set is stable and measurably faster on the target override lane.
  NEXT: Continue next tranche by targeting dominant Phase12 helper costs (`_construct_spell_instance_with_overrides` / `_invoke_spell_with_kwargs`) with stricter isolate-and-revert measurement loops.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: The follow-up `_build_kwargs_with_overrides` membership-gating micro-patch did not beat the current accepted baseline; repeated 5-run samples averaged `37.2902ms` and `37.3784ms` vs the current best `37.0468ms`, so this patch was rejected and reverted.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:88-92, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:101-110
  IMPACT: Keep the direct patch-map apply change as the active optimization and avoid helper-level churn without clear gain.
  NEXT: Shift next optimization slice to remaining dominant helpers (`_construct_spell_instance_with_overrides` / `_invoke_spell_with_kwargs`) with stricter isolate-and-measure loops.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: With wrapper overhead removed, the next isolated micro-optimization is to gate `_build_kwargs_with_overrides` override-membership checks behind a precomputed boolean (`has_override_values`) so empty-override calls do not pay repeated dict-membership probes inside dependency/contract loops.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.hotspots.json:82-110, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1511-1603
  IMPACT: This preserves helper semantics while targeting a remaining hot helper path after Phase10 wrapper removal.
  NEXT: Apply the boolean-gated membership patch only, then rerun repeated shallow timings and keep/revert based on measured delta.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Direct Phase10 patch-map apply in CreationContext produced a real shallow override improvement in repeated high-iteration runs (`37.4234, 37.0497, 36.3216, 37.5648, 36.8745 ms`; avg `37.0468 ms`, std `0.4395 ms`) versus the prior accepted baseline (`39.1105, 38.7711, 38.0447, 39.4234, 38.4694 ms`; avg `38.7638 ms`, std `0.4815 ms`).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:52-56, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:88-92
  IMPACT: Wrapper-layer removal in the Phase10 override application path yields an additional steady-state shallow speedup and should be kept.
  NEXT: Keep this patch and target the remaining dominant Phase12 runtime helpers (`_construct_spell_instance_with_overrides`, `_build_kwargs_with_overrides`).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: CreationContext override runtime now performs Phase10 targeting via direct `OverridePatchMap.apply(...)` call with explicit missing-map guard, removing one hot wrapper chain layer while preserving failure semantics.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context.py:541-596
  IMPACT: Hot-path override calls no longer pay repeated `apply_phase10_override_payload -> apply_override_patch_map` dispatch overhead.
  NEXT: Re-profile hotspot distribution and evaluate next micro-optimization in Phase12 helper execution path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Post-patch validation remains green across both profiling suites (`8 passed` each), with updated artifacts persisted for fast and overrides graph lanes.
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/benchmark_results.jsonl:82-89, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:93-100
  IMPACT: The optimization is validated without breaking current benchmark/profile workflows.
  NEXT: Continue iteration on the remaining Phase12 helper hotspots using the refreshed artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: Next attempt will remove Phase10 override wrapper call overhead from the CreationContext runtime path by calling `OverridePatchMap.apply(...)` directly (keeping the same missing-map error semantics) instead of routing through `apply_phase10_override_payload -> apply_override_patch_map`.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.hotspots.json:61-89, src/melder/aether/conduit/meld/creation_context/creation_context.py:595-595
  IMPACT: This targets measured wrapper overhead in a hot per-call path without changing patch-map targeting logic.
  NEXT: Patch `_execute_with_overrides` in `creation_context.py`, rerun 5x shallow timings (`warmup=100`, `iters=2000`), then validate both cprofile suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: The Phase12 helper micro-patch (dict-copy/check tightening + no-args tuple path) did not improve shallow override timings; two repeated 5-run distributions measured slower than the prior baseline (`39.9976ms` and `39.1827ms` vs earlier `38.7638ms`), so this optimization path is rejected.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:52-56, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:78-87
  IMPACT: Keep the override helper behavior unchanged and move to a different hotspot candidate to avoid shipping a regression/noise patch.
  NEXT: Investigate a no-patch-map/no-shape path for single-key override payloads in `CreationContext._execute_with_overrides` and remeasure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: Next wave will target Phase12 override runtime helper overhead by removing avoidable per-call allocations/checks in `_build_kwargs_with_overrides` and `_invoke_spell_with_kwargs` (dict copy on empty-dependency path, unconditional override-membership probes when override map is empty, and empty-list allocation for no-args invocation path).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:1-2, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.hotspots.json:54-89, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1487-1603, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1636-1636
  IMPACT: This keeps scope narrow to hot helper paths while preserving current Phase10/CreationContext behavior and should reduce steady-state override lane runtime cost after cache hit.
  NEXT: Apply a minimal helper-level patch in `phase12_overrides_executor.py`, then rerun repeated shallow override timings and both cprofile suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: The benchmark override workload currently sends one-key `spell_override` payloads per call, while steady-state hotspot ranking still shows Phase10 override apply (`apply_phase10_override_payload` / `apply_override_patch_map`) as a dominant per-call cost.
  EVIDENCE: benchmarks/testing_other_di/test_overrides_all.py:577-577, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.hotspots.json:61-68
  IMPACT: A single-key fast path in `OverridePatchMap.apply` is a high-leverage next optimization candidate with low semantic risk.
  NEXT: Implement cached per-raw-key TargetSpec resolution + single-key apply fast path in `patch_maps.py`, then rerun the same 5-run shallow timing distribution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Repeated shallow override timing profile runs (5 consecutive runs, same settings `warmup=100`, `iters=2000`) landed at `47.6779, 47.7133, 47.6709, 46.4154, 47.0055 ms` (avg `47.2966 ms`, std `0.5139 ms`), confirming the lane is stable in the high-40ms band and that the recent shape-cache tweak does not deliver a material end-to-end improvement.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:52-56
  IMPACT: Wave-2 optimization should move to heavier hotspots (`patch_maps` override apply and Phase12 override kwargs/construct paths) rather than additional socket-shape micro-tuning.
  NEXT: Prototype a narrow single-key override fast path in `patch_maps.OverridePatchMap.apply` and rerun the same 5-run shallow timing distribution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: CreationContext override-shape memoization patch is behavior-safe (`fast` and `overrides` cprofile suites pass) but shows no clear end-to-end shallow timing win in same-setting high-iteration runs (`48.5444ms` pre -> `49.7372ms` post for the 2100-call lane), while hotspots remain dominated by Phase10 override apply and Phase12 override construct/kwargs paths.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:42-43, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.hotspots.json:61-68, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.hotspots.json:96-110
  IMPACT: This micro-optimization is not sufficient for material override-lane speedup; next wave should target heavier per-call override-application/runtime merge work.
  NEXT: Evaluate a single-key override fast path in `patch_maps.OverridePatchMap.apply` (current benchmark workload uses one override key per call) and remeasure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: The overrides-namespace blocker is resolved by removing the stale `_register_spell_instance` export, and targeted shallow override cprofile validation is green again.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:376-397, benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:681-696
  IMPACT: Override-lane profiling is unblocked for wave-2 runtime optimization work.
  NEXT: Implement the next minimal runtime optimization slice and remeasure shallow override timings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: A high-iteration shallow override profile (`warmup=100`, `iters=2000`) shows steady-state override cost concentrated in per-call override plumbing after codegen cache hit: `apply_phase10_override_payload/apply_override_patch_map` (`~14.4ms` total), `creation_context._collect_override_socket_shape` (`~2.75ms`), and Phase12 override helpers (`_construct_spell_instance_with_overrides` `~15.1ms`, `_build_kwargs_with_overrides` `~4.76ms`, `_build_step_override_values` `~1.30ms`) across 2100 calls.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:4-10, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.hotspots.json:61-68, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.hotspots.json:96-124
  IMPACT: Cached override codegen removes first-call compile cost, but override lanes still pay measurable runtime normalization and shape-derivation overhead each call.
  NEXT: Implement a creation-context socket-shape fast path cache keyed by override socket refs to reduce `_collect_override_socket_shape` overhead on repeated override payload shapes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: BLOCKER
  CLAIM: Override specialization compile currently fails with `NameError: _register_spell_instance is not defined` because the overrides executor namespace still exports a stale `_register_spell_instance` symbol after prebound-registration migration.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:379-379, benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:688-696
  IMPACT: Override-lane timing validation is blocked until the namespace export mismatch is removed.
  NEXT: Remove the stale namespace binding and rerun override cprofile tests to restore green baseline before wave-2 optimization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Post-patch reruns are green; immediate pre/post timings entries show faster no-overrides fast-graph lanes (`shallow`: 112.2439 -> 108.0718 ms, `wide`: 125.6342 -> 115.9445 ms, `diamond`: 120.6750 -> 110.2565 ms) with a small `solo` increase (76.6844 -> 76.8766 ms), while override timings are mixed/slightly slower on the latest sample (`shallow`: 24.2603 -> 24.4236 ms, `wide`: 37.3619 -> 37.9155 ms, `diamond`: 32.7675 -> 34.3365 ms).
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/benchmark_results.jsonl:38-49, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:21-32
  IMPACT: The prebound registration metadata patch improves primary no-overrides timings lanes but needs another pass for override-lane regressions/noise before closure.
  NEXT: Inspect override-lane hotspots after this patch and choose a wave-2 change targeting `_construct_spell_instance_with_overrides` or `_build_step_override_values`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Wave-1 patch now prebinds registration metadata (`spell_id`, `has_disposal_methods`, `disposal_methods`) into generated step lanes and routes hot-path registration calls through `_register_spell_instance_prebound(...)` for both no-overrides and overrides executors.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:489-499, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:538-726, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1098-1167, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:379-398, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:657-1116
  IMPACT: Runtime registration no longer re-reads spell registration attributes on each helper invocation in generated lanes.
  NEXT: Run targeted profiler suites to verify behavior and measure lane-level impact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: The no-overrides hotspot helper `_register_spell_instance` performs repeated per-call spell attribute extraction (`spell_id`, `has_disposal_methods`, `disposal_method_names`) while generated step source invokes this helper across many hotpath callsites in both no-overrides and overrides executors.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1038-1097, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:575-706, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:700-1062, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:10-20
  IMPACT: Replacing spell-attribute lookups with prebound step constants should reduce helper overhead on the hottest no-overrides lane and improve shared helper usage for overrides lanes.
  NEXT: Add a prebound registration helper and switch emitted no-overrides/overrides source to call it with per-step constants.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Timings-lane summaries identify runtime helper hotspots in Phase12 execution paths for both no-overrides and overrides lanes (`_construct_spell_instance*`, `_register_spell_instance`, and creation-context overrides dispatcher path).
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:6-29, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:5-29
  IMPACT: The first patch should target helper-call overhead in these runtime helpers instead of compile/build-once paths.
  NEXT: Inspect helper implementations and select the smallest high-frequency optimization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: The `_invoke_spell_with_kwargs` no-args direct call experiment (`spell.spell(**kwargs)`) regressed shallow repeated timings and was rejected after same-setting A/B runs; changed variant averaged `38.5584ms` (`38.5325, 38.3347, 38.1554, 39.0781, 38.6914`) while reverted baseline averaged `37.1777ms` (`37.1150, 37.1263, 37.3620, 37.3805, 36.9049`).
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1633-1640, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:152-161
  IMPACT: Keep `_invoke_spell_with_kwargs` on the prior path (`args=[]; call_kwargs=kwargs`) and avoid no-args direct-call specialization.
  NEXT: Continue optimization on other Phase12 override helpers, prioritizing `_construct_spell_instance_with_overrides` / kwargs assembly costs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Post-revert validation is green again on both profiling suites (`8 passed` fast, `8 passed` overrides) with refreshed artifacts.
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/benchmark_results.jsonl:114-121, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:162-169
  IMPACT: Retained state is stable after rejecting the no-args invoke experiment.
  NEXT: Start next isolated helper optimization slice from this validated baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Wave-1 task is active and ready for code-level hotspot optimization and
targeted profiler validation.
