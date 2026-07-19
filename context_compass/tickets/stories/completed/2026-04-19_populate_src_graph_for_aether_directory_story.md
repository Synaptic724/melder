Completed: 2026-06-12T12:29:40Z
Summary: Closed as a stale graph-population reference lane. Its graph-building
notes remain useful historically, but current work is moving to a fresh
documentation-drift investigation epic.

# Story: Populate Src Graph For Aether Directory

## Metadata
- Story ID: STORY-2026-04-19-populate-src-graph-for-aether-directory
- Epic: EPIC-2026-04-19-populate-src-graph-for-melder-repo
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T19:36:46Z
- Updated: 2026-06-12T12:29:40Z

## User Narrative
As the graph maintainer, I want the `src/melder/aether` subtree represented in
`src_graph.json`, so the source-runtime substrate and AR relationship map can
be traversed without rereading the full architecture docs every time.

## Value / MRP Alignment
`aether` contains the heaviest runtime substrate and AR ownership model, so it
is the highest-value first story in the repo graph lane.

## Ticket Contract
- ENTRY_GATE: the repo-level graph epic is active and `aether` is the first
  top-level directory selected for population.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/**`
  - `codex/context_compass/system_docs/src_graph.json`
  - patch-lane expanded graph working copies
- DEPENDENCIES:
  - `tickets/tasks/2026-04-19_populate_src_graph_for_aether_first_tranche_task.md`
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `codex/context_compass/system_docs/graph_details_document.md`
- EXIT_GATE: important `aether` objects and their semantic relationships are
  populated in `src_graph.json` with evidence-backed task notes covering each
  tranche.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the node set starts slipping
  into low-signal module inventory instead of important system objects.

## Acceptance Criteria
- `aether` graph population is materially useful.
- Important ownership, creation, borrowing, publication, validation, and graph
  relationships are represented for the `aether` subtree.
- JSON validation stays green after each tranche.

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-19-populate-src-graph-for-aether-first-tranche
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during graph population.

## Notes
- DATETIME: 2026-04-19T19:36:46Z
  TYPE: PLAN
  CLAIM: `aether` is the first directory story because it contains both the
    lower runtime substrate and the public AR object graph. Populating it first
    will establish most of the high-value relationship vocabulary for the rest
    of the repo.
  EVIDENCE:
  - src/melder/aether: directory inventory
  - codex/context_compass/system_docs/src_architecture.md: runtime and AR sections
  IMPACT: This story should start with root and high-centrality `aether`
    objects before diving into every subordinate subsystem.
  NEXT: create the first `aether` tranche task and start with root/runtime/AR
    classes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T21:30:41Z
  TYPE: DECISION
  CLAIM: The `aether` story is coherent enough to pause in review. Across the
    two landed tranches it now covers the substrate roots, frame-local
    services, conduit/dev-ops runtime ownership, AR projection/viewer flow,
    descriptor records, contract/detail objects, and the ACL runtime core.
    Additional widening would mostly add low-signal leaf inventory.
  EVIDENCE:
  - tickets/tasks/2026-04-19_populate_src_graph_for_aether_first_tranche_task.md: review state
  - tickets/tasks/2026-04-19_populate_src_graph_for_aether_second_tranche_task.md: review state
  - codex/context_compass/system_docs/readable_src_graph.json: current `aether` coverage
  IMPACT: The repo graph lane can treat `aether` as a review-ready directory
    outcome and move on to the remaining top-level stories.
  NEXT: keep the story in review unless a later source-backed gap requires a
    bounded follow-on tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Context / Handoff Summary
This story owns the manual population of `src_graph.json` for
`src/melder/aether/**`.
