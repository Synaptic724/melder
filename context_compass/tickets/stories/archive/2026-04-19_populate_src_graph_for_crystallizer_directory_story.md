# Story: Populate Src Graph For Crystallizer Directory

## Metadata
- Story ID: STORY-2026-04-19-populate-src-graph-for-crystallizer-directory
- Epic: EPIC-2026-04-19-populate-src-graph-for-melder-repo
- Status: review
- Owner: codex
- Priority: p2
- Created: 2026-04-19T19:36:46Z
- Updated: 2026-04-19T21:30:41Z

## User Narrative
As the graph maintainer, I want the `src/melder/crystallizer` subtree
represented in `src_graph.json`, so any important crystallizer-side objects are
not omitted from the repo graph.

## Value / MRP Alignment
`crystallizer` appears smaller than the other top-level source directories, so
it should be captured after the heavier runtime and infrastructure stories.

## Ticket Contract
- ENTRY_GATE: the repo-level graph epic is active.
- EXECUTION_BOUNDARY:
  - `src/melder/crystallizer/**`
  - `codex/context_compass/system_docs/src_graph.json`
- DEPENDENCIES:
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
- EXIT_GATE: important crystallizer-side objects and relationships are
  populated in `src_graph.json`.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the subtree is too small or
  too low-signal to justify more than a minimal story.

## Acceptance Criteria
- `crystallizer` is either represented sufficiently in the graph or explicitly
  documented as a minimal/low-signal subtree.

## Notes
- DATETIME: 2026-04-19T19:36:46Z
  TYPE: PLAN
  CLAIM: `crystallizer` should be kept as its own story so the repo-level lane
    stays complete, but it is intentionally lower priority until the heavier
    runtime directories are populated.
  EVIDENCE:
  - src/melder/crystallizer: directory inventory
  IMPACT: This story stays ready and may close quickly if the subtree proves
    small.
  NEXT: keep this story ready for later activation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-19T21:30:41Z
  TYPE: DECISION
  CLAIM: `crystallizer` is now the active top-level lane because the
    `utilities` story is coherent enough to pause. The subtree appears small
    enough that the likely honest outcome is either a minimal graph addition or
    an explicit low-signal closure.
  EVIDENCE:
  - tickets/tasks/2026-04-19_populate_src_graph_for_utilities_first_tranche_task.md: latest coherence decision
  - src/melder/crystallizer: subtree inventory
  IMPACT: The repo graph lane can finish the last top-level directory without
    inventing unnecessary follow-on work.
  NEXT: start the first `crystallizer` tranche task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T21:30:41Z
  TYPE: DECISION
  CLAIM: The `crystallizer` story is review-ready as an explicit low-signal
    closure. The subtree currently has no implemented runtime objects worth
    graphing beyond an empty `__init__.py` and one directional prose `info`
    file, so no graph nodes were added.
  EVIDENCE:
  - tickets/tasks/2026-04-19_populate_src_graph_for_crystallizer_first_tranche_task.md: review state
  - src/melder/crystallizer/info:1-10
  IMPACT: The repo graph lane now has an evidence-backed outcome for the final
    top-level source directory without inventing fake implementation nodes.
  NEXT: keep the story in review unless real crystallizer implementation files
    land later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story owns the manual population of `src_graph.json` for
`src/melder/crystallizer/**`.
