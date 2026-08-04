# Story: Add Command System To Rift Space
- Completed: 2026-04-13T11:34:18Z
- Summary: Completed the first room-local command-system story after the base command layer landed and later room-mode work built on it.

## Metadata
- Story ID: STORY-2026-04-11-add-command-system-to-rift-space
- Epic: EPIC-2026-04-10-rift-access-modes-static-capability-dynamic
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T16:01:14Z
- Updated: 2026-04-13T11:34:18Z

## User Narrative
As the Rift runtime designer, I want `RiftSpace` to own a command system on top
of the workstation, so that viewer discovery, controlled retrieval, and local
binding/use form one coherent room workflow before ACL enforcement is wired in.

## Ticket Contract
- ENTRY_GATE: the workstation canvas is landed and the user explicitly approved
  building the command system next.
- EXECUTION_BOUNDARY: command-system object, `RiftSpace` integration, focused
  tests, and ticket/patch sync only.
- DEPENDENCIES:
  - tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md
  - tickets/tasks/2026-04-11_add_command_system_to_rift_space_task.md
- EXIT_GATE: `RiftSpace` owns a command system with the first controlled
  getter/execute surface and the focused unit slice is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the first command-system cut
  requires ACL wiring or target-aware command policy in the same slice.

## Acceptance Criteria
- `RiftSpace` owns a command system
- command system stays separate from workstation persistence
- first getter/execute surface is real and tested

## Notes
- DATETIME: 2026-04-11T16:01:14Z
  TYPE: DECISION
  CLAIM: The command system owns controlled retrieval/execution only. Viewer
    still owns discovery/description, and workstation still owns persistence.
    The command system should therefore expose getters and execute helpers, not
    a second persistence layer.
  EVIDENCE:
  - user_instruction: "viewer takes care of that"
  - user_instruction: "it should be getters they can just use with bind"
  - user_instruction: "getters is all you get in command registry and you can execute methods"
  IMPACT: The first command-system slice can stay lean: no describe API, no
    binding API, no ACL enforcement yet.
  NEXT: create the implementation task and patch docs, then inspect the live
    viewer target model before coding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:34:18Z
  TYPE: DECISION
  CLAIM: This story is complete. The first room-local command system landed,
    and the later room-mode gating, shared manual-runtime expansion, and
    capability-room work all depend on it as settled infrastructure.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-11_add_command_system_to_rift_space_task.md:1-161
  - tickets/tasks/2026-04-12_refactor_rift_space_to_mode_specific_command_systems_task.md:1-153
  - tickets/tasks/2026-04-12_expand_shared_command_system_manual_runtime_surface_task.md:1-170
  IMPACT: The initial command-system story can move to the completed lane.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story owned the first command-system slice on top of the workstation only.
That slice is now complete and forms part of the settled AR room substrate.
