# Task: Sync Nexus Rift Architecture Docs To Live Model
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-19-sync-nexus-rift-architecture-docs-to-live-model
- Story:
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T00:31:00Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Rewrite the main AR architecture/component sections so
`src_architecture.md` and `src_components.md` describe the live
`Nexus -> Rift -> RiftSpace` ownership and refresh model instead of the older
partial story.

## Ticket Contract
- ENTRY_GATE: the comparison task proved the docs still under-describe the
  live Nexus/Rift/room ownership chain and the user explicitly approved the
  broader doc sync pass.
- EXECUTION_BOUNDARY: documentation only across:
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - active ticket/board state
- DEPENDENCIES:
  - tickets/tasks/2026-04-19_compare_architecture_docs_against_live_nexus_rift_task.md
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
- EXIT_GATE: the main AR ownership and refresh sections now match the live
  code, the focused ring is still green, and the board/task state is synced.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the doc sync requires a
  broader architecture rewrite outside the bounded AR ownership lane.

## Scope Boundaries
- In scope:
  - AR ownership sections
  - AR component sections
  - AR refresh flow sections
  - code-map references that are directly wrong for the live room model
- Out of scope:
  - runtime code changes
  - unrelated lower-runtime docs
  - full-repo doc sweep

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the broader AR doc sync is implemented and the focused
  AR/Nexus viewer ring is still green.

## Steps / Checklist
- [x] Rewrite the `Nexus and Rift Responsibilities` section in
      `src_architecture.md`.
- [x] Update the AR code-map references in `src_architecture.md`.
- [x] Rewrite the `AR Runtime Surface` section in `src_components.md`.
- [x] Rewrite the AR refresh-flow and AR room/component subsections in
      `src_components.md`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- synced AR ownership narrative in `src_architecture.md`
- synced AR component/flow narrative in `src_components.md`

## Files / Paths Impacted
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md
- codex/context_compass/tickets/tasks/2026-04-19_sync_nexus_rift_architecture_docs_to_live_model_task.md
- codex/context_compass/attention_board.md

## Validation
- `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py`
- Result: `198 passed`

## Risks / Rollback Notes
- Risk: the docs may still have older historical statements outside the bounded
  AR ownership sections.
- Rollback: revert the touched documentation sections only.

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
- DATETIME: 2026-04-19T09:51:36Z
  TYPE: FACT
  CLAIM: The broader AR documentation sync is landed. The main AR ownership
    sections now describe the live story:
    `Nexus` compiles projections and fans out ACL refresh,
    `Rift` owns frame contracts and per-Rift refresh orchestration,
    `RiftSpace` owns installed projections and viewer rebuild, and the
    config-backed refresh barrier is now part of that main narrative.
  EVIDENCE:
  - codex/context_compass/system_docs/src_architecture.md:436-520
  - codex/context_compass/system_docs/src_architecture.md:983-998
  - codex/context_compass/system_docs/src_architecture.md:1154-1165
  - codex/context_compass/system_docs/src_components.md:500-600
  - codex/context_compass/system_docs/src_components.md:1901-2040
  IMPACT: The docs now tell the live AR ownership chain instead of a partial
    historical version.
  NEXT: hold for review unless you want a wider non-AR documentation sweep.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T09:51:36Z
  TYPE: MEASURE
  CLAIM: The focused AR/Nexus viewer ring stayed green after the broader doc
    sync.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py` -> 198 passed
  IMPACT: This confirms the sync stayed documentation-only from a runtime
    behavior perspective.
  NEXT: wait for user acceptance or the next bounded follow-on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-19T00:31:00Z
  TYPE: PLAN
  CLAIM: This pass is broader than the tiny wording cleanup. It needs to
    rewrite the main AR ownership and refresh-flow sections so the docs tell
    the live story:
    `Nexus` compiles projections and fans out ACL refresh,
    `Rift` owns frame contracts and refresh orchestration,
    `RiftSpace` owns installed projections and viewer rebuild.
  EVIDENCE:
  - tickets/tasks/2026-04-19_compare_architecture_docs_against_live_nexus_rift_task.md:1-106
  - src/melder/aether/nexus/nexus.py:1797-1984
  - src/melder/aether/nexus/rift/rift.py:348-547
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:373-680
  IMPACT: This should replace the partial/historical AR doc story with the
    current runtime contract.
  NEXT: patch the main ownership sections in `src_architecture.md` first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task is the broader AR documentation sync pass after the comparison lane.
It is now implemented and waiting on review.