- Completed: 2026-01-21
- Summary: Documented public interface exposure policy guidance.

# Story: Document public interface exposure policy

## Metadata
- Story ID: STORY-2026-01-21-interface-public-contract-policy
- Epic: EPIC-2026-01-21-interface-public-contract-policy
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-21
- Updated: 2026-01-21

## User Narrative
As a maintainer, I want explicit guidance that interfaces may be exposed in
public APIs when they mirror concrete classes, so API expectations are clear.

## Value / MRP Alignment
Clear API contracts reduce confusion and make public expectations explicit.

## Requirements (Functional)
- Add policy note to AGENTS.MD.
- Add interface exposure guidance to interfaces.md.

## Requirements (Non-Functional)
- Use existing docs only.
- Keep wording consistent across docs.

## Scope Boundaries
- In scope:
  - `context_compass/AGENTS.MD`
  - `context_compass/agent_onboarding/agent/general/skills/python/interfaces.md`
- Out of scope:
  - Code changes.

## Dependencies / Related Work
- Task: TASK-2026-01-21-interface-public-contract-policy-docs

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-21-interface-public-contract-policy-docs - Update policy docs.

## Acceptance Criteria
- Policy note exists in AGENTS.MD and interfaces guidance.
- Interfaces are explicitly allowed in public APIs when they mirror concrete classes.

## Validation / Test Plan
- Not applicable (documentation-only change).

## UX / API / Data Notes
- None.

## Risks / Mitigations
- Risk: Misinterpretation that interfaces are always required.
  - Mitigation: State that exposure is allowed when they mirror concrete classes.

## Open Questions
- None.

## Decision Log
- 2026-01-21: Document public interface exposure policy.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created to document that public APIs may expose interfaces when they
mirror concrete runtime classes.
