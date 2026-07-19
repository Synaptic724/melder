# Component Patch: CompilerPhase11

## Before
Phase 11 caches execution-plan metrics directly onto `Spell`.

## After
Phase 11 writes the execution-plan metrics onto `SpellCompilerArtifact` and
continues writing `execution_plan_dispatch_route` onto `Spell`.

## Interface Deltas
- Redirect metric writes from `Spell` to `artifact`.
- Leave `spell.execution_plan_dispatch_route` unchanged in this slice.

## State / Failure Deltas
- No compile-shape logic changes.
- No plan-building logic changes.
- This is ownership relocation only.

## Dependency / Ordering
- `SpellCompilerArtifact` must expose the destination fields before Phase 11
  writes are redirected.

## Validation Expectations
- `compiler_phase_11.py` parses after write redirection.
