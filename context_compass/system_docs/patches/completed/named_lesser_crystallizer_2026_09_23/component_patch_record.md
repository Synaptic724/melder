# Named record lifecycle and capture

## Before / After
The record stores root ConduitCrystal rows and has no conduit-only tombstone. Extend the same family
to named lessers, with parent/root and value-only supporting ancestry. Book/frame sweeps keep their
existing parent-edge semantics; removal of one lesser never evicts its borrowed Book.

Crystallizer.emit_conduit_removed is an inactive no-op and thin facade; PersistenceSystem delegates
to the active profile; PersistenceProfile removes one id and journals conduit_removed. Capture emits
the same id/removal tombstone shape used by other families. Fold pops one conduit id. Final-payload
windows still resolve emit/remove/emit correctly in journal order, including a reused pooled id.

## Payload Ownership
ConduitCrystal construction/getter/describe must detach nested ancestry values. PersistenceCrystal
construction/replay_data/to_cached_item must detach nested captured payloads too; callers must never
mutate a sealed checkpoint by editing an exported ancestor row. No live references cross these APIs.

## Formations
Root anchor includes named descendants on that root. Lesser anchor includes its named subtree and
required named ancestors/root, retaining each selected row's supporting unnamed ancestry. Shared Book
custody/index state remains one subtree. Frame capture already selects every recorded Book/conduit.
Selection does not import loader/analysis objects into the record, preserving the V3 edge law.

## Validation
Pure record unit tests plus real emitted checkpoints prove removal/reuse/history. Mutating constructor
inputs, described data, replay data or cached items must not change held ancestor values.
