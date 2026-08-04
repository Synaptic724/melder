# Task: Trim FrameLinkContract To Exposure Only
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-trim-frame-link-contract-to-exposure-only
- Story: STORY-2026-04-03-frameinfolink-hld
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T05:05:00Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Trim `FrameLinkContract` back to exposure-only semantics so it represents what
the Rift may take in from descriptors, while viewer behavior stays owned by
`FrameViewer`.

## Ticket Contract
- ENTRY_GATE: the current frame-surface contract/viewer layer is landed, and
  the user explicitly clarified that `FrameLinkContract` should symbolize the
  frames/data a Rift is permitted to consume, not viewer commands.
- EXECUTION_BOUNDARY: `FrameLinkContract` semantics cleanup plus the smallest
  dependent code/test adjustments only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_finish_frame_link_contract_and_cache_frame_viewers.md
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/nexus.py
- EXIT_GATE: `FrameLinkContract` is exposure-only, viewer behavior stays in
  the viewer layer, and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if removing command semantics
  from the contract requires a bigger Rift ACL redesign in the same slice.

## Scope Boundaries
- In scope:
  - remove or neutralize command semantics from `FrameLinkContract`
  - keep exposure helpers
  - adjust Nexus/view/viewer metadata paths if needed
  - focused tests
- Out of scope:
  - full Rift-scoped ACL redesign
  - viewer profile system
  - search DSL

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Inspect current command-oriented contract usage.
- [x] Trim `FrameLinkContract` to exposure-only semantics.
- [x] Adjust dependent view/viewer/Nexus code and tests.
- [x] Run focused validation.
- [x] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- cleaned exposure-only contract semantics
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
- src/melder/aether/nexus/rift/frame_viewer/
- src/melder/aether/nexus/nexus.py
- tests/unit/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`

## Risks / Rollback Notes
- Risk: over-trimming could remove helper data that the view layer still needs.
  Rollback: keep exposure helpers and only remove viewer-behavior semantics.

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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T05:05:00Z
  TYPE: PLAN
  CLAIM: The next bounded frame-surface slice is contract-semantic cleanup.
    The user explicitly clarified that `FrameLinkContract` is for what the Rift
    is permitted to take in from descriptors for viewing, not for viewer
    commands. The first job is to inspect the current contract/viewer/Nexus
    paths for command semantics so we can remove them without breaking the
    exposure pipeline.
  EVIDENCE:
  - user_instruction: "the contract has nothign to do with anything related to commands, it represents what the rift is permitted to take in"
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-338
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:1-350
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-453
  IMPACT: The contract/viewer layer needs one semantics pass before more
    feature growth makes the confusion harder to unwind.
  NEXT: inspect every current use of `allowed_commands` and contract helpers,
    then trim the contract to exposure-only behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T05:12:00Z
  TYPE: FACT
  CLAIM: The command semantics are more isolated than they looked. Current
    `FrameLinkContract` command usage is not spread through the runtime. The
    live uses are basically:
    - contract tests
    - one `FrameView` metadata export of `allowed_commands`
    The viewer itself does not depend on contract commands for behavior. That
    means we can trim the contract back to exposure-only semantics without
    reworking the rest of the frame-surface stack in the same slice.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:296-304
  - tests/unit/melder/aether/test_frame_link_contract_profiles.py:1-584
  - tests/unit/melder/aether/test_frame_view_contract_projection.py:1-337
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:1-270
  IMPACT: The cleanup can stay bounded to contract/view metadata/tests instead
    of turning into a broader viewer redesign.
  NEXT: remove `allowed_commands` from the contract semantics and adjust the
    dependent view metadata/tests accordingly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T05:18:00Z
  TYPE: FACT
  CLAIM: After trimming the runtime contract, the remaining breakage is test
    drift only. Two frame-view projection tests were still constructing a
    `FrameLinkContract(..., allowed_commands=...)` directly or asserting
    `frame_view.metadata["allowed_commands"]`. Those assertions are stale now
    that the contract is exposure-only.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_view_contract_projection.py:171-176
  - tests/unit/melder/aether/test_frame_view_contract_projection.py:206-209
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The remaining work is test alignment, not more runtime changes.
  NEXT: patch the stale frame-view projection tests and rerun the focused
    exposure-only cleanup slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T05:28:00Z
  TYPE: FACT
  CLAIM: The downstream frame-link profile layer still carries stale codegen
    semantics that no longer fit the exposure-only contract. The whole
    `FrameLinkCodegenProfile` side and the `codegen_profile` half of
    `FrameLinkContractProfile` are now leftovers from the earlier mixed model.
    Current runtime usage no longer needs them for projection.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/profiles/frame_link_codegen_profile.py:1-82
  - src/melder/aether/nexus/rift/frame_link/profiles/frame_link_contract_profile.py:1-95
  - src/melder/aether/nexus/rift/frame_link/profiles/safe_profile.py:1-30
  - src/melder/aether/nexus/rift/frame_link/profiles/hybrid_profile.py:1-35
  - src/melder/aether/nexus/rift/frame_link/profiles/permissive_profile.py:1-39
  IMPACT: The semantic cleanup should continue through the frame-link profile
    layer so we do not leave dead codegen-profile concepts behind.
  NEXT: simplify `FrameLinkContractProfile` to view-only and remove the stale
    frame-link codegen profile layer plus its stale tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T05:32:00Z
  TYPE: FACT
  CLAIM: The stale frame-link codegen-profile half is now removed. The
    downstream frame-link profile layer is view-only again:
    - `FrameLinkContractProfile` now wraps only `FrameLinkViewProfile`
    - `FrameLinkCodegenProfile` was removed
    - the seeded `safe` / `hybrid` / `permissive` frame-link profiles now only
      describe exposure posture
    - the affected tests were realigned and the focused exposure-only slice is
      green
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/profiles/frame_link_contract_profile.py:1-84
  - deleted:src/melder/aether/nexus/rift/frame_link/profiles/frame_link_codegen_profile.py
  - src/melder/aether/nexus/rift/frame_link/profiles/safe_profile.py:1-24
  - src/melder/aether/nexus/rift/frame_link/profiles/hybrid_profile.py:1-29
  - src/melder/aether/nexus/rift/frame_link/profiles/permissive_profile.py:1-33
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The frame-link side is now much closer to the intended exposure-only
    model and no longer carries the dead codegen-profile concept.
  NEXT: continue into view/viewer profile foundations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T05:20:00Z
  TYPE: FACT
  CLAIM: `FrameLinkContract` is now aligned to the intended exposure-only
    meaning. It now carries:
    - visible kinds
    - visible frame payload fields
    - visible conduit payload sections
    - visible spell payload sections
    and no longer models viewer command semantics. `FrameView` metadata was
    adjusted accordingly, and the dependent tests were realigned to the
    cleaned contract meaning.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-272
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:1-348
  - tests/unit/melder/aether/test_frame_link_contract_profiles.py:1-544
  - tests/unit/melder/aether/test_frame_view_contract_projection.py:1-332
  IMPACT: The frame-surface stack now matches the intended semantic split much
    better:
    contract = exposure
    view = projection
    viewer = behavior
  NEXT: move into viewer/view profile foundations on top of the cleaned split.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T05:20:00Z
  TYPE: MEASURE
  CLAIM: The focused exposure-only cleanup slice is green. The cleaned
    contract/view/Nexus projection validation surface passed with 48 tests.
  EVIDENCE:
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_frame_view_contract_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  IMPACT: The semantic cleanup is stable enough to review as a bounded slice.
  NEXT: move into viewer/view profile foundations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to align `FrameLinkContract` with the intended exposure-only
meaning before more viewer features are added.



