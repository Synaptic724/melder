# Epic: Command Surface Cleanup And Rift Gate Entry
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Epic ID: EPIC-2026-04-18-command-surface-cleanup-and-rift-gate-entry
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T19:42:55Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Replace the current magic command wrapper and fake policy seams with a cleaner
command surface that uses explicit top-level RiftGate entry and real policy checks.

## Value / MRP Alignment
This removes structural sludge from one of the main agent-facing runtime
surfaces and makes gate behavior and policy semantics explicit.

## Ticket Contract
- ENTRY_GATE: the command audit identified concrete structural problems and the
  user requested implementation instead of more discussion.
- EXECUTION_BOUNDARY: `CommandSystem`, `StaticCommandSystem`, directly related
  tests, and the minimal command-surface support methods needed for the cleanup.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_refactor_command_system_public_surface_and_rift_gate_integration_task.md
- EXIT_GATE: command no longer depends on `__getattribute__` magic or
  `_command_memory_call_depth`, fake no-op policy seams are replaced with real
  checks, and the focused validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the cleanup widens into a full
  workstation/viewer gate integration tranche.

## Scope Boundaries
- In scope:
  - command-surface cleanup
  - explicit top-level RiftGate entry in command methods
  - real policy checks in place of no-op seams
  - focused test updates
- Out of scope:
  - workstation gate integration
  - broad viewer gate integration

## Story Checklist
- [x] Story: STORY-2026-04-18-command-surface-cleanup-and-rift-gate-entry
- [ ] Enforce Ticket Microcycle across linked work.

## Notes
- DATETIME: 2026-04-18T20:02:43Z
  TYPE: FACT
  CLAIM: The bounded command cleanup epic is now implemented and waiting on
    user review.
  EVIDENCE:
  - tickets/stories/2026-04-18_command_surface_cleanup_and_rift_gate_entry_story.md:1-92
  IMPACT: No further implementation is needed in this epic unless the user asks
    to widen into workstation/viewer gate work.
  NEXT: hold for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T19:42:55Z
  TYPE: FACT
  CLAIM: The live command surface now needs a real cleanup slice, not more
    wrapper extension. The current gate wrapper exists because public command
    methods chain into other public command methods extensively.
  EVIDENCE:
  - tickets/tasks/2026-04-18_audit_command_system_surface_and_plan_cleanup_task.md:1-120
  IMPACT: The next slice should refactor the command surface itself before any
    wider viewer/workstation gate work.
  NEXT: implement the bounded command cleanup task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This epic tracks the bounded cleanup of the command surface and its RiftGate
entry semantics.