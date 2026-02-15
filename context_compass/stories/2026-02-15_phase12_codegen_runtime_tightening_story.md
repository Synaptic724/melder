# Story: Phase12 and CreationContext Runtime Tightening

## Metadata
- Story ID: STORY-2026-02-15-phase12-codegen-runtime-tightening
- Epic: EPIC-2026-02-15-creationcontext-phase12-codegen-optimization
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## User Narrative
As a runtime maintainer, I want hotspot-led codegen runtime optimizations in
Phase12 and CreationContext, so that meld-path latency drops without changing
resolution contracts.

## Value / MRP Alignment
This story implements the first optimization tranche from measured cProfile
evidence and keeps changes small, reviewable, and contract-safe.

## Requirements (Functional)
- Implement at least one measurable optimization in Phase12/CreationContext
  runtime codegen path.
- Preserve no-overrides and overrides runtime behavior and resolution outputs.
- Keep optimization scope inside codegen/runtime helper path (no API redesign).

## Requirements (Non-Functional)
- Keep performance claims evidence-backed.
- Keep behavior deterministic and compatible with current tests.

## Scope Boundaries
- In scope:
- Runtime hotpath edits in `phase12_*_executor.py` and/or
  `creation_context.py`/codegen helpers.
- Targeted benchmark+pytest reruns for changed lanes.
- Out of scope:
- Broad refactors outside codegen runtime path.
- Policy/contract behavior changes.

## Dependencies / Related Work
- `context_compass/tasks/2026-02-15_profile_meld_hotpath_with_test_shallow_all_task.md`
- `context_compass/tasks/2026-02-15_profile_melder_overrides_graph_callchain_task.md`
- `benchmarks/testing_other_di/profiles/fast_graphs_melder/*.summary.txt`
- `benchmarks/testing_other_di/profiles/overrides_graphs_melder/*.summary.txt`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-15-optimize-phase12-creationcontext-codegen-wave1 - Implement first hotspot optimization patch and validate.
- [ ] Enforce Ticket Microcycle across linked tasks.
- [ ] Require meaningful-finding note updates during investigation and implementation.

## Acceptance Criteria
- At least one hotspot-led optimization patch is implemented.
- Targeted profiler/pytest lanes pass after the patch.
- Summary artifacts remain readable and continue to be emitted.

## Validation / Test Plan
- `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s`
- `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s`

## Risks / Mitigations
- Risk: hotpath tuning changes semantics or override behavior.
  Mitigation: keep changes local to helper internals and validate both fast and override suites.

## Decision Log
- 2026-02-15: Story opened from validated cProfile evidence to begin runtime optimization wave 1.

## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Current-head profile summaries show Phase12 runtime helpers as dominant codegen frames in timings lanes for both no-overrides and overrides paths.
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:1-29, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:1-29
  IMPACT: First optimization slice should prioritize Phase12 helper path rather than setup/compile-only paths.
  NEXT: Create and route to a wave-1 implementation task with concrete hotspot targets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Wave-1 runtime tightening story is active. Immediate next step is implementing
the first hotspot optimization patch with targeted benchmark validation.
