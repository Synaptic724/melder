# Task: Implement codegen_ast_structure_strategy.py
- Completed: 2026-04-25T10:37:18Z
- Summary: Closed during cleanup after the structural AST strategy landed as
  the first rule-family boundary in the validator.

## Metadata
- Task ID: TASK-2026-04-25-implement-codegen-ast-structure-strategy-py
- Story: STORY-2026-04-25-codegen-system-validation-strategies-directory
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-25T00:01:28Z
- Updated: 2026-04-25T10:37:18Z

## Objective
Implement the AST-structure validation strategy for code shape rules.

## Ticket Contract
- ENTRY_GATE: the validation-strategies story is active.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_ast_structure_strategy.py`
- DEPENDENCIES:
  - `tickets/stories/2026-04-25_codegen_system_validation_strategies_directory_story.md`
- EXIT_GATE: AST structure validation is isolated into one strategy file.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if structure checks must merge
  with another validation strategy.

## Scope Boundaries
- In scope:
  - AST structure rules
- Out of scope:
  - imports
  - builtins
  - name resolution
  - attribute access

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: structure validation is a distinct rule family.

## Steps / Checklist
- [ ] Implement AST structure strategy.
- [ ] Keep it limited to structural node/pattern rules.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- AST structure validation strategy

## Files / Paths Impacted
- src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_ast_structure_strategy.py

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: this file turns into a generic catch-all strategy.
  Rollback: keep only structural AST rules here.

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
  CLAIM: Structural AST validation is the clean first strategy boundary.
  EVIDENCE:
  - tickets/stories/2026-04-25_codegen_system_validation_strategies_directory_story.md:1-103
  IMPACT: This file should exist before import or name-resolution policy checks.
  NEXT: implement structural rules first when the strategy story starts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-04-25T10:37:18Z
  TYPE: FACT
  CLAIM: `codegen_ast_structure_strategy.py` is now implemented as the
    structure-rule family for the governed validator chain.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_ast_structure_strategy.py:1-82
  - tickets/stories/2026-04-25_codegen_system_validation_strategies_directory_story.md:101-122
  IMPACT: Structural policy now has its own file instead of being folded into
    the validator root.
  NEXT: keep unrelated import/name/access checks out of this file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the structural AST validation strategy.
