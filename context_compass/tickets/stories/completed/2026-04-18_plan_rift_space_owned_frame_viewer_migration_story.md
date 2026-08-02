# Story: Plan RiftSpace-Owned FrameViewer Migration
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Story ID: STORY-2026-04-18-plan-rift-space-owned-frame-viewer-migration
- Epic: EPIC-2026-04-18-rehome-frame-viewer-ownership-to-rift-space
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T22:59:13Z
- Updated: 2026-04-19T16:37:39Z

## User Narrative
As a runtime maintainer, I want one source-grounded migration plan for moving
`FrameViewer` assembly out of `Nexus` and into `RiftSpace`, so that the next
implementation cut uses honest ownership boundaries instead of layered seams.

## Value / MRP Alignment
This story locks the ownership model before code churn starts. That keeps the
viewer migration coherent, reviewable, and free of compatibility sludge.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested investigation plus a detailed epic
  and migration plan.
- EXECUTION_BOUNDARY: viewer-construction ownership only; no runtime code
  migration in this story.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_investigate_and_plan_rift_space_owned_frame_viewer_migration_task.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py
- EXIT_GATE: the current ownership split, the target ownership model, the
  migration cuts, and the main risks are explicit enough for user approval.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the investigation proves the
  migration is entangled with a larger frame-target/default-frame redesign.

## Requirements (Functional)
- Explain the current live viewer construction path with source evidence.
- Explain what `FrameLinkContract` actually owns and what it does not own.
- Explain why `RiftSpace` can build the viewer from `ViewProjection`.
- Define the concrete migration cuts and the seam removals they imply.

## Requirements (Non-Functional)
- No compatibility or deprecation strategy in this planning story.
- Keep the plan bounded to viewer ownership.
- Keep architecture statements source-grounded.

## Scope Boundaries
- In scope:
  - current call-path analysis
  - ownership analysis
  - migration planning
  - epic/story/task creation and board routing
- Out of scope:
  - code implementation
  - command/codegen redesign
  - explicit frame-target redesign

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the investigation and migration plan are complete and now
  need user review before implementation.

## Dependencies / Related Work
- recent review-state cleanup around room viewer seams and command cleanup
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-18-investigate-and-plan-rift-space-owned-frame-viewer-migration - trace the live ownership split and stage the migration plan
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The current viewer ownership split is explained with code evidence.
- The target ownership model is explicit.
- The proposed migration sequence is explicit enough to implement in bounded
  follow-on cuts.
- The user can approve or redirect the plan without reopening basic discovery.

## Validation / Test Plan
- Planning-only.
- Not run.

## UX / API / Data Notes
- This story assumes no public compatibility layer for removed viewer-builder
  APIs.
- Any later API removals should be staged only after the room-owned builder is
  landed.

## Risks / Mitigations
- Risk: cached-viewer semantics may drag extra surface area into the first cut.
  Mitigation: decide early whether cache moves with the room or dies.
- Risk: static wrapping may be accidentally left as a second-stage patch seam.
  Mitigation: keep room-mode viewer composition explicit in the plan.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should cache ownership move to `RiftSpace`, `Rift`, or be removed outright?
- Should the frame-scoped viewer factory survive separately from the main
  room-owned builder?

## Decision Log
- Pending user review of the migration plan.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-18T22:59:13Z
  TYPE: FACT
  CLAIM: The current runtime path is `Rift.target_frame(...)` ->
    `Rift.refresh_runtime_projections(...)` -> `Nexus.create_frame_projection_sets_for_rift(...)`
    -> `Rift.attach_frame_viewer(...)` -> `Nexus.create_frame_viewer_for_rift(...)`
    -> `Nexus.create_frame_viewer(...)` -> `RiftSpace._replace_frame_viewer(...)`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:361-628
  - src/melder/aether/nexus/nexus.py:1719-2273
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:366-397
  IMPACT: Projection installation and viewer assembly are split, and the
    current refresh path duplicates projection work.
  NEXT: keep the story in review while the user decides whether to approve the
    migration implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T22:59:13Z
  TYPE: FACT
  CLAIM: `FrameLinkContract` owns only per-frame selected contract names for
    `view`, `command`, and `codegen`; it does not own projections or viewers.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:16-94
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:149-222
  IMPACT: The room can consume projections directly without treating the
    contract object as a view model or viewer owner.
  NEXT: keep the implementation plan anchored on projection consumption inside
    the room.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T22:59:13Z
  TYPE: PLAN
  CLAIM: The bounded implementation order should be:
    1. add one generic room-owned viewer builder on `RiftSpace` that consumes
    installed `ViewProjection` objects,
    2. keep static wrapping in `StaticRiftSpace`,
    3. change `Rift.refresh_runtime_projections(...)` to rebuild through the
    room instead of `Nexus`,
    4. remove Nexus/Rift viewer-builder and cache seams and update docs/tests.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:151-516
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:15-104
  - src/melder/aether/nexus/nexus.py:1815-2273
  IMPACT: The work can be done in bounded ownership-first slices instead of one
    large churn pass.
  NEXT: present the proposed cuts to the user for approval.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

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
This story holds the source-grounded migration plan for moving viewer ownership
to `RiftSpace`. The next step is user review before implementation is staged.