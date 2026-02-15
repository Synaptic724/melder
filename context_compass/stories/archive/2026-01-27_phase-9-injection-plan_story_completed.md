# Story: Phase 9 injection plan compilation

- Completed: 2026-01-27
- Summary: Documented Phase 9 InjectionPlan investigation, schema, and compiler
  integration plan with evidence-backed scope, lifecycle, and validation notes.

## Metadata
- Story ID: STORY-2026-01-27-phase-9-injection-plan
- Epic: EPIC-2026-01-27-fast-path-phases-8-10
- Status: complete
- Owner:
- Priority: p1
- Created: 2026-01-27
- Updated: 2026-01-28

## User Narrative
As the meld runtime, I want injection wiring precompiled into an InjectionPlan,
so that argument resolution does not rebuild per call in the best-case path.

## Value / MRP Alignment
Phase 9 removes per-call argument wiring by compiling injection steps at conjure,
enabling the fast executor to resolve arguments with minimal branching.

## Requirements (Functional)
- Compile an InjectionPlan from existing Phase 1-7 artifacts.
- Encode argument sources, positional overrides, and contract slot bindings.
- Preserve correctness by falling back when plan is missing or stale.

## Requirements (Non-Functional)
- No new module-level mutable state.
- Plan lifecycle and invalidation rules are explicit and testable.

## Scope Boundaries
- In scope:
  - Investigation and schema definition for InjectionPlan.
  - Compiler plan for Phase 9 integration in conjure.
- Out of scope:
  - Override/mutation patch maps (Phase 10).
  - Phase 11 codegen executor.

## Dependencies / Related Work
- context_compass/artifacts/README.md
- context_compass/artifacts/README.md
- context_compass/artifacts/README.md
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-27-phase-9-injection-plan-investigation - Map current argument wiring and overrides.
- [x] Task: TASK-2026-01-27-phase-9-injection-plan-schema - Define InjectionPlan schema and lifecycle.
- [x] Task: TASK-2026-01-27-phase-9-injection-plan-compiler - Plan compiler integration and tests.

## Acceptance Criteria
- InjectionPlan scope and contents are defined with evidence references.
- Phase 9 compiler integration points and invalidation rules are documented.
- Tests required for compilation and fallback are specified.

## Validation / Test Plan
- Not run (planning only).
- Define tests for argument wiring accuracy and override fallback.

## UX / API / Data Notes
- No public API changes expected; artifacts remain internal.

## Risks / Mitigations
- Risk: injection plan misses contract variability or spellspace binding.
  Mitigation: include contract and spellspace cases in schema definition.

## Open Questions
- Which runtime inputs must be preserved for positional overrides?
- Where is the InjectionPlan stored (spell, spellcrafter, conduit)?

## Decision Log
- TBD.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Completion Notes
Phase 9 planning artifacts (investigation, schema, compiler plan) are complete
with runtime gating documented; implementation remains future work.

## Context / Handoff Summary
Story created to plan Phase 9 injection compilation work and its deliverables.
