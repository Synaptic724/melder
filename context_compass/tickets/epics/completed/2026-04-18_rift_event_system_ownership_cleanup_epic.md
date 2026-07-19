# Epic: Rift Event System Ownership Cleanup
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Epic ID: EPIC-2026-04-18-rift-event-system-ownership-cleanup
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-18T19:23:23Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Remove the dead `event_system` injection seam from `RiftSpace` so event-system
ownership is internal and truthful.

## Value / MRP Alignment
This tightens room ownership semantics and removes a false dependency seam from
the runtime surface.

## Ticket Contract
- ENTRY_GATE: user approved the bounded ownership cleanup after investigation.
- EXECUTION_BOUNDARY: `RiftSpace`, its concrete room subclasses, directly
  affected interfaces, and focused tests only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_remove_rift_space_event_system_injection_seam_task.md
- EXIT_GATE: the constructor seam is removed, the focused tests are green, and
  board routing reflects the active task.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if removing the seam exposes a
  real external injection requirement in runtime code.

## Scope Boundaries
- In scope:
  - remove `event_system` constructor injection
  - preserve `space.event_system` as the runtime access surface
  - port directly affected tests
- Out of scope:
  - redesign of event payloads or callback semantics
  - memory-system changes

## Story Checklist
- [x] Story: STORY-2026-04-18-rift-event-system-ownership-cleanup
- [ ] Enforce Ticket Microcycle across linked work.

## Notes
- DATETIME: 2026-04-18T19:25:29Z
  TYPE: FACT
  CLAIM: The bounded ownership-cleanup epic is now implemented and waiting on
    user review.
  EVIDENCE:
  - tickets/stories/2026-04-18_rift_event_system_ownership_cleanup_story.md:1-92
  IMPACT: No further implementation is needed unless the user asks for a
    broader event-model follow-on.
  NEXT: hold for review/closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T19:23:23Z
  TYPE: FACT
  CLAIM: The current `event_system` seam is constructor pass-through noise,
    not a meaningful runtime dependency boundary.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:103-186
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:35-83
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:35-91
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:29-77
  - tests/unit/melder/aether/test_rift_space.py:30-46
  IMPACT: We can remove the seam without widening into broader event redesign.
  NEXT: patch the room constructors and the focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This epic exists only to track the bounded ownership cleanup for the room-local
event system.