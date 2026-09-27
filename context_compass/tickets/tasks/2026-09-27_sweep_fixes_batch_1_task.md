# Task: Fix sweep findings batch 1 (doc-scope only)

## Metadata
- Task ID: TASK-2026-09-27-sweep-fixes-batch-1
- Epic: EPIC-2026-09-27-defect-hunting
- Status: in_progress
- Owner: user
- Agent Name: muse_0
- Priority: p2
- Created: 2026-09-27T16:07:16Z
- Updated: 2026-09-27T16:07:16Z

## Objective
Repair the eight logged sweep findings in `src_components.md` with
source-verified prose and corrected evidence ranges, then regenerate the
index in the same pass.

## Ticket Contract
- ENTRY_GATE: owner directed doc updates; defect_hunting epic routed.
- EXECUTION_BOUNDARY: edits confined to `src_components.md` stale blocks
  identified in findings 1-8 plus its index regen. No `src/` changes, no
  architecture-doc changes unless a duplicate claim is confirmed by fresh
  slice, no C1 remeasure beyond cited-range corrections.
- DEPENDENCIES: TASK-2026-09-27-spellbook-sweep (findings evidence).
- EXIT_GATE: each finding resolved or explicitly deferred with reason;
  index `--check` clean; preservation compare shows additions/corrections
  only.
- FAILURE_ESCALATION: BLOCKER if a fresh slice contradicts the finding or
  the index refuses; DECISION_REQUEST for any scope beyond findings 1-8.

## Scope Boundaries
- In scope:
  - Finding 1 qualifier (after confirming notch/add/remove call sites).
  - Findings 2-8 prose and range corrections.
- Out of scope:
  - Source changes, C1 full remeasure, architecture-doc edits without
    fresh-slice confirmation.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner-approved fix lane opens on the eight logged
  findings with re-verification required before each edit.

## Steps / Checklist
- [ ] Re-verify components index and re-slice each target block fresh.
- [ ] Confirm finding 1 call sites before qualifying.
- [ ] Apply findings 2-8 corrections with design-skill gates.
- [ ] Regenerate index same pass; run preservation and portability checks.
- [ ] Record each repair below before the next one.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Corrected component blocks with verified ranges; clean index check.

## Files / Paths Impacted
- context_compass/system_docs/src_components.md
- context_compass/system_docs/src_components_index.md

## Validation
- Not run.
- Recommended commands:
  - python context_compass/tools/system_documents/index_document.py --doc
    context_compass/system_docs/src_components.md --check

## Risks / Rollback Notes
- Risk: docs moved since the hunt (other agents active); mitigated by
  re-slicing every target fresh instead of reusing offsets.
- Rollback: git checkout of system_docs if a patch mislands.

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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: on ticket close

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - sweep fix repairs
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-27T16:07:16Z
  TYPE: PLAN
  CLAIM: Fix lane opened on findings 1-8 with fresh-slice-before-edit rule.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-09-27_spellbook_sweep_task.md:94-200
  IMPACT: Repairs stay scoped to logged findings; drift since the hunt is
    caught by re-slicing instead of assumed offsets.
  NEXT: Confirm finding 1 call sites, then re-slice finding 2 block.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-27T16:20:00Z
  TYPE: FACT
  CLAIM: Findings 1-2 repaired with fresh slices; spellbook.py evidence
    ranges re-verified still landing before editing.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:451-466
  - context_compass/system_docs/src_components.md:596-606
  IMPACT: Plane attribution and entry-vs-start contradictions resolved at
    the prose level; index regen deferred to batch end per same-pass rule.
  NEXT: Re-verify finding 3 source ranges against moved code, then repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-27T16:35:00Z
  TYPE: FACT
  CLAIM: Finding 5 repaired and self-verified line by line: eager MR in
    both places, two owned roots added, cleanup prose rewritten to match
    the actual try/except/finally shape.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:1057-1082
  - context_compass/system_docs/src_components.md:1105-1115
  - src/melder/aether/aether.py:312-337
  IMPACT: Caught my own loose "finally-adjacent" wording and the missed
    second lazy in the folded narrative before they stood; both corrected
    against fresh reads.
  NEXT: Repair findings 6-8 with the same verify-first discipline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-27T16:50:00Z
  TYPE: FACT
  CLAIM: Findings 6-8 repaired from full method reads; index regenerated
    same pass with all 147 ranges validated.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:1250-1262
  - context_compass/system_docs/src_components.md:1453-1480
  - context_compass/system_docs/src_components.md:2652-2659
  IMPACT: Batch complete at doc level. Concurrent peer authorship detected
    (+8 sections, +1,233 lines from other lanes); my edits applied only on
    exact-match blocks with post-edit re-reads, so no peer prose clobbered.
  NEXT: Owner reviews the batch diff; preservation delta beyond my 8 blocks
    belongs to peer lanes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-27T18:55:00Z
  TYPE: FACT
  CLAIM: Top-down/bottom-up coherence verified: arch boot already tells the
    eager story with mediator in order, and the one duplicate bare-mediator
    claim in arch is now qualified; arch carries no bind-return or
    freeze-emission duplicates.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:550-560
  - context_compass/system_docs/src_architecture.md:422-426
  - src/melder/aether/conduit/conduit.py:5141-5157
  IMPACT: Every fix now reads consistently from source method up through
    component prose to architecture narrative; arch index regenerated with
    56 ranges validated.
  NEXT: Await owner review of the full batch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Fix lane opened per owner direction. Next: finding-1 call-site confirmation,
then fresh slices and repairs in finding order.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
