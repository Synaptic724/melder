Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Task: Implement codegen fast transient executor

## Metadata
- Task ID: TASK-2026-02-07-codegen-fast-transient
- Story: 
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-02-07
- Updated: 2026-02-07

## Objective
Implement a codegen-based fast transient executor in MeldRuntime and route
execute_fast_transient through it, mirroring current behavior.

## Scope Boundaries
- In scope:
- Add codegen executor in MeldRuntime.
- Substitute execute_fast_transient to use codegen path.
- Out of scope:
- Changes to other files or routing.
- Tests (user requested no tests).

## Steps / Checklist
- [x] Add codegen executor in MeldRuntime with parity behavior.
- [x] Route execute_fast_transient through codegen executor.
- [x] Keep fallback to loop-based execution if codegen fails.

## Deliverables
- Updated MeldRuntime with codegen_fast_transient executor.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py

## Validation
- Not run (user request).
- Recommended commands:
  - pytest tests/unit

## Risks / Rollback Notes
- Codegen failures should fall back to existing loop implementation.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Added codegen fast transient executor in MeldRuntime and routed
  execute_fast_transient through it with a loop fallback and per-runtime cache.
  Added solo fast path, micro-DAG (<=8 steps), tiny-DAG (steps < 32),
  small-DAG (<=128 steps, <=9 depth), and large-DAG codegen paths; selection
  uses step count + depth metrics.

