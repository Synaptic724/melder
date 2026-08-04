<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner hope_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Story: Investigate Nexus Directory Doc Drift

## Metadata
- Story ID: STORY-2026-06-12-investigate-nexus-directory-doc-drift
- Epic: EPIC-2026-06-12-investigate-source-system-doc-drift-excluding-mutation-and-crystallizer
- Status: ready
- Owner: codex
- Agent Name: hope_0
- Priority: p0
- Created: 2026-06-12T13:00:58Z
- Updated: 2026-06-12T13:00:58Z

## User Narrative
As the documentation maintainer, I want the meaningful `src/melder/nexus/**`
runtime surfaces mapped against the live code, so the architecture,
components, and graph docs stay correct for the public AR runtime.

## Value / MRP Alignment
`nexus` is the second highest-value lane because it owns the public AR root,
Rift, ACL, projection, and codegen-facing surfaces that dominate a large part
of the current source-system narrative.

## Ticket Contract
- ENTRY_GATE: the new source-system doc-drift epic is active and the `aether`
  lane is the first live investigation lane.
- EXECUTION_BOUNDARY:
  - `src/melder/nexus/**`
  - the source-system docs and graph surfaces when `nexus` drift is directly
    evidenced
- DEPENDENCIES:
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `codex/context_compass/system_docs/readable_src_graph.json`
  - `codex/context_compass/system_docs/src_graph.json`
- EXIT_GATE: concrete `nexus`-scoped drift is inventoried and the required
  refresh slice is explicit or complete.
- FAILURE_ESCALATION: raise `DECISION_REQUEST`, `CONFLICT`, or `BLOCKER` if
  this lane drags in excluded mutation/crystallizer work.

## Requirements (Functional)
- verify `nexus` / Rift / ACL / projection docs against live code
- refresh only directly evidenced drift

## Requirements (Non-Functional)
- skip low-signal package markers and caches
- preserve graph/schema contracts if graph edits are needed

## Scope Boundaries
- In scope:
  - `nexus`
  - `frame_descriptor`
  - `acl`
  - `rift`
  - `projection`
  - `codegen_system`
- Out of scope:
  - mutation-research
  - crystallizer
  - `__pycache__`
  - metadata-only modules with no runtime-architecture value

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the story is defined and bounded, but active execution
  should start with the already-proven `aether` drift seam first.

## Dependencies / Related Work
- parent epic
- future child tasks to be created after the first `nexus` drift seams are found

## Tasks (Implementation Checklist)
- [ ] Task: TBD - first bounded `nexus` drift investigation slice
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `nexus`-scoped drift is concrete and evidence-backed
- low-signal files stay out of the mapping lane

## Validation / Test Plan
- doc and graph consistency validation when edits occur

## UX / API / Data Notes
- likely high-value seams live around Rift/ACL/codegen narratives and graph edges

## Risks / Mitigations
- Risk: the `nexus` surface is broad and dense.
  Mitigation: split by first concrete seams, not by abstract subsystem names alone.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- whether the first `nexus` slice should target Rift/space posture drift or ACL/profile drift

## Decision Log
- 2026-06-12: keep `nexus` ready behind `aether`; do not widen the active lane prematurely.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - nexus directory drift
  - rift and acl coherence
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-06-12T13:00:58Z
  TYPE: PLAN
  CLAIM: `nexus` is a ready follow-on lane, but current execution should stay
    on the already-evidenced `aether` seam first.
  EVIDENCE:
  - src/melder/nexus: directory inventory
  - codex/context_compass/system_docs/src_architecture.md
  IMPACT: This story is ready to route once the first `aether` slice is either
    complete or split cleanly.
  NEXT: keep this story parked in ready state until the current active task
    defines the next lane switch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

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
This story defines the `nexus` directory drift lane and is ready for routing
after the first `aether` seam is handled.
