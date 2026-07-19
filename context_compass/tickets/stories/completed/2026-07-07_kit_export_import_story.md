# Story: Profile-scoped checkpoint cache (KIT CONCEPT DEAD - owner ruling)

## Metadata
- Story ID: STORY-2026-07-07-kit-export-import
- Parent Epic: EPIC-2026-07-03-crystallizer-bootstrap-checkpoint
- Status: closed
- Owner: cowork
- Agent Name: melder_0
- Priority: p2
- Created: 2026-07-07T13:50:00Z
- Updated: 2026-07-07T13:50:00Z

## Problem / Opportunity
A profile's checkpoint chain is the whole system (owner-run proven by the
restore program). KITS = PLUGINS (epic north star): one profile's foldable
history must travel as a portable payload - exported from one process,
imported into a fresh ledger, unfolded by the existing restore engine.

## MRP Alignment
Smallest trustworthy kit: JSON-safe payload shape (manifest + cached
items), export gated on chain fold-safety, import insert-if-absent with no
retention dropout. Archive/file format, naming, and signing are OWNER
TASTE CALLS deferred by design (decision log in the parent epic).

## Design (grounded in landed surfaces)
- EXPORT: PersistenceSystem.build_kit_payload(profile_name=None) ->
  {"manifest": {kit_format_version, profile_name, checkpoint_ids,
  checkpoint_numbers, chain_report}, "items": [to_cached_item...]}.
  Gate: verify_checkpoint_chain - REFUSE "broken" (ValueError, expressive);
  "truncated_prefix" exports with the verdict carried in the manifest
  (honest annotation, importer sees it).
- IMPORT: PersistenceSystem.import_kit_payload(kit) -> Dict summary
  {inserted, skipped_existing, profile_name}. from_cached_item each;
  insert-if-absent (reload semantics; cache lane precedent); NO retention
  dropout on import.
- Facades: Crystallizer.export_kit / Crystallizer.import_kit
  (activation-gated passthroughs).
- Unfold stays load_checkpoint (the restore engine folds imported chains
  like any chain). Reload verbs cover config rebuild; activation rules
  carry over (synthetic-containing kits need dynamic frames - shortfalls
  report as with any restore).

## Acceptance Criteria
- Export refuses broken chains loudly; annotates truncated ones.
- Round trip: export -> fresh system -> import -> load_checkpoint restores
  the world (integration test across singleton reset).
- Import is idempotent (re-import skips existing ids).
- All payloads JSON-safe (json.dumps round-trip test).

## Test Intentions
- Unit: gate refusal, manifest shape, import insert/skip, JSON round trip.
- Integration: full export/import/unfold across a fresh boot.

## Notes

