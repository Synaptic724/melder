# Task: Sync Primary Architecture Docs From codex_agent_2
- Completed: 2026-04-22T11:14:18Z
- Summary: Closed during the 2026-04-22 rebaseline after the primary architecture docs were synced and the stale Nexus-object references were corrected.

## Metadata
- Task ID: TASK-2026-04-21-sync-primary-architecture-docs-from-codex-agent-2
- Story: none
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-21T11:37:25Z
- Updated: 2026-04-22T11:14:18Z

## Objective
Compare the primary `codex/context_compass` copies of `src_architecture.md`
and `src_components.md` against the `codex_agent_2/context_compass` copies,
then merge any newer Nexus/AR/runtime documentation from `agent_2` into the
primary docs without regressing the frame-link/API updates that just landed in
the primary source of truth.

## Ticket Contract
- ENTRY_GATE: the primary docs are the source of truth and the user explicitly
  requested a bounded diff/merge against `codex_agent_2`.
- EXECUTION_BOUNDARY: `src_architecture.md`, `src_components.md`, this task,
  and the routing board only; no code changes, no graph regeneration, no
  secondary-context rewrites.
- DEPENDENCIES:
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
  - codex_agent_2/context_compass/system_docs/src_architecture.md
  - codex_agent_2/context_compass/system_docs/src_components.md
- EXIT_GATE: the primary docs contain the newer Nexus/AR details that belong
  there, recent frame-link changes remain intact, and the merged deltas are
  summarized with evidence.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if `agent_2` contains
  contradictory older AR/Nexus language that cannot be merged safely without
  reopening source verification.

## Scope Boundaries
- In scope:
  - doc diffing between primary and `agent_2`
  - Nexus / Rift / frame viewer / frame manager / AR runtime wording
  - merging newer doc details into the primary docs
- Out of scope:
  - source-code changes
  - graph file updates
  - ticket/document cleanup outside this lane
  - copying `agent_2` docs wholesale

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the doc comparison is complete, the primary docs were
  already ahead on the live frame-link/API seam, and the remaining stale
  Nexus-object references in the primary copy have been corrected.

## Steps / Checklist
- [ ] Diff the primary and `agent_2` architecture/components docs.
- [ ] Read the differing Nexus/AR sections in bounded chunks.
- [ ] Merge only the newer compatible content into the primary docs.
- [ ] Preserve the recent `create_frame_link(frame_name)` and Nexus-managed
      frame-link authorization changes in the primary docs.
- [ ] Validate the merged docs for coherence and summarize the delta.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Updated primary `src_architecture.md`
- Updated primary `src_components.md`
- Evidence-backed merge summary

## Files / Paths Impacted
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md
- codex/context_compass/tickets/tasks/2026-04-21_sync_primary_architecture_docs_from_codex_agent_2_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `git diff -- codex/context_compass/system_docs/src_architecture.md`
  - `git diff -- codex/context_compass/system_docs/src_components.md`

## Risks / Rollback Notes
- Risk: copying stale `agent_2` language back into the primary docs would
  regress the current AR/Nexus contract.
  Rollback: keep the merge evidence-backed and primary-source-biased, using
  `agent_2` only as a delta source.

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
- DATETIME: 2026-04-21T11:37:25Z
  TYPE: PLAN
  CLAIM: This lane is a bounded doc-sync pass only. The primary
    `codex/context_compass` docs remain authoritative, and `codex_agent_2` is
    only a comparison source for newer Nexus/AR wording that may not have been
    merged back yet.
  EVIDENCE:
  - user_instruction: "the primary is codex/context_compass just fyi"
  - user_instruction: "what I want is just to insure we have the most up to date architecture document"
  IMPACT: The pass must be evidence-driven and selective instead of a
    wholesale overwrite from `agent_2`.
  NEXT: diff the four docs and identify the Nexus/AR-relevant deltas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T11:37:25Z
  TYPE: FACT
  CLAIM: The direct diff shows `codex_agent_2` is older on the live
    Rift/Nexus seam. Its copies still describe `Rift.target_frame(...)`,
    pre-Nexus-managed frame-link authorization behavior, and the deleted
    `NexusFrameRecord` model, while the primary docs already contain the newer
    `create_frame_link(frame_name)` contract.
  EVIDENCE:
  - codex/context_compass/system_docs/src_architecture.md:400-404
  - codex_agent_2/context_compass/system_docs/src_architecture.md:400-402
  - codex/context_compass/system_docs/src_components.md:578-587
  - codex_agent_2/context_compass/system_docs/src_components.md:578-583
  - codex/context_compass/system_docs/src_components.md:2064-2071
  - codex_agent_2/context_compass/system_docs/src_components.md:2064-2068
  IMPACT: There was no newer Nexus/AR behavior to pull from `agent_2`; the
    merge had to stay primary-biased.
  NEXT: patch the stale primary Nexus-object references that still mention
    `NexusFrameRecord` and old Nexus-owned state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T11:37:25Z
  TYPE: FACT
  CLAIM: The only worthwhile doc edits were stale primary references to the
    deleted `NexusFrameRecord` path and the removed
    `_next_indexed_nexus_frame_number` state. Those are now updated to the live
    `NexusFrameManager` / `_frame_manager` model in both primary docs.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:26-105
  - src/melder/aether/nexus/nexus.py:205-205
  - src/melder/aether/nexus/nexus.py:425-433
  - src/melder/aether/nexus/nexus_frame_manager.py:22-77
  - codex/context_compass/system_docs/src_architecture.md:458-466
  - codex/context_compass/system_docs/src_architecture.md:1031-1037
  - codex/context_compass/system_docs/src_components.md:541-545
  - codex/context_compass/system_docs/src_components.md:1892-1905
  IMPACT: The primary docs now match the current Nexus object model instead of
    mixing the new frame-link contract with deleted Nexus-frame-record language.
  NEXT: review the merged docs and decide whether you want a wider AR/Nexus doc
    audit beyond this bounded sync lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task compares the primary architecture/components docs against the
`codex_agent_2` copies and merges only the newer compatible Nexus/AR content
back into the primary docs. The diff proved `agent_2` was older on the live
Rift/Nexus seams, so the only primary-doc edits were stale Nexus-object
reference fixes.
