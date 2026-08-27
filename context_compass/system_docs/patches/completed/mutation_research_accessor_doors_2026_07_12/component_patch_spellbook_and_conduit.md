# Component Patch: Spellbook and Conduit MR Accessor Doors
# (mutation_research_accessor_doors_2026_07_12)

## Spellbook Core (Binding and Conjure)

### Before
- Holds `_crystallizer` as a private emit-only reference
  (spellbook.py:230, del :452, tombstone :641).
- Touches MR only through two non-constructing record seams reading
  `Spellbook._aether._mutation_research` (spellbook.py:4384, :4415);
  no stored reference, no public accessor.

### After
- `__slots__` gains `"_mutation_research"` beside `"_crystallizer"`.
- `__init__` binds `self._mutation_research = Spellbook._aether.mutation_research`
  immediately after the crystallizer bind; annotation uses the truthful concrete
  type via a `typing.TYPE_CHECKING` import (no quotes, no fallback alias).
- New public read-only property `mutation_research`: `check_cleaned()` then return
  the bound root. Rank-5 docstring states: borrowed WORLD-scoped root, identical
  object to `Aether().mutation_research`; activation/liveness enforced by the
  root's own verbs, never by this door.
- `_cleanup_components`: `del self._mutation_research` beside `del self._crystallizer`.
- `_cleanup_core`: `self._mutation_research = None` beside the existing
  `self._crystallizer = None` tombstone (exact pattern parity).
- Record seams UNCHANGED (still peek, still never construct, still no-op unless the
  root is live and activated).

### State / Failure Deltas
- New owned slot holding a borrowed reference; no new locks.
- Spellbook() now raises RuntimeError when the MR root was cleaned under a live
  Aether (aether.py:1602-1612 contract) - fail-fast, surfaced at construction.
- First Spellbook() in a process builds the inactive MR root (one-time import chain
  + thin registry object; zero recording while unactivated).

### Dependency / Ordering
- Bind happens after `_ensure_frame` and the crystallizer bind, before transaction
  identity assembly.
- Cleanup deletes the borrowed reference in the same passes that handle
  `_crystallizer`; the MR root itself is never cleaned from here.

## Conduit Runtime (Normal and Lesser)

### Before
- Holds `_crystallizer` bound from the owning spellbook (conduit.py:248, del :794).
- `get_mutation_research()` door DELETED 2026-07-11 (NOTE at conduit.py:2947-2950).

### After
- `__slots__` gains `"_mutation_research"` beside `"_crystallizer"`.
- `__init__` binds `self._mutation_research = spellbook._mutation_research` beside
  the crystallizer bind (lesser conduits inherit the same root through the shared
  spellbook; upgrade path needs no extra wiring - the field rides the instance).
- New public read-only property `mutation_research` placed at the old door site;
  same rank-5 world-scoped/borrowed docstring contract as Spellbook.
- The 2026-07-11 deletion NOTE is UPDATED (never deleted) to record the 2026-07-12
  owner reversal and the new borrowed-door contract.
- Cleanup: `del self._mutation_research` beside `del self._crystallizer` (:794).

### State / Failure Deltas
- New owned slot holding a borrowed reference; no new locks, no gate interaction.
- No new failure mode beyond Spellbook's: by conduit construction time the
  spellbook field is always populated.

### Dependency / Ordering
- Conduit binding depends only on the owning Spellbook's field (already bound).
- Doors add zero interaction with CreationGate, Meld, ward, or the transaction plane.

## Validation Expectations
- Unit rows (pytest): identity through both doors and Aether; lesser-conduit
  identity; no activation side effect from binding; post-cleanup check_cleaned
  raise on both properties; cleaned-root RuntimeError at Spellbook construction.
- Agent reports "Not run." for anything not executed; owner runs the 3.14t tree.
