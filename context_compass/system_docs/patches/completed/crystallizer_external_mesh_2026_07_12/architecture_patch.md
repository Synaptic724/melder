# Architecture Patch: external mesh lane (generic units + tap + retention)

- Patch ID: crystallizer_external_mesh_2026_07_12
- Ticket: EPIC-2026-07-11-crystallizer-v3-horizon-iteration (owner-directed
  extension, rulings 2026-07-12: generic kind-partitioned handlers;
  flush-shipped formations now + OPT-IN emission tap; opt-in delete
  handler + retention verb)
- Status: active

## Objective
"Store ANYTHING from the persistence mesh in the user's DB": one generic,
kind-partitioned callable trio carries every mesh unit (checkpoints,
formations, live emission events), an opt-in tap streams every
crystallizer emission as a delta row, and an opt-in delete handler gives
melder-driven remote retention. CALLABLES-FIRST LAW UNTOUCHED: the user
assigns plain functions; melder never imports a DB stack; the record
carries presence flags only.

## Interface Deltas (all additive; legacy checkpoint trio untouched)
- ExternalPersistenceManagerConfiguration: new slots + fluents
  with_store_handler(fn(kind, profile_name, unit_id, payload)),
  with_fetch_handler(fn(kind, unit_id) -> payload|None),
  with_list_units_handler(fn(kind, profile_name) -> [unit_id]),
  with_delete_handler(fn(kind, unit_id)),
  with_stream_emissions(bool, default False); describe_presence gains
  the flags.
- ExternalPersistenceManager: store_unit (lenient + store_failure_count;
  respects upload_on_flush for flush lanes), fetch_unit / list_units /
  delete_unit (loud-refuse without their handler), store_enabled /
  stream_emissions_enabled properties; LEGACY BRIDGE: the checkpoint
  verbs prefer the legacy handlers and fall back to the generic trio
  with kind="checkpoint" (one handler set can serve everything).
- AssetManagementSystem: store_formation ships remote (kind="formation",
  unit_id=formation_name) when the store lane is enabled;
  reload_formations_from_external(profile) mirrors the checkpoint
  reload (list+fetch -> local insert-if-absent);
  apply_external_retention(profile, max_checkpoints) ULID-sorts remote
  checkpoint ids and deletes the oldest beyond the cap (requires
  delete + list lanes; returns deleted ids).
- Crystallizer: EMISSION TAP in emit() - recording on + manager attached
  + stream_emissions -> store_unit("emission", active_profile,
  new ULID, {"crystal_kind", "payload"}) AFTER the record lands;
  lenient+counted, never blocks the R-A covenant.
  Facades: reload_formations_from_external(), apply_external_retention()
  (cap from the crystallizer configuration's max_persistence_crystals).

## Failure Posture
Writes (store/tap) are lenient + counted (store_failure_count) unless
strict_uploads; reads and deletes refuse loudly without their handlers;
remote contradiction (list-says/fetch-denies) raises per the existing
law.

## Migration Order
config -> manager -> asset system -> facades/tap -> SQLite + unit tests.

## Rollback
All additive; legacy trio byte-identical without the new fluents.
