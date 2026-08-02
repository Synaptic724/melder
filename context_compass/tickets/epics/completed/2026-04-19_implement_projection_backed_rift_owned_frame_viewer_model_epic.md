# Epic: Implement Projection-Backed Rift-Owned FrameViewer Model
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Epic ID: EPIC-2026-04-19-implement-projection-backed-rift-owned-frame-viewer-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T16:01:49Z
- Updated: 2026-04-19T16:37:39Z
- Target Window: 2026-04-19
- Related Program/Initiative: AetherRift viewer/runtime ownership cleanup

## Problem / Opportunity
The planning lane proved the current viewer stack still inserts a second median
layer after the projection bundle:
- `Nexus` already builds one per-frame `FrameProjectionSet`
- `Rift` already owns the live projection registry
- `RiftSpace` already hosts the durable viewer asset
- `FrameViewer` still rehosts descriptor/config/surface maps and rebuilds
  bound profile assets from those local copies

The user approved implementing the settled migration rather than extending the
investigation further.

## MRP Alignment (Most Reasonable Product)
The smallest coherent implementation cut is:
- add Rift-level viewer profile selection
- keep compiled ACL/config/surface ownership on the projection bundle
- remove viewer-owned duplicate descriptor/config/surface maps
- keep `FrameViewer` as a durable asset that consumes projection-owned truth
- preserve the current Nexus refresh pipeline and the current helper behavior

## Ticket Contract
- ENTRY_GATE: the projection-backed viewer planning lane is accepted and the
  user explicitly requested implementation.
- EXECUTION_BOUNDARY: `RiftConfiguration`, `Rift`, `RiftSpace`,
  `FrameViewer`, `StaticFrameViewer`, `FrameViewerProfile`, focused tests, and
  matching docs only.
