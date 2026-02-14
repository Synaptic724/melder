- Completed: 2026-01-21
- Summary: Documented the value-only dataclass rule across core policy docs.

# Story: Document dataclass value-only policy

## Metadata
- Story ID: STORY-2026-01-21-dataclass-value-only-policy
- Epic: EPIC-2026-01-21-dataclass-value-only-policy
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-21
- Updated: 2026-01-21

## User Narrative
As a maintainer, I want a clear, consistent rule that dataclasses are value-only
so that object ownership and cleanup are never hidden inside dataclasses.

## Value / MRP Alignment
This policy keeps lifecycle responsibilities explicit and prevents hidden
resource ownership inside dataclasses.

## Requirements (Functional)
- Add the value-only dataclass rule to AGENTS.MD.
- Add the value-only dataclass rule to Python policy docs.

## Requirements (Non-Functional)
- Do not create new policy documents.
- Keep language consistent across all updated files.

## Scope Boundaries
- In scope:
  - `context_compass/AGENTS.MD`
  - `context_compass/agent_onboarding/agent/general/skills/python/banned_patterns.md`
  - `context_compass/agent_onboarding/agent/general/skills/python/init_and_ownership.md`
  - `context_compass/agent_onboarding/agent/general/skills/python/cleanup_and_disposal.md`
- Out of scope:
  - Code changes or enforcement tooling.

## Dependencies / Related Work
- Task: TASK-2026-01-21-dataclass-value-only-policy-docs

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-21-dataclass-value-only-policy-docs - Update policy docs.

## Acceptance Criteria
- Dataclass value-only rule is present in AGENTS.MD and Python policy docs.
- Rule wording is consistent and explicit about allowed types and disallowed
  object instances.

## Validation / Test Plan
- Not applicable (documentation-only change).

## UX / API / Data Notes
- None.

## Risks / Mitigations
- Risk: Rule conflicts with existing dataclass usage.
  - Mitigation: Document first, then review usage in a separate task.

## Open Questions
- None.

## Decision Log
- 2026-01-21: Document the value-only dataclass policy in core docs.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created to document the dataclass value-only rule in core policy docs.
