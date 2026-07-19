# Architecture Patch: Phase12 Artifact Processor And Codegen Plan Scaffold

## Objective
Add the first real Phase 12 scaffold so the compiler has explicit processor and
codegen-plan surfaces instead of a no-op placeholder.

## Non-Goals
- No Phase 13 emitter redesign.
- No `CreationContext` consumer rewrite.
- No concrete strategy-family behavior yet.

## Changed Components
- `SpellCompilerArtifact`
- `CompilerPhase12`
- `SpellCompiler`
- `SpellCompilerSystem`
- new Phase 12 scaffold packages under:
  - `spell_compiler/artifact_processor/`
  - `spell_compiler/codegen_planner/`

## Invariants
- Compiler-owned Phase 12 outputs live on `SpellCompilerArtifact`.
- `Spell` remains the runtime-owned holder for `CreationContext` and related
  bind/react state.
- Phase 13 remains untouched in this slice.
- The Phase 12 scaffold consumes the full artifact truth surface, not only the
  summary shape profiles.

## Interface Deltas
- Add artifact-owned Phase 12 fields for processor state and codegen plan.
- Add compiler-owned Phase 12 processor and codegen-plan class surfaces.
- Change `CompilerPhase12.run(...)` from no-op placeholder to scaffold builder
  that stores placeholder outputs.

## Migration Order
1. Add artifact fields and cleanup/reset support.
2. Add Phase 12 scaffold classes.
3. Wire `CompilerPhase12`.
4. Wire `SpellCompiler` and `SpellCompilerSystem`.
5. Add focused tests.

## Rollback
Remove the new Phase 12 fields/files and restore the placeholder no-op phase
atomically.

## Ticket Coverage Matrix
- `tickets/tasks/2026-05-30_scaffold_phase12_artifact_processor_and_codegen_plan_task.md`
