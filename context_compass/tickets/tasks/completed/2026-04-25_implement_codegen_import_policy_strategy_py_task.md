# Task: Implement codegen_import_policy_strategy.py
- Completed: 2026-04-25T10:37:18Z
- Summary: Closed during cleanup after the import-policy strategy landed as its
  own validator rule family.

## Metadata
- Task ID: TASK-2026-04-25-implement-codegen-import-policy-strategy-py
- Story: STORY-2026-04-25-codegen-system-validation-strategies-directory
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-25T00:01:28Z
- Updated: 2026-04-25T10:37:18Z

## Objective
Implement the import-policy validation strategy.

## Ticket Contract
- ENTRY_GATE: the validation-strategies story is active.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py`
- DEPENDENCIES:
  - `tickets/stories/2026-04-25_codegen_system_validation_strategies_directory_story.md`
- EXIT_GATE: import-policy checks live in one explicit strategy file.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if import policy must be folded
  into builtins or structure strategy logic.

## Scope Boundaries
- In scope:
  - import policy only
- Out of scope:
  - structural AST rules
  - builtins
  - namespace names

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: import policy is a standalone validation concern.

## Steps / Checklist
- [ ] Implement import policy strategy.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- import policy validation strategy

## Files / Paths Impacted
- src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: import rules drift into structural validation.
  Rollback: keep import policy in its own strategy file.

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
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: PLAN
  CLAIM: Import policy should stay separate from the rest of validation because
    it is one explicit codegen governance axis.
  EVIDENCE:
  - tickets/stories/2026-04-25_codegen_system_validation_strategies_directory_story.md:1-103
  IMPACT: This file can evolve independently from structural or namespace checks.
  NEXT: stage import policy after AST structure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-04-25T10:37:18Z
  TYPE: FACT
  CLAIM: `codegen_import_policy_strategy.py` is now implemented as the import
    governance file in the validator strategy family.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py:1-78
  - tickets/stories/2026-04-25_codegen_system_validation_strategies_directory_story.md:101-122
  IMPACT: Import blocking is now explicit and separate from structural or
    builtins policy.
  NEXT: keep later allowed-import relaxations in this file rather than leaking
    them into the validator root.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the import-policy validation strategy.
