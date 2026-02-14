Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Task: Add shallow graph Phase 11 metrics diagnostics test

## Metadata
- Task ID: TASK-2026-02-06-shallow-graph-phase11-metrics-diagnostics
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-02-06
- Updated: 2026-02-06

## Objective
Add a pytest that models the `test_shallow_all.py` graph shapes (solo, shallow,
wide, diamond, deep) and computes Phase 11-style metrics without running
Phase 11, then prints the metrics for inspection.

## Scope Boundaries
- In scope:
  - New pytest under `benchmarks/testing_other_di/`.
  - Import graph shapes from `test_shallow_all.py` for parity.
  - Compute step count, unique count, max depth, max dependency count,
    CALLN presence, and preferred route thresholds.
- Out of scope:
  - Runtime code changes.
  - Benchmark harness modifications.

## Steps / Checklist
- [x] Define a diagnostic test that enumerates graph roots and prints metrics.
- [x] Compute metrics using constructor dependency expansion.
- [x] Apply Phase 11 preferred-route thresholds.
- [x] Add minimal assertions for expected shapes.

## Deliverables
- `benchmarks/testing_other_di/test_shallow_diagnostics.py`

## Files / Paths Impacted
- `benchmarks/testing_other_di/test_shallow_diagnostics.py`

## Validation
- Run: `python -m pytest -q -s benchmarks/testing_other_di/test_shallow_diagnostics.py`
- Result: 5 passed.
- Note: Pytest cache warning due to `<local-workspace>\.pytest_cache` permission.

## Risks / Rollback Notes
- Risk: Metrics drift from real Phase 11 if thresholds or graph definitions change.
  Mitigation: Keep thresholds aligned with `SpellCrafter._cache_execution_plan_metrics`.
- Rollback: Remove the new test file.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Diagnostic pytest for shallow benchmark graphs added to expose Phase 11-style
metrics without running Phase 11. Pending user validation of output.

