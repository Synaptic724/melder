# Task: Update Meld cleanup and docstrings for id maps

- Completed: 2026-01-25
- Summary: Cleanup now explicitly clears spell_id map references and docstrings
  describe map usage in `src/melder/aether/conduit/meld/meld.py`.

## Metadata
- Task ID: TASK-2026-01-25-meld-id-map-cleanup-docs
- Story: STORY-2026-01-25-meld-spell-id-lookup
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Ensure Meld cleanup and docstrings reflect new spell_id map references.

## Scope Boundaries
- In scope:
  - Cleanup nulling for new map references.
  - Docstring updates for touched methods.
- Out of scope:
  - Behavior changes outside spell_id resolution.

## Steps / Checklist
- [x] Update Meld cleanup to clear spell_id map references.
- [x] Update docstrings for `__init__`, `cleanup`, and `_resolve_spell_by_id`.

## Deliverables
- Updated cleanup and docstrings for Meld id map usage.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/aether/conduit/meld -q`

## Risks / Rollback Notes
- Risk: cleanup omissions cause lingering references.
  Rollback: null all new fields explicitly.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Meld cleanup explicitly clears spell_id map references and docstrings now
  describe owned/contracted map usage in
  `src/melder/aether/conduit/meld/meld.py`.
- Acceptance confirmed by user.
