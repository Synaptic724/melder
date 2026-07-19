# Task: Fix RiftSpace And AR Room Documentation Drift
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-19-fix-rift-space-and-ar-room-documentation-drift
- Story: STORY-2026-04-18-cleanup-rift-space-and-ar-room-documentation-drift
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-19T00:02:00Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Fix the current source-proven `RiftSpace` and AR room/viewer documentation drift
left behind after the room-owned viewer migration and the config-driven refresh
barrier follow-on.

## Ticket Contract
- ENTRY_GATE: user explicitly asked to fix the drifts and update the
  architecture docs.
- EXECUTION_BOUNDARY: `RiftSpace` docstrings/comments plus
  `codex/context_compass/system_docs/src_architecture.md` and
  `codex/context_compass/system_docs/src_components.md` only.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
- EXIT_GATE: the stale room-kind, viewer-ownership, and removed
  selected-target wording is corrected and the focused AR/Nexus viewer ring is
  still green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the drift proves broader than
  this bounded room/viewer slice.

## Scope Boundaries
- In scope:
  - `RiftSpace` docstring drift
  - AR room/viewer architecture/component doc drift
- Out of scope:
  - runtime behavior changes
  - large doc sweeps
  - unrelated subsystem docs

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the bounded drift cleanup is implemented and the focused
  AR/Nexus viewer ring is still green.

## Steps / Checklist
- [x] Fix stale room-kind wording in `RiftSpace`.
- [x] Fix stale room-selected-target and viewer-ownership wording in
      `src_architecture.md`.
- [x] Fix stale room/file-path wording in `src_components.md`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- updated `RiftSpace` docstrings
- updated AR architecture/component docs

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md

## Validation
- `python -m py_compile src/melder/aether/nexus/rift/rift_space/rift_space.py`
- `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py`
- Result: `198 passed`

## Risks / Rollback Notes
- Risk: bounded drift cleanup may miss unrelated historical doc drift.
- Rollback: revert the touched docstring/doc lines only.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-19T00:14:29Z
  TYPE: FACT
  CLAIM: The bounded drift cleanup is landed. `RiftSpace` now documents the
    live `capability` / `codegen` room model and room-owned projection/viewer
    ownership, and the AR docs no longer describe removed room-selected-target
    state or old `dynamic_*` room files as live.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:39-84
  - codex/context_compass/system_docs/src_architecture.md:463-505
  - codex/context_compass/system_docs/src_architecture.md:992-998
  - codex/context_compass/system_docs/src_architecture.md:1159-1165
  - codex/context_compass/system_docs/src_components.md:507-590
  - codex/context_compass/system_docs/src_components.md:711-752
  - codex/context_compass/system_docs/src_components.md:1901-1950
  - codex/context_compass/system_docs/src_components.md:2032-2036
  - codex/context_compass/system_docs/src_components.md:2362-2375
  IMPACT: The durable docs now match the live room/viewer model instead of
    describing old AR seams as if they still existed.
  NEXT: hold for review unless you want a larger AR doc sweep.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-19T00:14:29Z
  TYPE: MEASURE
  CLAIM: The focused AR/Nexus viewer ring stayed green after the bounded drift
    cleanup.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/rift_space.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py` -> 198 passed
  IMPACT: This confirms the cleanup stayed documentation-only from a runtime
    behavior perspective.
  NEXT: wait for user acceptance or the next bounded follow-on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-19T00:02:00Z
  TYPE: FACT
  CLAIM: The current drift is real and bounded. `RiftSpace` still describes
    the old `dynamic` room in its class docstring, and the AR docs still
    mention removed room-selected-target state plus old `dynamic_*` room file
    references.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:39-81
  - codex/context_compass/system_docs/src_architecture.md:463-505
  - codex/context_compass/system_docs/src_components.md:507-590
  - codex/context_compass/system_docs/src_components.md:1901-1950
  IMPACT: The runtime code is clean, but the durable docs still describe old
    AR room semantics in a few places.
  NEXT: patch those exact lines and rerun the focused ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
This task fixes the small documentation drift left behind after the viewer
ownership and refresh-barrier changes. The cleanup is implemented and waiting
on review.