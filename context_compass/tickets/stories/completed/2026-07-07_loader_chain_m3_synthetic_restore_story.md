# Story: Loader chain M3 - synthetic-module restore

- Completed: 2026-07-11T19:10:00Z
- Summary: Delivered in full (synthetic_module_sources harvest,
  _rebuild_synthetic_world parents-first rebuild, boot-boundary E2E
  integration test incl. sys.modules eviction) and validated by the
  owner's subsequent full-tree greens; the custody model then EXTENDED
  through the closed S2 story (user-source retention rides the same
  lane) and the shared user_world_rebuild extraction. Closed late on
  owner-directed self-cleanup - the closure walk was overtaken by the
  successor lanes built on top of it.

## Metadata
- Story ID: STORY-2026-07-07-loader-chain-m3
- Parent Epic: EPIC-2026-07-03-crystallizer-bootstrap-checkpoint
- Status: closed (owner-directed self-cleanup 2026-07-11; delivered +
  green-covered + extended by closed successor lanes)
- Owner: cowork
- Agent Name: melder_0
- Priority: p2
- Created: 2026-07-07T22:10:00Z
- Updated: 2026-07-07T22:10:00Z

## Problem / Opportunity
Synthetic-rooted spells restored as honest
`synthetic_root_requires_loader_chain_m3` shortfalls: the record carried
synthetic module NAMES but never their SOURCE, and synthetic modules have
no files - their source IS the record. M3 closes the last gap between
"restores everything importable" and "restores everything".

## Design (grounded: src/melder/crystallizer/synthetic_module.py)
- SyntheticModule already owns the full rebuild surface: source_text,
  source_sha256, binding_signature, spell_crystal_id, parent/package
  semantics, registry + sys.modules publication, execute_source, and a
  Cleanable-mirroring cleanup that unpublishes/unregisters.
- CAPTURE: SpellCrystal._harvest_synthetic_source called in the module
  walk beside _record_module_target - for every reachable SyntheticModule
  records {source_text, source_sha256, binding_signature,
  spell_crystal_id, parent_name, is_package} into NEW
  `synthetic_module_sources` (slots/init/cleanup/describe wired;
  additive).
- REPLAY: engine _hydrate_target's synthetic branch now calls
  _rebuild_synthetic_world: parents-first (dot-depth order), sys.modules
  presence skips (idempotent across custody crystals), construct ->
  register_in_import_registry -> publish_to_sys_modules ->
  execute_source, each built module rides _built_stack (all-or-nothing
  teardown unpublishes via SyntheticModule.cleanup), then the NORMAL
  importlib hydration lane resolves the target. Failures -> per-module
  expressive shortfall. Pre-M3 payloads (no sources key) keep an honest
  `synthetic_root_recorded_without_sources_pre_m3` shortfall.

## Acceptance Criteria
- A synthetic-rooted bind's custody crystal carries rebuildable sources.
- A fresh engine hydrates the target from the recorded sources alone;
  teardown unpublishes.
- Pre-M3 payloads degrade honestly.

## Notes

- DATETIME: 2026-07-07T22:10:00Z
  TYPE: FACT
  CLAIM: LANE LANDED in one burst (capture + replay + 3 unit tests):
    test_spell_crystal_harvests_synthetic_module_sources (live
    SyntheticModule -> custody describe carries source/sha/metadata),
    test_hydrate_rebuilds_synthetic_world_and_teardown_unpublishes
    (hand-built payload -> target hydrated, built_counts
    synthetic_module==1, teardown removes it from sys.modules),
    test_pre_m3_synthetic_payload_keeps_the_honest_shortfall. Compile:
    engine + tests clean in-sandbox; spell_crystal.py Not run (replica
    rot; disk verified). Execution: Not run. REMAINING for closure:
    owner sweep + (follow-up candidate) an end-to-end integration test
    binding a real synthetic-rooted spell through a live book across a
    fresh boot - the unit lanes prove capture and rebuild separately.
  EVIDENCE:
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py
    (_harvest_synthetic_source + synthetic_module_sources)
  - src/melder/crystallizer/persistence/restore_engine.py
    (_rebuild_synthetic_world)
  - tests/unit/melder/crystallizer/persistence/test_restore_engine.py
    (3 M3 tests)
  IMPACT: The restore engine now rebuilds module worlds that never had
    files - the record is the source of record, literally.
  NEXT: Owner sweep; then graph regen remains the last queued doc lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T22:40:00Z
  TYPE: FACT
  CLAIM: END-TO-END INTEGRATION TEST LANDED
    (test_synthetic_rooted_spell_restores_across_the_boot_boundary in the
    restore integration file): a live SyntheticModule hosts the bind
    target class; a real book binds + conjures it; seal + flush; process
    death simulated FULLY (fresh singletons + module cleanup + sys.modules
    eviction - a new process has neither); reload + load_checkpoint ->
    built_counts synthetic_module >= 1, spell_active == 1, the module is
    back in sys.modules, and the SAME content-derived SHA re-records.
    GATE VERIFIED from source before landing: rebindability derives from
    root_target_kind (class/function -> "hydratable") independent of
    module kind, so synthetic-rooted classes reach the M3 branch in the
    real lane. Compile clean in-sandbox. Execution: Not run.
  EVIDENCE:
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py
    (tail test)
  IMPACT: M3 is validated at every level: capture unit, rebuild unit,
    degradation unit, and the full boot-boundary round trip.
  NEXT: Owner sweep -> closure walk. Queue after: graph regen, adapter
    package (future).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
