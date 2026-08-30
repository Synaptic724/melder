# Component Patch: SpellCompiler And SpellCompilerSystem

## Before
`SpellCompiler` and `SpellCompilerSystem` instantiate and route a placeholder
Phase 12 that stores nothing.

## After
They still instantiate Phase 12, but that phase now builds and stores
placeholder processor state and placeholder codegen plan on the
spell-owned compiler artifact.

## Interface Deltas
- `CompilerPhase12.run(...)` becomes a scaffolded build/store phase.
- Existing `run_phase_strategy_selection(...)` compiler facades now route into
  a real Phase 12 scaffold instead of a no-op.

## State / Failure Deltas
- No Phase 13 behavior change.
- Compiler/system facades gain a real Phase 12 side effect on artifact state.

## Validation Expectations
- `spell_compiler.py` and `spell_compiler_system.py` still parse and delegate
  correctly after the scaffold wiring.
