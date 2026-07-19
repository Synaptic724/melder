# code_description_patch_frame_acl_configuration_chain

## Trigger justification (why this file is required)
The chain adds lifecycle semantics that later builder and propagation work will
depend on: head insertion, current selection, rollback, and tail trimming.

## Control-flow description (pseudocode level, not production code)
1. Container creates chain with one default config.
2. Manager resolves the container for a frame.
3. New committed config:
   - validate config node shape
   - insert at head
   - optionally move current
   - trim tail if over limit
4. Rollback:
   - select a historical config id
   - move current to that id
5. Listing:
   - walk from head to tail through previous ids

## Invariants and idempotency expectations
- one default config exists immediately
- head insertions are append-only at the front
- tail trimming is the only delete behavior
- chain order is newest-first

## Validation focus points
- head/current correctness
- rollback correctness
- bounded history trim
