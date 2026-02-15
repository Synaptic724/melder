Completed: 2026-02-07
Summary: Routed runtime override execution through spell-scoped specialization executors with compile-on-miss behavior.

# Task: Route Runtime Through Override Specialization Executors

## Metadata
- Task ID: TASK-2026-02-07-override-specialization-runtime-routing
- Story: STORY-2026-02-07-phase12-override-shape-specialization
- Status: done
- Owner:
- Priority: p1
- Created: 2026-02-07
- Updated: 2026-02-07

## Objective
Add runtime routing that selects and executes override-shape specialization
executors as the override execution path.

## Scope Boundaries
- In scope:
- Runtime selection gates for specialization hit/miss.
- Miss-path compile/build behavior for specialization executors.
- Out of scope:
- Public API changes.
- Non-override execution paths.

## Steps / Checklist
- [x] Implement specialization executor selection by shape key.
- [x] Compile specialization executor on miss and cache it.
- [x] Record basic hit/miss diagnostics for validation.

## Deliverables
- Runtime override specialization routing path without engine fallback.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`

## Validation
- Run:
  - `python -m py_compile src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
  - `python -m pytest -q tests/component/melder/aether/conduit/test_conduit_component_meld_overrides.py`
  - `python -m pytest -q tests/component/melder/aether/conduit/test_conduit_component_meld_overrides_deep.py`
  - `python -m pytest -q tests/component/melder/aether/conduit/test_conduit_component_spell_contracts.py`
  - `python -m pytest -q tests/integration/melder/conduit/test_conduit_integration_spell_contract_variants.py`

## Risks / Rollback Notes
- Risk: specialization route diverges from existing targeting semantics.
- Mitigation: parity tests against patch-map/frontend targeting outputs.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task completes override re-enable path in codegen-only runtime after signature
and cache layers are in place.

