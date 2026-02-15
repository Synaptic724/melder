# Story: Phase 8 occurrence plan compilation

- Completed: 2026-01-27
- Summary: Archived Phase 8 occurrence plan planning ticket per user direction;
  checklist items remain as recorded below.

## Metadata
- Story ID: STORY-2026-01-27-phase-8-occurrence-plan
- Epic: EPIC-2026-01-27-fast-path-phases-8-10
- Status: complete
- Owner:
- Priority: p1
- Created: 2026-01-27
- Updated: 2026-01-27

## User Narrative
As the meld runtime, I want occurrence order and reuse decisions precompiled,
so that meld does not rebuild occurrence graphs per call in the best-case path.

## Value / MRP Alignment
Phase 8 moves occurrence graph work into conjure, creating a durable plan
artifact that enables tight-loop execution with minimal branching.

## Requirements (Functional)
- Compile an OccurrencePlan from existing Phase 1-7 artifacts.
- Encode occurrence order, per-path expansion, and existence-specific actions.
- Preserve correctness by deferring to slow path when plan is missing or stale.

## Requirements (Non-Functional)
- No new module-level mutable state.
- Plan lifecycle and invalidation rules are explicit and testable.

## Scope Boundaries
- In scope:
  - Investigation and schema definition for OccurrencePlan.
  - Compiler plan for Phase 8 integration in conjure.
- Out of scope:
  - Phase 11 codegen executor.
  - Override/mutation patch maps (Phase 10).

## Dependencies / Related Work
- context_compass/artifacts/README.md
- context_compass/artifacts/README.md
- context_compass/artifacts/README.md
- src/melder/spellbook/spell_crafter/spell_crafter.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-01-27-phase-8-occurrence-plan-investigation - Map current occurrence planning inputs/outputs.
- [ ] Task: TASK-2026-01-27-phase-8-occurrence-plan-schema - Define OccurrencePlan schema and lifecycle.
- [ ] Task: TASK-2026-01-27-phase-8-occurrence-plan-compiler - Plan compiler integration and tests.

## Acceptance Criteria
- OccurrencePlan scope and contents are defined with evidence references.
- Phase 8 compiler integration points and invalidation rules are documented.
- Tests required for compilation and fallback are specified.

## Validation / Test Plan
- Not run (planning only).
- Define tests for compilation correctness and stale-plan fallback.

## UX / API / Data Notes
- No public API changes expected; artifacts remain internal.

## Risks / Mitigations
- Risk: OccurrencePlan misses edge cases for Existence.many or spellspace.
  Mitigation: include per-path and spellspace cases in schema definition.

## Open Questions
- Which artifact is the canonical input for occurrence ordering?
- Where is the OccurrencePlan stored (spell, spellcrafter, conduit)?

## Decision Log
- TBD.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created to plan Phase 8 occurrence compilation work and its deliverables.
