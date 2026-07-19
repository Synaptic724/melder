# code_description_patch_creations

## Metadata
- Patch ID: creations_plain_ref_disposal_split
- Component: creations
- Status: draft
- Owner: codex
- Created: 2026-05-26T22:36:42Z
- Updated: 2026-05-26T22:36:42Z

## Trigger Justification
- `Creations` owns mixed storage, disposal stacks, transfer extract/restore,
  and pool reset. Changing the stored-entry shape changes control flow and
  rollback semantics directly.

## Control-Flow Description (Pseudocode Level)
1. On add/register:
   - if disposal methods exist, create `Creation` and store it
   - else store raw object directly
2. On retrieval:
   - if stored entry is `Creation`, return `.value`
   - else return the raw object
3. On extract/restore:
   - move stored entry shape without losing whether it is raw or disposable
4. On cleanup/reset:
   - explicitly dispose only stack-enrolled entries
   - clear plain retained storage directly

## Edge/Error and Rollback Semantics
- Edge case 1:
  spellspace bucket may contain mixed raw and disposable entries.
- Error behavior 1:
  duplicate key and wrong bucket-shape errors remain unchanged.
- Rollback behavior:
  transfer extract/restore must preserve the stored-entry shape exactly.

## Invariants and Idempotency Expectations
- Invariant 1:
  disposal stacks only contain `Creation` entries.
- Invariant 2:
  non-disposable retained entries never need explicit disposal iteration.
- Idempotency condition 1:
  cleanup/reset remains safe on repeated calls.

## Explicit Non-Goals
- Non-goal 1:
  redesigning `many` retention behavior.
- Non-goal 2:
  changing spellspace ownership boundaries.

## Validation Focus Points
- Validation item 1:
  unique/shared/spellspace retrieval returns correct object type.
- Validation item 2:
  transfer extract/restore preserves plain-vs-disposable shape.

## Context / Handoff Summary
- What changed:
  control-flow patch doc established for the storage split
- Remaining unknowns:
  whether any stale tests assert universal wrapper identity
- Next entrypoint:
  implementation task
