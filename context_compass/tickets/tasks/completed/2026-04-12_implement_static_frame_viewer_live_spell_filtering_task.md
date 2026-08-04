# Task: Implement Static Frame Viewer Live Spell Filtering
- Completed: 2026-04-13T11:20:06Z
- Summary: Landed and closed the static viewer live-only filtering slice after the later static-room work confirmed the final boundary.

## Metadata
- Task ID: TASK-2026-04-12-implement-static-frame-viewer-live-spell-filtering
- Story: STORY-2026-04-11-precision-acl-target-model-and-descriptor-validation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T17:05:00Z
- Updated: 2026-04-13T11:20:06Z

## Objective
Finish the static room by giving it a real static viewer surface that filters
spell-facing queries and target projection down to already-live spells while
leaving frame and conduit visibility intact.

## Ticket Contract
- ENTRY_GATE: the static command system already has live-only spell runtime
  retrieval, and the user explicitly redirected the next tranche to finishing
  static before capability.
- EXECUTION_BOUNDARY: `StaticFrameViewer`, `StaticRiftSpace` viewer
  composition, focused tests, patch docs, and board/artifact sync only.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py
  - src/melder/aether/conduit/conduit.py
  - src/melder/aether/conduit/meld/meld.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: static rooms attach a static viewer variant that exposes only
  already-live spells through spell-facing viewer surfaces and target
  projection, and the focused static/runtime ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if finishing static viewer
  semantics requires a broader descriptor or capability redesign.

## Scope Boundaries
- In scope:
  - static viewer subclass/composition
  - live-spell filtering for spell-facing viewer methods
  - live-only spell target projection in static viewer output
  - focused tests
- Out of scope:
  - conduit visibility redesign
  - capability mode
  - broader viewer API redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: static command is already mostly done; the remaining user-
  approved static gap is the viewer side.

## Steps / Checklist
- [x] Stage patch docs and route the task from the board.
- [x] Add `StaticFrameViewer` with live-spell filtering over the existing
      descriptor/runtime truth.
- [x] Compose `StaticFrameViewer` from `StaticRiftSpace`.
- [x] Update focused static viewer/runtime tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `StaticFrameViewer`
- `StaticRiftSpace` viewer composition
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
- src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py
- src/melder/aether/nexus/rift/rift_space/static_rift_space.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: static viewer filtering mutates the wrong ownership layer and creates
  drift between descriptor truth and viewer projection.
  Rollback: keep filtering entirely inside the static viewer overlay and do not
  mutate descriptor publication.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/static_frame_viewer_live_spell_filtering/architecture_patch.md
  - system_docs/patches/active/static_frame_viewer_live_spell_filtering/component_patch_static_frame_viewer.md
  - system_docs/patches/active/static_frame_viewer_live_spell_filtering/component_patch_static_rift_space.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the static viewer model is merged into canonical
  runtime docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T17:05:00Z
  TYPE: FACT
  CLAIM: Static command is mostly done, but static viewer is not. `StaticRiftSpace`
    currently only composes `StaticCommandSystem`; it does not compose a
    static viewer. `FrameViewer` still iterates `descriptor.spell_records_by_key`
    directly in spell-facing methods and the selected-profile target path still
    uses the generic compiled spell visibility. That means static rooms can
    still *see* published-but-not-live spells even though static command now
    refuses to create them.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:1-68
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1273-2060
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:2931-3047
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:3253-3319
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:1-155
  IMPACT: Static is not fully finished. The remaining slice is a static viewer
    overlay that filters spell-facing surfaces to already-live spells.
  NEXT: add a dedicated `StaticFrameViewer`, compose it from `StaticRiftSpace`,
    and update the focused static viewer/runtime tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T17:15:00Z
  TYPE: FACT
  CLAIM: The static viewer slice is now landed in source. `StaticFrameViewer`
    is a thin overlay over `FrameViewer` that refreshes a live-only spell
    projection on access, filters spell-facing viewer methods to already-live
    spells, and rebuilds selected profiles so profile-driven target lists stay
    aligned with the filtered spell surface. `StaticRiftSpace` now composes
    that viewer variant automatically when a viewer is attached.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:1-337
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:1-102
  - tests/unit/melder/aether/test_nexus.py:1940-2129
  IMPACT: Static room semantics are now complete on both sides:
    - command -> live-only spell runtime retrieval
    - viewer -> live-only spell visibility/projection
  NEXT: run the focused and nearby Rift/static validation ring, then decide
    whether static is complete enough to stop and move to capability.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T17:15:00Z
  TYPE: MEASURE
  CLAIM: The static viewer slice is green on the focused and nearby Rift
    runtime rings. The updated `test_nexus.py` surface passes with the new
    static viewer behavior, and the nearby Rift runtime-contract slice also
    passes with static viewer composition active during frame attachment.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py` -> 91 passed
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> 106 passed
  IMPACT: Static is now coherent enough to review as a completed room-mode
    slice instead of another partial boundary.
  NEXT: summarize the final static boundary and decide whether the next room
    tranche is capability.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:20:06Z
  TYPE: DECISION
  CLAIM: This static viewer slice is complete and can move to the completed
    lane. Later static-room tasks and the canonical docs now treat the static
    viewer overlay as part of the settled static boundary, and the user
    explicitly asked to clean up finished older tickets.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:1-337
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:1-102
  - codex/context_compass/system_docs/src_components.md:560-574
  IMPACT: The static viewer slice no longer needs to remain in active review
    state on the board.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task finishes the static room on the viewer side: live-only spell
filtering and static viewer composition, without reopening the command seam.
The focused and nearby Rift/static validation ring is green.
