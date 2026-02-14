Completed: 2026-02-08
Summary: Added runtime benchmark sampling and threshold-evaluation gates with regression-focused unit coverage.

# Task: Define Benchmark Gates and Regression Thresholds

## Metadata
- Task ID: TASK-2026-02-07-benchmark-gates-and-regression-thresholds
- Story: STORY-2026-02-07-validation-perf-gates
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## Objective
Create repeatable benchmark gates for cold compile and warm execution paths.

## Scope Boundaries
- In scope:
- Benchmark harness and threshold reporting.
- Out of scope:
- Backward compatibility behavior.

## Steps / Checklist
- [x] Implement scoped changes.
- [x] Add/update tests for scoped behavior.
- [x] Update ticket context summary.

## Deliverables
- Scoped code and tests for this task.

### Delivered Benchmark Gate Surface
- Added benchmark sample harness API:
  - `MeldRuntime.collect_codegen_benchmark_samples_ns(...)`
  - deterministic warmup + sample collection in nanoseconds.
- Added gate evaluation API:
  - `MeldRuntime.evaluate_codegen_benchmark_gates(...)`
  - median-based warm/cold and mixed/cold ratio checks with threshold reporting.
- Added validation helpers:
  - `_sample_callable_ns`
  - `_normalize_benchmark_samples`
  - `_median_ns`
- Added runtime unit coverage for:
  - sample collection determinism and invocation counts,
  - pass/fail threshold reporting,
  - invalid sample and threshold rejection.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `src/melder/aether/conduit/meld/meld.py`
- `tests/`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py`
- Result:
  - 230 passed.

## Risks / Rollback Notes
- Risk of semantic drift in lock/reuse/registration behavior.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Benchmark gate contract is now present in runtime code and can be consumed by
bench scripts/CI wrappers to evaluate cold compile vs warm/mixed regression
ratios deterministically from median samples.

