# Task: Implement codegen_builtins_strategy.py

## Metadata
- Task ID: TASK-2026-04-25-implement-codegen-builtins-strategy-py
- Story: STORY-2026-04-25-codegen-system-namespace-strategies-directory
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-04-25T00:01:28Z
- Updated: 2026-04-25T00:01:28Z

## Objective
Implement the namespace strategy that exposes approved builtins.

## Ticket Contract
- ENTRY_GATE: the namespace-strategies story is active.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py`
- DEPENDENCIES:
  - `tickets/stories/2026-04-25_codegen_system_namespace_strategies_directory_story.md`
- EXIT_GATE: builtins exposure is isolated into one strategy file.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if builtins exposure needs a
  separate safe/permissive split before implementation.

## Scope Boundaries
- In scope:
  - builtins exposure only
- Out of scope:
  - validation policy
  - room objects
  - workstation

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: builtins exposure is a distinct namespace concern.

## Steps / Checklist
- [ ] Implement builtins exposure strategy.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- builtins namespace strategy

## Files / Paths Impacted
- src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: builtins exposure becomes an implicit policy layer instead of an
  explicit namespace strategy.
  Rollback: keep this file purely on the exposure side.

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
  CLAIM: Builtins exposure should stay in one explicit namespace strategy file.
  EVIDENCE:
  - tickets/stories/2026-04-25_codegen_system_namespace_strategies_directory_story.md:1-104
  IMPACT: Builtins visibility stays explicit and auditable.
  NEXT: implement it after the other namespace exposure strategies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

## Context / Handoff Summary
This task owns the builtins exposure namespace strategy.

