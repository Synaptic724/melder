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
| benchmark: shallow conjure aot-vs-jit pytest | in_progress | codex | none | confirm if benchmark task should be closed now or extended with follow-up measurements | `context_compass/tasks/2026-02-15_add_melder_shallow_conjure_aot_vs_jit_pytest_task.md` | 2026-02-15 | HELPFUL |

## Active Attention Details
- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: After user-directed ticket turn-in, routing moved to the remaining in-progress benchmark task; closed review tasks were anchored under recently closed.
  EVIDENCE: context_compass/tasks/2026-02-15_add_melder_shallow_conjure_aot_vs_jit_pytest_task.md:1-40, context_compass/tasks/completed/2026-02-15_implement_resolution_complete_phase12_lifecycle_task.md:1-14
  IMPACT: Active board no longer references completed tickets and preserves one clear next work item.
  NEXT: Close the remaining benchmark task if user confirms acceptance, otherwise continue follow-up benchmark scope.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| implementation: resolution_complete phase12 lifecycle | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_resolution_complete_phase12_lifecycle_task.md` | 2026-02-15 | REQUIRED |
| discovery: jit mode skip phase8-12 conjure | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_discovery_jit_mode_skip_phase8_12_conjure_task.md` | 2026-02-15 | REQUIRED |
| discovery: jit/aot propagation contract surfaces | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_discovery_jit_aot_propagation_contract_surfaces_task.md` | 2026-02-15 | REQUIRED |
| implementation: align spellcrafter phase order with spellbook creation system | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_align_spellcrafter_phase_order_with_spellbook_creation_system_task.md` | 2026-02-15 | REQUIRED |
| implementation: add melder jit toggle to test_shallow_all | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_add_melder_jit_toggle_to_test_shallow_all_task.md` | 2026-02-15 | REQUIRED |
| discovery: jit/aot resolution_required spell contract | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_discovery_jit_aot_resolution_required_spell_contract_task.md` | 2026-02-15 | REQUIRED |
| discovery: jit/aot phase order contract | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_discovery_jit_aot_phase_order_contract_task.md` | 2026-02-15 | REQUIRED |
| discovery: jit/aot creation_context builder runtime contract | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_discovery_jit_aot_creation_context_builder_runtime_contract_task.md` | 2026-02-15 | REQUIRED |
| discovery: jit/aot assumption challenge | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_discovery_jit_aot_assumption_challenge_task.md` | 2026-02-15 | REQUIRED |
| discovery: phase12 codegen | done | codex | none | none | `context_compass/tasks/completed/2026-02-13_discovery_phase12_codegen_task.md` | 2026-02-15 | REQUIRED |
| onboarding: readme compaction and readset reduction | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_onboarding_readme_compaction_task_completed.md` | 2026-02-15 | REQUIRED |
| docs revalidation: src components epic | done | codex | none | none | `context_compass/epics/completed/2026-02-13_revalidate_src_components_document_epic.md` | 2026-02-15 | REQUIRED |
