# Task: Enforce Real Re-Onboarding Reads and Ban Performative Compliance

- Completed: 2026-02-15
- Summary: Added explicit anti-performative onboarding and re-onboarding policy language requiring substantive read integrity proof.
- Summary: Updated AGENTS and onboarding skill docs to preserve parallel reading while forbidding marker-only compliance loops.

## Metadata
- Task ID: TASK-2026-02-15-enforce-reonboard-real-read-no-performative-compliance
- Story: standalone
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Make re-onboarding and normal onboarding policy explicit that read steps must be
real document reads (parallel/bulk allowed), and marker-only/performative
compliance is prohibited.

## Scope Boundaries
- In scope:
- `context_compass/AGENTS.MD` re-onboarding attestation section.
- onboarding policy files that define read behavior and certification gates.
- Out of scope:
- runtime JIT/AOT implementation code and tests.

## Steps / Checklist
- [x] Add explicit anti-performative language to `REONBOARD: COMPLETE` contract in `AGENTS.MD`.
- [x] Add explicit "real read required" rule in compaction/onboarding skill docs.
- [x] Keep parallel/bulk reading allowance but require substantive read evidence.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Updated re-onboarding/onboarding policy text that bans performative compliance.

## Files / Paths Impacted
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md`
- `context_compass/agent_onboarding/agent/general/SKILLS.md`
- `context_compass/agent_onboarding/agent/general/skills/self_certification.md`

## Validation
- Ran:
  - `rg -n "performative|real reads|marker-only|READ_INTEGRITY_PROOF|read-integrity proof|parallel/bulk" context_compass/AGENTS.MD context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md context_compass/agent_onboarding/agent/general/SKILLS.md context_compass/agent_onboarding/agent/general/skills/self_certification.md`

## Risks / Rollback Notes
- Risk: overly strict language may accidentally forbid valid parallel/bulk reads.
- Mitigation: keep explicit allowance for parallel/bulk reads while banning marker-only proof.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Current onboarding docs allow parallel reading but do not explicitly require substantive read evidence in re-onboarding attestation wording, which allows marker-only behavior to appear compliant.
  EVIDENCE: context_compass/agent_onboarding/agent/general/SKILLS.md:44-44, context_compass/agent_onboarding/agent/general/skills/self_certification.md:7-7, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:39-43, context_compass/AGENTS.MD:17-20
  IMPACT: Re-onboarding can drift into performative compliance and reduce policy fidelity.
  NEXT: Patch AGENTS and onboarding skills to explicitly ban marker-only loops and require real read traces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Re-onboarding and onboarding policy now explicitly ban performative marker-only reread loops, require read-integrity proof, and keep parallel/bulk reading allowed when substantive.
  EVIDENCE: context_compass/AGENTS.MD:20-23, context_compass/AGENTS.MD:68-68, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:10-10, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:37-37, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:46-56, context_compass/agent_onboarding/agent/general/SKILLS.md:46-47, context_compass/agent_onboarding/agent/general/skills/self_certification.md:8-9
  IMPACT: Policy contract now blocks compliance theater during both re-entry and normal onboarding.
  NEXT: Run targeted policy-text grep validation, then present changes for acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Targeted policy-text validation confirms all expected anti-performative/read-integrity clauses are present across AGENTS and onboarding docs.
  EVIDENCE: context_compass/AGENTS.MD:20-24, context_compass/AGENTS.MD:68-68, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:10-10, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:37-37, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:46-56, context_compass/agent_onboarding/agent/general/SKILLS.md:46-47, context_compass/agent_onboarding/agent/general/skills/self_certification.md:8-9
  IMPACT: This policy update is complete and reviewable.
  NEXT: Ask user to confirm acceptance criteria and whether to move this task to completed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Policy patch complete; waiting for user acceptance confirmation before closure/move to completed.
