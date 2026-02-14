- Completed: 2026-01-17
- Summary: Added scan_bind decorator + Scan module scanner with Spellbook/Conduit scan facades.
- Summary: Updated interfaces/components docs and added scan binding tests (validation not run).

# Task: Add scan_bind decorator and module scan binding

## Metadata
- Task ID: TASK-2026-01-17-melder-scan-bind-module
- Story: STORY-2026-01-17-melder-architecture-components-docs
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-17
- Updated: 2026-01-17

## Objective
Introduce a `scan_bind` decorator that marks spell targets with metadata and a
`Spellbook.scan(module)` API (plus Conduit facade) that binds those targets by
scanning a single, user-supplied module (no package traversal), reusing existing
bind validation rules.

## Scope Boundaries
- In scope:
  - New `src/melder/spellbook/bind/scan.py` with decorator + scan helpers.
  - Spellbook facade (`scan`) that binds decorated targets in a module.
  - Conduit facade (`scan`) that delegates to Spellbook.
  - Tests for decorator metadata + scan binding + duplicate handling.
- Out of scope:
  - Package tree scanning.
  - Import-time binding side effects.
  - `__*.json` metadata files.

## Open Questions
- Answered: `scan_bind` requires explicit `existence` and `permissions` (no defaults).
- Answered: Duplicate bindings throw via Spellbook.bind (no dedupe/skip).
- Answered: Re-exports are rejected (`obj.__module__` must match scanned module).
- Answered: Conduit facade is allowed after conjure.

## Steps / Checklist
- [x] Finalize decorator signature (explicit `existence` + `permissions`).
- [x] Implement `scan_bind` decorator to attach metadata marker.
- [x] Implement module scan class to collect marked objects (module-only).
- [x] Bind each target using `Spellbook.bind` to reuse validation.
- [x] Add `Spellbook.scan` and `Conduit.scan` facade method(s).
- [x] Add tests for scan binding, re-export rejection, and duplicates.
- [x] Update docs/components if public API surface changes.

## Deliverables
- `src/melder/spellbook/bind/scan.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/utilities/interfaces/interfaces.py`
- `tests/unit/melder/spellbook/test_scan_bind.py`
- `context_compass/components/src_components.md`

## Files / Paths Impacted
- `src/melder/spellbook/bind/scan.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/utilities/interfaces/interfaces.py`
- `tests/` (new scan_bind tests)
- `context_compass/components/src_components.md`

## Validation
- Not run.
- Recommended commands:
  - `pytest`

## Risks / Rollback Notes
- Risk: scan re-exports or duplicate binds; mitigated via module ownership
  checks (`obj.__module__ == module.__name__`) and Spellbook.bind collisions.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded

## Context / Handoff Summary
- Implemented scan_bind decorator + Scan class in `src/melder/spellbook/bind/scan.py`.
- Added `Spellbook.scan` and `Conduit.scan` facades with module-only scan rules.
- Updated interfaces and added tests for scan binding, re-export rejection,
  duplicates, and conduit scan after conjure.
- Validation not run.
