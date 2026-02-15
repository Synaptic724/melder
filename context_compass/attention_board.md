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
| jit/aot phase split configuration | in_progress | codex | none | execute creation-context builder/factory deferred-runtime contract matrix and recommendation | `context_compass/tasks/2026-02-14_discovery_jit_aot_creation_context_builder_runtime_contract_task.md` | 2026-02-15 | REQUIRED |
| social contract document | in_progress | codex | none | run final acceptance/closure sync with user direction | `context_compass/tasks/2026-02-14_social_contract_active_partner_performance_engineering_document_task.md` | 2026-02-15 | REQUIRED |
| snapshot ownership cleanup audit | ready | codex | none | waiting for user prioritization | `context_compass/epics/2026-02-14_snapshot_ownership_cleanup_audit_epic.md` | 2026-02-14 | HELPFUL |

## Active Attention Details
- TYPE: FACT
  CLAIM: JIT/AOT lane currently has a completed phase-order implementation patch in code, and the next epic step is creation-context builder/factory discovery.
  EVIDENCE: `src/melder/spellbook/spell_crafter/spell_crafter.py:5047-5105`, `src/melder/spellbook/spell.py:1299-1349`, `context_compass/tasks/2026-02-14_discovery_jit_aot_creation_context_builder_runtime_contract_task.md:1-87`
  REREAD: REQUIRED
  NEXT: Complete discovery options matrix and recommended contract path.

- TYPE: DECISION
  CLAIM: Snapshot ownership cleanup epic remains available but unstarted per user direction.
  EVIDENCE: `context_compass/epics/2026-02-14_snapshot_ownership_cleanup_audit_epic.md:1-140`
  REREAD: HELPFUL
  NEXT: Start only when user prioritizes it.

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| attention board closure sync policy | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_attention_board_ticket_closure_sync_policy_task.md` | 2026-02-15 | HELPFUL |
