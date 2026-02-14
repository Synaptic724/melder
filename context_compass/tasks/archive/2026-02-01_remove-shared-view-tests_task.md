# Task: Remove shared-view expectations from validation tests

## Metadata
- Task ID: TASK-2026-02-01-remove-shared-view-tests
- Story: n/a
- Status: draft
- Owner: codex
- Priority: p1
- Created: 2026-02-01
- Updated: 2026-02-01

## Objective
Align validation unit tests with current code that no longer exposes shared_view or prepare_shared_view/clear_shared_view.

## Scope Boundaries
- In scope:
  - Update validation context/system unit tests to remove shared_view parameters/assertions.
  - Update local test stubs used by those tests.
- Out of scope:
  - Production code changes.
  - Concurrency or resolution-phase behavior.
  - Refactors or renames.

## Steps / Checklist
- [ ] Update SpellValidationContext tests to stop passing shared_view.
- [ ] Update validation system tests/stubs to remove shared_view expectations.
- [ ] Re-read touched docstrings for accuracy.

## Deliverables
- Tests no longer expect shared_view or prepare_shared_view APIs.

## Files / Paths Impacted
- tests/unit/melder/spellbook/spell_crafter/validation/test_spell_validation_context.py
- tests/unit/melder/spellbook/spell_crafter/validation/test_validation_system.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/spellbook/spell_crafter/validation/test_spell_validation_context.py
  - pytest tests/unit/melder/spellbook/spell_crafter/validation/test_validation_system.py

## Risks / Rollback Notes
- Risk: If shared_view is restored later, tests will need re-adding.
- Rollback: revert test edits only.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
User requested fixing shared_view test failures after rollback; scope is unit test updates only.
