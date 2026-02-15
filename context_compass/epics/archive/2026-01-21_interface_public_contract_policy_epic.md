- Completed: 2026-01-21
- Summary: Completed interface public-contract policy documentation.

# Epic: Interface Public-Contract Policy

## Metadata
- Epic ID: EPIC-2026-01-21-interface-public-contract-policy
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-21
- Updated: 2026-01-21
- Target Window: 2026-Q1
- Related Program/Initiative: Documentation policy

## Problem / Opportunity
We need a clear policy stating that interfaces may be exposed in public APIs
when they mirror concrete runtime classes. This prevents ambiguity about
whether interface exposure is allowed.

## MRP Alignment (Most Reasonable Product)
Explicit contracts reduce confusion and make API expectations clear.

## Goals (Outcomes)
- Document that interfaces are allowed in public-facing signatures when they
  mirror concrete classes.
- Require that interface contracts stay in lockstep with the concrete class.

## Non-Goals (Explicit Exclusions)
- Refactoring code or changing public APIs.
- Introducing new tooling or enforcement.

## Scope Boundaries
- In scope:
  - Policy updates in `context_compass/AGENTS.MD`.
  - Python guidance updates in
    `context_compass/agent_onboarding/agent/general/skills/python/interfaces.md`.
- Out of scope:
  - Production code changes.

## Success Metrics
- Policy is documented in core docs with consistent wording.

## Requirements (Functional + Non-Functional)
- If an interface is exposed, it must mirror the concrete class.
- Public API must return the concrete runtime object implementing the interface.

## Constraints / Assumptions
- Inactive mode: no git commands.
- Update existing docs only.

## Dependencies / External References
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/agent/general/skills/python/interfaces.md`

## Milestones (Track Progress)
- [x] Milestone 1: Tickets created and approved.
- [x] Milestone 2: Policy docs updated.

## Stories (Required to Complete)
- [x] Story: STORY-2026-01-21-interface-public-contract-policy - Update policy docs.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-01-21-interface-public-contract-policy

## Acceptance Criteria (Epic Done)
- Policy note exists in AGENTS.MD and interfaces guidance.
- Wording is consistent and explicit.

## Risks / Mitigations
- Risk: Conflicts with earlier interface-leak refactor ideas.
  - Mitigation: Make the allowance explicit and scoped.

## Validation / Test Approach
- Not applicable (documentation-only change).

## Rollout / Adoption Plan
- Update docs and follow the rule in future reviews.

## Open Questions
- None.

## Decision Log
- 2026-01-21: Allow public interface exposure when interfaces mirror concrete classes.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic created to document that interfaces may be exposed publicly when they
mirror the concrete runtime classes they represent.
