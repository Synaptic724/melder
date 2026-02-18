

Completed: 2026-02-17T11:57:04Z
Summary: Closed by explicit user directive to close all currently open tickets.

# Epic: Skill Path Map Onboarding State Machine Generalization

## Metadata
- Epic ID: EPIC-2026-02-16-skill-path-map-onboarding-state-machine-generalization
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-16T23:21:16Z
- Updated: 2026-02-17T11:57:04Z
- Target Window: 2026-Q1
- Related Program/Initiative: context_compass_public_generalization

## Problem / Opportunity
Current onboarding is policy-heavy and optimized for deep repository replay.
We now need a generalized onboarding system that can support first-time users,
public adoption, language-neutral operation, and configurable skill routing.

## MRP Alignment (Most Reasonable Product)
The MRP is a durable onboarding state machine plus a `skill_path_map` contract
that separates baseline onboarding from language- or career-specific paths.
This gives us one stable core that can scale to different repositories and
languages without rewriting the onboarding model.

## Ticket Contract
- ENTRY_GATE: active board row routes to this epic/story lane.
- EXECUTION_BOUNDARY: onboarding architecture, skills/careers routing model,
  configuration contract, and migration design.
- DEPENDENCIES: `AGENTS.MD`, `WORKFLOW.md`, config contract, and current
  onboarding skill tree layout.
- EXIT_GATE: approved state-machine spec, `skill_path_map` schema, migration
  plan, and accepted implementation tickets/stories/tasks.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` on scope, compatibility, or
  migration risk conflicts.

## Goals (Outcomes)
- Define a language-agnostic onboarding state machine.
- Define a `skill_path_map` structure for baseline + optional skill paths.
- Introduce first-time onboarding mode and configurable path selection.
- Decouple Python-specific skill assumptions from the main onboarding path.
- Establish committed profile layering with public defaults plus a concrete
  `user_defined/synaptic_python_developer` reference implementation.
- Produce an implementation roadmap for skills/careers reorganization.

## Non-Goals (Explicit Exclusions)
- Immediate full rewrite of all skills in this epic.
- Runtime/tooling implementation in this planning ticket.
- Backporting historical archived tickets to new schema.

## Scope Boundaries
- In scope:
- onboarding state-machine definition and transitions
- `skill_path_map` concept, schema expectations, and routing rules
- first-time onboarding flow and configuration entry points
- skills/careers reorganization strategy and migration phases
- Out of scope:
- full implementation of all migration tasks in this epic ticket
- non-onboarding subsystem redesigns

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: user requested closing all tickets as done.

## Success Metrics
- One approved onboarding state-machine specification.
- One approved `skill_path_map` contract with config ownership.
- One approved first-time onboarding and path-selection flow.
- Clear migration phases with explicit acceptance gates.

## Requirements (Functional + Non-Functional)
- Functional:
- onboarding supports baseline path + configurable branch paths.
- onboarding supports first-time flow and returning-agent flow.
- path routing is configurable and language-neutral.
- folder contract supports:
  `agent_onboarding/default/general`,
  `agent_onboarding/default/engineer`, and
  `agent_onboarding/user_defined/synaptic_python_developer`.
- Non-functional:
- preserve deterministic onboarding behavior.
- keep policy source authoritative and easy to audit.
- minimize token overhead while preserving safety gates.
- keep exemplar user-defined profile committed for public reuse patterns.

## Constraints / Assumptions
- Existing policy gates remain enforced until replacement is approved.
- Migration should be incremental and reviewable.
- UNKNOWN-first evidence discipline is required for redesign claims.

## Dependencies / External References
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/default/general/skills/workflow.md`
- `context_compass/config/context_compass_config.yaml`

## Milestones (Track Progress)
- [x] Milestone 1: Discovery interview and requirements alignment complete.
- [x] Milestone 2: State-machine and `skill_path_map` draft approved.
- [x] Milestone 3: Migration plan approved with implementation tickets/stories/tasks.

## Stories (Required to Complete)
- [x] Story: STORY-2026-02-16-skill-path-map-discovery-interview -
      capture requirements and decision constraints with user.
- [x] Story: STORY-YYYY-MM-DD-skill-path-map-state-machine-spec -
      define state graph, transitions, and guardrails.
- [x] Story: STORY-YYYY-MM-DD-skill-path-map-migration-plan -
      define phased reorganization and rollout.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-02-16-skill-path-map-discovery-interview.
