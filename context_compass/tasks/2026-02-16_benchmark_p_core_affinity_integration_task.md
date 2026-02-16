# Task: Benchmark P-Core Affinity Integration

## Metadata
- Task ID: TASK-2026-02-16-benchmark-p-core-affinity-integration
- Story: STORY-2026-02-16-benchmark-stability-support
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Add optional P-core affinity pinning support for benchmark processes so we can
reduce Intel P/E scheduling variance during benchmark runs.

## Scope Boundaries
- In scope:
- Add a Windows-oriented affinity utility under `benchmarks/p_core_affinity/`.
- Integrate optional affinity pinning into fast/overrides benchmark suites.
- Expose an opt-in control path for snapshot benchmark runs.
- Out of scope:
- Non-Windows affinity implementations.
- Mandatory affinity behavior for all benchmark runs.

## Steps / Checklist
- [x] Add `benchmarks/p_core_affinity` utility module with robust detection/pinning helpers.
- [x] Wire optional affinity activation into fast benchmark suite.
- [x] Wire optional affinity activation into overrides benchmark suite.
- [x] Surface affinity metadata in snapshot output for traceability.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `benchmarks/p_core_affinity` module with documented public helper(s).
- Env-driven optional P-core pinning in benchmark test suites.
- Snapshot artifact field(s) indicating whether affinity pinning was requested/applied.

## Files / Paths Impacted
- `benchmarks/p_core_affinity/`
- `benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py`
- `benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py`
- `benchmarks/testing_other_di/run_snapshot_timings.py`
- `context_compass/attention_board.md`

## Validation
- Run:
  - `$env:PYTHONPATH='.;src'; .\.venv_new\Scripts\python.exe -m py_compile benchmarks/p_core_affinity/p_core_affinity.py benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py benchmarks/testing_other_di/run_snapshot_timings.py benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe benchmarks/testing_other_di/run_snapshot_timings.py --snapshot-label affinity_smoke --iterations 1 --warmup-iters 0 --fast-graphs solo --override-graphs solo --output-dir benchmarks/testing_other_di/profiles/overrides_graphs_melder --pin-p-cores`
  - `$env:PYTHONPATH='.;src'; $env:DI_PIN_P_CORES='1'; $env:DI_CPROFILE='0'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s -k "smoke and solo"`
  - `$env:PYTHONPATH='.;src'; $env:DI_PIN_P_CORES='1'; $env:DI_OVERRIDE_CPROFILE='0'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s -k "smoke and solo"`
  - `$env:PYTHONPATH='.;src'; .\.venv_new\Scripts\python.exe benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 1 --warmup-count 0 --allow-gate-failure --allow-baseline-regression --output-path benchmarks/testing_other_di/results/codegen_benchmark_report_affinity_smoke.json --pin-p-cores`

