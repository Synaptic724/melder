# Task: Implement FrameViewerProfile Hosted Tool Surface
- Completed: 2026-04-06T14:31:44Z
- Summary: Landed the first real profile-owned viewer tool surface, then turned the slice in once the assigned-view follow-up took over the live frame-surface chain.

## Metadata
- Task ID: TASK-2026-04-06-implement-frame-viewer-profile-hosted-tool-surface
- Story: STORY-2026-04-03-frameinfolink-hld
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T13:16:15Z
- Updated: 2026-04-06T14:31:44Z

## Objective
Make `FrameViewerProfile` the owner of the agent-exposed tool surface and thin
`FrameViewer` into the host/runtime shell that exposes selected profile-owned
tools over one or more projected `FrameView` objects.

## Ticket Contract
- ENTRY_GATE: the user explicitly confirmed that the target model is:
  `FrameView` as the projected result, `FrameViewerProfile` as the tool owner,
  `FrameViewer` as the host, and `FrameLinkContract` as frame-attachment
  state only.
- EXECUTION_BOUNDARY: viewer-profile tool ownership plus the smallest runtime
  hosting/Nexus wiring needed to honor that model.
- DEPENDENCIES:
  - codex/context_compass/tickets/tasks/2026-04-03_design_frameinfolink_hld_task.md
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile_builder.py
  - src/melder/aether/nexus/nexus.py
- EXIT_GATE: `FrameViewerProfile` owns a real tool surface, `FrameViewer`
  hosts that selected tool surface over views, and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the clean implementation
  requires full workspace/runtime exposure in the same slice.

## Scope Boundaries
- In scope:
  - viewer-profile owned tool definitions
  - `FrameViewer` hosting/runtime routing for selected profile tools
  - smallest Nexus wiring needed for the hosted profile model
  - focused unit tests
- Out of scope:
  - full workspace/runtime object exposure
  - broad search/query DSL
  - ACL ownership redesign
  - unrelated Nexus lanes

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: the hosted tool-surface slice passed focused validation and
  the next assigned-view runtime slice superseded it as the live active lane.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user approved continuing the Nexus frame-surface work
  on the viewer-profile hosted tool surface model.

## Steps / Checklist
- [ ] Inspect the current viewer/profile/runtime wiring and identify the
      smallest gap between helper gating and profile-owned tool surfaces.
