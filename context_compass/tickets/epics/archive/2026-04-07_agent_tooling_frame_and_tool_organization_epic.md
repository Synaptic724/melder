# Epic: Agent Tooling Frame And Tool Organization

## Metadata
- Epic ID: EPIC-2026-04-07-agent-tooling-frame-and-tool-organization
- Status: draft
- Owner: codex
- Priority: p1
- Created: 2026-04-07T11:48:01Z
- Updated: 2026-04-07T11:48:01Z
- Target Window: 2026-Q2
- Related Program/Initiative: Melder agent-facing runtime surfaces

## Problem / Opportunity
The current viewer/runtime lane is proving out agent-facing tools, AST
introspection, top-level system-doc objects, and other operator surfaces. A
future opportunity exists to organize important agent-facing tools into a
dedicated frame or tooling-oriented runtime surface rather than scattering them
ad hoc across unrelated objects.

## MRP Alignment (Most Reasonable Product)
If Melder is going to host more first-class agent-facing capabilities, those
capabilities need a coherent home. A dedicated tooling frame/surface could
provide a stable place for:
- AST introspection tools
- system-doc objects
- future agent query helpers
- other non-conduit object-facing surfaces

## Ticket Contract
- ENTRY_GATE: the viewer/runtime proving ground has demonstrated enough value
  that a broader tooling-organization lane is worth preserving for later.
- EXECUTION_BOUNDARY: discovery/design for tooling organization only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_implement_actionable_viewer_profile_tool_compositions.md
  - tickets/epics/2026-04-07_agent_exposable_class_surface_contract_discovery_epic.md
  - src/melder/__architecture__.py
  - src/melder/__components__.py
  - src/melder/__graph_network__.py
  - src/melder/__graph_details__.py
- EXIT_GATE: the epic defines whether agent-facing tools should live in a
  dedicated frame, what belongs there, and how it should relate to Rift/viewer
  surfaces.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the “tooling frame” concept
  conflicts with core runtime ownership rules.

## Goals (Outcomes)
- Decide whether a dedicated tooling frame is the right home.
- Define what categories of tools belong there.
- Define how it should relate to Rift/viewer usage.

## Non-Goals (Explicit Exclusions)
- Immediate tooling-frame implementation.
- Rewriting the current viewer to depend on that concept right now.
- Mutation-system or graph-runtime changes.

## Scope Boundaries
- In scope:
  - discovery/design for dedicated tooling organization
  - candidate tool categories and ownership boundaries
  - relationship to top-level system-doc objects and AST surfaces
- Out of scope:
  - runtime rollout now
  - broad code motion now

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created as a future planning lane so the tooling-frame
  idea has a durable home.

## Success Metrics
- One accepted answer on whether the tooling frame is worth building.
- One accepted ownership map for what belongs there.
- One accepted relationship model to Rift/viewer surfaces.

## Requirements (Functional + Non-Functional)
- Functional:
  - identify candidate tool categories
  - define ownership and access boundaries
  - define relationship to top-level doc objects
- Non-functional:
  - preserve runtime clarity
  - avoid agent-tool sprawl
  - avoid duplicating the same tool surface in multiple places

## Constraints / Assumptions
- The current viewer/runtime proving ground remains useful independently.
- This lane is for organization/architecture, not immediate runtime changes.

## Dependencies / External References
- Current viewer AST and operator-surface work.

## Milestones (Track Progress)
- [ ] Milestone 1: Define tooling-frame candidate scope
- [ ] Milestone 2: Define ownership and integration boundaries

## Stories (Required to Complete)
- [ ] Story: STORY-TBD - tooling-frame discovery and candidate scope
- [ ] Story: STORY-TBD - ownership and integration model

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: create the first tooling-frame discovery story when activated
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The tooling-frame concept is either accepted with boundaries or rejected with
  rationale.

## Risks / Mitigations
- Risk: a tooling frame becomes a junk drawer.
  Mitigation: require explicit inclusion/exclusion rules.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Discovery validation only until the lane is activated.

## Rollout / Adoption Plan
- Defer until this lane is explicitly activated.

## Open Questions
- Is a dedicated tooling frame better than top-level objects plus Rift tools?
- What should be the first candidates if it exists?
- How should it relate to `__architecture__`, `__components__`,
  `__graph_network__`, and `__graph_details__`?

## Decision Log
- Created as a future planning epic after the current viewer/runtime tools
  suggested a broader organization opportunity.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-07T11:48:01Z
  TYPE: PLAN
  CLAIM: We need a durable reminder that agent-facing tools may eventually need
    a more coherent home than ad hoc placement. This epic exists so that later
    discovery can happen intentionally instead of being reinvented from chat
    memory.
  EVIDENCE:
  - user_instruction: "add an epic for properly organizing tools like this into a special frame we'll be using"
  IMPACT: The tooling-organization idea now has a durable planning home without
    being forced into the active viewer lane.
  NEXT: leave this epic dormant until you explicitly activate the tooling-frame
    discovery work.
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
This is a future planning epic only. The current viewer/runtime tools remain
the active proving ground; this epic simply preserves the later tooling-frame
idea as a durable lane.
