# code_description_patch_mutation_research_twin

## Metadata
- Patch ID: configure_in_seconds_2026_11_17
- Component: MutationResearch parts, views and twin
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Ticket: https://github.com/Synaptic724/melder/issues/331
- Created: 2026-11-17T12:05:00Z
- Updated: 2026-11-17T12:32:22Z

## Control Flow Commitments
- Append (`record_world_entry`, `register_spell`, `register_group`, `recompose_group`), under the set lock: claim
  residence (log append), add the node (lane `_add_node` appends the node's single describe payload), record the
  journal entry (its payload appended), set `_ring_stale`. After release, `_notify_mutation()` as before.
- Organizing verb (`create_lane`, `attach`, `detach`, `join`, `archive`, `restore_network`), under the set lock:
  `_mint_pending_snapshot_locked()` first, then the verb's own steps and its closing `_snapshot_locked()` as today.
- Ring reads (`snapshot_network`, `network_snapshot_shas`, `latest_network_snapshot`) take the set lock and mint a
  pending snapshot before reading. `describe_composition()` mints nothing.
- Emission: the root, under the emission lock and then the root lock, builds {set name: `_composition_view()`}; each
  set view is taken under the set lock (and each structure's own lock). The twin stores the view; its first read
  takes the twin's lock, materializes the payload in the `describe_composition()` shape, derives the rows, and drops
  the view; later reads serve the materialized payload exactly as the payload-built twin does.

## Edge and Error Semantics
- `_rollback_claim` removes the claim it undoes from the log (searching from the end), so a refused add leaves log
  and mapping equal. `transfer` rebuilds the log from the mapping after its updates.
- Materialization copies every node and journal payload it emits (lists and non-empty metadata copied), so a
  caller mutating a read never reaches the live parts.
- Materialization reads list prefixes (`parts[:length]`), never a live dict, so a concurrent append cannot make it
  raise; parts are never cleared or edited in place.

## Invariants and Idempotency
- The materialized twin equals `describe_composition()` for the same state; repeated reads return equal payloads.
- A node's payload is built once; a lane's payload list stays aligned with its node order.
- Minting a pending snapshot is idempotent: content addressing de-duplicates, and a mint clears the flag.

## Explicit Non-Goals
- No change to the twin's recorded shape, the journal window size, the ring size or restore semantics; no
  coalescing of emissions; no change to the configuration docking path.
