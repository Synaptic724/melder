# Task: Add fast-path metrics and timers

## Metadata
- Task ID: TASK-2026-01-25-fast-path-metrics
- Story: STORY-2026-01-25-fast-path-observability
- Status: draft
- Owner:
- Priority: p2
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Add counters and timers for fast-path hit rate, eligibility checks, and plan
execution time.

## Scope Boundaries
- In scope:
  - Metrics collection and minimal reporting.
- Out of scope:
  - External telemetry integration.

## Steps / Checklist
- [ ] Define metric names and collection points.
- [ ] Add guarded timers in fast-path runtime.
- [ ] Expose counters via logger or diagnostics API.

## Deliverables
- Fast-path metrics available for debugging and benchmarks.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- src/melder/aether/conduit/meld/fast_meld_executor.py (new)

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k metrics

## Risks / Rollback Notes
- Risk: metrics add overhead to fast path.
  Mitigation: guard behind configuration flag.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; fast-path metrics pending.
