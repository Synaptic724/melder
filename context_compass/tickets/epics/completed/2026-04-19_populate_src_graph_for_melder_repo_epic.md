# Epic: Populate Src Graph For Melder Repo
- Completed: 2026-04-24T01:03:27Z
- Summary: Closed during the 2026-04-24 cleanup after the exhaustive graph package landed and later work moved on from graph population.

## Metadata
- Epic ID: EPIC-2026-04-19-populate-src-graph-for-melder-repo
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T19:36:46Z
- Updated: 2026-04-24T01:03:27Z
- Target Window: 2026-04
- Related Program/Initiative: machine-first system graph population

## Problem / Opportunity
The graph workflow and schema now exist, but `src_graph.json` still contains
only a starter set of nodes and edges. The next lane is to populate the real
source-runtime relationship map for `src/melder` by hand, using the canonical
expand-edit-compress workflow and the existing architecture/components docs as
the long-form semantic source.

Right now:
- the graph workflow contract is implemented
- the graph is scoped to `src/` only
- `__init__.py` files and `tests/` are explicitly excluded
- but the actual repo graph still needs deliberate manual population

## MRP Alignment (Most Reasonable Product)
The MRP is not a full-repo file inventory and not a fake import graph.

It is:
- one repo-level graph-population lane
- one story per top-level source directory under `src/melder`
- hand-authored semantic nodes and edges that eventually cover every
  non-`__init__.py` source file in scope
- steady expansion until `src_graph.json` becomes a trustworthy full-source
  relationship map

## Ticket Contract
- ENTRY_GATE: the graph schema and compressed-storage workflow are already
  implemented and the user explicitly requested that the full codebase
  population lane begin now.
- EXECUTION_BOUNDARY:
  - `src/melder/**`
  - `codex/context_compass/system_docs/src_graph.json`
  - `codex/context_compass/system_docs/patches/active/*/src_graph.expanded.json`
  - graph-population tickets and board state
- DEPENDENCIES:
  - `codex/context_compass/system_docs/graph_details_document.md`
  - `codex/context_compass/system_docs/src_graph.json`
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
- EXIT_GATE: all non-`__init__.py` source files that are in scope for the
  graph contract are represented in `src_graph.json`, or explicitly excluded
  by documented rule.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the graph node set widens
  beyond useful system-significant objects into low-signal file inventory noise.

## Goals (Outcomes)
- Populate the graph for `src/melder` by hand.
- Organize that work per top-level source directory.
- Keep graph population aligned with architecture/components docs.
- Maintain compressed-storage discipline while the graph grows.

## Non-Goals (Explicit Exclusions)
- Graphing `tests/`
- Graphing `__init__.py` files
- CI or codegen automation for graph generation
- Runtime code changes in `src/`

## Scope Boundaries
- In scope:
  - `src/melder/aether/**`
  - `src/melder/crystallizer/**`
  - `src/melder/spellbook/**`
  - `src/melder/utilities/**`
  - graph population in `src_graph.json`
- Out of scope:
  - `tests/**`
  - examples and tickets as graph nodes
  - broad import-graph capture

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested the repo-level graph
  population lane and directed work to begin now.

## Success Metrics
- One story exists for each top-level source directory under `src/melder`.
- The active work can progress directory by directory without losing graph
  population continuity.
- `src_graph.json` grows through evidence-backed manual population instead of
  ad hoc edits.

## Requirements (Functional + Non-Functional)
- Story partitioning must follow the top-level source directory layout.
- Graph population must remain manual and semantic.
- Graph updates must use the documented expand-edit-compress workflow.
- Architecture/components docs remain the canonical narrative source.

## Constraints / Assumptions
- `src_graph.json` is source-only and excludes `tests/`.
- `__init__.py` files remain excluded from graph nodes.
- All non-`__init__.py` source files are now target candidates unless later
  excluded by explicit documented rule.

## Dependencies / External References
- `codex/context_compass/system_docs/graph_details_document.md`
- `codex/context_compass/system_docs/src_graph.json`
- `codex/context_compass/system_docs/src_architecture.md`
- `codex/context_compass/system_docs/src_components.md`

## Milestones (Track Progress)
- [ ] Milestone 1: seed top-level story/task structure for the repo graph lane
- [ ] Milestone 2: complete `aether` story
- [ ] Milestone 3: complete `spellbook` story
- [ ] Milestone 4: complete `utilities` story
- [ ] Milestone 5: complete `crystallizer` story

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-19-populate-src-graph-for-aether-directory
- [ ] Story: STORY-2026-04-19-populate-src-graph-for-spellbook-directory
- [ ] Story: STORY-2026-04-19-populate-src-graph-for-utilities-directory
- [ ] Story: STORY-2026-04-19-populate-src-graph-for-crystallizer-directory

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: complete directory stories in sequence and keep `src_graph.json`
      coherent during each tranche
