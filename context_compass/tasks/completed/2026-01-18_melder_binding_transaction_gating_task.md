# Task: Enforce binding transactions for bind/scan

## Metadata
- Task ID: TASK-2026-01-18-melder-binding-transaction-gating
- Story: STORY-2026-01-18-melder-post-conjure-binding
- Status: complete
- Owner:
- Priority: p1
- Created: 2026-01-18
- Updated: 2026-01-18

## Objective
Require an explicit binding transaction for bind/scan after conjure, with begin/end methods on Spellbook and Conduit.

## Scope Boundaries
- In scope: Spellbook binding transaction state, begin/end methods, bind/scan gating, conduit facades.
- Out of scope: revalidation and dependency tracking changes.

## Steps / Checklist
- [x] Add binding transaction state to Spellbook (default active pre-conjure, inactive after conjure).
- [x] Implement Spellbook begin/end methods with clear error messages on invalid usage.
- [x] Gate Spellbook.bind and Spellbook.scan on active transaction.
- [x] Add Conduit wrappers that enforce normal conduit state.
- [x] Update interface protocols for Spellbook and Conduit.

## Deliverables
- Binding transaction gating in Spellbook and Conduit.
- Updated protocol definitions.

## Files / Paths Impacted
- `src/melder/spellbook/spellbook.py`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/utilities/interfaces/interfaces.py`

## Validation
- User reported tests passing after updates.
- Recommended commands:
  - `pytest tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py`

## Risks / Rollback Notes
- Risk: Existing code that binds after conjure will fail without a transaction. Mitigation: update call sites or document the new requirement.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded

## Context / Handoff Summary
- Task drafted for binding transaction gating and conduit wrappers.
