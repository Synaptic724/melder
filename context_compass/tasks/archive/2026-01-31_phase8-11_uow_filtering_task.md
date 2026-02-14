# Task: Reduce Phase 8–11 UnitOfWork overhead

## Metadata
- Task ID: TASK-2026-01-31-phase8-11-uow-filtering
- Story:
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-31
- Updated: 2026-01-31

## Objective
Reduce conjure overhead by pre-filtering no-op spells in Phase 8–11 factories
so UnitOfWork objects are only created for spells that will actually build
artifacts.

## Scope Boundaries
- In scope:
  - Phase 8–11 factories in `Spellbook` (occurrence/injection/patch/execution).
  - Skip UnitOfWork creation for existing-creation spells.
  - Skip UnitOfWork creation when required upstream artifacts are missing
    (e.g., no Phase 5 blueprint attached for Phase 8).
- Out of scope:
  - Changes to phase logic inside SpellCrafter.
  - Any change to phase scheduling order or semantics.

## Steps / Checklist
- [ ] Identify artifact availability checks needed for each phase.
- [ ] Propose a minimal filter rule per factory and get approval.
- [ ] Implement filters with docstring updates.
- [ ] Add/adjust tests to ensure no regression in phase coverage.

## Deliverables
- Filtered UnitOfWork creation in Phase 8–11 factories.
- Tests covering filtered/no-op behaviors.

## Files / Paths Impacted
- `src/melder/spellbook/spellbook.py`
- `tests/unit/melder/spellbook/` (new or updated tests)

## Validation
- Not run.
- Recommended commands:
  - `pytest -q tests/unit/melder/spellbook`

## Risks / Rollback Notes
- Risk: incorrectly skipping a spell that should build artifacts.
  Mitigation: guard filters with explicit artifact checks + tests.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Ticket created to reduce Phase 8–11 UnitOfWork overhead by filtering no-op
spells and skipping UoW creation when required artifacts are missing.
