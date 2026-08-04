<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner hope_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Epic: Investigate Source System Doc Drift Excluding Mutation And Crystallizer

## Metadata
- Epic ID: EPIC-2026-06-12-investigate-source-system-doc-drift-excluding-mutation-and-crystallizer
- Status: in_progress
- Owner: codex
- Agent Name: hope_0
- Priority: p0
- Created: 2026-06-12T12:32:32Z
- Updated: 2026-06-12T12:32:32Z
- Target Window: 2026-06
- Related Program/Initiative: source-system documentation coherence refresh

## Problem / Opportunity
The current canonical source-system docs are large and clearly lived-in, but the
user believes they have drifted enough that we should stop routing through the
old graph/doc tickets and start a fresh investigation lane. We also now know
the older 2026-04 graph-population tickets are stale reference work rather than
the right execution surface for today's documentation drift.

## MRP Alignment (Most Reasonable Product)
The MRP is not a rewrite-for-style and not a repo-wide prose churn pass. It is:
- one fresh epic for current doc drift
- bounded investigation against live code and current system docs
- explicit mismatch inventory for `src_architecture`, `src_components`,
  `graph_details_document`, `readable_src_graph`, and `src_graph`
- follow-on patch slices only where drift is directly evidenced

## Ticket Contract
- ENTRY_GATE: the stale non-mutation/non-crystallizer doc/graph tickets were
  closed, and this epic is now the clean replacement lane for current
  documentation drift.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `codex/context_compass/system_docs/graph_details_document.md`
  - `codex/context_compass/system_docs/readable_src_graph.json`
  - `codex/context_compass/system_docs/src_graph.json`
  - live `src/melder/**` code needed to verify drift
  - excluding mutation-research and crystallizer-specific doc/code claims
- DEPENDENCIES:
  - `codex/context_compass/tickets/tasks/completed/2026-04-10_refresh_src_architecture_and_components_for_recent_rift_and_meld_changes.md`
  - `codex/context_compass/tickets/tasks/completed/2026-05-22_synthesize_mutationresearch_aethericrift_crystallizer_context_task.md`
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `codex/context_compass/system_docs/graph_details_document.md`
  - `codex/context_compass/system_docs/readable_src_graph.json`
  - `codex/context_compass/system_docs/src_graph.json`
- EXIT_GATE:
  - the current drift set is explicitly inventoried with evidence
  - follow-on patch slices are ticketed or completed
  - source-system docs are either refreshed or left with explicit UNKNOWN /
    follow-up boundaries
- FAILURE_ESCALATION: raise `DECISION_REQUEST` or `CONFLICT` if the drift lane
  expands into mutation/crystallizer architecture or into a repo-wide rewrite.

## Goals (Outcomes)
- establish one clean execution lane for current source-system doc drift
- inventory live mismatches between docs/graph and code
- refresh only the evidenced drift surfaces
- keep mutation-research and crystallizer out of this lane

## Non-Goals (Explicit Exclusions)
- mutation-research architecture refresh
- crystallizer architecture refresh
- tests-architecture rewrite unless directly required later
- runtime code edits unrelated to document truth verification

## Scope Boundaries
- In scope:
  - current drift in source-system docs and graph surfaces
  - live code verification in non-mutation/non-crystallizer areas
  - new tickets spawned from that drift inventory
- Out of scope:
  - mutation-research and crystallizer doc claims
  - unrelated closed historical tickets
  - style-only prose rewrites

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked for a new epic and a fresh
  drift-investigation lane after stale doc/graph tickets were cleaned up.

## Success Metrics
- one active investigation task routes the lane cleanly
- concrete drift inventory exists with evidence pointers
- stale old graph/doc tickets are no longer the active execution surface

## Requirements (Functional + Non-Functional)
- functional:
  - compare current docs/graph against live code
  - identify and record concrete drift
  - patch only directly evidenced drift
- non-functional:
  - preserve ticket/board coherence
  - keep scope bounded away from mutation/crystallizer
  - maintain readable, evidence-backed handoff state

## Constraints / Assumptions
- mutation-research and crystallizer are explicitly excluded by the user
- old graph/doc tickets should be treated as references, not active lanes
- the current active role is `design_engineer`

## Dependencies / External References
- `codex/context_compass/system_docs/src_architecture.md`
- `codex/context_compass/system_docs/src_components.md`
- `codex/context_compass/system_docs/graph_details_document.md`
- `codex/context_compass/system_docs/readable_src_graph.json`
- `codex/context_compass/system_docs/src_graph.json`

## Milestones (Track Progress)
- [ ] Milestone 1: Drift inventory completed with evidence-backed mismatch list.
- [ ] Milestone 2: First bounded doc/graph refresh slice completed or explicitly ticketed.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-06-12-investigate-aether-directory-doc-drift - investigate meaningful `aether/**` doc and graph drift first
- [ ] Story: STORY-2026-06-12-investigate-nexus-directory-doc-drift - investigate meaningful `nexus/**` doc and graph drift second
- [ ] Story: STORY-2026-06-12-investigate-utilities-directory-doc-drift - investigate meaningful `utilities/**` drift after the runtime lanes

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: TASK-2026-06-12-investigate-current-source-system-doc-drift
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- a fresh drift inventory exists
- stale historical graph/doc tickets are retired
- active work is routed through new evidence-backed tickets instead of old lanes

## Risks / Mitigations
- Risk: the lane broadens into excluded mutation/crystallizer work.
  Mitigation: treat those areas as explicit out-of-scope boundaries unless the
  user redirects.
- Risk: the docs are broad enough that drift classification becomes vague.
  Mitigation: require file/symbol evidence before promoting drift claims.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story/task evidence.
- [ ] No closure while required drift inventory is incomplete.
- [ ] No architecture claims without direct source evidence.

## Validation / Test Approach
- validation is documentation- and consistency-based:
  - source evidence pointers
  - section/contract conformance checks
  - graph JSON validity when graph edits occur

## Rollout / Adoption Plan
- start with one investigation task
- split follow-on refresh tasks only if the inventory proves separate slices

## Open Questions
- whether the first patch slice should start with `src_architecture` or
  `src_components`
- whether the graph surfaces have structural drift or only narrative drift

## Decision Log
- 2026-06-12: old non-mutation/non-crystallizer graph-population tickets were
  retired as stale reference lanes; a new epic is the clean replacement.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - source-system documentation drift
  - architecture/components/graph coherence
  - exclude mutation_research and crystallizer
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-06-12T12:32:32Z
  TYPE: DECISION
  CLAIM: The old graph/doc tickets are now reference-only. The active lane
    should be a fresh epic focused on current documentation drift in the live
    source-system docs, explicitly excluding mutation-research and
    crystallizer.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-06-12_cleanup_non_mutation_crystallizer_active_lanes_task.md:1-120
  - codex/context_compass/tickets/tasks/completed/2026-04-10_refresh_src_architecture_and_components_for_recent_rift_and_meld_changes.md:1-40
  IMPACT: Future doc work now has one clean umbrella instead of spreading
    across stale graph-population tickets.
  NEXT: start the first bounded investigation task and inventory live drift.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-task tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic replaces the old stale graph/doc lanes for current source-system
documentation drift. The first active work is a bounded investigation task, not
an immediate repo-wide rewrite.
