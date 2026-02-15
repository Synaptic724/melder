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
| discovery: jit conjure skip phases 8-12 | in_progress | codex | none | continue discovery and document concrete guard insertion plan for skipping 8-12 during conjure in jit mode | `context_compass/tasks/2026-02-15_discovery_jit_mode_skip_phase8_12_conjure_task.md` | 2026-02-15 | REQUIRED |

## Active Attention Details
- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: Active routing returns to the JIT conjure discovery task to finish file/symbol-level guard strategy for skipping phases 8-12 in conjure when JIT mode is enabled.
  EVIDENCE: context_compass/tasks/2026-02-15_discovery_jit_mode_skip_phase8_12_conjure_task.md:12-35, context_compass/tasks/2026-02-15_discovery_jit_mode_skip_phase8_12_conjure_task.md:59-88
  IMPACT: Work resumes on the unresolved runtime behavior gap after closing the onboarding-policy task.
  NEXT: Append next discovery note with exact insertion-point proposal and risk callouts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| onboarding policy: social contract first + remove parallel dump from instruction path | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_reorder_onboarding_social_contract_and_remove_parallel_dump_from_instruction_path_task_completed.md` | 2026-02-15 | REQUIRED |
| onboarding parallel dump enforcement | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_enforce_dump_chunked_500_line_onboarding_task_completed.md` | 2026-02-15 | REQUIRED |
| onboarding dump missing docs expansion | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_add_missing_onboarding_skills_docs_to_onboarding_dump_task.md` | 2026-02-15 | REQUIRED |
| onboarding single-command read bootstrap | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_add_single_powershell_onboarding_reonboarding_read_command_task.md` | 2026-02-15 | REQUIRED |
| re-onboarding read integrity enforcement | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_enforce_reonboard_real_read_no_performative_compliance_task.md` | 2026-02-15 | REQUIRED |
| jit/aot transfer propagation (non-contracted) | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_transfer_ownership_propagation_non_contracted_task.md` | 2026-02-15 | REQUIRED |
| jit/aot post-conjure bind propagation | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_post_conjure_bind_propagation_task.md` | 2026-02-15 | REQUIRED |
| jit/aot conjure propagation | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_conjure_propagation_task.md` | 2026-02-15 | REQUIRED |
| jit/aot config flag and fluent api | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_config_flag_and_fluent_api_task.md` | 2026-02-15 | REQUIRED |
| jit/aot regression matrix and compatibility | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_regression_matrix_and_compatibility_task.md` | 2026-02-15 | REQUIRED |
| jit/aot runtime resolution gate lifecycle | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_runtime_resolution_gate_lifecycle_task.md` | 2026-02-15 | REQUIRED |
| social contract document | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_social_contract_active_partner_performance_engineering_document_task.md` | 2026-02-15 | HELPFUL |
