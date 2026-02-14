# Task: Remove legacy MeldEngine run path and duplication

## Metadata
- Task ID: TASK-2026-01-30-remove-meldengine-legacy-run
- Story: N/A
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-01-30
- Updated: 2026-01-30

## Objective
Remove the legacy non-Phase-11 execution path in MeldEngine so Phase 11
ExecutionPlan is the only runtime execution path, with no fallback logic.

## Scope Boundaries
- In scope:
  - Remove MeldEngine.run() legacy execution path and helpers only used by it.
  - Make run_execution_plan the single entrypoint (no internal recompute).
  - Remove unused occurrence/injection plan fields from MeldEngine init.
  - Update docstrings/comments in touched code.
- Out of scope:
  - Architecture/components doc updates.
  - Tests (unless requested).

## Steps / Checklist
- [x] Remove MeldEngine.run() path and exclusive helpers/state.
- [x] Tighten run_execution_plan inputs and update runtime wiring.
- [x] Update docstrings/comments for Phase 11-only execution.

## Deliverables
- Phase 11 execution plan is the only MeldEngine runtime path.
- No duplicate planning/override logic in MeldEngine.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py

## Validation
- Not run.
- Recommended commands:
  - pytest -q

## Risks / Rollback Notes
- Risk: Runtime now requires Phase 11 artifacts; no fallback if missing.
  - Rollback: restore legacy run() path and wiring.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Removed the legacy MeldEngine.run path and its helper logic; Phase 11 plans are now the only execution path.
- Tightened run_execution_plan to require precomputed override inputs from MeldRuntime.
- Updated runtime wiring and docstrings to reflect Phase 11-only execution.
