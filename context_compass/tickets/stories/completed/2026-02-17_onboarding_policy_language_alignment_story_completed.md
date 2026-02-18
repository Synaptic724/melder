

- Completed: 2026-02-18T00:29:25Z
- Summary: Closed after user confirmation to continue and finalize onboarding language alignment.
- Summary: Story outcomes met for `SKILLS.MD` routing, token-only certification, and ONBOARD/REONBOARD semantics.

# Story: Align Onboarding Language Across Active Policy Docs

## Metadata
- Story ID: STORY-2026-02-17-onboarding-policy-alignment
- Epic: EPIC-2026-02-17-onboarding-policy-drift-hardening
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-17T23:07:47Z
- Updated: 2026-02-18T00:29:25Z

## Problem / Opportunity
Policy docs currently encode multiple onboarding variants (outdated routing docs vs `SKILLS.MD`,
`CERTIFY: APPROVED` vs environment-qualified token, and mixed ONBOARD/REONBOARD semantics).
This causes brittle behavior after compaction.

## MRP Alignment
Make onboarding deterministic and easy: one routing anchor, one certification token,
and one concise attestation structure.

## Ticket Contract
- ENTRY_GATE: epic is active and user requested immediate policy simplification.
- EXECUTION_BOUNDARY: active onboarding and policy docs in `context_compass/`.
- DEPENDENCIES: epic + task, `context_compass/AGENTS.MD`, certification docs.
- EXIT_GATE: all target docs aligned and verified by search.
- FAILURE_ESCALATION: raise `CONFLICT` if requested simplification conflicts with core safety gates.

## Goals (Outcomes)
- Replace outdated role-map references with top-level `SKILLS.MD` routing
  references.
- Standardize certification to `CERTIFY: APPROVED` only.
- Remove environment-qualified certification and outdated non-certification
  gating language from onboarding docs.
- Distinguish first-time `ONBOARD` from `REONBOARD` after compaction/handoff.

## Non-Goals
- Editing source runtime code.
- Refactoring ticketing workflow sections unrelated to onboarding/certification.

## Scope Boundaries
- In scope:
  - `context_compass/AGENTS.MD`
  - `context_compass/README.md`
  - `context_compass/config/context_compass_config.yaml`
  - `context_compass/SKILLS.MD`
  - `context_compass/agent_onboarding/default/general/*` onboarding/certification docs
  - `context_compass/agent_onboarding/default/engineer/*` docs with onboarding token/path references
  - `context_compass/agent_onboarding/default/new/*` docs with outdated routing wording
- Out of scope:
  - historical completed ticket archive rewrites

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: user confirmed continuation and accepted closure of completed story outcomes.

## Acceptance Criteria
- No active onboarding docs reference outdated role-map docs/terms.
- Certification guidance consistently uses `CERTIFY: APPROVED`.
- No onboarding docs require environment-qualified certification tokens.
- Re-onboarding attestation is concise and role-driven.

## Risks / Mitigations
- Risk: broad replacement could alter unrelated text.
  Mitigation: verify each affected file and run explicit `rg` checks.

## Applicable Anti-Patterns
- [x] No edits without linked task-level execution evidence.
- [x] No unresolved policy contradiction left undocumented.

## Tasks
- [x] TASK-2026-02-17-onboarding-policy-skills-certify-reonboard-sweep

## Notes
- DATETIME: 2026-02-17T23:07:47Z
  TYPE: PLAN
  CLAIM: Execute one focused task to normalize routing/certification/onboarding language,
    then validate with search checks.
  EVIDENCE:
  - context_compass/AGENTS.MD:64-133
  - context_compass/agent_onboarding/default/general/policies/policy_skills.md:16-35
  - context_compass/config/context_compass_config.yaml:22-35
  IMPACT: A single coherent policy pass reduces re-onboarding failure modes.
  NEXT: Create task and apply file edits in one scoped tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T00:23:03Z
  TYPE: MEASURE
  CLAIM: Story-level routing/certification language checks passed for active
    onboarding scope after cleanup.
  EVIDENCE:
  - context_compass/tickets/epics/2026-02-17_onboarding_policy_drift_hardening_epic.md:30-61
  - context_compass/tickets/tasks/2026-02-17_onboarding_policy_skills_certify_reonboard_sweep_task.md:38-103
  - context_compass/agent_onboarding/default/general/SKILLS.MD:14-44
  IMPACT: Story outcomes are met and ready for user acceptance.
  NEXT: request user confirmation to close this story/task chain.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and transition gates.

## Context / Handoff Summary
Story opened for a single-pass onboarding language alignment sweep tied to user directives.

## Closure Note
Closed after user confirmation to continue and complete the active policy alignment chain.