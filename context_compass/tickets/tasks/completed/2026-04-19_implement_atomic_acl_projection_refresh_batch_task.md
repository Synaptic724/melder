# Task: Implement Atomic ACL Projection Refresh Batch
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-19-implement-atomic-acl-projection-refresh-batch
- Story: STORY-2026-04-19-implement-atomic-acl-projection-refresh-batch
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T10:55:02Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Implement one atomic ACL projection refresh path that batches multiple changed
frame names across the union of impacted `Rift`s.

## Ticket Contract
- ENTRY_GATE: the user approved the batch-refresh implementation lane and the
  epic now identifies the exact missing Nexus and Rift seams.
- EXECUTION_BOUNDARY: `Nexus`, `Rift`, focused tests, matching AR docs, and the
  required patch-doc set only.
- DEPENDENCIES:
  - system_docs/patches/active/atomic_acl_projection_refresh_barrier/architecture_patch.md
  - system_docs/patches/active/atomic_acl_projection_refresh_barrier/component_patch_nexus.md
  - system_docs/patches/active/atomic_acl_projection_refresh_barrier/component_patch_rift.md
  - system_docs/patches/active/atomic_acl_projection_refresh_barrier/code_description_patch_batch_refresh_flow.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - tests/unit/melder/aether/test_nexus.py
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py
  - tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
- EXIT_GATE: batch refresh is live, the single-frame callback delegates to the
  batch path, focused tests are green, and durable state is synced.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if timeout semantics or viewer
  state preservation require broader runtime design changes.

## Scope Boundaries
- In scope:
  - Nexus batch orchestration
  - Rift multi-frame refresh
  - focused tests for overlap and one-shot merge/rebuild behavior
  - matching AR doc updates
- Out of scope:
  - RiftGate primitive redesign
  - room/viewer redesign
  - command/codegen work

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the batch refresh implementation is landed and the
  focused validation ring is green.

## Steps / Checklist
- [x] Create the batch Nexus helper over changed frame names.
- [x] Make the single-frame Nexus callback/helper delegate to the batch path.
- [x] Extend Rift projection refresh to accept a multi-frame scope.
- [x] Preserve one-shot room merge and one-shot viewer rebuild per impacted Rift.
- [x] Add focused tests for overlapping changed-frame batches and one-shot
      refresh behavior.
- [x] Update AR docs/tickets/board state to match the landed runtime path.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further investigation.

## Deliverables
- batch Nexus refresh orchestration
- Rift multi-frame projection refresh
- focused tests
- synced AR docs/tickets

## Files / Paths Impacted
- src/melder/aether/nexus/nexus.py
- src/melder/aether/nexus/rift/rift.py
- tests/unit/melder/aether/test_nexus.py
- tests/unit/melder/aether/test_nexus_frame_surface_projection.py
- tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md
- codex/context_compass/tickets/tasks/2026-04-19_implement_atomic_acl_projection_refresh_batch_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- `python -m py_compile src/melder/aether/nexus/nexus.py src/melder/aether/nexus/rift/rift.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`
- `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`
- `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`
- Result: `127 passed`

## Risks / Rollback Notes
- Risk: partial batch refresh on timeout may leave confusing semantics.
- Risk: batch refresh may accidentally rebuild viewers more than once per Rift.
- Rollback: restore the single-frame orchestration path only if the batch path
  proves internally inconsistent.

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
  - system_docs/patches/active/atomic_acl_projection_refresh_barrier/architecture_patch.md
  - system_docs/patches/active/atomic_acl_projection_refresh_barrier/component_patch_nexus.md
  - system_docs/patches/active/atomic_acl_projection_refresh_barrier/component_patch_rift.md
  - system_docs/patches/active/atomic_acl_projection_refresh_barrier/code_description_patch_batch_refresh_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: apply artifact disposition when the task closes

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-19T10:55:02Z
  TYPE: PLAN
  CLAIM: The implementation plan is:
    1. add one Nexus batch helper over changed frame names,
    2. convert the single-frame helper and ACL callback into thin delegates,
    3. extend Rift refresh to one multi-frame scope,
    4. keep room merge/rebuild one-shot by reusing existing room methods,
    5. validate overlap and one-shot behavior in focused tests.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1797-1984
  - src/melder/aether/nexus/rift/rift.py:463-529
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:493-624
  IMPACT: The code change stays narrowly centered on the two runtime seams that
    still force single-frame refresh.
  NEXT: consume the patch docs and patch Nexus first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T11:01:58Z
  TYPE: FACT
  CLAIM: Nexus now owns one batch refresh helper over changed frame names,
    while the single-frame helper and `_on_frame_acl_changed(...)` both
    delegate into that batch path. `create_frame_projection_sets_for_rift(...)`
    now accepts a multi-frame scope for one Rift.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1797-1880
  - src/melder/aether/nexus/nexus.py:1964-2064
  IMPACT: The single-frame orchestration bottleneck is gone from the Nexus
    seam, and overlapping frame batches can now be coordinated centrally.
  NEXT: hold for review unless you want a different timeout or error policy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T11:01:58Z
  TYPE: FACT
  CLAIM: Rift now refreshes one explicit multi-frame scope in one call. It
    asks Nexus for one multi-frame projection subset, merges once into the
    room, and rebuilds the viewer once while preserving current profile
    selection state.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:463-579
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:493-624
  IMPACT: The runtime now matches the intended one-shot per-Rift batch refresh
    model instead of reopening the merge/rebuild path per frame.
  NEXT: hold for review unless you want the explicit batch path widened
    further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T11:01:58Z
  TYPE: MEASURE
  CLAIM: The focused Nexus/Rift frame-projection ring is green after the batch
    refresh implementation, including new overlap and one-shot rebuild tests.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:670-866
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:245-376
  - tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py:198-205
  - validation_result: `python -m py_compile src/melder/aether/nexus/nexus.py src/melder/aether/nexus/rift/rift.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py` -> 115 passed
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py` -> 127 passed
  IMPACT: The bounded implementation slice is stable enough to move into
    review.
  NEXT: wait for user acceptance or the next bounded follow-on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task implements the batch refresh feature behind the new epic. The room
layer is already sufficient; the work is focused on Nexus orchestration, Rift
refresh shape, and focused validation.