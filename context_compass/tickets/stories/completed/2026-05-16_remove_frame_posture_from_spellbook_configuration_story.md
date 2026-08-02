# Story: Remove Frame Posture From SpellbookConfiguration
- Completed: 2026-05-16T15:47:45Z
- Summary: Closed after removing frame posture from SpellbookConfiguration and completing the final owner-boundary migration.


## Metadata
- Story ID: STORY-2026-05-16-remove-frame-posture-from-spellbook-configuration
- Epic: EPIC-2026-05-16-migrate-frame-posture-ownership-into-aetheric-frame
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-16T13:30:44Z
- Updated: 2026-05-16T15:47:45Z

## User Narrative
As the project owner, I want frame posture removed from `SpellbookConfiguration`
first, so the owner boundary is clean before we do anything more complex.

## Value / MRP Alignment
This is the minimum sane step. Until frame posture leaves the rich local config,
every later lifecycle or sharing change risks recreating mixed ownership.

## Ticket Contract
- ENTRY_GATE: the reset epic is active and the user explicitly chose this as
  the first bounded slice.
- EXECUTION_BOUNDARY: remove frame posture fields and methods from
  `SpellbookConfiguration`, and reroute the direct runtime readers that still
  depend on them.
- DEPENDENCIES:
  - `src/melder/spellbook/configuration/spellbook_configuration.py`
  - `src/melder/aether/aetheric_frame_configuration.py`
  - `src/melder/spellbook/spellbook.py`
  - `src/melder/spellbook/spellbook_creation_system.py`
  - `src/melder/aether/conduit/conduit.py`
- EXIT_GATE: frame posture is no longer owned by `SpellbookConfiguration`, and
  the direct runtime readers in this slice use frame posture instead.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if a direct runtime reader
  proves one of those fields still belongs to the rich config.

## Requirements (Functional)
- Remove:
  - `_frame_configuration`
  - `with_system_state(...)`
  - `with_ai_native(...)`
  - `with_rift_enabled(...)`
  - `with_shared_framewide_spellbook_configuration(...)`
  - `dynamic_defaults()`
  - `automatic_defaults()`
  - `to_aetheric_frame_configuration(...)`
- Remove frame posture fields from the rich config property bag.
- Reroute direct runtime reads in this slice away from `SpellbookConfiguration`.

## Scope Boundaries
- In scope:
  - owner split for frame posture
  - direct reader reroutes in current runtime hot paths
  - focused tests for the new owner
- Out of scope:
  - full `AethericFrame` lifecycle API
  - final shared-rich-config behavior

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: this is the first explicit owner-boundary slice under the
  new epic.

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-05-16-strip-frame-posture-fields-from-spellbook-configuration

## Acceptance Criteria
- `SpellbookConfiguration` no longer owns frame posture.
- runtime no longer reads those fields from the rich config bag in this slice.

## Validation / Test Plan
- focused rings for configuration, Spellbook, Conduit, and adjacent Nexus frame
  posture tests

## Notes
- DATETIME: 2026-05-16T13:30:44Z
  TYPE: PLAN
  CLAIM: This story exists to keep the work from drifting back into mixed
    ownership. The first slice is just: remove frame posture from the rich local
    config and move the direct readers.
  EVIDENCE:
  - tickets/epics/2026-05-16_migrate_frame_posture_ownership_into_aetheric_frame_epic.md:1-120
  IMPACT: Later frame lifecycle and shared-rich-config decisions will be much
    easier once the owner boundary is correct.
  NEXT: open the first task and route the board to it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story owns the first bounded owner-boundary correction: posture out of the
rich local config.

