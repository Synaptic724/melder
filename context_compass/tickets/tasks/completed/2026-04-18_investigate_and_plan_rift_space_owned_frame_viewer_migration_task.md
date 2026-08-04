# Task: Investigate And Plan RiftSpace-Owned FrameViewer Migration
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-18-investigate-and-plan-rift-space-owned-frame-viewer-migration
- Story: STORY-2026-04-18-plan-rift-space-owned-frame-viewer-migration
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T22:59:13Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Trace the live `FrameViewer` ownership/construction path, explain why it is
currently split, and stage one bounded migration plan that moves viewer
assembly into `RiftSpace`.

## Ticket Contract
- ENTRY_GATE: user explicitly requested investigation plus a detailed epic and
  plan for moving viewer ownership.
- EXECUTION_BOUNDARY: source investigation, planning artifacts, and board
  routing only; no runtime code edits in this task.
- DEPENDENCIES:
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
  - src/melder/aether/nexus/rift/projection/frame_projection_set.py
  - src/melder/aether/nexus/rift/projection/view_projection.py
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
- EXIT_GATE: the current ownership split, the target ownership model, and the
  migration cuts are explicit in ticketed form and ready for user review.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the investigation proves the
  viewer move is blocked by a larger unresolved frame-target/default-frame
  redesign.

## Scope Boundaries
- In scope:
  - trace current viewer builder/orchestration path
  - prove what contracts and projections actually own
  - define the target ownership model
  - create epic/story/task planning artifacts
  - sync attention-board routing
- Out of scope:
  - implementing the migration
  - editing runtime code
  - redesigning command/codegen surfaces

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the investigation and plan are complete and ready for user
  review.

## Steps / Checklist
- [x] Trace the current viewer construction path across `Nexus`, `Rift`, and
      `RiftSpace`.
- [x] Verify what `FrameLinkContract`, `FrameProjectionSet`, and
      `ViewProjection` actually own.
- [x] Verify what `FrameViewer.__init__(...)` actually needs to construct a
      live viewer.
- [x] Define a bounded migration sequence with risks and non-goals.
- [x] Create epic/story/task planning artifacts for the migration lane.
- [x] Sync `attention_board.md` routing to the new planning lane.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- source-grounded explanation of current viewer ownership
- target ownership model for room-owned viewer assembly
- detailed epic/story/task plan for the migration

## Files / Paths Impacted
- codex/context_compass/tickets/epics/2026-04-18_rehome_frame_viewer_ownership_to_rift_space_epic.md
- codex/context_compass/tickets/stories/2026-04-18_plan_rift_space_owned_frame_viewer_migration_story.md
- codex/context_compass/tickets/tasks/2026-04-18_investigate_and_plan_rift_space_owned_frame_viewer_migration_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_rift_space.py`

## Risks / Rollback Notes
- Risk: architectural docs still contain stale AR ownership statements.
- Risk: cached-viewer semantics may widen the eventual implementation cut.
- Rollback: planning-only; no runtime rollback needed.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-18T22:59:13Z
  TYPE: FACT
  CLAIM: The current ownership split is concrete: `Nexus.create_frame_viewer(...)`
    assembles `FrameViewer(...)` from fresh projection sets, `Rift` delegates
    to that path, and `RiftSpace` only stores the result and post-binds the gate.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1815-2273
  - src/melder/aether/nexus/rift/rift.py:463-628
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:366-516
  IMPACT: The room already owns the installed projections but not the viewer
    assembly step, which is the ownership bug.
  NEXT: prove whether the room already has every input needed to build the
    viewer itself.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T22:59:13Z
  TYPE: FACT
  CLAIM: `FrameLinkContract` owns only selected contract names, while
    `FrameProjectionSet.view_projection` plus `FrameViewer.__init__(...)`
    prove that viewer assembly can happen entirely from room-owned projection
    data plus the room-owned `rift_gate`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:16-94
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:149-222
  - src/melder/aether/nexus/rift/projection/frame_projection_set.py:10-90
  - src/melder/aether/nexus/rift/projection/view_projection.py:6-96
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:82-172
  IMPACT: `Nexus` is not the necessary owner of viewer construction; it is just
    where the assembly code still lives.
  NEXT: define the bounded migration sequence and the seam removals it implies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T22:59:13Z
  TYPE: FACT
  CLAIM: The room-mode-specific viewer concern is already room-local:
    `StaticRiftSpace` wraps generic viewers into `StaticFrameViewer`, and the
    static overlay clones a base viewer into a room-specific filtered surface.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:1-104
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:15-104
  IMPACT: Viewer composition already wants to live at the room layer, not in
    `Nexus`.
  NEXT: keep static wrapping as part of the room-owned migration plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T22:59:13Z
  TYPE: PLAN
  CLAIM: The migration plan is:
    1. add one generic internal viewer builder on `RiftSpace` that consumes
    installed `ViewProjection` objects and passes `rift_gate` directly into
    `FrameViewer(...)`,
    2. keep `StaticRiftSpace` as the room-mode wrapper owner,
    3. change `Rift.refresh_runtime_projections(...)` to call the room-owned
    builder after `replace_projection_sets(...)`,
    4. delete `Nexus.create_frame_viewer*`, cached-viewer seams, and the
    related Rift delegation helpers, then update focused tests/docs.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1631-2273
  - src/melder/aether/nexus/rift/rift.py:554-628
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:151-516
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:15-104
  IMPACT: The implementation can be split into bounded ownership-first cuts and
    does not require keeping backward-compat APIs alive.
  NEXT: create the epic/story/task artifacts and route the board to this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task captures the source-grounded migration plan for moving viewer
assembly from `Nexus` into `RiftSpace`. No runtime code changed in this slice;
the next step is user review of the proposed implementation order.