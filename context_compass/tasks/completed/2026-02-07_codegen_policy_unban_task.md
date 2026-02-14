Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Task: Allow eval/exec/compile for agent work

## Metadata
- Task ID: TASK-2026-02-07-codegen-policy-unban
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-02-07
- Updated: 2026-02-07

## Objective
Update policy docs to allow eval/exec/compile for agent work without an explicit
permission gate.

## Scope Boundaries
- In scope:
  - Update AGENTS.md banned pattern rules to allow eval/exec/compile.
  - Update python banned_patterns skill to match.
- Out of scope:
  - Any code changes.
  - Any new permission gates or runtime checks.

## Steps / Checklist
- [x] Update `context_compass/AGENTS.md` banned pattern section.
- [x] Update `context_compass/agent_onboarding/agent/general/skills/python/banned_patterns.md`.
- [x] Record validation status (docs-only).

## Deliverables
- Updated `context_compass/AGENTS.md`
- Updated `context_compass/agent_onboarding/agent/general/skills/python/banned_patterns.md`

## Files / Paths Impacted
- `context_compass/tasks/2026-02-07_codegen_policy_unban_task.md`
- `context_compass/AGENTS.md`
- `context_compass/agent_onboarding/agent/general/skills/python/banned_patterns.md`

## Validation
- Not run (documentation only).

## Risks / Rollback Notes
- Risk: Allowing eval/exec/compile reduces auditability of generated code.
  Mitigation: Documented policy change and explicit task record.
- Rollback: Revert policy changes in AGENTS.md and banned_patterns.md.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Policy docs updated to allow eval/exec/compile for agent work. Awaiting user
acceptance confirmation.

