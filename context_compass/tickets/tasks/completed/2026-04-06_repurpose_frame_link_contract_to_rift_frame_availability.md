# Task: Repurpose FrameLinkContract To Rift Frame Availability
- Completed: 2026-04-09T11:31:39Z
- Summary: Rewrote FrameLinkContract into Rift frame availability and removed the old per-frame contract path.


## Metadata
- Task ID: TASK-2026-04-06-repurpose-frame-link-contract-to-rift-frame-availability
- Story: STORY-2026-04-06-contract-backed-assigned-frame-views
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T14:53:43Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Repurpose `FrameLinkContract` into the Rift's frame-availability object,
remove the old per-frame exposure-contract/profile path from the frame-surface
runtime, and keep only the new canonical chain:
Rift assignment -> frame availability contract -> assigned views -> available
targets -> hosted viewer commands.

## Ticket Contract
- ENTRY_GATE: the assigned-view slice is landed and the user explicitly
  reiterated that `FrameLinkContract` represents what frames the Rift is
  connected to.
- EXECUTION_BOUNDARY: contract semantics rewrite plus cleanup of the old
  per-frame contract/profile leftovers only.
- DEPENDENCIES:
  - codex/context_compass/tickets/tasks/2026-04-06_implement_contract_backed_assigned_frame_views.md
  - src/melder/aether/nexus/rift/frame_link/
  - src/melder/aether/nexus/rift/frame_viewer/
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
- EXIT_GATE: `FrameLinkContract` is Rift frame availability, the old per-frame
  contract/profile path is removed, and the focused frame-surface tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the rewrite forces a broader
  ACL redesign in the same slice.

## Scope Boundaries
- In scope:
  - `FrameLinkContract` rewrite
  - removal of frame-link contract profiles and old per-frame contract usage
  - Rift/Nexus wiring to the new availability contract
  - focused test realignment
- Out of scope:
  - broader ACL redesign
  - codegen runtime
  - workspace UI/runtime exposure beyond this chain

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the contract rewrite is implemented, the focused cleanup
  slice passed, and the task is ready for review.

## Steps / Checklist
- [ ] Rewrite `FrameLinkContract` as Rift frame availability.
- [ ] Remove per-frame contract/profile usage from `FrameLink`, `FrameView`,
      and Nexus projection.
- [ ] Wire Rift/Nexus to the new contract semantics.
- [ ] Delete stale frame-link profile leftovers and realign tests.
- [ ] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- repurposed `FrameLinkContract`
- cleaned frame-surface runtime path
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_link/
- src/melder/aether/nexus/rift/frame_viewer/
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/nexus.py
- tests/unit/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: half-removing the old contract path leaves split-brain semantics.
  Rollback: remove the old per-frame contract/profile path in the same slice if
  the new Rift availability contract lands.

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
- DATETIME: 2026-04-06T14:53:43Z
  TYPE: PLAN
  CLAIM: The next bounded cleanup/implementation slice is the contract
    semantics rewrite. The current runtime still uses `FrameLinkContract` as a
    per-frame exposure object, but the user has now reasserted the intended
    model clearly: `FrameLinkContract` should represent what frames the Rift is
    connected to. The right next move is to rewrite that contract to the Rift
    availability role and remove the old per-frame contract/profile leftovers
    in the same slice.
  EVIDENCE:
  - user_instruction: "we already decided what FrameLinkContract does it represents what frames the rift is connected to"
  - user_instruction: "the contract should create some kind of availability for the agents in the Viewer"
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-306
  - src/melder/aether/nexus/nexus.py:1411-1738
  IMPACT: This slice should clean up one of the last major semantic leftovers in
    the Nexus frame-surface path.
  NEXT: map the remaining live uses of `FrameLinkContract` and
    `contract_profile_name`, then rewrite them against the Rift availability
    model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T14:53:43Z
  TYPE: FACT
  CLAIM: The old per-frame contract/profile path is still materially live in
    the runtime, not just in historical docs. `Nexus.create_frame_view(...)`
    still accepts `contract_profile_name`, constructs a
    `FrameLinkContractProfileBuilder`, and passes the resulting per-frame
    contract into `FrameView.from_compiled_access_surface(...)`. `FrameLink`
    still stores a `FrameLinkContract` per target, and the old contract/profile
    tests still exercise that per-frame shaping path. That means the cleanup
    has to remove real live code, not just dead test leftovers.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1411-1499
  - src/melder/aether/nexus/nexus.py:1502-1785
  - src/melder/aether/nexus/rift/frame_link/frame_link.py:23-248
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:25-306
  - tests/unit/melder/aether/test_frame_link_contract_profiles.py:1-431
  - tests/unit/melder/aether/test_frame_view_contract_projection.py:24-279
  - tests/integration/melder/aether/test_frame_acl_compiler_integration.py:11-253
  IMPACT: The correct implementation is a real semantics rewrite: repurpose the
    contract, remove the old frame-link profile path, and realign the tests to
    the new chain in the same slice.
  NEXT: rewrite `FrameLinkContract` first, then remove per-frame contract usage
    from `FrameLink`, `FrameView`, and Nexus projection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T14:53:43Z
  TYPE: FACT
  CLAIM: The rewrite is now implemented. `FrameLinkContract` is now the
    Rift-local assigned-frame availability contract, `Rift` now owns one
    contract instance, `Nexus.create_frame_viewer_for_rift(...)` and the cached
    variant now populate assigned views from `rift.frame_link_contract`, and the
    old per-frame contract path is gone from `FrameLink`, `FrameView`, and the
    Nexus projection/cache keys. The dead `frame_link/profiles/` package was
    deleted in the same slice.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-250
  - src/melder/aether/nexus/rift/frame_link/frame_link.py:1-178
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:193-328
  - src/melder/aether/nexus/rift/rift.py:5-151
  - src/melder/aether/nexus/nexus.py:1411-1479
  - src/melder/aether/nexus/nexus.py:1502-1738
  - deleted:src/melder/aether/nexus/rift/frame_link/profiles/frame_link_contract_profile.py
  - deleted:src/melder/aether/nexus/rift/frame_link/profiles/frame_link_contract_profile_builder.py
  - deleted:src/melder/aether/nexus/rift/frame_link/profiles/frame_link_view_profile.py
  IMPACT: The frame-surface runtime now has one clean contract meaning instead
    of the old split-brain semantics.
  NEXT: run the focused contract/view/viewer/compiler slice and fix any stale
    expectations that still assume the deleted path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T14:53:43Z
  TYPE: MEASURE
  CLAIM: The focused contract rewrite and cleanup slice is green. A few stale
    tests needed realignment:
    - compiler/component/integration tests that still imported the deleted
      frame-link profile package
    - viewer tests still using the old `views_by_frame_name`/single-profile
      construction path
    - one malformed Nexus projection test helper and a couple of projection
      expectations that had drifted while the helper was broken
    After realigning those tests to the new canonical chain, the focused
    frame-surface slice passed cleanly.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_link_contract_profiles.py:1-180
  - tests/unit/melder/aether/test_frame_link_runtime_contracts.py:1-76
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-900
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:1-438
  - tests/component/melder/aether/test_frame_acl_compiler_component.py:1-241
  - tests/integration/melder/aether/test_frame_acl_compiler_integration.py:1-238
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_frame_link_runtime_contracts.py tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The frame-surface runtime and its focused regression slice are now on
    the new contract model without the old per-frame contract leftovers.
  NEXT: review the new canonical chain with the user and decide whether the
    next cut should push more behavior into `FrameView` profiles or into the
    `FrameViewer` host surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

