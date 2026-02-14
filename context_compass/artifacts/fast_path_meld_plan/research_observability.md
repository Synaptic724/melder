# Research: Observability and benchmark harness

Date: 2026-01-25

## Scope
Capture existing benchmark harness hooks and profiling toggles relevant to
fast-path measurement.

## Evidence
- benchmarks/testing_other_di/test_melder_hotpath_profiles.py
- src/melder/utilities/logger/safe_logger.py

## Findings
- The benchmark harness already supports profiling toggles (cProfile,
  tracemalloc, GC delta) and prints cold vs warm meld timings in
  test_melder_hotpath_profiles.py.
- The harness includes an optional PhaseScheduler timing wrapper that records
  per-phase durations for conjure.

## Unknowns
- UNKNOWN: Where fast-path metrics should live without introducing new module
  state (per-Conduit, per-MeldRuntime, or via existing logging).
  - Why it matters: metrics must be cheap and obey module-scope constraints.
  - Where to investigate: src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
    and src/melder/utilities/logger/safe_logger.py.
  - Status: uninvestigated.

- UNKNOWN: Whether existing benchmark harnesses should add flags for fast-path
  gating (hooks/change-control) or if new harness files are required.
  - Why it matters: baseline comparisons must match fast-path eligibility.
  - Where to investigate: benchmarks/testing_other_di/test_melder_hotpath_profiles.py
    and other benchmark modules under benchmarks/testing_other_di.
  - Status: uninvestigated.
