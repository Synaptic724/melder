# Component Patch: SpellCompilerArtifact

## Before
`SpellCompilerArtifact` stores raw compiler/build artifacts and some isolated
Phase 11 outputs, but not grouped incremental shape profiles across phases.

## After
`SpellCompilerArtifact` owns grouped shape profiles for:
- Phase 1 requirements shape
- Phase 8 occurrence/graph shape
- Phase 9 injection shape
- Phase 10 override targetability shape
- Phase 11 final runtime-step shape

## Interface Deltas
- Add new internal profile fields.
- Extend cleanup/reset paths to clear them.

## State / Failure Deltas
- No runtime semantic change.
- Profiles are best-effort compile-side summaries only.

## Validation Expectations
- `spell_compiler_artifact.py` parses after slot/init/cleanup/reset additions.
