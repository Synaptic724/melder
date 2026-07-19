# Architecture Patch: Execution Plan Metric Artifact Ownership

## Objective
Move compiler-owned Phase 11 execution-plan metric outputs off `Spell` and onto
`SpellCompilerArtifact`, while leaving `requires_spellspace_request` and
`execution_plan_dispatch_route` on `Spell` for the current runtime seam.

## Non-Goals
- No new strategy-selection phase.
- No runtime consumer redesign beyond redirecting writes.
- No move of `requires_spellspace_request`.
- No move of `execution_plan_dispatch_route`.

## Changed Components
- `Spell`
- `SpellCompilerArtifact`
- `CompilerPhase11`

## Invariants
- Phase 11 remains the producer of execution-plan metric outputs.
- `Spell` retains only `execution_plan_dispatch_route` from the current metric set.
- `CreationContextBuilder` continues to read `spell.execution_plan_dispatch_route`.
- No runtime behavior should change from the ownership move alone.

## Interface Deltas
- Removed from `Spell`:
  - `execution_plan_step_count`
  - `execution_plan_unique_spell_count`
  - `execution_plan_max_occurrence_depth`
  - `execution_plan_max_dependency_count`
  - `execution_plan_has_calln`
  - `execution_plan_has_contract_payloads`
  - `execution_plan_has_existing_creations`
- Added to `SpellCompilerArtifact` as compiler-owned Phase 11 outputs.

## Migration Order
1. Add the Phase 11 metric fields to `SpellCompilerArtifact`.
2. Remove the same fields from `Spell`.
3. Redirect Phase 11 writes to artifact-owned fields.
4. Leave `execution_plan_dispatch_route` on `Spell`.

## Rollback
Restore the removed `Spell` fields and redirect Phase 11 writes back to `Spell`.

## Ticket Coverage Matrix
- `tickets/tasks/2026-05-30_move_execution_plan_metrics_to_spell_compiler_artifact_task.md`
