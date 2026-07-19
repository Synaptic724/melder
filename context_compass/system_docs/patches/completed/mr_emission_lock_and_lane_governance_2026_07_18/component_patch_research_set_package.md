# component_patch_research_set_package

## Metadata
- Patch ID: mr_emission_lock_and_lane_governance_2026_07_18
- Component: MutationResearch ResearchSet Package (ResearchLane governance)
- Status: implemented (promotion pass)
- Owner: cowork (helper_f2)
- Created: 2026-07-18T17:05:00Z
- Updated: 2026-07-18T17:05:00Z

## Component Purpose and Boundary
- Current boundary: ResearchSet facade owns lanes, journal, residence, snapshots, and
  the `on_mutation` persistence emission callback.
- Target boundary: unchanged for the set; the LANE boundary shrank (see deltas).

## Before/After Behavior Summary
- Before (BUG-048): `ResearchLane` exposed public mutators (`add_node`, `detach_nodes`,
  `set_anchor`, `mark_joined`, `mark_archived`). Publicly returned lane objects allowed
  direct mutation that bypassed the set's residence claim, journal, snapshot callback,
  and persistence emission - the audit reproduced one identity resident in two lanes
  with `residence=None`.
- After: all five mutators are set-internal (`_add_node`, `_detach_nodes`, `_set_anchor`,
  `_mark_joined`, `_mark_archived`); the lane class docstring carries a
  "Governance (single-residence law)" section. Lanes are handed out LIVE as read
  surfaces; public state change flows through set verbs ONLY.

## Interface Deltas
- Inputs: lane mutator names underscore-prefixed (public shape change, owner-approved
  2026-07-18 "update tests please if you changing public shape"; option (a) set-governed).
- Outputs: unchanged.
- Error semantics: unchanged (set verbs keep their existing refusal contracts).

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- Removed failure mode: split-brain residence (same SHA in multiple lanes with no
  residence claim) constructed through a public lane handle.

## Dependency and Ordering Constraints
1. Set -> lane lock order unchanged (join holds the receiver lane RLock via the
   set-locked `_join_locked` commit - BUG-037, separate delta, already canonical-adjacent).
2. Only the owning ResearchSet calls lane mutators.

## Validation Expectations
- Public-mutator absence + governed-flow regression:
  tests/unit/melder/mutation_research/research_set/test_research_set.py; migrated
  test_research_lane.py / test_grouped_research_node.py call sites.
- Evidence: src/melder/mutation_research/research_set/research_lane.py:386,483,526,570,592.

## Unknowns and Open Decisions
- none

## Context / Handoff Summary
- What changed: lane mutation is set-governed; single residence structurally unbypassable.
- Remaining risks: none known; owner 3.14t run outstanding for the epic as a whole.
- Next entrypoint: src_components.md "ResearchSet Package" ResearchLane bullet.
