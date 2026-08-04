# Task: Expand FrameViewer Multi-View Query Helpers
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-expand-frame-viewer-multi-view-query-helpers
- Story: STORY-2026-04-03-frameinfolink-hld
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T04:05:00Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Expand `FrameViewer` with the next real multi-view query helpers so projected
frame surfaces are more usable without widening into a full search DSL.

## Ticket Contract
- ENTRY_GATE: Nexus can already project `FrameView` and `FrameViewer` objects,
  and the user explicitly asked to continue the frame-surface lane.
- EXECUTION_BOUNDARY: `FrameViewer` helper/query expansion only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_wire_frame_viewer_to_projected_frame_views.md
  - tickets/tasks/2026-04-06_project_frame_views_from_nexus_descriptor_and_acl.md
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - tests/unit/melder/aether/test_frame_viewer_projection.py
- EXIT_GATE: `FrameViewer` has richer deterministic multi-view helper methods
  and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the next useful helper layer
  requires a full search DSL or holding-zone cache.

## Scope Boundaries
- In scope:
  - deterministic helper/query methods over attached views and links
  - focused tests
- Out of scope:
  - fuzzy search
  - update subscriptions
  - binding/execution behavior
  - holding-zone cache

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Define the next high-value multi-view query helpers.
- [x] Implement the helper methods.
- [x] Add/update focused tests.
- [x] Run focused validation.
- [x] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- richer `FrameViewer` helper/query layer
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_viewer/
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`

## Risks / Rollback Notes
- Risk: helper growth turns `FrameViewer` into a fake repository/query engine.
  Rollback: keep the helpers deterministic, local, and projection-focused only.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/frame_viewer_multi_view_helpers/architecture_patch.md
  - system_docs/patches/active/frame_viewer_multi_view_helpers/component_patch_frame_viewer.md
  - system_docs/patches/active/frame_viewer_multi_view_helpers/code_description_patch_frame_viewer_multi_view_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T04:05:00Z
  TYPE: PLAN
  CLAIM: The next bounded frame-surface slice is richer multi-view
    `FrameViewer` helpers. The viewer now has basic list/filter/get helpers,
    and Nexus can project it from descriptor plus ACL truth. The next useful
    step is to add deterministic grouped/summarizing helpers over attached
    views and links without drifting into a full search DSL.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-281
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-293
  - user_instruction: "great so continue"
  IMPACT: We can keep improving the frame-surface usability without jumping
    into larger infrastructure yet.
  NEXT: create the patch-doc set, then define the next narrow multi-view
    helper set and implement it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T04:07:00Z
  TYPE: PLAN
  CLAIM: The patch-doc consumption mapping for this viewer-helper slice is now
    explicit. `architecture_patch.md` maps to keeping the helper growth
    deterministic and local. `component_patch_frame_viewer.md` maps to adding
    grouped/count/summarizing helpers to `frame_viewer.py`. The
    `code_description_patch_frame_viewer_multi_view_flow.md` doc maps to the
    reuse of the existing ordered link-list flow for derived helper outputs.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/frame_viewer_multi_view_helpers/architecture_patch.md:1-16
  - codex/context_compass/system_docs/patches/active/frame_viewer_multi_view_helpers/component_patch_frame_viewer.md:1-12
  - codex/context_compass/system_docs/patches/active/frame_viewer_multi_view_helpers/code_description_patch_frame_viewer_multi_view_flow.md:1-13
  IMPACT: The implementation can stay bounded to deterministic helper expansion
    instead of drifting into a search system.
  NEXT: implement the grouped/count/summarizing helpers and add focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T04:12:00Z
  TYPE: FACT
  CLAIM: The richer deterministic `FrameViewer` helper layer is now in code.
    The viewer now adds:
    - `list_links_grouped_by_frame()`
    - `list_links_grouped_by_kind(...)`
    - `list_display_names(...)`
    - `count_links(...)`
    - `describe_frame(...)`
    - `describe_frames()`
    while keeping the surface view-local and deterministic. One ordering bug in
    `describe_frames()` was fixed so frame summaries are keyed in sorted frame
    order.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-426
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-448
  IMPACT: `FrameViewer` is materially more usable across multiple projected
    views without drifting into a full query engine.
  NEXT: review whether the next frame-surface slice should keep enriching
    viewer helpers or pivot back to another lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T04:12:00Z
  TYPE: MEASURE
  CLAIM: The richer multi-view `FrameViewer` helper slice is green. The focused
    viewer/view/Nexus-projection validation surface passed with 34 tests.
  EVIDENCE:
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The helper expansion is stable enough to review as a bounded slice.
  NEXT: decide whether to keep iterating viewer helper richness or switch
    lanes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to extend the `FrameViewer` helper layer after the Nexus
projection bridge landed.



