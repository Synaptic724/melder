# Component patch: Spell explicit cache save

Patch id: cache_save_best_effort_2026_10_24. Component: Spell, the public explicit save `Spell.emit_cache_file()`
(src/melder/aether/spellbook/spell.py). Author: melder_0, 2026-10-24.

## Component purpose and boundary
- Current boundary: `Spell.emit_cache_file()` is the spell-facing public entry for saving the owning Spellbook's
  in-memory cache; it checks the spell is live and cached, then delegates to `Spellbook._emit_cache_file`.
- Target boundary: unchanged. The method's code does not change; its documented result does (D2).

## Before/after behavior summary
- Before: a save the operating system refused raised its OSError (PermissionError, for example) out of this call.
- After: the call returns False for a refused save; the Spellbook's cache utility logs it and keeps the staged cache
  in memory for the next save. True still means the bundle was written.

## Interface deltas
- Inputs: none.
- Outputs: False also covers a refused save, beside caching off and nothing staged since the last save.
- Error semantics: an OSError of the save MUST NOT escape; `RuntimeError` for a Spell with no owning Spellbook and
  the cleaned-object error stay as they are.

## State and lifecycle deltas
- None.

## Failure mode deltas
- Removed: the explicit save raising for a read-only cache folder, a full disk or a Windows sharing refusal.
- Changed: a caller that caught the OSError now reads False (a Breaking change for the release note).

## Dependency and ordering constraints
1. Lands with the Spellbook seam's change (component_patch_spellbook_cache_save.md), which produces the False.

## Validation expectations
- A unit test calls `Spell.emit_cache_file` over a Book whose save is refused and gets False with one save attempt.

## Unknowns and open decisions
- UNKNOWN: none.
- DECISION_REQUEST: none (D2 answered: return False and log).

## Context / Handoff Summary
- What changed: the docstring states the result for a refused save.
- Remaining risks: callers that relied on the exception; the release note names the change.
- Next entrypoint: the task's mapping note.
