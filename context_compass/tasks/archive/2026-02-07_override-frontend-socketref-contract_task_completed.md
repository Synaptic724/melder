Completed: 2026-02-07
Summary: Locked deterministic Phase 10 TargetSpec/SocketRef frontend contract for override codegen input.

# Task: Lock Override Frontend Targeting Contract for Runtime Codegen

## Metadata
- Task ID: TASK-2026-02-07-override-frontend-socketref-contract
- Story: STORY-2026-02-07-phase12-override-shape-specialization
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07

## Objective
Keep Phase 10 override frontend targeting (`TargetSpec` wildcard/path parsing +
`SocketRef` resolution) as the canonical input contract for override runtime codegen.

## Scope Boundaries
- In scope:
- Define immutable frontend payload handed to override runtime codegen compiler.
- Preserve wildcard/path targeting semantics and socket grouping guarantees.
- Out of scope:
- Runtime cache/selection implementation.
- Mutation-aware override semantics beyond current targeting contract.

## Steps / Checklist
- [x] Document canonical frontend payload shape (`SocketRef -> override value` and grouped indices).
- [x] Define deterministic ordering rules for codegen input emission.
- [x] Confirm compatibility with existing Phase 10 patch-map builders.

## Deliverables
- Signed-off override frontend contract for runtime codegen compiler input.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- `src/melder/spellbook/spell_crafter/dag/dag_index.py`
- `context_compass/artifacts/` design notes as needed

## Validation
- Run:
  - `python -m pytest -q tests/component/melder/aether/conduit/test_conduit_component_meld_overrides.py`
  - `python -m pytest -q tests/component/melder/aether/conduit/test_conduit_component_meld_overrides_deep.py`
  - `python -m pytest -q tests/component/melder/aether/conduit/test_conduit_component_spell_contracts.py`
  - `python -m pytest -q tests/integration/melder/conduit/test_conduit_integration_spell_contract_variants.py`

## Risks / Rollback Notes
- Risk: unstable targeting payload causes override codegen cache churn.
- Mitigation: deterministic ordering and explicit signature contract.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
This task preserves the current override frontend behavior and turns it into a
stable compiler input contract for future override runtime codegen.

