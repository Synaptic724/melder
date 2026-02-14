# Task: Optimize conjure occurrence-plan hot spots (queue, DagIndex keys, DFS allocations)

## Metadata
- Task ID: TASK-2026-01-31-conjure-occurrence-plan-hotspots
- Story: N/A
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-01-31
- Updated: 2026-01-31

## Objective
Reduce conjure build time by removing known O(n^2) and high-allocation hot spots
in Phase 8 and related indexing without changing resolution semantics.

## Scope Boundaries
- In scope:
  - Make Phase 8 execution-order build O(n) by eliminating list pop(0).
  - Change DagIndex path keys to tuple-based keys to avoid join allocations.
  - Reduce DFS path list allocations in CircularDependencyStrategy.
  - Avoid duplicate queue entries during occurrence graph expansion.
  - Avoid empty per-occurrence override dict allocations and guard injection lookups.
  - Add targeted benchmarks/conjure tests to guard behavior.
- Out of scope:
  - Changing override semantics, Existence.many semantics, or meld-time behavior.
  - Deferring conjure work to meld (partial compute strategy).
  - Broad refactors across spell_crafter phases.

## Steps / Checklist
- [x] Update OccurrencePlanBuilder execution-order queue to O(n) traversal.
- [x] Update DagIndex exact-path keying to use tuples (avoid string joins).
- [x] Replace DFS path list allocation in CircularDependencyStrategy with push/pop.
- [x] Avoid duplicate queue entries during occurrence graph expansion.
- [x] Avoid empty per-occurrence override dict allocations and guard injection lookups.
- [x] Add benchmark-conjure tests covering execution order + DagIndex path lookup.
- [x] Use topology when present and fall back to DAG only when topology is missing.
- [ ] Document validation status and results.

## Deliverables
- Code changes in Phase 8 execution ordering, DagIndex, and circular dependency validation.
- Benchmark-conjure tests covering the adjusted behavior.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- `src/melder/spellbook/spell_crafter/dag/dag_index.py`
- `src/melder/spellbook/spell_crafter/validation/strategies/circular_dependency_strategy.py`
- `benchmarks/conjure/`

## Validation
- Not run.
- Recommended commands:
  - `pytest benchmarks/conjure`

## Risks / Rollback Notes
- Risk: Changing DagIndex keying could break override lookup if callers rely on
  string-joined keys.
- Mitigation: Keep public API unchanged (accepts Sequence[str]) and normalize
  to tuple; add tests for list/tuple lookups.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Implemented the agreed hot-spot fixes (O(n) execution order in Phase 8,
tuple-based DagIndex path keys, DFS path push/pop) and added two more:
duplicate-queue suppression in occurrence graph expansion plus removal of
empty per-occurrence override dict allocations with guarded injection lookups.
Added benchmark tests in `benchmarks/conjure/test_conjure_hotspot_fixes.py`,
including topology-vs-DAG fallback behavior in Phase 8 occurrence planning.
Validation not run.
