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
| task: melder fast-graph cprofile suite | in_progress | codex | none | rank top hotspots from generated `.prof` artifacts for creationcontext/phase12 targeting | `context_compass/tasks/2026-02-15_profile_meld_hotpath_with_test_shallow_all_task.md` | 2026-02-15 | REQUIRED |

## Active Attention Details
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