## Risks / Rollback Notes
- Risk: CPU-set parsing on unsupported Windows versions may fail.
- Mitigation: graceful fallback to no affinity change and clear status metadata.
- Rollback: remove env toggle usage and keep utility module unused.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: User-directed work opened to add optional P-core process pinning for benchmark stability in fast/overrides and snapshot workflows.
  EVIDENCE: benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:97-109, benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:130-141, benchmarks/testing_other_di/run_snapshot_timings.py:597-676
  IMPACT: We can reduce cross-run variance from P/E-core scheduling while preserving opt-in behavior.
  NEXT: Implement `benchmarks/p_core_affinity` utility and wire env-driven activation into benchmark suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Implemented an opt-in Windows affinity utility under `benchmarks/p_core_affinity` and wired affinity metadata into fast/overrides benchmark JSONL artifacts plus snapshot/codegen benchmark payloads.
  EVIDENCE: benchmarks/p_core_affinity/p_core_affinity.py:233-413, benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:14-31, benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:648-660, benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:14-31, benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:631-643, benchmarks/testing_other_di/run_snapshot_timings.py:167-171, benchmarks/testing_other_di/run_snapshot_timings.py:627-680, benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:358-362, benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:945-992
  IMPACT: Benchmarks can now pin process affinity to detected P-core logical CPUs without changing default behavior.
  NEXT: Validate wiring and capture artifact evidence showing `reason: pinned` when enabled.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Validation passes show affinity activation is operational (`reason: pinned`) in snapshot and codegen artifacts, and targeted fast/overrides smoke benchmark tests pass with env pinning enabled.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/affinity_smoke_snapshot_summary_2026-02-16_20-57-20.txt:20-24, benchmarks/testing_other_di/profiles/fast_graphs_melder/benchmark_results.jsonl:1432-1432, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:1866-1866, benchmarks/testing_other_di/results/codegen_benchmark_report_affinity_smoke.json:2-107
  IMPACT: Feature is usable immediately for benchmark stability runs on hybrid Intel CPUs.
  NEXT: Share usage contract (`DI_PIN_P_CORES=1` or `--pin-p-cores`) and request acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Completed a full 15-second duration benchmark pass with affinity enabled across both suites; fast and overrides artifacts each contain 8 duration rows with `affinity_applied=true` and `affinity_reason=\"pinned\"`.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/fast/benchmark_results_15s_pcore_2026-02-16.jsonl:1-8, benchmarks/testing_other_di/profiles/baselines/overrides/benchmark_results_15s_pcore_2026-02-16.jsonl:1-8
  IMPACT: Confirms the utility works under real 15-second benchmark load, not only smoke checks.
  NEXT: Compare pinned 15-second artifacts versus unpinned 15-second baseline on request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Re-ran both 15-second suites with pinning enabled and compared against the original pinned artifacts; fast suite mean is slightly faster (`-0.679%`) while overrides suite mean is slightly slower (`+1.855%`), with per-label deltas spanning `-3.439%` to `+3.195%`.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/fast/benchmark_results_15s_pcore_2026-02-16.jsonl:1-8, benchmarks/testing_other_di/profiles/baselines/fast/benchmark_results_15s_pcore_repeat_2026-02-16.jsonl:1-8, benchmarks/testing_other_di/profiles/baselines/overrides/benchmark_results_15s_pcore_2026-02-16.jsonl:1-8, benchmarks/testing_other_di/profiles/baselines/overrides/benchmark_results_15s_pcore_repeat_2026-02-16.jsonl:1-8
  IMPACT: P-core pinning reduces scheduler noise but does not make these 15-second benchmark lanes fully deterministic across immediate repeats.
  NEXT: If needed, run unpinned A/B repeats in the same window to quantify pinning vs non-pinning variance directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Available fast-lane A/B artifacts indicate pinning materially improves repeat stability (`mean_abs_delta_pct` drops from `9.381%` unpinned to `1.395%` pinned; max abs drift `23.725%` to `3.439%`), while overrides lacks a matched unpinned repeat pair and remains inconclusive for stability.
  EVIDENCE: benchmarks/testing_other_di/profiles/baselines/fast/benchmark_results_15s_2026-02-16.jsonl:1-8, benchmarks/testing_other_di/profiles/baselines/fast/benchmark_results_15s_unpinned_repeat_2026-02-16.jsonl:1-8, benchmarks/testing_other_di/profiles/baselines/fast/benchmark_results_15s_pcore_2026-02-16.jsonl:1-8, benchmarks/testing_other_di/profiles/baselines/fast/benchmark_results_15s_pcore_repeat_2026-02-16.jsonl:1-8
  IMPACT: Pinning appears useful for determinism in fast lanes, but overrides still needs a same-window unpinned repeat pair before we can call it settled.
  NEXT: If we want closure, run one unpinned overrides 15-second pass and compare drift against the existing pinned repeat pair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: User direction is now codified in codegen planning docs: benchmark commands in the deep creationcontext/no-overrides/overrides stories default to pinned runs (`DI_PIN_P_CORES=1`), and the epic benchmark gate explicitly marks pinned mode as the default for benchmark pytest/snapshot runners.
  EVIDENCE: context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:129-129, context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:65-74, context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md:64-73, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:65-74
  IMPACT: Future codegen benchmark iterations now have one documented default execution mode for reduced scheduling variance.
  NEXT: Keep using pinned mode for codegen benchmark runs unless a ticket explicitly asks for unpinned comparison.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task is implemented and validated with opt-in toggles:
- Env toggle: `DI_PIN_P_CORES=1`
- CLI toggle: `--pin-p-cores` for snapshot/codegen runners
Default behavior remains unchanged when toggles are not enabled.
Codegen epic/story benchmark gates now document pinned execution as the default mode.
