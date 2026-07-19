# Component Patch: asset_management (S3 - bytes at rest)

## Metadata
- Patch ID: crystallizer_decomposition_2026_07_09
- Story: STORY-2026-07-09-asset-management-extraction
- Status: active
- Created: 2026-07-10T03:30:00Z
- Author: melder_0

## Before
Bytes-at-rest custody is smeared across two owners:
- PersistenceSystem owns `CrystallizerCache` (slot :85) and the asset verbs:
  flush_checkpoint_to_cache (:573), reload_checkpoint_from_cache (:622),
  list_cached_checkpoint_ids (:662), save_formation storage leg (:746),
  load_formation_record (:750), list_formations (:861),
  reload_profile_from_cache (:955).
- Crystallizer owns `_external_persistence_manager` directly (cleanup :166-170,
  configure :1591, describe :1634, reload_profile_from_external :1654, upload
  hook _upload_flushed_checkpoints :1694 called from flush_checkpoint :1302).
The ledger therefore touches disk, and the root facade owns a transport.

## After
NEW `crystallizer/asset_management/asset_management_system.py`:
`AssetManagementSystem` (Cleanable, own RLock) - BORROWS the PersistenceSystem
(reads feedstock + calls its sink through PUBLIC verbs only), OWNS
`CrystallizerCache` and the optional `ExternalPersistenceManager`.
Moved files: crystallizer_cache.py, external_persistence_manager.py,
external_persistence_manager_configuration.py -> asset_management/.

AssetManagementSystem verbs (moved semantics, preserved messages):
- flush_checkpoint(id=None) -> List[str]: feedstock via NEW ledger verb
  cached_item_forms(id); store each; FIFO cache retention per touched profile
  at the ledger's live max_persistence_crystals; then the upload leg (absorbed
  from Crystallizer._upload_flushed_checkpoints, reusing the SAME payloads -
  no double feedstock pull); lenient posture unchanged.
- reload_checkpoint_from_cache(id): cache load -> ledger.insert_cached_items
  ([item]) -> ledger.describe_checkpoint(id) (insert-if-absent preserved).
- list_cached_checkpoint_ids(): cache passthrough.
- reload_profile_from_cache(profile): cache profile listing (empty ->
  preserved teach-grade KeyError) -> batch insert via the sink -> summary.
- store_formation(formation_name, record, profile_name=None) /
  load_formation_record(name, profile_name=None) / list_formations(profile) -
  active-profile resolution via ledger.active_profile_name.
- configure_external_persistence_manager(config) (freeze + replace-and-clean),
  describe_external_persistence_manager(), reload_profile_from_external(
  profile) (missing-manager RuntimeError message preserved; downloads land in
  the ledger sink).

PersistenceSystem (the ledger) deltas:
- REMOVED: the seven asset verbs above + the `_crystallizer_cache` slot/init/
  cleanup. The ledger no longer touches disk.
- ADDED (record-side): cached_item_forms(checkpoint_id=None) -> List[Dict]
  (flush feedstock; payloads already carry checkpoint_id + profile_name);
  max_persistence_crystals read property (live retention cap for the asset
  system); capture_formation_record(...) -> Dict (the capture+assembly half
  of the old save_formation, storage-free).
- RESHAPED: restore_formation(formation_name, profile) ->
  restore_formation_record(formation_record) - the engine leg stays on the
  ledger UNTIL S4 moves it to the loader; the facade feeds it the record the
  asset system loaded. (Internal verb; Crystallizer facade signature is
  unchanged.)
- KEPT: cached_item_form, insert_cached_items, create_checkpoint, retention
  setter, verify_checkpoint_chain, load_checkpoint.

Crystallizer deltas (facade surface BYTE-COMPATIBLE):
- __init__ constructs `_asset_management_system = AssetManagementSystem(
  persistence_system)` after the record; `_external_persistence_manager`
  slot REMOVED (custody moved).
- cleanup order: asset system FIRST (it borrows the record), then the record.
- Facade reroutes: flush_checkpoint / reload_cached_checkpoint /
  list_cached_checkpoint_ids / reload_profile_from_cache / list_formations /
  configure+describe_external_persistence_manager /
  reload_profile_from_external -> asset system. save_formation = ledger
  capture + asset store. restore_formation / analyze_formation = asset load +
  ledger engine / analyzer. _upload_flushed_checkpoints DELETED (absorbed).

## Interface Deltas
- Crystallizer public surface: zero signature changes.
- PersistenceSystem internal surface: seven verbs removed, three added, one
  reshaped (bulk tests hitting removed verbs stay red until S-test).
- NEW public: AssetManagementSystem (verbs above).

## State / Failure Deltas
- All error messages and insert-if-absent/retention semantics preserved
  verbatim; the flush upload leg keeps the lenient failure accounting.
- Lock law: asset lock -> ledger public verbs (ledger locks itself); the
  ledger never calls the asset system (edge law; no cycles, no nesting
  reversal).

## Dependency / Ordering
- asset_management imports crystals/ (codec via ledger only - actually none
  directly), persistence (typing/borrowed collaborator), cache + EPM (owned).
- persistence/ no longer imports crystallizer_cache.
- Sentinel exposure: facade-level only - the restore integration suite
  (formation round trip, profile-cache round trip, pod bootstrap) exercises
  every reroute end to end.

## Validation Expectations
- Sentinel set green (owner 3.14t): the integration suite covers flush ->
  reload -> unfold, formations, and bootstrap-from-remote through the new
  routing.
- Unit: new AssetManagementSystem tests (flush feedstock + retention + upload
  leg with dict handlers; reload lanes; formation storage; EPM replace/
  describe semantics) ride S3; existing persistence_system/cache/EPM unit
  files re-point at S-test (bulk law).
- py_compile floor in-sandbox; execution reported "Not run." until owner runs.
