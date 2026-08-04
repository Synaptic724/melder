# Epic: Add Agent Name To Onboarding And Ticket Routing
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after agent naming was added to onboarding,
  certification, tickets, and attention-board assignment surfaces.

## Metadata
- Epic ID: EPIC-2026-04-25-agent-name-onboarding-ticket-routing
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-25T22:38:47Z
- Updated: 2026-04-26T15:08:08Z
- Target Window: 2026-Q2
- Related Program/Initiative: context_compass workflow identity

## Problem / Opportunity
Context Compass currently routes work through `attention_board.md`, tickets, and
onboarding/certification attestations, but it does not require a user-assigned
agent name during onboarding and it does not record agent names as first-class
ticket/board state.

That makes it harder to:
- distinguish multiple concurrently assigned agents
- preserve which named agent is responsible for a ticket
- carry the chosen name through onboarding and attestation each time

## MRP Alignment (Most Reasonable Product)
This epic adds the smallest coherent identity layer that is still operationally
useful:
- ask for an `agent_name` on every onboarding/re-onboarding certification flow
- carry that name into attestation
- add `agent_name` to ticket metadata/templates
- add `agent_name` to the attention board
- allow multiple assigned names on a ticket/board row

## Ticket Contract
- ENTRY_GATE: current onboarding/certification, ticketing, and board contracts
  are investigated and patch artifacts are defined before implementation.
- EXECUTION_BOUNDARY:
  - `agent_onboarding/default/general/**`
  - `templates/*.md`
  - `attention_board.md`
  - tickets for this lane
  - patch docs for this lane
- DEPENDENCIES:
  - current general onboarding/certification docs
  - current ticketing and attention-board docs
  - current templates
- EXIT_GATE: the identity flow is documented, wired, and reread; templates and
  board schema reflect `agent_name`; the patch artifacts and workflow state are
  synchronized.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the feature requires
  backfilling a large legacy ticket set rather than landing the forward schema
  and live-board behavior cleanly.

## Goals (Outcomes)
- Add mandatory agent naming to onboarding and re-onboarding.
- Retain agent names in ONBOARD/REONBOARD attestations.
- Require certification asks to request both `AGENT_NAME:` and
  `CERTIFY: APPROVED`.
- Add `Agent Name` metadata to ticket templates and ticketing guidance.
- Add `agent_name` to the attention board schema and live board rows.
- Allow multiple agent names on tickets and board rows.

## Non-Goals (Explicit Exclusions)
- Changing `artifact_board.md` schema unless investigation proves it is needed.
- Retrofitting every legacy ticket in the repository.
- Changing non-general role overlays unless directly needed for compatibility.

## Scope Boundaries
- In scope:
  - general onboarding/certification docs
  - ticketing docs and templates
  - attention board docs and live board schema
  - new workflow tickets and patch docs
- Out of scope:
  - legacy ticket backfill outside the tickets created in this lane
  - artifact board schema change unless later required

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested investigation plus
  implementation of onboarding/ticket/board agent naming.

## Success Metrics
- onboarding/certification docs explicitly require agent naming
- attestation formats include `AGENT_NAME`
- templates include `Agent Name`
- `attention_board.md` has an `agent_name` column
- the docs explain how multiple assigned names are represented

## Requirements (Functional + Non-Functional)
- Functional:
  - ask for name every time
  - preserve name in attestation
  - record assigned names in tickets and board rows
- Non-functional:
  - additive change
  - explicit multi-agent support
  - no ambiguous identity wording

## Constraints / Assumptions
- `CERTIFY: APPROVED` remains the exact approval token.
- Multiple assigned names will be represented in one `agent_name` field using a
  comma-separated list unless a later structured representation is requested.
- Current live rows can use `codex` as the current executor identity until a
  user-provided name exists for a future onboarding cycle.

## Dependencies / External References
- `agent_onboarding/default/general/AGENTS.MD`
- `agent_onboarding/default/general/skills/self_certification.md`
- `agent_onboarding/default/general/skills/user_approved_certification.md`
- `agent_onboarding/default/general/skills/compaction_requirements.md`
- `agent_onboarding/default/general/skills/ticketing.md`
- `agent_onboarding/default/general/skills/active_pointerboard.md`
- `templates/epic_template.md`
- `templates/story_template.md`
- `templates/task_template.md`

## Milestones (Track Progress)
- [ ] Milestone 1: Investigation and patch contracts are explicit.
- [ ] Milestone 2: Onboarding/certification identity flow is landed.
- [ ] Milestone 3: Ticket/template/board identity flow is landed.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-25-investigate-agent-name-onboarding-ticket-routing
- [ ] Story: STORY-2026-04-25-implement-agent-name-onboarding-ticket-routing

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete the investigation story and capture the identity contract.
- [ ] Task: Complete the implementation story and child tasks.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- onboarding and re-onboarding require agent naming
- attestation formats include `AGENT_NAME`
- ticket templates include `Agent Name`
- ticketing guidance explains multi-agent assignment
- attention board docs and live board rows include `agent_name`

## Risks / Mitigations
- Risk: field naming drifts between onboarding, tickets, and board.
  Mitigation: standardize on `AGENT_NAME` in attestation/certification and
  `Agent Name`/`agent_name` in ticket/board surfaces.
- Risk: legacy ticket backfill explodes scope.
  Mitigation: land the forward schema and live-board changes first.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Re-read changed onboarding/certification docs.
- Re-read changed ticket/templates and attention-board docs.
- Confirm the live board schema reflects the new column.
- Not run:
  - no runtime tests unless later requested

## Rollout / Adoption Plan
- Use the new naming flow on the next onboarding/re-onboarding cycle.
- Use `Agent Name` in new tickets going forward.
- Treat legacy tickets as backfill-optional unless they are touched again.

## Open Questions
- Should `artifact_board.md` eventually gain `agent_name`, or is ticket linkage
  sufficient?

## Decision Log
- Preserve `CERTIFY: APPROVED` and add agent naming alongside it.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/agent_name_onboarding_ticket_routing/architecture_patch.md
  - system_docs/patches/active/agent_name_onboarding_ticket_routing/component_patch_onboarding_identity_flow.md
  - system_docs/patches/active/agent_name_onboarding_ticket_routing/component_patch_ticket_and_template_agent_assignment.md
  - system_docs/patches/active/agent_name_onboarding_ticket_routing/component_patch_attention_board_agent_assignment.md
  - system_docs/patches/active/agent_name_onboarding_ticket_routing/code_description_patch_attestation_and_certification_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decide after the identity workflow is accepted.

## Notes
- DATETIME: 2026-04-25T22:38:47Z
  TYPE: FACT
  CLAIM: The current general workflow already treats onboarding,
    certification, tickets, and `attention_board.md` as canonical workflow
    state, so the new identity feature belongs in those same surfaces rather
    than in a sidecar memory system.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/AGENTS.MD:54-116
  - context_compass/agent_onboarding/default/general/skills/self_certification.md:5-24
  - context_compass/agent_onboarding/default/general/skills/ticketing.md:1-96
  - context_compass/agent_onboarding/default/general/skills/active_pointerboard.md:1-43
  IMPACT: We should implement `agent_name` directly in the current workflow
    primitives, not invent a separate identity registry.
  NEXT: create the investigation story/task and the identity-flow patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic owns the addition of explicit agent naming to onboarding,
attestation, tickets, and attention-board routing.
