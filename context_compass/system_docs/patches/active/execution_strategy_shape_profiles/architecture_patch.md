# Architecture Patch: Execution Strategy Shape Profiles

## Objective
Add compiler-owned shape profiles to `SpellCompilerArtifact` and populate them
incrementally from Phases 1, 8, 9, 10, and 11 so future strategy selection can
consume richer facts without a second heavy analysis pass.

## Non-Goals
- No new strategy-selection phase yet.
- No `CreationContext` consumer changes yet.
- No runtime behavior change from the profiles alone.

## Changed Components
- `SpellCompilerArtifact`
- `CompilerPhase1`
- `CompilerPhase8`
- `CompilerPhase9`
- `CompilerPhase10`
- `CompilerPhase11`

## Invariants
- Shape data remains compiler-owned.
- Collection happens only where the truth is already being built.
- No new deep graph scan is introduced.

## Interface Deltas
- Add artifact-owned phase shape profile fields for Phases 1/8/9/10/11.
- Leave the current runtime consumer surface unchanged.

## Migration Order
1. Add the artifact fields and cleanup/reset support.
2. Populate Phase 1 profile.
3. Populate Phase 8 profile.
4. Populate Phase 9 profile.
5. Populate Phase 10 profile.
6. Populate Phase 11 profile.

## Rollback
Remove the profile fields and phase writes if the collection proves too noisy
or too expensive.

## Ticket Coverage Matrix
- `tickets/tasks/2026-05-30_collect_execution_strategy_shape_profiles_task.md`
