# Epic: Consolidate Rift Conduit Access Onto Room Command Surfaces
- Completed: 2026-04-19T16:54:36Z
- Summary: Closed during the 2026-04-19 cleanup pass after the facade-removal implementation tasks landed.

## Metadata
- Epic ID: EPIC-2026-04-16-rift-facade-command-surface-consolidation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-16T23:43:31Z
- Updated: 2026-04-19T16:54:36Z
- Target Window: 2026-04
- Related Program/Initiative: AethericRift room/runtime consolidation

## Problem / Opportunity
`Rift` still carries a legacy direct conduit-access facade (`get_conduit_cloud`,
`list_conduit_ids`, `get_conduit_by_id`, and related helpers) even though the
newer room model already exposes the same capability family through
`RiftSpace.command_system`. That leaves the Rift layer mixed: part session/frame
orchestration, part direct runtime convenience facade. Tests and integration
helpers still depend on the old surface, which is why commenting the methods
causes broad failures instead of a clean consolidation.

## MRP Alignment (Most Reasonable Product)
The holistic core here is not "delete methods for cleanliness." The right MRP
is one coherent AR layering model:
- `Rift` owns session identity, frame targeting, space registration, and viewer
  attachment orchestration.
- `RiftSpace` owns room-local mediated interaction surfaces.
- conduit/runtime access routes through room-owned command systems instead of a
  second direct facade on `Rift`.

That reduces duplicated surface area without changing the deeper room/runtime
model already chosen for static/capability/codegen spaces.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested the Rift facade removal to be staged
  as a proper epic/story/task lane before implementation.
- EXECUTION_BOUNDARY: consolidate the legacy direct conduit-access facade from
  `Rift` onto room-owned command surfaces plus the required test/helper
  migration; no unrelated codegen or CommandOps work.
- DEPENDENCIES:
  - tickets/tasks/2026-04-14_investigate_codegen_rift_space_implementation_task.md
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/command_system/command_system.py
  - tests/unit/melder/aether/test_rift_runtime_contracts.py
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py
- EXIT_GATE: investigation is accepted, implementation/test migration lands,
  and board sync reflects the surviving live lane only.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if removing the facade breaks a
  required external/public contract that should be preserved intentionally.

## Goals (Outcomes)
- Remove the duplicated conduit-access facade from `Rift`.
- Route tests and integration helpers through the proper room command surface.
- Keep `Rift` focused on session/frame/space orchestration responsibilities.

## Non-Goals (Explicit Exclusions)
- New codegen execution behavior.
- CommandOps queue/orchestration changes.
- Broad AR API redesign beyond the legacy conduit facade family.

## Scope Boundaries
- In scope:
  - `Rift` direct conduit-access facade methods
  - room-command migration for tests and helper utilities
  - interface/doc/test updates required by that migration
- Out of scope:
  - unrelated `Rift` session APIs
  - `CommandSystem` semantic redesign
  - CommandOps or ASE work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the legacy Rift facade is now a concrete, evidenced
  migration target and the user requested a staged execution lane.

## Success Metrics
- Zero remaining runtime/testbench consumers of the removed `Rift` conduit
  facade.
- `Rift` only retains session/frame/space orchestration responsibilities for
  this surface family.
- Focused AR tests pass through the room-command path.

## Requirements (Functional + Non-Functional)
- Preserve existing functionality by rerouting callers through the correct
  `RiftSpace.command_system`.
- Keep behavior explicit and reviewable; no hidden fallback/shim layer.
- Maintain accurate docstrings and interface contracts on touched public
  surfaces.

## Constraints / Assumptions
- Existing room command systems already provide the required conduit-access
  surface.
- The current failures are mostly tests/integration helpers rather than unseen
  product/runtime consumers.

## Dependencies / External References
- tickets/tasks/2026-04-14_investigate_codegen_rift_space_implementation_task.md

## Milestones (Track Progress)
- [ ] Milestone 1: investigation and migration plan accepted
- [ ] Milestone 2: runtime/interface/test migration lands green

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-16-migrate-rift-conduit-access-onto-room-command-surface
      - remove the facade and move consumers to room-owned commands

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-04-16-migrate-rift-conduit-access-onto-room-command-surface
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The story and child tasks are accepted.
- `Rift` no longer exposes the duplicated conduit facade.
- Tests/helper utilities use the room-owned command surface instead.

## Risks / Mitigations
- Risk: a hidden contract still needs the direct `Rift` facade.
  Mitigation: investigate all current repo consumers before deletion and raise
  `DECISION_REQUEST` if a true external/public contract remains.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Focused AR unit and integration rings touching Rift runtime contracts and
  JSON testbench helpers.

## Rollout / Adoption Plan
- First migrate internal consumers/tests.
- Then remove the duplicated facade.
- Then close the lane after user acceptance.

## Open Questions
- Does any external consumer outside the current repo still rely on the direct
  `Rift` facade?

## Decision Log
- 2026-04-16T23:43:31Z: create a dedicated migration lane instead of deleting
  the facade ad hoc.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-16T23:43:31Z
  TYPE: PLAN
  CLAIM: This epic exists to turn the mixed Rift layering into one explicit
    migration lane rather than a random "cleanup" edit.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:433-611
  - src/melder/aether/nexus/rift/command_system/command_system.py:306-430
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:424-432
  IMPACT: The work can now be routed, investigated, and implemented without
    pretending the facade deletion is risk-free.
  NEXT: stage the story and tasks that break the migration into investigation,
    runtime removal, and test/helper rerouting.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic owns the staged removal of the legacy direct conduit-access facade
from `Rift` and the reroute of remaining consumers onto room-owned command
surfaces.
