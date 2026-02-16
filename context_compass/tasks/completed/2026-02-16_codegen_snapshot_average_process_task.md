# Task: Build Average-Based Snapshot Benchmark Process (Non-cProfile)

Completed: 2026-02-16
Summary: Implemented and validated the non-cProfile averaged snapshot runner
for fast/overrides lanes, including baseline-compare output and durable artifacts.

## Metadata
- Task ID: TASK-2026-02-16-codegen-snapshot-average-process
- Story: STORY-2026-02-16-deep-creation-context-codegen-strategy-discovery
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## Objective
Implement a dedicated benchmark snapshot process that is separate from cProfile and reports stable average-based outcomes for the same Melder fast/override benchmark lanes used throughout the ticket stream.

## Scope Boundaries
- In scope:
- `benchmarks/testing_other_di/run_snapshot_timings.py`
- Snapshot artifact output under `benchmarks/testing_other_di/profiles/overrides_graphs_melder/`
- Ticket + board routing updates for this process
- Out of scope:
- Runtime codegen behavior changes in `src/melder/**`
- Replacing existing cProfile benchmark tests

## Steps / Checklist
- [x] Capture baseline process requirements from current benchmark lanes and graph selectors.
- [x] Implement a non-cProfile snapshot runner with averaged timing statistics.
- [x] Support configurable iteration count (default 1000, allow 10000+) and warmup controls.
- [x] Emit JSON + text artifacts with per-lane/per-graph stats and aggregate lane summaries.
- [x] Support baseline comparison mode (pre vs post snapshot deltas).
- [x] Smoke-run the new script with reduced iterations to verify contract and output shape.
- [x] Update ticket notes with measurement artifacts and announce process readiness.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- New script: `benchmarks/testing_other_di/run_snapshot_timings.py`
- Snapshot artifacts for one smoke run (JSON + summary text)
- Ticket notes proving the process is separate from cProfile and uses averaged runs

## Benchmark Gate (Mandatory for Follow-on Optimization Slices)
- Pre-test baseline:
  - Run snapshot script before code edit with `--snapshot-label <candidate>_prebaseline`.
- Post-test snapshot:
  - Re-run script after code edit with `--snapshot-label <candidate>_posttest`.
- Decision policy:
  - Compare post snapshot against prebaseline and retained checkpoint artifacts.
  - If regression or non-winning deltas are observed, raise `RESULT: DECISION_REQUEST` and wait for user keep/revert direction.
  - If user selects revert, execute one post-revert snapshot run and record `RESULT: REVERTED`.

## Files / Paths Impacted
- `context_compass/attention_board.md`
- `context_compass/tasks/completed/2026-02-16_creationcontext_codegen_low_risk_discovery_task.md`
- `context_compass/tasks/completed/2026-02-16_codegen_snapshot_average_process_task.md`
- `benchmarks/testing_other_di/run_snapshot_timings.py`

## Validation
- Executed:
  - `python -m py_compile benchmarks/testing_other_di/run_snapshot_timings.py`
  - `python benchmarks/testing_other_di/run_snapshot_timings.py --iterations 25 --warmup-iters 5 --snapshot-label smoke_snapshot_process`
  - `python benchmarks/testing_other_di/run_snapshot_timings.py --iterations 10 --warmup-iters 2 --snapshot-label smoke_snapshot_compare --baseline-json benchmarks/testing_other_di/profiles/overrides_graphs_melder/smoke_snapshot_process_snapshot_2026-02-16_12-15-56.json --max-regression-pct 999999`
  - `python benchmarks/testing_other_di/run_snapshot_timings.py --iterations 10 --warmup-iters 2 --snapshot-label smoke_snapshot_gatecheck2 --baseline-json benchmarks/testing_other_di/profiles/overrides_graphs_melder/smoke_snapshot_process_snapshot_2026-02-16_12-15-56.json --max-regression-pct 0` (`LASTEXIT:2`, expected threshold failure)
  - `python benchmarks/testing_other_di/run_snapshot_timings.py --iterations 1000 --warmup-iters 100 --snapshot-label wave3_snapshot_process_baseline_2026-02-16`
  - `python benchmarks/testing_other_di/run_snapshot_timings.py --iterations 10000 --warmup-iters 200 --snapshot-label wave3_snapshot_process_10k_2026-02-16`
