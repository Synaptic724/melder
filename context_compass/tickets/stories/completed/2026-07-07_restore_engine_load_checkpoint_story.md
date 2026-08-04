# Story: Restore Engine - load_checkpoint unfolds a recorded world (B3 + B5 shortfalls)

## Metadata
- Story ID: STORY-2026-07-07-restore-engine-load-checkpoint
- Parent Epic: EPIC-2026-07-03-crystallizer-bootstrap-checkpoint
- Status: closed
- Owner: cowork
- Agent Name: melder_0
- Priority: p2
- Created: 2026-07-07T03:00:00Z
- Updated: 2026-07-07T03:00:00Z

## Problem / Opportunity
The record is complete (wire epic Phase A) but `PersistenceSystem.load_checkpoint`
is a NotImplementedError placeholder. A checkpointed world cannot unfold on a
fresh boot. This story lands the restore engine: fold the checkpoint chain,
replay it through the PUBLIC runtime verbs in canon order, translate record-local
ULIDs to fresh identities, and report rebindability shortfalls instead of
under-building.

## MRP Alignment
All-or-nothing first cut (owner-approved 2026-07-07): a failed restore tears the
half-built world down; shortfalls are REPORTED (hooks, replay_required spells,
synthetic roots, lossy config values), never silently dropped. Correct core over
feature breadth.

## Ticket Contract
- ENTRY_GATE: bootstrap epic ready; Design Note + rebuild-side survey notes in
  epic; patch docs exist under
  system_docs/patches/active/restore_engine_2026_07_07/ and are linked below.
- EXECUTION_BOUNDARY: NEW module
  src/melder/crystallizer/persistence/restore_engine.py; the body of
  PersistenceSystem.load_checkpoint (delegation only); CAPTURE-GAP fixes on
  src/melder/crystallizer/persistence/crystals/spell_crystal.py
  (+ its constructor reads) for disposal_method_names + profile_family; tests.
  EXCLUDES: capture pipeline changes beyond the two gap fields, spellbook/
  conduit/ward/nexus surfaces, the adapter contract (persistence epic), the
  chain-integrity verb, synthetic-module loading (parent M3/M5).
- DEPENDENCIES: shipped record surfaces (replay_data, cache reload); public
  rebuild verbs (bind/bind_inactive/notch/conjure/link/contract/cluster).
- EXIT_GATE: a world sealed into checkpoints unfolds on a fresh boot via
  load_checkpoint; hydratable spells rebind; shortfall report lists everything
  not rebuilt and why; failure rolls back; tests authored; owner-run 3.14t green.
