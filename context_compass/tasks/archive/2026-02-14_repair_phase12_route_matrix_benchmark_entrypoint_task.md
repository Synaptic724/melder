Completed: 2026-02-14
Summary: Repaired Phase12 codegen benchmark entrypoint by removing stale
MeldRuntime dependencies, inlining local benchmark helper evaluators, and
regenerating fresh current-head route-matrix artifacts.

# Task: Repair Phase12 Route-Matrix Benchmark Entrypoint

## Metadata
- Task ID: TASK-2026-02-14-repair-phase12-route-matrix-benchmark-entrypoint
- Story: STORY-2026-02-13-optimize-phase12-codegen
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Repair `run_codegen_benchmark_deltas.py` imports and runtime wiring so current-head route-matrix measurements (including override-targeted routes) can run and provide fresh evidence for Phase12 prioritization.

## Scope Boundaries
- In scope:
- Benchmark import-path/runtime wiring fixes required to execute on current head.
- Updated benchmark output artifact on repaired entrypoint.
- Out of scope:
- Runtime optimization behavior changes in production code.

## Steps / Checklist
- [x] Replace stale `meld_runtime` imports with current modules/contracts.
- [x] Execute benchmark script with valid environment wiring and capture output/json artifacts.
- [x] Document baseline route ratios for warm root/spellspace/override routes.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Repaired benchmark entrypoint compatible with current codebase.
- Fresh route-matrix artifact for current head.

## Files / Paths Impacted
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
- `context_compass/artifacts/`

## Validation
- Ran:
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 5 --warmup-count 1 --allow-gate-failure --output-path context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_report_repaired.json`
- Result:
  - script completed successfully (`exit 0`) and produced new summary + JSON artifacts.
- Artifacts:
  - `context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_output_repaired.txt`
  - `context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_report_repaired.json`

## Risks / Rollback Notes
- Risk: benchmark assumptions still reference removed runtime APIs beyond import path.
- Rollback: keep script marked blocked and rely on archived route-matrix artifacts until benchmark contract is fully migrated.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: User accepted benchmark-entrypoint repair and confirmed the optimization wave improved override benchmark behavior.
  EVIDENCE: context_compass/artifacts/2026-02-14_user_reported_override_perf_test_overrides_all.txt:1-30
  IMPACT: Benchmark repair task is approved for completion move.
  NEXT: Move ticket to `tasks/completed/` and update story/board references.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Benchmark entrypoint repair is validated on head: script now executes and emits fresh gate/route reports; route ratios are documented (`warm_root_ns=6.7095e-05`, `warm_spellspace_ns=0.0027777`, `warm_override_root_args_ns=0.0004831`, `warm_override_targeted_ns=0.0008991`, `warm_mixed_ns=0.0031535`).
  EVIDENCE: context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_output_repaired.txt:1-3, context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_report_repaired.json:19-31
  IMPACT: Phase12 story is unblocked for fresh route-matrix evidence on current head and no longer depends on stale pre-repair artifacts.
  NEXT: Walk repair outcomes with user for acceptance; if approved, move task to completed and refresh phase12 story ranking notes with current report.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Benchmark repair requires more than path renaming: the script still calls `MeldRuntime` benchmark helper APIs (`_normalize_benchmark_samples`, `_median_ns`, `collect_codegen_benchmark_samples_ns`, gate/baseline evaluators) and those APIs have no surviving counterparts in current `src` modules.
  EVIDENCE: benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:9-9, benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:550-554, benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:676-683, benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:721-727, context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_output_env_root_src.txt:17-21
  IMPACT: Entrypoint migration must replace both stale import and removed helper API dependencies to run on head.
  NEXT: Inline local benchmark helper functions in `run_codegen_benchmark_deltas.py` and swap all `MeldRuntime` helper callsites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Repaired benchmark helper wiring by replacing `MeldRuntime` dependencies with local sample normalization/median/collection/gate/baseline evaluators and migrating all callsites to those local helpers.
  EVIDENCE: benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:485-751, benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:816-817, benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:942-955, benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:987-993
  IMPACT: The script no longer depends on removed `meld_runtime` modules and is ready for current-head execution validation.
  NEXT: Execute benchmark runner with `PYTHONPATH=.;src` and capture output/json artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Benchmark-entrypoint repair is now active after rank-1/rank-2 phase12 runtime tasks reached validated review status.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:6-6, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:41-49, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:6-6, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:38-46
  IMPACT: Remaining story work shifts from runtime code changes to measurement unblocking.
  NEXT: Inspect benchmark script for stale imports/runtime assumptions and patch to current CreationContext paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Current benchmark entrypoint is broken on head due stale `meld_runtime` import path and cannot produce fresh route-matrix data without migration.
  EVIDENCE: benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:9-9, context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_output_env_root_src.txt:17-21
  IMPACT: Fresh Phase12 ranking metrics are blocked until benchmark wiring is repaired.
  NEXT: Update benchmark imports/contracts and rerun to generate current-head route artifact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task objective is complete and validated in review. `run_codegen_benchmark_deltas.py`
no longer depends on removed `meld_runtime` imports/helpers and now emits fresh
current-head route-matrix artifacts. Awaiting user acceptance for closure and
move-to-completed, then phase12 story notes can be refreshed from repaired
artifacts.
