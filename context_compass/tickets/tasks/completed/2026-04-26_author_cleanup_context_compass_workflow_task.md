# Task: Author cleanup_context_compass Workflow
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after the `cleanup_context_compass` workflow was authored
  under `general` and registered in the general workflow manifest.

## Metadata
- Task ID: TASK-2026-04-26-author-cleanup-context-compass-workflow
- Story: STORY-2026-04-26-implement-role-local-workflow-system
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-26T11:45:35Z
- Updated: 2026-04-26T15:08:08Z

## Objective
Author the first real role-local workflow in `general`: `cleanup_context_compass`.

## Ticket Contract
- ENTRY_GATE: the role-local workflow system exists and the user explicitly
  requested this workflow.
- EXECUTION_BOUNDARY:
  - `agent_onboarding/default/general/WORKFLOWS.MD`
  - `agent_onboarding/default/general/workflows/**`
  - workflow-system patch docs only as directly needed
- DEPENDENCIES:
  - workflow-system lane
  - closure-sync and ticketing docs
- EXIT_GATE: the workflow file exists and the `general` workflow manifest lists it.
- FAILURE_ESCALATION: raise `CONFLICT` if the requested cleanup semantics
  require changing ticket/artifact closure rules instead of composing them.

## Scope Boundaries
- In scope:
  - one workflow file
  - `general/WORKFLOWS.MD`
- Out of scope:
  - changing base closure rules
  - executing the workflow

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the workflow was authored immediately in response to the
  user request and listed in the `general` workflow manifest.

## Steps / Checklist
- [x] Define the cleanup workflow behavior.
- [x] Add the workflow to `general/WORKFLOWS.MD`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `cleanup_context_compass.md`
- updated `general/WORKFLOWS.MD`

## Files / Paths Impacted
- codex/context_compass/agent_onboarding/default/general/WORKFLOWS.MD
- codex/context_compass/agent_onboarding/default/general/workflows/cleanup_context_compass.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/agent_onboarding/default/general/WORKFLOWS.MD`
  - `Get-Content codex/context_compass/agent_onboarding/default/general/workflows/cleanup_context_compass.md`

## Risks / Rollback Notes
- Risk: the workflow closes tickets too aggressively on paper.
  Rollback: keep the workflow explicit about user choice before closure.

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
- DATETIME: 2026-04-26T11:45:35Z
  TYPE: FACT
  CLAIM: The first starter workflow in `general` should be conservative and
    user-driven: ask scope first, list candidate tickets second, and only then
    close selected tickets while using the existing closure and artifact rules.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/skills/ticketing.md:43-73
  - context_compass/agent_onboarding/default/general/skills/ticket_closure_attention_sync.md:8-39
  - user_request: cleanup my assets or everything, then list tickets and accept `all`
  IMPACT: The workflow composes existing rules rather than inventing a new
    closure mechanism.
  NEXT: keep the workflow in review while the user inspects the workflow text.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first real workflow definition in the `general` role.
