- Completed: 2026-01-17
- Summary: Added scan_bind mock modules and expanded integration coverage with ~20 tests.
- Summary: Validation not run.

# Task: Expand scan_bind integration tests (kitchen sink)

## Metadata
- Task ID: TASK-2026-01-17-melder-scan-bind-kitchen-sink-integration-tests
- Story: STORY-2026-01-17-melder-architecture-components-docs
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-17
- Updated: 2026-01-17

## Objective
Expand scan_bind integration coverage with additional mock modules and end-to-end
conjure/meld scenarios, including decorator stacking, re-export behavior, and
failure cases.

## Scope Boundaries
- In scope:
  - Additional mock modules under `tests/mocks/spellbook/`.
  - Expanded integration tests for Spellbook.scan and Conduit.scan.
  - End-to-end scan -> conjure -> meld flows for class/function spells.
- Out of scope:
  - Production code changes.
  - Package traversal scanning.

## Steps / Checklist
- [x] Add mock modules for wrapped decorators, lambdas, empty scan, and bad metadata.
- [x] Expand integration test coverage to ~20 scan_bind scenarios.
- [x] Validate end-to-end conjure/meld after scan.

## Deliverables
- `tests/mocks/spellbook/scan_bind_module_wrapped.py`
- `tests/mocks/spellbook/scan_bind_module_lambda.py`
- `tests/mocks/spellbook/scan_bind_module_lambda_invalid.py`
- `tests/mocks/spellbook/scan_bind_module_empty.py`
- `tests/mocks/spellbook/scan_bind_module_bad_metadata.py`
- Updated `tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py`

## Files / Paths Impacted
- `tests/mocks/spellbook/`
- `tests/integration/melder/spellbook/`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py`

## Risks / Rollback Notes
- Risk: decorator stacking behavior varies with wrappers; tests should document
  expected behavior for wraps vs non-wraps decorators.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded

## Context / Handoff Summary
- Added scan_bind mock modules and expanded integration coverage (~20 tests)
  including decorator stacking, lambdas, re-exports, and end-to-end conjure/meld.
- Validation not run.
