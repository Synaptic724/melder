# Task: Inline Phase 11 fast-path construction + precompiled construct metadata

## Metadata
- Task ID: TASK-2026-01-30-phase11-fastpath-inline-construct
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-01-30
- Updated: 2026-01-30

## Objective
Reduce remaining per-step overhead in the NO_OVERRIDES_FAST path by removing
helper calls and property access in the construction loop and by precompiling
spell construction metadata into the fast plan.

## Problem / Opportunity
Profiling shows the remaining time concentrated in `_construct_spell_positional`
and repeated spell kind/property lookups. These are pure runtime overhead in the
fast path and can be eliminated with precompiled metadata.

## Context
- Phase 11 NO_OVERRIDES_FAST is already array-driven.
- Validation at the meld front door is assumed to enforce correctness.

## MRP Alignment
This is a focused performance change to the core execution path, keeping the
same external semantics and avoiding new dependencies.

## Goals
- Precompile per-step construct metadata into the fast plan.
- Inline construction in the NO_OVERRIDES_FAST loop to avoid helper calls.
- Avoid per-step property access (`ExecutionPlanStep.spell`) in the fast loop.
- Preserve existing behavior for override/mutation paths.

## Non-Goals
- No changes to override/mutation override semantics.
- No tests added in this pass (explicitly deferred by user).
- No public API changes.

## Scope Boundaries
- In scope:
  - ExecutionPlan fast arrays extended to include construct metadata.
  - MeldEngine fast loop uses arrays directly for construction.
  - Cached spell flags used to avoid property access on hot paths.
- Out of scope:
  - Rewriting reuse/locking algorithms.
  - Changing Phase 1-4 validation logic.

## Requirements
- Remove redundant guards in fast path based on validation guarantees.
- Avoid `_construct_spell_positional` and `_construct_spell` in the fast loop.
- Keep docstrings in sync with new fast-plan contents.

## Acceptance Criteria
- Fast path uses precompiled construct metadata and avoids helper calls.
- Profiling no longer shows `_construct_spell_positional` as a hotspot.
- Override/mutation paths remain functional.

## Steps / Checklist
- [x] Create task ticket for inline fast-path construction.
- [x] Extend ExecutionPlan fast arrays with construct metadata (spell, call target,
      existing object, callable flags).
- [x] Update fast-plan builder to populate construct metadata arrays.
- [x] Update MeldEngine fast loop to use inline construction and precompiled metadata.
- [x] Update docstrings for modified methods.

## Deliverables
- Faster NO_OVERRIDES_FAST execution loop with inlined construction.
- Updated docstrings for fast-plan metadata and execution behavior.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/execution_plan.py`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`

## Validation
- Not run (per user instruction).
- Recommended commands:
  - `python benchmarks/testing_other_di/profile_deep_all_di_transient_only_no_singletons.py`

## Risks / Rollback Notes
- Risk: Guard removal could hide invalid plan inputs. Mitigation: front-door validation
  is assumed to enforce correctness for fast path.

## Context / Handoff Summary
Fast plan now carries construct metadata (spells, call targets, existing objects,
callable flags). NO_OVERRIDES_FAST loop inlines construction using these arrays,
avoids helper calls, and uses preallocated argument lists. Docstrings updated.
