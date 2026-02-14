Completed: 2026-02-08
Summary: Closed and turned in for Migrate Resolver and Supporting Runtime Methods into CreationContext.

# Task: Migrate Resolver and Supporting Runtime Methods into CreationContext

## Metadata
- Task ID: TASK-2026-02-08-migrate-runtime-resolver-into-creation-context
- Story: STORY-2026-02-08-runtime-migration-codegen-cutover
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-08
- Updated: 2026-02-08

## Objective
Move `_resolver` and supporting existence/runtime helpers into spell-owned `CreationContext` classes so runtime execution is fully context-owned.

## Scope Boundaries
- In scope:
  - Migrate resolver and supporting helper methods.
  - Preserve existence semantics and lock contracts.
  - Keep method ownership coherent inside spell-owned context.
- Out of scope:
  - Hook front-door logic.
  - New override semantics.

## Steps / Checklist
- [x] Identify `_resolver` support method cluster and migration order.
- [x] Move methods into spell-owned context class/module.
- [x] Rebind internal method calls to new class ownership.
- [x] Delete or inline replaced method shells.

## Deliverables
- Resolver and dependent runtime helper logic owned by spell context.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/aether/conduit/meld/meld_context/creation_context.py`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest tests/unit/melder/aether/conduit/meld -q`

## Risks / Rollback Notes
- Risk: missed helper migration causes split ownership regressions.
- Rollback: restore previous helper and re-run migration by smaller method sets.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
This task is the method-ownership migration center of gravity. It should leave no unresolved resolver internals in the old meld-owned path.
