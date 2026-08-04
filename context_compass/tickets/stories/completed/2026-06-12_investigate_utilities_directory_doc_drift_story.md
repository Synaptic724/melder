<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner hope_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Story: Investigate Utilities Directory Doc Drift

## Metadata
- Story ID: STORY-2026-06-12-investigate-utilities-directory-doc-drift
- Epic: EPIC-2026-06-12-investigate-source-system-doc-drift-excluding-mutation-and-crystallizer
- Status: ready
- Owner: codex
- Agent Name: hope_0
- Priority: p1
- Created: 2026-06-12T13:00:58Z
- Updated: 2026-06-12T13:00:58Z

## User Narrative
As the documentation maintainer, I want the meaningful
`src/melder/utilities/**` support surfaces mapped against the live code, so
shared helpers, synchronization, logger, and interface docs stay coherent with
the runtime they support.

## Value / MRP Alignment
`utilities` is shared infrastructure. It matters, but it should follow the
primary runtime directories once their live drift is understood first.

## Ticket Contract
- ENTRY_GATE: the source-system doc-drift epic is active and at least one
  higher-leverage runtime directory lane has been investigated first.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/**`
  - source-system docs and graph surfaces when utility drift is directly evidenced
- DEPENDENCIES:
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `codex/context_compass/system_docs/readable_src_graph.json`
  - `codex/context_compass/system_docs/src_graph.json`
- EXIT_GATE: concrete `utilities`-scoped drift is inventoried and the required
  refresh slice is explicit or complete.
- FAILURE_ESCALATION: raise `DECISION_REQUEST`, `CONFLICT`, or `BLOCKER` if
  the lane broadens into low-signal junk instead of real support surfaces.

## Requirements (Functional)
- verify meaningful utilities surfaces against docs/graph
- skip low-signal files

## Requirements (Non-Functional)
- preserve graph/schema contracts when graph edits are needed
- avoid inventory theater around helper files with no architectural value

## Scope Boundaries
- In scope:
  - `general_base`
  - `helpers`
  - `interfaces`
  - `logger`
  - `synchronization`
  - meaningful exception and data-structure surfaces only when they materially
    affect runtime documentation
- Out of scope:
  - `__pycache__`
  - metadata-only modules
  - mutation-research
  - crystallizer

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the story is defined, but its leverage is lower than the
  already-evidenced `aether` seam and the likely `nexus` follow-on lane.

## Dependencies / Related Work
- parent epic
- future child tasks to be created after first concrete `utilities` drift is found

## Tasks (Implementation Checklist)
- [ ] Task: TBD - first bounded `utilities` drift investigation slice
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `utilities`-scoped drift is concrete and evidence-backed
- low-signal infrastructure junk stays out of the lane

## Validation / Test Plan
- doc and graph consistency validation when edits occur

## UX / API / Data Notes
- likely high-value seams will be interface/logger/synchronization alignment,
  not every helper module

## Risks / Mitigations
- Risk: over-documenting low-signal helper files.
  Mitigation: require direct architecture or runtime leverage before widening.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- whether utilities drift is mostly graph coverage or mostly narrative/component drift

## Decision Log
- 2026-06-12: keep `utilities` ready behind the higher-leverage runtime lanes.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - utilities directory drift
  - synchronization/logger/interface coherence
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-06-12T13:00:58Z
  TYPE: PLAN
  CLAIM: `utilities` is a meaningful directory lane, but it should stay behind
    `aether` and likely `nexus` because those directories dominate the current
    runtime architecture drift story.
  EVIDENCE:
  - src/melder/utilities: directory inventory
  - codex/context_compass/system_docs/src_components.md
  IMPACT: This story is parked in ready state and can be activated once the
    higher-leverage runtime lanes are under control.
  NEXT: keep this story ready and create a first child task only after the
    earlier lanes expose a utilities-specific drift seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

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
This story defines the `utilities` directory drift lane and keeps it ready for
later routing once the higher-leverage runtime directories are explored first.