- Artifacts:
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/smoke_snapshot_process_snapshot_2026-02-16_12-15-56.json`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/smoke_snapshot_process_snapshot_summary_2026-02-16_12-15-56.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/smoke_snapshot_compare_snapshot_2026-02-16_12-16-04.json`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/smoke_snapshot_compare_snapshot_summary_2026-02-16_12-16-04.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/smoke_snapshot_gatecheck2_snapshot_2026-02-16_12-17-37.json`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/smoke_snapshot_gatecheck2_snapshot_summary_2026-02-16_12-17-37.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_snapshot_process_baseline_2026-02-16_snapshot_2026-02-16_12-16-23.json`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_snapshot_process_baseline_2026-02-16_snapshot_summary_2026-02-16_12-16-23.txt`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_snapshot_process_10k_2026-02-16_snapshot_2026-02-16_12-16-31.json`
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_snapshot_process_10k_2026-02-16_snapshot_summary_2026-02-16_12-16-31.txt`

## Risks / Rollback Notes
- Risk: Long 10k runs can consume significant wall time.
- Mitigation: keep default at 1000, provide explicit 10000 opt-in.
- Rollback: script-only change; safe to revert file and board/ticket routing if needed.

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
  CLAIM: Current Melder fast and overrides cProfile benchmarks already expose stable melder-only graph builders and fast-graph selectors, so a non-cProfile snapshot runner can reuse these exact builders and preserve benchmark comparability.
  EVIDENCE: benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:15-15, benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:637-655, benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:15-15, benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:135-149
  IMPACT: We can keep benchmark lane parity while removing profiler overhead from measurement snapshots.
  NEXT: Implement script that imports these builders and runs averaged loops directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: The underlying shallow benchmark suite already includes average-call timing semantics (`_average_call_ns`) and canonical graph registry/build ops helpers, so average-based snapshot math aligns with existing benchmark intent.
  EVIDENCE: benchmarks/testing_other_di/test_shallow_all.py:62-79, benchmarks/testing_other_di/test_shallow_all.py:603-627, benchmarks/testing_other_di/test_shallow_all.py:1166-1176
  IMPACT: The new process can remain contract-consistent with prior benchmark language (average timings, same graph lanes).
  NEXT: Implement per-lane timing loops that compute mean/median/std/min/max and persist artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Implementation plan is to create `run_snapshot_timings.py` with CLI controls for iterations/warmup/graphs and baseline comparison output, then smoke-run once before broader usage.
  EVIDENCE: benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:689-724, benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:663-692, benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:452-563
  IMPACT: This provides a reusable pre/post snapshot process with stable averages and explicit delta reporting.
  NEXT: Implement script and run low-iteration smoke validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Implemented `run_snapshot_timings.py` as a non-cProfile snapshot runner that measures both normal fast lanes and override lanes, computes descriptive stats, and supports optional baseline delta comparison with regression gating.
  EVIDENCE: benchmarks/testing_other_di/run_snapshot_timings.py:120-151, benchmarks/testing_other_di/run_snapshot_timings.py:240-342, benchmarks/testing_other_di/run_snapshot_timings.py:412-478, benchmarks/testing_other_di/run_snapshot_timings.py:592-682
  IMPACT: We now have one reusable benchmark command for averaged pre/post snapshots across both benchmark families, including 1000 default and 10000-capable iterations.
  NEXT: Run smoke validation with reduced iterations, then record artifact paths and readiness status.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Validation runs succeeded for smoke, baseline-compare, 1000-iteration baseline, and 10000-iteration snapshot modes; summary artifacts confirm both fast and overrides lanes are measured and reported in averaged form.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/smoke_snapshot_process_snapshot_summary_2026-02-16_12-15-56.txt:1-33, benchmarks/testing_other_di/profiles/overrides_graphs_melder/smoke_snapshot_compare_snapshot_summary_2026-02-16_12-16-04.txt:1-52, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_snapshot_process_baseline_2026-02-16_snapshot_summary_2026-02-16_12-16-23.txt:1-33, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_snapshot_process_10k_2026-02-16_snapshot_summary_2026-02-16_12-16-31.txt:1-33
  IMPACT: The ticket now has a working averaged snapshot process that can replace single-run cProfile timing snapshots for pre/post decision quality.
  NEXT: Update board/ticket routing with process readiness and announce the new command contract for upcoming optimization slices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Regression-threshold gating is active: a strict `--max-regression-pct 0` comparison intentionally failed and returned exit code 2 when baseline deltas regressed.
  EVIDENCE: benchmarks/testing_other_di/run_snapshot_timings.py:707-716, benchmarks/testing_other_di/profiles/overrides_graphs_melder/smoke_snapshot_gatecheck2_snapshot_summary_2026-02-16_12-17-37.txt:36-39
  IMPACT: The snapshot process can enforce fail-fast gate behavior in automation instead of requiring manual interpretation only.
  NEXT: Use this threshold mode selectively in post-test candidate runs when we need strict automated regression rejection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Snapshot process is ready for adoption as the default pre/post benchmark gate for upcoming codegen slices, with both normal and override lanes included in every run.
  EVIDENCE: benchmarks/testing_other_di/run_snapshot_timings.py:240-342, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_snapshot_process_baseline_2026-02-16_snapshot_summary_2026-02-16_12-16-23.txt:6-33
  IMPACT: Next optimization attempts can be evaluated on high-repeat averages (1000 default, 10000 optional) with optional automated regression exit behavior.
  NEXT: Use `run_snapshot_timings.py` for next candidate pre/post snapshots and record `RESULT` notes from those artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task decouples performance snapshots from cProfile overhead while preserving fast and overrides benchmark lane parity. Implementation and validation are complete for smoke, baseline-compare, 1000-iteration, and 10000-iteration runs; next action is process announcement and adoption as the default pre/post gate for follow-on codegen slices.
