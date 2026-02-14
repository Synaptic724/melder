- Completed: 2026-01-21
- Summary: Documented the TYPE_CHECKING ban and interface-preference guidance.

# Story: Ban TYPE_CHECKING in policy docs

## Metadata
- Story ID: STORY-2026-01-21-ban-type-checking-policy
- Epic: EPIC-2026-01-21-ban-type-checking-policy
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-21
- Updated: 2026-01-21

## User Narrative
As a maintainer, I want TYPE_CHECKING banned in policy docs so typing guidance
stays explicit and interfaces are the preferred alternative.

## Value / MRP Alignment
This keeps type behavior predictable and avoids hidden runtime dependency
patterns.

## Requirements (Functional)
- Ban TYPE_CHECKING in AGENTS.MD and Python policy docs.
- Call out interfaces as the preferred alternative.

## Requirements (Non-Functional)
- Use existing docs only; no new policy files.
- Keep language consistent across docs.

## Scope Boundaries
- In scope:
  - `context_compass/AGENTS.MD`
  - `context_compass/agent_onboarding/agent/general/skills/python/banned_patterns.md`
  - `context_compass/agent_onboarding/agent/general/skills/python/typing.md`
  - `context_compass/agent_onboarding/agent/general/skills/python/interfaces.md`
- Out of scope:
  - Code changes.

## Dependencies / Related Work
- Task: TASK-2026-01-21-ban-type-checking-policy-docs

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-21-ban-type-checking-policy-docs - Update policy docs.

## Acceptance Criteria
- TYPE_CHECKING is explicitly banned in policy docs.
- Interfaces are positioned as the preferred alternative.

## Validation / Test Plan
- Not applicable (documentation-only change).

## UX / API / Data Notes
- None.

## Risks / Mitigations
- Risk: Conflicts with existing usage.
  - Mitigation: document first, inventory later.

## Open Questions
- None.

## Decision Log
- 2026-01-21: Ban TYPE_CHECKING in policy docs.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created to ban TYPE_CHECKING in policy docs and point to interfaces as
the preferred alternative.
