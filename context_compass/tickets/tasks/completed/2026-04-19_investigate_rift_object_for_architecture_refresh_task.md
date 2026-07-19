# Task: Investigate Rift Object For Architecture Refresh
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-19-investigate-rift-object-for-architecture-refresh
- Story:
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T11:02:52Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Read the full live `Rift` object, record the object-level ownership and
behavior contract, and update the `Rift` sections in
`src_architecture.md` / `src_components.md` only where the source proves drift.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a deeper object-first
  `Nexus`/`Rift` investigation and this task follows the `Nexus` task in the
  same epic.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/rift.py`
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - this task file
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - tickets/epics/2026-04-19_investigate_nexus_and_rift_objects_for_architecture_refresh_epic.md
  - tickets/tasks/2026-04-19_compare_architecture_docs_against_live_nexus_rift_task.md
  - tickets/tasks/2026-04-19_sync_nexus_rift_architecture_docs_to_live_model_task.md
  - src/melder/aether/nexus/rift/rift.py
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
- EXIT_GATE: the full `Rift` object has been read, key findings are appended
  with evidence, and the relevant `Rift` doc sections are updated or explicit
  UNKNOWNs remain recorded.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if `rift.py` alone is
  insufficient and the task must widen into space/gate/frame-link helpers.

## Scope Boundaries
- In scope:
  - `Rift` lifecycle and cleanup
  - configuration/gate/frame-contract ownership
  - target-frame attachment and projection-refresh seams
  - primary-space creation contract
  - `Rift` sections in the architecture/component docs
- Out of scope:
  - runtime code changes
  - deep helper/space investigation unless proven necessary
  - `Nexus` object investigation

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the full `Rift` object was read, the object-level drift
  was recorded, and the relevant `Rift` doc sections were patched.

## Steps / Checklist
- [x] Read the full `Rift` object in ordered chunks.
- [x] Record lifecycle, gate, frame-contract, and space findings in `## Notes`.
- [x] Compare those findings against the current `Rift` sections in
      `src_architecture.md`.
- [x] Compare those findings against the current `Rift` sections in
      `src_components.md`.
