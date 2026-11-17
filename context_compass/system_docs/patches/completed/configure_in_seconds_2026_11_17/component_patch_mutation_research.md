# component_patch_mutation_research

## Metadata
- Patch ID: configure_in_seconds_2026_11_17
- Component: MutationResearch research set, root emission and twin (`mutation_research/research_set/`,
  `mutation_research/mutation_research.py`, `crystallizer/crystals/mutation_research_crystal.py`)
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Ticket: https://github.com/Synaptic724/melder/issues/331
- Created: 2026-11-17T12:05:00Z
- Updated: 2026-11-17T12:32:22Z

## Component Purpose and Boundary
- The research set records every spell version entering the world (lanes, residence, journal, undo ring); the
  root re-emits its persistence twin after every mutating verb. Both stay; what changes is the cost of each
  append and each emission.

## Before/After Behavior Summary
- Before: a fresh world entry described every lane and node under the set lock and serialized and hashed the whole
  organization into the undo ring; after release, the root described every set again (organization plus the
  200-entry journal window) and the twin derived one row per node at construction. Node and journal-entry
  describes deep-copy their metadata on each call. Cost per entry grew with the set: quadratic over a configure.
- After: an append builds its node's payload once (one describe), its journal entry's payload once, and one
  residence claim; the ring is marked stale instead of minted; the root emits a twin holding views - references to
  the append-only parts with their lengths at emission - and the twin materializes them on its first read,
  deriving its rows then. Emission costs O(lanes); a read costs what a describe cost before.

## Interface Deltas
- `ResearchLane`: keeps `_node_payloads`, aligned with `_node_order`; appended by `_add_node` and by hydration,
  rebuilt (a new list) by `_detach_nodes`; `_payload_view()` returns the lane's header values, its tip, the list
  and its length. Cleanup drops the list without clearing it.
- `ResearchJournal`: keeps `_entry_payloads`, appended by `record` and by hydration; `_payload_view()` returns the
  list, its length and `next_sequence`.
- `ResidenceRegistry`: keeps `_claim_log`, a list of (identity, lane_id) pairs in the order of its mapping;
  `claim` appends, `_rollback_claim` pops the claim it undoes, `transfer` and hydration rebuild it;
  `_payload_view()` returns the list and its length.
- `NetworkVersioner`: keeps its `describe()` payload and its address list from the last mint (rebuilt by each
  `snapshot` and by hydration); `_payload_view()` returns them.
- `ResearchSet`: `_ring_stale`; `_mint_pending_snapshot_locked()`; `_composition_view()` (under the set lock: the
  set's identity fields and each structure's view, lanes in `lane_id` order). `describe_composition()` keeps its
  full-describe path and contract.
- `MutationResearch`: `_emit_research_composition` passes `composition_view` (set name -> set view) instead of
  `describe_research_composition()`.
- `MutationResearchCrystal`: a keyword `composition_view`; with it, `composition_payload`, `research_nodes`,
  `grouped_research_nodes` and `describe()` materialize the view once (under the twin's lock) and serve the result
  as before. The `composition_payload` path (configuration docking, tests) is unchanged.

## State and Lifecycle Deltas
- Parts are value structures owned by their structure; views are tuples of references and ints owned by the twin.
  A view keeps its lists alive after the structure is cleaned or replaced, so a twin still describes what it was
  emitted for.
- `_ring_stale` starts False; appends (`record_world_entry`, `register_spell`, `register_group`,
  `recompose_group`) set it; every mint clears it.

## Failure Mode Deltas
- A twin read after its structures were cleaned still materializes (the parts outlive them); a read after the twin
  itself was cleaned raises as before.
- The ring can lag the organization between an append and the next mint; `describe_composition()` and the twin
  report that lag honestly (the ring as of its last mint). Hydration mints at load, as before.

## Dependency and Ordering Constraints
- Lock order unchanged: emission -> root -> set -> structure. `_composition_view()` reads under the set lock; the
  structures' views are taken under their own locks inside it. Materialization takes no MutationResearch lock.

## Validation Expectations
- After 600 world entries, the last entry builds one node payload and one journal payload and mints nothing (counted
  describes and versioner snapshots), and the twin materializes equal to `describe_composition()`.
- A restore to the snapshot minted before `join` (or `archive`) after appends rebuilds the organization as it was;
  `network_snapshot_shas()` after N appends shows one new address; `describe_composition()` mints nothing.
- A twin emitted before a restore, and one emitted before the root's cleanup, still materialize their composition.
- The existing MutationResearch, crystallizer and twin suites stay green; pins asserting a snapshot per append move
  to the lazy rule.

## Unknowns and Open Decisions
- None open.

## Context / Handoff Summary
The append path pays O(1); the read path pays what describe paid. Views over append-only parts make the twin
consistent without copying at emission.
