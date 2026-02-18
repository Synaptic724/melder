

- Completed: 2026-02-18T00:29:25Z
- Summary: Closed after user confirmation to continue and finalize token-only certification policy.
- Summary: Certification contract remains exact `CERTIFY: APPROVED` with no environment-qualified variants.

# Story: Lock Certification To A Single Token

## Metadata
- Story ID: STORY-2026-02-18-certification-token-only
- Epic: EPIC-2026-02-17-onboarding-policy-drift-hardening
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-18T00:06:30Z
- Updated: 2026-02-18T00:29:25Z

## Problem / Opportunity
Certification policy needs one exact token with no environment qualifiers so
re-onboarding remains deterministic after compaction/handoff.

## MRP Alignment
Use one cert phrase everywhere:
- `CERTIFY: APPROVED`

## Ticket Contract
- ENTRY_GATE: user requested token-only certification language.
- EXECUTION_BOUNDARY: onboarding/certification docs under `context_compass/`.
- DEPENDENCIES: EPIC-2026-02-17-onboarding-policy-drift-hardening and
  TASK-2026-02-17-onboarding-policy-skills-certify-reonboard-sweep.
- EXIT_GATE: no certification docs require environment-qualified tokens.
- FAILURE_ESCALATION: raise `CONFLICT` if token-only language conflicts with
  authoritative policy.

## Goals (Outcomes)
- Keep certification token fixed to `CERTIFY: APPROVED`.
- Remove environment-qualified certification wording from active policy docs.
- Verify search-based consistency across onboarding/certification docs.

## Non-Goals
- Runtime code changes.
- Rewriting archived/completed ticket history.

## Scope Boundaries
- In scope:
  - `context_compass/AGENTS.MD`
  - `context_compass/README.md`
  - `context_compass/agent_onboarding/default/general/`
  - active onboarding-policy tickets
- Out of scope:
  - `src/` runtime behavior
  - historical archive normalization unless requested

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: user confirmed continuation and accepted token-only certification closure.

## Acceptance Criteria
- Certification token guidance is `CERTIFY: APPROVED` in active onboarding docs.
- No active onboarding docs require environment-qualified certification tokens.
- Search checks pass:
  - `rg -n "CERTIFY: APPROVED \\([^)]*\\)" context_compass`

## Risks / Mitigations
- Risk: broad wording updates could alter unrelated policy context.
  Mitigation: limit edits to certification language and verify with targeted
  searches.

## Applicable Anti-Patterns
- [x] No policy claim without evidence.
- [x] No closure without validation evidence.

## Tasks
- [x] TASK-2026-02-17-onboarding-policy-skills-certify-reonboard-sweep

## Notes
- DATETIME: 2026-02-18T00:06:30Z
  TYPE: FACT
  CLAIM: Active onboarding docs already use `CERTIFY: APPROVED`; a dedicated
    story is required to lock and track token-only policy enforcement.
  EVIDENCE:
  - context_compass/AGENTS.MD:62-127
  - context_compass/agent_onboarding/default/general/skills/self_certification.md:25-30
  - context_compass/agent_onboarding/default/general/skills/user_approved_certification.md:6-10
  IMPACT: Certification language remains deterministic across re-onboarding and
    compaction recovery.
  NEXT: patch residual wording and verify by search.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T00:23:03Z
  TYPE: MEASURE
  CLAIM: Token-only certification checks passed with no environment-qualified
    variants in active onboarding/certification docs.
  EVIDENCE:
  - context_compass/AGENTS.MD:62-127
  - context_compass/agent_onboarding/default/general/skills/self_certification.md:25-30
  - context_compass/agent_onboarding/default/general/skills/user_approved_certification.md:6-10
  IMPACT: Story acceptance criteria are satisfied and ready for closure on user
    confirmation.
  NEXT: request user confirmation to close this story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and transition gates.

## Context / Handoff Summary
Story opened to enforce token-only certification language across active
onboarding policy docs.

## Closure Note
Closed after user confirmation to continue and finalize token-only certification alignment.



