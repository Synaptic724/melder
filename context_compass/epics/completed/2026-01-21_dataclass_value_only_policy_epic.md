- Completed: 2026-01-21
- Summary: Established the value-only dataclass policy in core documentation.

# Epic: Dataclass Value-Only Policy

## Metadata
- Epic ID: EPIC-2026-01-21-dataclass-value-only-policy
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-21
- Updated: 2026-01-21
- Target Window: 2026-Q1
- Related Program/Initiative: Documentation policy

## Problem / Opportunity
Dataclass usage needs a clear, consistent rule: dataclasses must be value-only
and must not hold object instances or resources. This requirement must be
explicit in core policy docs to avoid ambiguity.

## MRP Alignment (Most Reasonable Product)
Clear ownership and cleanup boundaries are foundational. Value-only dataclasses
reduce hidden lifecycle risks and keep contracts explicit.

## Goals (Outcomes)
- Document the value-only dataclass rule in primary policy docs.
- Make the rule discoverable in Python-specific guidance.
- Avoid creating new policy documents; update existing sources of truth.

## Non-Goals (Explicit Exclusions)
- Refactoring code or converting existing dataclasses.
- Introducing new tooling or enforcement scripts.

## Scope Boundaries
- In scope:
  - Policy updates in `context_compass/AGENTS.MD`.
  - Python policy updates in
    `context_compass/agent_onboarding/agent/general/skills/python/`.
- Out of scope:
  - Changes to production code or tests.

## Success Metrics
- Rule is present in core policy docs and Python guidance.
- Rule is consistent across updated documents.

## Requirements (Functional + Non-Functional)
- Dataclasses may contain only value types (None, bool, int, float, str).
- Dataclasses must not store object instances or resources.
- If a data model holds objects or requires cleanup, use a normal class with
  cleanup semantics.

## Constraints / Assumptions
- Inactive mode: no git commands.
- Use existing docs; do not add new policy files.

## Dependencies / External References
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/agent/general/skills/python/banned_patterns.md`
- `context_compass/agent_onboarding/agent/general/skills/python/init_and_ownership.md`
- `context_compass/agent_onboarding/agent/general/skills/python/cleanup_and_disposal.md`

## Milestones (Track Progress)
- [x] Milestone 1: Tickets created and approved.
- [x] Milestone 2: Policy docs updated with value-only dataclass rule.

## Stories (Required to Complete)
- [x] Story: STORY-2026-01-21-dataclass-value-only-policy - Update policy docs.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-01-21-dataclass-value-only-policy

## Acceptance Criteria (Epic Done)
- Dataclass value-only rule is documented in AGENTS.MD and Python policy docs.
- Rule language is consistent across all updated documents.

## Risks / Mitigations
- Risk: Existing code may violate the rule.
  - Mitigation: Treat this as documentation-first; follow-up review separately.

## Validation / Test Approach
- Not applicable (documentation-only change).

## Rollout / Adoption Plan
- Update docs, then reference the rule in future code reviews and tickets.

## Open Questions
- None.

## Decision Log
- 2026-01-21: Document dataclass value-only policy in core docs.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic created to document the dataclass value-only rule in core policy docs.
