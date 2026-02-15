# Task: Create Active-Partner and Performance-Engineer Social Contract Document

## Metadata
- Task ID: TASK-2026-02-14-social-contract-active-partner-performance-engineering-document
- Story: STORY-2026-02-14-jit-aot-split-discovery-and-viability
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Create a first-class social contract document that defines active-partner behavior,
performance-engineering mindset, decision/conflict protocol, and durable role
boundaries between architect and lead engineer, including robust note/attention
`TYPE` semantics.

## Scope Boundaries
- In scope:
- Add one large social-contract document under onboarding skills.
- Add policy references from core onboarding and routing documents.
- Expand `TYPE` schema for architect/lead-engineer decisioning and conflict contexts.
- Out of scope:
- Changing code runtime behavior.

## Steps / Checklist
- [ ] Create social contract document with mission-first and performance-first expectations.
- [ ] Include requested "American soldier vs Soviet soldier" framing verbatim.
- [ ] Include explicit architect/lead engineer responsibility contract.
- [ ] Add references from `AGENTS.MD`, general `SKILLS.md`, and policy docs.
- [ ] Expand `TYPE` schema and sync all templates/policy docs.
- [ ] Add robust per-type semantics for all base and new types.
- [ ] Verify links and summarize outcomes for user review.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md`
- Updated references in onboarding/policy docs.

## Files / Paths Impacted
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/agent/general/SKILLS.md`
- `context_compass/agent_onboarding/agent/general/skills/agent_stance.md`
- `context_compass/agent_onboarding/agent/general/policies/policy_router.md`
- `context_compass/SKILLS.MD`
- `context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "SOCIAL_CONTRACT|American soldier|Soviet soldier" context_compass`
  - `rg -n "social contract|active partner|performance engineer" context_compass/AGENTS.MD context_compass/agent_onboarding/agent/general/SKILLS.md context_compass/agent_onboarding/agent/general/policies/policy_router.md`

## Risks / Rollback Notes
- Risk: policy duplication drifts across files.
- Mitigation: keep one primary document and point other files to it.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: User requested a large, authoritative social-contract document (roughly 500 LOC) that formalizes active-partner and performance-engineering behavior and becomes a high-priority reference for agent conduct.
  EVIDENCE: context_compass/AGENTS.MD:37-44, context_compass/AGENTS.MD:51-51, context_compass/agent_onboarding/agent/general/skills/agent_stance.md:4-16
  IMPACT: Work is documentation-architecture and policy wiring, not runtime implementation.
  NEXT: Create the primary social-contract document and then wire references from policy/onboarding anchors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Canonical collaboration contract was created as a dedicated directory artifact and includes explicit mission model language, role contract, conflict/strategy protocols, and deep `TYPE` semantics.
  EVIDENCE: context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:1-609, context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:62-73, context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:92-118, context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:354-427
  IMPACT: Collaboration policy is now centralized in one durable source instead of scattered policy fragments.
  NEXT: Complete policy reference wiring and consistency checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Core onboarding and policy docs now point to the social contract, including AGENTS onboarding/engagement gates, general read order, compaction re-entry, policy-router flow, and note-type semantic references.
  EVIDENCE: context_compass/AGENTS.MD:11-11, context_compass/AGENTS.MD:40-40, context_compass/AGENTS.MD:63-63, context_compass/agent_onboarding/agent/general/SKILLS.md:40-40, context_compass/agent_onboarding/agent/general/SKILLS.md:52-52, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:28-28, context_compass/agent_onboarding/agent/general/policies/policy_router.md:25-26, context_compass/agent_onboarding/agent/general/skills/ticketing.md:66-67, context_compass/agent_onboarding/agent/general/skills/reactive_documentation.md:55-56, context_compass/agent_onboarding/agent/general/skills/active_documentation.md:35-36
  IMPACT: Social-contract behavior now has explicit policy entrypoints across startup, routing, and note semantics.
  NEXT: Request user review and decide whether to split this contract into additional focused sub-docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Added an explicit, binding "Agent Role Declaration" section to remove ambiguity: user is Architect, agent is Lead Engineer, with non-optional duty to raise technical conflicts and prohibition on neutral tool-only posture.
  EVIDENCE: context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:92-113
  IMPACT: Role semantics are now explicit and enforceable instead of implied.
  NEXT: Confirm with user whether they want additional authority/escalation clauses under this declaration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Architect-role wording was normalized from ambiguous second-person phrasing to explicit role language (`the user is the Architect`) across role, accountability, escalation, oath, and final-directive sections.
  EVIDENCE: context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:13-13, context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:116-122, context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:153-155, context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:313-313, context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:702-703, context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:767-768
  IMPACT: Role semantics are clearer for onboarding and reduce interpretation drift in future sessions.
  NEXT: Continue any remaining wording normalization only if the user requests further style constraints.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Remaining second-person architect phrasing (`you`/`your`) was removed from operational lines and replaced with explicit Architect-role language.
  EVIDENCE: context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:40-40, context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:112-112, context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:313-313, context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:350-350, context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:701-702, context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:767-767
  IMPACT: Architect comments are now consistently explicit and reduce role ambiguity during re-onboarding.
  NEXT: Hold for user review of phrasing preferences before further wording passes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: By user direction, `TYPE` schema was expanded for decisioning/conflict strategy with new values (`DECISION_REQUEST`, `STRATEGY_DISCUSSION`, `ASSUMPTION_CHALLENGE`, `CONFLICT`, `TRADEOFF`, `BLOCKER`, `ALIGNMENT_CHECK`, `RAISE`) and robust per-type semantics were defined.
  EVIDENCE: context_compass/agent_onboarding/agent/general/social_contract/SOCIAL_CONTRACT.md:544-713, context_compass/agent_onboarding/agent/general/skills/reactive_documentation.md:28-43, context_compass/agent_onboarding/agent/general/skills/reactive_documentation.md:57-65, context_compass/WORKFLOW.md:123-133, context_compass/templates/epic_template.md:73-80, context_compass/templates/story_template.md:55-63, context_compass/templates/task_template.md:48-56
  IMPACT: Notes and attention entries now support explicit architect-facing escalation and strategy workflows without overloading generic types.
  NEXT: Confirm user accepts the expanded schema as canonical and begin using new types in active notes where applicable.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task activated to create and integrate the social contract document as a first-class
execution policy reference.
