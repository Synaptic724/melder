# Task: Harden MRP Policy Definition

## Metadata
- Task ID: TASK-2026-04-02-harden-mrp-policy-definition
- Story: none
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-02T22:17:03Z
- Updated: 2026-04-05T17:50:09Z

## Objective
Update the MRP policy skill so it reflects the stricter intent the user
described: build as if there is no patch, no second chance, and no acceptable
MVP compromise.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a stronger MRP definition and gave
  the Super Mario World example as the framing.
- EXECUTION_BOUNDARY: update the MRP skill definition only.
- DEPENDENCIES:
  - codex/context_compass/agent_onboarding/default/general/skills/mrp_policy.md
- EXIT_GATE: the MRP skill explicitly encodes the no-MVP, no-second-chance,
  build-it-right framing and is reread once after writing.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if the wording would force
  broader product-policy changes outside the skill itself.

## Scope Boundaries
- In scope:
  - `agent_onboarding/default/general/skills/mrp_policy.md`
  - stronger MRP definition
  - Super Mario World analogy
- Out of scope:
  - broad policy rewrites
  - mission or psychology docs
  - runtime code edits

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the MRP skill text has been updated directly to the
  stronger no-patch/no-second-chance framing and reread once.

## Steps / Checklist
- [x] Route this policy-doc slice on the attention board.
- [x] Update `agent_onboarding/default/general/skills/mrp_policy.md`.
- [x] Re-read the updated skill.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- updated `codex/context_compass/agent_onboarding/default/general/skills/mrp_policy.md`

## Files / Paths Impacted
- codex/context_compass/agent_onboarding/default/general/skills/mrp_policy.md
- codex/context_compass/tickets/tasks/2026-04-02_harden_mrp_policy_definition_task.md
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `Get-Content codex/context_compass/agent_onboarding/default/general/skills/mrp_policy.md`

## Risks / Rollback Notes
- Risk: the policy becomes vague rhetoric instead of an actionable product
  strategy rule.
  Rollback: keep the definition concrete around system quality, no-patch
  posture, and no-MVP discipline.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-02T22:17:03Z
  TYPE: FACT
  CLAIM: The current MRP skill was too soft for the actual repo standard. It
    described the smallest coherent trustworthy system, but it did not encode
    the stronger intent the user just clarified: build as if there is no patch,
    no second chance, and no acceptable MVP fallback. The Super Mario World
    example is the right analogy because it captures "ship it right or do not
    ship it" without turning MRP into vague perfectionism.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/general/skills/mrp_policy.md:1-19
  - user_instruction: "there is no MVP, we're building Super Mario World"
  - user_instruction: "there is no way to patch this thing"
  IMPACT: The skill needed a harder product-quality definition so future design
    and implementation choices do not drift back toward MVP thinking.
  NEXT: keep the stronger MRP framing unless the user wants the wording even
    harsher.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to harden the MRP policy definition so it matches the repo's
actual no-MVP, build-it-right posture.