- [ ] Implement the profile-owned tool surface.
- [ ] Thin `FrameViewer` into the host/runtime shell over that tool surface.
- [ ] Wire the minimum Nexus projection hooks needed.
- [ ] Add/update focused tests.
- [ ] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- profile-owned viewer tool surface
- hosted `FrameViewer` runtime shell updates
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_viewer/
- src/melder/aether/nexus/nexus.py
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: the slice drifts into a full workspace model too early.
  Rollback: keep the first cut bounded to profile-owned tool definitions plus
  host/runtime routing.

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
- DATETIME: 2026-04-06T13:16:15Z
  TYPE: PLAN
  CLAIM: The next live Nexus slice is the hosted viewer tool-surface model.
    The user explicitly confirmed the intended split: `FrameView` is the
    projected result, `FrameViewerProfile` owns the tool surface, `FrameViewer`
    hosts those selected profile tools over views, and `FrameLinkContract` is
    just attachment state. The first implementation cut should therefore turn
    the current helper-gating model into real profile-owned tool definitions
    without widening into full workspace exposure yet.
  EVIDENCE:
  - user_instruction: "we already decided what FrameLinkContract does it represents what frames the rift is connected to"
  - user_instruction: "sure yes that correct this is the goal"
  - codex/context_compass/tickets/tasks/2026-04-03_design_frameinfolink_hld_task.md:1-245
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-507
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:1-131
  IMPACT: The viewer/profile ownership model can now move from discussion into
    the next bounded implementation slice.
  NEXT: inspect the current viewer/profile/Nexus code to identify the smallest
    real gap between helper gating and a profile-owned tool surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T13:16:15Z
  TYPE: FACT
  CLAIM: The current runtime is still one step short of the intended ownership
    model. `FrameViewerProfile` only owns helper-name/default metadata, while
    `FrameViewer` still owns the concrete tool methods directly and merely gates
    them through `_require_helper_enabled(...)`. Nexus then projects those
    helper ids/defaults into the viewer instance. So the profile is still a
    gate over host-owned behavior rather than the actual owner of the exposed
    tool surface.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:27-29
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:71-85
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:256-286
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:441-524
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:556-599
  - src/melder/aether/nexus/nexus.py:1543-1570
  IMPACT: The clean next cut is to give the profile a real tool-definition
    surface and make `FrameViewer` route through that owned surface instead of
    hardcoding the tool list as host-local methods plus helper gating.
  NEXT: inspect the current tests, then implement the smallest profile-owned
    tool-definition path and update the viewer to host it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T13:16:15Z
  TYPE: FACT
  CLAIM: The first hosted-tool ownership cut is now implemented. The selected
    `FrameViewerProfile` now owns an explicit tool-id -> handler-name mapping,
    can list/resolve/clone that tool surface, and `FrameViewer` now hosts a
    profile clone and exposes `list_available_tools()` plus `execute_tool(...)`
    over that hosted surface. Nexus now passes the selected profile object into
    the viewer rather than flattening it only into helper/default metadata.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:28-29
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:81-113
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:176-253
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:579-660
  - src/melder/aether/nexus/nexus.py:1556-1568
  - tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py:177-249
  - tests/unit/melder/aether/test_frame_viewer_projection.py:127-319
  IMPACT: The viewer/profile relationship now matches the intended model much
    more closely: profile owns the tool surface, viewer hosts it, Nexus prepares
    it.
  NEXT: run the focused viewer/profile test slice and see whether any contract
    drift remains.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T13:16:15Z
  TYPE: MEASURE
  CLAIM: The focused hosted-tool slice is green after one small alias-gating
    correction. The first test run exposed exactly one real runtime mismatch:
    alias tools resolved to the correct host handler, but the host was still
    re-gating by handler name instead of the profile-owned tool map. After
    allowing helper gating to treat either an exposed tool id or an exposed
    handler target as valid, the focused viewer/profile/Nexus projection slice
    passed cleanly.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:660-677
  - tests/unit/melder/aether/test_frame_viewer_projection.py:240-319
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py
  IMPACT: The current runtime now has a real profile-owned tool surface instead
    of only helper-name gating, and the first focused regression slice is
    stable.
  NEXT: review the hosted-tool ownership slice with the user and decide whether
    the next cut should be multi-profile hosting on `FrameViewer` or direct
    workspace exposure through Nexus.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T13:16:15Z
  TYPE: FACT
  CLAIM: The next missing center of gravity is `FrameView`, not more
    `FrameViewerProfile` polish. The current frame-surface runtime still has:
    - `FrameView` as only `links_by_id` + metadata
    - no explicit `available_targets` surface on the view
    - no local `FrameViewProfileBuilder` or `active_profiles_by_name` on the view
    - `FrameViewer` still exposing `views_by_frame_name`, but not an explicit
      assigned/available-views surface
    - no explicit runtime chain that says:
      contract -> assigned frame views -> available targets -> profile-built
      viewer commands
    That means the next implementation cut should move into the view/viewer
    hosting model directly.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:68-80
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:290-325
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_view_profile_builder.py:10-97
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:75-84
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:149-190
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:18-29
  - src/melder/aether/nexus/nexus.py:1502-1574
  IMPACT: The correct next slice is to build the assigned-view and
    available-target runtime on top of the now-working profile-owned tool
    surface.
  NEXT: implement `FrameView` active targets/profile hosting and `FrameViewer`
    available-view hosting in one bounded follow-up cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
