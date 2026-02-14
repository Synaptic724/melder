- Completed: 2026-01-21
- Summary: Documented the interface public-contract allowance in policy docs.

# Task: Document interface public-contract policy

## Metadata
- Task ID: TASK-2026-01-21-interface-public-contract-policy-docs
- Story: STORY-2026-01-21-interface-public-contract-policy
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-21
- Updated: 2026-01-21

## Objective
Document that interfaces may be exposed in public APIs when they mirror
concrete classes and represent the real runtime objects.

## Scope Boundaries
- In scope:
  - `context_compass/AGENTS.MD`
  - `context_compass/agent_onboarding/agent/general/skills/python/interfaces.md`
- Out of scope:
  - Code changes.

## Steps / Checklist
- [x] Add interface exposure policy note to AGENTS.MD.
- [x] Add interface exposure policy note to interfaces.md.
- [x] Keep wording consistent across docs.

## Deliverables
- Updated policy docs with the interface public-contract allowance.

## Files / Paths Impacted
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/agent/general/skills/python/interfaces.md`

## Validation
- Not run (documentation-only change).

## Risks / Rollback Notes
- Risk: Conflicts with interface leakage refactor requests.
  - Mitigation: Make the allowance explicit and scoped.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Documented the interface public-contract allowance in AGENTS.MD and interfaces.md.
