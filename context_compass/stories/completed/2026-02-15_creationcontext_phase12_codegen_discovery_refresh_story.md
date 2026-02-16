# Story: CreationContext and Phase12 Discovery Refresh

Completed: 2026-02-16
Summary: Closed after user acceptance; melder fast-graph and overrides
profiling discovery tasks are complete with durable artifact outputs.

## Metadata
- Story ID: STORY-2026-02-15-creationcontext-phase12-codegen-discovery-refresh
- Epic: EPIC-2026-02-15-creationcontext-phase12-codegen-optimization
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-16

## User Narrative
As a runtime maintainer, I want a fast and repeatable melder-only profiling lane,
so that we can rank `CreationContext` and `Phase12` hotspots on current head.

## Value / MRP Alignment
This discovery slice provides measurable hotspot evidence before optimization edits,
which keeps the performance plan contract-safe and reviewable.

## Requirements (Functional)
- Use a dedicated pytest cProfile suite that targets `melder` only.
- Cover fast graph combinations only: `solo`, `shallow`, `wide`, `diamond`.
- Use the first `test_shallow_all` lane behavior (`single_resolve` smoke/timing routes).

## Requirements (Non-Functional)
- Keep profiling runs fast enough for repeated local iteration.
- Persist profile artifacts (`.prof`) for deterministic follow-up analysis.

## Scope Boundaries
- In scope:
- New benchmark test suite for melder fast-graph cProfile capture.
- Routing updates for active task execution.
- Out of scope:
- Runtime code optimizations in `CreationContext`/`Phase12`.
- Threaded stress lanes and `deep` graph profiling.

## Dependencies / Related Work
- `context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md`
- `benchmarks/testing_other_di/test_shallow_all.py`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-15-profile-meld-hotpath-with-test-shallow-all - Add melder fast-graph cProfile pytest suite and validate targeted execution.
- [x] Task: TASK-2026-02-15-profile-melder-overrides-graph-callchain - Add melder overrides-graph cProfile suite with call-chain artifacts and validate targeted execution.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- New benchmark suite exists and is melder-only.
- Suite limits graphs to `solo`, `shallow`, `wide`, `diamond`.
- Targeted pytest run passes with profile artifacts generated.

## Validation / Test Plan
- `PYTHONPATH=src` and run:
  - `.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s`

## UX / API / Data Notes
- Test-only delivery; no public API change.

## Risks / Mitigations
- Risk: profiling suite accidentally includes slow graph lane.
  Mitigation: hard-code fast graph name tuple and assert it resolves from `_all_graphs()`.

## Open Questions
- Which fast graph contributes highest cumulative runtime in the first profiling pass?

## Decision Log
- 2026-02-15: Discovery narrowed to melder fast graphs (`solo`, `shallow`, `wide`, `diamond`) per user direction.

## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: `test_shallow_all` first-lane tests (`test_single_resolve_smoke`, `test_single_resolve_timings`) provide the exact route shape needed for fast cProfile capture.
  EVIDENCE: benchmarks/testing_other_di/test_shallow_all.py:1583-1630, benchmarks/testing_other_di/test_shallow_all.py:1602-1630
  IMPACT: We can build a dedicated cProfile suite without inventing new runtime wiring.
  NEXT: Add a melder-only benchmark test module that reuses `_build_ops(...)` and fast graph specs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Both linked profiling tasks are completed and moved to `tasks/completed` with acceptance confirmed.
  EVIDENCE: context_compass/tasks/completed/2026-02-15_profile_meld_hotpath_with_test_shallow_all_task.md:1-20, context_compass/tasks/completed/2026-02-15_profile_melder_overrides_graph_callchain_task.md:1-20
  IMPACT: Discovery implementation work is complete; story is now pending story-level closure confirmation only.
  NEXT: Confirm story closure with user and move to `stories/completed` when approved.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Discovery implementation is complete and both linked tasks are now closed in
`tasks/completed`. Story closed after user acceptance.
