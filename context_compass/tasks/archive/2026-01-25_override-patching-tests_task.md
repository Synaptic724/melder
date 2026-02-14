# Task: Add override and mutation patching tests

## Metadata
- Task ID: TASK-2026-01-25-override-patching-tests
- Story: STORY-2026-01-25-override-mutation-fast-path
- Status: draft
- Owner:
- Priority: p2
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Add tests that validate override and mutation patching for fast-path plans.

## Scope Boundaries
- In scope:
  - Unit tests for override slot patching.
  - Unit tests for mutation patching or fallback.
- Out of scope:
  - Performance benchmarks.

## Steps / Checklist
- [ ] Add unit tests for override slot patching.
- [ ] Add tests for mutation patch map behavior.
- [ ] Add tests for fallback when patching is ineligible.

## Deliverables
- Override and mutation patching tests.

## Files / Paths Impacted
- tests/unit/melder/aether/conduit/meld/test_override_patching.py (new)

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k patch

## Risks / Rollback Notes
- Risk: tests overfit internal representation.
  Mitigation: assert behavior and output equivalence.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; override and mutation patching tests pending.
