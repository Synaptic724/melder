# Story: Validate Descriptor ACL Payload Contracts And Collapse FrameView
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed payload validation and the FrameView runtime collapse onto the descriptor-driven viewer path.


## Metadata
- Story ID: STORY-2026-04-06-validate-descriptor-acl-payload-contracts-and-collapse-frame-view
- Epic: EPIC-2026-04-06-descriptor-acl-payload-contract-and-viewer-collapse
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T16:52:25Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Prove the consequences of removing `FrameView`, add descriptor<->ACL payload
contract validation, and then collapse the runtime onto a descriptor-driven
`FrameViewer`.

## Ticket Contract
- ENTRY_GATE: the epic is active and the user explicitly wants a staged
  investigation-first rollout.
- EXECUTION_BOUNDARY: impact analysis, payload-contract validation, and
  runtime removal of `FrameView`.
- DEPENDENCIES:
  - tickets/epics/2026-04-06_descriptor_acl_payload_contract_and_viewer_collapse_epic.md
  - tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
  - tickets/tasks/2026-04-03_design_frameinfolink_hld_task.md
- EXIT_GATE: impacts are documented, payload validation lands, and the viewer
  no longer depends on `FrameView`.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if direct viewer execution still
  needs a retained intermediate aggregate object.

## Scope Boundaries
- In scope:
  - investigation of `FrameView` removal
  - descriptor payload contract validation
  - runtime `FrameView` collapse
  - focused tests
- Out of scope:
  - codegen execution
  - mutation work
  - workspace redesign beyond the viewer path

## Tasks
- [ ] TASK-2026-04-06-investigate-frame-view-removal-impacts-and-payload-contract-gates
- [ ] TASK-2026-04-06-implement-descriptor-acl-payload-contract-validation
- [ ] TASK-2026-04-06-remove-frame-view-and-rewire-frame-viewer-to-descriptor-surface

## Acceptance Criteria
- The consequences of removing `FrameView` are documented with source evidence.
- Descriptor payload contracts are validated against ACL requirements.
- Viewer creation fails fast on payload mismatch.
- `FrameView`, `FrameViewProfile`, and `FrameViewProfileBuilder` are removed
  from the runtime path.
- `FrameViewer` can execute its methods directly against descriptor-organized
  frame/conduit/spell data through ACL filtering.

## Risks / Mitigations
- Risk: the viewer still needs some hidden projection object.
  Mitigation: make that explicit in the investigation task before runtime edits.
- Risk: payload contracts differ by frame and break late.
  Mitigation: validate at descriptor publication and viewer creation.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the epic is active and the first task is now the impact
  investigation plus routing pass.

## Applicable Anti-Patterns
- [ ] No implementation before the impact investigation lands.
- [ ] No stateful viewer rewrite without payload validation first.
- [ ] No closure without user acceptance and board sync.

## Notes
- DATETIME: 2026-04-06T16:52:25Z
  TYPE: PLAN
  CLAIM: This story is intentionally staged in three steps: investigate the
    removal impacts first, then implement payload validation, then collapse the
    runtime path. That is the only sane way to remove `FrameView` without
    breaking the active Nexus lane blindly.
  EVIDENCE:
  - user_instruction: "build an epic, investigate the concequences after you've built task tickets and documented the impacts of removing the view"
  IMPACT: The implementation order is now explicit and should not drift.
  NEXT: create the tasks and route the board to the investigation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
The first task in this story is routing/investigation only. No runtime edits
should happen until the remove-`FrameView` impacts are documented.


## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

