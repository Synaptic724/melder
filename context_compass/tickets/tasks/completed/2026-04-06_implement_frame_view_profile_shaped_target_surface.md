# Task: Implement FrameView Profile-Shaped Target Surface
- Completed: 2026-04-09T11:31:39Z
- Summary: Made per-view profiles shape the frame-local target surface and exposed it through the viewer.


## Metadata
- Task ID: TASK-2026-04-06-implement-frame-view-profile-shaped-target-surface
- Story: STORY-2026-04-06-contract-backed-assigned-frame-views
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T15:28:37Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Make `FrameViewProfile` actually shape the frame-local available-target surface
through active-profile ordering/detail behavior, and expose that shaped target
surface through `FrameViewer` commands.

## Ticket Contract
- ENTRY_GATE: the assigned-view chain, the Rift availability contract, and the
  Rift-facing viewer access layer are landed.
- EXECUTION_BOUNDARY: per-view profile behavior and the smallest viewer
  delegation needed to expose it.
- DEPENDENCIES:
  - codex/context_compass/tickets/tasks/2026-04-06_expose_rift_level_frame_viewer_access.md
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_view_profile.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
- EXIT_GATE: frame-view profiles shape the local target surface and the viewer
  can expose that shaped surface through focused commands.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the slice requires a broader
  viewer-profile redesign in the same cut.

## Scope Boundaries
- In scope:
  - default/active view profile selection on `FrameView`
  - profile-shaped target ordering/detail behavior
  - viewer delegation methods that expose the shaped target surface
  - focused unit tests
- Out of scope:
  - workspace runtime
  - codegen runtime
  - broader ACL changes

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the per-view behavior slice is implemented, the focused
  frame-surface tests passed, and the task is ready for review.

## Steps / Checklist
- [ ] Add default/active profile targeting to `FrameView`.
- [ ] Add profile-shaped available-target ordering/detail methods on the view.
- [ ] Add the minimal `FrameViewer` delegation commands over that shaped
      surface.
- [ ] Update focused unit tests.
- [ ] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- profile-shaped target surface on `FrameView`
- viewer commands that expose it
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_viewer/
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`

## Risks / Rollback Notes
- Risk: the slice drifts into a full viewer-DSL redesign.
  Rollback: keep the cut bounded to ordering/detail shaping plus viewer
  delegation only.

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
- DATETIME: 2026-04-06T15:28:37Z
  TYPE: PLAN
  CLAIM: The next bounded gap is per-view behavior. The current runtime has
    local `FrameView` profiles, but they still do not actually shape the
    target surface. The smallest real next step is to give `FrameView` a
    default/active view profile and let that profile control available-target
    ordering/detail, then expose that shaped surface through the viewer.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:68-90
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:426-616
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_view_profile.py:1-101
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:174-236
  IMPACT: This adds real value to the current chain without widening into a
    whole new host/runtime layer.
  NEXT: implement default view-profile targeting on `FrameView` and one shaped
    target-ordering path first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T15:28:37Z
  TYPE: FACT
  CLAIM: The per-view behavior layer is now in code. `FrameView` now owns:
    - `default_profile_name`
    - `get_default_profile()`
    - `set_default_profile(...)`
    - `list_available_targets_in_profile_order(...)`
    - `describe_available_targets(...)`
    And `FrameViewer` now delegates to that shaped surface through:
    - `list_available_targets(...)`
    - `describe_available_targets(...)`
    while preserving the existing assigned-view chain and Rift-facing access
    layer.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:68-90
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:510-689
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:274-312
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:523-587
  IMPACT: `FrameViewProfile` now shapes the local target surface instead of
    remaining passive metadata only.
  NEXT: run the focused frame-surface slice and confirm the shaping behavior
    holds end to end.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T15:28:37Z
  TYPE: MEASURE
  CLAIM: The focused per-view behavior slice is green. The targeted unit and
    integration surface covering frame-view profiles, shaped target ordering,
    viewer delegation, Rift-facing viewer access, and Nexus projection passed
    cleanly.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py:1-280
  - tests/unit/melder/aether/test_frame_view_contract_projection.py:1-380
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-980
  - tests/unit/melder/aether/test_nexus.py:1-980
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:1-438
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The current frame-surface chain is stable enough to review as the
    next real behavior slice rather than just another placeholder refactor.
  NEXT: review whether the next cut should move upward into the workspace-facing
    host or deepen per-profile/view switching behavior further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

