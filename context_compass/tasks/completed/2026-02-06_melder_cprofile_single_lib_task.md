Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Task: Add melder cProfile single-lib benchmark test

## Metadata
- Task ID: TASK-2026-02-06-melder-cprofile-single-lib
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-02-06
- Updated: 2026-02-06

## Objective
Add a melder-only cProfile test modeled after the Lagom single-lib benchmark
so we can capture per-graph timing and cProfile output for Melder.

## Scope Boundaries
- In scope:
  - New pytest under `benchmarks/competitors/melder_implementation_plan/tests/`.
  - Use `test_shallow_all` graph specs and melder runtime builder.
  - Output per-graph timing, optional cProfile stats.
- Out of scope:
  - Runtime changes.
  - Benchmark harness changes outside the new test.

## Steps / Checklist
- [x] Create melder benchmark test with env toggles matching Lagom version.
- [x] Implement per-graph timing and optional cProfile output.
- [x] Ensure outputs print under pytest capture.

## Deliverables
- `benchmarks/competitors/melder_implementation_plan/tests/test_melder_cprofile_single_lib.py`

## Files / Paths Impacted
- `benchmarks/competitors/melder_implementation_plan/tests/test_melder_cprofile_single_lib.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest -q -s benchmarks/competitors/melder_implementation_plan/tests/test_melder_cprofile_single_lib.py`

## Risks / Rollback Notes
- Risk: Misleading comparisons if env vars diverge from Lagom test.
  Mitigation: Use the same env var names and defaults.
- Rollback: Remove the new test file.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Added `test_melder_cprofile_single_lib.py` mirroring the Lagom benchmark with
Melder runtime wiring and shared graph specs. Validation not run yet.

