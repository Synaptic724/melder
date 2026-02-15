# Story: Split CreationContext Hook and No-Hook Lanes

- Completed: 2026-02-13
- Summary: Closed on user request to bulk-close all active tickets in this batch.

## Metadata
- Story ID: STORY-2026-02-08-creation-context-hook-lane-split
- Epic: EPIC-2026-02-08-optimize-phase12-and-codegen-in-creation-context
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-08
- Updated: 2026-02-13

## User Narrative
As a runtime maintainer, I want explicit hook and no-hook execution doors in
CreationContext, so that lane intent is unambiguous and hot-path dispatch stays
lean.

## Value / MRP Alignment
This isolates the two execution contracts in the spell-bound context object,
which is the core MRP runtime boundary for repeated meld calls.

## Requirements (Functional)
- Define explicit compiled doors for:
  - hook lane (tuple return for activation decision),
  - no-hook overrides lane,
  - no-hook no-overrides lane.
- Keep no-hook no-overrides lane directly tied to Phase 12 no-overrides executor.
- Keep no-hook overrides lane and hook lane tied to override specialization route.

## Requirements (Non-Functional)
- No extra defensive checks at CreationContext entrance.
- Preserve lock and existence semantics.
- Avoid adding avoidable call overhead in `Meld.meld`.

## Scope Boundaries
- In scope:
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/aether/conduit/meld/meld.py`
- Out of scope:
- Phase 12 emitter algorithm changes.

## Dependencies / Related Work
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-08-creation-context-lane-doors-definition - Define explicit compiled lane doors in CreationContext.
- [x] Task: TASK-2026-02-08-meld-entry-lane-door-wiring - Wire Meld front door to explicit CreationContext lane doors.

## Acceptance Criteria
- Hook and no-hook lane doors are explicit in CreationContext fields and methods.
- Meld no-hooks path uses no-hook lane doors only.
- Meld hooks path uses hook lane door only.

## Validation / Test Plan
- Targeted meld + creation_context unit tests.
- Benchmark smoke pass for transient heavy routes.

## UX / API / Data Notes
- Internal runtime boundary only; no public API changes.

## Risks / Mitigations
- Risk: lane split changes regress activation-created semantics.
- Mitigation: assert created-flag behavior on hook lane in targeted tests.

## Open Questions
- UNKNOWN: exact microsecond delta contribution from lane-name split alone.

## Decision Log
- 2026-02-08: Keep lane split in CreationContext as explicit first milestone.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Lane split is underway. CreationContext should remain the spell-bound executor
owner while Meld performs only front-door validation and lane selection.
