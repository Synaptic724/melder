# Task: Add tests for plan compilation

## Metadata
- Task ID: TASK-2026-01-25-plan-compilation-tests
- Story: STORY-2026-01-25-plan-compilation-phase8
- Status: draft
- Owner:
- Priority: p2
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Add unit tests that validate occurrence and arg plan compilation against known
DAG and requirement fixtures.

## Scope Boundaries
- In scope:
  - Unit tests for occurrence expansion and arg binding.
- Out of scope:
  - Runtime fast-path executor tests.

## Steps / Checklist
- [ ] Create plan compilation fixtures.
- [ ] Assert execution order and dependency indices.
- [ ] Assert contract eligibility markers.

## Deliverables
- Unit tests for plan compilation.

## Files / Paths Impacted
- tests/unit/melder/aether/conduit/meld/test_plan_compilation.py (new)

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k plan_compilation

## Risks / Rollback Notes
- Risk: tests overfit to internal layout.
  Mitigation: assert contract outcomes, not internal ordering unless required.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; plan compilation tests pending.
