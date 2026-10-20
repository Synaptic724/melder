

# Story: Atomic frame retirement and creation attribution (parked)

## Metadata
- Story ID: STORY-2026-09-29-atomic-frame-retirement-and-creation-attribution
- Epic: EPIC-2026-09-29-host-integration-read-surface
- Status: draft
- Owner: user
- Agent Name: melder_1
- Priority: p3
- Created: 2026-09-29T21:20:43Z
- Updated: 2026-10-19T12:35:35Z

## User Narrative
As a host that creates frames which other code may later share, I want Melder to tell me whether my call created
a frame and to retire a frame only while it is idle, so that I never clean a frame someone else is using.

## Value / MRP Alignment
MelderOps attributes creation by looking before and after constructing a Spellbook, which races with any other
creator of the same name; and it checks "no root conduits" before calling `frame.cleanup()`, which misses an
unconjured Spellbook and races with a root conjured in between. Only Aether, under its own lock, can make both
answers exact.

## Ticket Contract
- ENTRY_GATE: owner schedules this story (parked at epic creation).
- EXECUTION_BOUNDARY: design first (patch docs and a DECISION_REQUEST); no source until the owner approves a shape.
- DEPENDENCIES: STORY-2026-09-29-frame-lookups-and-read-accessors.
- EXIT_GATE: an approved design, then implementation under its own notch.
- FAILURE_ESCALATION: DECISION_REQUEST on what counts as "idle" (roots, unconjured books, DevOps identities).

## Requirements (Functional)
- Candidates: a create-or-get that reports whether it created the frame; `retire_frame_if_idle(frame) -> bool`.

## Scope Boundaries
- In scope: design and, once approved, the two calls.
- Out of scope: everything the first story delivers.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Parked at epic creation for an owner decision.

## Tasks (Implementation Checklist)
- [ ] Task: none yet (owner decides whether MelderOps shares its frames with other code)

## Acceptance Criteria
- Owner-approved design before any source change.

## Notes
- DATETIME: 2026-10-19T12:35:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner (chat 2026-10-19): "After you finish your change hand all your tickets to melder1 your
    competing for the same resources and document them". melder_0 hands this ticket to melder_1 as it stands:
    draft since 2026-09-29, parked for the owner's decision on whether MelderOps shares its frames with code
    outside its operation guard; no design and no source; its epic,
    EPIC-2026-09-29-host-integration-read-surface, is completed.
  EVIDENCE:
  - context_compass/tickets/stories/backlog/2026-09-29_atomic_frame_retirement_and_creation_attribution_story.md:50-51
  - context_compass/tickets/epics/completed/2026-09-29_host_integration_read_surface_epic.md:5-19
  IMPACT: Its holder is melder_1; nothing else in it changes.
  NEXT: The owner's word on sharing MelderOps frames; then the design (patch docs and a DECISION_REQUEST).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Parked 2026-09-29T21:20:43Z. Needed only if MelderOps frames can be shared with code outside Spectrum's operation guard.
- Holder: melder_1 since 2026-10-19, from melder_0 on the owner's word (DECISION note of 2026-10-19T12:35:35Z).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
