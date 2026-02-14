# Task: Strip runtime phase rebuilding from MeldRuntime and MeldEngine

## Metadata
- Task ID: TASK-2026-01-29_meld_runtime_engine_execution_only
- Story:
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-01-29
- Updated: 2026-01-29

## Objective
Make MeldRuntime and MeldEngine execution-only by removing runtime phase rebuilding/validation and deferring phase ownership to SpellSystemStates + phase pipelines.

## Scope Boundaries
- In scope:
  - Remove on-the-spot Phase 11 ExecutionPlan building in MeldRuntime.
  - Remove on-the-spot Phase 8 OccurrencePlan building in MeldEngine.
  - Keep basic execution invariants (root mismatch, existing creation handling).
  - Update tests that assume runtime/engine rebuilds.
- Out of scope:
  - Changes to SpellSystemStates gating logic.
  - Architecture/components doc updates (tracked separately).

## Steps / Checklist
- [x] Identify and remove runtime plan-building logic in MeldRuntime.
- [x] Identify and remove runtime plan-building logic in MeldEngine.
- [x] Adjust error handling to reflect missing phase artifacts.
- [x] Update affected tests to align with execution-only behavior.
- [ ] Summarize changes and recommend validation commands.

## Deliverables
- Execution-only MeldRuntime/MeldEngine behavior.
- Updated unit/integration tests (if needed) to reflect new behavior.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`
- Tests TBD after impact assessment.

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: Tests and flows relying on runtime phase builds will fail.
- Rollback: Re-introduce runtime plan building if needed.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Execution-only shift underway: removed runtime plan building in MeldRuntime and MeldEngine; updated Phase 11 gating tests to reflect slow-path fallback. Next: summarize changes and decide whether to adjust broader meld_engine tests or accept failures per user guidance.
