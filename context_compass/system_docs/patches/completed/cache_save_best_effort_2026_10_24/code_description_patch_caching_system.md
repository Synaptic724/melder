# Code description patch: CachingSystem save

Patch id: cache_save_best_effort_2026_10_24. Component: CachingSystem. Author: melder_0, 2026-10-24.

## Trigger justification
- The save's error semantics change (an OSError becomes a False return) and a retry with sleeps runs under a lock.

## Control-flow description
1. `emit()` takes the instance RLock and returns `_write_current_cache_to_disk_locked()`.
2. Build the envelope dict from `_cache_data` and marshal it, unchanged; a marshal error propagates.
3. The temp path is `<bundle name>.<pid>.<thread id>.tmp` in the bundle's folder (`_temp_bundle_path`).
4. In one `try`: make the folder (parents, exist_ok), write the temp bytes, `_replace_bundle_locked(temp, bundle)`.
5. `_replace_bundle_locked`: attempts = `REPLACE_ATTEMPTS` when `RETRY_REFUSED_RENAME` is True, else 1. Each attempt
   renames and returns; a PermissionError re-raises on the last attempt and otherwise sleeps
   `REPLACE_RETRY_DELAY_SECONDS * attempt` before the next.
6. `except OSError as error`: `_discard_temp_bundle_locked(temp)`, `_log_refused_save_locked(error)`, return False.
7. After the rename: `_cache_data` becomes the written envelope; return True.

## Edge, error and rollback semantics
- An OSError of the folder, the temp write or the final rename -> False; the bundle on disk is the previous one,
  or absent.
- A PermissionError the retry absorbs -> True; nothing is logged.
- Other OSError subclasses of the rename (the temp file gone, a full disk) are not retried -> False.
- Removing the temp file uses `missing_ok=True`; an OSError there is logged at WARNING with the leftover path.
- A non-OSError exception propagates unchanged; none is expected from these steps.
- Nothing is rolled back: a refused save changed nothing on disk and nothing in memory.

## Invariants and idempotency expectations
- The rename is the only step that changes the bundle; a False return never changed it.
- After False, `_cache_data` still holds every staged payload, and a later True writes them.
- `emit()` may be called again after False; each call is one save (with the Windows retries inside it).
- `_refused_save_logged` goes from False to True once per instance, under the instance lock.

## Explicit non-goals
- No cross-process file lock, no retry from the melding thread, no change to load, normalization or the format.
- No cleanup of temp files other writers left behind.

## Validation focus points
- The unit tests listed in component_patch_caching_system.md and T6.
- The task's probe, case A (one refusal) and case B (a lasting refusal), on the VM, the GIL off and on.

## Context / Handoff Summary
- What changed: the save's control flow above.
- Remaining unknowns: none for the code.
- Next entrypoint: the src change, step 2 of the architecture patch's order.
