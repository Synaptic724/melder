# Story: Investigate Agent Name Onboarding Ticket Routing
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after the current identity touchpoints and routing gaps
  were mapped into the implementation plan for agent-name support.

## Metadata
- Story ID: STORY-2026-04-25-investigate-agent-name-onboarding-ticket-routing
- Epic: EPIC-2026-04-25-agent-name-onboarding-ticket-routing
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-25T22:38:47Z
- Updated: 2026-04-26T15:08:08Z

## User Narrative
As the workflow designer, I want the current onboarding/certification and
ticket/board contracts mapped before implementation, so that the new
`agent_name` flow lands cleanly and consistently.

## Value / MRP Alignment
This story prevents an identity feature from being smeared across multiple docs
in inconsistent ways.

## Ticket Contract
- ENTRY_GATE: epic exists and the workflow identity lane is routed.
- EXECUTION_BOUNDARY:
  - current general onboarding/certification docs
  - current ticketing and board docs
  - current templates
  - this story and linked investigation task
- DEPENDENCIES:
  - current general baseline docs
  - current templates
- EXIT_GATE: the attestation/certification contract and the ticket/board schema
  contract are explicit enough to implement.
- FAILURE_ESCALATION: raise `BLOCKER` if the current docs do not define the
  right insertion points cleanly enough.

## Requirements (Functional)
- Identify where onboarding must ask for a name.
- Identify where attestation must carry the name.
- Identify where ticket metadata and board schema must change.
- Identify how multiple assigned names should be represented.

## Requirements (Non-Functional)
- Keep the change additive.
- Keep the naming key consistent across all changed surfaces.

## Scope Boundaries
- In scope:
  - onboarding/certification docs
  - ticket/board docs
  - templates
- Out of scope:
  - artifact board schema change
  - legacy ticket backfill

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested investigation before
  implementation.

## Dependencies / Related Work
- TASK-2026-04-25-investigate-current-agent-identity-touchpoints

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-25-investigate-current-agent-identity-touchpoints
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The onboarding insertion points are explicit.
- The ticket/template insertion points are explicit.
- The board insertion points are explicit.
- The multi-agent representation is explicit.

## Validation / Test Plan
- Not run.
- Validation is document reread and evidence consistency only.

## UX / API / Data Notes
- This is a workflow-identity API change, not a runtime source change.

## Risks / Mitigations
- Risk: inconsistent naming between ticket metadata and board schema.
  Mitigation: standardize the field now.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should `agent_name` default to `codex` on live legacy rows until a future
  named onboarding cycle occurs?

## Decision Log
- The field name will stay singular while allowing comma-separated values.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-25T22:38:47Z
  TYPE: FACT
  CLAIM: The current attestation/certification flow is split across
    `AGENTS.MD`, `self_certification.md`, `user_approved_certification.md`, and
    `compaction_requirements.md`, so the identity change must touch all of
    those surfaces instead of only one.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/AGENTS.MD:121-139
  - context_compass/agent_onboarding/default/general/skills/self_certification.md:16-24
  - context_compass/agent_onboarding/default/general/skills/user_approved_certification.md:4-17
  - context_compass/agent_onboarding/default/general/skills/compaction_requirements.md:39-73
  IMPACT: A single-doc patch would drift quickly; the feature needs a coherent
    documentation sweep.
  NEXT: create the investigation task and the implementation patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story proves where the identity feature belongs before implementation.
