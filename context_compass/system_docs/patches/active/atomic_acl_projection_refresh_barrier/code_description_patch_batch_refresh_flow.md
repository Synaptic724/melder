# Code Description Patch: Batch Refresh Flow

## Control Flow
1. ACL update produces one changed-frame sequence.
2. `Nexus` normalizes and dedupes the frame names.
3. `Nexus` computes impacted Rifts by frame-contract membership intersection.
4. If gate refresh is enabled:
   - disable each impacted Rift gate once
   - wait for each impacted Rift to drain once
5. For each impacted Rift:
   - compute the changed-frame subset that belongs to that Rift
   - ask Rift to refresh that subset in one call
6. Each Rift:
   - asks Nexus for one multi-frame projection subset
   - merges once into the room
   - rebuilds the viewer once
7. `Nexus` reopens each impacted Rift gate once.

## Error Semantics
- Empty changed-frame batches are invalid.
- Unknown or empty frame names in explicit batch scopes are invalid.
- Timeout while draining still raises immediately.
- Gates are reopened best-effort in `finally`.

## Idempotency / Non-Goals
- No second room-level batch coordinator.
- No duplicate single-frame orchestration logic left behind.
- No attempt to make the whole process a cross-Rift global transaction.
