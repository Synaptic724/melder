# Task: Add benchmark harness toggles for fast path

## Metadata
- Task ID: TASK-2026-01-25-benchmark-harness-toggles
- Story: STORY-2026-01-25-fast-path-observability
- Status: draft
- Owner:
- Priority: p2
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Add configuration toggles to benchmark harnesses for hooks, change-control, and
fast-path enablement.

## Scope Boundaries
- In scope:
  - Benchmark toggles for fast path and gating features.
- Out of scope:
  - Code changes to runtime other than exposed toggles.

## Steps / Checklist
- [ ] Identify benchmark entrypoints used for meld hot paths.
- [ ] Add toggles for hooks and change-control.
- [ ] Add toggles for fast-path enablement.

## Deliverables
- Benchmark harness toggles for fast-path profiling.

## Files / Paths Impacted
- benchmarks/testing_other_di/test_melder_hotpath_profiles.py
- benchmarks/testing_other_di/test_conduit_integration_perf_deep_graphs.py

## Validation
- Not run.
- Recommended commands:
  - pytest benchmarks/testing_other_di/test_melder_hotpath_profiles.py -q

## Risks / Rollback Notes
- Risk: toggles diverge from runtime defaults.
  Mitigation: log toggles at benchmark start.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; benchmark toggles pending.
