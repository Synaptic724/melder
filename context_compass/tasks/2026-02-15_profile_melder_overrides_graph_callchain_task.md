# Task: Profile Melder Overrides Graph Call Chains

## Metadata
- Task ID: TASK-2026-02-15-profile-melder-overrides-graph-callchain
- Story: STORY-2026-02-15-creationcontext-phase12-codegen-discovery-refresh
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Add a dedicated melder overrides-graph profiling suite that exports cProfile,
hotspot, and caller/callee chain artifacts per graph lane.

## Scope Boundaries
- In scope:
  - New benchmark test module for melder override graph lanes.
  - Graph-lane call-chain artifacts for codegen/phase12 override paths.
  - Targeted pytest validation using the project interpreter.
- Out of scope:
  - Runtime optimization edits.
  - Non-melder override library profiling.

## Steps / Checklist
- [x] Add `benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py`.
- [x] Reuse `test_overrides_all` graph specs and runtime builders.
- [x] Persist `.prof`, `.pstats.txt`, `.hotspots.json`, `.call_chain.json`, and JSONL benchmark rows.
- [x] Run targeted pytest and capture execution result.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Dedicated melder overrides graph cProfile suite.
- Durable profiling and call-chain artifact set per graph lane.
- Validation output from targeted pytest run.

## Files / Paths Impacted
- `benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py`
- `context_compass/attention_board.md`
- `context_compass/tasks/2026-02-15_profile_melder_overrides_graph_callchain_task.md`

## Validation
- Ran:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (post-compaction readability verification rerun)
- Result:
  - `8 passed, 1 warning in 0.82s` (fast graphs)
  - `8 passed, 1 warning in 0.39s` (override graphs rerun)
- Artifact directory:
  - `benchmarks/testing_other_di/profiles/overrides_graphs_melder`
  - `benchmarks/testing_other_di/profiles/fast_graphs_melder`
- Artifact types:
  - `.prof`
  - `.pstats.txt`
  - `.hotspots.json`
  - `.call_chain.json`
  - `.summary.txt`
  - `benchmark_results.jsonl`

## Risks / Rollback Notes
- Risk: graph lane includes non-override code paths that dilute override-chain signal.
  Rollback: keep lane set explicit and tag each artifact by graph name.

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
  TYPE: MEASURE
  CLAIM: Re-ran both profiler suites after the readability patch; both passed and now emit concise human-readable hotspot/call-chain summaries to console and per-lane `.summary.txt` artifacts.
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:1-29, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:1-29, benchmarks/testing_other_di/profiles/fast_graphs_melder/benchmark_results.jsonl:1-8, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:1-8
  IMPACT: Profile output is now readable without opening JSON files, while retaining durable artifact files for later ranking and comparison.
  NEXT: Continue hotspot ranking on override lanes and compare against fast-graph non-override lanes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: UNKNOWN
  CLAIM: Post-compaction state did not retain final validation output for the new plain-text summary patch, so current pass/fail status for both profiler suites is unknown until rerun.
  EVIDENCE: benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py:1-673, benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:1-663
  IMPACT: We cannot claim readable-summary output is verified until both targeted pytest modules are rerun and artifacts are inspected.
  NEXT: Run both profiler pytest modules and confirm console summary lines plus `.summary.txt` artifact generation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: `test_overrides_all` already contains graph specs and a melder override runtime builder, so a call-chain benchmark can reuse those internals without reimplementing override wiring.
  EVIDENCE: benchmarks/testing_other_di/test_overrides_all.py:256-334, benchmarks/testing_other_di/test_overrides_all.py:546-608, benchmarks/testing_other_di/test_overrides_all.py:667-763
  IMPACT: New profiling suite can stay focused on artifact capture and lane control instead of duplicating override runtime logic.
  NEXT: Implement overrides graph cProfile suite with the same artifact model used in the fast-graph non-override benchmark.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Added a dedicated melder overrides graph benchmark suite that mirrors fast-graph artifact behavior and includes codegen caller/callee chain export.
  EVIDENCE: benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py:1-603
  IMPACT: Override lanes now produce durable call-chain evidence in the same format as the existing non-override profiler.
  NEXT: Validate execution and confirm override-path codegen edges appear in call-chain artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Targeted pytest passed and generated override call-chain artifacts that show `meld -> creation_context_overrides executor -> phase12_overrides executor` edges on payload graphs.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.call_chain.json:1-611, benchmarks/testing_other_di/profiles/overrides_graphs_melder/benchmark_results.jsonl:1-8
  IMPACT: We can now inspect override-path codegen call chains per graph without ad-hoc profiling commands.
  NEXT: Rank override-specific helper hotspots and compare to non-override lanes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Normal (non-override) call-chain artifacts explicitly show `meld -> creation_context_no_overrides executor -> phase12_no_overrides executor` and downstream phase12 helper calls (`_register_spell_instance`, `_get_existing_creation`, `_construct_spell_instance`).
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.call_chain.json:1-918
  IMPACT: We can reason about normal-lane execution with concrete caller/callee edges, not only hotspot totals.
  NEXT: Use these edges to prioritize no-overrides helper optimization alongside override-path tuning.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: A true one-shot normal lane profile (`single meld` via `get_root_a`) still traverses the codegen path, and the artifact records 146 total profiled functions with explicit `meld -> creation_context_no_overrides -> phase12_no_overrides` edges.
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/single_meld_shallow.call_chain.json:1-163
  IMPACT: The prior 4,400-call counts were loop amplification; single-call tracing is now isolated and inspectable.
  NEXT: Use one-shot artifacts for chain comprehension and looped artifacts for hotspot ranking.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Overrides graph call-chain benchmark suite is implemented and validated, and
both profiler suites now emit readable console summaries plus per-lane
`.summary.txt` artifacts. Next step is ranked hotspot analysis for override
lanes and comparison against non-override fast-graph results.
