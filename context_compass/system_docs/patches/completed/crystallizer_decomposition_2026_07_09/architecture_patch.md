# Architecture Patch: Crystallizer Subsystem Decomposition

## Metadata
- Patch ID: crystallizer_decomposition_2026_07_09
- Parent Epic: EPIC-2026-07-09-crystallizer-subsystem-decomposition
- Canonical design anchor: artifacts/2026-07-09_crystallizer_philosophy_v3.md
- Status: active
- Created: 2026-07-10T00:05:00Z
- Author: melder_0

## Objective
Decompose the crystallizer persistence god object into the V3 subsystem model without
changing any recorded/replayed semantics or any `Crystallizer` public facade signature.

## Non-Goals
- MR Phase B composition persistence/hydration.
- Full physical source-text retention (fingerprint only in this patch lane).
- Environment/asset layer (uv.lock validation, env gates).
- Any change to twin shapes, emission factors, journal semantics, checkpoint sealing,
  fold rules, stage order, or all-or-nothing teardown.

## Changed Components (target state)
1. `crystallizer/crystals/` (NEW location) - twin vocabulary moves up from
   `persistence/crystals/` (+ `recorded_unit_state.py`). Pure-data carriers; the
   CARRIER LAW applies (results in, no analyzers).
2. `crystallizer/crystal_analysis/` (INHABITED) - standalone `CrystalAnalyzer` +
   `CrystalAnalysisResult`; strategy families: custody/ (synthetic, user_source,
   site_package, binary_unknown), strategies/ facts (import_statement,
   from_import_statement, export_surface NEW, dependency_view/load-order NEW),
   preflight/ (7 restore strategies relocate from `persistence/analysis/`).
3. `crystallizer/persistence/` (SLIMMED) - `PersistenceSystem` keeps ONLY: profiles,
   twins/journal, checkpoint minting, ledger retention, chain verify, insert sink,
   cached-item forms. Verbs LEAVING: flush_checkpoint_to_cache,
   reload_checkpoint_from_cache, list_cached_checkpoint_ids, reload_profile_from_cache,
   save/load/restore/list formation storage halves, load_checkpoint orchestration,
   checkpoint_replay_data consumers stay (ledger data verb).
4. `crystallizer/asset_management/` (NEW) - `AssetManagementSystem` owns
   `crystallizer_cache.py` (moves), `external_persistence_manager(.py|_configuration.py)`
   (moves), flush local-then-upload, reloads feeding the record's insert sink,
   formation FILES, cache-file retention.
5. `crystallizer/crystal_loader_system/` (NEW) - `CrystalLoaderSystem` (durable load
   state) + `BootMediator` (LoadPlan -> strategy verdicts -> refuse/proceed) +
   `load_plan.py` + `restore_engine.py` (moves unchanged) + `bootstrap_loader.py`
   (CrystallizerBootstrap moves, thins to mediator-verb wrapper; chain-verify gate and
   `with_preflight_gate` absorbed into standard admission).
6. `crystallizer/crystallizer.py` - facades reroute to the three children; surface
   byte-compatible for callers.

## Invariants (must hold through every tranche)
- EDGE LAW: anything imports crystals/; analysis reads crystals; loader reads record +
  invokes analysis; assets read record + call its insert sink; the record calls nobody.
- LOCK LAW: one-way ordering (emitters -> crystallizer -> subsystem -> profile); no
  subsystem-to-subsystem lock nesting.
- FLUSH CONTRACT: seal (ledger) then ship (assets); lenient uploads preserved
  (upload_failure_count accounting unchanged).
- VERDICT LAW: admission blockers REFUSE (teach-grade), warnings PROCEED + report.
- R-A covenant, never-rehydrate-ULIDs, re-emission-intended, shortfall honesty: all
  unchanged.
- Facade parity: zero public signature changes on `Crystallizer`.

## Interface Deltas
- NEW: `CrystalAnalyzer.analyze_spell(spell, policy...) -> CrystalAnalysisResult`;
  `CrystalAnalyzer.analyze_payload(payload) -> CrystalAnalysisResult` (retained-version
  re-analysis; MR consumer).
- NEW: `CrystalAnalysisResult.describe()` value-only payload (superset of the current
  SpellCrystal manifest keys + physical fingerprints, export surfaces, load order).
- NEW: `BootMediator.begin_load(...) -> LoadPlan` / `execute(plan)`; every load path
  (checkpoint, formation, bootstrap) routes through admission.
- MOVED: cache/EPM verbs from PersistenceSystem/Crystallizer internals into
  `AssetManagementSystem` (facades reroute; names preserved at the facade).
- CHANGED (internal only): SpellCrystal constructor delegates analysis; its describe()
  keys are preserved verbatim plus new fields (see component patch).

## Migration Order (tranches = stories)
- S1 crystal_analysis extraction + SpellCrystal slim-down + physical SHA (this lane's
  component patches: component_patch_crystal_analysis.md, component_patch_spell_crystal.md).
- S2 crystals/ move-up (mechanical; grep gate `persistence.crystals` == 0).
- S3 asset_management extraction (component patch authored at S3 open).
- S4 crystal_loader_system + BootMediator (component patch authored at S4 open).
- S-test single test re-point sweep (sentinel set stays green per tranche: whole-system
  restore, profile-cache round trip, formation round trip, pod bootstrap, analyzer units).
- S5 C-doc/graph promotion + patch lane closure.

## Rollback
Each tranche is a self-contained move set; rollback = git revert of that tranche's
commits. No dual-write states exist; facades reroute atomically per tranche, so a
revert restores the previous routing wholesale. The record's on-disk formats (cache
JSON, checkpoint payloads) do not change in any tranche - stored data is
version-agnostic across the whole patch lane.

## Ticket Coverage Matrix
- EPIC-2026-07-09-crystallizer-subsystem-decomposition -> this file
- STORY S1 (crystal-analysis-extraction) -> component_patch_crystal_analysis.md,
  component_patch_spell_crystal.md
- STORY S3 (asset-management-extraction) -> component_patch_asset_management.md (at open)
- STORY S4 (crystal-loader-system) -> component_patch_crystal_loader_system.md (at open)
- STORY S2 / S-test / S5 -> mechanical; covered by this architecture patch alone
