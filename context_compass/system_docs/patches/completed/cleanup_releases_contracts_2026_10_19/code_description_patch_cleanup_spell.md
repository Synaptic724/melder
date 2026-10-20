# code_description_patch_cleanup_spell

## Metadata
- Patch ID: cleanup_releases_contracts_2026_10_19
- Component: Conduit.cleanup_spell, Spellbook._dispose_spell, ConduitWard._emit_spell_disposed
- Status: active
- Owner: user
- Created: 2026-10-19T11:20:00Z
- Updated: 2026-10-19T11:20:00Z

## Trigger Justification
- Ordering-sensitive: the contracts must change after the Book's decision and before its disposal, with the Book's
  in-flight mark held and no Book lock held; a refusal must change nothing.

## Control-Flow Description (Pseudocode Level)
1. `Conduit.cleanup_spell(spell)`: check cleaned; `ward = self._spellbook._conduit._conduit_ward`.
2. `index_id = Book._dispose_spell(spell, release_contracts=ward._emit_spell_disposed)`:
   1. Book lock: refuse an overlapping call; owned, active, sole; mark the spell id in `_disposing_spell_ids`.
   2. Refuse (not owned / disposed / active member of a multi-member index) - nothing touched.
   3. try: `release_contracts(spell_id)` (no Book lock held) -> for each contract of the root ward holding a Detail
      for the version: `_uncontract_member_spell` (Detail, borrower entry, borrowed id; rule-2 mark for an active
      entry) -> contract records.
   4. The disposal as before (active: invalidate, `cleanup_and_remove_spell`; parked: maps, member, index if
      emptied, the Spell); return the destroyed index's id or None. finally: clear the mark.
3. If an index id came back: `ward._emit_index_destroy(index_id, ())` - the borrowers' tracked index, the
   IndexDetail, the contract records.
4. `Spellbook.cleanup_spell(spell)`: conjured -> `self._conduit.cleanup_spell(spell=spell)`; else `_dispose_spell`.

## Edge/Error and Rollback Semantics
- A refusal raises before step 2.3: no contract changes.
- A raise in step 2.3 propagates; nothing is disposed; the mark is cleared; a retry repeats steps 2.1-2.4.
- A link or grant that lands between steps 2.3 and 2.4 can still file the version (no transaction orders them;
  pre-existing).
- A lesser conduit's call reaches the root's contracts through the Book's root conduit.

## Invariants and Idempotency Expectations
- Each version leaves each contract once: the in-flight mark refuses a second call while the first runs, and a
  disposed version is refused after.
- An empty contract stays (a live link with nothing shared).

## Explicit Non-Goals
- `Spell.cleanup()` / `cleanup_and_remove_spell` doors; serializing the cleanup against links.

## Validation Focus Points
- The borrower's removal sees the lender's version live (order).
- A refused cleanup leaves every borrower record in place.

## Context / Handoff Summary
- What changed: the cleanup releases every contract of the version first, from every cleanup_spell door.
- Remaining unknowns: none for the change; the K6 doors are recorded for the owner.
- Next entrypoint: the tests, red on 0.2.8260.
