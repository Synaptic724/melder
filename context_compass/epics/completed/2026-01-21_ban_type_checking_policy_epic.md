- Completed: 2026-01-21
- Summary: Completed the TYPE_CHECKING ban policy documentation.

# Epic: Ban TYPE_CHECKING Pattern

## Metadata
- Epic ID: EPIC-2026-01-21-ban-type-checking-policy
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-21
- Updated: 2026-01-21
- Target Window: 2026-Q1
- Related Program/Initiative: Documentation policy

## Problem / Opportunity
`typing.TYPE_CHECKING` is being used as a workaround for dependency cycles and
type-hint imports. This repo prefers explicit interfaces to avoid hidden
runtime import behavior. The pattern should be banned in core policies.

## MRP Alignment (Most Reasonable Product)
Clear, enforceable typing rules reduce ambiguity and keep runtime behavior
explicit and predictable.

## Goals (Outcomes)
- Add a ban on TYPE_CHECKING in core policy docs.
- Clarify that interfaces are the preferred alternative.

## Non-Goals (Explicit Exclusions)
- Changing existing code or refactoring imports.
- Introducing tooling or automated enforcement.

## Scope Boundaries
- In scope:
  - Policy updates in `context_compass/AGENTS.MD`.
  - Python policy updates in `context_compass/agent_onboarding/agent/general/skills/python/`.
- Out of scope:
  - Production code changes.

## Success Metrics
- TYPE_CHECKING is explicitly banned in policy docs.
- Guidance points engineers to interfaces instead.

## Requirements (Functional + Non-Functional)
- Ban `typing.TYPE_CHECKING` in policy docs.
- Recommend interfaces for abstraction and dependency control.
- Keep language consistent and concise.

## Constraints / Assumptions
- Inactive mode: no git commands.
- Update existing docs only.

## Dependencies / External References
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/agent/general/skills/python/banned_patterns.md`
- `context_compass/agent_onboarding/agent/general/skills/python/typing.md`
- `context_compass/agent_onboarding/agent/general/skills/python/interfaces.md`

## Milestones (Track Progress)
- [x] Milestone 1: Tickets created and approved.
- [x] Milestone 2: Policy docs updated with TYPE_CHECKING ban.

## Stories (Required to Complete)
- [x] Story: STORY-2026-01-21-ban-type-checking-policy - Update policy docs.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-01-21-ban-type-checking-policy

## Acceptance Criteria (Epic Done)
- TYPE_CHECKING is banned in AGENTS.MD and Python policy docs.
- Interfaces are called out as the preferred alternative.

## Risks / Mitigations
- Risk: Existing code uses TYPE_CHECKING.
  - Mitigation: document first; follow-up inventory separately.

## Validation / Test Approach
- Not applicable (documentation-only change).

## Rollout / Adoption Plan
- Update docs and use the rule in future reviews and tickets.

## Open Questions
- None.

## Decision Log
- 2026-01-21: Ban TYPE_CHECKING in policy docs.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic created to ban TYPE_CHECKING usage and reinforce interfaces as the
preferred alternative in core policy docs.
