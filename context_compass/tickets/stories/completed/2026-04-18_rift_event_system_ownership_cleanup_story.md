# Story: Rift Event System Ownership Cleanup
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Story ID: STORY-2026-04-18-rift-event-system-ownership-cleanup
- Epic: EPIC-2026-04-18-rift-event-system-ownership-cleanup
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-18T19:23:23Z
- Updated: 2026-04-19T16:37:39Z

## User Narrative
As a runtime maintainer, I want `RiftSpace` to own its event system directly,
so that room ownership and cleanup semantics stay coherent.

## Value / MRP Alignment
This removes a false seam from the room model and makes ownership truthful at
the MRP level.

## Ticket Contract
- ENTRY_GATE: bounded cleanup approved by the user.
- EXECUTION_BOUNDARY: room constructors, room event ownership, interfaces, and
  focused tests only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_remove_rift_space_event_system_injection_seam_task.md
- EXIT_GATE: no room constructor accepts `event_system`, tests are ported, and
  the task is ready for review.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any real runtime caller still
  depends on injecting a custom event system.

## Requirements (Functional)
- `RiftSpace` must always create and own its own `RiftEventSystem`.
- Concrete room subclasses must stop forwarding `event_system`.
- `space.event_system` must remain the public runtime access surface.

## Requirements (Non-Functional)
- No backward-compat shim for the removed constructor arg.
- Keep the patch scoped and reviewable.

## Scope Boundaries
- In scope:
  - room event-system ownership cleanup
  - focused tests
- Out of scope:
  - changing event payload schema
  - changing callback execution model

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the runtime investigation showed the seam is dead and the
  user approved the cleanup.

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-18-remove-rift-space-event-system-injection-seam - remove the constructor seam and port tests
- [ ] Enforce Ticket Microcycle across linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `RiftSpace` and room subclasses no longer accept injected event systems.
- Focused tests pass without custom event-system injection.

## Validation / Test Plan
- `python -m py_compile ...`
- `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_rift_event_system.py tests/unit/melder/aether/test_nexus.py`

## Risks / Mitigations
- Risk: a hidden test/runtime seam still expects injection.
  Mitigation: search all source/tests before patching and fail fast if found.

## Notes
- DATETIME: 2026-04-18T19:25:29Z
  TYPE: FACT
  CLAIM: The child task landed the ownership cleanup: room constructors no
    longer accept `event_system`, and the focused room/event ring is green.
  EVIDENCE:
  - tickets/tasks/2026-04-18_remove_rift_space_event_system_injection_seam_task.md:1-150
  IMPACT: The story is ready for user review instead of further implementation.
  NEXT: wait for acceptance or a bounded follow-on request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T19:23:23Z
  TYPE: PLAN
  CLAIM: The bounded story implementation is to remove constructor injection,
    keep `space.event_system`, and port the focused tests to internal
    ownership.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:112-178
  - tests/unit/melder/aether/test_rift_space.py:30-46
  IMPACT: The story stays small and does not reopen broader event-model work.
  NEXT: implement the task and validate the focused ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This story tracks one small ownership cleanup: internalize room event-system
construction and remove the dead injection seam.