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
| test_shallow_all melder jit toggle | review | codex | none | waiting for user acceptance confirmation before closure | `context_compass/tasks/2026-02-15_add_melder_jit_toggle_to_test_shallow_all_task.md` | 2026-02-15 | REQUIRED |

## Active Attention Details
- TYPE: PLAN
  CLAIM: Active work is adding a benchmark-only Melder compilation mode toggle so `test_shallow_all` can run JIT opt-in or preserve default mode.
  EVIDENCE: `context_compass/tasks/2026-02-15_add_melder_jit_toggle_to_test_shallow_all_task.md:1-79`
  REREAD: REQUIRED
  NEXT: Fix default-mode test env handling and rerun `-k "melder_compilation_mode"` before returning to review.

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| onboarding single-command read bootstrap | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_add_single_powershell_onboarding_reonboarding_read_command_task.md` | 2026-02-15 | REQUIRED |
| re-onboarding read integrity enforcement | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_enforce_reonboard_real_read_no_performative_compliance_task.md` | 2026-02-15 | REQUIRED |
| jit/aot transfer propagation (non-contracted) | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_transfer_ownership_propagation_non_contracted_task.md` | 2026-02-15 | REQUIRED |
| jit/aot post-conjure bind propagation | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_post_conjure_bind_propagation_task.md` | 2026-02-15 | REQUIRED |
| jit/aot conjure propagation | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_conjure_propagation_task.md` | 2026-02-15 | REQUIRED |
| jit/aot config flag and fluent api | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_config_flag_and_fluent_api_task.md` | 2026-02-15 | REQUIRED |
| jit/aot regression matrix and compatibility | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_regression_matrix_and_compatibility_task.md` | 2026-02-15 | REQUIRED |
| jit/aot runtime resolution gate lifecycle | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_runtime_resolution_gate_lifecycle_task.md` | 2026-02-15 | REQUIRED |
| social contract document | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_social_contract_active_partner_performance_engineering_document_task.md` | 2026-02-15 | HELPFUL |
| attention board closure sync policy | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_attention_board_ticket_closure_sync_policy_task.md` | 2026-02-15 | HELPFUL |
