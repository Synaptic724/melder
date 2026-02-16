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
| task: phase12/creationcontext codegen optimize wave1 | in_progress | codex | none | prebound Phase10 apply-callable slice is retained on override-lane gains; continue from this baseline and target the next structural hotspot in `_execute_with_overrides`/`_phase12_executor` | `context_compass/tasks/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md` | 2026-02-16 | REQUIRED |

## Active Attention Details
- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Retain the `CreationContext` prebound Phase10 apply-callable slice as the active wave-1 baseline.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_creation_context_prebound_phase10_apply_delta_vs_prebaseline.txt:3-6, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_creation_context_prebound_phase10_apply_delta_vs_prebaseline.txt:9-12, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_creation_context_prebound_phase10_apply_postbaseline.txt:3-13
  IMPACT: Current routing baseline is stable and override-lane positive.
  NEXT: Continue from this baseline on the next structural hotspot.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: `CreationContext` binds `_override_apply_with_socket_shape_prechecked_phase10` once and reuses it in `_execute_with_overrides(...)`.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context.py:152-152, src/melder/aether/conduit/meld/creation_context/creation_context.py:228-234, src/melder/aether/conduit/meld/creation_context/creation_context.py:619-629, tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:99-130
  IMPACT: Removes repeated patch-map method lookup from override-bearing calls.
  NEXT: Keep as retained runtime behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Reject and revert the prebound active route-field slice and the positional executor-invocation slice; both were non-winning against retained baseline.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_creation_context_prebound_route_fields_delta_vs_prebaseline.txt:3-6, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_creation_context_positional_executor_invocation_delta_vs_prebaseline.txt:3-12
  IMPACT: Baseline remains focused on retained gains only.
  NEXT: Target a different structural optimization in `_execute_with_overrides` / `_phase12_executor`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Do not retain the no-overrides registration-inline emitter slice this tranche.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:587-591, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:625-629, benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_phase12_no_overrides_register_inline_slice_reverted.txt:2-20
  IMPACT: No no-overrides executor contract change is carried into active state.
  NEXT: Keep optimization effort override-focused.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Post-revert validation remains green (`83 passed` creation-context focused checks, `27 passed` no-overrides executor checks, `16 passed` cprofile suites).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_creation_context_positional_executor_invocation_slice_reverted.txt:1-9, benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_phase12_no_overrides_register_inline_slice_reverted.txt:2-20
  IMPACT: Active baseline correctness is reconfirmed after pruning non-retained slices.
  NEXT: Re-rank hotspots and implement next retained slice.
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

