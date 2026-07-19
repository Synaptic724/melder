# Code Description Patch: PhysicalSourceCache + analyzer fast path

Lane: crystallizer_analysis_io_cache_2026_07_19. Trigger: concurrency-sensitive shared
cache + control-flow change in the analysis hot path.

## PhysicalSourceCache control flow
- fingerprint_if_unchanged(path): stat OUTSIDE the lock; under the class RLock compare
  (mtime_ns, size) to the entry; hit -> LRU bump + return sha; miss/changed/stat-error ->
  None (callers fall to the cold lane). Never reads file content.
- read_text_and_fingerprint(name, path): the ONE read law (mirrors
  SourceCustodyStrategy._read_source_like_file byte-for-byte: non-source suffix or
  missing file -> (None, None, None); read failure -> (None, None, error_text)); stat is
  taken BEFORE the read so a mid-read writer leaves a guard that self-corrects on the
  next stat; sha256 of the utf-8 text; entry stored + LRU-capped under the lock.
- Staleness law: served sha always corresponds to content observed with the guarded
  stat pair; any mtime_ns/size change misses. Same-stat content swap is the documented
  residual (physically implausible; identical to build-system guard law).

## _extract_module_facts control flow (after)
1. physical_lane = custody.reads_physical_source and module_path is not None.
2. FAST PATH (default fact strategies + physical lane): stat-hit sha -> memo lookup by
   sha (sha IS the memo digest - same hash law) -> on memo hit: record fingerprint iff
   custody.claims_sha256_source_fingerprint, replay facts. Zero IO.
3. COLD: physical lane reads through the cache (one read, one sha); non-physical lanes
   (synthetic module text, binary None) keep custody.resolve_source verbatim.
4. Digest reuse: source_digest = cached sha on the physical lane (no second hash);
   non-physical default-strategy lanes keep _source_digest.
5. Everything downstream (memo store, fact dispatch, walk errors, fingerprint record on
   the cold path via custody.fingerprint) is byte-preserved.

## Descent gate
- _custody_descends(custody): custody.descends AND NOT (kind == site_package AND flag
  off). Applied at BOTH the dependency-enqueue decision and the current-node fact
  extraction (root-is-site-package). Non-descending site nodes: skip facts (empty
  deps/exports), keep provenance harvest + record_module_target.

## Drift guards
- SourceDriftStrategy: per fingerprinted (module, path): exists check unchanged ->
  fingerprint_if_unchanged -> hit compares cached sha; miss reads through the cache
  (feeding the next load); error/absent rows byte-preserved.
- ImpactEngine.describe_source_drift: same guard, same statuses vocabulary.

## Edge / Error Semantics
- Custom fact strategies (_uses_default_fact_strategies False) never enter the fast
  path or the memo; they still read through the cache (population only).
- A custody subclass overriding fingerprint() with a non-sha256 law MUST override
  claims_sha256_source_fingerprint False or the fast path would misclaim (documented on
  the base property).
- Cache never serves for synthetic modules (reads_physical_source False) - synthetic
  text lives on the object, not disk.

## Non-Goals
- No text retention, no cross-process persistence, no invalidation callbacks.
