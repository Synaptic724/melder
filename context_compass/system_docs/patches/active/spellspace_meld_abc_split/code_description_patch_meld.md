# code_description_patch_meld

## Metadata
- Patch ID: spellspace_meld_abc_split
- Component: meld
- Status: draft
- Owner: codex
- Created: 2026-05-30T10:46:42Z
- Updated: 2026-05-30T10:46:42Z

## Control Flow Commitments
- Shared base keeps:
  - spell identity resolution
  - override normalization
  - structural gating
  - deferred resolution
  - contract revalidation
  - compiler-system access
- Concrete subclasses own:
  - front-door legality checks
  - runtime storage selection
  - live-creation probe semantics

## Edge / Error Semantics
- Base class must not be directly instantiated by runtime construction after
  the split.
- Spellspace-required requests are only legal on the spellspace front door.

## Concurrency / Locking
- Shared lock remains on the base class unless the refactor proves a separate
  lock topology is needed.
- Spell-owned locks remain the gate for structural/deferred resolution paths.

## Non-Goals
- No backend executor rewrite in this patch.
- No transfer semantics rewrite in this patch.
