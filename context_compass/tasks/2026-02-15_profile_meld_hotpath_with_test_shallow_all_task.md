# Task: Profile Melder Fast Graph Hotpaths from Shallow Lane

## Metadata
- Task ID: TASK-2026-02-15-profile-meld-hotpath-with-test-shallow-all
- Story: STORY-2026-02-15-creationcontext-phase12-codegen-discovery-refresh
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Create a dedicated pytest suite that captures cProfile artifacts for melder
first-lane routes on fast graphs only (`solo`, `shallow`, `wide`, `diamond`).

## Scope Boundaries
- In scope:
  - New benchmark test module for melder-only fast graph profiling.
  - Targeted validation run using the project interpreter.
- Out of scope:
  - Runtime optimization edits.
  - Deep graph and threaded stress benchmarking.

## Steps / Checklist
- [x] Add `benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py`.
- [x] Reuse `test_shallow_all` runtime builders to avoid duplicate wiring logic.
- [x] Ensure graph scope is fast-only (`solo`, `shallow`, `wide`, `diamond`).
- [x] Run targeted pytest and capture execution result.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- New cProfile benchmark pytest suite for melder fast graphs.
- Validation output showing targeted suite execution status.
- Persistent artifact logs (`.pstats.txt`) and benchmark rows (`benchmark_results.jsonl`).
- Structured hotspot and call-chain artifacts (`*.hotspots.json`, `*.call_chain.json`).

## Files / Paths Impacted
- `benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py`
- `context_compass/attention_board.md`
- `context_compass/tasks/2026-02-15_profile_meld_hotpath_with_test_shallow_all_task.md`

## Validation
- Ran:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s`
- Result:
  - `8 passed, 1 warning in 0.79s`
- Profile artifacts:
  - `benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_smoke_solo.prof`
  - `benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_smoke_shallow.prof`
  - `benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_smoke_wide.prof`
  - `benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_smoke_diamond.prof`
  - `benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_solo.prof`
  - `benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.prof`
  - `benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_wide.prof`
  - `benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_diamond.prof`
- Text log artifacts:
  - `benchmarks/testing_other_di/profiles/fast_graphs_melder/*.pstats.txt`
- Benchmark artifact:
  - `benchmarks/testing_other_di/profiles/fast_graphs_melder/benchmark_results.jsonl`
 - Hotspot artifacts:
   - `benchmarks/testing_other_di/profiles/fast_graphs_melder/*.hotspots.json`
- Call-chain artifacts:
  - `benchmarks/testing_other_di/profiles/fast_graphs_melder/*.call_chain.json`

## Risks / Rollback Notes
- Risk: benchmark noise from graph/mode drift.
  Rollback: keep profile suite hard-scoped to melder and explicit fast graph tuple.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Fast graph profiling scope is technically enforceable because graph selection in `test_shallow_all` is name-based and includes all required fast lanes.
  EVIDENCE: benchmarks/testing_other_di/test_shallow_all.py:598-607, benchmarks/testing_other_di/test_shallow_all.py:616-632
  IMPACT: The dedicated suite can hard-lock graph names and fail fast if any expected graph is missing.
  NEXT: Implement the new melder-only cProfile benchmark suite file and validate with targeted pytest.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Added a dedicated benchmark module that profiles melder-only fast graph routes and reuses `test_shallow_all` runtime builders to keep setup contract-aligned.
  EVIDENCE: benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:13-13, benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:70-91, benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:177-247
  IMPACT: Profiling is now isolated to requested fast graph combinations without running non-melder libraries or slow graph lanes.
  NEXT: Run targeted pytest to capture cProfile artifact set and verify execution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Targeted pytest execution passed and produced per-graph smoke/timing cProfile artifacts for all fast graph combinations.
  EVIDENCE: benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:129-150, benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:177-247
  IMPACT: Discovery now has reproducible profile artifacts for ranking CreationContext and Phase12 hotspots.
  NEXT: Review `.prof` outputs and extract top cumulative hotpaths for rank-1 optimization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: The suite now persists both textual profile summaries and benchmark timing records as artifacts for every lane execution.
  EVIDENCE: benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:126-216, benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:243-247
  IMPACT: Profiling output is durable and machine-consumable for regression tracking and benchmark comparisons across runs.
  NEXT: Parse `benchmark_results.jsonl` and top pstats entries to rank optimization targets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Structured hotspot JSON artifacts are now emitted per lane, and they include `CreationContext` and `Phase12` executor frames in top cumulative rows for timings lanes.
  EVIDENCE: benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:173-240, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.hotspots.json:1-211
  IMPACT: cProfile evidence is directly inspectable without manual `pstats` parsing and can be consumed in downstream ranking scripts.
  NEXT: Build hotspot ranking summary across all fast graph timing artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Latest fast-graph timings lane shows `solo` as the fastest (`80.7205ms`) and `wide` as the slowest (`116.4788ms`), with consistent top cumulative hotspots across graphs at `spellspace_cycle -> conduit.meld -> meld.meld -> CreationContext no-overrides executor -> Phase12 no-overrides executor`.
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/benchmark_results.jsonl:9-16, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_solo.hotspots.json:1-211, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.hotspots.json:1-211, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_wide.hotspots.json:1-211, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_diamond.hotspots.json:1-211
  IMPACT: Optimization priority should focus inside spellspace timings lane, specifically CreationContext/Phase12 execution and spellspace entry/register helpers rather than smoke-path setup.
  NEXT: Produce rank-ordered candidate list for CreationContext and Phase12 callsites using the hotspot artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: The suite now exports codegen call-chain artifacts and confirms explicit edges `meld.meld -> creation_context executor -> phase12 executor -> phase12 helper` in timings lanes.
  EVIDENCE: benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:264-408, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.call_chain.json:1-611
  IMPACT: We can inspect caller/callee chains for codegen functions directly without ad-hoc pstats commands.
  NEXT: Use call-chain artifacts to isolate highest-leverage internal helper targets for the first optimization patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Implementation and targeted validation are complete. Next step is profiling
analysis: open the generated `.prof` artifacts and rank highest-cost callpaths.
