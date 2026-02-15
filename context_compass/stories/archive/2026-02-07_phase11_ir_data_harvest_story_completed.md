Completed: 2026-02-07
Summary: Implemented phase-driven IR harvest across phases 2-5 and 8-11 for Phase 12 consumption.

# Story: Phase 1-11 Codegen IR Data Harvest

## Metadata
- Story ID: STORY-2026-02-07-phase11-ir-data-harvest
- Epic: EPIC-2026-02-07-phase12-spell-scoped-execution
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07

## User Narrative
As a runtime/compiler maintainer, I want phases 1-11 to emit a stable spell-scoped Codegen IR, so that Phase 12 can generate exact executors without re-deriving runtime semantics.

## Value / MRP Alignment
This story turns existing phase work into a durable compiler contract. It keeps runtime lean and avoids duplicate interpretation logic between SpellCrafter and MeldRuntime.

## Requirements (Functional)
- Define a spell-scoped Codegen IR contract owned by SpellCrafter.
- Export normalized constructor/socket/dependency data from phases 1-5 into IR fields, without moving Phase 1 to bind.
- Export plan/patch/execution metadata from phases 8-11 into IR fields.
- Ensure IR lifecycle/invalidation follows spell lineage changes.
- Ensure Phase 12 consumes IR directly rather than rebuilding semantics from runtime branches.

## Requirements (Non-Functional)
- IR format must be deterministic for a given spell lineage version.
- IR generation must not alter existing phase behavior or public APIs.
- No runtime-only defensive fallback branches should be introduced for missing internal IR fields.

## Scope Boundaries
- In scope:
- Internal IR schema and phase-to-IR wiring in SpellCrafter.
- Spell-scoped IR storage and cleanup semantics.
- Out of scope:
- Full runtime cutover (handled by Phase 12 no-overrides story).
- Override-shape specialization cache behavior.

## Dependencies / Related Work
- `context_compass/stories/completed/2026-02-07_phase12_no_overrides_executor_story_completed.md`
- `context_compass/tasks/completed/2026-02-07_phase12_artifact_contract_task_completed.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-07-phase2-5-ir-export - Export phases 2-5 artifacts into canonical Codegen IR fields.
- [x] Task: TASK-2026-02-07-phase8-11-ir-export - Export phases 8-11 artifacts into canonical Codegen IR fields.
- [x] Task: TASK-2026-02-07-phase12-ir-handoff-wiring - Wire Phase 12 compiler input to consume the Codegen IR contract end-to-end.

## Acceptance Criteria
- SpellCrafter owns a documented Codegen IR contract with deterministic fields.
- Phase 1-11 populate all required Phase 12 input fields without runtime semantic re-derivation.
- IR is reset/invalidated correctly on lineage changes and cleanup.
- Phase 12 input path can be traced from spell bind -> phase population -> compiler handoff.

## Validation / Test Plan
- Unit tests for IR field population and invalidation boundaries.
- Integration tests ensuring phase execution still yields prior behavior.
- Focused benchmark checks for any added phase overhead.

## UX / API / Data Notes
- No user-facing API changes.
- Internal artifact names must remain explicit and spell-scoped.

## Risks / Mitigations
- Risk: IR drift from phase semantics over time.
- Mitigation: single contract owner + explicit field mapping tests per phase.
- Risk: over-collecting data inflates conjure time.
- Mitigation: collect only Phase 12-required fields and keep deterministic shape.

## Open Questions
- UNKNOWN: whether Phase 6/7 diagnostics should be included in first IR contract or remain external to Phase 12 executor input.

## Decision Log
- 2026-02-07: Phase 12 compiler input must be phase-produced, not reconstructed in runtime.
- 2026-02-07: Phase 1 remains in SpellCrafter; bind-time Phase 1 precompute is out of scope.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story introduced to make Phase 12 implementation deterministic: phases 1-11 now explicitly gather and publish the compiler contract consumed by spell-scoped codegen.

