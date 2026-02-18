

- Completed: 2026-02-18T00:29:25Z
- Summary: Closed after user confirmation to continue and finalize onboarding policy unification.
- Summary: Epic goals met for `SKILLS.MD` routing, token-only certification, and forward-only ONBOARD/REONBOARD language.

# Epic: Unify Onboarding Policy And Re-Onboarding Semantics

## Metadata
- Epic ID: EPIC-2026-02-17-onboarding-policy-drift-hardening
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-17T23:07:47Z
- Updated: 2026-02-18T00:29:25Z
- Target Window: 2026-Q1
- Related Program/Initiative: Context Compass Onboarding Reliability

## Problem / Opportunity
Onboarding and re-onboarding policy language diverged across `AGENTS.MD`, certification skills,
and routing docs. The drift causes inconsistent attestations and ambiguous certification behavior
after compaction/handoff.

## MRP Alignment (Most Reasonable Product)
Deliver one simple, deterministic onboarding contract with minimal tokens and no environment split.
This reduces policy interpretation overhead and prevents repeated onboarding failures.

## Ticket Contract
- ENTRY_GATE: user explicitly requested onboarding policy unification and simplification.
- EXECUTION_BOUNDARY: onboarding/policy docs and related routing references under `context_compass/`.
- DEPENDENCIES: `context_compass/AGENTS.MD`, certification skills, and role-routing docs.
- EXIT_GATE: docs align on `SKILLS.MD` routing, `CERTIFY: APPROVED`, ONBOARD vs REONBOARD semantics,
  and simplified attestation format.
- FAILURE_ESCALATION: raise `CONFLICT` if requested simplification conflicts with authoritative policy.

## Goals (Outcomes)
- Replace outdated role-map guidance with top-level `SKILLS.MD` guidance.
- Standardize certification token to `CERTIFY: APPROVED` only.
- Remove environment-qualified and outdated non-certification gating language
  from onboarding/certification docs.
- Separate `ONBOARD` (first-time certification) from `REONBOARD` (post-compaction/handoff only).
- Simplify attestation to role-skill listing.

## Non-Goals (Explicit Exclusions)
- Runtime code changes outside documentation.
- Runtime behavior changes under `src/`.

## Scope Boundaries
- In scope:
  - `context_compass/AGENTS.MD`
  - `context_compass/config/context_compass_config.yaml`
  - `context_compass/SKILLS.MD`
  - `context_compass/README.md`
  - onboarding policy docs under `context_compass/agent_onboarding/default/`
- Out of scope:
  - source/runtime behavior under `src/`
  - test architecture behavior changes

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: user confirmed continuation and accepted closure of epic outcomes.

## Success Metrics
- Zero conflicting certification token guidance in active onboarding docs.
- Zero active onboarding docs requiring environment labels for certification.
- Zero active onboarding docs instructing outdated role-map routing.
- Re-onboarding attestation reduced to concise role-skill declaration.

## Requirements (Functional + Non-Functional)
- Keep policy language explicit and deterministic.
- Preserve UNKNOWN/evidence discipline and ticket workflow requirements.
- Keep edits reviewable and scoped to onboarding policy domain.

## Dependencies / External References
- `context_compass/AGENTS.MD`
- `context_compass/config/context_compass_config.yaml`
- `context_compass/SKILLS.MD`
- `context_compass/agent_onboarding/default/general/skills/compaction_requirements.md`

## Milestones (Track Progress)
- [x] Milestone 1: Create epic/story/task and route active work.
- [x] Milestone 2: Apply policy sweep and verify search-based consistency.

## Stories (Required to Complete)
- [x] Story: STORY-2026-02-17-onboarding-policy-alignment - normalize routing/certification/attestation language.
- [x] Story: STORY-2026-02-18-certification-token-only - lock certification to `CERTIFY: APPROVED` with no environment qualifiers.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: TASK-2026-02-17-onboarding-policy-skills-certify-reonboard-sweep
- [x] Task: Verify policy consistency via repository-wide searches.

## Acceptance Criteria (Epic Done)
- All active onboarding docs use `SKILLS.MD` routing language.
- Certification language is `CERTIFY: APPROVED` without environment qualifiers.
- Re-onboarding template uses role-skill listing and is distinct from first-time onboarding.

## Risks / Mitigations
- Risk: broad text replacement could introduce semantic regressions.
  Mitigation: run targeted verification searches after edits.

## Applicable Anti-Patterns
- [x] No policy claim without source evidence.
- [x] No closure while required story/task is incomplete.
- [x] No hidden scope expansion beyond onboarding-policy domain.

## Validation / Test Approach
- `rg` verification over onboarding docs for token/path consistency.

## Rollout / Adoption Plan
- Merge as one coherent documentation sweep.
- Use new simplified ONBOARD/REONBOARD tokens in subsequent sessions.

## Decision Log
- Pending.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: epic closure

## Notes
- DATETIME: 2026-02-17T23:07:47Z
  TYPE: FACT
  CLAIM: Root onboarding/certification docs currently conflict on routing path, token shape,
    and environment gating semantics.
  EVIDENCE:
  - context_compass/AGENTS.MD:64-133
  - context_compass/agent_onboarding/default/general/skills/compaction_requirements.md:46-71
  - context_compass/agent_onboarding/default/general/policies/policy_skills.md:16-35
  IMPACT: Compaction recovery and certification can drift between sessions.
  NEXT: Create linked story/task and apply one-pass policy normalization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T00:23:03Z
  TYPE: MEASURE
  CLAIM: Active onboarding policy alignment stories are in review with
    consistency checks passing for token-only certification and role-map routing.
  EVIDENCE:
  - context_compass/tickets/stories/2026-02-17_onboarding_policy_language_alignment_story.md:1-99
  - context_compass/tickets/stories/2026-02-18_certification_token_only_story.md:1-108
  - context_compass/tickets/tasks/2026-02-17_onboarding_policy_skills_certify_reonboard_sweep_task.md:1-103
  IMPACT: Epic execution is complete for the current sweep and awaiting user
    closure confirmation.
  NEXT: request user acceptance and close routed tickets on approval.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Epic opened to unify onboarding/re-onboarding semantics and remove routing/certification drift.

## Closure Note
Closed after user confirmation to continue and finalize the onboarding-policy sweep.








