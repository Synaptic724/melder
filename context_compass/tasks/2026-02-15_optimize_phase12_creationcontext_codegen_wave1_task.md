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

## Context / Handoff Summary
Wave-1 task is active and ready for code-level hotspot optimization and
targeted profiler validation.
