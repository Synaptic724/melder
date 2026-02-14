- Completed: 2026-01-17
- Summary: Aligned scan_bind integration tests with scan return IDs and explicit bindings.
- Summary: Added scan-after-conjure coverage for Aether registration (validation not run).

# Task: Fix scan_bind integration tests for conjure/meld semantics

## Metadata
- Task ID: TASK-2026-01-17-melder-scan-bind-integration-test-fixes
- Story: STORY-2026-01-17-melder-architecture-components-docs
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-17
- Updated: 2026-01-17

## Objective
Align scan_bind integration tests with Spellbook/Aether registration timing and
explicit spellframe/binding resolution semantics.

## Scope Boundaries
- In scope:
  - Adjust integration tests to use scan return IDs or explicit frame/binding.
  - Add coverage for scan after conjure registering in Aether.
- Out of scope:
  - Production code changes.

## Steps / Checklist
- [x] Replace pre-conjure inspect_spell assumptions with scan IDs.
- [x] Update meld calls to use spellframe/binding or spell_id.
- [x] Add tests for scan after conjure (spellbook + conduit).

## Deliverables
- Updated `tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py`

## Files / Paths Impacted
- `tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py`

## Risks / Rollback Notes
- Risk: assumptions about scan order; use scan return order to drive checks.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded

## Context / Handoff Summary
- Updated scan_bind integration tests to use scan return IDs and explicit
  frame/binding keys. Added scan-after-conjure coverage for Aether registration.
- Validation not run.
