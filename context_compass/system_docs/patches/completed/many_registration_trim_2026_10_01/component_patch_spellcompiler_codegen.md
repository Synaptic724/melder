# component_patch_spellcompiler_codegen

## Metadata
- Patch ID: many_registration_trim_2026_10_01
- Component: SpellCompiler and Validation Pipeline (codegen creation system: site-plan lowering, solo
  templates, generalized specializer emitter)
- Status: active
- Owner: user (agent fable_0)
- Created: 2026-10-01T01:08:13Z
- Updated: 2026-10-01T01:08:13Z

<!-- BEGIN ENTRY: "Codegen: the many registration line" -->
## Component Purpose and Boundary
- Current boundary: the emitters decide which steps register (disposal-bearing `many` steps only) and write
  `many_store.add_many_creations(sidN, vN, has_disposal_methods=True, disposal_methods=dmN)` (site-plan
  lowering), `many_creations.add_many_creations(spell_id, instance, has_disposal_methods=True,
  disposal_methods=disposal_methods)` (solo templates) and `creations_{i}.add_many_creations(spell_id_{i},
  instance_{i}, has_disposal_methods=True, disposal_methods=disposal_methods_{i})` (specializer emitter).
- Target boundary: the same decisions; the line becomes the positional `register_many(sid, v, dm)` at the
  three sites. The prologue (`many_store = meld._spellspace_creations; if None: meld._conduit_creations`), the
  `sidN`/`dmN` namespace bindings and every other emitted line are unchanged.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1313-1329
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:98-122
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:97-118
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:488-556

## Before/After Behavior Summary
- Before: a keyword call into the public verb (two frames, keyword binding) per disposal-bearing many creation.
- After: a positional call into the hot verb (one frame) per creation; same store, same scope selection.

## Interface Deltas
- Inputs/Outputs: none public. The runtime-library helper `_register_spell_instance_prebound` (exported to
  emitted namespaces, called by no emitted body) keeps calling the public verb and is not touched.
- Error semantics: unchanged (the store raises the same errors).

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New/removed/changed: none.

## Dependency and Ordering Constraints
1. Lands with the store change and the generation bump (16, `many_registration_per_key_methods`) so bundles
   emitted before this change are rebuilt rather than hydrated.

## Validation Expectations
- Test/validation item 1: emitter unit tests assert the new line for the site plan (normal and key-set plans),
  the solo templates and the specializer branch; a component test conjures a disposal-bearing many root and
  melds it through a conduit and a SpellSpace, then checks the store and the disposal order at exit.
- Evidence target 1: tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py,
  tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py, tests/component/.
<!-- END ENTRY: "Codegen: the many registration line" -->

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none beyond the store's.

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: an emitter test that pins the old text.
- Next entrypoint: the task's mapping note.
