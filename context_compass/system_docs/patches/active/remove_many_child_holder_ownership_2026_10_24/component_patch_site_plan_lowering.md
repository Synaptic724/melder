# component_patch_site_plan_lowering

## Metadata
- Patch ID: remove_many_child_holder_ownership_2026_10_24
- Component: Codegen site-plan lowering (`SitePlanEmission`, `site_plan_lowering.py`)
- Status: draft
- Owner: Mark (decision); melder_1 (executor)
- Created: 2026-10-24T20:06:55Z
- Updated: 2026-10-24T20:06:55Z

## Component Purpose and Boundary
- Current boundary: a disposal-bearing `many` step inside shared site i's miss registers in `c{i}` (the holder's
  store, 0.2.8235) and the miss adopts it after publication (`c{i}.adopt_children(...)`, 0.2.8238).
- Target boundary: every disposal-bearing `many` step registers through `many_store`, the meld's innermost scope, at
  the top level and inside a miss alike; a miss that registers one emits the innermost-scope prologue itself.

## Before/After Behavior Summary
- Before: `_emit_context` picks `c{i}` inside a miss; `_emit_miss` emits the adoption line.
- After: `_emit_context` picks `many_store` for every non-leasing context and reports its use; `_emit_miss` emits
  `_many_store_prologue` after its unresolved-input checks when its children register; no adoption line. Leasing
  managed misses keep `kids{i}` and `h{i}.adopt` unchanged.

## Interface Deltas
- Inputs: none.
- Outputs: miss source changes (prologue in, adoption out); `_site_plan_executor` bodies unchanged.
- Error semantics: unchanged.

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: a holder's children are disposed with the meld's innermost scope.

## Failure Mode Deltas
- Changed failure mode: as in the Creations patch - a holder that outlives the scope that built its child holds a
  disposed child.

## Dependency and Ordering Constraints
1. Lands with the Creations change (the adoption verb goes).
2. The specializer decline (`rows_feed_many_into_non_many_step`) stays; only its rationale text changes.

## Validation Expectations
- Test/validation item 1: emission unit tests - a miss's child registers through `many_store` after the prologue; no
  `adopt_children` anywhere in emitted source; leasing misses unchanged.
- Evidence target 1: tests/unit/melder/spellbook/spell_compiler/shared_assets/.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: door-held root misses and key-set plans - both emit through `_emit_miss`, covered by the tests.
- Next entrypoint: `SitePlanEmission._emit_context`, `_emit_miss`, `_many_store_prologue`, the class contract.
