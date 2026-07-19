# Task: Wire FrameLink And FrameView To Compiled ACL Contract
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-wire-frame-link-and-frame-view-to-compiled-acl-contract
- Story: STORY-2026-04-06-frame-acl-compiled-access-surface
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T03:05:00Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Wire the compiled ACL/frame-link contract into the actual frame-surface
objects so `FrameView` can be built from descriptor truth plus compiled ACL
output instead of leaving `FrameLinkContract` as a standalone foundation.

## Ticket Contract
- ENTRY_GATE: the compiled ACL access surface and downstream contract-profile
  foundation are landed, and the user explicitly redirected back to the
  FrameLink contract wiring lane.
- EXECUTION_BOUNDARY: `FrameLink`, `FrameView`, and the smallest required
  `FrameLinkContract` support only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_implement_frame_acl_compiled_access_surface.md
  - src/melder/aether/nexus/acl/frame_acl_compiler.py
  - src/melder/aether/nexus/rift/frame_link/frame_link.py
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py
- EXIT_GATE: the frame-surface layer can build view-safe `FrameLink` objects
  from descriptor truth plus compiled ACL output, and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if clean wiring requires the
  full Nexus-side canonical holding-zone implementation first.

## Scope Boundaries
- In scope:
  - `FrameLink` contract consumption
  - `FrameView` construction from descriptor truth plus compiled ACL output
  - smallest supporting `FrameLinkContract` helper changes
  - focused tests
- Out of scope:
  - full Nexus holding-zone implementation
  - `FrameViewer` strategy/query implementation
  - event/update stream model

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Define the smallest clean bridge from compiled ACL output into
      `FrameLink` / `FrameView`.
- [x] Implement the wiring changes.
- [x] Add/update focused tests.
- [x] Run focused validation.
- [x] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- wired `FrameLink` / `FrameView` contract bridge
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_link/
- src/melder/aether/nexus/rift/frame_viewer/
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_frame_link_runtime_contracts.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py`

## Risks / Rollback Notes
- Risk: forcing `FrameLink` to own too much canonical state would recreate the
  missing Nexus holding zone inside the view layer.
  Rollback: keep the wiring view-safe and derived only.

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
  - system_docs/patches/active/frame_link_contract_wiring/architecture_patch.md
  - system_docs/patches/active/frame_link_contract_wiring/component_patch_frame_link.md
  - system_docs/patches/active/frame_link_contract_wiring/component_patch_frame_view.md
  - system_docs/patches/active/frame_link_contract_wiring/code_description_patch_frame_link_contract_wiring.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T03:05:00Z
  TYPE: FACT
  CLAIM: The compiled ACL contract foundation is landed, but the actual
    frame-surface objects still do not consume it. `FrameLinkContract` can be
    built from compiled ACL output, but `FrameLink`, `FrameView`, and
    `FrameViewer` remain placeholders with no bridge from descriptor truth plus
    compiled access output into view-safe links.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link.py:1-170
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:1-141
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-158
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-203
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:1-270
  IMPACT: The next clean slice is to wire the compiled contract into the
    frame-surface objects instead of leaving it as a detached foundation.
  NEXT: create the patch docs for a bounded `FrameLink` / `FrameView` bridge,
    then implement that bridge.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T03:08:00Z
  TYPE: PLAN
  CLAIM: The patch-doc consumption mapping for this wiring slice is now
    explicit. `architecture_patch.md` maps to keeping the bridge derived-only
    and not recreating the missing Nexus holding zone. `component_patch_frame_link.md`
    maps to adding the smallest contract-aware `FrameLink` construction path.
    `component_patch_frame_view.md` maps to adding a `FrameView` construction
    path from descriptor truth plus compiled ACL output. The
    `code_description_patch_frame_link_contract_wiring.md` doc maps to the
    descriptor -> compiled contract -> link/view translation flow and its
    fail-fast behavior.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/frame_link_contract_wiring/architecture_patch.md:1-24
  - codex/context_compass/system_docs/patches/active/frame_link_contract_wiring/component_patch_frame_link.md:1-13
  - codex/context_compass/system_docs/patches/active/frame_link_contract_wiring/component_patch_frame_view.md:1-16
  - codex/context_compass/system_docs/patches/active/frame_link_contract_wiring/code_description_patch_frame_link_contract_wiring.md:1-14
  IMPACT: The code cut can stay bounded to the actual contract bridge without
    drifting into full frame-surface repository work.
  NEXT: implement the new `FrameLinkContract` / `FrameLink` / `FrameView`
    bridge and add focused tests around it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T03:18:00Z
  TYPE: FACT
  CLAIM: The first actual frame-surface contract bridge is now implemented.
    `FrameLinkContract` can be cloned, `FrameLink` can now be built from one
    derived contract subject while owning a detached contract instance, and
    `FrameView` can now be built directly from `FrameDescriptor` truth plus
    `CompiledFrameACLAccessSurface` output, optionally narrowed again by a
    downstream `FrameLinkContractProfile`. The resulting view builds
    frame/conduit/spell links only for visible kinds and carries derived
    payload-section metadata instead of raw runtime objects.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-219
  - src/melder/aether/nexus/rift/frame_link/frame_link.py:1-245
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:1-350
  - tests/unit/melder/aether/test_frame_view_contract_projection.py:1-337
  IMPACT: The compiled ACL contract is no longer detached from the frame-surface
    objects. We now have a real derived bridge from descriptor truth plus ACL
    output into `FrameLink` / `FrameView`.
  NEXT: review whether the next frame-surface slice should extend this bridge
    into `FrameViewer` query helpers or stop here until the Nexus holding zone
    is implemented.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T03:18:00Z
  TYPE: MEASURE
  CLAIM: The focused frame-link contract-wiring slice is green. The widened
    unit/component/integration validation slice covering compiled ACL output,
    frame-link contracts, runtime links, projected frame views, and the
    compiler seam passed with 43 tests.
  EVIDENCE:
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_frame_link_runtime_contracts.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py
  IMPACT: The bridge is stable enough to review as a bounded slice instead of
    staying a loose placeholder direction.
  NEXT: decide whether to push the next bridge step into `FrameViewer` or pause
    until the missing Nexus holding zone is built.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to bridge the compiled ACL contract foundation into the
actual frame-surface objects.



