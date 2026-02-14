# Task: Investigate and design Phase 12 precompute artifacts for MeldRuntime

## Metadata
- Task ID: TASK-2026-01-29-phase12-precompute-meld-runtime
- Story: STORY-2026-01-29-phase12-precompute-meld-runtime
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-01-29
- Updated: 2026-01-29

## Objective
Investigate MeldEngine/MeldRuntime computations and design Phase 12 artifacts that precompute everything possible (root creations flap map, true spell refs, routing metadata) so runtime execution becomes a minimal assembly step.

## Scope Boundaries
- In scope:
  - Audit MeldEngine.run/run_execution_plan to catalog runtime computations.
  - Identify which computations can be fully precomputed in Phase 12 vs. per-call only.
- Define Phase 12 artifact schema (root creations flap map, true spell refs, override routing, contract/override lookup metadata).
- Draft minimal runtime execution flow with explicit inputs (creations, overrides, cancellation).
- Produce implementation plan + test strategy for Phase 12.
- Include plan variants (no overrides fast path, overrides, overrides+mutations) and selection gates.
- Define optimistic object ref handling and "available" param mapping for creations selection.
- Specify the Phase 12 execution handoff that returns the root instance and delegates creations placement without engine re-planning.
- Out of scope:
  - Implementing Phase 12 artifacts or runtime changes.
  - Performance benchmarking.

## Steps / Checklist
- [ ] Inventory MeldEngine computations (override routing, contract overrides, existence handling, creations selection, instance planning).
- [ ] Map precomputable vs. per-call computations and document boundaries.
- [ ] Define Phase 12 artifact schema and ownership/cleanup contracts.
- [ ] Draft minimal runtime execution function signature and flow.
- [ ] Outline implementation plan + unit tests for Phase 12.
- [x] Confirm implementation direction: Option A (new ExecutionAssemblyPlan), Option D1 (routing table creations delegation), Option E1 (pre-resolved refs with validation).

## Deliverables
- Phase 12 artifact schema proposal with root creations flap map + true spell refs.
- Documented runtime flow showing only minimal per-call computations.
- Implementation plan + test plan for Phase 12.
- Plan variant selection rules and optimistic object-ref/availability contract.
- Execution handoff contract covering root return + creations delegation.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- src/melder/spellbook/spell_crafter/blueprints/execution_plan.py
- src/melder/spellbook/spell_crafter/spell_crafter.py
- context_compass/artifacts/phase12_precompute_meld_runtime/phase12_precompute_audit.md

## Validation
- Not run (analysis-only).

## Risks / Rollback Notes
- Risk: Over-precomputation yields stale or invalid routing when overrides change.
  - Mitigation: keep override payload values runtime-bound; include plan snapshots for gating.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Expanded Phase 12 precompute audit with a method-by-method extraction map (instance routing, creations targeting, lock hints, optimistic ref validation), plus a confirmed direction to pursue Option A (new Phase 12 ExecutionAssemblyPlan), Option D1 (routing table creations delegation), and Option E1 (pre-resolved refs with validation). Phase 11 now selects plan variants by override/mutation presence and MeldRuntime precomputes override targets/flags to remove duplicated override detection as a precursor to Phase 12 plan switching. Phase 12 is intended to finalize execution with root return and creations delegation.
- Implementation started: added Phase 12 ExecutionAssemblyPlan scaffolding + builder, and wired SpellCrafter Phase 12 compilation to emit plan variants.
