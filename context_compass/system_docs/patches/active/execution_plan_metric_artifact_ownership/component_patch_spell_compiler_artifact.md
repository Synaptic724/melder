# Component Patch: SpellCompilerArtifact

## Before
`SpellCompilerArtifact` owns Phase 1-12 compiler/build artifacts, but not the
Phase 11 execution-plan metric outputs written onto `Spell`.

## After
`SpellCompilerArtifact` also owns the compiler-derived Phase 11 execution-plan
metrics, except for the currently runtime-consumed `dispatch_route` string that
remains on `Spell`.

## Interface Deltas
- Add artifact-owned fields for:
  - step count
  - unique spell count
  - max occurrence depth
  - max dependency count
  - has calln
  - has contract payloads
  - has existing creations

## State / Failure Deltas
- Cleanup and later-phase reset paths must null these metric fields with the
  rest of the Phase 11 state.

## Validation Expectations
- `spell_compiler_artifact.py` parses after slot/init/cleanup/reset additions.
