# Component patch: CachingSystem best-effort save

Patch id: cache_save_best_effort_2026_10_24. Component: CachingSystem
(src/melder/utilities/caching_system/caching_system.py). Author: melder_0, 2026-10-24.

## Component purpose and boundary
- Current boundary: CachingSystem owns one conduit's creation-cache bundle file - its load at construction, the
  in-memory envelope and the save - for one `(frame_name, conduit_name)`; one Spellbook builds it and drives it.
- Target boundary: unchanged. The save stays inside CachingSystem; it MUST NOT raise an OSError to its caller.

## Before
`emit()` returns None. Under the instance RLock `_write_current_cache_to_disk_locked` marshals the envelope, makes
the frame folder, writes `<conduit>.meldercache.tmp` and `Path.replace`s it onto the bundle. An OSError of any of the
three steps propagates; the temp file stays when the rename raises; every writer of one bundle shares the temp name.

## After
- `emit() -> bool`: True after the rename; False after an OSError of the folder, the temp write or the rename. On
  False it removes its own temp file (`unlink(missing_ok=True)`; an OSError there is logged at WARNING with the
  leftover path, never raised), logs the refused save and returns.
- The temp file is `<conduit>.meldercache.<pid>.<thread id>.tmp` (`os.getpid()`, `threading.get_ident()`).
- `_replace_bundle_locked` retries a PermissionError of the rename while `RETRY_REFUSED_RENAME` is True (Windows):
  `REPLACE_ATTEMPTS` (5) attempts, sleeping `REPLACE_RETRY_DELAY_SECONDS` (0.01 s) times the attempt number between
  them, about 100 ms in all. With the flag False (every other platform) a refusal is final at once.
- `_log_refused_save_locked`: the first refused save of the instance at WARNING - the bundle path, the error, that
  melds are unaffected and the cache stays in memory for the next save, and the remedies (make the cache folder
  writable; on Windows exclude it from real-time scanning; or turn caching off for the frame with
  `with_system_caching_enabled(False)`) - and every later one at DEBUG.
- `_cache_data` is replaced by the written envelope only after a successful rename, as today; after a refusal it
  still holds every staged payload.

## Interface deltas
- Inputs: none new.
- Outputs: `emit()` returns bool.
- Error semantics: OSError of a save -> False (logged); any other error propagates as before.

## State and lifecycle deltas
- New slot `_refused_save_logged: bool`, False at construction, set True under the instance lock by the first
  refused save, deleted in `cleanup()` with the other owned slots.
- New ClassVars `RETRY_REFUSED_RENAME` (`sys.platform == "win32"`), `REPLACE_ATTEMPTS` (5) and
  `REPLACE_RETRY_DELAY_SECONDS` (0.01): class-level, so a test can set them; no module-level constants.

## Failure mode deltas
- Removed: a refused save raising to its caller; a temp file orphaned by a refused rename.
- Changed: a lasting refusal (a read-only folder) costs one WARNING, then one DEBUG line per attempted save.
- Known limit: a temp file the operating system refuses to remove stays, named per writer and logged with its path.

## Dependency and ordering constraints
1. The temp file is written and renamed under the instance lock, as before; the retry sleeps under it.
2. The temp file is removed before the refusal is logged, so the log can name a leftover file.

## Validation expectations
- T6 `test_refused_save_leaves_no_temp_file_behind` green.
- New unit tests: a save returns True and leaves only the bundle; a refused save returns False and the next save
  writes the payloads staged before and after it; a rename refused twice then allowed saves with retry on, after two
  refusals; with retry off one refusal returns False; a lasting refusal with retry on gives up after
  `REPLACE_ATTEMPTS` refusals; only the first refused save logs a WARNING; the temp name carries the pid and the
  thread and differs between threads; a refused temp write and a refused folder return False and leave nothing; a
  temp file that cannot be removed is logged, not raised.

## Unknowns and open decisions
- UNKNOWN: none for this component.
- DECISION_REQUEST: none (D3 and D4 answered).

## Context / Handoff Summary
- What changed: `emit()` is best-effort and returns bool; per-writer temp names; a Windows-only rename retry.
- Remaining risks: a retried rename holds the instance lock up to about 100 ms on Windows.
- Next entrypoint: code_description_patch_caching_system.md.
