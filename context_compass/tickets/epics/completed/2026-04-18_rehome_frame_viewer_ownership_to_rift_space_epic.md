# Epic: Rehome FrameViewer Ownership To RiftSpace
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Epic ID: EPIC-2026-04-18-rehome-frame-viewer-ownership-to-rift-space
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T22:59:13Z
- Updated: 2026-04-19T16:37:39Z
- Target Window: 2026-04-18
- Related Program/Initiative: AetherRift runtime ownership cleanup

## Problem / Opportunity
`Nexus` currently owns both projection building and `FrameViewer` assembly.
That splits ownership across three layers:
- `FrameLinkContract` on `Rift` selects the frame-local `view` / `command` /
  `codegen` contract names.
- `Nexus` builds `FrameProjectionSet` objects from descriptor truth plus ACL
  truth.
- `RiftSpace` stores the installed projection sets, but does not build the
  viewer from them.

The live call path currently does extra work:
- `Rift.refresh_runtime_projections(...)` asks `Nexus` for fresh projection
  sets and installs them on the room.
- The same refresh then asks `Nexus` to build a `FrameViewer`, and that path
  rebuilds fresh projection sets again before constructing the viewer.
- `RiftSpace` only stores the viewer and patches the `RiftGate` into it after
  construction.

That means the room already owns the inputs the viewer needs, but not the
assembly step.

## MRP Alignment (Most Reasonable Product)
The honest ownership model is:
- `Nexus` owns descriptor truth, ACL truth, and projection compilation.
- `Rift` owns frame-target contracts and refresh orchestration.
- `RiftSpace` owns the live interaction surface, including the attached
  `FrameViewer`.

Moving viewer assembly into `RiftSpace` makes the runtime more coherent:
- the room consumes the already-installed `ViewProjection`,
- the room passes `rift_gate` at construction time,
- static wrapping stays a room concern,
- `Nexus` stops pretending it owns room-facing viewer lifecycle.

## Ticket Contract
- ENTRY_GATE: source-grounded investigation proves the current ownership split
  and the user requested a detailed migration plan.
- EXECUTION_BOUNDARY: viewer ownership, viewer build/caching seams, Rift
  refresh orchestration, and directly affected docs/tests only.
- DEPENDENCIES:
  - tickets/stories/2026-04-18_plan_rift_space_owned_frame_viewer_migration_story.md
  - tickets/tasks/2026-04-18_investigate_and_plan_rift_space_owned_frame_viewer_migration_task.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
- EXIT_GATE: `RiftSpace` builds and owns live viewers from installed
  projections, `Nexus` no longer builds viewers, focused tests/docs are
  updated, and no backward-compat shims remain.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the migration exposes a
  broader frame-target/default-frame redesign that should be split out.

## Goals (Outcomes)
- Make `RiftSpace` the owner of `FrameViewer` assembly and replacement.
- Keep `Nexus` limited to descriptor truth, ACL truth, and projection
  compilation.
- Remove duplicated projection work during viewer refresh.
- Keep static-room viewer wrapping as a room-local concern.
- Remove viewer-builder seams from `Nexus` and delegation seams from `Rift`
  once the room-owned path is live.

## Non-Goals (Explicit Exclusions)
- Do not redesign `CommandSystem` in this epic.
- Do not redesign `CodegenSystem` in this epic.
- Do not solve explicit `frame_name` enforcement in this epic unless a small
  change is directly required by the ownership move.
- Do not add compatibility aliases for removed viewer-builder APIs.

## Scope Boundaries
- In scope:
  - generic viewer assembly from `ViewProjection`
  - static viewer wrapping path
  - Rift refresh orchestration updates
  - cached-viewer ownership decision
  - focused tests and architecture/component docs
- Out of scope:
  - command/codegen refactors unrelated to viewer ownership
  - target-selection redesign
  - multi-room model redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the ownership move is implemented and the focused
  validation ring is green.

## Success Metrics
- One viewer build path exists, and it lives in `RiftSpace`.
- `Rift.refresh_runtime_projections(...)` no longer rebuilds projections again
  through viewer creation.
- `Nexus.create_frame_viewer*` and cache seams are removed or relocated.
- Static viewer composition still works without post-construction gate patching.

