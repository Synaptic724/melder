# Story: Add Workstation To Rift Space
- Completed: 2026-04-13T11:34:18Z
- Summary: Completed the room-local workstation story after the workstation, reference-mode, queue, and lock-hardening slices all landed.

## Metadata
- Story ID: STORY-2026-04-11-add-workstation-to-rift-space
- Epic: EPIC-2026-04-10-rift-access-modes-static-capability-dynamic
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T15:34:59Z
- Updated: 2026-04-13T11:34:18Z

## User Narrative
As the Rift runtime designer, I want every `RiftSpace` to own a workstation
canvas for saved bindings and active-target operations, so that static,
capability, and later dynamic work all share one room-local operating surface.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved the workstation model, clarified the
  ownership split (`RiftSpace` owns the room, workstation owns saved bindings),
  and asked for the workstation object to be implemented before the command
  system.
- EXECUTION_BOUNDARY: workstation object, `RiftSpace` integration, focused
  tests, and ticket/patch sync only.
- DEPENDENCIES:
  - tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md
  - tickets/tasks/2026-04-11_add_workstation_to_rift_space_task.md
- EXIT_GATE: `RiftSpace` owns a workstation and the focused workstation/Rift
  unit slice is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the first workstation cut
  requires a command system or ACL system to be useful at all.

## Acceptance Criteria
- `RiftSpace` owns a `workstation`
- workstation manages saved bindings and active target state
- workstation exposes `cleanup_target(...)` and `call_target(...)`
- focused tests pass

## Notes
- DATETIME: 2026-04-11T15:34:59Z
  TYPE: DECISION
  CLAIM: The workstation is a room-local canvas only. It owns saved bindings
    and active-target operations, while the later command system will own
    discovery and Melder/Rift command surfaces.
  EVIDENCE:
  - user_instruction: "the workstation is only responsible for retaining objects and using the objects you've saved there"
  - user_instruction: "the command system is responsible for all the available commands we need for using the melder system"
  - user_instruction: "workstation is better than workspace because we already have riftspace"
  IMPACT: The first workstation slice can stay narrow and avoid smearing into
    command-system design.
  NEXT: create the task and patch docs, then implement the workstation object
    and `RiftSpace` integration only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:34:18Z
  TYPE: DECISION
  CLAIM: This story is complete. The workstation object, the room-mode-aware
    reference model, the room-local queue/publication seam, and the targeted
    lock-hardening pass are all landed, so the room-local workstation canvas
    is no longer a pending story.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-11_add_workstation_to_rift_space_task.md:1-138
  - tickets/tasks/completed/2026-04-11_add_workstation_reference_modes_to_rift_space_task.md:1-159
  - tickets/tasks/completed/2026-04-11_add_rift_space_event_queue_and_weak_binding_events_task.md:1-181
  - tickets/tasks/completed/2026-04-11_harden_rift_space_and_workstation_locking_task.md:1-177
  IMPACT: The story can move to the completed lane and stop occupying active
    planning state.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story owned the room-local workstation canvas lane. That lane is now
complete and forms part of the settled AR room substrate.
