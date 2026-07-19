# Story: Implement Agent Name Onboarding Ticket Routing
- Completed: 2026-04-26T11:39:24Z
- Summary: Closed after agent naming was wired through onboarding,
  certification, ticket templates, and attention-board routing.

## Metadata
- Story ID: STORY-2026-04-25-implement-agent-name-onboarding-ticket-routing
- Epic: EPIC-2026-04-25-agent-name-onboarding-ticket-routing
- Status: done
- Owner: codex
- Agent Name: codex
- Priority: p0
- Created: 2026-04-25T22:38:47Z
- Updated: 2026-04-26T11:39:24Z

## User Narrative
As the user, I want agents to ask for a name on every onboarding cycle and to
carry that identity into tickets and the attention board, so that multiple
agents can be tracked cleanly.

## Value / MRP Alignment
This story lands the actual workflow identity feature: agent naming,
attestation retention, ticket metadata, and board routing support.

## Ticket Contract
- ENTRY_GATE: investigation findings are explicit and the patch-doc set exists.
- EXECUTION_BOUNDARY:
  - `agent_onboarding/default/general/**`
  - `templates/*.md`
  - `attention_board.md`
  - this story and linked child tasks
- DEPENDENCIES:
  - investigation story/task
  - patch-doc set
- EXIT_GATE: onboarding/certification docs, templates/docs, and live board
  schema all reflect the new `agent_name` feature.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the feature requires a broad
  legacy-ticket migration instead of the forward schema and live-board change.

## Requirements (Functional)
- Ask for `AGENT_NAME` on every onboarding/re-onboarding certification flow.
- Include `AGENT_NAME` in ONBOARD/REONBOARD attestation formats.
- Add `Agent Name` metadata to ticket templates.
- Add `agent_name` to the attention board.
- Allow multiple names in that field.

## Requirements (Non-Functional)
- Preserve `CERTIFY: APPROVED`.
- Keep the change additive and explicit.

## Scope Boundaries
- In scope:
  - general onboarding/certification docs
  - ticket templates and ticketing docs
  - live attention board schema
- Out of scope:
  - artifact board schema change
  - broad legacy ticket migration

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the onboarding/certification docs, ticket/templates, and
  live attention-board schema now reflect the `agent_name` workflow.

## Dependencies / Related Work
- STORY-2026-04-25-investigate-agent-name-onboarding-ticket-routing
- TASK-2026-04-25-implement-agent-name-attestation-and-certification
- TASK-2026-04-25-implement-agent-name-ticket-template-and-board-schema

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-25-implement-agent-name-attestation-and-certification
- [x] Task: TASK-2026-04-25-implement-agent-name-ticket-template-and-board-schema
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The next onboarding/re-onboarding cycle must ask for a name.
- Attestation formats include `AGENT_NAME`.
- Ticket templates include `Agent Name`.
- `attention_board.md` schema includes `agent_name`.
- Multiple assigned names are documented as valid.

## Validation / Test Plan
- Re-read changed general docs and templates.
- Re-read changed board schema.
- Not run:
  - no runtime tests unless later requested

## UX / API / Data Notes
- This is a workflow schema and certification prompt change, not a runtime code
  change.

## Risks / Mitigations
- Risk: the name flow becomes inconsistent across onboarding and re-onboarding.
  Mitigation: update all attestation/certification docs together.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should legacy rows/tickets be backfilled later or only on touch?

## Decision Log
- Use one `agent_name` field that can hold one or more comma-separated names.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/agent_name_onboarding_ticket_routing/architecture_patch.md
  - system_docs/patches/active/agent_name_onboarding_ticket_routing/component_patch_onboarding_identity_flow.md
  - system_docs/patches/active/agent_name_onboarding_ticket_routing/component_patch_ticket_and_template_agent_assignment.md
  - system_docs/patches/active/agent_name_onboarding_ticket_routing/component_patch_attention_board_agent_assignment.md
  - system_docs/patches/active/agent_name_onboarding_ticket_routing/code_description_patch_attestation_and_certification_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decide after the workflow identity feature is accepted.

## Notes
- DATETIME: 2026-04-25T22:38:47Z
  TYPE: DECISION
  CLAIM: The additive model is to keep `owner` and add `agent_name`. `owner`
    continues to track the current executor/runtime owner, while `agent_name`
    tracks one or more assigned user-facing names.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/skills/active_pointerboard.md:15-35
  - context_compass/attention_board.md:24-35
  IMPACT: The feature can support multiple named agents without breaking the
    existing executor field.
  NEXT: create the patch docs and implement the two slices: onboarding flow and
    ticket/board schema.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T22:51:41Z
  TYPE: FACT
  CLAIM: The identity workflow is landed. Root/general onboarding docs now ask
    for `AGENT_NAME` alongside certification, the general baseline includes a
    dedicated `agent_identity` skill, ticket docs/templates include `Agent
    Name`, and the live `attention_board.md` schema includes `agent_name` while
    preserving `owner`.
  EVIDENCE:
  - context_compass/AGENTS.MD:84-99
  - context_compass/AGENTS.MD:155-163
  - context_compass/agent_onboarding/default/general/SKILLS.MD:15-20
  - context_compass/agent_onboarding/default/general/skills/agent_identity.md:7-28
  - context_compass/agent_onboarding/default/general/skills/ticketing.md:23-25
  - context_compass/agent_onboarding/default/general/skills/active_pointerboard.md:20-25
  - context_compass/templates/task_template.md:5-12
  - context_compass/attention_board.md:24-32
  IMPACT: The requested feature now exists as a coherent workflow contract
    rather than as scattered wording changes.
  NEXT: present the landed feature and call out how the next onboarding cycle
    should request both name and certification.
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
This story owns the workflow identity feature itself once the investigation and
patch docs are in place.
