# Task: Implement Contract-Backed Assigned Frame Views
- Completed: 2026-04-09T11:31:39Z
- Summary: Landed the assigned-view runtime chain so Rift-assigned frames become available views with filtered target surfaces.


## Metadata
- Task ID: TASK-2026-04-06-implement-contract-backed-assigned-frame-views
- Story: STORY-2026-04-06-contract-backed-assigned-frame-views
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T14:31:44Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Implement the runtime chain where Rift-assigned frames become assigned
`FrameView`s on the viewer and each assigned `FrameView` owns a full filtered
`available_targets` surface built from the whole frame descriptor in one shot.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved building the frame-assignment chain
  and the live investigation proved the current runtime still bypasses it.
- EXECUTION_BOUNDARY: assigned views, frame-local available targets, and the
  smallest Rift/Nexus wiring needed for that chain.
- DEPENDENCIES:
  - codex/context_compass/tickets/stories/2026-04-06_contract_backed_assigned_frame_views_story.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/rift.py
- EXIT_GATE: assigned views are real runtime state, `FrameView` exposes the
  filtered available-target surface, and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the task requires fully
  repurposing `FrameLinkContract` into a Rift-global contract in the same cut.

## Scope Boundaries
- In scope:
  - `FrameView.available_targets`
  - frame-local profile builder/active profile runtime on the view
  - `FrameViewer.available_views`
  - Rift/Nexus wiring that populates assigned views from registered frames
  - focused tests
- Out of scope:
  - broad viewer DSL work
  - codegen runtime
  - mutation work

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the assigned-view runtime chain is implemented, the
  focused unit/integration slice passed, and the task is ready for review.

## Steps / Checklist
- [ ] Implement `FrameView` available-target and local profile runtime.
- [ ] Implement explicit `available_views` hosting on `FrameViewer`.
- [ ] Add the minimum Rift/Nexus chain that populates assigned views from
      registered frames.
- [ ] Update focused unit/integration tests.
- [ ] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- assigned-view runtime behavior
- frame-local filtered target surface
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_viewer/
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/nexus.py
- tests/unit/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`

## Risks / Rollback Notes
- Risk: the task drifts into a full contract rewrite.
  Rollback: keep the first cut on assigned views and available targets, and
  leave larger contract-shape redesign for a later explicit task.

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
- DATETIME: 2026-04-06T14:31:44Z
  TYPE: PLAN
  CLAIM: The current runtime still jumps straight from raw `frame_names` to
    projected views in `Nexus.create_frame_viewer(...)`. The first bounded fix
    is to make assigned views explicit, give `FrameView` a real
    `available_targets` surface, and have the viewer host only those assigned
    views.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1502-1574
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:68-80
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:290-325
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:75-84
  - src/melder/aether/nexus/rift/rift.py:124-141
  IMPACT: This task directly targets the actual runtime gap instead of more
    abstract ownership discussion.
  NEXT: implement the assigned-view and available-target surfaces in the view
    and viewer objects first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T14:31:44Z
  TYPE: FACT
  CLAIM: The assigned-view chain is now materially more real in code. `FrameView`
    now owns:
    - `available_targets_by_id`
    - `available_target_ids_by_kind`
    - a local `FrameViewProfileBuilder`
    - local `active_profiles_by_name`
    `FrameViewer` now owns:
    - explicit `available_views_by_frame_name`
    - a local `FrameViewerProfileBuilder`
    - local `active_profiles_by_name`
    - multi-profile `execute_tool(profile_name=..., tool_name=...)`
    And Nexus now exposes `create_frame_viewer_for_rift(...)` and
    `create_cached_frame_viewer_for_rift(...)`, which populate the viewer from
    the Rift's assigned target frames instead of only from raw frame-name
    inputs.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:86-90
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:426-616
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:75-80
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:232-241
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:701-833
  - src/melder/aether/nexus/nexus.py:1556-1568
  - src/melder/aether/nexus/nexus.py:1574-1650
  IMPACT: The runtime now matches the intended chain much more closely:
    Rift assignment -> assigned views -> available targets -> hosted viewer
    commands.
  NEXT: run the focused unit/integration slice and see whether any contract or
    expectation drift remains.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T14:31:44Z
  TYPE: MEASURE
  CLAIM: The focused assigned-view slice is green. One stale test expectation
    surfaced during the first validation pass: the live default ACL path only
    projected the frame target in the Nexus projection test helper, so older
    expectations that every `ops` projection included conduit/spell targets were
    stale. After aligning those expectations to the live runtime and enabling
    target-frame override in the Rift-viewer unit helper, the focused unit and
    integration slice passed cleanly.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_viewer_projection.py:872-872
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:184-207
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:415-432
  - tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py:119-157
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The assigned-view chain is stable enough to review as the next real
    Nexus frame-surface behavior slice.
  NEXT: review the slice with the user and decide whether the next cut should
    populate `FrameLinkContract` as a true Rift availability object or keep
    iterating the view/viewer hosting surfaces first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T14:31:44Z
  TYPE: FACT
  CLAIM: There is still some post-slice cleanup to finish before this path is
    truly clean. The current runtime still carries backward-compatible
    `FrameViewer` constructor/property aliases (`views_by_frame_name`,
    single-profile shorthands) and one of the projection test helpers became
    structurally messy while the Rift-viewer helper was inserted. Neither issue
    changes the runtime behavior, but both should be cleaned up now instead of
    leaving compatibility scaffolding and malformed test layout behind.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:89-128
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:225-241
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:40-118
  IMPACT: The assigned-view runtime is working, but the slice still carries
    avoidable compatibility clutter and one test-file layout mess.
  NEXT: remove the backward-compatible `FrameViewer` aliases and normalize the
    touched test helper file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

