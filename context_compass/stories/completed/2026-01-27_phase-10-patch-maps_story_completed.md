# Story: Phase 10 override and mutation patch maps

- Completed: 2026-01-27
- Summary: Documented Phase 10 patch-map scope, schema, compiler integration
  plan, and fallback cases with evidence and test requirements.

## Metadata
- Story ID: STORY-2026-01-27-phase-10-patch-maps
- Epic: EPIC-2026-01-27-fast-path-phases-8-10
- Status: complete
- Owner:
- Priority: p1
- Created: 2026-01-27
- Updated: 2026-01-28

## User Narrative
As the meld runtime, I want override and mutation patch maps precompiled,
so that supported override cases can stay on the fast path without graph rebuilds.

## Value / MRP Alignment
Phase 10 provides patchable override and mutation handling while preserving
correctness via explicit fallback when cases are unsupported.

## Requirements (Functional)
- Define patch map model for overrides and mutation overrides.
- Compile patch maps from Phase 1-7 artifacts and wiring metadata.
- Document which override/mutation cases are supported in fast path.

## Requirements (Non-Functional)
- No new module-level mutable state.
- Patch map lifecycle and invalidation rules are explicit and testable.

## Scope Boundaries
- In scope:
  - Investigation and schema definition for patch maps.
  - Compiler plan for Phase 10 integration in conjure.
- Out of scope:
  - Full override/mutation redesign.
  - Phase 11 codegen executor.

## Dependencies / Related Work
- context_compass/artifacts/fast_path_meld_plan/ticket3_fast_path_github.md
- context_compass/artifacts/fast_path_meld_plan/research_override_mutation.md
- context_compass/artifacts/fast_path_meld_plan/codex_exploration/meld_route_matrix_2026-01-26.md
- src/melder/aether/conduit/meld/overrides/graph_mutator.py
- src/melder/aether/conduit/meld/overrides/spell_overrider.py

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-27-phase-10-patch-map-investigation - Map override/mutation flows and targets.
- [x] Task: TASK-2026-01-27-phase-10-patch-map-schema - Define patch map model and lifecycle.
- [x] Task: TASK-2026-01-27-phase-10-patch-map-compiler - Plan compiler integration and tests.

## Acceptance Criteria
- Patch map scope and supported cases are documented with evidence.
- Phase 10 compiler integration points and invalidation rules are documented.
- Tests required for patching and fallback are specified.

## Validation / Test Plan
- Not run (planning only).
- Define tests for patchable overrides and mutation fallback.

## UX / API / Data Notes
- No public API changes expected; artifacts remain internal.

## Risks / Mitigations
- Risk: patch maps drift from runtime override semantics.
  Mitigation: trace and document override/mutation entry points with evidence.

## Open Questions
- Which override and mutation cases are safe to patch without rebuild?
- How do patch maps interact with contract bindings?

## Decision Log
- TBD.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Completion Notes
Phase 10 planning artifacts (investigation, schema, compiler plan) are complete
with patch map scope and fallback behavior documented; implementation remains
future work.

## Context / Handoff Summary
Story created to plan Phase 10 patch map compilation work and its deliverables.
