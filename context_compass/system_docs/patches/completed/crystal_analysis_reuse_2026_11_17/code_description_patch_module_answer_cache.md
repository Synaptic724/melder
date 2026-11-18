# code_description_patch_module_answer_cache

## Metadata
- Patch ID: crystal_analysis_reuse_2026_11_17
- Ticket: https://github.com/Synaptic724/melder/issues/331
- Status: implemented at 0.2.8304
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-17T10:20:00Z
- Updated: 2026-11-17T10:38:24Z

## Control Flow Commitments
- `resolve_module_path(name, obj)`: a synthetic object keeps its uncached branch. Otherwise read `obj.__file__`,
  look up (name, same object, same file text - and, with no object, the same `sys.path`); on a miss compute as
  before and store when the file text is absolute or there is none (the `find_spec` origin branch).
- `_match_custody(name, obj, path)`: the per-pass answer first; then, for a default-chain analyzer, a non-synthetic
  object and a path, the cached kind for (roots, path text) mapped to this analyzer's strategy of that kind; on a
  miss run the chain and store a non-synthetic kind.
- `_extract_module_facts`: for a default-strategies analyzer on the physical lane, stat the file, look up (name,
  same object, path text, mtime_ns, size); a hit records the fingerprint when the custody claims one, records the
  export surface and returns detached copies; a miss derives as before, captures the source sha256 and export
  surface, and stores them unless a walk error was recorded.
- Root resolvers: key by the raw inputs and the interpreter state they depend on (cwd, site lists, prefixes).
- Provenance: key the distribution map by the site roots' (path, mtime_ns) signature and the payload by
  (signature, top-level name).

## Edge and Error Semantics
- Every guard compares, never assumes: a dead or different weak reference, a different `__file__`, path or stat is a
  miss, and the miss recomputes and overwrites the entry.
- Lookups never raise for missing entries; validation errors (TypeError for a bad root entry) are raised before the
  cache is consulted, exactly as before.

## Invariants and Idempotency
- Map access is serialized by one class RLock; answers are computed outside it. Concurrent misses compute the same
  deterministic answer and the last store wins.
- Stores refresh LRU position; inserts beyond 8192 evict the oldest entry of that map. Eviction releases only
  values and weak references.
- Returned containers are fresh: callers never receive a cached tuple's mutable view.

## Explicit Non-Goals
- No time-based expiry, no file watching, no persistence across processes, no caching of source text.
