# Story: MutationResearch Discovery and Policy Framing

- Completed: 2026-07-11T19:30:00Z
- Summary: Closed SUPERSEDED with its parent epic (owner ruling 2026-07-11:
  not required anymore once MR shipped).
  The planned interview route never ran; the policy decisions it existed to
  capture were made instead through owner rulings across the V2 -> V3 program
  (explicit-only declarations, lane/join organization, single residence,
  notch-driven promotion, room exposure) and are durably recorded in
  artifacts/2026-07-11_mutation_research_philosophy_v3.md plus the closed
  build/exposure lanes.

## Metadata
- Story ID: STORY-2026-02-18-mutationresearch-discovery
- Epic: EPIC-2026-02-18-mutationresearch-discovery-design
- Status: superseded
- Owner: codex
- Priority: p0
- Created: 2026-02-18T23:35:36Z
- Updated: 2026-03-05T23:34:39Z

## User Narrative
As the project owner, I want a focused MutationResearch discovery story so that
we can lock governance and lifecycle policies before implementation starts.

## Value / MRP Alignment
This story anchors mutation design on explicit lane and gate contracts, reducing
risk of unsafe or ambiguous mutation behavior during later implementation work.

## Ticket Contract
- ENTRY_GATE: Epic is ready and interview task is created and routed
- EXECUTION_BOUNDARY: discovery and policy synthesis only
- DEPENDENCIES: MutationResearch forward contract + systems docs + user interview
- EXIT_GATE: acceptance criteria met and policy decisions captured in notes
- FAILURE_ESCALATION: raise DECISION_REQUEST for unresolved governance conflicts

## Requirements (Functional)
- Consolidate MutationResearch lane contract and control-plane gate expectations.
- Capture interview decisions for lock, validation, and promotion policy.
- Convert unresolved policy items into explicit follow-up tasks.

## Requirements (Non-Functional)
- Keep all decisions evidence-backed and traceable.
- Preserve UNKNOWN-first discipline for unresolved governance questions.
- Keep discovery notes compact and resumable.

## Scope Boundaries
- In scope:
- mutation lane governance discovery and policy framing
- interview capture and decision closure
- Out of scope:
- runtime implementation and mutation engine code changes
- production rollout decisions

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: user redirected active focus to MutationResearch and the
  linked interview task is now the active discovery route.

## Dependencies / Related Work
- EPIC-2026-02-18-mutationresearch-discovery-design
- TASK-2026-02-18-mutationresearch-user-interview

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-18-mutationresearch-user-interview - run structured user interview
- [ ] Task: synthesize policy decisions into follow-up implementation planning task(s)
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Interview completed and policy decisions documented.
- Open policy questions have clear next actions and owners.
- Story output is sufficient to start implementation decomposition.

## Validation / Test Plan
- Validate policy synthesis consistency against source contract docs.
- Validate interview outcomes through explicit user confirmation.

## UX / API / Data Notes
- Focus on mutation governance and lifecycle semantics, not code-level APIs.

## Risks / Mitigations
- Risk: escalation/promotion policy stays ambiguous.
- Mitigation: explicit decision checkpoints and DECISION_REQUEST notes.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- What lock granularity is acceptable for multi-agent mutation campaigns?
- What promotion authority model is required in shared environments?

## Decision Log
- 2026-02-18: Story initiated as policy-first discovery prerequisite.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-02-18T23:35:36Z
  TYPE: FACT
  CLAIM: MutationResearch sources already define strict lane separation and a
    mandatory gated lifecycle from proposal through promotion/rollback/closure.
  EVIDENCE:
  - MutationResearch/systems/lane_contract.md:6-26
  - MutationResearch/systems/control_plane_gates.md:6-36
  - MutationResearch/systems/mutation_lifecycle.md:6-36
  IMPACT: Discovery work should focus on policy choices and operational thresholds,
    not re-defining baseline mutation mechanics.
  NEXT: execute interview task and settle top governance questions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-02-20T22:02:45Z
  TYPE: FACT
  CLAIM: Story-level documentation now explicitly captures that MutationResearch
    is directionally stable on lane/gate contracts while governance defaults
    remain intentionally open for interview resolution.
  EVIDENCE:
  - MutationResearch/WORKING_MODEL.md:17-24
  - MutationResearch/systems/control_plane_gates.md:1-42
  - MutationResearch/systems/open_questions.md:1-21
  IMPACT: Story synthesis should preserve strict lane/gate invariants and avoid
    prematurely fixing unresolved promotion/validation policy defaults.
  NEXT: run interview and convert resolved governance defaults into decisions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-05T23:34:39Z
  TYPE: DECISION
  CLAIM: Story can advance from `ready` to `in_progress` because the linked
    interview task already bounds the unresolved governance set and is the
    designated successor lane after the current AethericRift interview.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-02-18_aethericrift_user_interview_task.md:229-230
  - MutationResearch/systems/open_questions.md:1-21
  IMPACT: Story completion now depends on direct interview closure and
    follow-up ticketization rather than further pre-interview preparation.
  NEXT: run the MutationResearch interview and convert confirmed policy defaults
    into story/epic decisions.
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
Story initialized with policy-focused discovery scope. Next action is interview
capture to finalize unresolved mutation governance choices, with active focus
now switched to this lane and current
baseline/open-unknown status now fully documented.
