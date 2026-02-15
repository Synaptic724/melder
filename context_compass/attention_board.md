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
| implementation: resolution_complete phase12 lifecycle | review | codex | none | confirm acceptance with user and close or route follow-up | `context_compass/tasks/2026-02-15_implement_resolution_complete_phase12_lifecycle_task.md` | 2026-02-15 | REQUIRED |

## Active Attention Details
- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: Active routing moved from discovery to implementation for resolution_complete lifecycle migration (default false, phase12 set true, invalidation clear false).
  EVIDENCE: context_compass/tasks/2026-02-15_implement_resolution_complete_phase12_lifecycle_task.md:1-46, context_compass/tasks/2026-02-15_implement_resolution_complete_phase12_lifecycle_task.md:78-85
  IMPACT: The next tranche is code edits + targeted validation, with scope constrained to resolution_complete semantics.
  NEXT: Apply focused code patch in Spell/SpellCrafter/Spellbook creation and transfer paths, then run targeted pytests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Resolution_complete lifecycle patch and targeted tests are complete; active row is now in review pending user acceptance.
  EVIDENCE: context_compass/tasks/2026-02-15_implement_resolution_complete_phase12_lifecycle_task.md:23-46, context_compass/tasks/2026-02-15_implement_resolution_complete_phase12_lifecycle_task.md:49-62, context_compass/tasks/2026-02-15_implement_resolution_complete_phase12_lifecycle_task.md:87-94
  IMPACT: Implementation tranche is finished and can be closed once acceptance is confirmed.
  NEXT: Ask user to confirm acceptance criteria.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated | reread |
|---|---|---|---|---|---|---|---|
| onboarding: readme compaction and readset reduction | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_onboarding_readme_compaction_task_completed.md` | 2026-02-15 | REQUIRED |
| docs revalidation: src components epic | done | codex | none | none | `context_compass/epics/completed/2026-02-13_revalidate_src_components_document_epic.md` | 2026-02-15 | REQUIRED |
| docs revalidation: src architecture epic | done | codex | none | none | `context_compass/epics/completed/2026-02-13_revalidate_src_architecture_document_epic.md` | 2026-02-15 | REQUIRED |
| onboarding hardening: manual-read path no dump lookup drift | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_harden_manual_onboarding_no_dump_path_task_completed.md` | 2026-02-15 | REQUIRED |
| onboarding policy: social contract first + remove parallel dump from instruction path | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_reorder_onboarding_social_contract_and_remove_parallel_dump_from_instruction_path_task_completed.md` | 2026-02-15 | REQUIRED |
| onboarding parallel dump enforcement | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_enforce_dump_chunked_500_line_onboarding_task_completed.md` | 2026-02-15 | REQUIRED |
| onboarding dump missing docs expansion | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_add_missing_onboarding_skills_docs_to_onboarding_dump_task.md` | 2026-02-15 | REQUIRED |
| onboarding single-command read bootstrap | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_add_single_powershell_onboarding_reonboarding_read_command_task.md` | 2026-02-15 | REQUIRED |
| re-onboarding read integrity enforcement | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_enforce_reonboard_real_read_no_performative_compliance_task.md` | 2026-02-15 | REQUIRED |
| jit/aot transfer propagation (non-contracted) | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_transfer_ownership_propagation_non_contracted_task.md` | 2026-02-15 | REQUIRED |
| jit/aot post-conjure bind propagation | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_post_conjure_bind_propagation_task.md` | 2026-02-15 | REQUIRED |
| jit/aot conjure propagation | done | codex | none | none | `context_compass/tasks/completed/2026-02-15_implement_jit_aot_conjure_propagation_task.md` | 2026-02-15 | REQUIRED |
