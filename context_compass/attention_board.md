# Attention Board

Purpose
- Active-work routing board.
- Attention-only summary for fast re-entry.
- Canonical detail lives in linked tickets.

Attention details rule
- Keep this board compact and operational.
- Durable history belongs in ticket `## Notes`, not here.
- Use evidence ranges in `EVIDENCE` (`path:start_line-end_line`).
- Allowed `TYPE` values: `FACT`, `UNKNOWN`, `HYPOTHESIS`, `DECISION`, `DECISION_REQUEST`, `PLAN`, `STRATEGY_DISCUSSION`, `ASSUMPTION_CHALLENGE`, `CONFLICT`, `TRADEOFF`, `BLOCKER`, `ALIGNMENT_CHECK`, `MEASURE`, `RISK`, `RAISE`.
- During ticket closure, run deterministic board sync (remove/replace active rows, prune stale details, add compact closed anchor, cap anchors).

## Active Items
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| task: phase12/creationcontext codegen optimize wave1 | in_progress | codex | none | keep retained direct Phase10 apply + patch-map cache wins, reject no-args invoke specialization, and continue on `_construct_spell_instance_with_overrides` / kwargs helper hotspots | `context_compass/tasks/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md` | 2026-02-15 | REQUIRED |

## Active Attention Details
- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: The `_invoke_spell_with_kwargs` no-args direct-call experiment regressed and was rejected by same-setting A/B runs; changed path averaged `38.5584ms` over 5 runs, while reverted baseline averaged `37.1777ms` over the next 5 runs (`warmup=100`, `iters=2000`, shallow overrides lane).
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1633-1640, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:152-161
  IMPACT: Keep prior invoke path and avoid no-args specialization in Phase12 overrides executor.
  NEXT: Continue isolated optimization on remaining dominant helper costs (`_construct_spell_instance_with_overrides` / kwargs assembly).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: After reverting the no-args invoke experiment, both profiling suites are green again (`8 passed` fast, `8 passed` overrides) with updated artifacts persisted.
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/benchmark_results.jsonl:114-121, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:162-169
  IMPACT: Retained optimization baseline remains stable for the next iteration tranche.
  NEXT: Begin next helper-level experiment from this baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: The latest empty-override kwargs short-circuit experiment regressed on repeated shallow timings (`37.9463ms` and `38.2707ms` sample averages), so it was reverted and not retained.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:111-115, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:124-133
  IMPACT: Current retained performance remains from the direct Phase10 apply and cached patch-map path; no new helper shortcut is kept.
  NEXT: Continue with a different isolated experiment focused on `_invoke_spell_with_kwargs`/call-site specialization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Final retained optimization state is validated (`8 passed` fast suite, `8 passed` overrides suite) and keeps shallow repeated timings below pre-wrapper baseline (`avg 37.5374ms` vs prior `38.7638ms`) after reverting non-winning helper tweaks.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:52-56, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:111-123, benchmarks/testing_other_di/profiles/fast_graphs_melder/benchmark_results.jsonl:90-97
  IMPACT: We have a stable, measured win and a clean starting point for the next optimization tranche.
  NEXT: Target remaining dominant Phase12 helper runtime (`_construct_spell_instance_with_overrides` / `_invoke_spell_with_kwargs`) with isolate-and-revert loops.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: A follow-up helper micro-patch (gating override-membership checks in `_build_kwargs_with_overrides`) did not improve over the current best baseline and was reverted after two repeated 5-run shallow timing samples (`37.2902ms`, `37.3784ms` vs baseline `37.0468ms`).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:88-92, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:101-110
  IMPACT: Keep the direct Phase10 apply optimization only; next iterations should focus on larger remaining Phase12 helper costs.
  NEXT: Target `_construct_spell_instance_with_overrides` / `_invoke_spell_with_kwargs` with isolate-and-measure workflow.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Replacing wrapper-based Phase10 application with direct `OverridePatchMap.apply(...)` in `CreationContext._execute_with_overrides` improved shallow override repeated timings from prior baseline avg `38.7638ms` to avg `37.0468ms` (5 runs each; same `warmup=100`, `iters=2000`), and both profiling suites remain green.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context.py:541-596, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:52-56, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:88-92, benchmarks/testing_other_di/profiles/fast_graphs_melder/benchmark_results.jsonl:82-89, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:93-100
  IMPACT: Phase10 wrapper overhead is reduced; next gains should focus on remaining Phase12 helper runtime costs.
  NEXT: Re-rank shallow override hotspots and patch the highest-value Phase12 helper path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Shallow override timing was rerun 5 times with the same settings (`warmup=100`, `iters=2000`): `47.6779, 47.7133, 47.6709, 46.4154, 47.0055 ms` (avg `47.2966 ms`, std `0.5139 ms`), confirming stable high-40ms behavior and no material win from the recent shape-cache tweak.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:52-56
  IMPACT: Further gains should target higher-cost override runtime paths instead of additional socket-shape caching.
  NEXT: Implement and test a narrow single-key override fast path in patch-map apply logic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: The CreationContext override-shape cache patch is runtime-safe but produced no clear shallow timing gain in same-setting high-iteration runs (`48.5444ms` pre vs `49.7372ms` post for the 2100-call lane); hotspot ranking still shows `apply_phase10_override_payload/apply_override_patch_map` and Phase12 override construct/kwargs helpers as dominant.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:42-43, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.hotspots.json:61-68, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.hotspots.json:96-110
  IMPACT: Wave-2 should pivot to heavier override application/runtime merge hotspots for measurable gains.
  NEXT: Implement a narrow single-key override fast path in Phase10 override apply and remeasure shallow timings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Steady-state shallow override profile (`warmup=100`, `iters=2000`) is now captured and shows cached-codegen override runtime still spending measurable per-call time in override application + shape/kwargs plumbing (`apply_phase10_override_payload/apply_override_patch_map`, `_collect_override_socket_shape`, `_construct_spell_instance_with_overrides`, `_build_kwargs_with_overrides`).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:4-10, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.hotspots.json:61-68, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.hotspots.json:96-124
  IMPACT: Next optimization wave should target per-call override preprocessing/runtime merge overhead rather than first-call compile costs.
  NEXT: Implement a minimal CreationContext override-shape preprocessing cache and remeasure shallow override lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Override profiling blocker from stale `_register_spell_instance` namespace export is fixed, and targeted shallow override timing profile test passes again.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:376-397, benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:681-696
  IMPACT: Active optimization work is unblocked and can proceed with wave-2 runtime edits.
  NEXT: Apply minimal override-shape runtime caching in CreationContext, then rerun targeted profiling.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Wave-1 prebound-registration patch validated green; immediate pre/post fast-graph entries improved for shallow/wide/diamond no-overrides lanes, while override timings are mixed/slightly slower on latest sample.
  EVIDENCE: context_compass/tasks/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md:68-75, benchmarks/testing_other_di/profiles/fast_graphs_melder/benchmark_results.jsonl:38-49, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:21-32
  IMPACT: We have a validated first optimization win on primary no-overrides lanes and a clear next target for override-lane follow-up.
  NEXT: Investigate override-lane hotspot changes and prepare wave-2 patch targeting override instance-construction helper overhead.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: Active routing moved from profiling to implementation using a new wave-1 optimization task under the Phase12 runtime-tightening story.
  EVIDENCE: context_compass/stories/2026-02-15_phase12_codegen_runtime_tightening_story.md:1-64, context_compass/tasks/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md:1-44
  IMPACT: Execution is now authorized for direct hotspot optimization edits with measured validation.
  NEXT: Read Phase12/CreationContext hotspot helper implementations and apply the first low-risk optimization patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Post-compaction reruns confirmed both cprofile suites pass with the new readable console summary format and persisted `.summary.txt` artifacts per lane.
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:1-29, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:1-29, context_compass/tasks/2026-02-15_profile_melder_overrides_graph_callchain_task.md:69-84
  IMPACT: Profiling output is now directly consumable without JSON parsing while preserving durable artifacts.
  NEXT: Rank override-lane hotspots and compare against non-override fast-graph timings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Overrides graph profiler is implemented and validated (`8 passed`) with durable artifacts under `profiles/overrides_graphs_melder`, including caller/callee chain JSON files.
  EVIDENCE: benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:1-603, context_compass/tasks/2026-02-15_profile_melder_overrides_graph_callchain_task.md:45-55
  IMPACT: Override-path codegen call chains are now inspectable per graph lane with the same artifact model as non-override profiling.
  NEXT: Build ranked override hotspot summary and identify first optimization targets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: User requested an overrides graph call-chain benchmark, so active routing moved to a new task that mirrors the artifact format used by the existing fast-graph profiler.
  EVIDENCE: context_compass/tasks/2026-02-15_profile_melder_overrides_graph_callchain_task.md:1-36, benchmarks/testing_other_di/test_overrides_all.py:256-334
  IMPACT: Discovery now expands to override-path call-chain evidence for codegen lanes.
  NEXT: Implement `test_melder_overrides_graphs_cprofile.py` and validate artifact generation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Profiling suite now writes persistent `.prof`, `.pstats.txt`, and JSONL benchmark artifacts per fast graph lane under `profiles/fast_graphs_melder`.
  EVIDENCE: benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:126-216, context_compass/tasks/2026-02-15_profile_meld_hotpath_with_test_shallow_all_task.md:41-52
  IMPACT: Benchmark and profile data are durable for cross-run analysis, not only console output.
  NEXT: Extract ranked hotspots and benchmark deltas from artifact files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Dedicated melder fast-graph cProfile suite executed successfully and generated smoke/timings profile artifacts for `solo`, `shallow`, `wide`, and `diamond`.
  EVIDENCE: benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:13-13, benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:177-247, context_compass/tasks/2026-02-15_profile_meld_hotpath_with_test_shallow_all_task.md:37-50
  IMPACT: Discovery now has concrete profile data for ranking rank-1 optimization targets.
  NEXT: Inspect generated `.prof` files and extract top cumulative hotspots by lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: Active routing moved from epic level to a concrete task that implements melder-only fast-graph cProfile coverage for the first shallow lane.
  EVIDENCE: context_compass/tasks/2026-02-15_profile_meld_hotpath_with_test_shallow_all_task.md:1-36, context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:82-89
  IMPACT: Execution scope is now directly actionable and validation-ready.
  NEXT: Implement `test_melder_fast_graphs_cprofile.py` and run the targeted pytest command.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: User redirected work to CreationContext + Phase12 codegen optimization, so active routing now targets a new dedicated optimization epic.
  EVIDENCE: context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:1-20, context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:72-97, context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:128-135
  IMPACT: Active execution lane is now explicitly scoped to codegen/runtime performance work with discovery-first ranking.
  NEXT: Create a discovery-refresh story/task under the new epic and begin hotspot inventory on current head.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| epic: jit/aot phase split configuration | done | codex | none | none | `context_compass/epics/completed/2026-02-14_jit_aot_phase_split_configuration_epic.md` | 2026-02-15 | REQUIRED |
