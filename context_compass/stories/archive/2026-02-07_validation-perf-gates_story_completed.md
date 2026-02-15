Completed: 2026-02-08
Summary: Landed parity matrix, benchmark gates, docs updates, and repeatable benchmark delta scripting.

# Story: Validation and Performance Gates for Full Codegen

## Metadata
- Story ID: STORY-2026-02-07-validation-perf-gates
- Epic: EPIC-2026-02-07-full-aot-codegen-cutover
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## User Narrative
As a maintainer, I want explicit parity and perf gates, so full codegen cutover
is objectively validated and protected against regression.

## Value / MRP Alignment
Protects long-term architecture and performance outcomes.

## Requirements (Functional)
- Build explicit test matrix covering:
  all existences x overrides x mutation overrides x spellspace/borrowed contexts.
- Add assertions that generated executors are the only execution route.
- Add benchmark harness and thresholds for cold/warm/mixed workloads.

## Requirements (Non-Functional)
- Repeatable benchmark process.
- CI-friendly failure reporting for semantic/perf regressions.

## Scope Boundaries
- In scope:
- Tests, benchmarks, docs updates.
- Out of scope:
- New runtime features.

## Dependencies / Related Work
- Depends on all execution stories.

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-07-test-matrix-full-codegen-parity
- [x] Task: TASK-2026-02-07-benchmark-gates-and-regression-thresholds
- [x] Task: TASK-2026-02-07-docs-and-architecture-update-for-codegen-only
- [x] Task: TASK-2026-02-08-repeatable-codegen-benchmark-deltas

## Acceptance Criteria
- Parity test matrix passes.
- Perf thresholds met.
- Docs reflect final codegen-only model.

## Validation / Test Plan
- Unit + component + integration + benchmark validation.

## UX / API / Data Notes
- Internal quality gates only.

## Risks / Mitigations
- Risk: benchmark noise.
- Mitigation: repeated runs and median/percentile reporting.

## Open Questions
- None.

## Decision Log
- 2026-02-07: cutover is not done without explicit perf and parity gates.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story ensures full codegen rollout is measurable and enforced.
Parity matrix task is now complete with expanded generated-path coverage across
existence scopes (`many`, `unique`, `unique_per_conduit`,
`unique_per_spell_space`) and target-kind routing (`CALLER`, `OWNER`,
`SPELLSPACE`) plus override spellspace existing-instance guard validation.
Benchmark gate task is now complete with runtime-level sampling and threshold
evaluation APIs for cold/warm/mixed codegen paths, including unit-level
regression checks for pass/fail gate reporting and invalid sample rejection.
Docs/architecture task is now complete with stale `meld_engine` references
removed and architecture/components execution flows aligned to Phase 12
generated executor paths for codegen-only runtime behavior.
Repeatable benchmark delta task is now complete with a scriptable cold/warm/
mixed benchmark runner and runtime baseline median delta evaluation contract.
