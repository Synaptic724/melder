- Completed: 2026-01-21
- Summary: Expanded unit test coverage for change-control managers.

# Story: Change-Control Unit Test Expansion

## Metadata
- Story ID: STORY-2026-01-20-change-control-unit-tests
- Epic: EPIC-2026-01-20-change-control-test-expansion
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-20
- Updated: 2026-01-21

## User Narrative
As a Melder maintainer, I want deep unit coverage of change-control managers,
so that admission, embargo, and request modeling stay correct as features evolve.

## Value / MRP Alignment
Unit tests harden the core admission logic and normalize inputs before
integration layers depend on them.

## Requirements (Functional)
- Unit coverage for conflict/embargo/orchestrator/transaction manager behavior.
- Include mixed hash/key conflict checks and staged mutation updates.

## Requirements (Non-Functional)
- Deterministic tests with isolated fixtures.

## Scope Boundaries
- In scope:
  - ChangeControlManager sub-managers and request models.
  - Scope key/hash normalization, admission rejection reasons.
- Out of scope:
  - Full integration with Spellbook/Conduit flows.

## Dependencies / Related Work
- `context_compass/architecture/change_control_object_map.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-20-change-control-unit-tests - Add unit tests for managers.

## Acceptance Criteria
- Unit test targets expanded with meaningful coverage of core managers.

## Validation / Test Plan
- `python -m pytest tests/unit/melder/aether/dev_ops/change_control_manager`

## UX / API / Data Notes
- No API changes expected.

## Risks / Mitigations
- Risk: Unit tests duplicate integration coverage.
  - Mitigation: keep unit tests focused on manager behavior.

## Open Questions
- Confirm target unit test count after plan is finalized.

## Decision Log
- 2026-01-20: Create unit test expansion story.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created to expand unit tests for change-control manager stack.
