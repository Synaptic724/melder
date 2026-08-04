

# Task: Repair truncated tails of src_architecture.md and src_components.md

## Metadata
- Task ID: TASK-2026-07-05-repair-truncated-system-doc-tails
- Story: none (standalone task)
- Status: draft
- Owner: cowork
- Agent Name: mutation_0
- Priority: p2
- Created: 2026-07-05T21:40:23Z
- Updated: 2026-07-05T21:40:23Z

## Objective
Restore the missing tail content of the two canonical system docs so both files end cleanly
and no section is cut mid-sentence or mid-token.

## Ticket Contract
- ENTRY_GATE: active `attention_board.md` row routes to this ticket; onboarding complete
  (mutation_0 certified 2026-07-05); truncation evidence recorded in `## Notes`.
- EXECUTION_BOUNDARY: `codex/context_compass/system_docs/src_architecture.md` and
  `codex/context_compass/system_docs/src_components.md` only. No source-code edits.
- DEPENDENCIES: git history of this repository (primary recovery source);
  `system_docs/readable_src_graph.json` and existing doc bodies (fallback derivation source).
- EXIT_GATE: both docs end with complete sections; recovered content verified against git
  history or explicitly marked as regenerated; user accepts the repair.
- FAILURE_ESCALATION: if git history has no intact tail and regeneration would require claims
  without evidence, record `DECISION_REQUEST` and stop rather than invent doc content.

## Scope Boundaries
- In scope:
  - Recover or regenerate the truncated tail of `src_architecture.md`
    (Context / Handoff Summary list, cut at "Documented optimization-wave runt").
  - Recover or regenerate the truncated tail of `src_components.md`
    (C1 Code Map section onward, cut at "- `s").
- Out of scope:
  - Content rewrites of intact sections; drift audits; graph regeneration;
    the mailbox path-drift finding (separate decision for the owner).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: ticket staged; awaiting owner approval of scope before implementation.

## Steps / Checklist
- [ ] Investigate: check git history for the last intact revision of both files
      (`git log --oneline -- <file>`, `git show <rev>:<file> | tail`).
- [ ] Document: record whether intact tails exist in history (FACT) or not (UNKNOWN).
- [ ] Strategy: choose restore-from-git vs regenerate-with-evidence; note DECISION.
- [ ] Implement: write the recovered/regenerated tails via file tools
      (bash-mount replicas are known to truncate; file tools only for these writes).
- [ ] Validate: full-file read-back of both tails; line counts recorded; no mid-token endings.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Repaired `system_docs/src_architecture.md` with a complete final section.
- Repaired `system_docs/src_components.md` with a complete C1 Code Map and any
  following sections restored.

## Files / Paths Impacted
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md

## Validation
- Not run.
- Recommended commands:
  - `git -C <repo> log --oneline -5 -- codex/context_compass/system_docs/src_architecture.md`
  - `tail -n 20` on both files after repair (read-only check).

## Risks / Rollback Notes
- Risk: git history may also hold the truncated version only; then regeneration risks
  unevidenced claims. Mitigation: DECISION_REQUEST before writing regenerated content.
- Rollback: both files are git-tracked; `git checkout -- <file>` restores pre-repair state.

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
- ARTIFACT_PATHS: none
- DISPOSITION: none
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-07-05T21:40:23Z
  TYPE: FACT
  CLAIM: Both canonical system docs are tail-truncated on disk; each ends mid-sentence or
    mid-token via file-tool reads (not a bash-mount replica artifact).
  EVIDENCE:
  - codex/context_compass/system_docs/src_architecture.md:1690-1691
  - codex/context_compass/system_docs/src_components.md:3354-3357
  IMPACT: Canonical C4/C3 docs are incomplete; any agent relying on the C1 Code Map tail or the
    final handoff bullets of the architecture doc is reading a cut-off record.
  NEXT: After owner approval, run the git-history check for the last intact revision of both files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Ticket staged by mutation_0 immediately after onboarding certification (2026-07-05).
Truncation evidenced; recovery plan is git-first, regenerate-only-with-evidence second.
Awaiting owner approval before any investigation/implementation tranche.
