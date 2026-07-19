# Component Patch: link identity + journal rows (S1)

Lane: parallel_restore_ulid_identity_2026_07_18. Ticket: STORY-2026-07-18-link-identity-journal-rows.

## Before
- link() wires initiator -> target; the relationship has no identity. Checkpoints record it
  as a link_targets id list inside the initiating conduit's crystal payload; replay scans
  initiators and re-links by translated conduit ids (restore_engine.py:1590-1612).
- Unlink precision at fold time is entangled with whole-conduit payload rewrites; a link
  cannot be tombstoned as itself.

## After
(FINAL - third correction 2026-07-18, IMPLEMENTED: link identity ALREADY EXISTS. Every
initiated link is materialized by a Contract minting its own ULID
(contract.py:60, IDBuilder.create_id()); the ward indexes target_conduit_id ->
contract._id (conduit_ward.py:75, 181, 815); the contract twin records
(contract_id, conduit_a_id=initiator ward id, conduit_b_id=target) at emission
(crystallizer.py:933-937). No ward change, no twin change, no record-format change -
the only genuine gap was replay-side identity coverage.)
- _replay_links (restore_engine.py) now builds a folded lookup
  (initiator_recorded_id, target_recorded_id) -> recorded contract ULID from the folded
  contract twins, and after each successful public link() maps recorded contract ULID ->
  the fresh contract ULID the live ward minted (read from the initiator ward's initiated
  index - the engine's existing identity seam posture). Links are now locatable through
  the identity map like every identity-bearing unit.
- Legacy tolerance: an edge with no folded contract twin rebuilds without a mapping entry;
  nothing is under-built, no shortfall. Missing live target keeps the existing
  link_target_not_rebuilt shortfall.
- The S4 planner consumes folded CONTRACT twins as its link/contract graph nodes and edges
  (contract_id node; edges to both endpoint book-chains); conduit link_targets contributes
  initiation direction only.

## Interface Deltas
- restore_engine._replay_links: mapping enrichment only (implemented 2026-07-18).
- ConduitWard / Conduit twin / ConduitCrystal / PersistenceSystem: UNCHANGED.
- RestoreReport: links gain identity-map entries (kind string "link" unchanged).

## State / Failure Deltas
- Ward link registry gains link-id keying; cleanup unchanged (del posture).
- Failure: dangling target -> shortfall row (same as today); duplicate link_id in a folded
  chain -> later-wins (journal law), no error.

## Dependency / Ordering
- No dependency on S2/S3/S4; lands first. S4 consumes link rows as unit boundaries.

## Validation Expectations
- Round-trip: link -> checkpoint -> restore -> identity map contains the link row; re-emitted
  world records fresh link ids. Tombstone: unlink -> fold -> absent. Legacy compat: old
  chain restores identically. Density >= 10 tests/100 LOC on touched surfaces.
