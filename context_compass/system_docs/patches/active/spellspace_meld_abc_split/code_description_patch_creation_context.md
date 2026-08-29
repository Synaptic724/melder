# code_description_patch_creation_context

## Metadata
- Patch ID: spellspace_meld_abc_split
- Component: creation_context
- Status: draft
- Owner: codex
- Created: 2026-05-30T11:08:16Z
- Updated: 2026-05-30T11:08:16Z

## Control Flow Commitments
- Spellspace route emitted code must use direct spellspace-owned storage for:
  - existing creation probe
  - miss/create lock path
  - registration path

## Edge / Error Semantics
- Spellspace route still errors when no spellspace-owned store is available.
- Caller/conduit/shared routes retain their existing ownership semantics.

## Concurrency / Locking
- Spellspace route uses the spellspace-owned store lock directly.

## Non-Goals
- No transfer semantics rewrite.
- No pooling semantics rewrite.
