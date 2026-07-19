# Task: Build FrameView And FrameViewer Profile Foundations
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-build-frame-view-and-frameviewer-profile-foundations
- Story: STORY-2026-04-03-frameinfolink-hld
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T05:30:00Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Build the first profile foundations for `FrameView` and `FrameViewer` so the
read-side surface has one strong generalized behavior with versioned profile
modifiers instead of ad hoc branching.

## Ticket Contract
- ENTRY_GATE: the contract/viewer split is cleaned up and the user explicitly
  agreed that profiles should modify a generalized viewer rather than invent
  entirely new paradigms.
- EXECUTION_BOUNDARY: view/viewer profile foundations only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_trim_frame_link_contract_to_exposure_only.md
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/nexus.py
- EXIT_GATE: versioned `FrameViewProfile` / `FrameViewerProfile` foundations
  exist with one seeded `general` posture and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a useful profile foundation
  requires a full command-catalog system in the same slice.

## Scope Boundaries
- In scope:
  - `FrameViewProfile`
  - `FrameViewerProfile`
  - simple builder/catalog foundations
  - one seeded `general` profile
  - light Nexus hosting hooks if needed
  - focused tests
- Out of scope:
  - full viewer command catalog
  - search DSL
  - large presentation system

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Define the minimal view/viewer profile object shapes.
- [x] Implement the profile foundations and one seeded `general` posture.
- [x] Add/update focused tests.
- [x] Run focused validation.
- [x] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- `FrameViewProfile` foundation
- `FrameViewerProfile` foundation
- one seeded `general` profile path
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_viewer/
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_frame_view_contract_projection.py`

## Risks / Rollback Notes
- Risk: profiles become a second behavior engine instead of a modifier layer.
  Rollback: keep profiles as defaults/enabled-capability modifiers over the
  shared viewer surface.

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
  - system_docs/patches/active/frame_view_and_viewer_profiles/architecture_patch.md
  - system_docs/patches/active/frame_view_and_viewer_profiles/component_patch_frame_view.md
  - system_docs/patches/active/frame_view_and_viewer_profiles/component_patch_frame_viewer.md
  - system_docs/patches/active/frame_view_and_viewer_profiles/code_description_patch_viewer_profile_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T05:30:00Z
  TYPE: PLAN
  CLAIM: The next bounded frame-surface slice is view/viewer profile
    foundations. The user explicitly agreed that profiles should not create
    brand new display systems; they should modify a strong generalized viewer.
    So the right first cut is small:
    - `FrameViewProfile`
    - `FrameViewerProfile`
    - one seeded `general` posture
    - simple builder/catalog foundations
  EVIDENCE:
  - user_instruction: "the profile system is not meant to make BRAND new ways to display things entirely"
  - user_instruction: "we make a strong generalized view and then if we want to change that or modify it we can add a new layer"
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:1-348
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-426
  IMPACT: We can start making the read-side surface configurable without
    overcommitting to a full command-catalog system yet.
  NEXT: create the patch-doc set, then define the minimal profile object shapes
    and seeded `general` path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T05:32:00Z
  TYPE: PLAN
  CLAIM: The patch-doc consumption mapping for this profile-foundation slice is
    now explicit. `architecture_patch.md` maps to keeping profiles as bounded
    modifiers over the shared viewer surface. `component_patch_frame_view.md`
    maps to the view-side profile identity/default posture. The
    `component_patch_frame_viewer.md` doc maps to viewer-side profile
    identity/default posture and the small builder/catalog path. The
    `code_description_patch_viewer_profile_flow.md` doc maps to the
    profile-resolution and attachment flow.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/frame_view_and_viewer_profiles/architecture_patch.md:1-16
  - codex/context_compass/system_docs/patches/active/frame_view_and_viewer_profiles/component_patch_frame_view.md:1-6
  - codex/context_compass/system_docs/patches/active/frame_view_and_viewer_profiles/component_patch_frame_viewer.md:1-8
  - codex/context_compass/system_docs/patches/active/frame_view_and_viewer_profiles/code_description_patch_viewer_profile_flow.md:1-9
  IMPACT: The implementation can stay focused on the first real profile
    foundations instead of drifting into a full viewer command architecture.
  NEXT: implement the minimal profile objects and the seeded `general` path,
    then add focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T05:40:00Z
  TYPE: FACT
  CLAIM: The first profile foundations for `FrameView` and `FrameViewer` are
    now implemented. The runtime now has:
    - `FrameViewProfile`
    - `FrameViewProfileBuilder`
    - `FrameViewerProfile`
    - `FrameViewerProfileBuilder`
    - one seeded `general` posture for both
    `FrameView` and `FrameViewer` can now carry applied profile identity, and
    Nexus projection now accepts `view_profile_name` / `viewer_profile_name`
    inputs so the selected posture is attached to the projected result.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_view_profile.py:1-116
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_view_profile_builder.py:1-113
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:1-130
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile_builder.py:1-113
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:1-393
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-463
  - src/melder/aether/nexus/nexus.py:1362-1631
  IMPACT: The read-side surface is now configurable through bounded profile
    modifiers instead of only ad hoc metadata.
  NEXT: review whether the next step should be a viewer command/capability
    catalog on top of these profile foundations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T05:40:00Z
  TYPE: MEASURE
  CLAIM: The focused profile-foundation slice is green. The new profile
    classes/builders plus the Nexus projection/view/viewer surface passed with
    53 tests.
  EVIDENCE:
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_frame_view_contract_projection.py
  IMPACT: The profile foundations are stable enough to review as a bounded slice.
  NEXT: decide whether to add the first viewer command/capability catalog next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T05:38:00Z
  TYPE: FACT
  CLAIM: The first focused profile-foundation run exposed one real cache-key
    bug in Nexus. After adding `view_profile_name` and `viewer_profile_name`
    into the projection cache keys, the invalidation helpers were still
    comparing only raw frame names. That leaves stale cached views/viewers
    behind on ACL changes. The fix belongs in the invalidation helpers, not in
    the tests.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1611-1698
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:225-247
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:321-343
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The profile foundation slice needs one targeted cache invalidation fix
    before it can be considered stable.
  NEXT: match invalidation against the frame-name prefix embedded in the cache
    keys, then rerun the focused projection slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to add the first profile foundations for `FrameView` and
`FrameViewer` after the contract/viewer split was cleaned up.



