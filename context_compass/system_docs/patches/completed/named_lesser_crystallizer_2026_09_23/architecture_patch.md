# Named lesser structural persistence

## Objective and Boundaries
Persist named lesser structure through the existing passive record and public-verb restore. Retain
stage-1 directory semantics, no application instance data, no Nexus work and no packaged generation.

## Selected Representation
ConduitCrystal keeps its existing family and configuration_payload. A lesser carries conduit_state,
root_conduit_id, parent_conduit_id and lineage_ancestors ordered from root to immediate parent.
Each ancestor is a detached plain-value row naming its id, name, parent and policy. Named ancestors
must have their own recorded twin. Unnamed ancestors are supporting structure owned by the named
record, not independent live record entries. Removing/replacing that named record retires its support
snapshot automatically. Shared support ids are reconstructed once, with conflicting snapshots refused.

This preserves the flat named record and the one-check unnamed pool route. No reference counter,
unnamed cleanup flag, runtime world walk or callback-bearing carrier is added.

## Record and Replay
- Add conduit_removed through facade -> record -> profile -> journal/capture -> folded store.
- Named creation emits after attachment/discovery, under the child's existing lifecycle lock.
- Named return removes its record before clearing the name/publishing idle. Normal cleanup also
  removes its own recorded id, covering promotion failure before a replacement root twin emitted.
- Conduit and checkpoint payload APIs deeply detach nested values, matching their existing contracts.
- Shared topology analysis validates and expands supporting ancestors, with parent-first replay order.
- Root selection is explicit. Both restore drivers reconstruct lessers in their common per-Book unit.
- Names use ordinary admission. skip_existing may create an unnamed lesser and report that lost name;
  it must not borrow an unrelated existing object as the restored child.
- RecordVersion advances to 3.0.0. Older root-only records remain readable; major-2 readers refuse
  child-bearing major-3 envelopes. This does not bump the Melder package version.

## Concurrency and Failure
Directory locks never cover recording. The named child's lock serializes emit/remove/reuse; ordinary
unnamed cycles do not enter recorder logic. Existing load authority does not drain ordinary scope
cycles: callers must quiesce scope acquisition/return around live restore. No new global gate is added.
Replay failure uses the existing reverse-build cleanup. Invalid hierarchy refuses before public replay.

## Qualification
Capture/remove/reuse within and across windows; sealed history isolation; nested named/unnamed parents;
shared ancestors; both drivers; fresh ids/empty creation stores; promotion; formations and version gates.
