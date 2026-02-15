# Task: Policy Update - Ticket Before Repo-Sprawl Reads

## Metadata
- Task ID: TASK-2026-02-15-policy-ticket-before-repo-sprawl-reads
- Story: n/a (cross-cutting policy maintenance)
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Update repository policy docs to require ticket creation before broad repository
read sweeps that can trigger compaction risk.

## Scope Boundaries
- In scope:
- Policy and skill documentation updates only.
- Out of scope:
- Feature implementation in `src/`.

## Steps / Checklist
- [ ] Add explicit rule in `context_compass/AGENTS.MD` under ticketing/execution gates.
- [ ] Add matching rule in ticketing/active documentation skills.
- [ ] Add concise guidance in execution contract hygiene section.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Policy updates in onboarding/rule files requiring ticket-first before large read passes.

## Files / Paths Impacted
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/agent/general/skills/ticketing.md`
- `context_compass/agent_onboarding/agent/general/skills/active_documentation.md`
- `context_compass/EXECUTION_CONTRACT.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "ticket|sprawl|read|compaction" context_compass/AGENTS.MD context_compass/agent_onboarding/agent/general/skills/ticketing.md context_compass/agent_onboarding/agent/general/skills/active_documentation.md context_compass/EXECUTION_CONTRACT.md`

## Risks / Rollback Notes
- Risk: rule duplication conflicts across docs.
- Mitigation: keep wording aligned and explicit on precedence.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: User requested policy reinforcement that tickets must be created before broad repository read sprawl to reduce compaction-loss risk.
  EVIDENCE: context_compass/AGENTS.MD:374-404, context_compass/agent_onboarding/agent/general/skills/ticketing.md:31-53
  IMPACT: This becomes a cross-cutting process update, separate from JIT/AOT feature work.
  NEXT: Execute this policy task after current JIT/AOT discovery gate is complete.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Policy maintenance task queued per user direction; not active while JIT/AOT
discovery gate is in progress.
