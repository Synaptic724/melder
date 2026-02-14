Completed: 2026-02-08
Summary: Added repeatable codegen benchmark delta runner plus baseline median regression API and tests.

# Task: Add Repeatable Codegen Benchmark Delta Script

## Metadata
- Task ID: TASK-2026-02-08-repeatable-codegen-benchmark-deltas
- Story: STORY-2026-02-07-validation-perf-gates
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-08
- Updated: 2026-02-08

## Objective
Provide a repeatable script that measures codegen cold/warm/mixed paths and emits
baseline deltas for milestone tracking.

## Scope Boundaries
- In scope:
- Benchmark runner script and baseline delta evaluation wiring.
- Unit tests for baseline delta gate behavior.
- Out of scope:
- Competitor benchmark updates.
- Broad benchmark suite refactors.

## Steps / Checklist
- [x] Add baseline-delta evaluation API to runtime benchmark helpers.
- [x] Add repeatable benchmark script for codegen cold/warm/mixed samples.
- [x] Add/extend unit tests for delta pass/fail contracts.
- [x] Update ticket context summary.

## Deliverables
- Runtime API for comparing current benchmark medians against baseline medians.
- Script that records benchmark samples, gate report, and baseline deltas.

### Delivered
- Added runtime baseline delta API:
  - `MeldRuntime.evaluate_codegen_benchmark_baseline_deltas(...)`
  - supporting median validation helper:
    - `MeldRuntime._require_benchmark_report_median(...)`
- Added repeatable benchmark runner script:
  - `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
  - supports:
    - cold/warm/mixed sample collection,
    - warm/mixed gate evaluation,
    - optional baseline report comparison,
    - JSON report output and pass/fail exit code.
- Added benchmark baseline delta unit tests in:
  - `tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py`

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py`
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
- `context_compass/stories/completed/2026-02-07_validation-perf-gates_story_completed.md`
- `context_compass/epics/completed/2026-02-07_full-aot-codegen-cutover_epic_completed.md`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py`
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 1 --warmup-count 0 --allow-gate-failure --allow-baseline-regression --output-path benchmarks/testing_other_di/results/codegen_benchmark_report_smoke.json`
- Result:
  - 39 passed (runtime unit suite).
  - Script smoke run passed and emitted gate summary.

## Risks / Rollback Notes
- Benchmark noise may trigger false regression signals if thresholds are too strict.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task closed with runtime-level baseline delta reporting and a repeatable runner
script that can be used per milestone to record JSON benchmark reports and
compare medians against prior baselines.
