# code_description_patch_world_reuse

## Metadata
- Patch ID: crystal_world_reuse_2026_11_17
- Ticket: https://github.com/Synaptic724/melder/issues/331
- Status: implemented at 0.2.8305
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-17T11:00:00Z
- Updated: 2026-11-17T11:15:23Z

## Control Flow Commitments
- `analyze_spell_root`: when the analyzer keys answers and retains no sources, look up the world by (policy key,
  descent flag, root name, root path text) and the root object; a valid world loads into a fresh result and returns.
  Otherwise walk; before the per-pass answers are emptied, collect one entry per touched module; after finalize keep
  the world if the walk recorded no error before finalize and nothing excludes it.
- World entry: (name, object reference, spec reference, `sys.path` when there is no object, path text, stat pair for
  a file read without an object). Validation reads `sys.modules` (the passed root object for the root), compares
  object and spec identity, `sys.path`, and stats only the files read without an object.
- `_extract_remembered_module_facts`: a loaded module looks up facts by object, spec and path without a stat; a
  module with no object stats first, as before, and notes its guard for the world.
- `_walk_module_dependencies`: a leaf record is skipped when the identical leaf record is the last one made for that
  name in this pass; a current-node record clears that marker.

## Edge and Error Semantics
- Every guard compares; any mismatch is a miss that walks and replaces the entry. Validation never raises: an
  object without a readable spec counts as a spec of None.
- A failed read or parse leaves walk errors before finalize, so that world is not kept; cycle reports from finalize
  are deterministic and stay in the kept payload.

## Invariants and Idempotency
- One class RLock serializes the maps; validation stats run outside it. The kept payload is never handed out: a hit
  copies it into a new result.
- Skipping an identical leaf record leaves the result's state unchanged, because recording the same leaf again only
  rewrites the same values.

## Explicit Non-Goals
- No reuse across processes, no time window, no file watching, no shared result objects between crystals.