## Requirements (Functional + Non-Functional)
- `RiftSpace` must be able to build a generic `FrameViewer` from its installed
  `ViewProjection` objects.
- `StaticRiftSpace` must keep room-local wrapping through
  `StaticFrameViewer.from_frame_viewer(...)` or an equivalent room-owned
  factory path.
- The room-owned viewer build path must pass `rift_gate` directly to
  `FrameViewer(...)` instead of calling `bind_rift_gate(...)` afterward.
- The migration must not leave backward-compat shims for the removed Nexus
  viewer-builder APIs.
- The migration must keep code/doc ownership explicit and reviewable.

## Constraints / Assumptions
- `FrameLinkContract` owns only selected contract names, not projection or
  viewer instances.
- `FrameProjectionSet.view_projection` already carries the descriptor, detached
  ACL configuration, and detached compiled surface the viewer needs.
- `FrameViewer.__init__(...)` already accepts those inputs plus `rift_gate`.
- Static wrapping is already room-local in `StaticRiftSpace._replace_frame_viewer(...)`.

## Dependencies / External References
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md
- recent review-state cleanup tickets around room/viewer seams and projection
  ownership

## Milestones (Track Progress)
- [x] Milestone 1: Ownership investigation complete
      Source-backed explanation exists for why viewer ownership is currently
      split and why it should move.
- [x] Milestone 2: Room-owned generic viewer builder landed
      `RiftSpace` can assemble a `FrameViewer` from installed projection sets.
- [x] Milestone 3: Nexus/Rift viewer-builder seams removed
      `Nexus.create_frame_viewer*` and Rift delegation helpers are gone with no
      compatibility layer left behind.

## Stories (Required to Complete)
- [x] Story: STORY-2026-04-18-plan-rift-space-owned-frame-viewer-migration -
      source-grounded migration plan and execution boundary
- [x] Story: STORY-2026-04-18-implement-rift-space-owned-frame-viewer-migration -
      move generic viewer assembly into `RiftSpace` and remove old builder seams
- [x] Story: STORY-2026-04-18-add-configurable-rift-gate-projection-refresh -
      add the default-on config surface for ACL-driven refresh gating

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: TASK-2026-04-18-investigate-and-plan-rift-space-owned-frame-viewer-migration
- [x] Task: TASK-2026-04-18-implement-rift-space-owned-frame-viewer-builder-and-remove-nexus-viewer-seams
- [x] Task: TASK-2026-04-18-implement-configurable-rift-gate-projection-refresh
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- `Nexus` no longer constructs `FrameViewer` instances.
- `RiftSpace` builds the live viewer directly from installed projections.
- `Rift` refreshes projections and asks the room to rebuild its viewer instead
  of delegating viewer assembly to `Nexus`.
- Static rooms still produce `StaticFrameViewer` behavior without a post-build
  gate patch seam.
- Focused tests and `codex/context_compass/system_docs/*` are updated to match
  the landed ownership model.

## Risks / Mitigations
- Risk: cached-viewer ownership is currently Nexus-local and may be coupled to
  configuration ids.
  Mitigation: decide early whether cache ownership moves into `RiftSpace` or
  is deleted as non-essential.
- Risk: static viewer wrapping may accidentally stay as a post-build seam.
  Mitigation: keep room-mode viewer composition as part of the room-owned build
  path, not a Nexus concern.
- Risk: default-frame behavior in `FrameViewer` may bleed into the migration.
  Mitigation: keep explicit frame-target enforcement as a separate lane unless
  a small direct fix is required here.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Planning-only in this ticket tranche.
- Implementation validation will require focused Rift/Nexus/RiftSpace/viewer
  rings once the code migration is staged.

## Rollout / Adoption Plan
- First approve the ownership plan.
- Then land the room-owned generic viewer builder.
- Then remove Nexus/Rift builder seams and port tests/docs in one cleanup cut.

## Open Questions
- Should viewer caching survive this move, and if so should it live on
  `RiftSpace` or on `Rift` rather than `Nexus`?
- Should `Rift.create_new_frame_viewer(...)` survive as a frame-scoped helper
  or die with the rest of the viewer-builder delegation family?
