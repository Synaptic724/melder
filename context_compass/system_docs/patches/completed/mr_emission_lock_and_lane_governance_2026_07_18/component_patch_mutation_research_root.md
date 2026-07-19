# component_patch_mutation_research_root

## Metadata
- Patch ID: mr_emission_lock_and_lane_governance_2026_07_18
- Component: MutationResearch Root (ResearchSet Registry)
- Status: implemented (promotion pass)
- Owner: cowork (helper_f2)
- Created: 2026-07-18T17:05:00Z
- Updated: 2026-07-18T17:05:00Z

## Component Purpose and Boundary
- Current boundary: Aether-hosted singleton root owning the ResearchSet registry and the
  package's ONLY crystallizer touchpoint (`_emit_research_composition`).
- Target boundary: unchanged - the delta is concurrency-internal.

## Before/After Behavior Summary
- Before (BUG-031): `_emit_research_composition` read the registry and published with no
  serialization against registry replacement. A hydration (`load_recorded_composition`)
  or `create_research_set` racing an in-flight emission could publish a torn or stale
  composition to the crystallizer.
- After: a dedicated `_emission_lock` (RLock, `__slots__` member, created in `__init__`
  before the default set, deleted in cleanup) serializes the whole emission body.
  `create_research_set` and `load_recorded_composition` acquire emission BEFORE root
  because set constructors fire `on_mutation` while the root lock is held.

## Interface Deltas
- Inputs/Outputs: none (no public signature change).
- Error semantics: none.

## State and Lifecycle Deltas
- Owned state: `_emission_lock: threading.RLock` added.
- Lifecycle/cleanup: emission lock deleted in cleanup teardown (del-posture; logger last
  law unchanged).

## Failure Mode Deltas
- Removed failure mode: torn/stale composition publish around registry swap.
- New failure mode: none (RLock; re-entrant; one-way order prevents AB-BA).

## Dependency and Ordering Constraints
1. One-way lock order: spellbook -> emission -> root -> set -> child/crystallizer.
2. Emission is acquired bare on the emit path (set verbs notify AFTER releasing their
   lock) and as the emission->root prefix on the two registry-mutating root paths.

## Validation Expectations
- Gated-crystallizer race regression: nothing publishes during the gate hold, publish
  counts stay monotone, final publish equals live registry
  (tests/unit/melder/mutation_research/test_mutation_research_root.py).
- Evidence: src/melder/mutation_research/mutation_research.py:146,590,668,3380.

## Unknowns and Open Decisions
- none

## Context / Handoff Summary
- What changed: emission serialization; lock-order law extended one hop leftward.
- Remaining risks: none known; owner 3.14t run outstanding for the epic as a whole.
- Next entrypoint: src_components.md "MutationResearch Root" Concurrency/Threading.
