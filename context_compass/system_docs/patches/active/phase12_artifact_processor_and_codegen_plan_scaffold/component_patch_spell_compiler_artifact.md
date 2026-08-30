# Component Patch: SpellCompilerArtifact

## Before
`SpellCompilerArtifact` owns the phase caches, the newer shape profiles, and
the Phase 11 -> 13 no-overrides handoff, but it has no explicit Phase 12
processor-state or codegen-plan outputs.

## After
`SpellCompilerArtifact` also owns:
- one Phase 12 processor-state slot
- one Phase 12 codegen-plan slot

## Interface Deltas
- Add new internal Phase 12 fields.
- Extend cleanup/reset paths so Phase 12 outputs clear with later-phase
  invalidation.

## State / Failure Deltas
- No direct runtime behavior change.
- Phase 12 state becomes compiler-owned and explicitly resettable.

## Validation Expectations
- `spell_compiler_artifact.py` parses after slot/init/cleanup/reset additions.