- Should the room-owned builder expose one internal generic helper plus room
  subclass overrides, or should static wrapping remain only in
  `_replace_frame_viewer(...)` for one intermediate slice?

## Decision Log
- Pending user review of the migration plan before implementation begins.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-18T22:59:13Z
  TYPE: FACT
  CLAIM: The current viewer ownership split is real: `Nexus` builds
    `FrameProjectionSet` objects and also assembles `FrameViewer` objects,
    while `RiftSpace` only stores the viewer and post-binds the gate.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1631-2273
  - src/melder/aether/nexus/rift/rift.py:463-628
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:151-516
  IMPACT: Viewer ownership is split across layers that should have cleaner
    boundaries, and refresh currently does duplicated work.
  NEXT: stage the migration plan and get user approval before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T22:59:13Z
  TYPE: FACT
  CLAIM: `FrameViewer.__init__(...)` already accepts exactly the room-owned
    inputs it needs: descriptor refs, detached ACL configs, detached compiled
    access surfaces, selected profiles, default frame name, and optional
    `rift_gate`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:82-172
  - src/melder/aether/nexus/rift/projection/view_projection.py:6-96
  - src/melder/aether/nexus/rift/projection/frame_projection_set.py:10-90
  IMPACT: `Nexus` is not required to assemble viewers; the room can consume
    installed `ViewProjection` objects directly.
  NEXT: define the room-owned builder cut and the seam removals behind it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T22:59:13Z
  TYPE: PLAN
  CLAIM: The migration should happen in three cuts: first move generic viewer
    assembly into `RiftSpace`, then keep static wrapping room-local, then
    delete the Nexus/Rift viewer-builder and cache seams with focused test/doc
    updates.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:15-104
  - src/melder/aether/nexus/nexus.py:1815-2273
  - src/melder/aether/nexus/rift/rift.py:554-628
  IMPACT: This keeps the ownership move reviewable and avoids mixing it with
    unrelated command/codegen or frame-target redesign.
  NEXT: capture the same plan in the story/task and present it to the user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T23:05:00Z
  TYPE: DECISION
  CLAIM: The user approved implementation of the room-owned viewer migration.
    The epic is now active with one implementation story/task staged behind the
    required patch-doc gate.
  EVIDENCE:
  - tickets/stories/2026-04-18_implement_rift_space_owned_frame_viewer_migration_story.md:1-108
  - tickets/tasks/2026-04-18_implement_rift_space_owned_frame_viewer_builder_and_remove_nexus_viewer_seams_task.md:1-136
  IMPACT: The next step is runtime code implementation, not more ownership
    planning.
  NEXT: land the implementation task and validate the focused rings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T23:27:29Z
  TYPE: FACT
  CLAIM: The ownership move is now implemented: `RiftSpace` builds the viewer,
    `StaticRiftSpace` keeps the static wrapper, `Rift` only orchestrates
    refresh, `Nexus` only builds projections, and the old viewer-builder/cache
    seams are gone.
  EVIDENCE:
  - tickets/stories/2026-04-18_implement_rift_space_owned_frame_viewer_migration_story.md:1-90
  - tickets/tasks/2026-04-18_implement_rift_space_owned_frame_viewer_builder_and_remove_nexus_viewer_seams_task.md:1-174
  IMPACT: The epic is back in review and no longer needs active implementation
    work unless a follow-on is requested.
  NEXT: hold for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T23:58:36Z
  TYPE: FACT
  CLAIM: The follow-on config slice is also implemented. The refresh barrier is
    now explicit in `NexusConfiguration` with a safe default-on flag plus
    timing settings, and the focused config/Nexus ring is green.
  EVIDENCE:
  - tickets/stories/2026-04-18_add_configurable_rift_gate_projection_refresh_story.md:1-94
  - tickets/tasks/2026-04-18_implement_configurable_rift_gate_projection_refresh_task.md:1-168
  IMPACT: The epic now contains both the ownership move and the default-on
    refresh-barrier config follow-on.
  NEXT: hold for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

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
This epic tracks the migration of `FrameViewer` ownership out of `Nexus` and
into `RiftSpace`. The bounded ownership move is implemented and waiting on
review.