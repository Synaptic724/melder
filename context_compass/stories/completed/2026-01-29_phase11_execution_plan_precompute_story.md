# Story: Phase 11 execution plan precomputes overrides, contracts, and mutations

## Metadata
- Story ID: STORY-2026-01-29-phase11-execution-plan-precompute
- Epic: EPIC-2026-01-29-phase-system-investigation
- Status: completed
- Owner: codex
- Priority: p0
- Created: 2026-01-29
- Updated: 2026-01-29

## User Narrative
As a system owner, I want Phase 11 execution plans to precompute override, contract, and mutation routing so that meld-time execution performs minimal work and relies on prebuilt artifacts.

## Value / MRP Alignment
Moves runtime work into the phase system so the execution path is coherent, predictable, and optimized for the MRP core (correctness + durability before later optimization).

## Requirements (Functional)
- Phase 11 execution plans must carry the data needed to route overrides, contract overrides, and mutation overrides without recomputation at meld time.
- Phase 11 must be able to compile plans that remain valid when overrides or mutation overrides are present.
- Meld engine must consume Phase 11 plans directly without reconstructing override/contract routing.
- Meld runtime must use Phase 10 artifacts (override/mutation patch maps) and Phase 11 execution plans without duplicating planning work.

## Requirements (Non-Functional)
- Minimize per-meld computations; prefer precomputed maps over runtime derivation.
- Preserve docstring accuracy for any modified public methods/classes.
- No new module-level mutable state; no defensive getattr/hasattr in owned code.

## Scope Boundaries
- In scope:
  - Phase 11 plan data model and builder enhancements for overrides/contracts/mutations.
  - Phase 11 compilation flow changes to incorporate mutation overrides at compile time when required.
  - Meld engine and runtime consumption of the precomputed plan.
  - Unit test updates for Phase 11 behavior.
- Out of scope:
  - Performance profiling or micro-optimizations.
  - Changes to public API entrypoints beyond internal plan consumption.

## Dependencies / Related Work
- Epic: EPIC-2026-01-29-phase-system-investigation
- Related story: STORY-2026-01-29-phase11-fast-path-implementation

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-29-phase11-execution-plan-precompute - Implement plan precompute + tests

## Acceptance Criteria
- [x] Phase 11 execution plan includes precomputed override routing and contract override payloads.
- [x] Mutation overrides are incorporated into Phase 11 compilation flow (no runtime plan rebuild).
- [x] Meld engine uses the plan directly; no redundant override/contract computation paths remain.
- [x] Tests cover the new execution plan behavior and pass with updated expectations.

## Validation / Test Plan
- Updated unit tests for execution plan build/consume behavior.
- Ran:
  - PYTHONPATH=/workspace/melder_private pytest tests/unit/melder/aether/conduit/meld/test_meld_runtime_phase11.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_execution_plan_phase11.py tests/unit/melder/aether/conduit/meld/test_meld_engine_phase11.py -q

## UX / API / Data Notes
- Internal execution plan shape changes are acceptable; public API behavior should remain stable.

## Risks / Mitigations
- Risk: Plan precomputation mismatches runtime expectations for override payloads.
  - Mitigation: explicit unit tests for override routing and contract override application.
- Risk: Mutation overrides require plan rebuild and cause unexpected phase work.
  - Mitigation: document compile-time mutation handling and keep behavior in Phase 11 only.

## Open Questions
- None.

## Decision Log
- 2026-01-29: Plan precomputation will be the primary path; runtime/engine should not rebuild override/contract routing.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
- Phase 11 execution plans now carry precomputed override/contract routing and mutation snapshots, and runtime/engine consume them without rebuilding planning state.
