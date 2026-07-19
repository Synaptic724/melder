# Component Patch: SpellCrystal slim-down (S1)

## Metadata
- Patch ID: crystallizer_decomposition_2026_07_09
- Story: STORY-2026-07-09-crystal-analysis-extraction
- Status: active
- Created: 2026-07-10T00:05:00Z
- Author: melder_0

## Before (persistence/crystals/spell_crystal.py, ~1684 lines)
Constructor (:104-265) does three jobs:
1. Identity + bind-signature capture (:156-238): spell_id, root target resolution,
   spellbook parent edge, spell/binding/spellframe names, existence/permissions,
   disposal_method_names, profile_family, rebindability. THIS STAYS.
2. Analysis policy resolution (:184-187): user/site root paths. MOVES to policy input.
3. Embedded analysis (:163-178 slots init, :240-265 root classification + walk):
   12 analysis slots (_module_targets, _path_targets, _synthetic_module_targets,
   _synthetic_module_sources, _user_source_targets, _site_package_targets,
   _unknown_targets, _module_to_path/_kind/_extension/_direct_dependencies,
   _ast_import(_from)_targets_by_module, _walk_errors) filled by
   _classify_module_target/_resolve_module_source_text/_extract_import_targets_from_ast/
   _walk_module_dependencies/_harvest_synthetic_source/_record_module_target
   (:1150-1620, ~500 lines). ALL OF THIS MOVES.
describe() (:1620-1681) reads identity fields + the 12 analysis slots into one dict.
cleanup() (:267-323) dels identity fields + the 12 analysis slots.

## After
SpellCrystal = bind-signature CARRIER + one analysis result:
- Constructor keeps job 1 verbatim, then delegates:
  `self._analysis: CrystalAnalysisResult = CrystalAnalyzer-owned call` via a
  lazily-imported analyzer (import inside __init__ to keep crystals/ import-light;
  analyzer cleaned in a finally if construction fails after creation).
  Root-module resolution (_resolve_root_target_from_spell/_resolve_root_module) STAYS
  on SpellCrystal (it is spell-identity work, not analysis) and feeds the analyzer the
  (root_module_name, root_module_obj, root_module_path, policy) input.
- The 12 analysis slots are DELETED from __slots__; one `_analysis` slot replaces them.
- Read properties (module_targets, user_source_targets, site_package_targets,
  synthetic_module_sources, etc.) delegate to `self._analysis` and keep their exact
  signatures/return shapes (property parity - restore engine and tests read these).
- describe() preserves EVERY existing key verbatim, sourcing analysis keys from
  `self._analysis.describe()`, and adds: `physical_module_fingerprints`,
  `export_surfaces`, `module_load_order`.
- cleanup(): identity dels stay; the 12 slot dels become `self._analysis.cleanup()`
  then `del self._analysis` (children-first, del posture).
- _classify/_resolve_module_source_text/_extract/_walk/_harvest/_record_module_target
  and the root-path resolvers for classification policy are REMOVED from this file
  (relocated per component_patch_crystal_analysis.md). Comments referencing them are
  UPDATED, never deleted.

## Interface Deltas
- Constructor signature unchanged (spell, user_source_root_paths, spellbook_id).
- describe() payload: existing keys byte-compatible; three additive keys.
- Properties preserved; no callers change.
- from-payload construction path (used by restore fold) unaffected: payloads carry the
  same keys plus additive ones; older payloads without new keys load with the new
  fields absent-tolerant (preflight treats absent fingerprints as info, mirroring the
  existing synthetic_source_integrity absent-fingerprint law).

## State / Failure Deltas
- TypeError/ValueError constructor guards unchanged.
- Analysis failures keep the walk_errors honesty channel (now inside the result).
- Cleanup ordering: _analysis cleaned before identity dels? NO - children-first means
  the owned result cleans FIRST, then identity fields del, lock del last (matching the
  existing pattern; logger not owned here).

## Dependency / Ordering
- SpellCrystal gains one runtime import edge: crystal_analysis.crystal_analyzer
  (lazy, inside __init__). crystals/ stays otherwise import-light. EDGE LAW holds:
  a crystal consumes the analyzer's OUTPUT; the analyzer never imports the crystal.
  (Sanctioned nuance: the crystal CALLS the service at construction because bind-time
  custody is the crystal's birth contract; it owns the result, not the machinery.)

## Validation Expectations
- describe() key-set parity test (before-keys subset of after-keys, values equal on a
  fixture spell).
- Property parity spot checks used by restore fold + preflight (rebindability,
  synthetic_module_sources, module targets).
- Cleanup idempotence + post-cleanup check_cleaned behavior unchanged.
- Sentinel integration set (whole-system restore, formation round trip) green on
  owner-run 3.14t closes the tranche. Agent-side: py_compile floor, "Not run."
