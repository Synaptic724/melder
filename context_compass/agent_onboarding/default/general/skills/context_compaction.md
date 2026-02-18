

# Context Compaction Policy

## Purpose
Ensure continuity and minimize lost context when a session is compacted or handed off.

## Durable truth vs compaction cache
- Repository artifacts are the durable source of truth for decisions and evidence.
- The compaction summary is a volatile cache used to carry P0/P1 operational truths across a reset.
- The cache is useful but **not authoritative** until verified via Diff-Onboarding.

## Compaction summary rules (non-negotiable)
- Empty compaction summaries are forbidden.
- Follow `CONTEXT_COMPACTION.md` summary structure exactly:
  - resume pointers (role, tickets, next actions)
  - P0/P1 retention set (atomic claims + evidence pointers)
  - Diff-Onboarding hook (`cycle_id`, board pointer)
- Do NOT write narrative replay.
- Do NOT include secrets.

## Required review set

Core review set (ALWAYS required) — review these files in order:
- `AGENTS.MD`
- `CONTEXT_COMPACTION.md`
- `agent_onboarding/default/general/skills/execution_contract.md`
- `config/context_compass_config.yaml`
- `context_compass/SKILLS.MD`
- resolved role `SKILLS.MD` chain (parent-first; the SKILLS files themselves)
- `agent_onboarding/default/general/skills/compaction_requirements.md`
- `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
- `agent_onboarding/default/general/skills/workflow.md`
- `attention_board.md`
- Active epic/story/task tickets in `tickets/epics/`, `tickets/stories/`, `tickets/tasks/`
- `compacting_differential_board.md` (review open rows only)

Conditional review set (ONLY when triggered):
- `artifact_board.md` (when active tickets include artifacts or artifact disposition changes)
- `artifacts/README.md` (when artifact lifecycle protocol is active)
- System-context / architecture docs are **ON-DEMAND** and MUST be reviewed only when:
  - the active ticket requires architecture/components/tests documentation work, OR
  - this session modified `system_docs/*`, OR
  - the handoff requires making architecture claims in the next step.
  If triggered, review:
  - `agent_onboarding/default/engineer/skills/src_architecture_instructions.md`
  - `agent_onboarding/default/engineer/skills/tests_architecture_instructions.md`
  - `agent_onboarding/default/engineer/skills/src_components_instructions.md`
  - `agent_onboarding/default/engineer/skills/tests_components_instructions.md`
  - `system_docs/src_architecture.md`
  - `system_docs/tests_architecture.md`
  - `system_docs/src_components.md`
  - `system_docs/tests_components.md`

Read discipline (non-negotiable)
- Review-set document reads must be manual per file path.
- Loop-based/batch document-reading commands are forbidden (for/foreach/while
  loops, xargs-style runners, or piped file-list iterators).
- For files over 500 LOC, read in explicit 500-line chunks in sequential order.

## Required updates
- Update `attention_board.md` during work so active items, status, blockers, and next actions stay current.
- Keep ticket `## Notes` current with evidence pointers.
- Maintain a small P0/P1 retention set so the compaction cache summary can stay compact while preserving operational truth.

References
- `CONTEXT_COMPACTION.md`
- `agent_onboarding/default/general/skills/compaction_requirements.md`
- `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
- `context_compass/compacting_differential_board.md`