- DEPENDENCIES:
  - tickets/epics/2026-04-19_migrate_frame_viewer_to_projection_backed_rift_owned_model_epic.md
  - tickets/stories/2026-04-19_plan_frame_viewer_projection_backed_rift_owned_migration_story.md
  - tickets/tasks/2026-04-19_investigate_and_plan_frame_viewer_projection_backed_rift_owned_migration_task.md
  - tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/*
- EXIT_GATE: the viewer no longer owns duplicate descriptor/config/surface
  maps, Rift selects the viewer profile through `RiftConfiguration`, the
  focused tests are green, and docs/tickets/board/artifact state are synced.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if removing viewer-side
  duplication breaks a real shipped helper/view contract that was not proven in
  the planning artifact.

## Goals (Outcomes)
- Add one Rift-level viewer profile selection seam.
- Move viewer profile choice to `RiftConfiguration` / `Rift`.
- Remove viewer-owned duplicate descriptor/config/surface maps.
- Bind selected viewer behavior from projection-owned state.
- Preserve the current helper behavior and Nexus refresh pipeline.

## Non-Goals (Explicit Exclusions)
- No redesign of `Nexus` ACL compilation.
- No redesign of `CommandSystem`.
- No redesign of projection-family duplication across view/command/codegen in
  this epic.
- No new multi-profile viewer product surface.

## Scope Boundaries
- In scope:
  - `RiftConfiguration` viewer-profile config
  - `Rift` viewer sync/profile-selection update
  - `RiftSpace` viewer construction seam updates if required
  - `FrameViewer` ownership cut
  - `StaticFrameViewer` adaptation
  - `FrameViewerProfile` binding changes
  - focused viewer/rift/nexus tests
- Out of scope:
  - command/codegen redesign
  - ACL model redesign
  - unrelated room/workstation changes

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the ownership cut is implemented and the focused
  viewer/rift/nexus validation rings are green.

## Success Metrics
- `RiftConfiguration` can select one viewer profile.
- `Rift` uses that selection during viewer sync.
- `FrameViewer` no longer owns local descriptor/config/surface maps.
- The bound helper stack still works against projection-owned state.
- The focused viewer/rift/nexus tests pass.

## Requirements (Functional + Non-Functional)
- Add `viewer_profile_name` to `RiftConfiguration` with defaults and fluent
  setter.
- `Rift.refresh_runtime_projections(...)` must use the configured viewer
  profile by default.
- `FrameViewer` must stop cloning/storing descriptor/config/surface maps from
  `ViewProjection`.
- `FrameViewerProfile` binding must consume `ViewProjection` or the same
  projection-owned references directly.
- `StaticFrameViewer` must preserve its live-only spell filtering without
  recreating the old viewer-owned median layer.
- Keep validation truthful and focused.

## Dependencies / External References
- `tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md`

## Milestones (Track Progress)
- [x] Milestone 1: Implementation lane staged
- [x] Milestone 2: Core ownership cut lands
- [x] Milestone 3: Static overlay/tests/docs are green

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-19-implement-projection-backed-rift-owned-frame-viewer-model

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: TASK-2026-04-19-implement-projection-backed-rift-owned-frame-viewer-model
- [ ] Task: Verify Ticket Microcycle enforcement across the implementation lane.

## Acceptance Criteria (Epic Done)
- Rift-level viewer profile selection exists and is used.
- Viewer no longer duplicates projection-owned descriptor/config/surface state.
- The helper stack still resolves through projection-owned compiled access
  surfaces.
- Focused tests and docs are updated and green.

## Risks / Mitigations
- Risk: static viewer filtering relies on the old copied compiled-surface maps.
  Mitigation: adapt `StaticFrameViewer` explicitly instead of assuming it keeps
  working.
- Risk: host-level viewer methods may implicitly depend on local descriptor
  maps.
  Mitigation: update them against projection-owned access or cached bound
  helpers only where needed.

## Applicable Anti-Patterns
- [ ] No preserving the second viewer-owned median layer out of convenience.
- [ ] No widening into projection-family normalization in this epic.
- [ ] No multi-profile/per-frame profile machinery retained without proved use.

## Validation / Test Approach
- Focused viewer/rift/nexus unit tests.

## Open Questions
- Whether a tiny generation-aware bound-profile cache is needed immediately or
  can be deferred after the ownership cut.

## Decision Log
- 2026-04-19T16:01:49Z: Started direct implementation after user approval of
  the settled projection-backed viewer plan.

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
  CLAIM: The implementation cut is landed. `RiftConfiguration` now owns the
    viewer profile choice, `Rift` applies that choice during viewer sync, the
    old descriptor/config/surface constructor path is gone from `FrameViewer`,
    and the viewer/helper stack now binds against projection-owned state
    instead of a second local snapshot layer.
  EVIDENCE:
  - src/melder/aether/nexus/configuration/rift_configuration.py:47-62
  - src/melder/aether/nexus/rift/rift.py:471-520
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:28-3568
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:14-440
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:1-540
  IMPACT: The implementation lane is ready for review, not more coding.
  NEXT: hold for user review unless one more bounded follow-on is requested.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T16:01:49Z
  TYPE: PLAN
  CLAIM: The implementation cut is now authorized. The next compliant move is
    to apply the patch contract around the settled ownership split:
    `Nexus` keeps projection compilation, `Rift` selects the viewer profile and
    owns current projections, `RiftSpace` hosts the viewer asset, and
    `FrameViewer` stops owning duplicate descriptor/config/surface maps.
  EVIDENCE:
  - tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md:1-236
  - user_instruction: "implement all these things"
  IMPACT: The implementation can stay bounded to the viewer ownership cut
    instead of reopening the design lane.
  NEXT: create the story/task/patch docs and route the board to the
    implementation task before editing code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: implementation tranche order, patch-to-code mapping, and test/doc
  synchronization.
- Keep notes append-only and evidence-backed.

## Context / Handoff Summary
This epic implements the settled viewer ownership cut after the planning
artifact proved the current second median layer lives on `FrameViewer`.