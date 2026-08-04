# Epic: MutationResearch Discovery and Design Program

- Completed: 2026-07-11T19:30:00Z
- Summary: Closed SUPERSEDED (owner ruling 2026-07-11: the old epics were not
  required anymore once MR shipped - this epic's planned route never ran and
  nothing in the live system depends on it; "done" would overclaim). The goals
  (one coherent MR design baseline, resolved governance policy,
  implementation-ready follow-ups) were ALL achieved - through the owner-ruled
  V2 -> V3 philosophy program rather than the planned interview route. The old
  MutationResearch/ docs model (safe-lane/mutation-lane, control-plane gates,
  promotion governance) was superseded by the research-record model
  (artifacts/2026-07-11_mutation_research_philosophy_v3.md): lanes as version
  lines, divergence-aware join (no merge machinery), single residence,
  forward-only journal, room exposure. The open questions resolved with it:
  intent = explicit declarations only; locks = per-structure RLock + single
  residence + the change-control transaction plane; promotion = notch
  auto-record under owner rulings. The built, tested, owner-accepted system
  (closed 2026-07-11/12 lanes) is the design baseline this epic asked for.

## Metadata
- Epic ID: EPIC-2026-02-18-mutationresearch-discovery-design
- Status: superseded
- Owner: codex
- Priority: p0
- Created: 2026-02-18T23:35:36Z
- Updated: 2026-03-05T23:34:39Z
- Target Window: 2026-Q1
- Related Program/Initiative: MutationResearch Foundations

## Problem / Opportunity
MutationResearch has a strong philosophical contract and systems model, but the
current direction still requires discovery synthesis and user-driven decisions
on locks, validation policy, and promotion governance before implementation.

## MRP Alignment (Most Reasonable Product)
The MRP is a governed mutation design baseline where safe lane and mutation lane
separation, control-plane gates, and promotion semantics are fully explicit and
ready to convert into implementation slices without policy drift.

## Ticket Contract
- ENTRY_GATE: MutationResearch source set reviewed and discovery interview scheduled
- EXECUTION_BOUNDARY: discovery/design synthesis only; no runtime implementation work
- DEPENDENCIES: MutationResearch forward contract + lane/gate/lifecycle system docs
- EXIT_GATE: discovery story accepted with resolved decisions and prioritized unknowns
- FAILURE_ESCALATION: raise DECISION_REQUEST on governance conflicts and BLOCKER on missing policy truth

## Goals (Outcomes)
- Produce one coherent MutationResearch design baseline.
- Validate safe-lane vs mutation-lane boundaries and escalation criteria.
- Resolve policy for lock granularity, validation profiles, and promotion authority.
- Produce implementation-ready follow-up tickets linked to confirmed decisions.

## Non-Goals (Explicit Exclusions)
- Implementing mutation runtime mechanics in this epic.
- Defining final storage backend or low-level persistence classes.
- Treating unsafe mode as a default mutation path.

## Scope Boundaries
- In scope:
- discovery synthesis for lane contract, control-plane gates, lifecycle, and topology
- user interview and decision capture for unresolved policy questions
- Out of scope:
- code changes to Melder/AethericRift runtime
- production rollout execution

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: user redirected active focus to MutationResearch and the
  governance interview lane is now the active discovery tranche.

## Success Metrics
- Discovery story completed with interview-backed decisions.
- Control-plane gate decisions documented with clear acceptance criteria.
- Open questions mapped to explicit follow-up tasks.

## Requirements (Functional + Non-Functional)
- Preserve strict safe-lane and mutation-lane contract boundaries.
- Keep mutation lifecycle states and required artifacts explicit.
- Keep governance and rollback semantics auditable and deterministic.
- Maintain boundary alignment with Rift and CommandOps responsibilities.

## Constraints / Assumptions
- Mutation operations are high-risk and require explicit gate discipline.
- Community and enterprise topologies share contract semantics but differ in placement.
- Promotion authority is policy-sensitive and may require hybrid approval flow.

## Dependencies / External References
- MutationResearch/Ticket - Forward MutationResearch Philosophical Implementation Contract.md
- MutationResearch/WORKING_MODEL.md
- MutationResearch/systems/lane_contract.md
- MutationResearch/systems/control_plane_gates.md
- MutationResearch/systems/mutation_lifecycle.md

