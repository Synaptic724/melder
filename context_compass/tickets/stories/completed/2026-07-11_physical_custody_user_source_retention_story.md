# Story: S2 physical custody - opt-in user-source TEXT retention

## Metadata
- Story ID: STORY-2026-07-11-physical-custody-user-source-retention
- Parent: EPIC-2026-07-11-crystallizer-v3-horizon-iteration (tranche S2)
- Status: closed
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-11T18:30:00Z
- Updated: 2026-07-11T18:30:00Z

## Problem / Opportunity
Spells whose source lives in USER FILES cannot rebuild on a fresh pod: the
SpellCrystal manifest records paths and bind-time SHA256 fingerprints
(physical_module_fingerprints - already shipped), but not text. Synthetic
modules already retain text (M3 synthetic_module_sources) and rebuild
through the normal import lane. S2 mirrors that lane for user-owned
modules, OPT-IN (user code may be large/sensitive; retention is a policy
choice, never a default).

## Ticket Contract
- ENTRY_GATE: epic tranche order (owner 2026-07-11); investigation
  complete (see 18:30Z note).
- EXECUTION_BOUNDARY: crystallizer/configuration (flag),
  crystallizer.py (threading), crystals/spell_crystal.py (payload),
  crystal_analysis/ (harvest + result + preflight strategies),
  crystal_loader_system/restore_engine.py (rebuild lane), tests, patch
  docs. Nothing outside crystallizer.
- DEPENDENCIES: none (S1 closed). LAWS: normal-verbs restore (configs
  excepted); retained user modules rebuild through the SYNTHETIC MODULE
  LANE (register->publish->execute->import - the sanctioned from-text
  path); shortfall honesty; additive/byte-compatible facades.
- EXIT_GATE: patch docs before code; owner-run full tree green;
  acceptance walk.
- FAILURE_ESCALATION: breakage beyond crystallizer -> CONFLICT + stop.

## Pinned Design (from source, 2026-07-11)
1. FLAG: `retain_user_sources: bool` in CrystallizerConfiguration
   (schema entry + with_defaults False + @property +
   with_retain_user_sources fluent setter + reload-lane coverage).
2. THREADING (all additive, default False): Crystallizer.
   build-spell-crystal seam (crystallizer.py:1011) already passes
   user_source_root_paths from _configuration; add retain_user_sources ->
   SpellCrystal ctor -> CrystalAnalyzer ctor.
3. HARVEST (mirror of the M3 synthetic lane, analyzer walk loop
   crystal_analyzer.py:486-493): when a walked module classifies
   user_source AND retention is on, capture via the custody strategy's
   EXISTING resolve_source seam -> result.record_user_module_source
   (payload: text, sha256, path, package) -> new
   `user_module_sources` dict on CrystalAnalysisResult.describe() ->
   SpellCrystal.describe() surfaces it (additive key).
   SCOPE RECOMMENDATION: ALL reachable user_source modules (exact mirror
   of the synthetic lane; root-only would strand user dependency modules
   and yield partial rebuilds). Owner may narrow.
4. RESTORE (engine): during custody hydration, when a user root/dep
   module import fails because the file is ABSENT and retained text
   exists -> rebuild through the synthetic module lane + shortfall
   "user_module_rebuilt_synthetic_from_retained_source". Absent + no
   retention keeps today's honest failure.
5. DRIFT RULE (recommended): when the file EXISTS on disk, THE LIVE FILE
   WINS (users own their code); recorded-sha-vs-disk mismatch reports a
   WARNING "user_source_drifted_since_seal" (fingerprints already
   recorded - comparison is free). Retained text is a fallback, never an
   override.
6. PREFLIGHT: hydration_strategy upgrades missing-user-file findings from
   blocker to info when retained text exists; new
   user_source_integrity_strategy mirrors the synthetic SHA integrity
   strategy (retained-text sha vs recorded fingerprint tamper check =
   blocker; disk drift = warning per rule 5).

## Acceptance Criteria
- With retention ON: seal a world containing user-file spells, delete the
  user source tree, fresh-boot restore rebuilds those spells through the
  synthetic lane with honest shortfalls; full tree green.
- With retention OFF (default): byte-identical behavior to today.
- Facades stay byte-compatible supersets (additive keys/params only).
- Drift and tamper are reported per rules 5/6, never silent.

## Applicable Anti-Patterns
- [ ] Patch docs before code.
- [ ] No special loaders (synthetic lane IS the sanctioned path).
- [ ] No retention by default (opt-in only).
- [ ] "Not run." until the owner runs.