- FAILURE_ESCALATION: DECISION_REQUEST on any replay-order ambiguity the Design
  Note does not answer; CONFLICT if another agent edits persistence/** while
  this lane is open.

## Goals (Outcomes)
- RestoreEngine: fold chain 1..K (later payloads win per kind/key; tombstones
  delete), replay in canon order (aether config -> frame postures -> book
  configs -> conjure -> binds by bind_order -> staged onto index anchors ->
  notch selections -> links -> clusters -> contracts LAST), old->new ULID map,
  detached RestoreReport (built / shortfalls / translation map).
- load_checkpoint(checkpoint_id) = fold + replay + report (all-or-nothing).
- Capture-gap fixes: SpellCrystal records disposal_method_names + profile_family
  so restore passes them back into bind.

## Non-Goals
- Synthetic module re-import (parent M3/M5) - REPORTED as shortfalls.
- Hook callables (markers only, by design) - REPORTED.
- MR internals (other agent). Adapter (persistence epic, LAST).

## Requirements
- 3.14t no-GIL thread-safe; engine instances are single-use per restore call.
- Cleanup directly after __init__ (owner law); Cleanable del posture.
- No new public API on runtime classes; engine drives EXISTING public verbs.

## Acceptance Criteria
- Round-trip: record world -> seal checkpoint(s) -> fresh boot -> load_checkpoint
  -> world re-melds; re-emission re-records under fresh ULIDs.
- Tombstoned units absent after restore; staged members parked; selections match.
- Shortfall report enumerates hooks + replay_required + synthetic + lossy config.
- Failure mid-replay tears down what was built (all-or-nothing).
- Owner accepts; suites green on owner-run 3.14t.

## Risks / Mitigations
- Risk: replay ordering bug -> canon order is data-driven + integration tests.
- Risk: partial world on failure -> teardown path tested explicitly.
- Risk: write-fault -> FILE-TOOL-ONLY ticket/board writes; code via file tools.

## Validation Plan
- Unit: fold semantics (later-wins, tombstones), translation map, shortfall
  classification, report shape, engine cleanup idempotence.
- Integration: seal -> wipe -> reload-from-cache -> load_checkpoint round trip;
  staged+notch restore; link+contract re-grant; cluster regroup; failure
  rollback. All "Not run." until owner runs 3.14t.

## Applicable Anti-Patterns
- [ ] No silent under-build (shortfalls MUST be reported).
- [ ] No raw map-merge hydration (checkpoint-shaped replay only).
- [ ] No ULID rehydration (fresh identities + translation map).
- [ ] No implementation before patch docs are linked + consumed.

## State Transition Event
- from_state: none -> to_state: in_progress
- transition_reason: owner "start sending it" 2026-07-07; atomicity =
  all-or-nothing per melder_0 recommendation accepted with that directive.

## Artifact Links (Optional)
- system_docs/patches/active/restore_engine_2026_07_07/architecture_patch.md
  (disposition: promote_to_documentation)
- system_docs/patches/active/restore_engine_2026_07_07/component_patch_crystallizer_persistence.md
  (disposition: promote_to_documentation)

## Noting Behavior
- Story notes: cross-task synthesis, replay-stage progress, gate transitions.

## Notes
- DATETIME: 2026-07-07T03:00:00Z
  TYPE: PLAN
  CLAIM: Landing order: (1) patch docs, (2) SpellCrystal capture-gap fields
    (disposal_method_names + profile_family), (3) restore_engine.py (fold /
    translate / replay / report / all-or-nothing), (4) load_checkpoint body
    delegates, (5) tests. Consumption mapping (patch section -> implementation
    -> validation) recorded in the next note after patch docs land.
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-07-03_crystallizer_bootstrap_checkpoint_epic.md:103-160
  IMPACT: One narrow module + two capture fields; runtime surfaces untouched.
  NEXT: Write the two patch docs, then start implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T04:10:00Z
  TYPE: FACT
  CLAIM: FULL SLICE LANDED. (1) Capture-gap fields: SpellCrystal now records
    disposal_method_names (sorted) + profile_family (type-name duck check, no
    examiner import) - slots/init/cleanup/properties/describe all extended.
    (2) restore_engine.py NEW: RestoreReport (value-only, detached describe) +
    RestoreEngine (single-use, cleanup directly after __init__, del posture,
    lazy runtime imports). Fold: later-wins per (kind,key), tombstone sweeps
    mirror live eviction match rules, spell_activity custody moves. Replay:
    aether logger-knob only (fluent config surface is callable-bearing -
    entries report as code-participation shortfalls), books+conjure+binds in
    bind_order inside spellbook.transaction("bind") windows, staged members
    onto translated index anchors, divergent selections notched, links from
    initiator edges, clusters via ConduitCloud (leader reported), contracts
    LAST from initiated details inside link windows (index subscriptions
    reported this cut). All-or-nothing: reverse-order teardown then
    RuntimeError naming the failed stage. (3) Seat: PersistenceSystem.
    load_checkpoint assembles the profile chain DETACHED under its lock and
    runs the engine OUTSIDE it (emit re-entry safe); Crystallizer facade
    returns the report dict. (4) Tests: 18 unit (fold/report/lifecycle/
    hydration honesty) + 8 integration (cache round trip, staged+selection,
    links, contracts, tombstone hold, rollback, pre-patch tolerance,
    post-notch selection). CONSUMPTION MAPPING: patch "Capture-gap" ->
    spell_crystal edits -> unit describe checks; "Fold" -> _fold_* ->
    fold unit tests; "Translate" -> report identity map -> map tests;
    "Replay 1-9" -> _replay_* -> integration round trips; "Shortfalls" ->
    report entries -> honesty tests; "All-or-nothing" -> _teardown_built ->
    rollback test. VALIDATION: restore_engine.py py_compile OK pre-final-edit;
    spell_crystal/persistence_system/crystallizer/final engine compile
    NOT RUN in-sandbox (bash replica rot, user disk verified via file-tool
    tails) - owner runs 3.14t.
  EVIDENCE:
  - src/melder/crystallizer/persistence/restore_engine.py:1-1226
  - src/melder/crystallizer/persistence/persistence_system.py:874-945
  - src/melder/crystallizer/crystallizer.py:1235-1263
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:208-234
  - tests/unit/melder/crystallizer/persistence/test_restore_engine.py:1-999
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:1-999
  IMPACT: B3 first cut complete on disk; B5 shortfall reporting live; the
    NotImplementedError seat is gone.
  NEXT: Owner runs 3.14t (unit persistence + integration crystallizer suites
    first); melder_0 triages any fallout, then the chain-integrity verb lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T04:40:00Z
  TYPE: FACT
  CLAIM: SELF-REVIEW ROUND caught two real bugs BEFORE the owner run + landed a
    THIRD capture-gap fix. (1) GUARD REFUSAL: the engine never finalized the
    rebuilt SpellbookConfiguration, so the conjure configuration-discipline
    guard would refuse every recorded-lane conjure. FIXED: finalize() before
    binds + replay restructured to the natural lane (actives PRE-conjure via
    bind's self-admitted window - the unverified spellbook.transaction("bind")
    dependency is gone entirely; staged POST-conjure). (2) STAGED LOCATION
    BLINDNESS: _record_spell_crystal_locked journals kind "spell_crystal" for
    BOTH locations and the captured payload carried no location - staged
    members that never flipped would restore ACTIVE. FIXED capture-side:
    capture_segment_since now annotates custody payloads with
    custody_location read from the live maps; fold routes on it (pre-patch
    payloads default active). (3) AetherConfiguration is a fluent callable-
    bearing surface with no set_property - stage 1 now replays only the
    boolean activation knob and reports every other entry. Unit test added
    for the location fold; patch doc updated. VALIDATION: persistence_profile
    + unit test file py_compile OK in-sandbox; restore_engine final compile
    Not run (replica rot at the cap boundary; disk verified via file-tool
    tail read :1185-1208).
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_profile.py:973-989
  - src/melder/crystallizer/persistence/restore_engine.py:452-470
  - src/melder/crystallizer/persistence/restore_engine.py:640-700
  - tests/unit/melder/crystallizer/persistence/test_restore_engine.py:246-272
  IMPACT: Without this round the first 3.14t run would have failed on every
    conjure and silently mis-restored staged worlds - both are correctness
    saves, not polish.
  NEXT: Owner runs 3.14t (unit persistence then restore integration);
    melder_0 triages fallout, then the chain-integrity verb lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T05:45:00Z
  TYPE: FACT
  CLAIM: PRODUCER-SIDE VERIFICATION SWEEP complete - every replay input is
    now line-verified against its emitter. Cluster twin keys match the engine
    exactly (cluster_id/cluster_name/frame_name/member_conduit_ids/
    leader_conduit_id/shared_spells); cleanup_and_remove_spell accepts the id
    string; contract detail contract_type values are the lowercase enum
    names the engine filters on. Two more pre-run saves: (1) recorded
    cluster shared_spells entries now file ONE honest shortfall per cluster
    ("auto_share_governs: N") instead of folding silently; (2) the wire-era
    unit test asserting load_checkpoint's NotImplementedError placeholder
    (test_persistence_system.py) would have FAILED the owner run - updated
    to the live contract (KeyError ordering + empty-world completed report).
    No other placeholder assertions exist tree-wide. Chain-integrity task
    landed in parallel (see task ticket): verify_checkpoint_chain + facade +
    8 tests + the latent retention-numbering duplicate fixed.
  EVIDENCE:
  - src/melder/crystallizer/persistence/crystals/cluster_crystal.py:116-133
  - src/melder/aether/conduit/conduit_cluster.py:280-300
  - src/melder/aether/spellbook/spellbook.py:518-524
  - tests/unit/melder/crystallizer/persistence/test_persistence_system.py:247-269
  - src/melder/crystallizer/persistence/restore_engine.py:1090-1110
  IMPACT: The owner's first 3.14t run starts from a line-verified engine with
    zero known stale assertions; 36 tests now ride the lane.
  NEXT: Owner-run 3.14t; melder_0 triages; then kit lane (design note staged
    in the epic) on owner go.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T06:05:00Z
  TYPE: FACT
  CLAIM: OWNER-RUN TRIAGE #1. Partial 3.14t output received: new persistence
    unit tests PASSING; single failure class = component suite
    test_spell_crystal_component.py fixture setup, AttributeError 'DummySpell'
    object has no attribute 'disposal_method_names' at spell_crystal.py:220.
    Root cause: the two NEW capture-gap reads on SpellCrystal.__init__
    (disposal_method_names + profile) were never added to the spell test
    doubles. FIX: both doubles patched - tests/mocks/crystallizer/
    spell_crystal_harness.py DummySpell and the local _DummySpell in
    tests/unit/melder/crystallizer/test_crystallizer.py now carry
    disposal_method_names=[] and profile=SimpleNamespace() (type-name duck
    check classifies SimpleNamespace as the "general" fallback - correct for
    a minimal double). Consumer sweep: every create_spell_crystal caller
    routes through these two doubles or asserts the activation gate before
    any spell read (test_crystallizer_gates.py). No production code touched.
  EVIDENCE:
  - tests/mocks/crystallizer/spell_crystal_harness.py:17-38
  - tests/unit/melder/crystallizer/test_crystallizer.py:14-33
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:213-231
  IMPACT: Fixture-setup error class cleared for the whole component/unit/
    integration spell-crystal family. Compile: harness Not run (replica rot;
    disk verified), test_crystallizer.py py_compile OK.
  NEXT: Owner reruns 3.14t (same order); triage any remaining fallout -
    the paste cut off mid-run, so later failures may still surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T07:30:00Z
  TYPE: FACT
  CLAIM: OWNER-RUN TRIAGE #2 - the round-trip suite caught a PRODUCTION
    record gap (capture gap #4, audit correction): SpellbookCrystal never
    emitted in any legal recorded world. Emission lived only inside
    SpellbookConfiguration.freeze(origin...) which early-returns for frozen
    configs, while the dynamic-mode bind guard FORCES finalize-before-bind
    and the conjure-side _validate_and_freeze_configuration short-circuited
    frozen configs without calling freeze. Every finalize-first world sealed
    windows with no book twin; restore folded nothing and truthfully
    reported "complete" with zero builds (the fold's silent-skip on missing
    payloads masked the upstream absence). FIXED both sides: freeze()
    routes emission through new _emit_spellbook_twin_when_recording on both
    the fresh-freeze and frozen re-entry paths; conjure re-enters freeze
    with origin identity. Emission fires exactly once per book. ALSO FIXED:
    (a) _replay_contracts direction was BACKWARDS - ward truth: details
    live in the lineage OWNER's map (both labels), the verb is borrower-
    called naming the owner; engine now replays every detail as
    borrower.add_spell_to_contract(conduit=owner) (was initiated-only,
    owner-called); (b) engine loads the default config dictionary before
    overlaying recorded properties (pre-patch/lossy windows finalize on
    defaults - fixes the tolerance test's legitimate lane); (c) round-trip
    contract test's record lane corrected to borrower-called. Verification
    trail: replay_data/codec/reload/chain-assembly/fold all line-verified
    intact before the root cause landed on the emission factor.
  EVIDENCE:
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:252-350
  - src/melder/aether/spellbook/spellbook.py:4975-4990
  - src/melder/crystallizer/persistence/restore_engine.py:690-700
  - src/melder/crystallizer/persistence/restore_engine.py (stage 9 loop)
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:311-319
  IMPACT: The record now actually carries spellbooks in the only legal
    recorded bind lane; restores stop silently unfolding empty worlds;
    contract re-grants run in the direction the ward accepts. The passing
    rollback/tolerance/harness suites plus 13+ record integration tests
    were already green this run.
  NEXT: Owner reruns 3.14t. Open verification question for the rerun: the
    empty-fold silence - consider a fold-level shortfall when a journal
    entry has no payload (honesty guard) as a follow-up.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T08:20:00Z
  TYPE: FACT
  CLAIM: OWNER-RUN TRIAGE #3 (owner directive: "go read the code" - and the
    code settled it). Rerun failures were uniform: conjure(dynamic=True)
    refused with system_state=automatic. Root cause is a REPLAY gap, not
    capture: AethericFrameCrystal already records the full frame posture
    (system_state_name/rift/ai_native + describe_posture dev-ops surface;
    emitted at frame-config freeze with origin_frame_name, dynamic-only
    gate), and frames are the posture OWNERS - check_system_state reads
    spellbook._aetheric_frame_configuration, the FRAME-owned object the
    book merely retains (_initialize_aetheric_frame_configuration). The
    engine folded "frame" twins into _frames and never replayed them, so
    rebuilt frames kept the fresh-boot automatic default and every book
    conjure was refused. FIX: new stage 2 "frames" - _replay_frames +
    _posture_frame build an attempted AethericFrameConfiguration from the
    twin payload and bind via frame.bind_frame_configuration (copy-into-
    canonical + freeze WITH origin => twin re-emits; idempotent for
    matching frozen postures). Missing-twin fallback _ensure_frame_postured
    postures dynamic from book config hints + shortfall. Slots/init/
    cleanup carry _postured_frames (del posture). Verified before coding:
    posture ctor keyword surface (15 fields), with_defaults switch values
    (ctor-identical), bind_frame_configuration branches, Spellbook posture
    retention, and that the original test lane DID emit frame twins (the
    posture sync helper postures the frame pre-book; first bind freezes
    with origin).
  EVIDENCE:
  - src/melder/crystallizer/persistence/restore_engine.py (stage list,
    _replay_frames/_ensure_frame_postured/_posture_frame)
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:309-362
  - src/melder/aether/aetheric_frame/aetheric_frame.py:518-625
  - src/melder/aether/spellbook/spellbook.py:4811-4835
  - src/melder/crystallizer/persistence/crystals/aetheric_frame_crystal.py
  IMPACT: Rebuilt worlds now carry their recorded frame postures (including
    the dev-ops disable_* switches and wait times), frames re-record on
    restore, and the dynamic conjure gate reads recorded truth.
  NEXT: Owner rerun (restore integration file first). Compile Not run
    (replica rot; disk verified).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T08:50:00Z
  TYPE: DECISION
  CLAIM: OWNER RULING adopted - restore rebuilds configurations through
    dedicated RELOAD lanes, never defaults/authoring lanes (defaults drift;
    defaults-first rebuilds silently rewrite sealed history). Landed:
    SpellbookConfiguration.load_recorded_dictionary (recorded-first via
    set_property; rejected list carries "key: reason"; required-key
    backfill via load_default_dictionary's populate-missing-only semantics,
    returned per-key) + AethericFrameConfiguration.from_recorded_posture
    (classmethod; system_state_name hard-required - the reload lane never
    guesses a frame state; all other absent keys default-with-report).
    Engine rewired: books and frames consume the reload verbs and file
    per-key shortfalls (config_property_not_replayable /
    config_property_backfilled_schema_default /
    posture_key_backfilled_schema_default); _posture_frame reduced to
    bind-only; the missing-twin frame fallback stays an explicit authoring
    construction (nothing recorded to reload) with one tolerance
    shortfall. load_default_dictionary is gone from the engine.
  EVIDENCE:
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py
    (load_recorded_dictionary, after load_default_dictionary)
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py
    (from_recorded_posture, before dynamic_defaults)
  - src/melder/crystallizer/persistence/restore_engine.py
    (_replay_frames / _ensure_frame_postured / _posture_frame / book loop)
  IMPACT: Sealed worlds rebuild from sealed truth; schema evolution
    surfaces as reported shortfalls instead of silent default drift. Both
    verbs are engine-consumed today and kit-import-ready tomorrow.
  NEXT: Owner rerun (restore integration file first). Compile Not run
    (replica rot; disk verified on all three files). 6 reload-lane unit
    tests authored in tests/unit/melder/aether/
    test_configuration_reload_lanes.py (recorded-wins, per-key rejected
    with reason, recorded-beats-default, full-payload round trip, 13-key
    defaulted report + unfrozen contract, stateless refusal) - py_compile
    OK in-sandbox, execution Not run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T09:30:00Z
  TYPE: FACT
  CLAIM: OWNER REPORTS ALL TESTS PASSED (run 3) - the full restore lane is
    GREEN end-to-end: record -> seal -> flush -> fresh boot -> reload ->
    load_checkpoint -> re-melded re-recording world. Plus owner spec
    refinement adopted post-green: the reload verbs LOAD AND FREEZE in one
    motion. load_recorded_dictionary and from_recorded_posture now seal
    internally (standalone freeze, no origin identity so no twin emission;
    the spellbook conjure-time freeze re-entry and the frame bind-time
    freeze carry identity and emit). Engine's separate finalize() call
    removed (comment updated, not deleted); payload inputs documented as
    the JSON-safe cached-item shapes; the 2 affected reload-lane unit
    tests updated to sealed-on-return contracts (set_property /
    with_rift_enabled refused post-reload). No engine behavioral delta:
    the config reaches Spellbook construction frozen exactly as the green
    run proved; only freeze ownership moved into the verbs.
  EVIDENCE:
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py
    (load_recorded_dictionary: internal freeze)
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py
    (from_recorded_posture: internal freeze)
  - src/melder/crystallizer/persistence/restore_engine.py (finalize call
    removed from the book loop)
  - tests/unit/melder/aether/test_configuration_reload_lanes.py
  IMPACT: Reload is one atomic internal motion per owner spec; no caller
    can hold a mutable half-reloaded configuration.
  NEXT: Owner rerun to confirm the refinement holds green (restore
    integration + test_configuration_reload_lanes.py). Compile Not run
    (replica rot; disk verified). Then: closure walk for story + task, or
    the kit lane on owner go.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T09:55:00Z
  TYPE: FACT
  CLAIM: RUN 4 TRIAGE - 1 failure, 5 passes, failure was MY TEST-AUTHORSHIP
    BUG and the verb behaved exactly per contract: the payload fed
    system_state / ai_native_enabled / rift_enabled to
    load_recorded_dictionary, but the posture trio lives on the FRAME
    configuration, not the spellbook property registry - the reload verb
    honestly rejected all three with reasons (the rejection lane working as
    designed; run 3's green integration lane confirms real recorded
    payloads never carry posture keys). Test rewritten to registered
    rich-config properties (workers/disposal/disposal_method_names) with
    a comment routing posture keys to the refused-keys test; asserts
    recorded-wins, precise backfill membership, and sealed-on-return.
    py_compile OK in-sandbox. Side-proof from the run: available registry
    == the defaults-table keys (validate froze happily on backfill alone),
    so the registry and defaults table are in lockstep today.
  EVIDENCE:
  - tests/unit/melder/aether/test_configuration_reload_lanes.py:21-50
  IMPACT: Suite contract now matches the real property registry; no
    production code touched.
  NEXT: Owner rerun of test_configuration_reload_lanes.py; on green,
    closure walk.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-07T10:40:00Z
  TYPE: FACT
  CLAIM: OWNER DIRECTIVE LANDED - reload lanes for ALL configurations (MR
    excluded as too new) + the crystallizer's own persistence crystal.
    NEW: AetherConfiguration.from_recorded_payload,
    NexusConfiguration.load_recorded_dictionary (+ emission fidelity:
    enum->name/collections->list branches; emission seam extracted to
    emit_configured_twin_when_recording; Nexus.enable emits for pre-frozen
    reloaded configs - spellbook-conjure fix class),
    CrystallizerConfiguration.load_recorded_dictionary, and the NEW
    CrystallizerCrystal twin self-emitted at Crystallizer.activate
    (profile slot/record/resolve/cleanup wired; journal kind
    "crystallizer"/"root"). Engine: folds the crystallizer twin ->
    boot-time-act shortfall; stage 1 rewired to the aether reload verb +
    LATENT FIX (configuration.activate() before Aether.activate - old
    lane would have raised; masked because stage 1 never ran in green
    worlds). All verbs load-and-freeze per owner spec. 8 new unit tests
    (aether knob+callable report, aether missing-knob report, nexus
    round-trip of emission forms, nexus frozen-refusal, crystallizer
    policy reload, crystallizer twin round trip) in
    test_configuration_reload_lanes.py (now 14 tests). Compile: nexus_
    configuration + crystallizer_crystal + earlier test file OK
    in-sandbox; five grown files Not run (replica rot; disk verified).
  EVIDENCE:
  - src/melder/aether/aether_configuration.py (from_recorded_payload)
  - src/melder/nexus/configuration/nexus_configuration.py
    (load_recorded_dictionary/_coerce_recorded_value/emission seam)
  - src/melder/nexus/nexus.py:578-600 (enable pre-frozen emission)
  - src/melder/crystallizer/configuration/crystallizer_configuration.py
    (load_recorded_dictionary)
  - src/melder/crystallizer/persistence/crystals/crystallizer_crystal.py
  - src/melder/crystallizer/crystallizer.py (activate self-emission)
  - src/melder/crystallizer/persistence/persistence_profile.py (slot/
    record/_resolve_twin/cleanup)
  - src/melder/crystallizer/persistence/restore_engine.py (fold + stage 1)
  IMPACT: Every config in the recorded world reboots from sealed JSON
    truth; the recorder records itself; nexus records stop stringifying
    enums/tuples lossily.
  NEXT: Owner-run 3.14t (reload-lane unit file + restore integration +
    full sweep recommended: the nexus/aether emission changes touch
    record content). Follow-up flagged: boot orchestration verb reading
    the cache to reload crystallizer config pre-activation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T11:10:00Z
  TYPE: FACT
  CLAIM: WHOLE-SYSTEM RESTORE COMPLETE (owner directive; MR excluded).
    Nexus was the last unrestored root: the twin recorded but the engine
    never replayed it, and nexus_state fell through the fold silently.
    LANDED: fold branches for nexus / nexus_state (later-wins lifecycle
    name) / mutation_research+state (honest
    mutation_research_recorded_not_restored_first_cut shortfall, never
    silent) + new engine stage 1b _replay_nexus - config rebuilds through
    NexusConfiguration.load_recorded_dictionary (per-key shortfalls),
    enables through the public verb (pre-frozen emission seam re-records
    the root), final "disabled" replays enable-then-disable, final
    "cleaned" skips with report; nexus rides _built_stack for
    all-or-nothing teardown. Slots/init/cleanup carry the two new folded
    fields. Integration test added: nexus round trip across the boot
    boundary (built_counts nexus==1, is_enabled, recorded governance value
    survives). Replay coverage now: aether, crystallizer(boot-reported),
    nexus, frames, books/binds/custody/selections, links, clusters,
    contracts - every recorded kind folds to a build, a report, or a
    tombstone; nothing silent. Compile: engine + integration file OK
    in-sandbox this pass.
  EVIDENCE:
  - src/melder/crystallizer/persistence/restore_engine.py (_replay_nexus,
    fold branches, slots)
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py
    (test_round_trip_restores_the_nexus_root)
  IMPACT: A persistence-crystal chain now restores the WHOLE system - the
    stated point of the record.
  NEXT: Owner-run full sweep. Then closure walk (story + chain task) and
    the kit lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T11:40:00Z
  TYPE: FACT
  CLAIM: AETHER ROOT REGENERATION closed (owner instinct confirmed by
    code). The config RESTORE already existed (stage 1 reload verb +
    Aether.activate, which applies the configuration into the
    AetherUtilitySystem through _apply_configuration_to_utility_system -
    the utility system regenerates transitively through the real lane).
    The REAL hole was emission ORDER: the aether twin emitted only at
    AetherConfiguration.activate, which structurally precedes crystallizer
    activation (the aether hosts it) - so normal boots never recorded the
    root at all (why stage 1 never fired in green runs). FIX: emission
    extracted to AetherConfiguration.emit_configured_twin_when_recording
    (same seam class as nexus enable / spellbook conjure re-freeze);
    activate still calls it, and Crystallizer.activate now performs a
    targeted ROOT CATCH-UP - emitting the already-active aether's twin
    once recording is live (guarded on aether presence/configured; a
    targeted root emission, NOT a world walk - bind still owns structural
    emission). Both files compile in-sandbox. FOLLOW-UP flagged: audit
    AetherUtilitySystem for configured surface beyond the aether config
    (unaudited; if any exists it is unrecorded today).
  EVIDENCE:
  - src/melder/aether/aether_configuration.py
    (emit_configured_twin_when_recording)
  - src/melder/crystallizer/crystallizer.py (activate root catch-up)
  IMPACT: Normal-boot worlds now record their aether root, so restores
    regenerate it (config + utility-system application) instead of
    skipping stage 1 for lack of a twin.
  NEXT: Owner-run full sweep covers this (aether twin now appears in every
    recorded world - twin-count assumptions may shift).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T12:00:00Z
  TYPE: DECISION
  CLAIM: OWNER CANONICAL ORDER adopted in the stage machine:
    Aether|AetherUtilitySystem -> Crystallizer -> MR -> Nexus ->
    AethericFrame -> Spellbook -> Conduit|Ward. Engine restore() now runs
    stages: aether_configuration -> crystallizer_policy (boot-time report,
    extracted from the aether stage) -> mutation_research (NEW ordered
    honest-report stage; MR folds to stores instead of fold-time
    shortfalls) -> nexus -> frames -> books_and_binds -> links ->
    clusters -> contracts. Stage docstrings renumbered; slots/init/cleanup
    carry the two MR fold fields. Owner also confirmed the aether root
    catch-up is legitimate (crystallizer hosts on aether but is not
    config-DEPENDENT on it). Compile Not run (replica rot; disk verified
    at the cut line).
  EVIDENCE:
  - src/melder/crystallizer/persistence/restore_engine.py (restore stage
    sequence, _replay_crystallizer_policy, _replay_mutation_research)
  IMPACT: Restore order now mirrors the canonical boot order exactly;
    MR/crystallizer truth reports in-order, never silently.
  NEXT: Owner-run full sweep; then closure walk + kit lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T12:40:00Z
  TYPE: FACT
  CLAIM: TRIAGE #4 (--last-failed run) - 4 classes, all fixed. (1) DOMINANT
    (120 errors): crystallizer activation self-emission called get_property
    on every registered key; fluent-built configs legally leave optional
    keys unset -> KeyError. FIX: has_property guard - the twin records the
    CONFIGURED surface only (reload backfills-with-report). (2) Journal
    count drift (+1 everywhere the policy twin now emits): three exact-count
    assertions updated with explanatory comments (record_sinks 0->1 and
    4->5, record_component 6->7). (3) My reload-lane test asserted a raw
    string tuple; the property system normalizes source roots to resolved
    Paths - assertion now compares Path("/recorded/root").resolve().
    (4) Stale fold test expected the OLD fold-time state-switch shortfalls;
    rewritten to the whole-system contract (states fold to stores, zero
    fold shortfalls; renamed test_fold_state_switches_land_in_stores_not_
    shortfalls). No production logic changes beyond the has_property guard.
    Compile: three clean in-sandbox; crystallizer.py + test_restore_engine
    Not run (replica rot; disk verified).
  EVIDENCE:
  - src/melder/crystallizer/crystallizer.py (activation emission guard)
  - tests/unit/melder/crystallizer/test_crystallizer_record_sinks.py
  - tests/component/melder/crystallizer/test_crystallizer_record_component.py
  - tests/unit/melder/aether/test_configuration_reload_lanes.py
  - tests/unit/melder/crystallizer/persistence/test_restore_engine.py
  IMPACT: The 120-error class was one guard; everything else was expected
    record-content drift from the new policy twin.
  NEXT: Owner rerun --last-failed; on green, closure walk + kit lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T13:05:00Z
  TYPE: FACT
  CLAIM: CLOSED - acceptance walk on owner-run GREEN ("all passed", runs
    3-6 collectively prove every lane). Criteria walk: (1) a checkpointed
    world unfolds on a fresh boot via load_checkpoint - PROVEN (round-trip
    binds/conduit/links/contracts/staged/selection/tombstone/nexus
    integration tests); (2) all-or-nothing rollback - PROVEN (injected
    failure test, frame._conduits == {}); (3) shortfalls honest and
    per-key - PROVEN across reload lanes + fold honesty guard; (4)
    WHOLE-SYSTEM scope per owner: aether root (+ utility system via
    activate) + crystallizer policy twin + nexus + frames + books/binds/
    custody/selections + links + clusters + contracts, canonical boot
    order, MR excluded-with-report. Session bug ledger: 4 capture gaps,
    contract direction inversion, freeze/conjure emission gap class fixed
    in THREE seams (spellbook conjure, nexus enable, aether catch-up),
    latent aether activate-order, latent retention numbering duplicate,
    120-error has_property guard. Reload verbs on all 5 configurations
    (load-and-freeze, JSON cached-item shapes). Remaining program work
    moves to: patch-doc promotion (closure of the patch lane, needs the
    C-doc tail repairs), kit export/import lane (design note staged in
    the epic), AetherUtilitySystem configured-surface audit, public
    frame/ConduitCloud accessors.
  EVIDENCE:
  - system_docs/patches/active/restore_engine_2026_07_07/ (full deltas)
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py
  IMPACT: The persistence crystal restores the whole system - the record's
    stated purpose - owner-run proven.
  NEXT: none (closed). Follow-ups tracked in the bootstrap epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Restore engine story under the bootstrap epic. Record verified complete except
two capture gaps (disposal_method_names, profile_family) - fixed here. Engine
folds the chain, replays through public verbs in canon order, mints fresh
identities, reports shortfalls, and rolls back on failure.
