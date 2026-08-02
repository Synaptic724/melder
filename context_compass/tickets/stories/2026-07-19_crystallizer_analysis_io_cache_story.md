# Story: Crystallizer analysis IO economy - physical-source cache + descent policy

## Metadata
- Story ID: STORY-2026-07-19-crystallizer-analysis-io-cache
- Status: in_progress
- Owner: cowork
- Agent Name: UNASSIGNED (helper_f departed 2026-08-02, owner-directed; lane left ACTIVE)
- Priority: p1
- Created: 2026-07-19T11:20:00Z
- Updated: 2026-07-19T11:20:00Z
- Parent strategy: TASK-2026-07-19-crystallizer-analysis-io-storm

## Objective
Close the analysis IO storm as a durable public-library capability: stat-guarded
process-wide fingerprint cache (zero-IO fast path for unchanged worlds), single-hash
cold path, site-package dependency-descent policy knob (default False), and stat-guarded
drift surfaces - all behind the patch lane crystallizer_analysis_io_cache_2026_07_19.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-19 ("best outcomes... investigate then send it");
  strategy FACT evidenced in the parent task; patch docs authored before code.
- EXECUTION_BOUNDARY: crystal_analysis package (new cache module, analyzer, custody
  strategies, preflight drift, impact engine), crystallizer configuration + facade +
  spell_crystal threading, tests. No record fingerprint-value changes.
- DEPENDENCIES: patch docs under
  system_docs/patches/active/crystallizer_analysis_io_cache_2026_07_19/.
- EXIT_GATE: owner 3.14t run green with observable test-suite speedup; docs promoted.
- FAILURE_ESCALATION: CONFLICT if fingerprint parity breaks; DECISION_REQUEST already
  flagged on the descent default (False; reversible one line).

## Applicable Anti-Patterns
- [ ] No caching that can serve stale truth past a stat change.
- [ ] No silent record-shape breaks; descent-off leaves are additive-tolerant.

## Noting Behavior
- Story notes: cross-surface synthesis and gate transitions.

## Notes
- DATETIME: 2026-07-19T11:37:00Z
  TYPE: MEASURE
  CLAIM: Full wave LANDED behind the patch lane (docs authored first). CODE: (1) NEW
    crystal_analysis/physical_source_cache.py - process-wide stat-guarded fingerprint
    cache (path -> mtime_ns/size/sha256; LRU 4096; class RLock mirroring the syntax-memo
    posture; stat-before-read self-correcting guard; read law mirrors the custody
    _read_source_like_file byte-for-byte). (2) CrystalAnalyzer: stat fast path (unchanged
    stat + memo hit = fingerprint from cache + fact replay, ZERO reads/hashes), cold path
    reads THROUGH the cache with ONE sha reused as memo digest AND fingerprint (double
    hash gone), _custody_descends() gate applied at both the current-node extraction and
    the dependency enqueue, ctor kwarg site_package_dependency_descent (raw default True
    = byte-compatible). (3) Custody family: additive reads_physical_source +
    claims_sha256_source_fingerprint contract properties (base True/True; site
    True/False; synthetic False/False; binary False/False - the 1:1 mirror of the
    fingerprint() overrides). (4) CrystallizerConfiguration: schema key + typed defaulted
    property site_package_dependency_descent (default False) + with_defaults entry;
    threaded Crystallizer.create_spell_crystal -> SpellCrystal -> analyzer. (5)
    SourceDriftStrategy + ImpactEngine.describe_source_drift stat-guard first, cold reads
    feed the cache; dead hashlib imports removed. TESTS (22 new rows + 1 updated):
    test_physical_source_cache.py (9: truth-law parity, poisoned-read stat-hit, mtime and
    size invalidation, no-source law, unreadable honesty, LRU cap, clear hook, 8-thread
    hammer), analyzer +4 (second-pass zero .py reads with fingerprint parity, tamper
    re-fingerprints, descent-off leaf law, descent-on interior walk - result property
    names corrected from source mid-wave: module_to_kind/module_to_direct_dependencies,
    custody ctor idioms corrected to positional per the house file), custody contract
    mirror row, impact +2 (poisoned-read second pass, tamper through the cache), drift
    strategy file (3: silent-no-reread, drift-after-primed-pass, unreadable info row),
    config knobs (5), reload-lanes backfill list +site_package_dependency_descent
    (sorted order preserved). compile() green x18; 120-col clean x18; CRLF + BOM
    preserved per file. pytest Not run - rides the owner's 3.14t run (device VM cannot
    import the 3.14 runtime).
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/physical_source_cache.py:1-210
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:769-800
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:940-1010
  - src/melder/crystallizer/configuration/crystallizer_configuration.py:272-300
  - src/melder/crystallizer/crystal_analysis/preflight/source_drift_strategy.py:80-135
  - src/melder/crystallizer/crystal_analysis/impact_engine.py:300-345
  - tests/unit/melder/crystallizer/crystal_analysis/test_physical_source_cache.py:1-260
  - tests/unit/melder/crystallizer/crystal_analysis/test_crystal_analyzer.py:230-420
  IMPACT: Bind cost drops from O(import world) reads+hashes to O(changed files) after
    the first pass; loads and drift views stat instead of read; the pytest/third-party
    interior walk is gone by default (descent knob reverses it in one line). Expected
    test-suite effect: the seconds-per-test crystallizer integration cost collapses to
    the first-bind pass per process.
  NEXT: Owner 3.14t run (add: pytest tests/unit/melder/crystallizer -q and time the
    integration suite before/after); DECISION standing: descent default False - flip in
    with_defaults if you want interior third-party inventories back.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-07-19T11:46:00Z
  TYPE: MEASURE
  CLAIM: REOPEN micro-wave for the owner's 3-row red (suite otherwise vastly faster,
    owner-confirmed "massive improvement"). Root cause 1 (production, mine): empty
    sources never enter the syntax memo BY LAW, but the stat fast path consulted the
    memo for them anyway - every warm pass counted one phantom MISS per empty
    __init__.py and paid a pointless read; the two pre-existing memo-counter
    regressions (memoized_facts_survive / source_edit_invalidates) caught it exactly
    (3!=2, 4!=3). Fix: class anchor _EMPTY_SOURCE_SHA256 beside the memo state and a
    fast-path short-circuit BEFORE the memo lookup (cold-path parity: no facts, no
    fingerprint, no memo participation - and now no read either). Root cause 2 (test,
    mine): test_changed_file_between_analyses_re_fingerprints never put tmp_path on
    sys.path, so dependency modules resolved as unknown leaves and carried no
    fingerprints - KeyError, not a cache defect. Fix: syspath_prepend + presence
    assert; the zero-reads parity row strengthened the same way (its second pass now
    proves the empty-__init__ fast path reads nothing under poisoned read_text).
    compile() green x2; 120-col clean. pytest Not run - rides the owner's rerun.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:133-145
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:995-1010
  - tests/unit/melder/crystallizer/crystal_analysis/test_crystal_analyzer.py:275-370
  - tests/unit/melder/crystallizer/crystal_analysis/test_crystal_analyzer.py:562-600
  IMPACT: Memo counters are truthful again; empty modules are now the CHEAPEST case
    (stat only) instead of a hidden read-per-pass; the drift regression actually
    exercises the multi-module world it claimed to.
  NEXT: Owner reruns pytest tests/unit/melder/crystallizer/crystal_analysis -q; green
    -> acceptance walkthrough for both IO tickets + patch promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Implementation lane for the analysis IO economy; design and evidence live in the parent
strategy task and the three patch docs.
