# code_description_patch_nexus

## Trigger justification (why this file is required)
This refactor changes the internal state topology of Nexus, not just one method
body. The migration needs a staged control-flow description so the first slice
does not sprawl.

## Control-flow description (pseudocode level, not production code)
1. Nexus receives a frame-scoped publish/update event.
2. Resolve or create the `FrameDescriptor` for that frame.
3. Update the nested descriptor-owned state instead of flat Nexus fields.
4. Keep current public/internal behavior unchanged while migration is partial.
5. Only after a slice is validated, remove the superseded flat state.

## Edge/error behavior and rollback semantics
- Missing descriptor:
  create it
- Partial migration ambiguity:
  fail fast or stop the slice; do not silently fork state

## Invariants and idempotency expectations
- One descriptor per frame
- Descriptor remains the single frame-scoped aggregate once a given field
  migrates
- No dual source of truth for migrated fields

## Explicit non-goals
- This file does not define final ACL schema
- This file does not define final viewer contract
- This file does not define mutation semantics

## Validation focus points
- validate descriptor creation/lookup
- validate migrated fields stop using flat Nexus state
- validate current publish paths still behave the same after each slice
