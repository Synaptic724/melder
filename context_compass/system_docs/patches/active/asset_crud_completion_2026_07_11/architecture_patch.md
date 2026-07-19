# Architecture Patch: asset-management CRUD completion + mesh interface contract

- Patch ID: asset_crud_completion_2026_07_11
- Ticket: TASK-2026-07-11-asset-crud-completion
- Status: active

## Objective
Finish the CRUD symmetry of the asset layer and make the mesh a
SELF-DESCRIBING interface layer (owner directive): melder forms the
calls, emits the SHAPE (the "table") so users can register handlers and
build their storage directly from the emitted contract, and the data
itself keeps flowing as versioned JSON both ways (emit via tap/store,
retrieve via fetch/list).

## Non-goals
- No SQL/DDL generation (callables-first law stands: melder describes
  shape, never writes storage code; the record stores presence flags).
- No change to existing verb behavior; everything here is additive.
- The first-party adapter package stays parked (backlog epic).

## Interface Deltas (additive)
1. NEW asset_management/mesh_interface_contract.py -
   MeshInterfaceContract (static authority, RecordVersion precedent):
   class-level shape table for every unit kind (checkpoint, formation,
   index_graft, emission envelope) - per-kind payload key inventory,
   identity column semantics (kind, profile_name, unit_id, payload),
   handler call signatures (store/fetch/list/delete + stream), and the
   registration fluent names. describe() emits it as one
   RecordVersion-stamped plain dict.
2. Cache single-item deletes: CrystallizerCache.delete_cached_item(id)
   + delete_formation(profile, name) (missing = teach-grade KeyError;
   atomic unlink).
3. AssetManagementSystem: delete_cached_checkpoint(id),
   delete_formation(profile, name, include_remote=False) (remote leg =
   strict delete lane, mirrors retention law), store_index_graft /
   fetch_index_graft / list_index_grafts (generic lanes under kind
   "index_graft"; fetch gates RecordVersion.check_readable),
   describe_external_interface() (contract + live handler presence).
4. Crystallizer facades: delete_cached_checkpoint, delete_formation,
   store_index_graft_external, fetch_index_graft_external,
   list_index_grafts_external, describe_external_interface
   (activation-gated, byte-compatible additions).

## Scope Expansion (owner-directed, 2026-07-11: "implement all the
## final things")
5. Mesh-aware bootstrap: CrystallizerBootstrap gains
   with_formation_reload(bool) (default True, mirroring
   with_pull_remote) + a formation-pull step between the remote
   checkpoint pull and chain verify; the report gains
   "formation_reload". Touches crystal_loader_system/bootstrap_loader
   .py - EXPANDS the original boundary (recorded here + ticket note);
   purely additive, existing steps unchanged.

## Migration order / Rollback
All additive; land contract class first (pure), then cache verbs, then
system verbs, then facades, then tests. Rollback = delete the new
verbs/file.

## Validation expectations
Unit: contract describe shape (keys per kind, stamped version), cache
delete hit/miss, formation delete local/remote strict, graft
store/fetch/list round trip over dict-backed handlers, facade gating.
Owner runs 3.14t; agent reports "Not run."