## Notes
- DATETIME: 2026-07-11T18:30:00Z
  TYPE: FACT
  CLAIM: Investigation complete; design pinned above from source.
    Key finds: physical_module_fingerprints (bind-time sha256 of physical
    modules) ALREADY ships in the crystal
    (crystal_analysis_result.py:284-311) - integrity substrate exists;
    UserSourceCustodyStrategy already owns resolve_source (:121) - the
    harvest is one retained copy of an existing read;
    the M3 synthetic lane provides the exact template at every layer
    (harvest crystal_analyzer.py:486-493, payload result.py:258-282,
    engine consume restore_engine.py:1715, preflight
    hydration/integrity strategies). Two design defaults surfaced to the
    owner: harvest scope = ALL reachable user modules (recommended);
    drift rule = live file wins + warning (recommended).
  EVIDENCE:
  - src/melder/crystallizer/configuration/crystallizer_configuration.py:33-61
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:460-504
  - src/melder/crystallizer/crystal_analysis/crystal_analysis_result.py:258-311
  - src/melder/crystallizer/crystal_analysis/preflight/hydration_strategy.py:70-95
  IMPACT: S2 is a mirror-build, not new architecture; risk concentrates
    in the engine rebuild lane and record-size honesty.
  NEXT: owner nod on the two defaults -> patch docs -> implement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T19:40:00Z
  TYPE: FACT
  CLAIM: IMPLEMENTED per the pinned design (patch
    crystallizer_s2_user_source_retention_2026_07_11 authored FIRST:
    architecture + component_patch_retention_chain). Landed: (1) config
    flag retain_user_sources (schema + defaults False + property + fluent
    setter; reload lane rides free); (2) additive threading Crystallizer
    -> SpellCrystal -> CrystalAnalyzer; (3) harvest: base-strategy
    harvest_payload default None + UserSourceCustodyStrategy override
    (existing _read_source_like_file + fingerprint; payload text/sha/
    path/is_package); (4) result store record_user_module_source +
    property + describe key + cleanup + analyze_payload re-fold +
    SpellCrystal.describe additive "user_module_sources"; (5) engine:
    _import_qualified_target extraction + _rebuild_user_world (absent
    files only - LIVE FILE WINS; sys.modules skip; dot-depth order;
    SyntheticModule lifecycle with binding sentinel
    "user_source_retained"; built-stack teardown; shortfall
    "user_module_rebuilt_synthetic_from_retained_source"; single import
    retry); (6) preflight: hydration absent-module blocker downgrades to
    info when text is retained; NEW UserSourceIntegrityStrategy (8th
    default row): tamper=blocker, drift vs bind fingerprint=warning
    "user_source_drifted_since_seal" (read_text mirrors the custody read
    - CRLF never false-drifts), unverifiable=info; (7) 6-test unit suite
    test_user_source_retention.py (flag lanes, harvest happy+None,
    store/describe/re-fold detachment, tamper/drift/absent rows,
    hydration downgrade, default-set registration). CORRECTED during
    authoring: preflight strategies are stateless ABCs (no cleanup) -
    test calls adjusted; drift hash uses read_text not read_bytes.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1625-1700,1760-1860
  - src/melder/crystallizer/crystal_analysis/preflight/user_source_integrity_strategy.py:1-165
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:496-518
  - tests/unit/melder/crystallizer/crystal_analysis/test_user_source_retention.py:1-232
  IMPACT: Fresh pods rebuild user-file spells from retained text through
    the sanctioned synthetic lane; retention-off stays byte-identical.
  TESTS: Not run (sandbox; replica rot on grown files - disk verified via
    file-tool sentinels; new files parsed clean). Owner 3.14t run is the
    exit gate. Integration seal->delete-tree->restore round-trip flagged
    as a validation expectation (candidate follow-up test with the owner
    run).
  NEXT: owner run; then the MR integration/twin epic (owner-directed,
    authored by another agent).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T04:40:00Z
  TYPE: FACT
  CLAIM: CLOSED - owner runs GREEN. ACCEPTANCE WALK: (1) retention ON:
    the end-to-end test seals a real user-file spell, asserts the
    crystal carries the text, deletes the file + evicts sys.modules,
    fresh-boots, and load_checkpoint rebuilds through the synthetic
    lane with the named shortfall and the module import-resolvable -
    owner-run green; (2) retention OFF (default) byte-identical -
    proven by the untouched pre-S2 suites staying green; (3) facades
    additive-only (flag + describe key + preflight rows); (4) drift and
    tamper report per the pinned rules (integrity-strategy unit matrix
    green; CRLF-safe hashing). Owner rulings honored: opt-in only,
    live-file-wins, synthetic lane = the sanctioned from-text path.
  EVIDENCE:
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:995-1075
  IMPACT: Fresh pods rebuild user-file spells from the record alone.
  NEXT: none (story closed); promotion rides the batched pass.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
S2 tranche: opt-in user-source TEXT retention mirroring the M3 synthetic
lane end to end (flag -> threading -> harvest -> payload -> engine rebuild
via synthetic lane -> preflight). Fingerprints already shipped; laws:
normal-verbs restore, opt-in only, live-file-wins drift rule.
