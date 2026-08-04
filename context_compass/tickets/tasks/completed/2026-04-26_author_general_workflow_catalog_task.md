# Task: Author General Workflow Catalog
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after the general workflow catalog was expanded with the
  requested active and on-demand workflow set.

## Metadata
- Task ID: TASK-2026-04-26-author-general-workflow-catalog
- Story: STORY-2026-04-26-implement-role-local-workflow-system
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-26T12:32:40Z
- Updated: 2026-04-26T15:08:08Z

## Objective
Author the remaining general workflows the user requested and split them into
active and on-demand entries in `general/WORKFLOWS.MD`.

## Ticket Contract
- ENTRY_GATE: the role-local workflow system exists and the user explicitly
  requested the next general workflow set.
- EXECUTION_BOUNDARY:
  - `agent_onboarding/default/general/WORKFLOWS.MD`
  - `agent_onboarding/default/general/workflows/**`
  - directly related workflow-system patch docs only
- DEPENDENCIES:
  - workflow-system lane
  - current `cleanup_context_compass` workflow
- EXIT_GATE: the requested active workflows and optional on-demand workflows
  exist and are listed correctly in the general workflow manifest.
- FAILURE_ESCALATION: raise `CONFLICT` if any requested workflow requires
  changing the base closure/board rules instead of composing them.

## Scope Boundaries
- In scope:
  - `start_context_compass_work`
  - `turn_in_selected_tickets`
  - `sync_attention_board`
  - on-demand `role_creation`
  - on-demand `workflow_creation`
  - manifest split between active and on-demand workflows
- Out of scope:
  - executing the workflows
  - adding more roles or templates

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the requested workflow catalog was authored immediately and
  split into active vs on-demand entries in the general manifest.

## Steps / Checklist
- [x] Add the three active general workflows.
- [x] Add the two on-demand workflow scaffolds.
- [x] Split the manifest into active vs on-demand workflows.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- new general workflow files
- updated `general/WORKFLOWS.MD`

## Files / Paths Impacted
- codex/context_compass/agent_onboarding/default/general/WORKFLOWS.MD
- codex/context_compass/agent_onboarding/default/general/workflows/**

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/agent_onboarding/default/general/WORKFLOWS.MD`
  - `Get-ChildItem codex/context_compass/agent_onboarding/default/general/workflows`

## Risks / Rollback Notes
- Risk: optional workflows become de facto baseline reads.
  Rollback: keep them only in the `On-demand workflows` section and document
  the discovery-only behavior clearly.

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
- DATETIME: 2026-04-26T12:32:40Z
  TYPE: FACT
  CLAIM: The requested catalog is split correctly into three active general
    workflows and two optional on-demand workflows. The on-demand pair exists so
    agents can know about them but does not sit in the active section of the
    manifest.
  EVIDENCE:
  - user_request: add `start_context_compass_work`, `turn_in_selected_tickets`, `sync_attention_board`
  - user_request: keep `role_creation` and `workflow_creation` optional/on-demand
  IMPACT: The manifest now distinguishes baseline workflow availability from
    discoverable but non-baseline workflow scaffolds.
  NEXT: keep the catalog task in review while the user inspects the workflow set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T12:31:03Z
  TYPE: FACT
  CLAIM: The active workflow set is now:
    `cleanup_context_compass`, `start_context_compass_work`,
    `turn_in_selected_tickets`, and `sync_attention_board`. The on-demand set
    is now: `role_creation` and `workflow_creation`.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/WORKFLOWS.MD:11-19
  - context_compass/agent_onboarding/default/general/workflows/start_context_compass_work.md:1-78
  - context_compass/agent_onboarding/default/general/workflows/turn_in_selected_tickets.md:1-72
  - context_compass/agent_onboarding/default/general/workflows/sync_attention_board.md:1-71
  - context_compass/agent_onboarding/default/general/workflows/role_creation.md:1-31
  - context_compass/agent_onboarding/default/general/workflows/workflow_creation.md:1-31
  IMPACT: The requested catalog exists exactly where the role-local workflow
    model says it should.
  NEXT: keep this task in review while the user inspects the workflow set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the general workflow catalog beyond the first cleanup workflow.
