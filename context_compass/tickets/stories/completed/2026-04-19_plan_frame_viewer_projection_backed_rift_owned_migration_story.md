# Story: Plan FrameViewer Projection-Backed Rift-Owned Migration
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Story ID: STORY-2026-04-19-plan-frame-viewer-projection-backed-rift-owned-migration
- Epic: EPIC-2026-04-19-migrate-frame-viewer-to-projection-backed-rift-owned-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T15:27:26Z
- Updated: 2026-04-19T16:37:39Z

## User Narrative
As a Rift runtime maintainer, I want one source-backed migration plan for
making `FrameViewer` a thin Rift-owned projection-backed viewer instead of a
snapshot-heavy host with per-frame profile selection and decomposed projection
constructor args.

## Value / MRP Alignment
This keeps the viewer honest:
- `Nexus` compiles `ViewProjection`
- `Rift` owns current projection truth and viewer profile choice
- `FrameViewer` stays a durable host with only viewer-local state
- helper/profile code still works, but binds to bundled projection truth

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a holistic MRP migration plan and
  source-backed research for the viewer stack.
- EXECUTION_BOUNDARY: discovery and planning only across the viewer/profile /
  projection / RiftConfiguration chain.
- DEPENDENCIES:
  - tickets/tasks/2026-04-19_investigate_and_plan_frame_viewer_projection_backed_rift_owned_migration_task.md
  - tickets/epics/2026-04-19_migrate_frame_viewer_to_projection_backed_rift_owned_model_epic.md
- EXIT_GATE: one accepted migration plan exists with explicit state moves,
  constructor cuts, and implementation order.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the plan reveals a real
  shipped need for multiple viewer profiles per viewer.

## Requirements (Functional)
- Prove what the builder does.
- Prove what `active_profiles_by_name` adds beyond the builder.
- Prove what the shipped helper/profile stack actually reads.
- Prove whether raw `FrameACLConfiguration` is needed in the live helper path.
- Prove where `CompiledFrameACLAccessSurface` is built and cloned.
- Prove where projection ownership ends and viewer-local duplication begins.
- Propose the MRP migration shape and order.

## Requirements (Non-Functional)
- No implementation yet.
- No fake optionality or hypothetical future-proofing in the plan.
- Keep the plan bounded to the viewer stack and directly coupled config/state.

## Scope Boundaries
- In scope:
  - `FrameViewer`
  - viewer profile builder/profile stack
  - `ViewProjection`
  - Rift viewer configuration direction
- Out of scope:
  - command/codegen redesign
  - unrelated ACL redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user approved the discovery/plan lane.

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-19-investigate-and-plan-frame-viewer-projection-backed-rift-owned-migration

## Acceptance Criteria
- The story explains why the current viewer stack looks the way it does.
- The story explains why the current shape is too broad for the live product.
- The story proposes the Rift-owned one-profile-per-viewer MRP cut.
- The story explicitly states that the compiled ACL surface remains
  projection-owned because Nexus already generates it there.
- The story explains the two-median problem clearly:
  `ViewProjection` as the first bundle and `FrameViewer` as the current second
  local snapshot layer.
- The user can approve or redirect implementation from this plan alone.

## Validation / Test Plan
- Not run. Planning only.

## Notes
- DATETIME: 2026-04-19T15:27:26Z
  TYPE: PLAN
  CLAIM: The plan must answer four things cleanly:
    1. what the current builder/profile stack is doing,
    2. what state is genuinely viewer-local,
    3. what state should live in `ViewProjection` / `Rift`,
    4. what the safest MRP migration order is.
  EVIDENCE:
  - tickets/epics/2026-04-19_migrate_frame_viewer_to_projection_backed_rift_owned_model_epic.md:1-178
  IMPACT: The task can stay bounded and still give a real implementation-ready
    answer.
  NEXT: land the linked investigation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:38:43Z
  TYPE: FACT
  CLAIM: One migration constraint is now explicit: do not move
    `CompiledFrameACLAccessSurface` out of projection ownership. Nexus already
    compiles it and clones it into `ViewProjection`, so the viewer migration
    should consume that bundled surface rather than inventing another owner.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1573-1699
  - src/melder/aether/nexus/rift/projection/view_projection.py:1-90
  IMPACT: The plan can stay focused on shrinking `FrameViewer` instead of
    rewriting ACL compilation or projection generation.
  NEXT: preserve this ownership rule in the linked task findings and final
    recommendation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T15:41:04Z
  TYPE: FACT
  CLAIM: The deeper full-object reread proves the migration problem is not
    just "too many viewer fields." The live chain already has a correct first
    median layer in `ViewProjection`, but `FrameViewer.sync_from_projection_sets(...)`
    still decomposes that bundle into local descriptor/config/surface maps and
    then rebuilds per-frame bound profiles on top of those local copies. The
    helper trio is already a borrowed consumer tree, so the current second
    median layer lives on the viewer itself.
  EVIDENCE:
  - tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md:1-236
  IMPACT: The story can now state the migration target more precisely:
    preserve the projection bundle, preserve the borrowed helper tree, and
    remove the viewer-owned duplicate median layer.
  NEXT: keep the implementation proposal centered on that ownership cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context / Handoff Summary
This story is the planning lane for the next viewer-stack cleanup after the
Rift-owned projection move.