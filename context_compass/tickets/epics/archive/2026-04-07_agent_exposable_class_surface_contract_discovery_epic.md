# Epic: Agent-Exposable Class Surface Contract Discovery

## Metadata
- Epic ID: EPIC-2026-04-07-agent-exposable-class-surface-contract-discovery
- Status: draft
- Owner: codex
- Priority: p1
- Created: 2026-04-07T01:21:38Z
- Updated: 2026-04-07T01:21:38Z
- Target Window: 2026-Q2
- Related Program/Initiative: Melder agent-facing runtime surfaces

## Problem / Opportunity
The current AST-backed viewer/profile class-surface introspection proves that
agents benefit from a predictable self-description layer for active runtime
surfaces. A broader opportunity exists across Melder: classes throughout the
system could expose a stable, agent-consumable class surface in a predictable
way instead of each subsystem inventing its own description mechanics later.

## MRP Alignment (Most Reasonable Product)
This is a systems-first discovery lane. If Melder is going to be an
AI-native runtime world, then agents need predictable class-surface contracts
across that world. The right foundation is not one-off viewer-specific
introspection forever; it is a coherent class-surface protocol that can be
applied across the system without breaking ownership, cleanup, or policy
boundaries.

## Ticket Contract
- ENTRY_GATE: the current viewer-surface AST slice is accepted as a useful
  proving ground for class-surface introspection.
- EXECUTION_BOUNDARY: discovery and design only for a broader Melder-wide
  agent-exposable class-surface contract or mixin/base pattern.
- DEPENDENCIES:
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
  - src/melder/aether/nexus/rift/frame_viewer/class_surface_ast_describer.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py
- EXIT_GATE: the discovery work defines whether Melder should adopt a shared
  mixin/base contract, a protocol, or a service-based introspection layer.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the candidate global
  contract starts forcing incompatible behavior on core runtime classes.

## Goals (Outcomes)
- Define the right system-wide shape for agent-exposable class surfaces.
- Determine whether inheritance, protocol, or service composition is the right
  mechanism.
- Define the minimum stable JSON surface that classes should expose.
- Identify which Melder subsystems should adopt the pattern first.

## Non-Goals (Explicit Exclusions)
- Immediate repo-wide rollout.
- Mutation-system integration.
- Replacing existing runtime APIs with AST-only surfaces.
- Forcing every class in Melder to expose itself to agents.

## Scope Boundaries
- In scope:
  - discovery of a system-wide class-surface contract
  - design tradeoffs between mixin/base/protocol/service approaches
  - candidate rollout targets and sequencing
- Out of scope:
  - implementation beyond the current viewer proof-of-concept
  - broad retrofitting across the codebase

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created as a later discovery lane after the viewer AST
  slice suggested a broader reusable opportunity.

## Success Metrics
- One clear recommended contract mechanism.
- One minimal stable JSON schema for agent-consumable class surfaces.
- One prioritized rollout order for the first candidate Melder subsystems.

## Requirements (Functional + Non-Functional)
- Functional:
  - identify the right reusable contract shape
  - define what "agent-exposable" means at class scope
  - define what should be excluded by default
- Non-functional:
  - preserve ownership/cleanup boundaries
  - avoid payload/runtime leakage by default
  - keep JSON output deterministic and compact

## Constraints / Assumptions
- The current viewer AST slice is only a proving ground, not proof that the
  exact same mechanism should be inherited globally.
- Runtime object ownership and cleanup rules remain first-class.
- Source-surface introspection must not become a backdoor into unsafe runtime
  internals.

## Dependencies / External References
- Current viewer AST surface work in the active viewer task.

## Milestones (Track Progress)
- [ ] Milestone 1: define candidate contract shapes and tradeoffs
- [ ] Milestone 2: identify first rollout targets and exclusion rules

## Stories (Required to Complete)
- [ ] Story: STORY-TBD - discovery of Melder-wide class-surface contract
- [ ] Story: STORY-TBD - rollout-target prioritization and boundary rules

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: create the discovery story when this lane is activated
- [ ] Task: verify whether mixin inheritance is actually the right shape or if
      a protocol/service layer is cleaner
- [ ] Task: verify the minimum stable JSON schema for agent consumption
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- One accepted discovery story defines the recommended contract mechanism.
- One accepted discovery story defines rollout ordering and exclusions.

## Risks / Mitigations
- Risk: a global mixin/base contract could become intrusive or force poor
  inheritance choices.
  Mitigation: keep discovery focused on real tradeoffs, including protocol and
  service alternatives.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Discovery validation only until this lane is activated.

## Rollout / Adoption Plan
- Defer until discovery defines the first candidate rollout targets.

## Open Questions
- Should this be a mixin, an ABC/protocol pair, or a standalone service?
- Which Melder classes should be agent-exposable by default, if any?
- What should be the minimum stable JSON schema?

## Decision Log
- Created as a later discovery lane after the viewer AST surface proved useful.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: if later activated, update according to the discovery lane

## Notes
- DATETIME: 2026-04-07T01:21:38Z
  TYPE: PLAN
  CLAIM: The viewer AST surface suggests a larger reusable opportunity across
    Melder: a predictable agent-exposable class-surface contract that could be
    adopted by selected subsystems later. This epic exists to hold that later
    discovery lane without polluting the currently active viewer-runtime work.
  EVIDENCE:
  - user_instruction: "maybe this is something we should have for every class in melder"
  - src/melder/aether/nexus/rift/frame_viewer/class_surface_ast_describer.py:1-1
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1358-1517
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:327-434
  IMPACT: We now have a durable place to run this later discovery without
    hijacking the active viewer task.
  NEXT: leave this epic dormant until the viewer AST slice is accepted and the
    user explicitly activates discovery.
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
This epic is parked as a later discovery lane. The active viewer AST surface
acts as the proving ground, and this epic exists so the larger Melder-wide
contract question has a durable home when the time comes.
