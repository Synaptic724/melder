# Component Patch: crystal_analysis IO economy

Lane: crystallizer_analysis_io_cache_2026_07_19.

## Before
- _extract_module_facts: custody.resolve_source READS the file on every call; sha256
  computed TWICE per cold module (memo digest + fingerprint claim); memo hits still pay
  read + digest hash. Every bind re-reads the whole walked world.
- _walk_module_dependencies descends into site-package dependencies unconditionally
  (source read + AST parse of pytest/pluggy/numpy interiors).
- SourceDriftStrategy re-reads + re-hashes every recorded fingerprint on every load;
  ImpactEngine.describe_source_drift does the same per call.

## After
- Stat fast path: reads_physical_source custody + stat-guard hit + syntax-memo hit =
  fingerprint recorded from cache (claims_sha256_source_fingerprint strategies only)
  + facts replayed - no read, no hash, no parse.
- Cold path: ONE read through PhysicalSourceCache, ONE sha reused as memo digest and
  fingerprint; walk-error honesty channel preserved verbatim (same read law:
  suffix/exists gates, utf-8, error text shape).
- Site-package descent behind the analyzer knob (config-threaded, default False):
  site nodes record kind/path/extension/provenance with empty deps and enqueue nothing;
  root-is-site-package worlds get the same leaf law.
- Drift surfaces stat-guard first; cold reads feed the cache so the NEXT load stats.

## Interface Deltas (all additive)
- PhysicalSourceCache: fingerprint_if_unchanged(path), read_text_and_fingerprint(name,
  path), _clear_for_tests(), _stats_for_tests().
- SourceCustodyStrategy: reads_physical_source, claims_sha256_source_fingerprint
  properties (+ overrides on synthetic/binary/site).
- CrystalAnalyzer.__init__(..., site_package_dependency_descent: bool = True) - raw
  constructions stay byte-compatible; SpellCrystal passes the config truth.
- SpellCrystal.__init__(..., site_package_dependency_descent: bool = True).
- CrystallizerConfiguration.site_package_dependency_descent (typed defaulted property,
  schema default False via with_defaults; reload lanes backfill it).

## State / Failure Deltas
- None on failure lanes: unreadable/absent/parse-error semantics byte-preserved.
- Memory: cache holds <= 4096 (path, ints, 64-char sha) tuples; LRU eviction.

## Dependency / Ordering
- Independent of the parallel-restore lane; composes with it (restore workers hit the
  cache concurrently - lock law covers them).

## Validation Expectations
- Unit: cache guard laws (hit serves without read, mtime/size change re-hashes, LRU cap,
  unreadable honesty, thread hammer); analyzer parity (fast path fingerprints ==
  cold-path fingerprints; changed file re-fingerprints; synthetic lane untouched);
  descent knob (off: site leaf + provenance, no interior walk; on: byte-compatible);
  config knob rows + reload backfill list update.
- Component: second analysis of an unchanged world performs ZERO source reads
  (counted at the read seam); drift preflight on an unchanged world reads nothing.
- Integration: tampered file after seal STILL reports drift through the cache.
