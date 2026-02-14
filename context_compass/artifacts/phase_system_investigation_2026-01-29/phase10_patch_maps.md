# Phase 10 Investigation (Patch Maps)

## Metadata
- Created: 2026-01-29
- Updated: 2026-01-29
- Task: TASK-2026-01-29-phase10-patch-maps-investigation

## Scope
Analyze override and mutation patch map compilation and runtime application.

## Key Questions
- What inputs are required to build patch maps?
- How are override targets derived from the blueprint?
- How does runtime apply patch maps to overrides?

## Evidence
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter.run_phase_patch_maps
- src/melder/spellbook/spell_crafter/blueprints/patch_maps.py: PatchMapBuilder.build_override_patch_map
- src/melder/spellbook/spell_crafter/blueprints/patch_maps.py: PatchMapBuilder.build_mutation_patch_map
- src/melder/spellbook/spell_crafter/blueprints/patch_maps.py: apply_phase10_override_payload
- src/melder/spellbook/spell_crafter/blueprints/patch_maps.py: apply_phase10_mutation_overrides
- src/melder/spellbook/spell_crafter/blueprints/patch_maps.py: apply_override_patch_map
- src/melder/spellbook/spell_crafter/blueprints/patch_maps.py: apply_mutation_patch_map
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py: MeldRuntime.execute
- src/melder/spellbook/spellbook.py: Spellbook._phase_patch_maps_factory (docstring)

## Findings
- Phase 10 requires Phase 5 artifacts and a root blueprint. Non-root spells no-op.
- PatchMapBuilder derives targets from RootResolutionBlueprint.socket_refs and builds:
  - OverridePatchMap with path, unique, and broadcast target keys.
  - MutationPatchMap with mutation-contract sockets only, keyed by path, unique, and broadcast forms.
- apply_phase10_override_payload normalizes non-dict overrides to {} and requires a non-None OverridePatchMap.
- apply_phase10_mutation_overrides returns the original blueprint when mutation_override is empty, and requires a non-None MutationPatchMap when overrides are present.
- MeldRuntime.execute uses apply_phase10_mutation_overrides and apply_phase10_override_payload when a root blueprint exists.

## Risks / Concerns
- Spellbook._phase_patch_maps_factory docstring claims patch maps are based on Phase 9 injection plans, but the builder uses Phase 5 blueprints and socket refs. This may be a doc mismatch or a design gap.
- Root-only patch maps mean non-root spells cannot normalize override payloads via patch maps.

## Unknowns
- Whether patch maps should incorporate Phase 9 injection plan data (design decision).
- Whether override payloads should be rejected or tolerated when patch maps are missing for non-root spells.

## Next Steps
- Confirm intended relationship between Phase 9 injection plans and Phase 10 patch maps.
- Decide whether to compile patch maps for non-root spells or to adjust runtime expectations.
