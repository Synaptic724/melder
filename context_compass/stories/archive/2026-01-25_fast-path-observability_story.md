# Story: Fast-path observability and benchmarks

## Metadata
- Story ID: STORY-2026-01-25-fast-path-observability
- Epic: EPIC-2026-01-25-fast-path-meld-compiled-plans
- Status: draft
- Owner:
- Priority: p2
- Created: 2026-01-25
- Updated: 2026-01-25

## User Narrative
As a performance engineer, I want fast-path metrics and benchmark knobs so we
can quantify speedups and validate regressions.

## Value / MRP Alignment
Observability ensures the optimized path is measurable and safe to roll out.

## Requirements (Functional)
- Track fast-path hit rate and fallback reasons.
- Measure eligibility checks and plan execution time.
- Add benchmark toggles for hooks, change-control, and dynamic mode.

## Requirements (Non-Functional)
- Minimal overhead when metrics are disabled.

## Scope Boundaries
- In scope:
  - Structured counters or timers for fast-path runtime.
  - Benchmark harness toggles and baseline runs.
- Out of scope:
  - Full telemetry pipeline integration.

## Dependencies / Related Work
- Bench harness files in benchmarks/testing_other_di.

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-25-observability-research - Research benchmark harness and metrics placement.
- [ ] Task: TASK-2026-01-25-fast-path-metrics - Add counters and timers.
- [ ] Task: TASK-2026-01-25-benchmark-harness-toggles - Add toggles to benchmarks.
- [ ] Task: TASK-2026-01-25-fast-path-benchmark-baselines - Record baseline runs.

## Acceptance Criteria
- Fast-path hit rate and fallback reasons are observable.
- Bench harness can enable or disable hooks and change-control.

## Validation / Test Plan
- Not run.
- Recommended: pytest benchmarks/testing_other_di/test_melder_hotpath_profiles.py -q

## UX / API / Data Notes
- Internal metrics only.

## Risks / Mitigations
- Risk: metrics add overhead to the fast path.
  Mitigation: guard metrics behind configuration flags.

## Open Questions
- Where should fast-path metrics live to avoid new module-level state?

## Decision Log
- TBD.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created; metrics and benchmark toggles pending.
