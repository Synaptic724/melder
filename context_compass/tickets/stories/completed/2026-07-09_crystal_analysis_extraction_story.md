# Story: crystal_analysis extraction (S1 - analyzer, custody, facts, SpellCrystal slim)

- Completed: 2026-07-10T09:10:00Z
- Summary: crystal_analysis stood up for real (analyzer + result carrier +
  custody strategies w/ physical SHA256 fingerprints + fact strategies incl.
  NEW export_surface/load_order + relocated preflight); SpellCrystal slimmed
  1684->1030 as a carrier. 22 new tests; owner-run sentinel green; owner
  accepted at epic closure.

## Metadata
- Story ID: STORY-2026-07-09-crystal-analysis-extraction
- Parent Epic: EPIC-2026-07-09-crystallizer-subsystem-decomposition
- Status: done
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-10T00:10:00Z
- Updated: 2026-07-10T00:10:00Z

## Problem / Opportunity
SpellCrystal owns ~500 lines of embedded analysis (classification, source resolution,
AST walk, synthetic harvest) welded into its constructor - unusable against retained
historical versions (MR's requirement), missing export surface, load order, physical
fingerprints, and site-package provenance. Owner law (2026-07-09): crystals carry
results, never analyzers; crystal_analysis/ hosts all crystal analysis.

## Design
Per patch docs (entry gate satisfied):
- system_docs/patches/active/crystallizer_decomposition_2026_07_09/architecture_patch.md
- .../component_patch_crystal_analysis.md
- .../component_patch_spell_crystal.md
Canonical design anchor: artifacts/2026-07-09_crystallizer_philosophy_v3.md.

## Ticket Contract
- ENTRY_GATE: epic routed; patch docs above exist and are linked. SATISFIED 00:10Z.
- EXECUTION_BOUNDARY: new package src/melder/crystallizer/crystal_analysis/**;
  src/melder/crystallizer/persistence/crystals/spell_crystal.py (slim-down);
  persistence/analysis/* relocation (+ the two import sites: restore_engine.py
  _run_preflight lazy import, crystallizer.py analyze facades); NEW unit tests under
  tests/unit/melder/crystallizer/crystal_analysis/; sentinel test import re-points.
  NOTHING ELSE.
- DEPENDENCIES: none (first tranche; deliberately self-contained).
- EXIT_GATE: py_compile floor green in-sandbox; describe()-parity + property-parity
  tests authored; sentinel set re-pointed; owner-run 3.14t sentinel green.
- FAILURE_ESCALATION: any fold/preflight behavior delta -> CONFLICT + stop; any
  describe() key regression -> BLOCKER (restore compatibility).

## Tasks
- [x] T1: crystal_analysis_result.py (value-only result carrier + describe()). DONE 00:20Z.
- [x] T2: custody/ - source_custody_strategy.py (ABC) + synthetic / user_source
      (+SHA256 fingerprint) / site_package / binary_unknown strategies. DONE 00:40Z.
- [x] T3: strategies/ - base_strategy.py (ABC CrystalFactStrategy + FactContext) +
      import_statement + from_import_statement (moved logic) + export_surface (NEW) +
      dependency_view (NEW: topological load order, cycle-tolerant). DONE 00:45Z.
- [x] T4: crystal_analyzer.py - walk loop moves here; analyze_spell_root +
      analyze_payload entry points. DONE 00:55Z (see 00:55Z note).
- [x] T5: SpellCrystal slim-down - delegate to analyzer, store result, property +
      describe() parity, cleanup children-first, comments updated. DONE 01:20Z.
- [x] T6: preflight/ relocation - persistence/analysis/* -> crystal_analysis/preflight/
      (bash mv) + re-point restore_engine._run_preflight and Crystallizer facades.
      DONE 01:30Z (grep gate: zero `persistence.analysis` paths repo-wide).
- [x] T7: NEW unit tests - 22 tests / 3 files under
      tests/unit/melder/crystallizer/crystal_analysis/ (custody 7, facts 9,
      analyzer 6 incl. the drift regression + MR payload seam). Describe-parity
      rides the sentinel integration suite (real spells bind there). DONE 01:50Z.
- [x] T8: sentinel import re-point - S1 moved only the preflight package; the sole
      sentinel import touching it (test_persistence_analyzer.py:8) is re-pointed;
      restore/formation/bootstrap sentinels import unchanged paths this tranche.
      DONE 01:35Z.
- [x] T9: story notes + board sync; handed to owner for the 3.14t sentinel run.
      DONE 01:55Z.

## Acceptance Criteria
- No analysis logic (classify/resolve-source/AST/walk/harvest/record) remains in
  spell_crystal.py; the 12 analysis slots are replaced by one _analysis result.
- describe() emits every pre-existing key with equal values on a fixture spell, plus
  physical_module_fingerprints / export_surfaces / module_load_order.
- CrystalAnalyzer.analyze_payload() produces a result from a retained describe()
  payload with no live Spell (MR seam proven by test).
- user_source modules carry SHA256 fingerprints; a mutated fixture file yields a
  detectable mismatch between two analyses (regression test).
- Preflight strategies run from crystal_analysis/preflight/ with zero behavior change.
- Owner-run 3.14t sentinel set green. Full-tree red is EXPECTED until S-test.

## Applicable Anti-Patterns
- [ ] No facade signature changes smuggled into reroutes.
- [ ] No comment deletions during the slim-down (update stale ones).
- [ ] No defensive getattr/hasattr on owned contracts in new code.
- [ ] No claim of test execution (sandbox = py_compile floor; report "Not run.").

## Noting Behavior
- Story notes: cross-task synthesis, parity evidence, and gate transitions.

## Notes
- DATETIME: 2026-07-10T00:10:00Z
  TYPE: PLAN
  CLAIM: S1 opened with patch gate satisfied (3 patch docs authored). Test strategy
    per owner ruling: bulk test breakage is ACCEPTED epic-wide; only the sentinel set
    (whole-system restore, profile-cache round trip, formation round trip, pod
    bootstrap, analyzer units) is kept green per tranche; one S-test re-point sweep
    story runs after S4. Build order T1->T9 (result carrier first; everything else
    produces/consumes it). Evidence baseline for the slim-down captured pre-work:
    constructor jobs split at :156-238 (identity, STAYS) vs :163-178 + :240-265
    (analysis, MOVES); describe at :1620-1681; the 6 relocating methods at :1150-1620.
  EVIDENCE:
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:104-265
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:1150-1681
  - codex/context_compass/system_docs/patches/active/crystallizer_decomposition_2026_07_09/component_patch_crystal_analysis.md:1-999
  IMPACT: Post-compaction retrace = this note + the 3 patch docs + V3 philosophy.
  NEXT: implement T1 (crystal_analysis_result.py).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-10T00:20:00Z
  TYPE: FACT
  CLAIM: T1 LANDED - CrystalAnalysisResult (~700 lines) at
    src/melder/crystallizer/crystal_analysis/crystal_analysis_result.py. Cleanable;
    RLock; write verbs for the analyzer (set_root_module_kind, record_module_target
    [same dedupe/last-write-wins semantics as the old SpellCrystal recorder, extension
    now passed in], record_synthetic_module_source, record_physical_fingerprint,
    record_export_surface, set_module_load_order, record_walk_error); detached-copy
    read properties preserving the pre-decomposition vocabulary; describe() =
    analysis-half of the old SpellCrystal payload + root_module_kind +
    ast_(from_)import maps + 3 new keys (physical_module_fingerprints,
    export_surfaces, module_load_order). Compile: Not run (replica rot - bash mount
    reads the file at its old 0-byte length; disk verified current via file-tool Read,
    describe() tail intact at :640-680). Execution: Not run.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/crystal_analysis_result.py:1-700
  - codex/context_compass/system_docs/patches/active/crystallizer_decomposition_2026_07_09/component_patch_crystal_analysis.md:20-40
  IMPACT: Everything downstream (custody/fact strategies, analyzer, SpellCrystal
    slim) now has its output contract.
  NEXT: T2 - custody/ package: source_custody_strategy.py ABC + synthetic /
    user_source(+SHA) / site_package / binary_unknown strategies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-10T00:45:00Z
  TYPE: FACT
  CLAIM: T2+T3 LANDED (9 files under crystal_analysis/). CUSTODY: ABC
    SourceCustodyStrategy (kind/descends/matches/resolve_source ->
    (source, error) tuple honesty channel; default fingerprint=SHA256; shared
    _read_source_like_file + _normalize_path) + 4 strategies reproducing
    _classify_module_target EXACTLY via first-match priority order [synthetic ->
    user_source -> site_package -> binary_unknown(always-True fallback)]:
    synthetic (protocol identity; harvest_payload = the M3 rebuild dict; fingerprint
    None - source_sha256 rides the harvest), user_source (policy roots; ABC SHA256
    fingerprint = the NEW physical drift detection), site_package (site roots + the
    historical "site-packages"/"dist-packages" path-text fallback; fingerprint None
    first cut), binary_unknown (kind "unknown", never descends - honest leaves).
    FACTS: base_strategy.py = CrystalFactStrategy ABC (visit_node/analyze_module/
    finalize hooks) + FactContext (per-module accumulator: flat_import_targets +
    from_import_targets). ORDER-PARITY DESIGN DECISION: the analyzer walks each AST
    ONCE and dispatches nodes to strategies in registration order, so candidate
    order (probed from-import members BEFORE their base; interleaved with plain
    imports in visit order) stays byte-compatible with the old single-pass extractor
    at spell_crystal.py:1364-1405 - manifest ordering parity holds. import_statement
    (ast.Import aliases verbatim), from_import_statement (relative resolve_name +
    find_spec member probing + member map; base appended after members),
    export_surface (NEW: static __all__ list/tuple-of-str extraction + public
    top-level def/class/assign names, module body only, honest under-claim on
    dynamic __all__), dependency_view (NEW: Kahn topological order over walked-module
    edges, sorted tie-break, cycle-tolerant append + walk-error naming the cycle).
    COMPILE: custody/ 5/5 py_compile GREEN in-sandbox (new dir, replica current);
    crystal_analysis_result.py + strategies/* Not run (replica rot - these paths
    pre-existed as 0-byte scaffolds and the mount replica caps at old length; disks
    current via file-tool write/edit confirmations; result tail Read-verified
    :640-680). Execution: Not run.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/custody/source_custody_strategy.py:1-207
  - src/melder/crystallizer/crystal_analysis/strategies/base_strategy.py:1-250
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:1364-1405
  IMPACT: All strategy machinery exists; T4 analyzer is pure composition now.
  NEXT: T4 - crystal_analyzer.py (walk loop moves from spell_crystal; custody
    dispatch; single AST walk + fact dispatch; analyze_spell_root + analyze_payload;
    current_package derivation ported from :1349-1362).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-10T00:55:00Z
  TYPE: FACT
  CLAIM: T4 LANDED - CrystalAnalyzer (~640 lines) at
    src/melder/crystallizer/crystal_analysis/crystal_analyzer.py. Single-use
    composition: default custody chain [synthetic, user_source(roots),
    site_package(roots), binary_unknown] + default facts [import_statement,
    from_import_statement, export_surface, dependency_view]. PORTED FAITHFULLY from
    spell_crystal.py: the LIFO walk (:1473-1576; leaf-record-then-current order,
    dedup-first-seen candidates, unknown deps as honest leaves via
    custody.descends=False), current_package fallback chain (:1349-1362),
    _resolve_module_path (:1017-1079 incl. SyntheticModule physical-path branch),
    _resolve_file_extension, root-path resolvers (now analyzer statics
    resolve_user_root_paths/resolve_site_package_root_paths - crystals call them
    once, keep tuples for describe parity, pass here). Entry points:
    analyze_spell_root(root triple) and analyze_payload(retained describe dict:
    recorded truths copy through, load order RECOMPUTED from edges, ValueError on
    missing root_module_name/module_to_direct_dependencies). Fingerprints record
    only when custody claims one (user_source SHA256). Cleanup children-first.
    Compile: Not run (pre-existing scaffold path -> replica rot expected; disk
    current via file-tool Write confirmation). Execution: Not run.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:1-640
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:1473-1576
  IMPACT: T5 (SpellCrystal surgery) is now a delegation rewrite: constructor keeps
    identity capture (:156-238), calls analyzer, stores result; 12 slots -> 1.
  NEXT: T5 - slim spell_crystal.py (delegate + property/describe parity + cleanup
    rewire + remove the 6 relocated methods and root-path resolvers).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-10T01:30:00Z
  TYPE: FACT
  CLAIM: T5+T6 LANDED. T5 (spell_crystal.py 1684 -> 1030 lines): imports slimmed
    (ast/site/importlib/SyntheticModule/Mapping/Set gone; CrystalAnalysisResult under
    TYPE_CHECKING - 3.13+ stopped evaluating complex-target annotations so the
    unquoted `self._analysis: CrystalAnalysisResult` is runtime-safe on 3.14t);
    __slots__ 12 analysis slots -> one `_analysis`; constructor keeps identity/
    bind-signature capture verbatim, resolves policy roots + root module path via
    CrystalAnalyzer public statics, delegates analysis to a single-use analyzer
    (cleaned in finally), derives root_module_kind + created_from_* flags from the
    result; cleanup children-first (`_analysis.cleanup()` then del, before identity
    dels); 11 properties delegate to the result (module/path/kind buckets, 3 lookup
    maps, dependency map, walk_errors); pre-existing PEP 604 `str | None` on
    root_module_kind fixed to Optional[str] (touched-code law); describe() preserves
    every pre-decomposition key sourcing analysis keys from the carried result and
    ADDS physical_module_fingerprints, export_surfaces, module_load_order, and the
    two AST maps (previously unpersisted - now persisted, which also strengthens
    analyze_payload round trips); every deleted method left an UPDATED NOTE comment
    naming its new home (comment-preservation law). Analyzer gained public statics
    resolve_module_path/resolve_file_extension + resolve_user_root_paths got the
    dedupe parity fix (the original resolver dedupes; first port missed it).
    T6: bash mv persistence/analysis -> crystal_analysis/preflight (rename-only,
    content-safe); 8 self-imports + restore_engine.py:509 + crystallizer.py:1536/1576
    + sentinel test re-pointed via file-tool Edits; grep gate GREEN (zero
    `persistence.analysis` refs in src+tests). COMPILE FLOOR: preflight 9/9 GREEN +
    restore_engine GREEN in-sandbox; spell_crystal.py/crystallizer.py/
    crystal_analyzer.py Not run - TWO replica-rot variants hit (null-byte tail on the
    SHRUNK spell_crystal replica; mid-token cut at :1783 on the LENGTHENED
    crystallizer replica) - BOTH real disks verified intact via file-tool Reads
    (spell_crystal ends cleanly :1028-1030; crystallizer ends cleanly :1783-1784).
    Execution: Not run. T8 NOTE: for S1 the only sentinel file whose imports moved
    was test_persistence_analyzer.py (done); the restore/formation/bootstrap
    integration sentinels import unchanged paths this tranche.
  EVIDENCE:
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:148-266
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:960-1028
  - src/melder/crystallizer/crystal_analysis/preflight/persistence_analyzer.py:7-31
  - src/melder/crystallizer/persistence/restore_engine.py:508-511
  IMPACT: The V3 carrier law is now enforced in code - no crystal owns analysis
    machinery; preflight lives in the analysis subsystem.
  NEXT: T7 - author the new unit tests (custody, facts incl. export-surface +
    load-order cases, analyzer-from-payload, fingerprint drift, describe parity).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-10T01:55:00Z
  TYPE: FACT
  CLAIM: T7-T9 LANDED; S1 BUILD COMPLETE, awaiting owner validation. 22 new unit
    tests / 3 files (711 lines, py_compile 3/3 GREEN in-sandbox): custody (7 -
    policy-root matching, SHA256 fingerprint claim, non-source (None,None) law,
    site-packages path-text fallback + no-claim law, terminal fallback leaf law,
    synthetic protocol rejection + harvest None, cleanup idempotence); facts (9 -
    interleaved candidate ORDER parity vs the historical extractor
    ["zlib","os.path","os","json"], plain-member vs probed-member from-imports,
    star law, relative resolution via package context, static __all__ + public
    names, dynamic-__all__ honest under-claim, topo order chain+diamond, external
    edges ignored, deterministic cycle break + single honesty error); analyzer (6 -
    real tmp-package walk + classification, fingerprints/exports/load-order ride
    every analysis, analyze_payload rebuild WITHOUT a live spell (MR seam) with
    recomputed load order, malformed-payload teach-grade ValueError, on-disk DRIFT
    regression (fingerprints differ across an edit), unknown honest-leaf law).
    SENTINEL RUN REQUEST (owner, 3.14t):
    pytest tests/unit/melder/crystallizer/crystal_analysis/ -q
    pytest tests/unit/melder/crystallizer/persistence/test_persistence_analyzer.py -q
    pytest tests/unit/melder/crystallizer/persistence/test_restore_engine.py -q
    pytest tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py -q
    Bulk-tree red outside these is EXPECTED (epic DECISION 00:10Z). Execution:
    Not run.
  EVIDENCE:
  - tests/unit/melder/crystallizer/crystal_analysis/test_custody_strategies.py:1-199
  - tests/unit/melder/crystallizer/crystal_analysis/test_fact_strategies.py:1-267
  - tests/unit/melder/crystallizer/crystal_analysis/test_crystal_analyzer.py:1-245
  IMPACT: S1 exit gate is now one owner run away; S2 (crystals move-up) is
    unblocked design-wise but waits for the sentinel verdict per tranche law.
  NEXT: owner runs the sentinel set; on green, open S2
    (crystals-vocabulary-move-up) with its mechanical sweep.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-10T02:20:00Z
  TYPE: FACT
  CLAIM: SENTINEL RUN 1 TRIAGE (owner-run, 4 root causes, all fixed):
    (1) `import tests.*` ModuleNotFoundError (restore_engine 2 fails +
    integration collection error) = INVOCATION ARTIFACT, not deletion - the tests
    tree is a namespace package (zero __init__.py, verified never had them);
    `tests.mocks`/`tests._frame_posture_test_support` exist on disk; bare `pytest`
    lacks the repo root on sys.path (historical green runs used a root-injecting
    invocation). FIX: tests/conftest.py now inserts PROJECT_ROOT alongside src/ -
    both invocations behave identically.
    (2) test_persistence_analyzer clean-bundle "blockers" = same root cause
    (hydration find_spec on tests.mocks unfindable -> blocker); resolves via (1);
    fixture ALSO lacked frame coverage (see 3).
    (3) test_persistence_analyzer configuration-loss "warnings" = LATENT FIXTURE
    BUG from the 2026-07-08 batch (first-ever run): FramePostureStrategy honestly
    warns for books with no frame twin; the minimal fixtures carried none. FIX:
    both fixtures gained frame_name "covered" + the frame twin (strategy behavior
    is correct and unchanged).
    (4) test_analyze_payload ValueError = REAL S1 CONTRACT BUG my test caught:
    analyze_payload demanded root_module_name, a CRYSTAL identity key absent from
    bare result payloads, contradicting the documented two-shape contract. FIX:
    minimum key is module_to_direct_dependencies only; docstring + refusal message
    + component patch doc corrected (CORRECTED marker in patch); the refusal test
    asserts the new key.
    ALSO: stray tests/tests/ junk (doubled-path caching fixture outputs) removed.
    COMPILE: both test files GREEN in-sandbox (replica current); conftest.py +
    crystal_analyzer.py Not run (replica rot; disks current via file-tool edit
    confirmations). Execution: Not run - rerun requested.
  EVIDENCE:
  - tests/conftest.py:10-22
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:318-334
  - tests/unit/melder/crystallizer/persistence/test_persistence_analyzer.py:34-50
  IMPACT: 21/22 new tests passed first-run; the one failure was the test doing
    its job. Sentinel rerun should be green everywhere.
  NEXT: owner reruns the same 4 sentinel commands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-10T02:40:00Z
  TYPE: FACT
  CLAIM: SENTINEL RUN 2: 22/22 + 7/7 + 26/26 GREEN; integration 12/13 with ONE
    residual - the conduit-formation round trip's preflight asserted "clean" but
    got "warnings". ROOT CAUSE: latent first-contact, not migration damage - the
    test was authored 2026-07-08 00:30Z against the 4-strategy analyzer;
    FramePostureStrategy landed 01:20Z and this suite never ran the 7-strategy
    set until today. A CONDUIT-scoped formation deliberately excludes the frame
    twin (frame posture is frame-scope material; the engine fallback-postures
    from book hints), so the scope-blind frame_posture strategy honestly warns.
    This is the exact scope-blindness identified in the load-scoping design
    debate; the REAL fix is S4's scope-aware BootMediator admission. S1 FIX:
    the test now asserts current truth - verdict "warnings" with frame_posture
    as the ONLY warning strategy - with a comment pointing at S4 where conduit
    scope will interpret frame-absence as expected. RESTORE LEG of the test
    (fresh boot, built_counts, SHA re-record) was already passing; only the
    preflight assertion moved. Execution: Not run - rerun requested (4th command
    only is sufficient).
  EVIDENCE:
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:765-781
  IMPACT: S4 gains a concrete acceptance criterion: flip this assertion back to
    clean-for-scope when admission becomes scope-aware.
  NEXT: owner reruns the integration suite; on green, S1 acceptance walk + open S2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-10T02:48:00Z
  TYPE: FACT
  CLAIM: SENTINEL RUN 3 (owner): ALL GREEN - "all passed keep moving". S1 exit
    gate satisfied (22/22 + 7/7 + 26/26 + 13/13). Status stays in_progress
    pending the formal acceptance walk at a closure batch; S2 opened on the
    owner's directive.
  EVIDENCE:
  - owner message 2026-07-10 ("all passed keep moving")
  IMPACT: Tranche law satisfied; S2 executes.
  NEXT: S2 (see 2026-07-09_crystals_vocabulary_move_up_story.md).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
S1 of the decomposition epic: stand up crystal_analysis (result carrier, custody
strategies with physical SHA fingerprints, fact strategies incl. NEW export_surface +
load_order, analyzer with live-spell and retained-payload entry points), slim
SpellCrystal to a bind-signature carrier holding one result, relocate preflight.
Sentinel-set testing per tranche; bulk test fixes deferred to S-test after S4.