- [ ] Task: keep ticket notes and board state synchronized as the graph grows

## Acceptance Criteria (Epic Done)
- All four top-level source-directory stories are accepted.
- `src_graph.json` contains a materially useful relationship map for the
  important source-runtime objects across `src/melder`.

## Risks / Mitigations
- Risk: the graph turns into a low-signal file inventory.
  Mitigation: enforce selective node inclusion and semantic edges only.
- Risk: graph population drifts from architecture/components docs.
  Mitigation: treat docs as the canonical narrative and patch the graph only
  from evidenced relationships.

## Validation / Test Approach
- JSON parse validation for the canonical graph after each tranche.
- Ticket-note evidence review for semantic graph changes.

## Rollout / Adoption Plan
- Start with `aether`.
- Move through `spellbook`, `utilities`, and `crystallizer`.
- Keep one active task at a time while the repo graph grows.

## Open Questions
- Whether `crystallizer` has enough system-significant objects to justify more
  than a small story.

## Decision Log
- 2026-04-19T19:36:46Z: structure the graph-population lane as one repo epic
  and one story per top-level source directory under `src/melder`.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-19T19:36:46Z
  TYPE: FACT
  CLAIM: The real top-level source directories under `src/melder` are
    `aether`, `crystallizer`, `spellbook`, and `utilities`. Those are the
    natural top-level story boundaries for the repo graph lane.
  EVIDENCE:
  - src/melder: directory inventory
  IMPACT: We can keep the graph-population lane bounded and navigable by using
    one story per top-level source directory instead of trying to fan out the
    whole repo at once.
  NEXT: create the four top-level directory stories and route the first active
    task to the `aether` story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T21:30:41Z
  TYPE: DECISION
  CLAIM: The repo-level graph population epic is now review-ready. All four
    top-level source-directory stories have evidence-backed outcomes:
    - `aether`: review-ready with substantive runtime/AR coverage
    - `spellbook`: review-ready with substantive bind/graph/plan coverage
    - `utilities`: review-ready with shared contract/synchronization/helper coverage
    - `crystallizer`: review-ready as an explicit low-signal no-node closure
  EVIDENCE:
  - tickets/stories/2026-04-19_populate_src_graph_for_aether_directory_story.md: review state
  - tickets/stories/2026-04-19_populate_src_graph_for_spellbook_directory_story.md: review state
  - tickets/stories/2026-04-19_populate_src_graph_for_utilities_directory_story.md: review state
  - tickets/stories/2026-04-19_populate_src_graph_for_crystallizer_directory_story.md: review state
  IMPACT: The manual repo graph lane is complete enough for review rather than
    further active expansion.
  NEXT: hold the epic in review until the user accepts the current graph or
    requests another bounded follow-on lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T21:30:41Z
  TYPE: DECISION
  CLAIM: The previous review-ready state was premature for the user's actual
    target. The real target is exhaustive non-`__init__.py` `src/` coverage,
    and the current graph only covers 78 of 278 eligible files, leaving 200
    files unrepresented. The lane is therefore reopened around exhaustive gap
    fill from the existing baseline.
  EVIDENCE:
  - coverage_measure: graph file count = 78
  - coverage_measure: source file count = 278
  - coverage_measure: missing file count = 200
  - tickets/tasks/2026-04-19_resume_src_graph_exhaustive_gap_fill_from_baseline_task.md: active follow-on task
  IMPACT: The repo graph lane returns to active implementation and should now
    advance through explicit missing-file tranches instead of treating the
    selective baseline as complete.
  NEXT: route active work through the exhaustive gap-fill task and land the
    first missing-file tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T22:37:16Z
  TYPE: DECISION
  CLAIM: The repo-level graph population epic is now genuinely review-ready.
    After the resumed exhaustive gap-fill lane, the graph covers all 278
    eligible non-`__init__.py` files under `src/melder`; no in-scope source
    files remain uncovered.
  EVIDENCE:
  - tickets/tasks/2026-04-19_resume_src_graph_exhaustive_gap_fill_from_baseline_task.md: review state
  - coverage_measure: graph file count = 278
  - coverage_measure: source file count = 278
  - coverage_measure: missing file count = 0
  IMPACT: The repo graph lane now meets the clarified exhaustive-coverage
    target instead of the earlier selective baseline.
  NEXT: hold the epic in review until the user accepts the current graph
    package or requests semantic refinements beyond file coverage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Context / Handoff Summary
This epic owns the full manual population of `src_graph.json` for `src/melder`
using one story per top-level source directory.