- [x] Patch only the `Rift` sections that the source proves are stale.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed `Rift` object findings
- refreshed `Rift` sections in `src_architecture.md` and `src_components.md`
  if drift is proven

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift.py
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md
- codex/context_compass/tickets/tasks/2026-04-19_investigate_rift_object_for_architecture_refresh_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py`

## Risks / Rollback Notes
- Risk: `Rift` may depend on room/gate/frame-link helpers that are not fully
  explained by `rift.py` alone.
- Rollback: investigation/doc-only lane; revert only the touched ticket/doc
  lines if needed.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No helper/gate/space scope expansion without explicit evidence that
      `rift.py` is insufficient.

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
- Note focus: tactical `Rift` findings, concrete doc impacts, and one-step
  continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-19T11:09:19Z
  TYPE: FACT
  CLAIM: The bounded `Rift` pass is complete. The full object confirms the live
    local-state, cleanup, and refresh contract, and the docs are now patched to
    reflect the owned registration/active flags, the teardown of the config
    snapshot / `RiftGate` / frame-link contracts, and the preservation of
    viewer-selection/default-view state across refresh-triggered rebuilds.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:27-745
  - codex/context_compass/system_docs/src_architecture.md:466-480
  - codex/context_compass/system_docs/src_architecture.md:822-824
  - codex/context_compass/system_docs/src_components.md:512-552
  - codex/context_compass/system_docs/src_components.md:1931-1935
  - codex/context_compass/system_docs/src_components.md:2032-2040
  IMPACT: The object-level AR doc pass now covers both `Nexus` and `Rift`
    without needing a wider helper/room deep dive in this lane.
  NEXT: hold the `Rift` task in review unless you want one more narrow
    object-level follow-on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T11:09:19Z
  TYPE: FACT
  CLAIM: The current `Rift` docs are close but still understate the object's
    own state and lifecycle. They omit the local registration/active flags, do
    not say that cleanup tears down the owned config snapshot, `RiftGate`, and
    frame-link contracts, and they do not describe that the refresh path
    preserves current viewer-selection/default-view state across the rebuild.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:88-91
  - src/melder/aether/nexus/rift/rift.py:163-165
  - src/melder/aether/nexus/rift/rift.py:237-246
  - src/melder/aether/nexus/rift/rift.py:502-524
  - src/melder/aether/nexus/rift/rift.py:638-685
  - codex/context_compass/system_docs/src_architecture.md:474-478
  - codex/context_compass/system_docs/src_architecture.md:822-824
  - codex/context_compass/system_docs/src_components.md:514-548
  - codex/context_compass/system_docs/src_components.md:1932-1933
  IMPACT: The next `Rift` doc edit should stay narrow and object-focused:
    fix owned-state, cleanup, and refresh-orchestration wording rather than
    reopening the whole AR section.
  NEXT: patch the `Rift` bullets in `src_architecture.md` and
    `src_components.md`, then reread those sections for object-level drift.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T11:09:19Z
  TYPE: FACT
  CLAIM: The active worktree is shared. The user confirmed another agent just
    landed the ACL refresh follow-on that uses `RiftGate` to pause impacted
    Rifts during batch projection refresh, so this `Rift` pass must treat that
    behavior as live concurrent context and avoid reasoning from older
    single-frame assumptions.
  EVIDENCE:
  - codex/context_compass/attention_board.md:30-30
  - codex/context_compass/tickets/tasks/2026-04-19_implement_atomic_acl_projection_refresh_batch_task.md:13-19
  - codex/context_compass/tickets/tasks/2026-04-19_implement_atomic_acl_projection_refresh_batch_task.md:56-58
  IMPACT: The `Rift` doc comparison needs to preserve and accurately describe
    the current gate-backed batch refresh behavior instead of regressing to an
    older refresh story.
  NEXT: compare the live `Rift` refresh/gate sections in the source against the
    current docs with this concurrent ACL-refresh context in mind.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T11:09:19Z
  TYPE: FACT
  CLAIM: The full `Rift` object shows a thinner but still concrete ownership
    contract than the old AR summaries: `Rift` owns the per-Rift config
    snapshot, one `RiftGate`, one frame-link contract map, exactly one primary
    space, registration/active flags, and the refresh path that preserves
    viewer-selection state while replacing one changed-frame subset or the full
    assigned frame set.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:27-146
  - src/melder/aether/nexus/rift/rift.py:209-563
  - src/melder/aether/nexus/rift/rift.py:704-745
  IMPACT: The `Rift` doc pass should focus on the object's own lifecycle,
    gating, frame-contract, and refresh orchestration responsibilities rather
    than re-describing the whole room subsystem.
  NEXT: compare the current `Rift` sections in `src_architecture.md` and
    `src_components.md` against these live object seams and record the exact
    drift before editing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T11:02:52Z
  TYPE: PLAN
  CLAIM: This task should start with the live `Rift` object itself before any
    helper/space widening, because `rift.py` already carries the object-level
    lifecycle, gate, frame-contract, targeting, refresh, and primary-space
    creation seams the docs need to describe accurately.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:27-146
  - src/melder/aether/nexus/rift/rift.py:209-209
  - src/melder/aether/nexus/rift/rift.py:361-463
  - src/melder/aether/nexus/rift/rift.py:704-704
  IMPACT: The first pass can stay bounded to the object file and still support
    a real doc refresh instead of a vague AR summary.
  NEXT: start this task after the active `Nexus` task records enough evidence
    to switch focus.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
This task is the completed second object investigation. `rift.py` was read in
full, the object-level findings were recorded, and the relevant `Rift`
architecture/component lines were patched without widening into helper files.