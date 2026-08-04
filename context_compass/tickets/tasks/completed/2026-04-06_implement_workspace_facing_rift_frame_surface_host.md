# Task: Implement Workspace-Facing Rift Frame Surface Host
- Completed: 2026-04-09T11:31:39Z
- Summary: Added the workspace-facing host seam by letting RiftSpace own the attached FrameViewer.


## Metadata
- Task ID: TASK-2026-04-06-implement-workspace-facing-rift-frame-surface-host
- Story: STORY-2026-04-06-contract-backed-assigned-frame-views
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T15:33:12Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Build the smallest real workspace-facing host on top of the current
Rift-assignment -> assigned views -> profile-shaped target surface chain so a
Rift exposes a coherent hosted frame-surface object for the agent to use.

## Ticket Contract
- ENTRY_GATE: the per-view behavior slice is landed and the current frame
  surface chain is directly consumable from `Rift`.
- EXECUTION_BOUNDARY: workspace-facing host behavior only.
- DEPENDENCIES:
  - codex/context_compass/tickets/tasks/2026-04-06_expose_rift_level_frame_viewer_access.md
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/
  - src/melder/aether/nexus/rift/frame_viewer/
- EXIT_GATE: the Rift exposes a coherent hosted frame-surface object for the
  agent without widening into a full workspace runtime redesign.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the clean host requires a
  broader workspace/room ownership redesign in the same slice.

## Scope Boundaries
- In scope:
  - smallest host object/path over the current viewer chain
  - Rift-facing access to that host
  - focused tests
- Out of scope:
  - codegen runtime
  - command execution engine redesign
  - ACL redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the workspace-facing host slice is implemented, the
  focused tests passed, and the task is ready for review.

## Steps / Checklist
- [ ] Inspect the current Rift/RiftSpace/FrameViewer path and identify the
      smallest host seam.
- [ ] Implement the workspace-facing host path.
- [ ] Add/update focused tests.
- [ ] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- workspace-facing host over the current frame surface chain
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/
- tests/unit/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`

## Risks / Rollback Notes
- Risk: the slice drifts into a full workspace redesign.
  Rollback: keep the cut bounded to the smallest host path over the current
  viewer chain.

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
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T15:33:12Z
  TYPE: PLAN
  CLAIM: The next bounded frame-surface step is the workspace-facing host. The
    assigned-view chain, the availability contract, the Rift-facing viewer
    access, and the per-view behavior layer are all landed now. The most useful
    next cut is to expose that chain through one coherent host object/path from
    Rift instead of only through lower-level helper methods.
  EVIDENCE:
  - user_instruction: "I'd build the workspace-facing host next."
  - src/melder/aether/nexus/rift/rift.py:362-434
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:174-760
  IMPACT: This can make the current chain directly usable without widening into
    codegen or a broader workspace redesign yet.
  NEXT: inspect the current `RiftSpace`/`Rift`/viewer seams and identify the
    smallest real host surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T15:33:12Z
  TYPE: FACT
  CLAIM: The smallest real host seam is `RiftSpace`, not another new wrapper.
    `RiftSpace` already exists as the room/workspace object, but today it only
    owns room metadata and event configuration. `Rift` already owns the
    assigned-frame contract and can already build viewers from it. So the
    smallest host cut is:
    - let `RiftSpace` own an attached `FrameViewer`
    - let `Rift` build that viewer from its assigned-frame chain
    - let `Rift` install it onto a space
    That exposes the current chain through the workspace boundary without
    widening into a full runtime redesign.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:1-112
  - src/melder/aether/nexus/rift/rift.py:397-434
  - tests/unit/melder/aether/test_nexus.py:481-552
  IMPACT: The host slice can stay bounded to one new ownership seam on
    `RiftSpace` plus one Rift helper path.
  NEXT: add attached-viewer ownership to `RiftSpace`, then add Rift helpers and
    focused tests around that host path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T15:33:12Z
  TYPE: FACT
  CLAIM: The host path is now in code. `RiftSpace` now owns an optional
    attached `FrameViewer` and exposes:
    - `frame_viewer`
    - `attach_frame_viewer(...)`
    - `detach_frame_viewer()`
    `Rift` now exposes:
    - `attach_frame_viewer_to_space(...)`
    - `get_space_frame_viewer(...)`
    and can therefore install the current assigned-view chain directly onto a
    space instead of forcing callers to manage that stitching themselves.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:18-109
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:163-208
  - src/melder/aether/nexus/rift/rift.py:404-474
  IMPACT: The current frame-surface chain now has a real workspace-facing host
    seam without widening into a full workspace/runtime redesign.
  NEXT: run the focused host slice and confirm the Rift/RiftSpace path works.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T15:33:12Z
  TYPE: MEASURE
  CLAIM: The focused workspace-facing host slice is green. The targeted
    unit/integration surface covering `Rift`, `RiftSpace`, viewer access,
    assigned views, and Nexus projection passed cleanly after simplifying one
    new unit test to use a direct `FrameViewer()` instance instead of requiring
    extra descriptor setup.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:481-585
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-980
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The workspace-facing host seam is stable enough to review as the next
    bounded frame-surface slice.
  NEXT: review whether the next cut should deepen host behavior on `RiftSpace`
    or start integrating codegen-facing workspace use over the hosted viewer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

