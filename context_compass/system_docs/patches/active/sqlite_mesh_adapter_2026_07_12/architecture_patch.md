# Architecture Patch: First-Party SQLite Mesh Adapter

## Metadata
- Patch ID: sqlite_mesh_adapter_2026_07_12
- Status: active
- Owner: melder_0
- Ticket: tickets/epics/2026-07-03_crystallizer_persistence_epic.md

## Objective
Ship the first first-party adapter PROVIDING the external-mesh callables
(owner reactivation ruling: "adapter LAST" = adapter NOW): one leaf
module backed by stdlib sqlite3 that a user constructs, registers through
the NORMAL configuration fluents, and points at a database file - the
whole mesh (checkpoints, formations, index grafts, emissions - and any
future kind) then persists without the user writing storage code. Spec
authority is MeshInterfaceContract.describe(): the adapter's table IS the
contract's identity-column model, its handlers ARE the contract's call
signatures.

## Non-Goals
- No core imports of the adapter (callables-first law intact: core forms
  calls against registered callables; the USER imports the adapter and
  registers it - core never references sqlite3 or this module).
- No new mesh verbs, kinds, or manager behavior.
- No ORM/DDL generation beyond the one contract table.
- No per-twin schema (twin payloads ride the JSON payload column
  opaquely - verified against mutation_0's 2026-07-12 additive twin keys:
  PAYLOAD_SHAPES enumerates unit-kind top-level keys only, so twin-
  internal additions need no contract or adapter change).

## Changed Components
1. NEW `src/melder/crystallizer/asset_management/adapters/
   sqlite_mesh_adapter.py` - `SqliteMeshAdapter` (Cleanable):
   - One table (default "melder_mesh_units") mirroring
     IDENTITY_COLUMNS: kind, profile_name, unit_id, payload (JSON
     text), PRIMARY KEY (kind, unit_id); created idempotently at
     construction.
   - Handlers matching HANDLER_SIGNATURES exactly:
     `store_unit(kind, profile_name, unit_id, payload)` (INSERT OR
     REPLACE - replace-on-emit precedent), `fetch_unit(kind, unit_id)`
     (payload dict or None), `list_units(kind, profile_name)` (unit_id
     list, lexicographic - ULID order = age), `delete_unit(kind,
     unit_id)` (STRICT: missing unit raises KeyError, mirroring the
     dict prototype's `del`).
   - `register_with(configuration)` convenience that registers all four
     handlers THROUGH the normal fluents (with_store_handler et al.) -
     sugar over the public registration surface, never a bypass.
   - Connection-per-operation (no long-lived sqlite3 connection): each
     verb opens/uses/closes its own connection, so handlers are safe
     from any thread under no-GIL without check_same_thread hazards;
     mesh operations are flush-time IO, not hot paths.

## Interface Deltas (all additive)
- `SqliteMeshAdapter(database_path, *, table_name="melder_mesh_units")`
- `store_unit / fetch_unit / list_units / delete_unit` (contract
  signatures), `register_with(configuration)`, `describe()`, `cleanup()`.

## Invariants
- The payload column always carries the RecordVersion-stamped JSON
  document exactly as the mesh shipped it (json.dumps/loads round trip;
  reader gates stay melder-side per the contract).
- Store is idempotent per (kind, unit_id) - latest write wins.
- Deletes are strict (retention passes must not lie).

## Migration Order / Rollback
Single additive leaf module + tests; rollback = delete both files.

## Validation Expectations
- Unit suite drives the adapter THROUGH the real
  ExternalPersistenceManager (the runtime consumer), not just directly:
  round trip any kind, persistence across adapter instances (pod-restart
  story), strict-delete refusal, kind+profile partitioning, replace
  semantics, JSON fidelity with RecordVersion stamps, cleanup contract,
  register_with wiring. Agent: Not run (owner-run 3.14t).
