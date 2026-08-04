# Story: Implement Projection-Backed Rift-Owned FrameViewer Model
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Story ID: STORY-2026-04-19-implement-projection-backed-rift-owned-frame-viewer-model
- Epic: EPIC-2026-04-19-implement-projection-backed-rift-owned-frame-viewer-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T16:01:49Z
- Updated: 2026-04-19T16:37:39Z

## User Narrative
As a Rift runtime maintainer, I want the live viewer to consume projection-owned
truth instead of rehosting descriptor/ACL/surface copies, so that the viewer
stack matches the current ownership model and stops maintaining a redundant
median layer.

## Value / MRP Alignment
This makes the viewer honest:
- `Nexus` compiles projections
- `Rift` owns current projection truth and viewer-profile choice
- `RiftSpace` hosts the durable viewer
- `FrameViewer` binds helper behavior from the projection bundle instead of
  becoming a second snapshot host

## Ticket Contract
- ENTRY_GATE: the planning artifact is complete and the user explicitly
  approved implementation.
- EXECUTION_BOUNDARY: implementation only across `RiftConfiguration`, `Rift`,
  `RiftSpace`, `FrameViewer`, `StaticFrameViewer`, `FrameViewerProfile`,
  interfaces/tests/docs.
- DEPENDENCIES:
  - tickets/tasks/2026-04-19-implement-projection-backed-rift-owned-frame-viewer-model_task.md
  - tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/*
- EXIT_GATE: one accepted implementation lands with focused tests and synced
  docs/board/artifacts.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a real shipped helper
  requirement forces retaining more viewer-owned state than the settled plan
  allowed.

## Requirements (Functional)
- Add `viewer_profile_name` to `RiftConfiguration`.
- Select the viewer profile from `Rift` during viewer sync.
- Remove viewer-owned duplicate descriptor/config/surface maps.
- Bind viewer profiles against projection-owned state.
- Preserve static viewer semantics.

## Requirements (Non-Functional)
- No redesign of Nexus projection compilation.
- No fake compatibility layers that preserve the old second median by default.
- Keep the cut reviewable and focused.

## Scope Boundaries
- In scope:
  - config seam
  - Rift sync seam
  - FrameViewer ownership cut
  - StaticFrameViewer adaptation
  - FrameViewerProfile binding surface
  - tests/docs
- Out of scope:
  - command/codegen redesign
  - projection-family normalization
  - unrelated room/workstation changes

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the implementation landed and the focused validation ring
  is green.

## Dependencies / Related Work
- tickets/epics/2026-04-19_migrate_frame_viewer_to_projection_backed_rift_owned_model_epic.md
- tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-19-implement-projection-backed-rift-owned-frame-viewer-model - land the config, ownership, static-viewer, test, and doc cut
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `RiftConfiguration` selects the viewer profile.
- `Rift` uses that profile during viewer sync.
- `FrameViewer` no longer clones and owns descriptor/config/surface maps.
- `StaticFrameViewer` still filters live-only spells correctly.
- Focused tests are green.

## Validation / Test Plan
- Focused viewer/rift/nexus unit tests.

## UX / API / Data Notes
- Viewer profile choice should become Rift-config-driven, not per-frame-viewer
  state.

## Risks / Mitigations
- Risk: breaking host-level viewer queries while removing local maps.
  Mitigation: drive host methods from projection-owned state rather than
  reintroducing copies.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No preserving per-frame profile selection without proved need.

## Open Questions
- Whether a tiny bound-profile cache is still needed after the ownership cut.

## Decision Log
- 2026-04-19T16:01:49Z: Implementation story opened after direct user approval.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/architecture_patch.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_rift_configuration.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_rift.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_rift_space.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_frame_viewer.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_static_frame_viewer.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_frame_viewer_profile.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-19T16:30:19Z
  TYPE: FACT
  CLAIM: The story acceptance bar is materially met: the viewer profile is now
    Rift-config-driven, the second viewer-owned median layer is removed, and
    the focused viewer/rift/nexus test rings are green.
  EVIDENCE:
  - tickets/tasks/2026-04-19_implement_projection_backed_rift_owned_frame_viewer_model_task.md:1-200
  IMPACT: The story is now in review instead of implementation.
  NEXT: hold for user acceptance or one more bounded follow-on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T16:01:49Z
  TYPE: PLAN
  CLAIM: The task can stay tight because the artifact already proved the full
    ownership chain. The implementation now just has to remove the viewer's
    second median layer and wire the Rift-level profile choice into the sync
    path.
  EVIDENCE:
  - tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md:1-236
  IMPACT: We can implement directly without another design tranche.
  NEXT: land the linked task and keep the patch mapping explicit in ticket
    notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Keep notes append-only and reference the implementation task for tactical
  detail.

## Context / Handoff Summary
This story implements the settled projection-backed viewer ownership cut.