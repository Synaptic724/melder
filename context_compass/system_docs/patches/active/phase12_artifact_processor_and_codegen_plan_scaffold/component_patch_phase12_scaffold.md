# Component Patch: Phase12 Scaffold

## Before
There is no real Phase 12 subsystem. The compiler only has a placeholder phase
class with no processor, no plan builder, and no compiler-owned plan object.

## After
Phase 12 gains scaffold components for:
- `SpellCodegenModel`
- `SpellArtifactProcessorBuilder`
- `SpellArtifactProcessorStrategy`
- `SpellArtifactProcessor`
- `SpellCodegenPlan`
- `SpellCodegenPlanBuilder`
- `SpellCodegenPlanStrategy`

## Interface Deltas
- Add the new Phase 12 class surfaces under the compiler package.
- Keep the first cut strategy-free: no concrete strategy implementations yet.

## State / Failure Deltas
- No Phase 13 or runtime consumer changes in this slice.
- The new scaffold must still consume the full artifact truth surface.

## Validation Expectations
- New Phase 12 support files parse and can be imported by `CompilerPhase12`.
