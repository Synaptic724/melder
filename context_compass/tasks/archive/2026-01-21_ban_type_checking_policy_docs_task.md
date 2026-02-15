- Completed: 2026-01-21
- Summary: Banned TYPE_CHECKING in policy docs and emphasized interfaces as the alternative.

# Task: Ban TYPE_CHECKING in policy docs

## Metadata
- Task ID: TASK-2026-01-21-ban-type-checking-policy-docs
- Story: STORY-2026-01-21-ban-type-checking-policy
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-21
- Updated: 2026-01-21

## Objective
Ban TYPE_CHECKING in policy docs and document interfaces as the preferred
alternative.

## Scope Boundaries
- In scope:
  - `context_compass/AGENTS.MD`
  - `context_compass/agent_onboarding/agent/general/skills/python/banned_patterns.md`
  - `context_compass/agent_onboarding/agent/general/skills/python/typing.md`
  - `context_compass/agent_onboarding/agent/general/skills/python/interfaces.md`
- Out of scope:
  - Code changes.

## Steps / Checklist
- [x] Add TYPE_CHECKING ban to AGENTS.MD.
- [x] Add TYPE_CHECKING ban to banned_patterns.md.
- [x] Add TYPE_CHECKING ban guidance to typing.md.
- [x] Add interface-preference guidance to interfaces.md.
- [x] Keep wording consistent across docs.

## Deliverables
- Updated policy docs with a consistent TYPE_CHECKING ban.

## Files / Paths Impacted
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/agent/general/skills/python/banned_patterns.md`
- `context_compass/agent_onboarding/agent/general/skills/python/typing.md`
- `context_compass/agent_onboarding/agent/general/skills/python/interfaces.md`

## Validation
- Not run (documentation-only change).

## Risks / Rollback Notes
- Risk: Existing code uses TYPE_CHECKING.
  - Mitigation: document first; inventory usage separately.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Documented the TYPE_CHECKING ban across core policy docs and emphasized
interfaces as the preferred alternative.
