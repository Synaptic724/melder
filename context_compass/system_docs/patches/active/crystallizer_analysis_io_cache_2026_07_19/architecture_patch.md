# Architecture Patch: Crystallizer analysis IO economy (physical-source cache + descent policy)

Lane: crystallizer_analysis_io_cache_2026_07_19.
Ticket: STORY-2026-07-19-crystallizer-analysis-io-cache.

## Objective
Bind-time and load-time module-world analysis currently pays O(transitive import world)
file reads + SHA256 hashing on EVERY bind and EVERY load: resolve_source reads each
walked file per call, the memo digest and the custody fingerprint hash the same text
twice, the walk descends INTO installed site-packages, and the source_drift preflight +
ImpactEngine drift view re-read every fingerprinted file. Owner directive 2026-07-19:
durable public-library fix, not a test patch.

## Non-Goals
- No change to recorded fingerprint VALUES (UTF-8 SHA256 law stands byte-identical).
- No weakening of drift/tamper honesty: any real content change is still detected.
- No caching of source TEXT (memory posture: stat guards + hashes only).
- No change to synthetic/binary custody lanes (no disk source there).

## Changed Components
1. crystal_analysis/physical_source_cache.py (NEW): process-wide stat-guarded
   fingerprint cache (path -> (mtime_ns, size, sha256)), LRU-bounded, lock-disciplined,
   mirroring the existing syntax-fact memo posture.
2. CrystalAnalyzer: fast path (stat-hit + syntax-memo-hit = ZERO reads, ZERO hashes),
   cold path reads THROUGH the cache and computes ONE sha reused as memo digest AND
   fingerprint claim (kills the double hash); additive site_package_dependency_descent
   ctor knob gates walking INTO installed packages.
3. Custody strategy family: two additive contract properties -
   reads_physical_source (base True; synthetic/binary False) and
   claims_sha256_source_fingerprint (base True; site/synthetic/binary False - the 1:1
   mirror of the existing fingerprint() overrides).
4. CrystallizerConfiguration (+ Crystallizer.create_spell_crystal + SpellCrystal):
   new schema knob site_package_dependency_descent, DEFAULT False (see decision below),
   threaded exactly like retain_user_sources.
5. SourceDriftStrategy + ImpactEngine.describe_source_drift: stat-guard first, read+hash
   only when the stat changed; cold reads feed the cache.

## Invariants
- Truth law: a served fingerprint always equals the sha256 of content that produced the
  guarded (mtime_ns, size) stat pair; ANY observable file change misses the guard and
  re-hashes. Accepted residual: a same-size edit preserving mtime_ns is undetectable -
  the same guard law every build system accepts; documented on the cache class.
- Record shape: fingerprint values, module inventories for user/synthetic/binary lanes,
  and drift findings are byte-identical. With descent OFF, site-package nodes record as
  provenance-carrying LEAVES (empty deps/exports) - additive-tolerant for old records
  (fold and preflight never require interior third-party inventories).
- Concurrency: cache mirrors the syntax-memo discipline (class RLock, no text retained,
  test-only clear hook); safe under parallel restore workers.

## Decision (owner-facing, reversible one line)
site_package_dependency_descent DEFAULTS False: a public package's first impression is
bind latency, and walking pytest/numpy interiors serves no restore, drift, or custody
law (site packages make no fingerprint claims and never rebuild). Provenance
(name/version + binary identity) still captures the environment. Flip the default in
with_defaults() to restore the old walk wholesale.

## Migration Order
Cache + custody properties -> analyzer integration -> config knob + threading ->
preflight/impact guards -> tests. Single slice; no data migration (additive knob
backfills False on reload lanes).

## Rollback
Delete the cache module + revert analyzer/preflight/impact call sites (cold lanes are
byte-preserved behind the guards); set the knob default True.

## Ticket Coverage Matrix
- Cache unit rows -> physical_source_cache.py
- Analyzer fast/cold/parity rows -> crystal_analyzer.py
- Knob rows + reload backfill -> crystallizer_configuration.py
- Drift stat-guard rows -> source_drift_strategy.py / impact_engine.py
