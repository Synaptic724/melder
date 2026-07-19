# Story: User formations (scoped snapshots) + PersistenceAnalyzer

- Completed: 2026-07-11T19:10:00Z
- Summary: Delivered in full (formation snapshots + strategy-pattern
  analyzer + load-time preflight wiring) and validated by the owner's
  subsequent 614/614 crystallizer-tree and 9702 full-tree greens; the
  formation lane then MATURED through the closed S1 story (retarget/
  skip/compose into live worlds) and the mesh lane (formations ship
  remote; the analyzer set grew to 10 rows). Closed late on
  owner-directed self-cleanup - the closure walk was overtaken by the
  successor lanes that consumed this story's output.

## Metadata
- Story ID: STORY-2026-07-07-formations-and-analyzer
- Parent Epic: EPIC-2026-07-03-crystallizer-bootstrap-checkpoint
- Status: closed (owner-directed self-cleanup 2026-07-11; delivered +
  green-covered + superseded-forward by closed successor lanes)
- Owner: cowork
- Agent Name: melder_0
- Priority: p2
- Created: 2026-07-07T23:40:00Z
- Updated: 2026-07-07T23:40:00Z

## Problem / Opportunity (owner charter)
Users can only restore WHOLE worlds. Owner wants: (1) facades to rebuild
a conduit or a frame DIRECTLY ("this also means spellbook btw" - a
conduit formation includes its book); (2) user-DEFINED named snapshots
targeting a profile - "if they like a conduit formation... just reload
that conduit"; (3) linking included, which demands a
persistence_analyzer with a STRATEGY PATTERN that pre-flights bootload
issues (missing linking, other classes of problems) before the user
trusts a formation/checkpoint.

## Design

