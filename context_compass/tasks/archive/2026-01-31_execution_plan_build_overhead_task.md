# Task: Trim Phase 11 execution plan build overhead

## Metadata
- Task ID: TASK-2026-01-31-execution-plan-build-overhead
- Story:
- Status: draft
- Owner:
- Priority: p2
- Created: 2026-01-31
- Updated: 2026-01-31

## Objective
Reduce Phase 11 execution plan build overhead by optimizing parameter extraction and plan variant construction.

## Problem / Opportunity
Phase 11 execution plan compilation contributes ~0.053s in the full conjure build profile. The profile shows hot spots in `ExecutionPlan.build`, `_build_execution_plan_variant`, and `_extract_param_keys`, indicating non-trivial overhead per spell even before runtime execution.

## Context
Evidence from the user's `profile_conjure_build_direct.py` run on 2026-01-31:
- `SpellCrafter.run_phase_execution_plan` ~0.053s cumulative.
- `ExecutionPlan.build` and `_extract_param_keys` appear as top cumulative-time functions.
This phase is invoked via `SpellCrafter.run_phase_execution_plan` and should remain correct for all spell types.

## MRP Alignment
Execution plan compilation must remain correct and deterministic. Optimizations should not change plan semantics or ordering.

## Goals
- Reduce repeated parameter key extraction work.
- Avoid unnecessary recomputation across plan variants.
- Preserve plan outputs and public contracts.

## Non-Goals
- Do not change execution plan semantics or outputs.
- Do not alter public APIs.
- Do not remove plan variants or skip phases.

## Scope Boundaries
- In scope: `ExecutionPlan` build routines and helpers.
- Out of scope: runtime execution logic or meld runtime behavior.

## Requirements
- Preserve plan correctness and ordering.
- Keep changes localized and well-documented.
- Add or update tests to cover optimized behavior.

## Acceptance Criteria
- Phase 11 cumulative time decreases on the deep_layers direct benchmark.
- Existing execution plan tests continue to pass (user-run).
- New tests verify any optimized path remains correct.

## Steps / Checklist
- [ ] Inspect `ExecutionPlan.build` and `_extract_param_keys` call paths.
- [ ] Identify redundant work across plan variants.
- [ ] Propose a minimal optimization and get user approval.
- [ ] Implement optimization with docstring/comment updates.
- [ ] Add or update tests for plan build correctness.
- [ ] Validate with direct conjure benchmark (user-run).

## Deliverables
- Optimized execution plan build logic.
- Tests for execution plan build correctness.
- Benchmark comparison notes.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/blueprints/execution_plan.py
- src/melder/spellbook/spell_crafter/spell_crafter.py (only if wiring changes)
- tests/unit/melder/spellbook/spell_crafter/blueprints (new or updated tests)

## Validation
- Not run.
- Recommended commands:
  - `<local-workspace>\.venv_new\Scripts\python.exe benchmarks\conjure\profile_conjure_build_direct.py`
  - `pytest -q tests\unit\melder\spellbook\spell_crafter\blueprints`

## Risks / Rollback Notes
- Risk: plan variant generation changes subtly alter execution order.
- Mitigation: tests asserting plan ordering and param key coverage.

## Decision Log
- Baseline hotspots recorded from profile run provided by user (2026-01-31).

## Context / Handoff Summary
Phase 11 execution plan compilation shows non-trivial overhead in `ExecutionPlan.build` and `_extract_param_keys`. Optimize to reduce redundant work while preserving plan outputs and ordering.
