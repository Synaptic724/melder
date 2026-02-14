# Task: Skip ResolutionFrame in fast path + add call modes

## Metadata
- Task ID: TASK-2026-01-30-phase11-fastpath-skip-frame-callmodes
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-01-30
- Updated: 2026-01-30

## Objective
Reduce Phase 11 NO_OVERRIDES_FAST overhead by skipping `ResolutionFrame` creation
when safe and adding call-mode metadata to avoid per-step loop work.

## Problem / Opportunity
Profiling shows the remaining time is inside the fast-path loop. Two low-risk
reductions are still available:
- Skip `ResolutionFrame` allocation/cleanup when no overrides/mutations.
- Use precompiled call modes for trivial calls (0/1 dependency) to avoid list
  allocation and inner loops.

## Context
- NO_OVERRIDES_FAST already uses array-driven execution.
- Overrides/mutation overrides remain on the standard path.

## MRP Alignment
Small, internal performance changes without altering external semantics.

## Goals
- Skip `ResolutionFrame` creation in no-overrides fast path when a fast plan exists.
- Add precomputed call modes to avoid work for common 0/1-dependency calls.
- Keep override/mutation behavior intact.

## Non-Goals
- No test additions in this pass (explicitly deferred by user).
- No public API changes.
- No change to Phase 1–4 validation.

## Scope Boundaries
- In scope:
  - `ExecutionPlan` fast arrays extended with call modes and single-dep index.
  - `MeldRuntime` skips frame creation when safe.
  - `MeldEngine` fast loop uses call modes and tolerates missing frame.
- Out of scope:
  - Any changes to override/mutation plan semantics.

## Requirements
- Use call modes only when contracts/overrides do not apply.
- Preserve `ResolutionFrame` use on override/mutation paths.
- Update docstrings for touched methods.

## Acceptance Criteria
- NO_OVERRIDES_FAST runs without a `ResolutionFrame` allocation when safe.
- Fast loop uses call-mode metadata for trivial calls.
- Override/mutation execution remains unchanged.

## Steps / Checklist
- [x] Create task ticket.
- [x] Extend fast arrays with call modes and single-dep indices.
- [x] Populate call modes in fast-plan builder.
- [x] Skip `ResolutionFrame` creation when safe.
- [x] Use call modes in fast loop and tolerate missing frame.
- [x] Update docstrings for modified methods.

## Deliverables
- Faster NO_OVERRIDES_FAST path with reduced allocations/loop overhead.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/execution_plan.py`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`

## Validation
- Not run (per user instruction).
- Recommended commands:
  - `python benchmarks/testing_other_di/profile_deep_all_di_transient_only_no_singletons.py`

## Risks / Rollback Notes
- Risk: Missing frame on paths that expect it. Mitigation: only skip when
  no overrides/mutations and fast plan exists.

## Context / Handoff Summary
NO_OVERRIDES_FAST now skips `ResolutionFrame` allocation when a fast plan exists,
and the fast plan includes call modes + single-dependency indices for trivial
calls. MeldEngine uses the call modes and tolerates a missing frame. Docstrings
updated to reflect new behavior.
