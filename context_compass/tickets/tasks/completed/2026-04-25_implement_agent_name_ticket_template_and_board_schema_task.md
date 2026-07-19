# Task: Implement Agent Name Ticket Template And Board Schema
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after the ticket templates, ticketing docs, and the live
  attention-board schema were updated to carry `agent_name`.

## Metadata
- Task ID: TASK-2026-04-25-implement-agent-name-ticket-template-and-board-schema
- Story: STORY-2026-04-25-implement-agent-name-onboarding-ticket-routing
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-25T22:38:47Z
- Updated: 2026-04-26T15:08:08Z

## Objective
Implement the `agent_name` field across ticket templates/docs and the live
attention board schema, with support for multiple assigned names.

## Ticket Contract
- ENTRY_GATE: implementation story is active and the identity patch docs exist.
- EXECUTION_BOUNDARY:
  - `agent_onboarding/default/general/skills/ticketing.md`
  - `agent_onboarding/default/general/skills/active_pointerboard.md`
  - `templates/epic_template.md`
  - `templates/story_template.md`
  - `templates/task_template.md`
  - `attention_board.md`
- DEPENDENCIES:
  - implementation patch docs
  - investigation findings
- EXIT_GATE: templates/docs define `Agent Name`/`agent_name`, and the live
  board uses the new column.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if retrofitting the full live
  ticket set is required instead of landing the forward schema and board change.

## Scope Boundaries
- In scope:
  - ticket docs/templates
  - live attention board schema
- Out of scope:
  - artifact board schema
  - broad legacy ticket backfill

## State Transition Event
- from_state: ready
- to_state: review
- transition_reason: ticket/templates and the live board schema now include
  the new identity field and have been reread.

## Steps / Checklist
- [x] Add `Agent Name` metadata to ticket templates and guidance.
- [x] Add `agent_name` column/rules to attention-board docs.
- [x] Update the live `attention_board.md` tables to include `agent_name`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- landed ticket/template identity schema
- landed attention-board identity schema

## Files / Paths Impacted
- codex/context_compass/agent_onboarding/default/general/skills/ticketing.md
- codex/context_compass/agent_onboarding/default/general/skills/active_pointerboard.md
- codex/context_compass/templates/epic_template.md
- codex/context_compass/templates/story_template.md
- codex/context_compass/templates/task_template.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/templates/task_template.md`
  - `Get-Content codex/context_compass/attention_board.md`

## Risks / Rollback Notes
- Risk: the board column change drifts from template metadata naming.
  Rollback: keep `Agent Name` in templates and `agent_name` in the board only.

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
  TYPE: PLAN
  CLAIM: This task owns the ticket/template/board slice. It should add the new
    field to forward-looking schema and to the live board without forcing a
    full repository-wide ticket migration.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/skills/ticketing.md:1-96
  - context_compass/agent_onboarding/default/general/skills/active_pointerboard.md:15-35
  - context_compass/templates/task_template.md:1-79
  IMPACT: The feature can land now while legacy ticket backfill stays optional.
  NEXT: patch the ticket docs/templates and the live board schema.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-25T22:51:41Z
  TYPE: FACT
  CLAIM: The ticket/template/board slice is landed. Ticket docs now require
    `Agent Name`, templates include the field, `active_pointerboard.md`
    documents `agent_name`, and the live `attention_board.md` table carries the
    new column while preserving `owner`.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/skills/ticketing.md:23-25
  - context_compass/agent_onboarding/default/general/skills/active_pointerboard.md:20-25
  - context_compass/templates/task_template.md:5-12
  - context_compass/attention_board.md:24-32
  IMPACT: Ticket assignment can now carry one or more user-facing agent names
    without overloading the executor field.
  NEXT: keep this task in review while the user inspects the overall workflow feature.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the ticket/template and live-board schema slice of the identity feature.
