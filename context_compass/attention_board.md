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
| attention board closure sync policy | review | codex | none | waiting for user acceptance; hard gates and social-contract enforcement are implemented | `context_compass/tasks/2026-02-15_attention_board_ticket_closure_sync_policy_task.md` | 2026-02-15 | REQUIRED |
| jit/aot phase split configuration | in_progress | codex | none | close alignment task notes, then execute creation-context builder/factory contract discovery | `context_compass/tasks/2026-02-15_align_spellcrafter_phase_order_with_spellbook_creation_system_task.md` | 2026-02-15 | REQUIRED |
| social contract document | in_progress | codex | none | run final acceptance/closure sync with user direction | `context_compass/tasks/2026-02-14_social_contract_active_partner_performance_engineering_document_task.md` | 2026-02-15 | REQUIRED |
| snapshot ownership cleanup audit | ready | codex | none | waiting for user prioritization | `context_compass/epics/2026-02-14_snapshot_ownership_cleanup_audit_epic.md` | 2026-02-14 | HELPFUL |

## Active Attention Details
- TYPE: DECISION
  CLAIM: User-requested deterministic ticket-closure behavior is now formalized with hard execution gates in AGENTS/skills plus social-contract enforcement language.
  EVIDENCE: `context_compass/tasks/2026-02-15_attention_board_ticket_closure_sync_policy_task.md:1-125`, `context_compass/agent_onboarding/agent/general/skills/ticket_closure_attention_sync.md:1-46`, `context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:216-231`
  REREAD: REQUIRED
  NEXT: Get user acceptance, then enforce these gates on every ticket closure and active work tranche.

- TYPE: FACT
  CLAIM: JIT/AOT lane currently has a completed phase-order implementation patch in code, and the next epic step is creation-context builder/factory discovery.
  EVIDENCE: `src/melder/spellbook/spell_crafter/spell_crafter.py:5047-5105`, `src/melder/spellbook/spell.py:1299-1349`, `context_compass/tasks/2026-02-14_discovery_jit_aot_creation_context_builder_runtime_contract_task.md:1-78`
  REREAD: REQUIRED
  NEXT: Finish alignment-task closure notes/checklists, then advance discovery output matrix.

- TYPE: DECISION
  CLAIM: Snapshot ownership cleanup epic remains available but unstarted per user direction.
  EVIDENCE: `context_compass/epics/2026-02-14_snapshot_ownership_cleanup_audit_epic.md:1-140`
  REREAD: HELPFUL
  NEXT: Start only when user prioritizes it.

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| none in current pruning window | done | codex | none | none | `n/a` | 2026-02-15 | HELPFUL |
