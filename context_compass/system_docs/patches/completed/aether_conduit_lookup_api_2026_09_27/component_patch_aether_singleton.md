# Component patch: Aether Singleton (Global Runtime) - conduit lookups (2026-09-27)

## Purpose and boundary
Aether is the runtime root users reach first. Its conduit lookups read frame registries it owns; it does not own
conduit lifecycle.

## Before
- Eight lookups named generically answered over ROOT conduits only (frame `_conduits` / `_conduit_ids_by_name`);
  a live named lesser looked absent. Non-string frame names produced misleading errors.

## After
- `_resolve_lookup_frame(aetheric_frame_name)`: TypeError unless a `str`, then `_get_existing_frame(...)`.
- ROOT family, same results as before: `list_root_conduit_ids`, `list_root_conduit_names`, `count_root_conduits`,
  `has_root_conduit_id`, `has_root_conduit_name`, `find_root_conduit_id_by_name`, `get_root_conduit_by_name`,
  `get_root_conduit_by_id` (private `_get_root_conduit_by_name` / `_get_root_conduit_by_id`).
- `get_conduit_by_name(name, aetheric_frame_name="default")`: the frame Cloud's NAMED directory.
- `get_conduit_by_id(conduit_id, aetheric_frame_name="default")`: LIVE - the root map snapshot, then each root
  ward's `_get_lesser_conduit` (snapshot walk, see the ConduitWard code description).
- `_get_conduit_by_spell_id` resolves the owner through `_get_root_conduit_by_id` (owners are roots).

## Interface deltas
- Errors: TypeError "aetheric_frame_name must be a frame name string such as 'default'; got <type>." on all ten;
  ValueError "Root conduit with name 'N' not found in frame 'F'." / "Root conduit with id 'I' not found in frame
  'F'." for the root family; "Conduit with name 'N' not found in frame 'F'." and "Conduit with id 'I' not found in
  frame 'F'." (each with a one-line fix hint) for the reused lookups. Missing custom frames keep "Aetheric frame
  'F' does not exist.".

## State and lifecycle deltas
- None. No new owned state; returned conduits are borrowed and carry no lease.

## Failure mode deltas
- A concurrently returned or cleaned scope may or may not be found by a lookup running at the same moment; it is
  never returned after it has left its registry snapshot.

## Dependency and ordering
- MUST land after the ConduitWard snapshot walk and before the caller migrations.

## Validation expectations
- Unit: resolver TypeError (all ten), root family migrated, NAMED delegation, LIVE root/ward/missing, retired names
  absent. Integration: regression file (named, nested, anonymous, returned, custom frame, default frame).
