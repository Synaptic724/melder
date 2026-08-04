# Story: FrameDescriptor Refactor
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed the FrameDescriptor aggregate-refactor story and archived the finished staged migration lane.


## Metadata
- Story ID: STORY-2026-04-04-aethericframe-descriptor-refactor
- Epic: EPIC-2026-04-04-refactor-nexus-frame-state-around-aethericframe-descriptor
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-04T13:10:15Z
- Updated: 2026-04-09T21:59:36Z

## User Narrative
As the project owner, I want Nexus frame-scoped state consolidated under one
descriptor object so frame/view/ACL work can target one coherent aggregate
instead of several disconnected records and stores.

## Value / MRP Alignment
This story is the architecture bridge between the completed passive-ingest
slice and the future viewer/ACL layer. Without it, every next feature would
keep hardening the wrong internal shape.

## Ticket Contract
- ENTRY_GATE: the new epic is active and the user has explicitly selected
  `FrameDescriptor` as the aggregate direction.
- EXECUTION_BOUNDARY: design, investigation, and staged implementation
  sequencing only; no giant runtime rewrite in the story itself.
- DEPENDENCIES:
  - EPIC-2026-04-04-refactor-nexus-frame-state-around-aethericframe-descriptor
  - tickets/tasks/completed/2026-04-04_investigate_aethericframe_descriptor_refactor_task.md
  - tickets/tasks/completed/2026-04-04_implement_nexus_passive_ingest_and_canonical_store_task.md
- EXIT_GATE: the migration surface and staged runtime slices are defined
  clearly enough to execute without turning the refactor into one giant patch.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the descriptor boundary still
  leaves major ownership ambiguity after investigation.

## Requirements (Functional)
- Define what must live inside `FrameDescriptor`.
- Define what should remain outside it.
- Define the migration order from flat Nexus frame-scoped fields.
- Define which runtime publication paths must change in the first slice.

## Requirements (Non-Functional)
- Staged.
- Reviewable.
- Explicit about ownership.
- Compatible with future ACL and viewer work.

## Scope Boundaries
- In scope:
  - descriptor ownership model
  - migration sequencing
  - first implementation slice definition
- Out of scope:
  - final ACL model
  - final viewer implementation
  - mutation contract work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the descriptor refactor now has enough user-approved shape
  to justify a dedicated story beneath the new epic.

## Dependencies / Related Work
- tickets/epics/2026-04-04_refactor_nexus_frame_state_around_frame_descriptor_epic.md
- tickets/tasks/completed/2026-04-04_investigate_aethericframe_descriptor_refactor_task.md

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-04-investigate-aethericframe-descriptor-refactor -
      map the current migration surface and first staged slice
- [ ] Task: define the first implementation slice under the investigated migration plan
- [ ] Enforce Ticket Microcycle across the active descriptor task.

## Acceptance Criteria
- The story defines:
  - descriptor contents
  - descriptor boundaries
  - staged migration order
  - the first implementation slice

## Validation / Test Plan
- Design/investigation validation only.
- Runtime validation deferred to child implementation tasks.

## Risks / Mitigations
- Risk: descriptor becomes an unbounded garbage container.
  Mitigation: explicitly name what belongs inside and what remains separate.
- Risk: flat-store migration is attempted in one unsafe pass.
  Mitigation: force staged implementation slices.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Whether the first slice should introduce the descriptor as a wrapper or
  immediately migrate all current frame-scoped state under it.
- Whether the current `FrameRecord` should later be renamed to `FrameOverview`.

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-04T19:25:19Z
  TYPE: FACT
  CLAIM: The descriptor child task is now completed. The staged migration,
    cleanup slice, and lock/read-boundary correction all landed, so the
    descriptor is no longer the next thing to build; it is the cleaned base the
    ACL and frame/view lanes now build on.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-04_investigate_aethericframe_descriptor_refactor_task.md:1-322
  IMPACT: Story dependencies are now historical/reference-only and the active
    work should stay on ACL and frame-surface design instead of reopening the
    internal frame aggregate migration.
  NEXT: keep the story as reference unless another descriptor-internal slice is
    explicitly requested later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T13:10:15Z
  TYPE: FACT
  CLAIM: This story exists because the completed passive-ingest slice proved
    that frame-scoped Nexus state is real, but the current storage shape is too
    fragmented to keep extending safely. The descriptor is the next coherent
    move before deeper viewer and ACL work.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-04_implement_nexus_passive_ingest_and_canonical_store_task.md:1-170
  - tickets/epics/2026-04-03_frameinfolink_surface_query_and_binding_epic.md:1-170
  IMPACT: This story gives the refactor a durable place to stage multiple child
    implementation slices instead of forcing them into ad hoc follow-ups.
  NEXT: investigate the exact migration surface and define the first slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when migration boundaries or staging order change.
- Reference child-task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story stages the Nexus descriptor refactor in multiple slices so the
future viewer and ACL layers can target one frame aggregate.

