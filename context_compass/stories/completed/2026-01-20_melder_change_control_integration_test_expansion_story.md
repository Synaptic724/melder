- Completed: 2026-01-21
- Summary: Expanded integration test coverage for change-control flows.

# Story: Change-Control Integration Test Expansion

## Metadata
- Story ID: STORY-2026-01-20-change-control-integration-tests
- Epic: EPIC-2026-01-20-change-control-test-expansion
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-20
- Updated: 2026-01-21

## User Narrative
As a Melder maintainer, I want integration coverage for dynamic change-control
flows, so that end-to-end transactions, linking, and revalidation are safe in
realistic scenarios.

## Value / MRP Alignment
Integration tests exercise real flows across Spellbook, Conduit, and change-control,
confirming the system behaves deterministically under realistic usage.

## Requirements (Functional)
- Cover end-to-end bind/link/contract flows under change-control gating.
- Validate staged metadata updates and revalidation in real conduits.

## Requirements (Non-Functional)
- Avoid flaky concurrency unless explicitly required by the scenario.

## Scope Boundaries
- In scope:
  - Integration tests under `tests/integration/melder`.
  - Change-control admission behavior across multiple conduits.
- Out of scope:
  - Long-running stress tests beyond current target.

## Dependencies / Related Work
- `context_compass/architecture/change_control_object_map.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-20-change-control-integration-tests - Add integration tests for change-control flows.

## Acceptance Criteria
- Integration suite covers key change-control flows with clear assertions.

## Validation / Test Plan
- `python -m pytest tests/integration/melder`

## UX / API / Data Notes
- No API changes expected.

## Risks / Mitigations
- Risk: Integration tests increase runtime.
  - Mitigation: use targeted fixtures and reuse spell graphs.

## Open Questions
- Confirm integration test count allocation in the plan.

## Decision Log
- 2026-01-20: Create integration test expansion story.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created to expand integration coverage for change-control flows.