### Slice 1 - Formations (user-named scoped snapshots)
- CAPTURE (PersistenceProfile.capture_formation_slice): a LIVE current-
  state slice (payload-only, NO journal window) scoped either by
  conduit_id (conduit twin + its spellbook twin + that book's custody
  with custody_location annotations + its spell_index twins) or by
  frame_name (frame posture twin + every book/conduit/custody/index of
  the frame + the frame's clusters). Contracts/links captured as
  recorded on the twins (conduit link_targets ride along; peers outside
  the slice surface later as analyzer findings + restore shortfalls).
- STORAGE: cache-level artifacts ONLY (no ledger involvement):
  CrystallizerCache.store_formation/load_formation/
  list_formation_names under
  __crystallizer_cache__/{profile}/__formations__/{name}.json (atomic
  tmp+replace, JSON-safe payload {"formation_name", "profile_name",
  "scope", "created_at", "description", "payloads"}).
- RESTORE (restore_formation): manufacture ONE synthetic window (journal
  minted from payloads in canonical kind order: frame -> spellbook ->
  conduit -> spell_index -> spell_crystal -> cluster -> contract) and
  run the EXISTING RestoreEngine - a formation restores exactly like a
  one-window chain, with the same all-or-nothing + shortfall honesty.
- FACADES (Crystallizer): save_formation(formation_name, conduit_id=None,
  frame_name=None, description=""), restore_formation(formation_name),
  list_formations(), describe_formation(formation_name).

### Slice 2 - PersistenceAnalyzer (strategy pattern; owner: next step)
- Package src/melder/crystallizer/persistence/analysis/:
  - persistence_analysis_strategy.py: ABC (explicit runtime inheritance
    contract across multiple implementations - the sanctioned ABC case):
    `name` property + `analyze(payload_bundle) -> List[Dict]` finding
    rows {strategy, severity ("blocker"|"warning"|"info"), kind, key,
    detail}.
  - link_integrity_strategy.py: every conduit link_target resolves to a
    conduit IN the bundle (missing -> warning: restore shortfalls it).
  - contract_peer_strategy.py: both contract endpoints present in the
    bundle (missing -> warning).
  - hydration_strategy.py: custody rebindability != hydratable ->
    warning (replay_required); synthetic root WITHOUT recorded sources
    -> blocker (pre-M3); non-synthetic roots probed via
    importlib.util.find_spec -> blocker when unfindable; book missing
    for custody's spellbook_id -> blocker.
  - configuration_loss_strategy.py: book hook_names -> info
    (code participation); aether resolver/logger presence flags -> info.
  - persistence_analyzer.py: Cleanable; owns the strategy list (default
    set when none supplied); analyze(bundle) -> {"findings", "counts by
    severity", "verdict": clean|warnings|blockers}.
- Bundle shape = {kind: {key: payload}} - works for formation payloads
  AND checkpoint captured_payloads.
- FACADES: Crystallizer.analyze_formation(name) +
  analyze_checkpoint(checkpoint_id). CrystallizerBootstrap preflight
  knob = follow-up, not this slice.

## Acceptance Criteria
- Save a conduit formation from a live world; fresh boot; restore JUST
  it (book + conduit + custody rebuilt; absent link peers shortfall).
- Frame-scoped formation captures the frame subtree.
- Analyzer flags a formation with a dangling link_target (warning) and
  a pre-M3 synthetic root (blocker); clean formation -> "clean".
- All payloads JSON-safe; formations survive process death via cache.

## Notes

- DATETIME: 2026-07-07T23:40:00Z
  TYPE: PLAN
  CLAIM: Lane opened on owner charter (scoped rebuild facades + user
    formations + analyzer via strategies; readable-graph work explicitly
    skipped per owner). Implementation order: profile slice capture ->
    cache formation storage -> system save/restore/list verbs (restore
    = synthetic window into the EXISTING engine) -> facades -> analyzer
    package -> analyzer facades -> tests per slice. crystal_analysis/
    was checked for house style: ALL placeholder files are 0 bytes, so
    the analyzer establishes the strategy-pattern style (ABC sanctioned:
    real multi-implementation runtime contract).
  EVIDENCE:
  - owner message 2026-07-07 (charter)
  IMPACT: Users keep the formations they like and pre-flight their
    bootloaders.
  NEXT: Implement slice 1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-08T00:30:00Z
  TYPE: FACT
  CLAIM: BOTH SLICES LANDED in one burst.
    SLICE 1 (formations): PersistenceProfile.capture_formation_slice
    (conduit scope = conduit + spellbook + custody-with-location +
    indexes + touching contracts; frame scope = posture + book subtrees
    + conduits + clusters + touching contracts; exactly-one-scope
    ValueError; expressive KeyErrors); CrystallizerCache
    store_formation/load_formation/list_formation_names at
    {profile}/__formations__/{name}.json (filesystem-safe name gate;
    depth-3 placement verified collision-free vs every checkpoint glob);
    PersistenceSystem save_formation/load_formation_record/
    restore_formation (synthetic single-window manufacture in canonical
    kind order -> EXISTING RestoreEngine)/list_formations; Crystallizer
    facades save/restore/list.
    SLICE 2 (analyzer): analysis/ package established (crystal_analysis
    checked: all 0-byte placeholders, no style to inherit) -
    PersistenceAnalysisStrategy ABC + LinkIntegrityStrategy (warning) +
    ContractPeerStrategy (warning) + HydrationStrategy (blockers:
    missing book / pre-M3 synthetic / find_spec-unfindable; warning:
    replay_required) + ConfigurationLossStrategy (info: hooks + root
    callable flags) + PersistenceAnalyzer (default set; verdict
    clean|warnings|blockers; info never moves the verdict); Crystallizer
    facades analyze_formation + analyze_checkpoint (checkpoint captured
    payloads share the bundle shape).
    TESTS: 4 analyzer unit tests (clean verdict, dangling link +
    absent peer warnings, 3-blocker dominance, info-only verdict) +
    the formation integration round trip (save named conduit formation
    -> clean preflight -> process death -> list survives -> restore JUST
    the formation -> same SHA re-records). Compile: all 6 analyzer
    files + both test files clean in-sandbox; profile/system/crystallizer
    Not run (replica rot; disks verified). Execution: Not run.
  EVIDENCE:
  - src/melder/crystallizer/persistence/analysis/ (6 files)
  - src/melder/crystallizer/persistence/persistence_profile.py
    (capture_formation_slice)
  - src/melder/crystallizer/persistence/crystallizer_cache.py
    (formation trio)
  - src/melder/crystallizer/persistence/persistence_system.py
    (save/load/restore/list formation verbs)
  - src/melder/crystallizer/crystallizer.py (5 new facades)
  - tests/unit/melder/crystallizer/persistence/test_persistence_analyzer.py
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py
    (tail test)
  IMPACT: Users save the conduit/frame formations they like under their
    own names, reload them directly without touching the world, and
    pre-flight any formation or checkpoint for bootload issues before
    trusting it.
  NEXT: Owner sweep. Follow-up candidates: bootstrap preflight knob
    (run the analyzer inside CrystallizerBootstrap before load),
    formation-scoped frame restore integration test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-08T01:20:00Z
  TYPE: FACT
  CLAIM: LOAD-TIME STRATEGY WIRING LANDED (owner: "we want to run the
    strategies as we're loading" - previously they were pre-flight-only
    verbs). RestoreEngine now runs the FULL default strategy set over
    the FOLDED bundle immediately after _fold_chain, before any replay;
    RestoreReport gained the "preflight" section (slots/init/cleanup/
    set_preflight/describe) - EVERY restore (load_checkpoint,
    restore_formation, bootstrap) now carries its own analysis. The
    engine never gates (all-or-nothing + shortfalls already protect);
    CrystallizerBootstrap gained the opt-in with_preflight_gate(True)
    which refuses the boot on a "blockers" verdict AFTER the protected
    restore. THREE NEW STRATEGIES (default set now 7):
    ClusterMembershipStrategy (absent members warn; recorded leader =
    info), FramePostureStrategy (books on unrecorded frames warn -
    fallback posture, not truth), SyntheticSourceIntegrityStrategy
    (recomputed SHA256 vs recorded fingerprint: mismatch = BLOCKER -
    never execute unverified source; absent fingerprint = info). TESTS:
    +3 analyzer unit tests (membership+leader severities, covered vs
    bare frame, tampered/verified/unstamped source triple) and +1
    engine test proving the preflight rides restore() reports (dangling
    link -> warnings verdict on an otherwise empty replay). Compile:
    strategies + both test files clean in-sandbox; analyzer/engine/
    bootstrap grown files Not run (replica rot; disks verified).
    Execution: Not run. NOTE: analyze_checkpoint (facade) analyzes ONE
    window's captured payloads - partial-delta findings are per-window
    truth; the ENGINE's load-time preflight analyzes the folded chain,
    where completeness findings are authoritative.
  EVIDENCE:
  - src/melder/crystallizer/persistence/restore_engine.py
    (_run_preflight + report preflight surface)
  - src/melder/crystallizer/persistence/analysis/ (3 new strategies +
    default-set update)
  - src/melder/crystallizer/crystallizer_bootstrap.py
    (with_preflight_gate)
  - tests/unit/melder/crystallizer/persistence/
    test_persistence_analyzer.py (+3) / test_restore_engine.py (+1)
  IMPACT: Analysis is no longer something users remember to run - every
    load carries it; strict boots can refuse known-unbuildable worlds.
  NEXT: Owner sweep -> closure walk (M3 story + this story together).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
