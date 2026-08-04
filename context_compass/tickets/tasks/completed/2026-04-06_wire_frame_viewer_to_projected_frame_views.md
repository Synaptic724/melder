# Task: Wire FrameViewer To Projected Frame Views
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-wire-frame-viewer-to-projected-frame-views
- Story: STORY-2026-04-03-frameinfolink-hld
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T03:30:00Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Implement the first real `FrameViewer` consumption layer over the projected
`FrameView` objects so the frame-surface stack can do real read/query work
instead of stopping at passive containers.

## Ticket Contract
- ENTRY_GATE: `FrameLink` and `FrameView` now consume compiled ACL output, and
  the user explicitly asked to continue.
- EXECUTION_BOUNDARY: `FrameViewer` query/helper wiring only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_wire_frame_link_and_frame_view_to_compiled_acl_contract.md
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py
  - src/melder/aether/nexus/rift/frame_link/frame_link.py
- EXIT_GATE: `FrameViewer` can consume projected `FrameView` objects through a
  small real query/helper layer and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a clean query surface
  requires the full Nexus holding-zone implementation first.

## Scope Boundaries
- In scope:
  - `FrameViewer` view registration/lookup helpers
  - small query/read helpers over projected views and links
  - focused tests
- Out of scope:
  - full search DSL
  - event/update streaming
  - direct binding/execution behavior
  - full Nexus holding-zone implementation

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Define the smallest real query/helper surface `FrameViewer` should own.
- [x] Implement the `FrameViewer` wiring changes.
- [x] Add/update focused tests.
- [x] Run focused validation.
- [x] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- wired `FrameViewer` helper/query layer
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_viewer/
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_frame_link_runtime_contracts.py`

## Risks / Rollback Notes
- Risk: the viewer grows into a fake repository/query engine before the holding
  zone exists.
  Rollback: keep the helper layer narrow and view-local.

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
  - system_docs/patches/active/frame_viewer_query_wiring/architecture_patch.md
  - system_docs/patches/active/frame_viewer_query_wiring/component_patch_frame_viewer.md
  - system_docs/patches/active/frame_viewer_query_wiring/code_description_patch_frame_viewer_query_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T03:30:00Z
  TYPE: PLAN
  CLAIM: The next bounded frame-surface slice is `FrameViewer` consumption over
    the projected `FrameView` objects. The compiled ACL contract now reaches
    `FrameLink` and `FrameView`, but `FrameViewer` is still just a passive
    holder with only trivial add/get/list behavior. The next clean cut is to
    add a narrow real query/helper layer there without pretending the full
    holding-zone or search DSL already exists.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-158
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:1-350
  - user_instruction: "ok cool continue"
  IMPACT: We can keep forward momentum on the frame-surface stack without
    widening into the missing holding-zone implementation yet.
  NEXT: create the patch-doc set, then define the smallest real `FrameViewer`
    query/helper surface and implement it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T03:32:00Z
  TYPE: PLAN
  CLAIM: The patch-doc consumption mapping for this viewer slice is now
    explicit. `architecture_patch.md` maps to keeping the viewer layer narrow
    and view-local. `component_patch_frame_viewer.md` maps to adding the first
    real helper/query surface to `frame_viewer.py`. The
    `code_description_patch_frame_viewer_query_flow.md` doc maps to the
    deterministic view/link read flow and fail-fast error behavior.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/frame_viewer_query_wiring/architecture_patch.md:1-16
  - codex/context_compass/system_docs/patches/active/frame_viewer_query_wiring/component_patch_frame_viewer.md:1-11
  - codex/context_compass/system_docs/patches/active/frame_viewer_query_wiring/code_description_patch_frame_viewer_query_flow.md:1-14
  IMPACT: The code cut can stay bounded to the first real `FrameViewer`
    helper/query layer instead of drifting into a broader surface rewrite.
  NEXT: inspect the current `FrameViewer` code and implement the smallest real
    helper/query methods with focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T03:38:00Z
  TYPE: FACT
  CLAIM: The first real `FrameViewer` helper layer is now implemented. The
    viewer now uses a lock for grouped mutation/cleanup, snapshots its
    `views_by_frame_name` and `metadata` properties, validates `FrameView`
    registration, and exposes a narrow real query surface:
    - `list_links(...)`
    - `list_links_by_kind(...)`
    - `get_required_link_by_source(...)`
    It remains view-local and does not drift into binding, ACL evaluation, or
    a fake repository layer.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-281
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-293
  IMPACT: The frame-surface stack now has a real read/query progression:
    compiled ACL output -> `FrameLinkContract` -> `FrameLink` -> `FrameView` ->
    `FrameViewer`.
  NEXT: review whether the next frame-surface slice should stay on viewer
    helpers or wait for the Nexus holding-zone implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T03:38:00Z
  TYPE: MEASURE
  CLAIM: The focused `FrameViewer` helper slice is green. The viewer/view/link
    validation surface passed with 23 tests.
  EVIDENCE:
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_frame_link_runtime_contracts.py
  IMPACT: The `FrameViewer` helper/query bridge is stable enough to review as a
    bounded slice.
  NEXT: decide whether to continue iterating the viewer helper layer or pause
    for the Nexus holding-zone work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to give `FrameViewer` its first real projected-view query
surface after the `FrameLink` / `FrameView` bridge landed.



