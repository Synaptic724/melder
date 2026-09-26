# code_description_patch_conjure_cache_restage

## Metadata
- Patch ID: stable_callable_spell_ids_2026_09_26
- Component: SpellbookCreationSystem._stage_spell_payloads_at_conjure_end
- Status: active
- Owner: user (writer: melder_1)
- Created: 2026-09-26T10:42:41Z
- Updated: 2026-09-26T10:42:41Z

## Control Flow
1. Guard: no caching system in cache_state -> return (caching disabled).
2. Snapshot the cached id view (tuple) because the loop mutates the store; remove each payload
   (CachingSystem.remove_spell_payload, under its lock); remember whether anything was removed.
3. For each live payload-eligible id in sorted order, call Spellbook._emit_spell_cache (unchanged: it
   skips disabled/foreign spells, refuses non-replayable plans, upserts and flags emission on success).
4. If anything was removed, set Spellbook._cache_emit_required so the conjure-end emit persists the pruned
   bundle even when nothing re-staged.

## Edge / Error Semantics
- A build failure for one spell is logged by _emit_spell_cache and leaves that spell uncached (it compiles
  next conjure); other spells are unaffected.
- Emission failure keeps the existing behaviour (logged at conjure end, flag restored for retry).
- full_hit conjures do not call this function; their bundle is unchanged.

## Invariants / Idempotency
- Re-running the function in the same conjure yields the same bundle (remove-all then stage-all).
- Sorted staging makes the marshalled bundle byte-order deterministic for a given world.

## Explicit Non-Goals
- No change to classification, to full-hit loading, to hydration or to meld-time staging.
