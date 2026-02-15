Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Task: Move meld input validation to cache-miss path

## Metadata
- Task ID: TASK-2026-02-05-meld-input-validation-cache-miss
- Story: N/A
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-02-05
- Updated: 2026-02-05

## Objective
Move Conduit meld input validation into Meld so validation occurs only on cache
misses, and document any previously undocumented Meld helpers.

## Scope Boundaries
- In scope:
- Remove spell input validation from Conduit meld paths.
- Add a Meld helper to validate inputs on cache miss.
- Ensure Meld cache helper methods have rich docstrings.
- Out of scope:
- Changing public API signatures or error types.
- Adding new dependencies or refactoring unrelated logic.

## Steps / Checklist
- [x] Add a Meld input-validation helper that runs only on cache miss.
- [x] Remove duplicate validation from Conduit gated/ungated meld paths.
- [x] Add missing docstrings to Meld cache helper methods.
- [x] Record validation status.

## Deliverables
- Input validation centralized in Meld cache-miss path.
- Updated docstrings for Meld cache helpers.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/conduit/conduit.py`

## Validation
- Not run.
- Recommended commands:
  - pytest -q

## Risks / Rollback Notes
- Risk: moving validation changes log placement and raises earlier/later.
- Rollback: revert the Meld/Conduit changes and restore validation in Conduit.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Implemented validation movement into Meld cache-miss path, removed duplicate
Conduit validation, and added docstrings for cache helpers. Validation not run.

