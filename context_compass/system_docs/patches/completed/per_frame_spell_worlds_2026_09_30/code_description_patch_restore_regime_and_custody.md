# code_description_patch_restore_regime_and_custody

## Metadata
- Patch ID: per_frame_spell_worlds_2026_09_30
- Status: active
- Owner: user (agent melder_0)
- Created: 2026-09-30T17:18:12Z
- Updated: 2026-09-30T17:18:12Z

<!-- BEGIN ENTRY: "stage 1 decision table" -->
## Control Flow
1. No folded Aether payload, or an empty configuration payload: return (unchanged).
2. recorded = payload.get("process_wide_unique_spell_ids") (None for a pre-4.0 record); fixed = aether.configured or
   any live frame; live = aether.process_wide_unique_spell_ids.
3. fixed and recorded is not None and bool(recorded) != live:
   a. recorded False, live True and the folded custody binds one spell id in two frames: raise RuntimeError naming
      both regimes and the remedy (B).
   b. otherwise add shortfall ("aether", "process_wide_unique_spell_ids", reason) and set the payload's regime to
      live for any install below.
4. aether.configured: add `live_aether_already_configured_recorded_payload_skipped` and return (unchanged).
5. Rebuild through from_recorded_payload (report missing and code-participation keys), activate the configuration,
   activate Aether (unchanged).

## Edge / Error Semantics
- Step 3a raises inside the stage chain, so the report is marked failed at "aether_configuration" and the
  all-or-nothing teardown runs over an empty build stack: nothing was built.
- Which frame owns a custody entry: its payload "frame_name", else its Book's recorded frame, else "default".
- A pre-4.0 record never takes step 3 (its regime is unknown); its keys are spell ids, so step 3a cannot fire.

## Invariants / Idempotency
- Stage 1 installs at most one configuration and never one whose regime differs from a fixed live regime, so the
  0.2.8209 guard cannot fire from a restore.

## Explicit Non-Goals
- No live regime change; no per-frame restore into a process-wide world that already holds frames.
<!-- END ENTRY: "stage 1 decision table" -->

<!-- BEGIN ENTRY: "custody key lifecycle" -->
## Control Flow
1. Bind (active or staged) and transfer create a crystal from the live spell; the facade passes the per-frame flag,
   the crystal composes its key; the profile displaces and journals that key.
2. Park/promote and removal emit with the Book's frame; the facade composes the same key.
3. Checkpoint capture detaches payloads per key; fold applies entries per key (later wins, tombstones pop the key).
4. Replay groups custody by the payload's spellbook id, orders by the Book's bind_order through the id-to-key map,
   binds with the payload's spell id, and translates ids per Book.

## Edge / Error Semantics
- Per-frame emit without a frame: ValueError from the facade; every internal site passes one.
- A tombstone whose crystal is gone names its spell by splitting the key at the first "@".

## Invariants / Idempotency
- Replace-on-emit per key: a Book re-binding the same spell replaces only its own frame's copy.

## Explicit Non-Goals
- MutationResearch reads stay by spell id (either copy's module world is the same code).
<!-- END ENTRY: "custody key lifecycle" -->
