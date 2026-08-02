Completed: 2026-06-12T12:29:40Z
Summary: Closed as a stale graph-population reference lane. The existing notes
remain as historical context, but future graph/doc work now routes through a
fresh drift-investigation lane.

# Story: Populate Src Graph For Spellbook Directory

## Metadata
- Story ID: STORY-2026-04-19-populate-src-graph-for-spellbook-directory
- Epic: EPIC-2026-04-19-populate-src-graph-for-melder-repo
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T19:36:46Z
- Updated: 2026-06-12T12:29:40Z

## User Narrative
As the graph maintainer, I want the `src/melder/spellbook` subtree represented
in `src_graph.json`, so spell binding, spell crafter, and local graph/runtime
relationships are traversable from one machine-first map.

## Value / MRP Alignment
`spellbook` is the second major runtime pillar after `aether`, and it contains
the dependency-graph build path that the graph file should explain well.

## Ticket Contract
- ENTRY_GATE: the repo-level graph epic is active.
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/**`
  - `codex/context_compass/system_docs/src_graph.json`
- DEPENDENCIES:
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
- EXIT_GATE: important `spellbook` objects and their semantic relationships are
  populated in `src_graph.json`.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if spellbook graph population
  widens into exhaustive file inventory noise.

## Acceptance Criteria
- `spellbook` graph population is materially useful.
- Important binding, graph, validation, and execution objects are represented.

## Notes
- DATETIME: 2026-04-19T19:36:46Z
  TYPE: PLAN
  CLAIM: `spellbook` is the second directory story because it contains the
    binding and graph-build pipeline that complements the runtime substrate in
    `aether`.
  EVIDENCE:
  - src/melder/spellbook: directory inventory
  IMPACT: This story will likely define the heaviest graph/validation edges
    after the `aether` story establishes the runtime/AR roots.
  NEXT: leave this story ready and activate it after the first `aether` tranche
    is stable.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:16:31Z
  TYPE: DECISION
  CLAIM: The `spellbook` story is now the active top-level lane because the
    `aether` story is coherent enough to pause. The first `spellbook` tranche
    should focus on the root binding and graph-build objects before widening to
    deeper leaf helpers.
  EVIDENCE:
  - tickets/tasks/2026-04-19_populate_src_graph_for_aether_second_tranche_task.md: latest decision note
  IMPACT: The repo graph lane can keep moving top-down instead of overfitting
    the `aether` subtree.
  NEXT: start the first `spellbook` tranche task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:29:57Z
  TYPE: DECISION
  CLAIM: The first `spellbook` tranche is now coherent enough to pause in
    review. It covers the spellbook root, bind/spell/spell-index chain,
    SpellCrafter ownership, the Phase 1-3 artifact family, the runtime
    `ResolutionFrame` correction, and the first rooted/conjure-side planning
    seams (`SpellbookCreationSystem`, `SpellValidationSystem`,
    `SpellLocalTopology`, `RootResolutionBlueprint`, `SpellSystemIndex`).
  EVIDENCE:
  - tickets/tasks/2026-04-19_populate_src_graph_for_spellbook_first_tranche_task.md: latest note stack
  - codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json: current spellbook graph shape
  IMPACT: The story can keep moving through a second spellbook tranche instead
    of bloating the first one past a useful review boundary.
  NEXT: activate the second `spellbook` tranche for the deeper planning and
    system-validation object family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:38:07Z
  TYPE: DECISION
  CLAIM: The second `spellbook` tranche is now coherent enough to pause in
    review too. Between the first and second tranches the story now covers:
    - the bind/spell/spell-index ownership chain
    - the Phase 1-3 artifact family and runtime ResolutionFrame correction
    - the conjure orchestration seam
    - the retained Phase 5 rooted-system layer
    - the retained Phase 8-11 plan layer
    - the system-validation orchestrator, diagnostics, and validation state
    Continuing deeper in `spellbook` right now would mostly widen into
    builders, strategy leafs, or executor internals instead of materially
    improving the top-level system map.
  EVIDENCE:
  - tickets/tasks/2026-04-19_populate_src_graph_for_spellbook_first_tranche_task.md: latest note stack
  - tickets/tasks/2026-04-19_populate_src_graph_for_spellbook_second_tranche_task.md: latest note stack
  - codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json: current spellbook graph shape
  IMPACT: The repo graph lane can now move on to `utilities` without leaving
    the spellbook story half-explained.
  NEXT: activate the first `utilities` tranche around the base contracts and
    synchronization primitives the current graph already depends on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story owns the manual population of `src_graph.json` for
`src/melder/spellbook/**`.
