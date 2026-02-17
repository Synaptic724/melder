# Attention Board

Purpose
- Active-work routing board.
- Attention-only summary for fast re-entry.
- Canonical detail lives in linked tickets.

Attention details rule
- Keep this board compact and operational.
- Durable history belongs in ticket `## Notes`, not here.
- Use evidence ranges in `EVIDENCE` (`path:start_line-end_line`).
- Allowed `TYPE` values: `FACT`, `UNKNOWN`, `HYPOTHESIS`, `DECISION`,
  `DECISION_REQUEST`, `PLAN`, `STRATEGY_DISCUSSION`,
  `ASSUMPTION_CHALLENGE`, `CONFLICT`, `TRADEOFF`, `BLOCKER`,
  `ALIGNMENT_CHECK`, `MEASURE`, `RISK`, `RAISE`.
- During ticket closure, run deterministic board sync (remove/replace active
  rows, prune stale details, add compact closed anchor, cap anchors).
- Ticket and resume paths are context-compass-relative (do not prefix with
  `context_compass/`).
- Use `DATETIME` and `updated_at` values in ISO-8601 UTC
  (`YYYY-MM-DDTHH:MM:SSZ`).
- Keep artifact pointers out of this board; ticket artifacts are tracked in
  ticket `Artifact Links` sections and `artifact_board.md`.

## Active Items
| work_item | status | mode | owner | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
|---|---|---|---|---|---|---|---|---|---|---|
| task: split root AGENTS into bootstrap and profile-owned policies | in_progress | implementation | codex | none | review and tighten profile AGENTS content for final cutover | profile AGENTS docs are clean and complete for root replacement | user confirms root + new/general/engineer/synaptic structure is ready to finalize | `tickets/tasks/2026-02-17_agents_bootstrap_split_and_profile_distribution_task.md` | 2026-02-17T12:23:40Z | REQUIRED |

## Active Attention Details
- DATETIME: 2026-02-17T12:23:40Z
  TYPE: PLAN
  CLAIM: Active execution is now limited to root + profile-specific AGENTS
    (`new/general/engineer/synaptic`) after removing shared default AGENTS map
    usage.
  EVIDENCE:
  - tickets/tasks/2026-02-17_agents_bootstrap_split_and_profile_distribution_task.md:1-202
  IMPACT: Map layering now matches user intent; remaining work is content
    quality/coverage review before root cutover.
  NEXT: verify profile AGENTS content completeness and identify any policy gaps.
  SWITCH_TRIGGER: user confirms profile AGENTS content is complete.
  RESUME_HIERARCHY: ticket notes -> profile AGENTS docs -> skill map entries.
  REREAD: REQUIRED

## Recently Closed Anchors
| work_item | status | owner | blocker | next | ticket | updated_at | reread |
|---|---|---|---|---|---|---|---|
| task: profile bias partition and AGENTS bootstrap decomposition | done | codex | none | none | `tickets/tasks/completed/2026-02-17_profile_bias_partition_and_agents_bootstrap_decomposition_task_completed.md` | 2026-02-17T12:01:56Z | REQUIRED |
| story: system docs creation skill quality rebuild | done | codex | none | none | `tickets/stories/completed/2026-02-17_system_docs_creation_skill_quality_rebuild_story_completed.md` | 2026-02-17T11:39:58Z | REQUIRED |
| task: src architecture skill creation protocol rebuild | done | codex | none | none | `tickets/tasks/completed/2026-02-17_src_architecture_skill_creation_protocol_rebuild_task_completed.md` | 2026-02-17T11:39:58Z | REQUIRED |
| task: src components skill creation protocol rebuild | done | codex | none | none | `tickets/tasks/completed/2026-02-17_src_components_skill_creation_protocol_rebuild_task_completed.md` | 2026-02-17T11:39:58Z | REQUIRED |
| task: tests architecture skill creation protocol rebuild | done | codex | none | none | `tickets/tasks/completed/2026-02-17_tests_architecture_skill_creation_protocol_rebuild_task_completed.md` | 2026-02-17T11:39:58Z | REQUIRED |
| task: tests components skill creation protocol rebuild | done | codex | none | none | `tickets/tasks/completed/2026-02-17_tests_components_skill_creation_protocol_rebuild_task_completed.md` | 2026-02-17T11:39:58Z | REQUIRED |
| task: root docs to profile skill folder migration | done | codex | none | none | `tickets/tasks/completed/2026-02-17_root_docs_profile_skill_folder_migration_task_completed.md` | 2026-02-17T01:17:23Z | REQUIRED |
| task: ticket root and agent default structure migration | done | codex | none | none | `tickets/tasks/completed/2026-02-17_ticket_root_and_agent_default_structure_migration_task_completed.md` | 2026-02-17T01:17:23Z | REQUIRED |
| task: root agents bootstrap directives migration | done | codex | none | none | `tickets/tasks/completed/2026-02-16_root_agents_bootstrap_directives_migration_task_completed.md` | 2026-02-16T23:20:09Z | REQUIRED |
| story: system docs unification and instruction contract | done | codex | none | none | `tickets/stories/completed/2026-02-16_system_docs_unification_and_instruction_contract_story_completed.md` | 2026-02-16T22:32:29Z | REQUIRED |
| task: system docs unification discovery and cutover plan | done | codex | none | none | `tickets/tasks/completed/2026-02-16_system_docs_unification_discovery_and_cutover_plan_task_completed.md` | 2026-02-16T22:32:29Z | REQUIRED |
