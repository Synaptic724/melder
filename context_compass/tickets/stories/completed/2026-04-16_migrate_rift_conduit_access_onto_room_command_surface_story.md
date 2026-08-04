# Story: Migrate Rift Conduit Access Onto Room Command Surface
- Completed: 2026-04-19T16:54:36Z
- Summary: Closed during the 2026-04-19 cleanup pass after the facade-removal implementation tasks landed.

## Metadata
- Story ID: STORY-2026-04-16-migrate-rift-conduit-access-onto-room-command-surface
- Epic: EPIC-2026-04-16-rift-facade-command-surface-consolidation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-16T23:43:31Z
- Updated: 2026-04-19T16:54:36Z

## User Narrative
As a maintainer of the AR runtime, I want conduit/runtime access to route
through the room-owned command surface, so that `Rift` stops duplicating an
older direct facade and the layering becomes coherent.

## Value / MRP Alignment
This strengthens the room-centric AR model already chosen for
static/capability/codegen spaces. It keeps `Rift` focused on session/frame/room
orchestration while the actual mediated interaction surface lives where the room
owns it.

## Ticket Contract
- ENTRY_GATE: the epic is active and the legacy facade consumers are evidenced.
- EXECUTION_BOUNDARY: investigate current consumers, remove the `Rift` facade,
  and reroute tests/helpers to `space.command_system`; no unrelated API cleanup.
- DEPENDENCIES:
  - tickets/tasks/2026-04-16_investigate_legacy_rift_conduit_facade_consumers_and_migration_task.md
  - tickets/tasks/2026-04-16_remove_legacy_rift_conduit_facade_methods_task.md
  - tickets/tasks/2026-04-16_update_rift_testbenches_to_room_command_surface_task.md
- EXIT_GATE: all three tasks are accepted and the board reflects the remaining
  active lane cleanly.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a deliberate external/public
  compatibility shim is needed instead of hard removal.

## Requirements (Functional)
- Identify every current consumer of the legacy `Rift` facade family.
- Remove the direct conduit facade from `Rift`.
- Migrate tests/helpers to the room-owned command surface.
- Update interfaces/docstrings to match the new contract.

## Requirements (Non-Functional)
- Keep the change reviewable and bounded.
- Avoid adding compatibility fallbacks unless explicitly approved.
- Preserve truthful validation reporting.

## Scope Boundaries
- In scope:
  - `Rift` conduit facade methods
  - `IRift` contract if needed
  - directly affected tests and testbench helpers
- Out of scope:
  - unrelated `Rift` APIs
  - room/model redesign beyond rerouting

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a staged plan before
  implementation.

## Dependencies / Related Work
- tickets/tasks/2026-04-14_investigate_codegen_rift_space_implementation_task.md

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-16-investigate-legacy-rift-conduit-facade-consumers-and-migration
      - inventory live consumers and finalize the migration plan
- [ ] Task: TASK-2026-04-16-remove-legacy-rift-conduit-facade-methods
      - delete the duplicated `Rift` facade and update interfaces/docs
- [ ] Task: TASK-2026-04-16-update-rift-testbenches-to-room-command-surface
      - reroute tests/helper utilities through `RiftSpace.command_system`
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- No current repo consumer relies on the deleted `Rift` conduit facade.
- Room/testbench users get the same behavior through `space.command_system`.
- Focused AR validation is green.

## Validation / Test Plan
- Focused AR unit ring:
  - `tests/unit/melder/aether/test_rift_runtime_contracts.py`
  - `tests/unit/melder/aether/test_nexus.py`
- Targeted integration/testbench helpers and failing integration cases touched
  by the migration.

## UX / API / Data Notes
- This is an internal contract cleanup for now; if `IRift` is public in
  practice, the removal needs to be treated as a real public contract change.

## Risks / Mitigations
- Risk: testbench helpers assume a `Rift`-level conduit facade because they
  predate the room model.
  Mitigation: migrate them explicitly to room command paths instead of adding
  a second shim layer.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should a one-release compatibility shim exist if `IRift` is consumed outside
  the repo, or is hard removal acceptable now?

## Decision Log
- 2026-04-16T23:43:31Z: split the work into investigation, runtime removal,
  and test/helper migration rather than mixing all three in one task.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-16T23:43:31Z
  TYPE: PLAN
  CLAIM: This story exists to consolidate one duplicated surface family from
    `Rift` down into the room-owned command layer without changing the deeper
    room model.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:433-611
  - src/melder/aether/nexus/rift/command_system/command_system.py:306-430
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:350-350
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:494-494
  IMPACT: The migration can stay narrow and evidence-backed instead of drifting
    into generalized Rift cleanup.
  NEXT: activate the investigation task and lock the exact implementation plan
    before editing runtime code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story owns the actual migration from the old `Rift` conduit facade to the
room-owned command surface.
