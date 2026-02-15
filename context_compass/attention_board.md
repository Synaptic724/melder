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
| re-onboarding read integrity enforcement | review | codex | none | confirm acceptance; if approved move task to completed and resume runtime gate lane | `context_compass/tasks/2026-02-15_enforce_reonboard_real_read_no_performative_compliance_task.md` | 2026-02-15 | REQUIRED |
| jit/aot runtime resolution gate lifecycle | review | codex | none | review runtime gate test results; if accepted move task to completed and route next JIT/AOT lane | `context_compass/tasks/2026-02-15_implement_jit_aot_runtime_resolution_gate_lifecycle_task.md` | 2026-02-15 | REQUIRED |
| jit/aot regression matrix and compatibility | review | codex | none | review matrix evidence + targeted suite results; if accepted move task to completed | `context_compass/tasks/2026-02-15_implement_jit_aot_regression_matrix_and_compatibility_task.md` | 2026-02-15 | REQUIRED |
| snapshot ownership cleanup audit | ready | codex | none | waiting for user prioritization | `context_compass/epics/2026-02-14_snapshot_ownership_cleanup_audit_epic.md` | 2026-02-14 | HELPFUL |

## Active Attention Details
- TYPE: FACT
  CLAIM: User directed immediate enforcement patch for re-onboarding read integrity; active route temporarily shifts to policy docs before resuming runtime lane.
  EVIDENCE: `context_compass/tasks/2026-02-15_enforce_reonboard_real_read_no_performative_compliance_task.md:1-69`, `context_compass/tasks/2026-02-15_implement_jit_aot_runtime_resolution_gate_lifecycle_task.md:1-99`
  REREAD: REQUIRED
  NEXT: Confirm policy acceptance and close task, then resume runtime gate implementation.

- TYPE: DECISION
  CLAIM: User-selected direction is `A hybrid_rule_bound` with non-breaking default (`full_ahead_of_time_compilation=true`), plus mandatory propagation across conjure-time bind, late bind, and transfer (excluding contracted-spell ownership changes).
  EVIDENCE: `context_compass/tasks/2026-02-14_discovery_jit_aot_assumption_challenge_task.md:31-53`, `context_compass/tasks/2026-02-15_discovery_jit_aot_propagation_contract_surfaces_task.md:1-88`
  REREAD: REQUIRED
  NEXT: Complete propagation contract-surface discovery task, then start implementation tasks in story order.

- TYPE: MEASURE
  CLAIM: Runtime gate lifecycle tests now directly cover `_ensure_runtime_resolution_ready` transitions and meld pre-context ordering, with targeted suite passing.
  EVIDENCE: `tests/unit/melder/aether/conduit/meld/test_meld.py:1695-1931`, `context_compass/artifacts/2026-02-15_jit_aot_runtime_resolution_gate_lifecycle_meld_pytest.txt:1-12`, `context_compass/tasks/2026-02-15_implement_jit_aot_runtime_resolution_gate_lifecycle_task.md:6-41`
  REREAD: REQUIRED
  NEXT: Confirm acceptance criteria with user; on approval move runtime gate task to completed.

- TYPE: FACT
  CLAIM: Regression matrix lane is now active because all implementation tasks are review-ready.
  EVIDENCE: `context_compass/tasks/2026-02-15_implement_jit_aot_regression_matrix_and_compatibility_task.md:6-65`, `context_compass/tasks/2026-02-15_implement_jit_aot_config_flag_and_fluent_api_task.md:6-6`, `context_compass/tasks/2026-02-15_implement_jit_aot_conjure_propagation_task.md:6-6`, `context_compass/tasks/2026-02-15_implement_jit_aot_post_conjure_bind_propagation_task.md:6-6`, `context_compass/tasks/2026-02-15_implement_jit_aot_transfer_ownership_propagation_non_contracted_task.md:6-6`, `context_compass/tasks/2026-02-15_implement_jit_aot_runtime_resolution_gate_lifecycle_task.md:6-6`
  REREAD: REQUIRED
  NEXT: Complete regression matrix inventory and run targeted compatibility suites.

- TYPE: MEASURE
  CLAIM: Regression matrix targeted suites pass for spellbook propagation (3), transfer propagation/exclusion (3), and meld runtime gate lifecycle (7).
  EVIDENCE: `context_compass/artifacts/2026-02-15_jit_aot_regression_matrix_targeted_pytests_summary.txt:1-12`, `context_compass/tasks/2026-02-15_implement_jit_aot_regression_matrix_and_compatibility_task.md:6-56`
  REREAD: REQUIRED
  NEXT: Confirm acceptance criteria for regression matrix task and close if approved.

- TYPE: DECISION
  CLAIM: Snapshot ownership cleanup epic remains available but unstarted per user direction.
  EVIDENCE: `context_compass/epics/2026-02-14_snapshot_ownership_cleanup_audit_epic.md:1-140`
  REREAD: HELPFUL
  NEXT: Start only when user prioritizes it.

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| social contract document | done | codex | none | none | `context_compass/tasks/completed/2026-02-14_social_contract_active_partner_performance_engineering_document_task.md` | 2026-02-15 | HELPFUL |
| attention board closure sync policy | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_attention_board_ticket_closure_sync_policy_task.md` | 2026-02-15 | HELPFUL |
