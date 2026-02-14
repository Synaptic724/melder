# Task: Drop `_instance_results` writes in NO_OVERRIDES_FAST

## Metadata
- Task ID: TASK-2026-01-30-phase11-fastpath-drop-instance-results
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-01-30
- Updated: 2026-01-30

## Objective
Eliminate `_instance_results` writes in the NO_OVERRIDES_FAST path and return the
root instance directly from the fast-value array to reduce per-step dict overhead.

## Problem / Opportunity
Profiling shows the remaining time is concentrated in the fast-path execution loop.
Writing every instance into `_instance_results` is unnecessary when dependencies
are resolved through the fast-value array and the root instance can be returned
by index.

## Context
- NO_OVERRIDES_FAST is now a fully array-driven plan.
- Validation at the meld front door is assumed to enforce correctness.

## MRP Alignment
This is a narrow performance-only change within the core fast path, preserving
external semantics and avoiding new dependencies.

## Goals
- Avoid writing to `_instance_results` in NO_OVERRIDES_FAST.
- Add a precompiled root step index to return the root instance directly.
- Keep override/mutation execution paths unchanged.

## Non-Goals
- No changes to override/mutation semantics.
- No tests added in this pass (explicitly deferred by user).
- No public API changes.

## Scope Boundaries
- In scope:
  - ExecutionPlan fast arrays add root step index and optional fast-path flags.
  - MeldEngine fast loop returns root from `fast_values` without `_instance_results`.
- Out of scope:
  - Rewriting the reuse/locking algorithm.
  - Phase 1–4 validation changes.

## Requirements
- Remove `_instance_results` writes in NO_OVERRIDES_FAST.
- Use precomputed root step index for fast-path return.
- Keep docstrings in sync with new fast-plan contents.

## Acceptance Criteria
- NO_OVERRIDES_FAST avoids `_instance_results` writes.
- Root instance is returned via `fast_values[root_step_index]`.
- Override/mutation paths continue to behave as before.

## Steps / Checklist
- [x] Create task ticket for dropping `_instance_results` in fast path.
- [x] Extend ExecutionPlan fast arrays with root step index (and any fast-path flags).
- [x] Update fast-plan builder to populate root step index.
- [x] Update MeldEngine fast loop to stop writing `_instance_results` and return root directly.
- [x] Update docstrings for modified methods.

## Deliverables
- Faster NO_OVERRIDES_FAST path with fewer dict operations.
- Updated docstrings for fast-plan metadata and execution behavior.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/execution_plan.py`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`

## Validation
- Not run (per user instruction).
- Recommended commands:
  - `python benchmarks/testing_other_di/profile_deep_all_di_transient_only_no_singletons.py`

## Risks / Rollback Notes
- Risk: Code relying on `_instance_results` in fast path. Mitigation: limit removal
  to NO_OVERRIDES_FAST and keep ResolutionFrame population.

## Context / Handoff Summary
NO_OVERRIDES_FAST now carries a root step index and returns the root instance
directly from the fast-value array without `_instance_results` writes. Docstrings
updated to reflect the new fast-plan metadata and return behavior.
