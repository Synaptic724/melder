# Named lifecycle ordering and failure contract

## Directory locking
Frame mutation may enter Cloud under frame -> Cloud order. Named attachment uses parent -> child ->
ward/link, releases the ward lock, then Cloud. Return already holds its child lock and enters Cloud
only after disposal/detach. No Cloud helper calls a frame, ward, callback, logger or recorder.
Existing unrelated lock-order issues are not expanded or redesigned by this patch.

## Acquisition
1. Validate optional name before side effects.
2. Acquire/build unnamed shell; assign requested label when present.
3. Existing activation hook remains before attachment and advisory exceptions remain swallowed.
4. Named link rechecks parent and child liveness/state, attaches, then atomically admits the name.
5. Collision/failure cleans the uncommitted shell outside Cloud's lock; no other entry is removed.
6. Post-created runs after discovery publication. User-driven teardown may already retire its scope.

## Retirement
Existing Space/Creations disposal -> recursive ward detach -> one name conditional -> named-only
unregister plus None assignment -> existing pooled state and hooks -> idle deque. There is no separate
name helper call, lock or lookup on the unnamed branch. Incomplete disposal does not publish idle.

## Promotion
Both old and requested names exclude competitors while preparation runs: the old name remains a
live entry, the requested one is a private claim. Same-name promotion is legal. Final root registration
atomically exchanges the old directory alias; frame root ownership then commits. Finally releases the
claim regardless of failure. Before attachment the old entry remains; after attachment normal cleanup
retires whichever alias belongs to this id, including an old alias if root publication failed.

## Non-goals
No lease tokens, graph traversal in naming, Meld checks, callback serialization, new recording payloads,
new Nexus refresh, or broad hot-path locking. No claim that borrowed objects remain valid after cleanup.
