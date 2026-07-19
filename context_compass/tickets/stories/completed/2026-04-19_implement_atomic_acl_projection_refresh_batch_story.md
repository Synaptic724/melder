# Story: Implement Atomic ACL Projection Refresh Batch
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Story ID: STORY-2026-04-19-implement-atomic-acl-projection-refresh-batch
- Epic: EPIC-2026-04-19-atomic-acl-projection-refresh-barrier
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T10:55:02Z
- Updated: 2026-04-19T16:37:39Z

## User Narrative
As a runtime maintainer, I want ACL-driven projection refresh to freeze the
union of impacted `Rift`s once, drain once, refresh all changed frame
projections for each impacted Rift in one pass, and then reopen once, so live
ACL updates stay coherent when multiple frames change together.

## Value / MRP Alignment
The live runtime already has the correct single-frame barrier semantics. The
missing product slice is batching. Adding a single Nexus batch primitive plus a
single Rift multi-frame refresh path gives us atomic refresh behavior without
inventing a new room or viewer coordination layer.

## Ticket Contract
- ENTRY_GATE: the epic investigation proved the exact missing seams and the
  user explicitly requested the implementation plan plus implementation.
- EXECUTION_BOUNDARY: `Nexus`, `Rift`, focused tests, matching AR docs, and
  the required patch-doc set only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-19_implement_atomic_acl_projection_refresh_batch_task.md
  - system_docs/patches/active/atomic_acl_projection_refresh_barrier/architecture_patch.md
  - system_docs/patches/active/atomic_acl_projection_refresh_barrier/component_patch_nexus.md
  - system_docs/patches/active/atomic_acl_projection_refresh_barrier/component_patch_rift.md
  - system_docs/patches/active/atomic_acl_projection_refresh_barrier/code_description_patch_batch_refresh_flow.md
- EXIT_GATE: Nexus owns one batch barrier path, Rift owns one multi-frame
  refresh path, focused tests are green, and the docs/ticket state are synced.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if timeout semantics or
  viewer-state preservation require a broader runtime transaction model.

## Requirements (Functional)
- Add one Nexus batch refresh primitive for multiple changed frame names.
- Make `_on_frame_acl_changed(frame_name)` and the single-frame helper delegate
  to that batch primitive.
- Add one Rift multi-frame projection refresh path.
- Keep room merge and viewer rebuild one-shot per impacted Rift batch.
- Preserve current viewer profile-selection state across the rebuild.

## Requirements (Non-Functional)
- No duplicate single-frame and multi-frame orchestration logic.
- No new room-level batch coordinator.
- Keep the existing config-backed gate timing surface as the only barrier
  configuration authority.

## Scope Boundaries
- In scope:
  - Nexus batch orchestration
  - Rift multi-frame refresh
  - focused tests for overlap and one-shot rebuild behavior
  - AR doc sync for the batch semantics
- Out of scope:
  - RiftGate redesign
  - viewer API redesign
  - command/codegen redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the batch refresh implementation is landed and the
  focused validation ring is green.

## Dependencies / Related Work
- viewer-ownership epic and implementation task
- configurable refresh barrier task

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-19-implement-atomic-acl-projection-refresh-batch
- [ ] Enforce Ticket Microcycle across linked implementation work.
- [ ] Keep patch-doc consumption mapped in task notes before edits.

## Acceptance Criteria
- Nexus can refresh multiple changed frames in one batch across the union of
  impacted Rifts.
- Each impacted Rift is disabled, drained, refreshed, and reopened once per
  batch.
- Each impacted Rift merges refreshed projections once and rebuilds its viewer
  once per batch.
- The single-frame callback path is a thin delegate to the batch path.
- Focused tests pass.

## Validation / Test Plan
- Focused Nexus unit tests for overlapping changed-frame sets.
- Focused Rift/room tests for one-shot merge/rebuild behavior.

## Risks / Mitigations
- Risk: a timeout during drain could reopen a partially processed batch.
  Mitigation: keep timeout behavior explicit and covered by orchestration
  tests.
- Risk: the batch path could accidentally preserve duplicate single-frame
  refresh calls.
  Mitigation: assert one refresh call per impacted Rift in focused tests.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No cross-task synthesis claims without task-note evidence pointers.
- [ ] No closure while the implementation task remains active or unrouted.

## Open Questions
- Whether timeout should abort the whole batch before any projection swap or
  permit partial unaffected-Rift completion.

## Decision Log
- Pending implementation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-19T10:55:02Z
  TYPE: PLAN
  CLAIM: The implementation split is now explicit. Nexus needs one batch
    orchestration seam over changed frame names, and Rift needs one
    multi-frame refresh seam over the existing room merge/rebuild path.
  EVIDENCE:
  - tickets/epics/2026-04-19_atomic_acl_projection_refresh_barrier_epic.md:13-152
  - src/melder/aether/nexus/nexus.py:1797-1984
  - src/melder/aether/nexus/rift/rift.py:463-529
  IMPACT: The task can stay bounded to the two runtime seams instead of
    widening into room/viewer redesign.
  NEXT: land the linked implementation task and focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T11:01:58Z
  TYPE: FACT
  CLAIM: The child task landed the atomic batch refresh cut. Nexus now owns
    the batch impacted-Rift barrier, Rift now owns one multi-frame refresh
    path, focused tests are green, and the AR docs now describe the batch
    semantics accurately.
  EVIDENCE:
  - tickets/tasks/2026-04-19_implement_atomic_acl_projection_refresh_batch_task.md:1-168
  - codex/context_compass/system_docs/src_architecture.md:520-538
  - codex/context_compass/system_docs/src_components.md:2021-2036
  IMPACT: The story is ready for review instead of more implementation.
  NEXT: hold for acceptance or a bounded follow-on request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when implementation scope, timeout semantics, or validation
  expectations change.
- Reference child-task notes for tactical evidence instead of duplicating them.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story implements the missing batch refresh layer for ACL-driven projection
updates. The room merge/rebuild path already exists; the runtime work is
concentrated in the Nexus and Rift seams.