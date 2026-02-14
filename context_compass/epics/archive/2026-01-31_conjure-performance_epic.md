# Epic: Conjure performance deep dive and optimization

## Metadata
- Epic ID: EPIC-2026-01-31-conjure-performance
- Status: draft
- Owner:
- Priority: p0
- Created: 2026-01-31
- Updated: 2026-01-31
- Target Window: 2026-Q1
- Related Program/Initiative:

## Problem / Opportunity
Conjure time is high relative to the object graph size in the depth9 benchmark.
Latest profile shows ~207ms conjure with ~58ms in occurrence_plan and large
allocation counts in Phase 5 socket path creation. We need to keep all Phase
5-11 artifacts built during conjure while removing duplication and waste.

## MRP Alignment (Most Reasonable Product)
Reduce conjure overhead while preserving full pre-built resolution artifacts.
This keeps Melder trustworthy as a dependency graph runtime without shifting
work into meld or weakening validation/override behavior.

## Goals (Outcomes)
- Explain and quantify all major conjure allocation sources with evidence.
- Remove duplication in Phase 5-11 builds while keeping artifacts built at conjure.
- Improve conjure performance for depth9 benchmark without changing outputs.

## Non-Goals (Explicit Exclusions)
- Deferring Phase 8-11 work to meld.
- Changing public APIs or resolution semantics.

## Scope Boundaries
- In scope:
  - Phase 5-11 build pipeline in conjure.
  - Blueprint/socket/index/plan builders.
  - Benchmark instrumentation under `benchmarks/conjure/`.
- Out of scope:
  - Meld runtime changes.
  - External DI framework comparisons.

## Success Metrics
- Reduce depth9 conjure time. Target threshold to be confirmed with user.
- Reduce socket_path allocation count for depth9 conjure.

## Requirements (Functional + Non-Functional)
- All artifacts still built during conjure.
- Same outputs and behavior as current implementation.
- Evidence-based documentation of changes and new measurements.

## Constraints / Assumptions
- Conjure must remain the sole build point for Phase 5-11 artifacts.
- No new runtime dependencies on meld for plan building.

## Dependencies / External References
- `benchmarks/testing_other_di/test_melder_hotpath_profiles.py`
- `tests/mocks/spellbook/deep_layers.py`
- `src/melder/spellbook/spell_crafter/*`

## Milestones (Track Progress)
- [ ] Milestone 1: Measurement and root-cause inventory complete
- [ ] Milestone 2: Phase 5-11 duplication reductions implemented and validated

## Stories (Required to Complete)
- [ ] Story: STORY-2026-01-31-conjure-measurement - Instrumentation and evidence
- [ ] Story: STORY-2026-02-xx-conjure-phase5-dedupe - Phase 5 dedupe work
- [ ] Story: STORY-2026-02-xx-conjure-phase8-11-optimizations - Plan builders

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Maintain `benchmarks/conjure/conjure_performance_strategy.md`
- [ ] Task: Add benchmark harnesses with deterministic count assertions
- [ ] Task: Track allocation deltas per iteration

## Acceptance Criteria (Epic Done)
- Evidence-backed explanation for conjure allocation sources.
- All planned optimizations implemented without deferring to meld.
- Benchmarks demonstrate measurable conjure improvement.

## Risks / Mitigations
- Risk: Breaking override targeting semantics.
  - Mitigation: Explicit tests around SocketRef paths and patch maps.
- Risk: Hidden dependency on per-spell blueprints.
  - Mitigation: Map blueprint consumers and add regression tests.

## Validation / Test Approach
- Pytest benchmarks under `benchmarks/conjure/` with deterministic assertions.
- Use existing hotpath profiles for before/after comparison.

## Rollout / Adoption Plan
- Land measurement harness first.
- Apply Phase 5 dedupe and validate.
- Apply Phase 8-11 optimizations and validate.

## Open Questions
- Exact target conjure time threshold (needs user confirmation).
- Which blueprint consumers require per-spell DAG identity guarantees.

## Decision Log
- 2026-01-31: Conjure must build all Phase 5-11 artifacts (no deferral).

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
- Created epic to track conjure performance investigation and optimizations.
- Strategy doc lives at `benchmarks/conjure/conjure_performance_strategy.md`.
- Next step: add measurement harness and validate path/blueprint counts.
