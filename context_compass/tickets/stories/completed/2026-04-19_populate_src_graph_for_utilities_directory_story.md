Completed: 2026-06-12T12:29:40Z
Summary: Closed as a stale graph-population reference lane. The historical
utilities graph notes are retained, but the active lane is being replaced by a
fresh documentation-drift investigation.

# Story: Populate Src Graph For Utilities Directory

## Metadata
- Story ID: STORY-2026-04-19-populate-src-graph-for-utilities-directory
- Epic: EPIC-2026-04-19-populate-src-graph-for-melder-repo
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-19T19:36:46Z
- Updated: 2026-06-12T12:29:40Z

## User Narrative
As the graph maintainer, I want the `src/melder/utilities` subtree represented
in `src_graph.json`, so shared base types, helpers, logging, synchronization,
and interfaces can be traversed from the same graph.

## Value / MRP Alignment
`utilities` is shared infrastructure. It is important, but it should come after
the first high-value runtime stories.

## Ticket Contract
- ENTRY_GATE: the repo-level graph epic is active.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/**`
  - `codex/context_compass/system_docs/src_graph.json`
- DEPENDENCIES:
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
- EXIT_GATE: important utility-layer objects and their semantic relationships
  are populated in `src_graph.json`.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the utilities graph becomes
  too low-signal to justify broad inclusion.

## Acceptance Criteria
- utility-layer graph population is materially useful.
- important shared helpers and interfaces are represented without flooding the
  graph with low-value nodes.

## Notes
- DATETIME: 2026-04-19T19:36:46Z
  TYPE: PLAN
  CLAIM: `utilities` should be graphed after the main runtime stories because
    it is mostly supporting infrastructure rather than the primary runtime/AR
    object model.
  EVIDENCE:
  - src/melder/utilities: directory inventory
  IMPACT: This story should stay selective and focus on shared objects that
    materially affect runtime understanding.
  NEXT: keep this story ready for later activation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T20:38:07Z
  TYPE: DECISION
  CLAIM: The `utilities` story is now the active top-level lane because the
    `spellbook` story is coherent enough to pause. The first `utilities`
    tranche should stay narrowly focused on shared base contracts and
    synchronization primitives before widening into broader helper coverage.
  EVIDENCE:
  - tickets/tasks/2026-04-19_populate_src_graph_for_spellbook_second_tranche_task.md: latest coherence decision
  - src/melder/utilities: directory inventory
  IMPACT: The repo graph lane can now make the current runtime/spellbook graph
    more self-contained by adding the utility contracts it already depends on.
  NEXT: start the first `utilities` tranche task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T21:30:41Z
  TYPE: DECISION
  CLAIM: The first `utilities` tranche is coherent enough to pause in review.
    It now covers the shared lifecycle contract, the runtime-facing protocol
    slices, the synchronization/gate/scheduler primitives, and the helper/id/
    logger surfaces that the current runtime graph already depends on. Going
    deeper immediately would mostly add low-signal utility inventory.
  EVIDENCE:
  - tickets/tasks/2026-04-19_populate_src_graph_for_utilities_first_tranche_task.md: latest note stack
  - codex/context_compass/system_docs/readable_src_graph.json: current utility graph coverage
  IMPACT: The repo graph lane can move to the final top-level source directory
    instead of overfitting the utilities tree.
  NEXT: activate a minimal `crystallizer` tranche and decide whether that
    directory needs any graph nodes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story owns the manual population of `src_graph.json` for
`src/melder/utilities/**`.
