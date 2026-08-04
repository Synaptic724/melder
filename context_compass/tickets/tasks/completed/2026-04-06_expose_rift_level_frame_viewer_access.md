# Task: Expose Rift-Level FrameViewer Access
- Completed: 2026-04-09T11:31:39Z
- Summary: Exposed the assigned-view chain directly on Rift and added explicit default-view targeting on the viewer.


## Metadata
- Task ID: TASK-2026-04-06-expose-rift-level-frame-viewer-access
- Story: STORY-2026-04-06-contract-backed-assigned-frame-views
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T15:18:46Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Expose the assigned-view chain directly on `Rift` and make `FrameViewer`
explicitly target one default/active assigned view so the agent can consume the
frame-surface chain through the Rift object instead of only through Nexus
helper calls.

## Ticket Contract
- ENTRY_GATE: the assigned-view chain and the Rift-level frame availability
  contract are landed.
- EXECUTION_BOUNDARY: Rift-facing viewer access plus default/active view
  targeting only.
- DEPENDENCIES:
  - codex/context_compass/tickets/tasks/2026-04-06_repurpose_frame_link_contract_to_rift_frame_availability.md
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/nexus.py
- EXIT_GATE: the Rift can build viewers from its assigned-frame contract and
  the viewer exposes an explicit default/active assigned view.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the clean implementation
  requires full workspace lifecycle ownership in the same slice.

## Scope Boundaries
- In scope:
  - Rift helper methods for building frame viewers
  - default/active assigned view targeting on `FrameViewer`
  - focused unit/integration tests
- Out of scope:
  - workspace object exposure
  - codegen runtime
  - new ACL behavior

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the Rift-facing viewer access slice is implemented, the
  focused test surface passed, and the task is ready for review.

## Steps / Checklist
- [ ] Add default/active view targeting to `FrameViewer`.
- [ ] Add Rift-facing viewer construction helpers.
- [ ] Wire the default assigned frame from the Rift contract into the viewer.
- [ ] Update focused tests.
- [ ] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- Rift-facing viewer access
- active/default view targeting
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
- src/melder/aether/nexus/nexus.py
- tests/unit/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`

## Risks / Rollback Notes
- Risk: the slice drifts into full workspace ownership instead of staying on
  frame-viewer access.
  Rollback: keep the cut bounded to viewer construction and default/active
  view targeting.

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
- DATETIME: 2026-04-06T15:18:46Z
  TYPE: PLAN
  CLAIM: The assigned-view chain is now real, but the most usable next cut is
    to expose it directly from `Rift` and make the viewer target one default
    assigned view explicitly. Right now the chain is still primarily consumed
    through `Nexus.create_frame_viewer_for_rift(...)`. The next bounded step is
    to add the Rift helper methods and one default/active assigned-view target
    on the viewer itself.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:124-151
  - src/melder/aether/nexus/nexus.py:1576-1720
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:232-241
  IMPACT: This makes the current frame-surface chain more directly usable
    without widening into full workspace ownership yet.
  NEXT: inspect the current Rift/viewer methods and add the smallest default
    assigned-view targeting layer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T15:18:46Z
  TYPE: FACT
  CLAIM: The current runtime still lacks the last direct-use step for the
    chain. `FrameViewer` owns `available_views_by_frame_name`, but it does not
    yet track one explicit default/active assigned view. And `Rift` owns the
    assigned-frame contract, but it still does not expose the viewer
    construction path directly. So the chain exists structurally, but the
    consumer-facing access point is still awkward.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:174-183
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:257-283
  - src/melder/aether/nexus/rift/rift.py:326-371
  - src/melder/aether/nexus/nexus.py:1576-1720
  IMPACT: The next bounded cut should not change the core model; it should make
    the current model directly usable from the Rift object.
  NEXT: add default assigned-view targeting on `FrameViewer` and Rift methods
    that build viewers from `frame_link_contract`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T15:18:46Z
  TYPE: FACT
  CLAIM: The direct-use layer is now in code. `FrameViewer` now owns an
    explicit `default_view_frame_name` plus `get_default_view()` and
    `set_default_view(...)`. `Rift` now exposes:
    - `list_assigned_frame_names()`
    - `create_frame_viewer(...)`
    - `create_cached_frame_viewer(...)`
    and Nexus now threads the default assigned frame from the Rift contract
    into the viewer created through the Rift path.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:84-183
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:274-312
  - src/melder/aether/nexus/rift/rift.py:362-434
  - src/melder/aether/nexus/nexus.py:1587-1599
  - src/melder/aether/nexus/nexus.py:1707-1719
  IMPACT: The frame-surface chain is now directly consumable from the Rift
    object instead of only through Nexus internals.
  NEXT: run the focused Rift/viewer slice and confirm the new direct-use layer
    holds.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T15:18:46Z
  TYPE: MEASURE
  CLAIM: The focused Rift-facing viewer slice is green. One unit test needed a
    real descriptor seed because building a viewer for a Rift with an assigned
    frame still requires frame descriptor truth to exist. After seeding the
    minimal frame overview for that test, the focused viewer/Rift/Nexus unit +
    integration surface passed cleanly.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:49-107
  - tests/unit/melder/aether/test_nexus.py:537-552
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-911
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The direct-use layer is stable enough to review as the next bounded
    frame-surface slice.
  NEXT: review whether the next cut should enrich per-view behavior or start
    building the workspace-facing host around the current Rift/viewer chain.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

