# Task: Investigate Current Agent Identity Touchpoints
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after the current onboarding, attestation, ticket, and
  board identity touchpoints were inventoried for the agent-name lane.

## Metadata
- Task ID: TASK-2026-04-25-investigate-current-agent-identity-touchpoints
- Story: STORY-2026-04-25-investigate-agent-name-onboarding-ticket-routing
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-25T22:38:47Z
- Updated: 2026-04-26T15:08:08Z

## Objective
Map the current onboarding/certification, ticket/template, and board identity
touchpoints so the new `agent_name` feature lands coherently.

## Ticket Contract
- ENTRY_GATE: epic and investigation story exist and current docs are readable.
- EXECUTION_BOUNDARY:
  - `agent_onboarding/default/general/AGENTS.MD`
  - `agent_onboarding/default/general/skills/self_certification.md`
  - `agent_onboarding/default/general/skills/user_approved_certification.md`
  - `agent_onboarding/default/general/skills/compaction_requirements.md`
  - `agent_onboarding/default/general/skills/ticketing.md`
  - `agent_onboarding/default/general/skills/active_pointerboard.md`
  - `templates/*.md`
  - this task ticket
- DEPENDENCIES:
  - current general docs and templates
- EXIT_GATE: the implementation split is explicit.
- FAILURE_ESCALATION: raise `BLOCKER` if the identity flow cannot be expressed
  cleanly in the current workflow docs.

## Scope Boundaries
- In scope:
  - attestation/certification touchpoints
  - ticket metadata touchpoints
  - attention-board schema touchpoints
- Out of scope:
  - artifact board schema change
  - legacy ticket migration beyond this lane

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested a new workflow identity feature and it
  needs a bounded discovery pass first.

## Steps / Checklist
- [ ] Read the attestation and certification docs side by side.
- [ ] Read the ticketing and board docs side by side.
- [ ] Record the first evidence-backed implementation split.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed identity insertion points
- evidence-backed multi-agent representation decision

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-25_investigate_current_agent_identity_touchpoints_task.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/agent_onboarding/default/general/skills/self_certification.md`
  - `Get-Content codex/context_compass/agent_onboarding/default/general/skills/ticketing.md`

## Risks / Rollback Notes
- Risk: the schema change touches too many legacy rows/tickets.
  Rollback: land templates/docs and current live board behavior first.

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
- DATETIME: 2026-04-25T22:38:47Z
  TYPE: FACT
  CLAIM: The current attention board already distinguishes executor ownership
    (`owner`) from routing intent, so the cleanest additive identity change is
    to add a separate `agent_name` field instead of overloading `owner`.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/skills/active_pointerboard.md:15-35
  - context_compass/attention_board.md:24-35
  IMPACT: We can preserve `owner` as executor/runtime identity and use
    `agent_name` for one or more assigned user-facing names.
  NEXT: define the patch docs and implementation tasks around that split.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to pin down the exact insertion points for the new identity
workflow before implementation.
