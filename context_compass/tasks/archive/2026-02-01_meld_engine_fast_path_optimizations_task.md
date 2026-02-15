# Task: Optimize MeldEngine fast execution paths

- Completed: 2026-02-03
- Summary: Closed per user request; tests and validation remain pending.

## Metadata
- Task ID: TASK-2026-02-01-meld-engine-fast-path-optimizations
- Story: N/A
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-01
- Updated: 2026-02-03

## Objective
Reduce per-step overhead inside `MeldEngine.run_execution_plan_no_overrides()` by
specializing hot paths and minimizing unused work in the no-overrides case.

## Scope Boundaries
- In scope:
  - Specialize the no-overrides execution loop when `frame` is absent.
  - Defer per-step field loading to only the branches that require them.
  - Precompute direct dependency indices for CALL2/CALL3 in the Phase 11 fast plan.
  - Update `_construct_node_fast` to use CALL0–CALL3 dispatch when possible.
  - Make `_instance_results`, `_override_targets_by_spell_id`, and `_lock` lazy/removed
    when not needed by the fast path.
- Out of scope:
  - Adding a new transient-only ultra-fast plan variant.
  - Code generation or dynamic plan compilation.
  - Changes to public API surface or spellbook semantics.

## Steps / Checklist
- [x] Locate the Phase 11 execution plan builder and extend it with direct CALL2/CALL3
      dependency indices for the fast plan.
- [x] Split `run_execution_plan_no_overrides` into frame-less vs frame-aware loops and
      minimize per-step field loading.
- [x] Update `_construct_node_fast` to dispatch CALL0–CALL3 directly when available.
- [x] Adjust `MeldEngine` initialization to avoid allocating unused structures in the
      fast no-overrides path.
- [ ] Add/adjust tests if required by behavior changes and ensure documentation remains
      accurate.

## Deliverables
- Optimized `MeldEngine.run_execution_plan_no_overrides` with reduced per-step overhead.
- Fast plan updated with direct CALL2/CALL3 dependency indices.
- `MeldEngine` per-call allocations reduced for hot path usage.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`
- `src/melder/spellbook/spell_crafter/blueprints/execution_plan.py` (or the actual Phase 11 builder location)
- Tests under `tests/` as needed

## Validation
- Not run.
- Recommended commands:
  - pytest -q

## Risks / Rollback Notes
- Risk: Incorrect fast-plan indices could miswire dependency ordering.
- Rollback: Revert the fast-plan extension and restore prior loop logic.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Updated Phase 11 fast plan to include direct CALL2/CALL3 dependency indices and
specialized the no-overrides execution loop to reduce per-step overhead. MeldEngine
allocations are now lazy for hot-path execution. Remaining: decide on tests and
validate with benchmarks. Added a transient-only fast plan and tightened override
target collection in MeldRuntime. Closed per user request with tests/validation
still outstanding.
