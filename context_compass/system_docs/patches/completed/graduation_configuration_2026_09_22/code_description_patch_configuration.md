# Configuration hook publication and failure contract

<!-- BEGIN ENTRY: "Hook defaults publication" -->
## Control flow
1. Configuration initializes Bind seed storage to three empty immutable tuples.
2. add_bind_hooks normalizes incoming sequences and checks every callback before taking the lock.
3. Under the existing config lock, check cleaned/frozen again and publish one new tuple set.
4. clear/get use the same existing lock; callbacks never run while configuring defaults.
5. Book construction creates Bind with the selected tuple set. Runtime Bind add/clear creates new
   tuples, so it cannot alter the selected config or a sibling's callback registry.
6. Default Conduit/Meld maps use the existing registry with None as the default key. A getter checks
   default and specific maps: return the sole map directly, or merge with per-event specific wins.
7. Existing record emission includes effective event keys and current Book Bind markers only.

## Failure and lifecycle
Invalid callback batches publish nothing. Frozen/cleaned config refuses default mutation. Cleanup
drops config-owned callback containers without cleaning callable objects or an already-created Bind.
No callable serialization, callback identity hashing, runtime getter polling or added Meld locks.

## Implementation mapping
Configuration slots/init/cleanup + new methods -> callback storage and lifecycle tests.
Bind constructor + Book constructor -> normal and shared-Book initial callback behavior.
Runtime hook getters and recording producer -> default/specific events and marker checks.
Graduation adopts an empty Book per the owner's resolved definition boundary; no inherited visibility.
<!-- END ENTRY: "Hook defaults publication" -->
