# Document index publication: control flow

## Trigger
Concurrency-sensitive lazy publication with a two-field readiness contract.

## Control flow
When the section marker is None, import the shared section rows, construct the local tuple, construct
and assign the read-only key map, then assign the section marker last. Return the two completed values.

## Error and retry semantics
Mapping construction must finish before either publication assignment. An exception leaves the marker
unready, propagates to its caller and permits another call to rebuild. No fallback or new lock.

## Invariants
Every non-None section marker implies a complete key map. Builders never mutate published data;
equivalent first-use rebuilds are permitted, while warm calls reuse the populated index.

## Non-goals
No exactly-once construction promise, global cache, import-order change or cursor sharing.

## Verification
Use Events to force the failure window, not sleep-based timing. Always release the blocked builder in
finally and use bounded waits so a failing assertion cannot strand worker threads.
