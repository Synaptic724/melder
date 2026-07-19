# Task: Implement Projection-Backed Rift-Owned FrameViewer Model
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-19-implement-projection-backed-rift-owned-frame-viewer-model
- Story: STORY-2026-04-19-implement-projection-backed-rift-owned-frame-viewer-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T16:01:49Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Implement the settled ownership cut so `FrameViewer` consumes projection-owned
state from `Rift` instead of duplicating descriptor/ACL/surface maps, with
viewer-profile selection driven by `RiftConfiguration`.

## Ticket Contract
- ENTRY_GATE: user explicitly approved implementation and the patch docs below
  define the bounded system-impacting contract.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/configuration/rift_configuration.py`
  - `src/melder/aether/nexus/rift/rift.py`
  - `src/melder/aether/nexus/rift/rift_space/rift_space.py`
  - `src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py`
  - `src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py`
  - `src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py`
  - `src/melder/utilities/interfaces/interfaces.py`
  - focused tests/docs/board state
- DEPENDENCIES:
  - tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/architecture_patch.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_rift_configuration.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_rift.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_rift_space.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_frame_viewer.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_static_frame_viewer.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_frame_viewer_profile.md
- EXIT_GATE: code lands, focused tests are green, and the docs/tickets/board
  reflect the implemented ownership cut.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one of the targeted files
  proves insufficient and the cut must widen further.

## Scope Boundaries
- In scope:
  - Rift viewer-profile config seam
  - Rift sync path update
  - FrameViewer state ownership cut
  - StaticFrameViewer adaptation
  - FrameViewerProfile binding change
  - tests/docs for the cut
- Out of scope:
  - command/codegen redesign
  - projection-family deduplication
  - unrelated runtime cleanup

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the ownership cut is implemented and the focused tests are
  green.

## Steps / Checklist
- [x] Add the Rift-level viewer-profile configuration seam.
- [x] Update Rift viewer sync/profile selection.
- [x] Remove viewer-owned duplicate descriptor/config/surface maps.
- [x] Adapt StaticFrameViewer to the new ownership model.
- [x] Update FrameViewerProfile binding to consume projection-owned state.
- [x] Update focused tests and docs.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- implementation of the ownership cut
- focused tests/docs updates

## Files / Paths Impacted
- src/melder/aether/nexus/configuration/rift_configuration.py
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
- src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py
- src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_rift_configuration.py
- tests/unit/melder/aether/test_frame_viewer_projection.py
- tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py
- tests/unit/melder/aether/test_rift_runtime_contracts.py
- tests/unit/melder/aether/test_static_frame_viewer.py
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md

## Validation
- `python -m pytest -q tests/unit/melder/aether/test_rift_configuration.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_static_frame_viewer.py`
- Result: `124 passed`
- `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_static_rift_space.py`
- Result: `114 passed`
- `python -m pytest -q tests/component/melder/aether`
- Result: `299 passed, 2 xfailed`
- `python -m pytest -q tests/unit/melder/aether`
- Result: `2832 passed, 1 skipped`

## Risks / Rollback Notes
- Risk: breaking static viewer filtering while removing local compiled-surface
  copies.
- Rollback: revert the bounded ownership-cut files only.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No preserving local descriptor/config/surface copies without proved need.

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
  - tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/architecture_patch.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_rift_configuration.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_rift.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_rift_space.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_frame_viewer.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_static_frame_viewer.md
  - system_docs/patches/active/projection_backed_rift_owned_frame_viewer_model/component_patch_frame_viewer_profile.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical implementation findings, patch-to-code mapping, and one
  concrete next step.
- Keep notes append-only and evidence-backed.

## Notes
- DATETIME: 2026-04-19T16:37:39Z
  TYPE: MEASURE
  CLAIM: The component Aether ring is green after finishing the remaining hard
    swap fallout. The remaining failures were not hidden runtime incompatibility
    after all; they were component harnesses still constructing the removed
    viewer snapshot API directly. Once those harnesses were moved onto real
    projection-backed viewer construction, the entire component ring passed.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/component/melder/aether` -> 299 passed, 2 xfailed
  - tests/_nexus_viewer_matrix_support.py:1-515
  - tests/component/melder/aether/test_frame_acl_compiler_component.py:1-260
  - tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py:1-220
  - tests/component/melder/aether/test_nexus_viewer_general_helper_component_matrix.py:1-260
  IMPACT: The implementation now survives both the unit and component Aether
    validation rings.
  NEXT: hold for user review unless one more broader validation ring is
    requested.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T16:37:39Z
  TYPE: MEASURE
  CLAIM: The full Aether unit suite is now green after fixing the remaining
    implementation fallout. The last real issues were:
    - a missing Nexus refresh guard when ACL changes arrived before Nexus was
      configured/enabled
    - test harnesses still trying to build or mutate the removed viewer-owned
      snapshot model instead of real projection-backed state
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether` -> 2832 passed, 1 skipped
  - src/melder/aether/nexus/nexus.py:1989-2004
  - tests/_nexus_viewer_matrix_support.py:1-463
  - tests/unit/melder/aether/test_nexus.py:200-445
  IMPACT: The broader unit suite no longer contradicts the implementation
    claim. The lane is genuinely review-ready now.
  NEXT: hold for user review unless one more bounded follow-on is requested.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T16:30:19Z
  TYPE: FACT
  CLAIM: The hard swap is landed. `FrameViewer` no longer accepts the old
    descriptor/config/surface constructor path or the old per-frame selected
    profile sync path. The viewer now consumes projection-owned state, the
    selected viewer profile comes from Rift-level config/sync, and the static
    viewer keeps only its live-only filtered overlay as local state.
  EVIDENCE:
  - src/melder/aether/nexus/configuration/rift_configuration.py:47-62
  - src/melder/aether/nexus/rift/rift.py:471-520
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:74-3568
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:14-440
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:1-540
  IMPACT: The implementation lane has moved from coding to review.
  NEXT: hold for user review unless one more bounded follow-on is requested.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T16:30:19Z
  TYPE: MEASURE
  CLAIM: The focused viewer/rift/nexus test rings are green after the hard
    swap.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_configuration.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_static_frame_viewer.py` -> 124 passed
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_static_rift_space.py` -> 114 passed
  IMPACT: The ownership cut is validation-backed, not just source-edited.
  NEXT: wait for user review or the next bounded follow-on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T16:01:49Z
  TYPE: PLAN
  CLAIM: Patch-to-code mapping for this cut:
    - `architecture_patch.md` -> overall ownership cut + test/doc sync
    - `component_patch_rift_configuration.md` -> add `viewer_profile_name`
    - `component_patch_rift.md` -> use config-driven viewer-profile selection
      during sync
    - `component_patch_rift_space.md` -> adjust viewer construction only if the
      new viewer/provider seam requires it
    - `component_patch_frame_viewer.md` -> remove viewer-owned duplicate
      descriptor/config/surface maps
    - `component_patch_static_frame_viewer.md` -> preserve static live-only
      filtering under the new ownership model
    - `component_patch_frame_viewer_profile.md` -> bind from projection-owned
      state instead of decomposed viewer-owned copies
  EVIDENCE:
  - tickets/artifacts/2026-04-19_frame_viewer_projection_asset_chain.md:1-236
  IMPACT: The implementation is now decomposed enough to execute without
    widening scope blindly.
  NEXT: create the patch docs and board route, then start the code cut with
    `RiftConfiguration`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements the settled projection-backed viewer ownership cut.