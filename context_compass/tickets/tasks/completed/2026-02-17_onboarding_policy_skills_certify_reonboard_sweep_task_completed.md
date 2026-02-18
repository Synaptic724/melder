

- Completed: 2026-02-18T00:29:25Z
- Summary: Closed after user confirmation to continue and finalize onboarding policy cleanup.
- Summary: Delivered forward-only `SKILLS.MD` routing and token-only `CERTIFY: APPROVED` policy language.

# Task: Sweep Role-Map/Certification/Re-Onboarding Policy Language

## Metadata
- Task ID: TASK-2026-02-17-onboarding-policy-skills-certify-reonboard-sweep
- Parent Story: STORY-2026-02-17-onboarding-policy-alignment
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-17T23:07:47Z
- Updated: 2026-02-18T00:29:25Z

## Problem / Opportunity
Active policy docs contain conflicting onboarding/certification language that causes
compaction recovery drift.

## MRP Alignment
Deliver one deterministic onboarding surface:
- route via `SKILLS.MD`
- certify with `CERTIFY: APPROVED`
- simplify ONBOARD/REONBOARD attestation semantics

## Ticket Contract
- ENTRY_GATE: story is active and this task is the routed execution item.
- EXECUTION_BOUNDARY: only onboarding/policy docs and routing references.
- DEPENDENCIES: parent story + epic.
- EXIT_GATE: edits applied and verified with targeted `rg` consistency checks.
- FAILURE_ESCALATION: raise `CONFLICT` if doc-level requirements become mutually exclusive.

## Scope
- In scope:
  - core policy docs under `context_compass/AGENTS.MD` and `agent_onboarding/default/*`
  - top-level routing/certification references in `context_compass/README.md` and `SKILLS.MD`
  - config routing path text in `context_compass/config/context_compass_config.yaml`
- Out of scope:
  - runtime code under `src/`
  - rewriting archived completed tickets

## Steps
- [x] Create epic/story/task and route attention board.
- [x] Replace outdated routing guidance with top-level `SKILLS.MD` guidance.
- [x] Standardize certification token to `CERTIFY: APPROVED` and remove environment requirement.
- [x] Remove outdated non-certification gating references from
  onboarding/certification docs.
- [x] Separate `ONBOARD` (first certification) from `REONBOARD` (post-compaction/handoff).
- [x] Simplify re-onboarding attestation to role list (`ROLE_SKILLS_READ`).
- [x] Run consistency checks and record outcomes.

## Validation Plan
- `rg -n "\bSKILLS\.MD\b" context_compass`
- `rg -n "CERTIFY: APPROVED" context_compass/AGENTS.MD context_compass/agent_onboarding/default`
- `rg -n "REONBOARD: COMPLETE|ONBOARD: COMPLETE|ROLE_SKILLS_READ" context_compass/AGENTS.MD context_compass/agent_onboarding/default/general/skills/compaction_requirements.md`

## Notes
- DATETIME: 2026-02-17T23:07:47Z
  TYPE: FACT
  CLAIM: Drift exists now across routing, certification token shape, and re-onboarding attestation requirements.
  EVIDENCE:
  - context_compass/AGENTS.MD:64-133
  - context_compass/agent_onboarding/default/general/skills/compaction_requirements.md:46-71
  - context_compass/agent_onboarding/default/general/policies/policy_skills.md:16-35
  IMPACT: Sessions can fail or diverge after compaction due to conflicting onboarding rules.
  NEXT: Apply one-pass edits to harmonize all active policy docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T00:06:30Z
  TYPE: FACT
  CLAIM: User requested a dedicated story for removing environment-qualified
    certification wording; a focused story was added under the active epic.
  EVIDENCE:
  - context_compass/tickets/stories/2026-02-18_certification_token_only_story.md:1-93
  - context_compass/tickets/epics/2026-02-17_onboarding_policy_drift_hardening_epic.md:1-145
  - context_compass/tickets/stories/2026-02-17_onboarding_policy_language_alignment_story.md:27-33
  IMPACT: Token-only certification enforcement is explicitly tracked as a
    first-class story.
  NEXT: run consistency searches and confirm no environment-qualified token
    wording remains.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T00:20:59Z
  TYPE: FACT
  CLAIM: Outdated role-map wording and an outdated onboarding skill path were
    normalized in active policy/ticket docs.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/SKILLS.MD:14-44
  - context_compass/agent_onboarding/default/general/skills/repo_topology.md:1-21
  - context_compass/tickets/epics/2026-02-17_onboarding_policy_drift_hardening_epic.md:30-61
  - context_compass/tickets/stories/2026-02-17_onboarding_policy_language_alignment_story.md:29-60
  IMPACT: Active onboarding language now aligns with top-level `SKILLS.MD`
    routing and removes stale code-management framing.
  NEXT: run final consistency searches and close remaining checklist items.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T00:22:16Z
  TYPE: MEASURE
  CLAIM: Consistency checks report no remaining outdated role-map or
    code-management wording in
    active onboarding policy scope and no environment-qualified certification
    token forms.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/SKILLS.MD:14-44
  - context_compass/agent_onboarding/default/general/skills/repo_topology.md:1-21
  - context_compass/tickets/epics/2026-02-17_onboarding_policy_drift_hardening_epic.md:30-61
  - context_compass/tickets/stories/2026-02-17_onboarding_policy_language_alignment_story.md:29-60
  IMPACT: Task implementation criteria are satisfied and ready for user
    acceptance.
  NEXT: share results and ask user whether to close this task/story chain.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T00:24:21Z
  TYPE: FACT
  CLAIM: Remaining old `role-map`/`structured-ticket` wording in active sweep
    scope was
    removed to align with top-level `SKILLS.MD` language and forward-only
    policy wording.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-02-17_onboarding_policy_skills_certify_reonboard_sweep_task.md:1-103
  - context_compass/agent_onboarding/default/general/AGENTS.MD:80-95
  - context_compass/agent_onboarding/default/general/skills/ticketing_skill_contract.md:1-38
  - context_compass/agent_onboarding/default/general/skills/workflow.md:1-12
  IMPACT: Active policy language now consistently avoids deprecated terminology
    in the requested onboarding surface.
  NEXT: run final case-insensitive wording checks and request closure approval.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T00:26:34Z
  TYPE: FACT
  CLAIM: Forward-only cleanup removed outdated historical phrasing from the
    active onboarding documentation surface.
  EVIDENCE:
  - context_compass/README.md:43-53
  - context_compass/agent_onboarding/default/general/skills/workflow.md:11-33
  - context_compass/agent_onboarding/default/general/skills/ticketing.md:96-124
  - context_compass/agent_onboarding/default/general/skills/repo_topology.md:6-21
  IMPACT: Active policy docs now describe only the current operating model
    without historical fallback framing.
  NEXT: request user approval to close the review-ready ticket chain.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Noting Behavior
- Note focus: tactical findings, immediate impacts, and one-step continuation.

## Context / Handoff Summary
Task is active for a single-pass onboarding-policy harmonization sweep.

## Closure Note
Closed by explicit user instruction to continue and finalize the policy sweep.







