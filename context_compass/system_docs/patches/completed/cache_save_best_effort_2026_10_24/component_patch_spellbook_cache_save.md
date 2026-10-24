# Component patch: Spellbook cache save after a refusal

Patch id: cache_save_best_effort_2026_10_24. Component: Spellbook Core, the cache save
(src/melder/aether/spellbook/spellbook.py). The public explicit save on Spell is its own component patch,
component_patch_spell_emit_cache_file.md. Author: melder_0, 2026-10-24.

## Component purpose and boundary
- Current boundary: the Spellbook owns its CachingSystem and decides when the bundle is saved: the save flag
  `_cache_emit_required` (set by staging, cleared under the Book lock before a save) and the one save seam every meld
  door, the end of conjure and the explicit save call.
- Target boundary: unchanged. The seam MUST pass a refused save on as False and MUST NOT restore the flag for it.

## Before
`_emit_cache_file_if_required()` clears `_cache_emit_required` under the Book lock, calls `CachingSystem.emit()` and
returns True; on any exception it sets the flag again and re-raises. The nine meld-door call sites and
`_emit_cache_file` (to which the public `Spell.emit_cache_file()` delegates) do not catch, so an OS refusal fails the
meld after its object was built and, while the refusal lasts, every meld of the Book. The end-of-conjure save
(`SpellbookCreationSystem._emit_conduit_cache_file_at_conjure_end`) logs the failure and leaves the flag set, so the
first meld retries the save.

## After
- `_emit_cache_file_if_required()` returns what `emit()` returned. A refused save is False: the flag stays cleared,
  so no meld retries it or waits, and the payloads stay staged in the CachingSystem for the next staging's or
  conjure's save.
- Any other exception still restores the flag and propagates.
- `_emit_cache_file` returns False for a refused save (D2); its docstring says when it returns False: caching off,
  nothing staged since the last save, or a refused save.
- Unchanged: the meld doors (they ignore the result) and the end-of-conjure save, which now gets False for a refusal
  instead of an exception and leaves the flag cleared.

## Interface deltas
- Inputs: none.
- Outputs: `_emit_cache_file_if_required()` and `_emit_cache_file()` return False for a refused save.
- Error semantics: `_emit_cache_file_if_required()` raises only non-OS errors (flag restored), as before.

## State and lifecycle deltas
- None: the flag keeps its meaning (a save is owed); a refused save clears it like a written one.

## Failure mode deltas
- Removed: a meld at any door, a managed lease or a spellspace meld failing with the OSError of a refused save; a
  managed lease lost because its meld's save was refused.
- Changed: after a refused end-of-conjure save the first meld no longer retries it; the bundle is written at the
  next staging in this process or by the next process's conjure.

## Dependency and ordering constraints
1. CachingSystem's `emit() -> bool` lands with or before this change.
2. The flag is cleared under the Book lock before the save, as today, so two melds never save the same window twice.

## Validation expectations
- T1-T5, the component regression tests (eight cases), green the GIL off and on.
- Unit: the stub's `emit()` returns True and the emit-once test passes; a refused save returns False with the flag
  cleared and one emit; no save again before new staging; the end-of-conjure save leaves the flag cleared after a
  refusal; `Spellbook._emit_cache_file` returns True for a written save and False for a refused one.

## Unknowns and open decisions
- UNKNOWN: none.
- DECISION_REQUEST: none (D1 and D2 answered).

## Context / Handoff Summary
- What changed: the meld doors no longer see an OS refusal; the explicit save reports it as False.
- Remaining risks: none known beyond the CachingSystem patch's.
- Next entrypoint: the task's mapping note, then the src change.
