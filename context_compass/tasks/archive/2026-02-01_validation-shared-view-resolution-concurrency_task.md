# Task: Fix validation shared-view regressions and resolution concurrency cleanup

## Metadata
- Task ID: TASK-2026-02-01-validation-shared-view-resolution-concurrency
- Story: n/a
- Status: draft
- Owner: codex
- Priority: p1
- Created: 2026-02-01
- Updated: 2026-02-01

## Objective
Restore shared-view validation API expected by tests and prevent concurrent resolution phases from cleaning OccurrencePlan artifacts mid-build.

## Scope Boundaries
- In scope:
  - Reintroduce SpellValidationContext.shared_view support and SpellValidationSystem.prepare_shared_view/clear_shared_view behavior expected by tests.
  - Add serialization/guarding so concurrent conduit resolution phases do not clean Phase 8/11 artifacts during active execution-plan builds.
- Out of scope:
  - Behavioral changes unrelated to validation context or resolution-phase concurrency.
  - Refactors or renames.
  - New dependencies.

## Steps / Checklist
- [ ] Inspect validation context/system tests for expected API surface.
- [ ] Restore shared-view plumbing in validation context/system.
- [ ] Identify the earliest safe serialization point for conduit-scoped resolution phases.
- [ ] Implement minimal locking/guarding and verify artifact lifecycle expectations.
- [ ] Re-read touched docstrings for accuracy.

## Deliverables
- Validation API compatibility restored (shared_view + prepare_shared_view/clear_shared_view).
- Conduit resolution phases serialized to avoid OccurrencePlan cleanup races.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/validation/spell_validation_context.py
- src/melder/spellbook/spell_crafter/validation/validation_system.py
- src/melder/spellbook/spellbook.py
- tests/unit/melder/spellbook/spell_crafter/validation/test_spell_validation_context.py
- tests/unit/melder/spellbook/spell_crafter/validation/test_validation_system.py
- tests/integration/melder/conduit/test_conduit_integration_concurrency.py (expected to pass; no edits unless needed)

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/spellbook/spell_crafter/validation/test_spell_validation_context.py
  - pytest tests/unit/melder/spellbook/spell_crafter/validation/test_validation_system.py
  - pytest tests/integration/melder/conduit/test_conduit_integration_concurrency.py

## Risks / Rollback Notes
- Risk: Over-serialization of resolution phases could reduce concurrency throughput.
- Rollback: Revert lock/guard changes and shared-view API additions.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Reported failures: OccurrencePlan cleaned during concurrent conduit resolution; validation tests expect shared_view and prepare_shared_view. Need minimal, scoped fixes.