| story: jit/aot runtime phase resolution path | done | codex | none | none | `context_compass/stories/completed/2026-02-14_jit_aot_runtime_phase_resolution_path_story.md` | 2026-02-15 | REQUIRED |
| story: jit/aot configuration and spell contract | done | codex | none | none | `context_compass/stories/completed/2026-02-14_jit_aot_configuration_and_spell_contract_story.md` | 2026-02-15 | REQUIRED |
| story: jit/aot split discovery and viability | done | codex | none | none | `context_compass/stories/completed/2026-02-14_jit_aot_split_discovery_and_viability_story.md` | 2026-02-15 | REQUIRED |
| story: jit/aot config flag and fluent api | done | codex | none | none | `context_compass/stories/completed/2026-02-15_jit_aot_config_flag_and_fluent_api_story.md` | 2026-02-15 | REQUIRED |
| story: jit/aot conjure propagation | done | codex | none | none | `context_compass/stories/completed/2026-02-15_jit_aot_conjure_propagation_story.md` | 2026-02-15 | REQUIRED |
| story: jit/aot post-conjure bind propagation | done | codex | none | none | `context_compass/stories/completed/2026-02-15_jit_aot_post_conjure_bind_propagation_story.md` | 2026-02-15 | REQUIRED |
| story: jit/aot transfer ownership propagation non-contracted | done | codex | none | none | `context_compass/stories/completed/2026-02-15_jit_aot_transfer_ownership_propagation_non_contracted_story.md` | 2026-02-15 | REQUIRED |
| story: jit/aot runtime resolution gate lifecycle | done | codex | none | none | `context_compass/stories/completed/2026-02-15_jit_aot_runtime_resolution_gate_lifecycle_story.md` | 2026-02-15 | REQUIRED |
| story: jit/aot regression matrix and compatibility | done | codex | none | none | `context_compass/stories/completed/2026-02-15_jit_aot_regression_matrix_and_compatibility_story.md` | 2026-02-15 | REQUIRED |
| task: shallow conjure aot-vs-jit pytest | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_add_melder_shallow_conjure_aot_vs_jit_pytest_task.md` | 2026-02-15 | REQUIRED |
| task: resolution_complete phase12 lifecycle | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_resolution_complete_phase12_lifecycle_task.md` | 2026-02-15 | REQUIRED |
