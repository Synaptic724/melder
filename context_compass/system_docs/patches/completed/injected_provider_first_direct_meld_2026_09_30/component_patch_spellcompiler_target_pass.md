# component_patch_spellcompiler_target_pass

## Metadata
- Patch ID: injected_provider_first_direct_meld_2026_09_30
- Status: active
- Owner: user (agent melder_0)
- Created: 2026-09-30T19:31:23Z
- Updated: 2026-09-30T19:31:23Z

<!-- BEGIN ENTRY: "SpellbookCreationSystem: target pass tail" -->
## Before
- `run_resolution_phases_for_target_spell` runs local 5-7, then the target's 8-11, then cleans the scoped phase
  artifacts. Local Phase 5 publishes root blueprints only to the target (2026-09-19) and local Phase 6 stamps every
  node of the target's system index valid for the conduit, so a dependency the pass compiled only inside the
  target's plan keeps no plan and no context of its own yet reads valid: nothing resolves it before its first direct
  meld, and that meld reaches the CreationContext builder with no payload.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1654-1754
  - src/melder/aether/spellbook/spellbook_creation_system.py:2323-2355
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py:220-267
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:69-152

## After
- On the success path, after the scoped cleanup, the pass calls `flag_dependencies_without_own_plan(spellbook,
  target_spell_id, scoped_spell_ids)` with the scope it already collected. For each scoped id other than the target,
  in sorted order, it skips ids missing from `spellbook._spell_id_pool`, spells the Book does not own
  (`spell._spellbook is not spellbook`), non-resolvable spells and existing creations; under the dependency's spell
  lock it flags one that has no phase-11 plan (`_compiler_artifact._spell_codegen_creation is None`), no published
  CreationContext (`_creation_context_switch.state < 2`) and no flag yet: `resolution_complete=False`,
  `resolution_required=True`, `_door_epoch += 1`. It returns the flagged ids.
- The failure paths flag nothing: foundational errors raise SpellbookValidationError, and a visibility failure
  returns after writing invalid verdicts.

## State / Failure Deltas
- New state: a flagged dependency. Its own successful deferred-lane pass clears it; a failed pass keeps it.
- No verdict, Book flag or diagnostic changes.

## Validation Expectations
- Unit: flags an owned plan-less dependency and bumps its epoch; leaves alone a dependency with a plan, one with a
  published context, an existing creation, a non-resolvable one, a borrowed one, the target, an id missing from the
  pool and one already flagged (no second epoch bump); the write happens under the dependency's lock; the pass calls
  it on success only.
- Component: the regression file - the direct meld after injection returns the scope's instance.
<!-- END ENTRY: "SpellbookCreationSystem: target pass tail" -->
