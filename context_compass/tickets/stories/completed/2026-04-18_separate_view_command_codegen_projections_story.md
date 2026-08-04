# Story: Separate View Command And Codegen Projections
- Completed: 2026-04-19T16:54:36Z
- Summary: Closed during the 2026-04-19 cleanup pass after the projection-split implementation landed.

## Metadata
- Story ID: STORY-2026-04-18-separate-view-command-codegen-projections
- Epic: EPIC-2026-04-18-separate-view-command-and-codegen-projection-runtime
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T17:14:19Z
- Updated: 2026-04-19T16:54:36Z

## User Narrative
As the Rift runtime maintainer, I want view, command, and codegen to consume
separate ACL-driven projections, so command/codegen availability is not
coupled to viewer visibility and Nexus can refresh each downstream surface when
ACL state changes.

## Value / MRP Alignment
This keeps the next Rift runtime cut coherent:
- `FrameLinkContract` already stores separate selected names for `view`,
  `command`, and `codegen`
- the runtime should honor that split instead of collapsing command onto the
  viewer
- Nexus remains the owner of ACL mutation and refresh coordination

## Ticket Contract
- ENTRY_GATE: the viewer/ACL propagation investigation is complete and the live
  coupling plus refresh risks are explicit in the linked investigation task.
- EXECUTION_BOUNDARY: projection split and refresh protocol design plus the
  bounded implementation task that follows from it.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_investigate_frame_viewer_acl_propagation_and_refresh_task.md
  - tickets/tasks/2026-04-18_implement_separate_view_command_codegen_projections_task.md
- EXIT_GATE: the runtime split and refresh protocol are explicit enough to
  implement without guessing.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the projection split forces a
  broader target-selection redesign than this story can safely absorb.

## Acceptance Criteria
- The current view/command coupling is documented and rejected as the target
  model.
- The new split defines separate view, command, and codegen projections.
- The refresh protocol is Nexus-owned and explicit.
- A bounded implementation task exists for the next code change tranche.

## Notes
- DATETIME: 2026-04-18T17:14:19Z
  TYPE: PLAN
  CLAIM: This story exists because the live runtime already proved the next
    design pressure: `FrameLinkContract` stores separate ACL family names, but
    `CommandSystem` still reads the viewer. The next slice is to make the
    runtime honor the family split instead of relying on viewer-hosted command
    truth.
  EVIDENCE:
  - tickets/tasks/2026-04-18_investigate_frame_viewer_acl_propagation_and_refresh_task.md:113-140
  - user_instruction: "the command system shouldn't need to use the viewer at all"
  IMPACT: The next implementation needs a projection split, not another local
    patch on top of viewer-centric command access.
  NEXT: stage the bounded implementation task for the projection split.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T18:20:00Z
  TYPE: DECISION
  CLAIM: The synchronized ACL refresh sequence is now part of the story
    contract. `Nexus` should identify impacted Rifts, close their
    `RiftGate`s, wait for drain, rebuild projections, swap them into the
    owning `RiftSpace`, and then reopen the gates. This is the explicit
    coordination path the implementation task must follow.
  EVIDENCE:
  - tickets/tasks/2026-04-18_investigate_frame_viewer_acl_propagation_and_refresh_task.md:153-166
  - user_instruction: "ensure that we have some kind of method in nexus that'll properly turn off all frames impacted via the controller then switch the ACL and then update the project"
  IMPACT: The implementation task can no longer treat refresh as an internal
    viewer rebuild detail; it is a Nexus-owned runtime protocol now.
  NEXT: patch the implementation task to include the synchronized gate-driven
    refresh sequence explicitly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Context / Handoff Summary
This story owns the next Rift runtime lane after the closed event work:
separate view/command/codegen projections plus Nexus-owned ACL refresh.
