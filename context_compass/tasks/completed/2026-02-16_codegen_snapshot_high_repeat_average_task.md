# Task: Codegen Benchmark Duration + Baseline Process

## Metadata
- Task ID: TASK-2026-02-16-codegen-snapshot-high-repeat-average
- Story: STORY-2026-02-16-deep-creation-context-codegen-strategy-discovery
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Add optional duration-window sampling to existing fast/override cProfile
benchmark suites and create a dedicated baseline artifact folder so 60-second
reference baselines can be captured and reused in before/after comparisons.

## Scope Boundaries
- In scope:
- `benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py`
- `benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py`
- `benchmarks/testing_other_di/profiles/baselines/README.md`
- Optional duration-window controls and per-lane sample-average emission.
- Out of scope:
- Replacing existing before/after benchmark flow.
- Runtime code changes in `src/melder/**`.

## Steps / Checklist
- [x] Add optional duration env control to fast cProfile lanes.
- [x] Add optional duration env control to overrides cProfile lanes.
- [x] Emit per-lane `sample_mode`, `sample_count`, and `sample_avg_ms` in benchmark JSONL rows.
- [x] Add a baseline folder and capture instructions for 60-second baseline runs.
- [x] Run validation on default mode and duration mode.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Duration-window benchmark option (shared + suite-specific env vars).
- JSONL benchmark records with explicit sample-average metadata.
- Baseline folder docs for reusable 60-second reference captures.

## Files / Paths Impacted
- `benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py`
- `benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py`
- `benchmarks/testing_other_di/profiles/baselines/README.md`
- `context_compass/attention_board.md`
- `context_compass/tasks/completed/2026-02-16_phase12_overrides_high_risk_segmented_shape_helpers_slice2_task.md`

## Validation
- Completed.
- Commands:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q`
  - `$env:PYTHONPATH='src'; $env:DI_BENCHMARK_DURATION_S='0.2'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q`
  - `$env:PYTHONPATH='src'; $env:DI_BENCHMARK_DURATION_S='0.2'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q`
- Results:
  - Fast suite: `8 passed, 1 warning` (default mode), `8 passed, 1 warning` (duration mode).
  - Overrides suite: `8 passed, 1 warning` (default mode), `8 passed, 1 warning` (duration mode).

## Risks / Rollback Notes
- Risk: fixed-duration runs increase wall-clock test time (for example 60s/lane).
- Mitigation: duration mode is optional and disabled by default (`0.0`).
- Rollback: remove duration env handling and sample metadata fields.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Added optional duration-window mode to both cProfile suites with shared and suite-specific env vars (`DI_BENCHMARK_DURATION_S`, `DI_CPROFILE_DURATION_S`, `DI_OVERRIDE_CPROFILE_DURATION_S`), plus per-lane sample metadata in benchmark JSONL output.
  EVIDENCE: benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:69-146, benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:530-729, benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:100-177, benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:513-698
  IMPACT: Benchmarks can now run for fixed time budgets (for example 60s/lane) and produce stable average-per-sample metrics.
  NEXT: Capture clean idle-machine baseline artifacts in the baselines folder using 60-second runs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Added a dedicated baseline folder with usage docs for capturing reusable long-run references.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/README.md:1-33
  IMPACT: Baseline storage location and command contract are explicit and repeatable.
  NEXT: Store first canonical baseline under `profiles/baselines/{fast,overrides}` and reference it in future compare artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Both benchmark suites passed in default mode and duration mode after the harness changes.
  EVIDENCE: benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:659-729, benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:638-698
  IMPACT: Duration-window support is validated without breaking existing test flows.
  NEXT: Use `DI_BENCHMARK_DURATION_S=60` for strong baseline captures when machine is idle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task is complete. Existing fast/override cProfile suites now support optional
duration-window sampling with per-lane average metadata, and a baseline folder
is in place for reusable 60-second reference captures.
