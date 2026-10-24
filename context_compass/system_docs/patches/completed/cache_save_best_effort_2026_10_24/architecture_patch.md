# Architecture patch: cache_save_best_effort_2026_10_24

Patch id: cache_save_best_effort_2026_10_24. Task: TASK-2026-10-24-cache_file_write_failure_fails_meld (standalone).
Author: melder_0 (synaptic_python_developer), 2026-10-24. The owner's go (chat 2026-10-24): "yeah go ahead with all
hte recommended things you need to do" - D1-D4 of the task's DECISION_REQUEST, taken as recommended.

## Objective
A creation-cache bundle is an accelerator: a missing or unreadable bundle already only makes the cache cold. A save
the operating system refuses must not fail the call that triggered it. Today `CachingSystem.emit()` raises the
OSError of its folder, temp write or rename, `Spellbook._emit_cache_file_if_required` restores its flag and
re-raises, and every meld door that saves (nine call sites in `Conduit.meld`, `ConduitMeld.meld`, `SpellSpace.meld`
and `SpellSpaceMeld.meld`) hands the error to its caller after it built and stored the object: a unique is stored
and returned by the next meld, a many is lost to its caller, a managed lease is stranded for good, and while the
refusal lasts every meld of the Book fails. On Windows a rename onto a bundle another handle holds open (an
on-access scanner, an indexer) is refused with [WinError 5] - the owner's failure - and the refused save leaves its
temp file behind.

## Non-goals
- Fewer meld-time saves (direction 3) and the cache location and frame-folder pruning (direction 4): follow-ups.
- The Windows cause of the owner's refusal (the task's HYPOTHESIS): unchanged, still to verify on his machine.
- The cache format: the envelope and its bytes are unchanged, so no cache generation moves.
- Conjure's end-of-conjure save keeps its own handling (it logs a failure and continues).

## Changed components
| component | change_type | rationale | depends_on |
| --- | --- | --- | --- |
| CachingSystem (`emit`, the write) | modify | the save becomes best-effort and Windows-robust | none |
| Spellbook (`_emit_cache_file_if_required`, `_emit_cache_file`) | modify | the meld doors never meet an OS refusal | CachingSystem |
| Spell (`emit_cache_file`) | modify (docstring) | its False now covers a refused save (D2) | Spellbook |

One component patch per row: component_patch_caching_system.md, component_patch_spellbook_cache_save.md and
component_patch_spell_emit_cache_file.md; code_description_patch_caching_system.md for the save's control flow.

## Interface deltas
- `CachingSystem.emit() -> bool` (was None): True when the bundle was written, False when the operating system
  refused the save (logged). It never raises OSError; any other error propagates.
- `Spellbook._emit_cache_file_if_required() -> bool` returns emit's result (internal).
- `Spell.emit_cache_file()` (public) returns False for a refused save where it raised the OSError (D2, a behaviour
  change for the release note). Its signature does not change.
- The temp file is `<conduit>.meldercache.<pid>.<thread id>.tmp` beside the bundle (was `<conduit>.meldercache.tmp`).

## Cross-component invariants
- A meld never fails because a cache save was refused; it returns its object, stored where its existence puts it.
- A refused save never changes the bundle on disk (the rename is the only step that replaces it) and leaves no
  temp file of its own; the staged payloads stay in memory, so the next save writes them.
- After a refused save the Book's save flag stays cleared: no meld retries the save or waits on it; the next
  staging (a newly published creation context) or the next conjure saves again.
- The first refused save of a bundle is logged at WARNING with the bundle path, the error and the remedies; later
  ones at DEBUG (D4).
- A rename refused with PermissionError is retried only on Windows: up to five attempts within about 100 ms, under
  the cache utility's lock (D3). POSIX renames do not refuse for sharing, so elsewhere a refusal is final at once.
- Two writers of one bundle - processes sharing a frame and root conduit name in one install - never write into one
  temp file.
- A non-OS error from a save restores the Book's flag and propagates, as today: it would be a Melder defect.

## Locks
- No new lock and no lock-order edge. The save runs under the CachingSystem's RLock as today; the Book lock is still
  taken only around the flag. On Windows a retried rename sleeps under the cache utility's lock, at most about
  100 ms, and only that Book's cache calls wait on it.

## Migration and rollout order
1. These patch docs and the task's mapping note.
2. CachingSystem: `emit()` and the write, with its unit tests.
3. Spellbook and Spell: the return value and the docstrings; the stub test and new unit tests.
4. Validation: the nine regression tests, the new unit tests, the related and full trees, the GIL off and on, and
   the task's probe A-D rerun.
5. src_architecture, src_components, the graph, the release note, the notch to 0.2.8266; closure; rebuild last.

## Rollback strategy
- Trigger: a regression in the meld doors or the cache tests that the fix cannot answer.
- Steps: revert the three source files and the tests; no persisted state, record or cache format changed.
- Verification: the cache-related suites and the regression tests return to their 0.2.8265 results.

## Validation expectations and evidence plan
- The nine regression tests (T1-T6) MUST pass, the GIL off and on; they fail on 0.2.8265 for the bug.
- The new CachingSystem unit tests MUST pin each invariant above: the bool, the kept payloads, the Windows-only retry
  and its budget, the one WARNING, the per-writer temp name, the refused temp write and folder, the unremovable temp.
- The Spellbook and Spell unit tests MUST pin the flag left cleared, no retry before new staging, the end-of-conjure
  save after a refusal, and the explicit save's False.
- The full unit, component and integration trees MUST show no failure caused by the change, the GIL off and on.
- Evidence: the runs under the task's artifact folder, recorded as MEASURE notes; the task's probe A-D rerun.

## Ticket coverage
| requirement | change | validation |
| --- | --- | --- |
| a meld returns its object when its save is refused once (T1) | emit False, flag cleared | test_meld_returns_its_object_when_the_cache_save_fails[rename_refused, temp_write_refused] |
| melds keep returning while every save is refused (T2) | same | test_melds_keep_returning_while_every_cache_save_fails[both] |
| first melds after a refused conjure save return (T3) | same | test_first_melds_after_a_failed_conjure_save_return_their_object[both] |
| a managed lease survives a refused save (T4) | same | test_managed_lease_survives_a_failed_cache_save |
| a spellspace meld survives a refused save (T5) | same | test_spellspace_meld_returns_its_object_when_the_cache_save_fails |
| a refused save leaves no temp file (T6) | temp removed on failure | test_refused_save_leaves_no_temp_file_behind |
| retry on Windows only, per-writer temp names, logging once (F2, D3, D4) | the write | the new CachingSystem unit tests |
| `Spell.emit_cache_file()` returns False on refusal (D2) | Spellbook result | the new Spellbook and Spell unit tests |

## Unknowns and decision requests
- UNKNOWN: the Windows cause (a scanner or indexer holding the bundle) - the owner's Process Monitor capture or a
  run with the venv excluded from real-time scanning.
- DECISION_REQUEST: none open; D1-D4 are answered.

## Context / Handoff Summary
- What changed: the save is best-effort and Windows-robust; nothing is applied until the mapping note is recorded.
- What remains: steps 2-5 above.
- Next entrypoint: component_patch_caching_system.md, then code_description_patch_caching_system.md.
