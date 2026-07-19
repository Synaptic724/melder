# architecture_patch

## Metadata
- Patch ID: mr_emission_lock_and_lane_governance_2026_07_18
- Status: implemented (promotion pass; code landed under the 2026-07-17 MR audit epic)
- Owner: cowork (helper_f2)
- Created: 2026-07-18T17:05:00Z
- Updated: 2026-07-18T17:05:00Z

## Patch Scope and Non-Goals
- Objective: promote the two architecture-grade deltas from the MutationResearch audit
  remediation (EPIC-2026-07-17-bugfix-mutation-research) into canonical system docs:
  (BUG-031) the root emission lock and its extended one-way lock order, and (BUG-048)
  set-governed lane mutation (single-residence law made structurally unbypassable).
- Non-goals: the other 22 audited fixes (behavior-level, no boundary/invariant change);
  any new code change - this patch documents landed, sandbox-validated behavior.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| MutationResearch Root | modify | BUG-031: composition emission raced set creation/hydration | none |
| MutationResearch ResearchSet Package (ResearchLane) | modify | BUG-048: public lane mutators bypassed set governance | none |

## Interface and Boundary Deltas
- ResearchLane public surface SHRANK: `add_node`/`detach_nodes`/`set_anchor`/`mark_joined`/
  `mark_archived` are now set-internal `_`-prefixed mutators. Publicly returned lane objects
  are read surfaces; all state change flows through `ResearchSet` verbs.
- MutationResearch root gained a dedicated `_emission_lock` (RLock, owned, deleted in
  cleanup before the root lock teardown per del-posture).

## Cross-Component Invariants
- One-way lock order is now: spellbook -> emission -> root -> set -> child/crystallizer.
  The emission lock is NEVER acquired while root/set locks are held EXCEPT via the
  documented emission->root prefix in `create_research_set` / `load_recorded_composition`
  (set constructors fire `on_mutation` while the root lock is held).
- `_emit_research_composition` serializes its entire read-and-publish body under the
  emission lock: a concurrent hydration/creation can no longer interleave a registry swap
  into an in-flight publish (no torn/stale composition reaches the crystallizer).
- Single residence (one SHA in exactly one lane, network-wide) is structurally
  unbypassable from public surfaces: residence claims, journal, snapshot callback, and
  persistence emission all ride the owning set's verbs only.

## Migration and Rollout Order
1. Code landed 2026-07-18 (epic STORY-01); call sites migrated to `_`-mutators in the
   same pass; tests migrated per owner ruling ("update tests please if you changing
   public shape").
2. This patch: canonical doc merge (src_components.md x3 sites), then promote folder to
   patches/completed/.

## Rollback Strategy
- Rollback trigger: owner 3.14t validation red implicating either delta.
- Rollback steps: revert the epic commits for 031/048; restore this doc's before-state
  from git; return this folder to active/ with a REOPEN note.
- Post-rollback verification: sandbox suite + owner pytest rerun.

## Validation Expectations and Evidence Plan
- BUG-031: gated-crystallizer race regression (no publish during hold; monotone counts;
  final==live) - tests/unit/melder/mutation_research/test_mutation_research_root.py.
- BUG-048: public-mutator absence + governed-flow regression -
  tests/unit/melder/mutation_research/research_set/test_research_set.py (+ migrated
  test_research_lane.py / test_grouped_research_node.py).
- Sandbox suite 144/144 green (python3.13 harness); repo pytest on 3.14t: Not run.

## Ticket Coverage Map
- Epic: tickets/epics/2026-07-17_bugfix_mutation_research_epic.md
- Story: STORY-01 (BUG-031), STORY-02 (BUG-048) inside the epic checklist
- Tasks: none (epic-direct remediation)

## Unknowns and Decision Requests
- none

## Context / Handoff Summary
- What changed: emission lock + extended lock order documented; lane governance documented.
- What remains: owner 3.14t validation of the epic; nothing further for this patch.
- Next entrypoint: src_components.md "MutationResearch Root" / "ResearchSet Package".
