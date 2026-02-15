- Completed: 2026-01-17
- Summary: Added scan_bind mock modules and integration tests for scan, re-export, duplicates, and re-import collisions.
- Summary: Validation not run.

# Task: Add scan_bind integration tests with mock modules

## Metadata
- Task ID: TASK-2026-01-17-melder-scan-bind-integration-tests
- Story: STORY-2026-01-17-melder-architecture-components-docs
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-17
- Updated: 2026-01-17

## Objective
Add integration tests for scan_bind and module scanning using mock modules to
cover duplicates, re-import, and re-export behavior.

## Scope Boundaries
- In scope:
  - Mock modules under `tests/mocks/spellbook/` for scan_bind scenarios.
  - Integration tests for Spellbook.scan and Conduit.scan.
  - Coverage for duplicate bindings, re-exports, and repeated scans/re-imports.
- Out of scope:
  - Production code changes.
  - Package traversal scanning.

## Steps / Checklist
- [x] Create scan_bind mock modules for core, duplicate, and re-export cases.
- [x] Add integration tests for Spellbook.scan and Conduit.scan.
- [x] Validate duplicates, re-export rejection, and re-import/re-scan collisions.

## Deliverables
- `tests/mocks/spellbook/scan_bind_module_core.py`
- `tests/mocks/spellbook/scan_bind_module_duplicate.py`
- `tests/mocks/spellbook/scan_bind_module_reexport.py`
- `tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py`

## Files / Paths Impacted
- `tests/mocks/spellbook/`
- `tests/integration/melder/spellbook/`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py`

## Risks / Rollback Notes
- Risk: Module reloads can be sensitive to shared global state; isolate with Aether reset.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded

## Context / Handoff Summary
- Added scan_bind mock modules and integration tests for scan, re-export,
  duplicates, and re-import collisions. Validation not run.
