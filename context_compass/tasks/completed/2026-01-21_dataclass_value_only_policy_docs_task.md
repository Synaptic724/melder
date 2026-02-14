- Completed: 2026-01-21
- Summary: Updated core policy docs with the value-only dataclass rule.

# Task: Document dataclass value-only policy

## Metadata
- Task ID: TASK-2026-01-21-dataclass-value-only-policy-docs
- Story: STORY-2026-01-21-dataclass-value-only-policy
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-21
- Updated: 2026-01-21

## Objective
Document the value-only dataclass rule in core policy docs and Python guidance.

## Scope Boundaries
- In scope:
  - `context_compass/AGENTS.MD`
  - `context_compass/agent_onboarding/agent/general/skills/python/banned_patterns.md`
  - `context_compass/agent_onboarding/agent/general/skills/python/init_and_ownership.md`
  - `context_compass/agent_onboarding/agent/general/skills/python/cleanup_and_disposal.md`
- Out of scope:
  - Code changes or enforcement tooling.

## Steps / Checklist
- [x] Add dataclass value-only rule to AGENTS.MD.
- [x] Add dataclass value-only rule to banned_patterns.md.
- [x] Add dataclass value-only rule to init_and_ownership.md.
- [x] Add dataclass value-only rule to cleanup_and_disposal.md.
- [x] Keep wording consistent across all policy docs.

## Deliverables
- Updated policy docs with a consistent value-only dataclass rule.

## Files / Paths Impacted
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/agent/general/skills/python/banned_patterns.md`
- `context_compass/agent_onboarding/agent/general/skills/python/init_and_ownership.md`
- `context_compass/agent_onboarding/agent/general/skills/python/cleanup_and_disposal.md`

## Validation
- Not run (documentation-only change).

## Risks / Rollback Notes
- Risk: Rule conflicts with current dataclass usage.
  - Mitigation: Document first; review usage in a separate task.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Documented the dataclass value-only rule across core policy docs with consistent
language: AGENTS.MD, banned_patterns.md, init_and_ownership.md, and
cleanup_and_disposal.md.
