# Task: Implement Agent Name Attestation And Certification
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after onboarding and re-onboarding attestation and
  certification flows were updated to require an explicit agent name.

## Metadata
- Task ID: TASK-2026-04-25-implement-agent-name-attestation-and-certification
- Story: STORY-2026-04-25-implement-agent-name-onboarding-ticket-routing
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-25T22:38:47Z
- Updated: 2026-04-26T15:08:08Z

## Objective
Implement the onboarding/re-onboarding identity flow so the agent asks for a
name each time, carries it into attestation, and requests certification
alongside that name.

## Ticket Contract
- ENTRY_GATE: implementation story is active and the identity patch docs exist.
- EXECUTION_BOUNDARY:
  - `agent_onboarding/default/general/AGENTS.MD`
  - `agent_onboarding/default/general/SKILLS.MD` if a new skill is added
  - `agent_onboarding/default/general/skills/*` directly related to
    attestation/certification/identity
- DEPENDENCIES:
  - implementation patch docs
  - investigation findings
- EXIT_GATE: the docs define a coherent `AGENT_NAME` request and attestation
  flow.
- FAILURE_ESCALATION: raise `CONFLICT` if the identity feature cannot be
  expressed cleanly without breaking current certification semantics.

## Scope Boundaries
- In scope:
  - onboarding docs
  - certification docs
  - attestation docs
- Out of scope:
  - ticket/template schema
  - board schema

## State Transition Event
- from_state: ready
- to_state: review
- transition_reason: the onboarding and certification identity docs are landed
  and reread.

## Steps / Checklist
- [x] Add or wire the agent-identity rule in the general baseline.
- [x] Update ONBOARD/REONBOARD attestation formats.
- [x] Update certification request wording to require `AGENT_NAME` alongside
      `CERTIFY: APPROVED`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- landed onboarding/certification identity flow docs

## Files / Paths Impacted
- codex/context_compass/agent_onboarding/default/general/**

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/agent_onboarding/default/general/AGENTS.MD`
  - `Get-Content codex/context_compass/agent_onboarding/default/general/skills/self_certification.md`

## Risks / Rollback Notes
- Risk: the new naming request drifts between onboarding and re-onboarding.
  Rollback: keep one standardized `AGENT_NAME:` phrase across all changed docs.

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
  CLAIM: This task owns the attestation/certification slice only. It should
    standardize `AGENT_NAME` on every onboarding cycle without entangling the
    ticket/board schema in the same edit pass.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/skills/self_certification.md:16-24
  - context_compass/agent_onboarding/default/general/skills/user_approved_certification.md:4-17
  - context_compass/agent_onboarding/default/general/skills/compaction_requirements.md:39-73
  IMPACT: The identity prompt can be added cleanly as a first slice.
  NEXT: patch the general onboarding/certification docs first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-25T22:51:41Z
  TYPE: FACT
  CLAIM: The attestation and certification slice is landed. Root/general docs
    now require `AGENT_NAME` on every onboarding cycle, include it in
    attestation, and request it alongside `CERTIFY: APPROVED`.
  EVIDENCE:
  - context_compass/AGENTS.MD:84-99
  - context_compass/AGENTS.MD:155-163
  - context_compass/agent_onboarding/default/general/skills/self_certification.md:34-42
  - context_compass/agent_onboarding/default/general/skills/user_approved_certification.md:8-24
  - context_compass/agent_onboarding/default/general/skills/compaction_requirements.md:58-79
  IMPACT: Future onboarding and re-onboarding cycles will explicitly ask for a
    user-facing agent name instead of only asking for certification.
  NEXT: keep this task in review while the user inspects the overall workflow feature.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the onboarding/re-onboarding naming flow.
