Completed: 2026-02-08
Summary: Expanded benchmark runner with route matrix samples and optional per-route baseline delta regression checks.

# Task: Expand Benchmark Optimization Regression Matrix

## Metadata
- Task ID: TASK-2026-02-08-benchmark-optimization-regression-matrix
- Story: STORY-2026-02-08-codegen-meld-runtime-optimization-wave
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-08
- Updated: 2026-02-08

## Objective
Create a repeatable benchmark matrix for optimization tasks covering cold, warm,
mixed, overrides, and spellspace routes with baseline delta reporting.

## Scope Boundaries
- In scope:
- Extend benchmark runner/report structure for optimization milestones.
- Add baseline files or documented baseline capture flow.
- Out of scope:
- Competitor library benchmark integration.

## Steps / Checklist
- [x] Define benchmark matrix cases and expected output schema.
- [x] Extend runner/options for per-route and per-variant measurement.
- [x] Add validation checks for regression thresholds per route.
- [x] Document benchmark capture and baseline update procedure.

## Deliverables
- Expanded benchmark matrix runner and report artifacts.
- Documented baseline capture/update workflow.

## Files / Paths Impacted
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
- `benchmarks/testing_other_di/benchmarks.md`
- `context_compass/tasks/completed/2026-02-08_repeatable-codegen-benchmark-deltas_task_completed.md` (reference update if needed)

## Validation
- Ran:
  - python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py
  - $env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 1 --warmup-count 0 --allow-gate-failure --allow-baseline-regression --output-path benchmarks/testing_other_di/results/codegen_benchmark_report_smoke_v2.json
- Result:
  - Focused suites passed (138 passed).
  - Benchmark runner smoke passed and produced route matrix output.
- Recommended commands:
  - `python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 9 --warmup-count 1`

## Risks / Rollback Notes
- Risk: matrix growth increases run time and benchmark noise exposure.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task provides the benchmark guardrail surface for optimization tasks so each
change can be accepted/rejected against reproducible deltas.



