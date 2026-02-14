# Story: Fast-path executor and gating in meld runtime

## Metadata
- Story ID: STORY-2026-01-25-fast-path-runtime
- Epic: EPIC-2026-01-25-fast-path-meld-compiled-plans
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## User Narrative
As a runtime user, I want meld to execute a compiled plan when conditions are
safe, so that best-case resolution is fast and predictable.

## Value / MRP Alignment
Provides the fast path while preserving correctness through explicit gating and
fallback to the existing runtime.

## Requirements (Functional)
- Fast-path eligibility checks in MeldRuntime or Meld.
- Optimistic cache hit shortcut when overrides are absent.
- Fast-path executor that uses RootExecutionPlan for construction and
  registration.
- Explicit fallback to current runtime when gating fails.

## Requirements (Non-Functional)
- Minimal allocations in the optimistic case.
- No public API changes.

## Scope Boundaries
- In scope:
  - Eligibility checks and plan execution.
  - Fallback reasons captured for diagnostics.
- Out of scope:
  - Plan compilation.
  - Codegen execution engine.

## Dependencies / Related Work
- MeldRuntime.execute and gating logic
  (src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py).
- Existing registration and existence logic in Meld
  (src/melder/aether/conduit/meld/meld.py).

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-25-fast-path-gates-research - Research gating and hook constraints.
- [ ] Task: TASK-2026-01-25-fast-path-eligibility-gates - Implement fast-path checks.
- [ ] Task: TASK-2026-01-25-optimistic-cache-hit - Add no-lock cached instance return.
- [ ] Task: TASK-2026-01-25-fast-path-executor - Execute RootExecutionPlan.
- [ ] Task: TASK-2026-01-25-fast-path-fallback-reasons - Track fallback reasons.
- [ ] Task: TASK-2026-01-25-fast-path-runtime-tests - Add unit and component tests.

## Acceptance Criteria
- Fast path executes for eligible calls and returns correct instances.
- Fallback occurs when overrides, mutation, or validity gates require it.
- Optimistic cache hit returns without building a ResolutionFrame.

## Validation / Test Plan
- Not run.
- Recommended: pytest tests/unit/melder/aether/conduit/meld -k fast_path

## UX / API / Data Notes
- Internal runtime behavior only.

## Risks / Mitigations
- Risk: cache hit bypass breaks override semantics.
  Mitigation: gate cache hit on empty overrides and mutation overrides.

## Open Questions
- Should fast path skip hooks or allow hook-aware plan variants?

## Decision Log
- TBD.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created; runtime gating and executor pending.
