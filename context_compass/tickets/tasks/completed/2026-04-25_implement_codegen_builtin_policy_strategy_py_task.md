# Task: Implement codegen_builtin_policy_strategy.py
- Completed: 2026-04-25T10:37:18Z
- Summary: Closed during cleanup after the builtin-policy strategy landed as a
  separate validator governance file.

## Metadata
- Task ID: TASK-2026-04-25-implement-codegen-builtin-policy-strategy-py
- Story: STORY-2026-04-25-codegen-system-validation-strategies-directory
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-25T00:01:28Z
- Updated: 2026-04-25T10:37:18Z

## Objective
Implement the builtins-policy validation strategy.

## Ticket Contract
- ENTRY_GATE: the validation-strategies story is active.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py`
- DEPENDENCIES:
  - `tickets/stories/2026-04-25_codegen_system_validation_strategies_directory_story.md`
- EXIT_GATE: builtins policy is isolated into one strategy file.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if builtins policy must merge
  with import or name-resolution strategies.

## Scope Boundaries
- In scope:
  - builtins policy only
- Out of scope:
  - imports
  - name resolution
  - attribute access

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: builtins policy is a separate validation concern.

## Steps / Checklist
- [ ] Implement builtins policy strategy.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- builtins policy strategy

## Files / Paths Impacted
- src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: builtins rules bleed into namespace strategy files.
  Rollback: keep them inside validation policy.

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
  CLAIM: Builtins policy is one explicit validation axis and should not be
    hidden inside import or name-resolution code.
  EVIDENCE:
  - tickets/stories/2026-04-25_codegen_system_validation_strategies_directory_story.md:1-103
  IMPACT: This file keeps builtins governance explicit.
  NEXT: implement it after import policy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-04-25T10:37:18Z
  TYPE: FACT
  CLAIM: `codegen_builtin_policy_strategy.py` is now implemented as the
    builtin-governance rule family used by the validator.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py:1-96
  - tickets/stories/2026-04-25_codegen_system_validation_strategies_directory_story.md:101-122
  IMPACT: Banned builtins are now handled explicitly without leaking into import
    or namespace policy files.
  NEXT: keep builtin exposure and builtin validation separate across namespace
    and validation subsystems.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the builtins policy validation strategy.
