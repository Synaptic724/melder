# Component Patch: Spell

## Before
`Spell` stores both runtime-owned state and compiler-owned Phase 11 metric
outputs.

## After
`Spell` keeps runtime-owned state and retains only
`execution_plan_dispatch_route` from the current execution-plan metric set.

## Interface Deltas
- Remove these fields from `Spell`:
  - `execution_plan_step_count`
  - `execution_plan_unique_spell_count`
  - `execution_plan_max_occurrence_depth`
  - `execution_plan_max_dependency_count`
  - `execution_plan_has_calln`
  - `execution_plan_has_contract_payloads`
  - `execution_plan_has_existing_creations`
- Keep:
  - `execution_plan_dispatch_route`
  - `requires_spellspace_request`

## State / Failure Deltas
- `Spell.cleanup()` no longer tears down the removed compiler-owned fields.
- No runtime failure-mode change is intended in this slice.

## Validation Expectations
- `spell.py` parses after slot/init/cleanup removal.
