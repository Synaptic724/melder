# Epic: Descriptor ACL Payload Contract And Viewer Collapse
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed the payload-validation plus viewer-collapse epic and archived the finished runtime collapse lane.


## Metadata
- Epic ID: EPIC-2026-04-06-descriptor-acl-payload-contract-and-viewer-collapse
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T16:52:25Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Replace the current snapshot-style `FrameView` layer with a descriptor-driven
viewer path, but do it in the right order:
1) validate descriptor payload contracts against ACL configuration first,
2) then collapse `FrameView` out of the runtime path,
3) then let `FrameViewer` execute directly against descriptor-organized data
filtered by ACLs.

## Problem / Opportunity
The current frame-surface stack is structurally coherent but still split across
too many layers:
- descriptor payload truth
- compiled ACL section visibility
- `FrameView` snapshot objects
- `FrameViewProfile` shaping
- `FrameViewerProfile` tool composition

The user has now explicitly challenged whether `FrameView` is buying enough to
justify its cost. The stronger direction is:
- descriptor truth stays canonical
- ACLs filter descriptor payloads
- the viewer executes directly against descriptor-organized frame data
- payload contracts must be validated before viewer creation

## MRP Alignment
This epic is MRP-critical. If the descriptor payload contract is weak or the
viewer depends on a stale snapshot layer, the frame-surface system will drift
as soon as payloads vary by frame or evolve over time.

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected the active Nexus lane toward
  descriptor<->ACL payload validation and removal of the `FrameView` layer.
- EXECUTION_BOUNDARY: payload-contract validation, `FrameView` removal impact
  analysis, and the runtime collapse into a descriptor-driven viewer path.
- DEPENDENCIES:
  - tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
  - tickets/tasks/2026-04-03_design_frameinfolink_hld_task.md
  - src/melder/aether/nexus/frame_descriptor/
  - src/melder/aether/nexus/acl/
  - src/melder/aether/nexus/rift/frame_viewer/
- EXIT_GATE: payload contracts are validated, `FrameView` is removed from the
  runtime path, and `FrameViewer` consumes descriptor-organized data directly.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the descriptor model cannot
  support direct viewer execution without a different aggregate/projection
  boundary.

## Goals
- Make payload compatibility an explicit contract between descriptors and ACLs.
- Fail fast when a frame descriptor does not satisfy the selected ACL payload
  requirements.
- Remove the runtime dependency on `FrameView`, `FrameViewProfile`, and
  `FrameViewProfileBuilder`.
- Rewire `FrameViewer` to operate directly on descriptor-organized frame data.

## Non-Goals
- mutation work
- codegen execution
- workspace UI redesign
- repo-wide unrelated cleanup

## Stories
- [ ] STORY-2026-04-06-validate-descriptor-acl-payload-contracts-and-collapse-frame-view

## Risks / Mitigations
- Risk: removing `FrameView` breaks several landed viewer slices at once.
  Mitigation: investigate impacts first, then separate payload-validation and
  runtime-collapse tasks.
- Risk: descriptor payload contracts are still too weak to validate.
  Mitigation: land contract metadata before removing the intermediate layer.

## Validation Strategy
- Focused unit tests around:
  - descriptor payload contract matching/mismatch
  - ACL validator behavior
  - viewer runtime over descriptors after `FrameView` removal

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user redirected the active Nexus lane away from
  `FrameView`-centric viewer work and asked for a staged payload-validation +
  viewer-collapse plan first.

## Applicable Anti-Patterns
- [ ] No implementation before payload-contract evidence is documented.
- [ ] No runtime collapse while `FrameView` dependencies are still unknown.
- [ ] No closure without user acceptance and board sync.

## Notes
- DATETIME: 2026-04-06T16:52:25Z
  TYPE: PLAN
  CLAIM: The correct order is no longer "add more viewer tools." The system
    first needs payload-contract validation between descriptors and ACLs, then
    it can safely remove the `FrameView` layer and let `FrameViewer` execute
    directly against descriptor-organized data.
  EVIDENCE:
  - user_instruction: "lets remove the view, as well we don't need that and lets just use the viewer"
  - user_instruction: "the descriptor on its own should format the payloads into frame -> conduit -> spells"
  - user_instruction: "I don't want you to do this in 1 prompt"
  IMPACT: The active work must be split into an investigation/planning pass and
    later implementation passes.
  NEXT: create the story and tasks, document the remove-`FrameView` impacts,
    and reroute the board before any runtime edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This epic exists because the current frame-surface architecture likely has one
too many layers. The immediate next step is investigation and routing, not
runtime edits.


## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

