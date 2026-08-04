# Task: Implement codegen_name_resolution_strategy.py
- Completed: 2026-04-25T10:37:18Z
- Summary: Closed during cleanup after the name-resolution strategy landed and
  allowed local assignments while rejecting unknown namespace reads.

## Metadata
- Task ID: TASK-2026-04-25-implement-codegen-name-resolution-strategy-py
- Story: STORY-2026-04-25-codegen-system-validation-strategies-directory
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-25T00:01:28Z
- Updated: 2026-04-25T10:37:18Z

## Objective
Implement the name-resolution validation strategy against namespace policy.

## Ticket Contract
- ENTRY_GATE: the validation-strategies story is active.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py`
- DEPENDENCIES:
  - `tickets/stories/2026-04-25_codegen_system_validation_strategies_directory_story.md`
  - namespace configuration task
- EXIT_GATE: name-resolution validation is isolated into one strategy file.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if name-resolution rules must be
  validated somewhere other than the validation strategy family.

## Scope Boundaries
- In scope:
  - namespace name-resolution checks
- Out of scope:
  - attribute access
  - builtins exposure building

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: name resolution is one explicit validation boundary.

## Steps / Checklist
- [ ] Implement name-resolution strategy.
- [ ] Validate against namespace policy/config, not live exec side effects.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- name-resolution validation strategy

## Files / Paths Impacted
- src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: name resolution drifts into namespace-building logic.
  Rollback: keep validation on the policy side and leave object exposure to namespace strategies.

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
  CLAIM: Name resolution should validate against namespace configuration, not
    against whatever live objects happen to exist at exec time.
  EVIDENCE:
  - user_instruction: agreement on validator strategies and namespace configuration
  IMPACT: This keeps policy validation ahead of execution.
  NEXT: implement this strategy after namespace configuration exists.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-25T10:37:18Z
  TYPE: FACT
  CLAIM: `codegen_name_resolution_strategy.py` is now implemented and validates
    namespace reads against the configured exposure set while still allowing
    ordinary locally assigned names.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:1-73
  - tickets/stories/2026-04-25_codegen_system_validation_strategies_directory_story.md:101-122
  IMPACT: Name-policy validation now matches the intended agent coding
    experience instead of rejecting normal local-variable use.
  NEXT: keep live-object exposure decisions in namespace-building work and
    validation of names in this file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the namespace name-resolution validation strategy.
