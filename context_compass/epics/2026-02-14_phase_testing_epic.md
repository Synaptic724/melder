# Epic: Phase Testing (Component CProfile)

## Metadata
- Epic ID: EPIC-2026-02-14-phase-testing
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14
- Target Window: 2026-Q1
- Related Program/Initiative: Conjure Optimization Wave

## Problem / Opportunity
Current profiling around conjure phases is mixed with scheduler orchestration
(phase registration, queueing, worker lifecycle, UnitOfWork/Future barriers).
That makes it hard to isolate pure phase execution costs and optimize phase
logic directly.

## MRP Alignment (Most Reasonable Product)
We need a stable component-level profiling harness that measures phase logic in
isolation and remains reproducible under `cProfile` (single-threaded,
deterministic). This creates a reliable optimization foundation before deeper
runtime changes.

## Goals (Outcomes)
- Build a component test suite that profiles phase methods directly.
- Exclude `PhaseScheduler`, worker threads, and `UnitOfWork` from measured paths.
- Support boolean-gated phase chaining so we can profile grouped pipelines.
- Produce repeatable printed profile output suitable for task-level optimization.
- Cover grouped baselines for all conjure phase families (1-4, 5-7, 8-11).

## Non-Goals (Explicit Exclusions)
- Replacing production phase scheduling contracts.
- Changing runtime semantics during this planning pass.
- Integration benchmarking of full conjure flows in this epic setup step.

## Scope Boundaries
- In scope:
- Component test harness and profiling utilities for direct phase invocation.
- Grouped profiling tracks for phases 1-4 and phases 5-7.
- Grouped profiling track for phases 8-11.
- Target-local (single-spell) 5-7 profiling track.
- Out of scope:
- Multithreaded scheduler profiling.
- Phase 8-11 optimization execution (can be added after discovery).

## Success Metrics
- Epic has discovery-first stories/tasks for each phase-group profile track.
- Harness requirements are explicit: no scheduler, no workers, no UnitOfWork.
- Story outputs produce actionable optimization candidates with evidence.

## Requirements (Functional + Non-Functional)
- Component tests must run with `pytest` and support `cProfile`.
- Profiling path must be single-threaded.
- Harness must allow toggling grouped chains via explicit booleans.
- Printed output must include per-group timing/profile summaries.

## Constraints / Assumptions
- Constraints:
- Preserve current phase contracts and call ordering semantics per group.
- Keep changes scoped to component test harness/docs/tickets at first.
- Assumptions:
- Existing spell fixtures/deep-layer graphs remain available.

## Dependencies / External References
- `src/melder/spellbook/spell.py`
- `src/melder/spellbook/spellbook_creation_system.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `benchmarks/testing_other_di/test_melder_hotpath_profiles.py`
- `context_compass/WORKFLOW.md`

## Milestones (Track Progress)
- [ ] Milestone 1: Define and validate component profiling harness contract.
- [ ] Milestone 2: Capture baseline profile outputs for 1-4, 5-7, and 8-11 groups.
- [ ] Milestone 3: Convert baseline findings into ranked optimization tasks.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-14-phase-component-cprofile-harness - Build direct-call component cprofile harness with toggleable phase chains.
- [ ] Story: STORY-2026-02-14-phase-group-1-4-baseline - Baseline profile for structural phases 1-4 using direct phase calls.
- [ ] Story: STORY-2026-02-14-phase-group-5-7-conduit-baseline - Baseline profile for conduit-wide foundational phases 5-7.
- [ ] Story: STORY-2026-02-14-phase-group-5-7-local-baseline - Baseline profile for target-local foundational phases 5-7.
- [ ] Story: STORY-2026-02-14-phase-group-8-11-baseline - Baseline profile for conduit plan phases 8-11 using direct phase calls.
- [ ] Story: STORY-2026-02-14-phase-testing-optimization-backlog - Convert baseline findings into optimization leads/tasks.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-02-14-phase-component-cprofile-harness.
- [ ] Task: Complete story STORY-2026-02-14-phase-group-1-4-baseline.
- [ ] Task: Complete story STORY-2026-02-14-phase-group-5-7-conduit-baseline.
- [ ] Task: Complete story STORY-2026-02-14-phase-group-5-7-local-baseline.
- [ ] Task: Complete story STORY-2026-02-14-phase-group-8-11-baseline.
- [ ] Task: Complete story STORY-2026-02-14-phase-testing-optimization-backlog.

## Acceptance Criteria (Epic Done)
- Component harness exists and runs without `PhaseScheduler`/workers/UnitOfWork.
- Baseline profiles exist for grouped phase tracks (1-4, 5-7, 8-11) with reproducible output.
- Optimization backlog tasks are created from measured data.

## Risks / Mitigations
- Risk: component harness drifts from production execution semantics.
  Mitigation: keep group ordering and call boundaries explicitly mapped to
  existing phase facade methods.
- Risk: conflating conduit-wide and local 5-7 behavior.
  Mitigation: keep separate stories/tracks for conduit-wide vs target-local.

## Validation / Test Approach
- `pytest` component tests with `cProfile` instrumentation.
- Deterministic, single-threaded execution only.
- No benchmark timing claims without recorded output.

## Rollout / Adoption Plan
- Implement discovery story first (harness contract + path mapping).
- Capture baseline profiles per story group.
- Promote measured hotspots into optimization implementation tasks.

## Open Questions
- Should local target 8-11 baseline be tracked as a separate story after conduit-wide 8-11 discovery?
- What canonical fixture set should be used for default profile runs?

## Decision Log
- 2026-02-14: User requested a dedicated phase-testing epic using component
  cprofile paths with no scheduler/worker/unit-of-work runtime.
- 2026-02-14: Added an explicit conduit-wide 8-11 discovery baseline story so
  the phase-testing discovery plan covers all conjure phase groups.

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: There are two 5-7 families today: conduit-wide foundational phases and target-local foundational phases.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1063, src/melder/spellbook/spellbook_creation_system.py:1206
  IMPACT: The new component suite should baseline both families separately.
  NEXT: Execute discovery stories for harness and both 5-7 profile tracks.

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Target-local 5-7 phases are single-unit registrations in current scheduler wiring.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1165, src/melder/spellbook/spellbook_creation_system.py:1192
  IMPACT: Confirms a direct-call local 5-7 component profile track is meaningful and bounded.
  NEXT: Capture equivalent direct-call path in component harness design.

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conduit plan phases are an explicit grouped chain (occurrence, injection, patch maps, execution plan) in creation-system orchestration.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1111, src/melder/spellbook/spellbook_creation_system.py:1121, src/melder/spellbook/spell.py:1067, src/melder/spellbook/spell.py:1140
  IMPACT: A dedicated 8-11 baseline story is required for all-phase coverage.
  NEXT: Execute 8-11 discovery task after harness and 1-4/5-7 discovery setup is locked.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic created for component-level phase profiling with explicit isolation from
scheduler and worker orchestration overhead. Planned flow is discovery-first
across harness design, 1-4 baseline, conduit-wide 5-7 baseline, target-local
5-7 baseline, conduit-wide 8-11 baseline, then optimization backlog generation.
