Completed: 2026-02-08
Summary: Delivered Audit Override Shape-Key Stability Against Plan Identity Coupling scope, updated validation notes, and confirmed acceptance.

# Task: Audit Override Shape-Key Stability Against Plan Identity Coupling

## Metadata
- Task ID: TASK-2026-02-07-override-shape-key-stability-audit
- Story: STORY-2026-02-07-phase12-overrides-full-emitted
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## Objective
Verify override specialization cache key stability when plan objects are rebuilt,
and define whether `id(execution_plan)` must be replaced by signature-based
identity for equivalent-plan cache reuse guarantees.

## Scope Boundaries
- In scope:
- Audit `_build_override_shape_key` key components and cache behavior.
- Measure cache churn when equivalent plans are rebuilt with new object ids.
- Define canonical plan identity component for shape keys.
- Out of scope:
- Full override compiler rewrite.

## Steps / Checklist
- [x] Trace shape-key construction and cache hit/miss behavior by scenario.
- [x] Validate current behavior for equivalent-plan object rebuilds.
- [x] Propose and document signature-based plan identity replacement if needed.
- [x] Define regression tests for key stability and invalidation correctness.

## Deliverables
- Findings report for shape-key stability and cache churn risk.
- Final key contract recommendation and implementation checklist.
- Runtime now builds shape keys from deterministic plan semantics instead of object identity.
- Regression tests cover equivalent-plan reuse, semantic-change invalidation, and malformed plan error wrapping.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py`
- Result: 30 passed.

## Risks / Rollback Notes
- Risk: plan-identity keying can cause avoidable recompiles on equivalent plans.
- Mitigation: adopt signature-based identity component where parity-safe.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Implemented deterministic override plan signatures in `MeldRuntime` and removed
identity-coupling from shape-key behavior. Added explicit malformed-plan failure
wrapping in override execution route. Added regression tests to validate:
equivalent-plan key stability across object rebuilds, semantic-change key
invalidation, and runtime error wrapping for invalid plan artifacts.