- [x] Task: Define canonical config ownership for onboarding path selection.
- [x] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- User-approved onboarding state machine exists with clear transition rules.
- User-approved `skill_path_map` contract exists with config authority.
- User-approved migration plan exists with concrete implementation stories.

## Risks / Mitigations
- Risk: over-generalization can weaken enforcement guarantees.
  Mitigation: keep prime safety gates explicit in the state machine.
- Risk: migration churn across skills/careers can break onboarding continuity.
  Mitigation: phased rollout with acceptance gates per phase.

## Applicable Anti-Patterns
- [x] No epic-state transition without story-level evidence.
- [x] No closure while required stories are incomplete or unaccepted.
- [x] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Validate by design-review checkpoints and acceptance confirmation.
- Use story/task notes with evidence pointers for every major decision.

## Rollout / Adoption Plan
- Phase 1: discovery + model selection.
- Phase 2: schema/spec documentation and pilot routing.
- Phase 3: implementation tranche planning and execution.

## Open Questions
- What are the minimal mandatory states for safe onboarding?
- Which config surface should own path selection precedence?
- How do we enforce language neutrality without losing specialization depth?

## Decision Log
- 2026-02-16: Epic initiated for `skill_path_map` + onboarding state-machine
  redesign by user direction.
- 2026-02-16: `synaptic_python_developer` remains in-repo under
  `agent_onboarding/user_defined/` as a public example profile.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - artifacts/2026-02-16_skill_path_map_onboarding_state_machine_notes.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: upon epic closure decision

## Notes
- DATETIME: 2026-02-16T23:21:16Z
  TYPE: PLAN
  CLAIM: We are starting a top-priority epic to redesign onboarding around a
    configurable `skill_path_map` and an explicit onboarding state machine.
  EVIDENCE:
  - context_compass/AGENTS.MD:8-34
  - context_compass/AGENTS.MD:76-88
  - context_compass/config/context_compass_config.yaml:52-53
  IMPACT: This establishes a formal lane for language-neutral onboarding and
    future public adoption requirements.
  NEXT: create and route an interview/discovery story for direct user alignment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T23:31:33Z
  TYPE: DECISION
  CLAIM: Public adoption model will include a committed exemplar profile at
    `agent_onboarding/user_defined/synaptic_python_developer` layered above
    default general + python developer profiles.
  EVIDENCE:
  - tickets/epics/2026-02-16_skill_path_map_onboarding_state_machine_generalization_epic.md:35-45
  - tickets/stories/2026-02-16_skill_path_map_discovery_interview_story.md:33-45
  IMPACT: The repo will provide both generalized defaults and a concrete
    advanced profile example without local-only hidden behavior.
  NEXT: define the first migration task to separate `general` vs
    `python_developer` and codify YAML profile defaults.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T23:32:11Z
  TYPE: PLAN
  CLAIM: Epic now has the first execution task for split-contract definition:
    `TASK-2026-02-16-general-python-user-profile-split-contract`.
  EVIDENCE:
  - tickets/tasks/2026-02-16_general_python_user_profile_split_contract_task.md:1-42
  - tickets/stories/2026-02-16_skill_path_map_discovery_interview_story.md:63-75
  IMPACT: Program direction is now anchored to a concrete contract-first
    migration task.
  NEXT: complete the task discovery output and use it to plan migration tranche
    tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T23:45:25Z
  TYPE: FACT
  CLAIM: Initial discovery confirms baseline overload in `general` versus
    minimal `engineer` deltas; epic direction now explicitly targets
    rebalancing into `default/general` and `default/engineer` with skills-map
    ownership in `skill_path_map/`.
  EVIDENCE:
  - agent_onboarding/default/general/SKILLS.MD:26-38
  - agent_onboarding/default/general/skills/onboarding_read_paths.txt:38-55
  - agent_onboarding/default/engineer/SKILLS.MD:3-7
  - tickets/tasks/2026-02-16_general_python_user_profile_split_contract_task.md:157-162
  IMPACT: Epic can move from concept framing into contract-backed migration
    planning.
  NEXT: finalize and review the reallocation matrix, then open implementation
    tranche tickets/stories/tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Epic launched. Next action is interview/discovery with the user to define
state-machine boundaries, config authority, and migration constraints.







