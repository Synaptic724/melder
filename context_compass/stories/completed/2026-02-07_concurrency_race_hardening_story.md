Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Story: Harden Concurrency for Phase Artifact Publish/Cleanup

## Metadata
- Story ID: STORY-2026-02-07-concurrency-race-hardening
- Epic: EPIC-2026-02-07-phase-5-7-spell-isolated-revalidation
- Status: ready
- Owner: Mark + Codex
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07

## User Narrative
As a runtime maintainer, I want phase artifact publish and lifecycle semantics to be concurrency-safe, so that concurrent meld/revalidation never fails with cleaned-artifact races.

## Value / MRP Alignment
This story directly addresses runtime stability and correctness under concurrent load, which is required for durable performance improvements.

## Requirements (Functional)
- Remove use-after-clean race windows in Phase 8/9/11 artifact replacement paths.
- Ensure artifact read/write behavior is protected by spell-level locking discipline.
- Ensure cleanup semantics remain deterministic in teardown paths.

## Requirements (Non-Functional)
- Preserve or improve throughput under benchmark concurrency scenarios.
- Avoid introducing broad/global lock contention.

## Scope Boundaries
- In scope:
- Phase artifact lifecycle behavior for OccurrencePlan/InjectionPlan/ExecutionPlan paths.
- Concurrency regression coverage for known failure signatures.
- Out of scope:
- Full engine/runtime redesign.

## Dependencies / Related Work
- `src/melder/spellbook/spell_crafter/spell_crafter.py` (Phase 8/9/11 artifact fields)
- `src/melder/spellbook/spell_crafter/blueprints/injection_plan.py`
- `tests/integration/melder/conduit/test_conduit_integration_concurrency.py`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-07-artifact-publish-discipline - Apply safe publish lifecycle for phase artifacts.
- [ ] Task: TASK-2026-02-07-spell-lock-discipline - Ensure spell-level lock usage for artifact mutation/read windows.
- [ ] Task: TASK-2026-02-07-concurrency-regression - Add/adjust tests for intermittent race reproduction coverage.

## Acceptance Criteria
- Intermittent `OccurrencePlan has already been cleaned` failures are eliminated in targeted concurrency tests.
- No regressions in existing meld/conduit integration behavior.
- Artifact cleanup remains deterministic on teardown/cleanup paths.

## Validation / Test Plan
- Run targeted concurrency integration tests repeatedly.
- Run related spellbook/conduit regression subsets.
- Record commands/results and flake rate observations.

## UX / API / Data Notes
- No API changes expected.

## Risks / Mitigations
- Risk: Fix masks one race while exposing another in plan lifecycle.
- Mitigation: Expand stress test matrix across deep/wide/contracted scenarios.
- Risk: Over-locking degrades performance.
- Mitigation: Use spell-local lock boundaries and benchmark before/after.

## Open Questions
- UNKNOWN: Exact minimal locking window needed for maximum throughput with no race.

## Decision Log
- 2026-02-07: Prioritize deterministic artifact lifecycle and spell-level lock discipline over broad lock approaches.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
This story closes the known intermittent phase artifact race that surfaces as cleaned-plan runtime failures under concurrent revalidation.