- DATETIME: 2026-07-07T15:40:00Z
  TYPE: DECISION
  CLAIM: OWNER TASTE CALLS received - file-transport design locked.
    (1) FORMAT: JSON files in the existing cache location - NO archives;
    kits live beside the checkpoint cache under the resolved cache root:
    __melder_cache__/__kits__/{profile_name}/{profile_name}_epoch_{N}.json
    (same atomic-write pattern as CrystallizerCache).
    (2) NAMING: profile-based + version-based. Each EXPORT mints an
    incrementing KIT EPOCH per profile (filesystem-derived: max existing
    epoch + 1; no extra live state); manifest gains "kit_epoch".
    (3) INTEGRITY (owner delegated design): SHA256 digests of key assets -
    manifest gains "item_digests" {checkpoint_id: sha256(canonical JSON of
    the cached item)} and "kit_digest" (sha256 over the sorted item
    digests + profile + epoch). Canonical JSON = json.dumps(sort_keys=True,
    separators=(",", ":")). Import verifies EVERY digest BEFORE any ledger
    insert and refuses mismatches with expressive ValueErrors (integrity
    against corruption/tamper; SIGNING/trust remains deferred to the
    kit-distribution epic per standing decision).
    NOTE: checkpoints already carry the incrementing per-profile
    checkpoint_number (the "epoch" at checkpoint level); the kit epoch is
    the EXPORT-level version.
  EVIDENCE:
  - owner message 2026-07-07 (taste calls)
  IMPACT: Transport layer fully specified; payload verbs stay untouched
    (digests ride the manifest; a new KitStore owns file I/O beside
    CrystallizerCache).
  SUPERSEDED-IN-PART (owner 15:55Z): NO KitStore class - kit file I/O
    folds INTO CrystallizerCache (PersistenceSystem owns ALL caches).
    AND owner ruling landed immediately: EVERY snapshot is
    self-describing - Crystallizer._emit_policy_twin extracted (direct
    record, not emit, to keep the cadence ticker out of seal paths) and
    called at activation + BOTH seal paths (facade create_checkpoint +
    the automatic cadence ticker), so each PersistenceCrystal window
    carries the CrystallizerCrystal alongside all other captured items.
    Three exact-count journal assertions shifted +1 per seal and were
    updated (record_sinks 1->2 and 5->6, record_component 7->8). Compile:
    tests clean pattern; crystallizer.py Not run (replica rot; disk
    verified).
  NEXT: Implement KitStore (write_kit/read_kit/list_kit_epochs, atomic
    JSON) + digest build in build_kit_payload + digest verification in
    import_kit_payload + Crystallizer.export_kit_to_disk /
    import_kit_from_disk facades + unit tests (epoch increments, digest
    round trip, tamper refusal) + kit round-trip-from-disk integration
    test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T13:50:00Z
  TYPE: PLAN
  CLAIM: Lane opened on owner "continue" directly after the utility-system
    audit closed. Core verbs are taste-neutral (payload dicts); archive
    format/naming/signing await owner calls. NEXT: implement
    build_kit_payload + import_kit_payload on PersistenceSystem, facades,
    then tests. Consumption map: verify_checkpoint_chain (gate),
    to_cached_item/from_cached_item (codec), _checkpoint_crystals_by_id
    (ledger), load_checkpoint (unfold).
  EVIDENCE:
  - tickets/epics/2026-07-03_crystallizer_bootstrap_checkpoint_epic.md
    (Kit Export/Import Design Note)
  IMPACT: Kits become real on the proven restore substrate.
  NEXT: Implement system verbs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-07T14:10:00Z
  TYPE: FACT
  CLAIM: CORE LANDED. PersistenceSystem.build_kit_payload (fold-safety
    gated: broken/empty REFUSE with expressive ValueError;
    truncated_prefix exports with the verdict in the manifest; items =
    to_cached_item oldest-first; manifest carries format version 1 +
    ids/numbers/chain_report) + PersistenceSystem.import_kit_payload
    (insert-if-absent, idempotent, NO retention dropout, returns
    inserted/skipped summary) + Crystallizer.export_kit / import_kit
    facades (activation-gated). Compile: persistence_system OK in-sandbox;
    crystallizer.py Not run (replica rot; disk verified at the facades).
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_system.py
    (build_kit_payload / import_kit_payload)
  - src/melder/crystallizer/crystallizer.py (export_kit / import_kit)
  IMPACT: Export/import payload lane complete; unfold rides the proven
    load_checkpoint.
  NEXT: Tests per Test Intentions (unit gate/manifest/idempotence/JSON
    round trip + integration export->fresh boot->import->unfold), then
    owner taste calls (archive format, naming, signing) for the file
    transport layer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T14:30:00Z
  TYPE: FACT
  CLAIM: UNIT SUITE LANDED - tests/unit/melder/crystallizer/persistence/
    test_kit_export_import.py (4 tests): empty+broken export refusal with
    expressive messages; manifest shape (version 1, aligned ids/numbers
    oldest-first, chain report) + whole-payload json.dumps/loads round
    trip (the transport contract); truncated_prefix exports with the
    honest annotation and correct number bounds; import insert-if-absent
    + idempotent re-import + imported chain verifies intact - the kit
    even travels THROUGH json serialization before import in the test,
    proving the wire form. py_compile OK in-sandbox; execution Not run.
    REMAINING: integration export->fresh-boot->import->load_checkpoint
    round trip (restore-integration file fixtures ready for it), then the
    owner taste calls (archive format, naming, import auto-profile) for
    the file transport layer.
  EVIDENCE:
  - tests/unit/melder/crystallizer/persistence/test_kit_export_import.py
  IMPACT: The payload lane is contract-tested end to end at the unit
    level.
  NEXT: Integration round trip; owner taste calls.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T14:45:00Z
  TYPE: FACT
  CLAIM: INTEGRATION ROUND TRIP LANDED -
    test_kit_round_trip_exports_imports_and_unfolds appended to
    test_crystallizer_restore_integration.py: record world (bind +
    conjure) -> seal -> export_kit -> THROUGH json.dumps/loads (the wire
    form) -> _fresh_boot -> import_kit (all items inserted) ->
    load_checkpoint on the manifest head -> complete, book + active spell
    rebuilt, spell SHA in the identity map. Compile clean in-sandbox;
    execution Not run. The lane's remaining work is exactly the owner
    taste calls: archive format (.zip vs directory), kit naming, import
    auto-profile; signing stays deferred to the kit-distribution epic.
  EVIDENCE:
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py
    (tail test)
  IMPACT: Full kit lane contract-tested: gate, wire form, idempotence,
    and the unfold - 5 kit tests total riding the next sweep.
  NEXT: Owner sweep + taste calls; then the file-transport layer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T15:05:00Z
  TYPE: FACT
  CLAIM: TRIAGE (run: only 2 failures, everything else green incl. the
    kit unit suite + utility-system seam). (1) Mid-file mangle in the
    restore integration file: "is None" lost its tail ("is No") in the
    post-notch test - a bash-append casualty class on a GROWN file. FIXED
    via file-tool Edit. RULE HARDENED: ALL writes to existing files are
    FILE-TOOL-ONLY from here (appends included; the ticket/board rule now
    covers tests and source). (2) My kit round-trip asserted the spell SHA
    in the identity_map - by the engine's own design only ULIDs translate
    (SHAs are content-stable); assertion corrected to the re-emission
    proof (get_spell_crystal(sha) on the rebooted world). Compile clean
    in-sandbox; execution Not run.
  EVIDENCE:
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py
  IMPACT: Kit lane expected fully green on rerun; write-discipline gap
    closed permanently.
  NEXT: Owner rerun (--last-failed suffices); then taste calls.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T15:20:00Z
  TYPE: FACT
  CLAIM: OWNER-RUN GREEN ("those passed") - the kit PAYLOAD lane is fully
    proven: gate refusal, manifest shape, JSON wire form, idempotent
    import, truncated annotation, and the full export -> fresh boot ->
    import -> unfold round trip. Also green in the same runs: the
    utility-system emission seam + regression test. Story stays
    in_progress SOLELY for the file-transport layer, which is blocked on
    three owner taste calls: (1) archive format - single .zip per kit vs
    directory of JSON files; (2) kit naming - profile-derived vs
    user-supplied vs timestamped; (3) whether import auto-creates a
    profile named for the kit. Signing deferred to the kit-distribution
    epic (standing decision). The payload verbs are format-neutral; no
    landed code moves for any answer.
  EVIDENCE:
  - owner-run results 2026-07-07 (runs 7-8 green)
  IMPACT: KITS = PLUGINS is real at the payload level on the proven
    restore substrate.
  NEXT: Owner taste calls -> file-transport layer -> closure walk. Other
    queued program work: patch-doc promotion into C-docs (+ tail
    repairs), readable graph regen - both fresh-lane sized.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T16:30:00Z
  TYPE: FACT
  CLAIM: FILE-TRANSPORT SLICE LANDED per the locked owner design.
    CrystallizerCache (PersistenceSystem-owned; NO new class) gained the
    kit trio: _resolve_kit_directory (<cache root parent>/__kits__/
    <profile>), list_kit_epochs (filename-derived), store_kit (atomic
    tmp+os.replace, profile_epoch_N.json), load_kit (expressive KeyError).
    build_kit_payload now mints kit_epoch (max existing + 1) and the
    SHA256 integrity set: item_digests (canonical JSON per item:
    sort_keys + tight separators) + kit_digest (profile|epoch|sorted item
    digests); _canonical_digest helper. import_kit_payload verifies EVERY
    digest BEFORE any ledger insert (expressive refusal; pre-digest kits
    tolerated). NEW system verbs export_kit_to_disk /
    import_kit_from_disk (None epoch = latest) + Crystallizer facades.
    3 new unit tests (tamper refusal with empty-ledger proof; disk round
    trip minting epochs 1 and 2 and importing latest). Compile: cache +
    tests clean in-sandbox; persistence_system + crystallizer Not run
    (replica rot; disk verified). Execution: Not run.
  EVIDENCE:
  - src/melder/crystallizer/persistence/crystallizer_cache.py (kit trio)
  - src/melder/crystallizer/persistence/persistence_system.py (epoch +
    digests + disk verbs)
  - src/melder/crystallizer/crystallizer.py (disk facades)
  - tests/unit/melder/crystallizer/persistence/test_kit_export_import.py
  IMPACT: The kit lane is FEATURE-COMPLETE per owner spec: JSON in the
    owned cache world, profile+epoch naming, digest integrity,
    latest-epoch import, self-describing snapshots (policy twin per
    seal).
  NEXT: Owner sweep (kit unit file + count tests + full pass); on green,
    closure walk for this story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T17:00:00Z
  TYPE: DECISION
  CLAIM: OWNER RULING - THE KIT CONCEPT IS DEAD. Owner: "thats literally
    a persistence_system_checkpoint... you'd literally just need to make
    a profile name and put checkpoints under it." CONFESSION ON RECORD:
    "KITS = PLUGINS" entered the epic through the AGENT lane (introduced
    during epic scaffolding/rebuild), NOT from the owner - the agent then
    built on its own scaffolding as if it were an owner north star. The
    "kit" duplicated what __crystallizer_cache__ already IS: flushed
    checkpoint JSONs ({checkpoint_id}.json = to_cached_item form).
    Retention is governed by CrystallizerConfiguration
    (max_persistence_crystals) - checkpoints are bounded, and the cache
    (or a DB emitter later) is their durable store.
    THE REAL FEATURE (correction plan for the next burst):
    (1) RESTRUCTURE the cache layout to profile folders INSIDE the
    existing root: __crystallizer_cache__/{profile_name}/{checkpoint_id}
    .json (store_cached_item derives profile_name from the cached item;
    load searches by id or takes profile; list_cached_item_ids walks
    profile dirs).
    (2) NEW verb reload_profile_from_cache(profile_name): load EVERY
    cached checkpoint of a profile into the ledger insert-if-absent -
    that IS "import a world" (then load_checkpoint unfolds). No manifest,
    no epochs, no wrapper files.
    (3) RIP OUT the kit layer entirely: CrystallizerCache store_kit/
    load_kit/list_kit_epochs/_resolve_kit_directory; PersistenceSystem
    build_kit_payload/import_kit_payload/export_kit_to_disk/
    import_kit_from_disk/_canonical_digest; Crystallizer export_kit/
    import_kit/export_kit_to_disk/import_kit_from_disk; tests/unit/.../
    test_kit_export_import.py (7 tests); the kit round-trip integration
    test (replace with a reload_profile_from_cache round trip); the
    "Kit Export/Import Design Note" in the bootstrap epic (mark
    superseded); patch-doc kit references.
    (4) KEEP (owner-approved independent of kits): per-seal policy twin
    (self-describing snapshots), all reload verbs, chain-integrity verb.
    SHA256-of-key-assets (owner floated) can ride the cached item files
    later if wanted - not rebuilt as manifests.
  EVIDENCE:
  - owner message 2026-07-07 (ruling + cache question)
  IMPACT: Concept corrected before it calcified; the cache IS the
    transport, profiles ARE the packaging.
  NEXT: Execute the correction plan (rip-out + profile folders + reload
    verb + tests) as the next burst's first action.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T17:15:00Z
  TYPE: DECISION
  CLAIM: OWNER RETENTION RULING (addendum to the correction plan): the
    CACHE follows the checkpoint limit too - when no DB emitter is
    configured, cached checkpoint FILES cap per profile at the same
    max_persistence_crystals bound (FIFO: oldest cached file deleted on
    overflow at store time). Durability beyond the cap is the user's
    responsibility via a DB emitter ("its on them") - the DB emitter
    itself is a future lane. Execution of the full correction started
    this burst (order: cache layout+cap -> system verbs -> facades ->
    tests).
  EVIDENCE:
  - owner message 2026-07-07 (retention ruling)
  IMPACT: Bounded disk footprint by default; unbounded history is an
    explicit opt-in via DB.
  NEXT: Land the correction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T18:00:00Z
  TYPE: FACT
  CLAIM: CORRECTION FULLY LANDED - grep proves ZERO kit references remain
    in src/ or tests/. (1) CACHE: profile-scoped layout
    __crystallizer_cache__/{profile}/{id}.json (store derives profile
    from the cached item; load searches profile folders + legacy flat
    path; list counts both; NEW list_cached_item_ids_for_profile); NEW
    enforce_cache_retention (FIFO oldest-file deletion, ULID order);
    kit trio DELETED. (2) SYSTEM: build_kit_payload/_canonical_digest/
    import_kit_payload/export_kit_to_disk/import_kit_from_disk DELETED
    (hashlib/json imports removed); NEW reload_profile_from_cache
    (insert-if-absent, idempotent, expressive KeyError on unknown
    profile); flush_checkpoint_to_cache now enforces the cache cap per
    touched profile using _max_persistence_crystals (owner ruling: no DB
    emitter -> cache follows the checkpoint limit; "its on them").
    (3) FACADES: export_kit/import_kit/export_kit_to_disk/
    import_kit_from_disk DELETED; NEW Crystallizer.reload_profile_from_
    cache. (4) TESTS: test_kit_export_import.py REWRITTEN as the
    profile-cache suite (4 tests: profile-folder layout, cache cap FIFO,
    idempotent world reload + intact verify, unknown-profile refusal);
    the kit integration test replaced by
    test_profile_cache_round_trip_reloads_and_unfolds (flush -> fresh
    boot -> reload_profile_from_cache -> load_checkpoint -> same SHA
    re-emitted). Compile: cache + integration file clean in-sandbox;
    persistence_system (replica null-bytes variant) + crystallizer +
    unit file Not run (replica rot; ALL disks verified via file-tool
    reads). Execution: Not run.
  EVIDENCE:
  - src/melder/crystallizer/persistence/crystallizer_cache.py
  - src/melder/crystallizer/persistence/persistence_system.py
  - src/melder/crystallizer/crystallizer.py
  - tests/unit/melder/crystallizer/persistence/test_kit_export_import.py
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py
  IMPACT: The cache IS the transport; profiles ARE the packaging; disk
    footprint bounded by configuration. The kit concept is gone from the
    codebase.
  NEXT: Owner full sweep (the cache layout change touches every flush/
    reload path - test_crystallizer_cache.py may carry flat-layout
    assumptions to triage). On green: closure walk for this story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T21:00:00Z
  TYPE: FACT
  CLAIM: CLOSED - acceptance walk on owner-run green ("those passed" +
    "ok cool this works"). What this story ultimately delivered (after
    the kit concept was ruled dead and excised): profile-scoped
    checkpoint cache (__crystallizer_cache__/{profile}/{id}.json with
    legacy tolerance), FIFO cache-file retention at the checkpoint limit
    (no-DB default; DB durability is the user's opt-in), and
    reload_profile_from_cache as the import-a-world lane - all owner-run
    proven (profile-folder layout, cap FIFO, idempotent reload + intact
    verify, unknown-profile refusal, flush->fresh-boot->reload->unfold
    integration round trip). The dead-kit confession and correction
    ledger live in the 17:00Z/18:00Z notes. REPAIR NOTE: five trailing
    NUL bytes found at this file's tail on disk (file-tool write-fault
    class, fable_0 precedent); stripped via the sanctioned surgical
    exception (replica verified byte-current first) before this append.
  EVIDENCE:
  - owner-run results 2026-07-07 (post-correction sweeps green)
  IMPACT: The cache IS the transport; profiles ARE the packaging.
  NEXT: none (closed).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