## Milestones (Track Progress)
- [ ] Milestone 1: Discovery interview complete and policy unknowns triaged.
- [ ] Milestone 2: Design baseline approved and implementation tasks created.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-18-mutationresearch-discovery - discovery synthesis and policy framing

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-02-18-mutationresearch-discovery
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Discovery story accepted with explicit decisions for top governance unknowns.
- Mutation lifecycle and control-plane gate behavior documented and approved.
- Remaining unknowns converted into bounded follow-up tickets.

## Risks / Mitigations
- Risk: lane contract ambiguity causes unsafe escalation behavior.
- Mitigation: enforce explicit escalation/promotion decision points in design.
- Risk: policy disagreements delay execution start.
- Mitigation: interview-first decision capture with explicit approval gates.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Validate design consistency against source contracts and systems docs.
- Validate decision closure through interview outcomes and user checkpoint approval.

## Rollout / Adoption Plan
- Translate approved design into phased implementation tasks by risk tier.
- Start with strict gate/observability slices before mutation automation surfaces.

## Open Questions
- Mutation intent classifier model (explicit-only vs assisted).
- Lock granularity model (spell, graph region, domain scope).
- Promotion authority in shared environments (agent, human, hybrid).

## Decision Log
- 2026-02-18: Discovery-first lane selected to align mutation policy before coding.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-02-18T23:35:36Z
  TYPE: FACT
  CLAIM: MutationResearch direction is workspace-first mutation with explicit
    lane separation, lifecycle states, and non-negotiable control-plane gates.
  EVIDENCE:
  - MutationResearch/Ticket - Forward MutationResearch Philosophical Implementation Contract.md:124-166
  - MutationResearch/systems/lane_contract.md:6-26
  - MutationResearch/systems/mutation_lifecycle.md:6-36
  - MutationResearch/systems/control_plane_gates.md:6-36
  IMPACT: Discovery must resolve policy unknowns so implementation can proceed
    under stable governance constraints.
  NEXT: Execute interview task and record decisions in story/epic notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-20T22:02:45Z
  TYPE: FACT
  CLAIM: MutationResearch source set was re-read and documented as an active
    baseline with settled lane/gate direction plus intentionally unresolved
    policy details that remain UNKNOWN until interview closure.
  EVIDENCE:
  - MutationResearch/Ticket - Forward MutationResearch Philosophical Implementation Contract.md:4-7
  - MutationResearch/Ticket - Forward MutationResearch Philosophical Implementation Contract.md:159-169
  - MutationResearch/WORKING_MODEL.md:3-4
  - MutationResearch/systems/open_questions.md:1-21
  IMPACT: Epic execution remains discovery-first; implementation decomposition
    must wait for explicit policy decisions on open governance questions.
  NEXT: run the mutation interview task after AethericRift decision closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-05T23:34:39Z
  TYPE: DECISION
  CLAIM: MutationResearch epic can advance from `ready` to `in_progress`
    because the unresolved governance set is bounded and the linked interview
    task was already staged as the next discovery lane after AethericRift.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-02-18_aethericrift_user_interview_task.md:229-230
  - MutationResearch/systems/open_questions.md:1-21
  IMPACT: Epic Milestone 1 can now proceed through interview-driven closure
    rather than staying parked behind AethericRift sequencing.
  NEXT: run the linked MutationResearch interview task and propagate resolved
    governance defaults to story and epic notes.
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

## Salvage Review (owner-directed read-before-archive, 2026-07-11)
Read in full by mutation_0 before final archive. Nothing here contradicts or
extends the built system: the referenced MutationResearch/ source docs no
longer exist on disk, and every policy question this epic held open was
resolved or retired by the V2->V3 program. No salvage items originated from
this epic itself; the salvageable ideas came from the May artifacts and are
recorded in artifacts/2026-07-11_mutation_research_philosophy_v3.md Open
Directions (lane TYPE classification, surgical synthesis, runtime
recomposition).

## Context / Handoff Summary
MutationResearch discovery/design epic initialized with source-backed boundaries.
MutationResearch baseline and open-unknown posture are now explicitly
documented. Active focus is now interview-driven closure for governance and
promotion policy unknowns.
