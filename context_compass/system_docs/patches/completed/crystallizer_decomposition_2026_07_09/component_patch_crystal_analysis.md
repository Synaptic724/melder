# Component Patch: crystal_analysis (S1 - new subsystem)

## Metadata
- Patch ID: crystallizer_decomposition_2026_07_09
- Story: STORY-2026-07-09-crystal-analysis-extraction
- Status: active
- Created: 2026-07-10T00:05:00Z
- Author: melder_0

## Before
No standalone analysis exists. All module-world analysis is embedded in the
`SpellCrystal` constructor chain (persistence/crystals/spell_crystal.py):
- classification: `_classify_module_target` (:1150) - path policy vs configured roots
- source resolution: `_resolve_module_source_text` (:1212) - hand-rolled dispatch
  (SyntheticModule protocol / .py|.pyi disk read / None)
- AST extraction: `_extract_import_targets_from_ast` (:1288)
- walk: `_walk_module_dependencies` (:1473) - DFS, visited-set cycle protection,
  unknown deps recorded as leaves, all resolvable kinds descend
- synthetic harvest: `_harvest_synthetic_source` (:1578)
- recording: `_record_module_target` (:1407) mutates 12 crystal-owned maps/lists
Restore preflight strategies live at `persistence/analysis/` (7 strategies + analyzer).
Gaps: no export surface, no topological load order, no physical fingerprints, no
site-package provenance, analysis unusable without a live Spell.

## After
`crystallizer/crystal_analysis/` package:
- `crystal_analysis_result.py` - `CrystalAnalysisResult`: value-only carrier of the
  full analysis payload. Fields mirror the current SpellCrystal manifest maps
  (module/path targets, per-kind lists, module_to_path/kind/extension/
  direct_dependencies, ast import maps, synthetic_module_sources, walk_errors,
  created_from_* flags) PLUS: `physical_module_fingerprints` (module -> source
  SHA256 for user_source modules), `export_surfaces` (module -> {all_declared,
  public_names}), `module_load_order` (topological order over direct edges;
  cycle-tolerant: cycles broken deterministically + reported into walk_errors).
  Cleanable; describe() returns the detached dict.
- `custody/` strategies (ABC `SourceCustodyStrategy`: `kind` property,
  `matches(module_name, module_obj, module_path, policy) -> bool`,
  `resolve_source(...) -> Optional[str]`, `fingerprint(source) -> Optional[str]`,
  `descends() -> bool`):
  - `synthetic_custody_strategy` (protocol source; SHA; descends)
  - `user_source_custody_strategy` (.py/.pyi disk read; NEW SHA256 fingerprint
    recorded into result; descends)
  - `site_package_custody_strategy` (path classification; source read for walk;
    descends; provenance fields stubbed for the future env decision)
  - `binary_unknown_custody_strategy` (no source; leaf; never descends beyond
    classification)
- `strategies/` fact passes (ABC `CrystalFactStrategy`: `name`,
  `analyze(module_name, source_text, syntax_tree, context) -> None` writing into the
  result):
  - `import_statement_strategy` + `from_import_statement_strategy` (logic MOVED from
    `_extract_import_targets_from_ast`, split per scaffold naming)
  - `export_surface_strategy` (NEW: `__all__` when statically resolvable, else public
    top-level def/class/assign names)
  - `dependency_view_strategy` (NEW: builds `module_load_order` after the walk from
    `module_to_direct_dependencies`)
- `crystal_analyzer.py` - `CrystalAnalyzer` (Cleanable): owns the walk loop (moved),
  resolves custody strategy per module, AST-parses once per module, runs fact
  strategies over the tree, harvests synthetic sources, returns one
  `CrystalAnalysisResult`. Entry points: `analyze_spell_root(root_module_name,
  root_module_obj, root_module_path, policy)` and `analyze_payload(payload_dict)`
  (rebuilds a result view from a retained describe() payload and re-runs source-free
  fact passes; the MR re-analysis seam).
- `preflight/` - the 7 restore strategies + `persistence_analyzer.py` MOVE here from
  `persistence/analysis/` unchanged except import paths (RestoreEngine/_run_preflight
  and Crystallizer facades re-point).

## Interface Deltas
- NEW public: CrystalAnalyzer, CrystalAnalysisResult, SourceCustodyStrategy,
  CrystalFactStrategy + 8 concrete strategies.
- MOVED public: PersistenceAnalyzer + PersistenceAnalysisStrategy + 7 strategies
  (path change only: persistence/analysis -> crystal_analysis/preflight).
- No facade signature changes; `Crystallizer.analyze_formation/analyze_checkpoint`
  reroute imports only.

## State / Failure Deltas
- Analysis state stops living as 12 slots on SpellCrystal; it lives once on the
  result object the crystal stores (see component_patch_spell_crystal.md).
- Failure behavior preserved: read/parse failures append to walk_errors, never raise
  mid-walk; TypeError/ValueError constructor guards stay on SpellCrystal.
- NEW failure surface: `analyze_payload` raises ValueError on payloads missing
  `module_to_direct_dependencies` - the one key BOTH accepted shapes carry.
  (CORRECTED 2026-07-10 after first owner run: the original spec also demanded
  `root_module_name`, but that is a CRYSTAL identity key absent from bare
  result payloads - the validation contradicted the two-shape contract.)

## Dependency / Ordering
- crystal_analysis imports crystals/ types ONLY for typing (TYPE_CHECKING); runtime
  input is the spell-root triple + policy or a plain payload dict. It never imports
  persistence/, asset_management/, or loader modules (EDGE LAW).
- Synaptic law applies: no module constants (policy carried on analyzer/config),
  Optional/Union typing, cleanup-after-init, ~50-60 LOC methods.

## Validation Expectations
- Unit: per custody strategy (source resolution, fingerprint, descent law); per fact
  strategy (import extraction parity vs current behavior on a fixture module tree;
  export surface on __all__/public/dunder cases; load order on chain/diamond/cycle);
  analyzer-from-payload round trip; walk-error honesty on unreadable/unparseable.
- Regression: physical fingerprint mismatch detected between two analyses of a
  mutated fixture file (drift symptom test).
- Parity: SpellCrystal.describe() keys before == after (superset allowed), verified
  by an explicit key-set test.
- Execution on 3.14t is owner-run; agent reports "Not run." with py_compile floor.
