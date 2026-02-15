Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Task: Add melder route diagnostics for test_shallow_all

## Metadata
- Task ID: TASK-2026-02-06-shallow-all-melder-route-diagnostics
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-02-06
- Updated: 2026-02-06

## Objective
Add a pytest that uses the real `test_shallow_all.py` graph wiring and
Melder runtime to print timing and prove which execution path (fast
transient vs pooled vs engine) is actually taken for each root.

## Scope Boundaries
- In scope:
  - Diagnostic pytest under `benchmarks/testing_other_di/`.
  - Instrument MeldRuntime route selection for root A/B per graph.
  - Print per-root route, preferred route, and timing.
- Out of scope:
  - Runtime code changes.
  - Benchmark harness changes.

## Steps / Checklist
- [x] Build a melder-only diagnostic harness using test_shallow_all graphs.
- [x] Trace runtime route selection (fast transient vs pooled vs engine).
- [x] Print per-root timing and route diagnostics.
- [x] Add assertions that actual route matches expected route logic.

## Deliverables
- `benchmarks/testing_other_di/test_shallow_all_diagnostics.py`

## Files / Paths Impacted
- `benchmarks/testing_other_di/test_shallow_all_diagnostics.py`

## Validation
- Run: `python -m pytest -q -s benchmarks/testing_other_di/test_shallow_all_diagnostics.py`
- Result: 5 passed.
- Note: Pytest cache warning due to `<local-workspace>\.pytest_cache` permission.

## Risks / Rollback Notes
- Risk: Diagnostic output could be misread as a benchmark.
  Mitigation: Keep iterations low and label as diagnostics.
- Rollback: Remove the new test file.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Added a melder-only diagnostic pytest that proves runtime route selection
for the real test_shallow_all graphs and prints timing. Pending user
acceptance of diagnostics output.

