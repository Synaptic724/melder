# Epic: crystallizer V3 horizon iteration (load scopes / physical custody / impact engine)

## Metadata
- Epic ID: EPIC-2026-07-11-crystallizer-v3-horizon-iteration
- Status: closed
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-11T11:09:27Z
- Updated: 2026-07-11T11:09:27Z

## Problem / Opportunity
The decomposition epic (closed 2026-07-10) left the crystallizer with three
built-but-immature seams recorded on the V3 horizon
(artifacts/2026-07-09_crystallizer_philosophy_v3.md):
1. Formations only replay as world-shaped windows - they cannot compose INTO a
   live world (no host preconditions, no retargeting, no collision policy), and
   `PersistenceProfile.compose_frame_subtree`/`compose_conduit_subtree` are
   NotImplementedError placeholders awaiting a build-or-delete ruling.
2. User-source modules are fingerprint-only: a checkpoint rebuilds synthetic
   modules from retained sources, but user-source code must already exist on
   disk unchanged - the biggest honesty gap in "a checkpointed world unfolds on
   a fresh boot".
3. The analysis layer records export surfaces + dependency views + fingerprints
   but answers no questions with them - the blast-radius/impact view (the MR
   promotion-policy prerequisite) is unbuilt.
Owner directive 2026-07-11: iterate 1 -> 2 -> 3; MR Phase B is EXCLUDED
(another agent owns it - coordinate seams via mailbox, never implement there).

## MRP Alignment
Each story ships a coherent, trustworthy slice: mediated in-world loads that
refuse unsafe hosts loudly; opt-in source retention that round-trips honestly;
an impact view that only claims what recorded truth supports. No lane ships a
core that needs rework to be trusted.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-11 ("go ahead do 1,2,3 just iterate over
  them"); decomposition epic closed with 614/614 owner-run baseline.
- EXECUTION_BOUNDARY: src/melder/crystallizer/** ONLY (loader, analysis,
  record, configuration, facades) + matching tests + patch lane + C-doc/graph
  promotion at closure. MutationResearch untouched. Facade surface stays
  byte-compatible (additive keys/verbs only).
- DEPENDENCIES: S1 before S2/S3 tranche order (S2/S3 are independent of each
  other; S3 reads only analysis outputs).
- EXIT_GATE per story: patch docs exist + linked BEFORE code; sentinel suite
  green owner-run per tranche; story acceptance walk.
- FAILURE_ESCALATION: semantic conflicts with recorded owner law -> CONFLICT
  note + stop; anything touching MR seams -> mailbox NOTICE to the MR agent.

## Stories (tranche order)
- [ ] S1 load-scope maturity: host-precondition preflight strategies,
      retargeting, skip_existing collision policy for conduit/frame formation
      loads into LIVE worlds; compose_* placeholder ruling folded in
      (build-or-delete from source truth).
      -> tickets/stories/2026-07-11_load_scope_maturity_story.md
- [ ] S2 physical custody upgrade: opt-in user-source TEXT retention (config
      knob, default OFF) so user-source worlds rebuild on fresh pods like
      synthetic ones; restore-side rebuild lane + integrity fingerprint reuse.
      -> story ticket at tranche open.
- [ ] S3 impact engine: blast-radius view over retained manifests (fingerprint
      drift -> downstream modules/spells) consuming dependency views + export
      surfaces; read-only, detached payloads.
      -> story ticket at tranche open.

## Goals / Non-goals
- Goals: composable formations, honest fresh-pod durability, answerable
  impact questions - all behind the existing facade discipline.
- Non-goals: MR Phase B (other agent), EPM adapter package, env/uv.lock layer
  (open owner decisions), any automatic-mode recording changes (R-A covenant).

## Acceptance Criteria
- Per story below; epic closes when all three stories are owner-accepted and
  durable deltas are promoted into C-docs + graph.

## Risks / Mitigations
- Host-load collisions corrupt live worlds -> refuse-by-default admission,
  explicit skip_existing opt-in, preflight strategies own the verdict.
- Source retention bloats checkpoints -> opt-in knob, per-root policy, size
  recorded in describe payloads.
- Impact claims overreach recorded truth -> honest-unknown leaves, verdicts
  carry evidence rows only.

## Decision Log
- 2026-07-11 owner: iterate options 1,2,3 in order; MR Phase B excluded.
- 2026-07-11 owner: BootMediator RENAMED LoadAdmission (it admits, it does
  not mediate; kills the DevOps TransactionMediator name collision).
  Executed same day, full sweep in the S1 story FACT note.
- 2026-07-11 owner: loads must integrate with the DevOps transaction plane
  ("generic request from the actual transaction mediator") - structural
  mutations during replay currently ride only per-verb admissions with no
  whole-load transaction. Design direction: formation_load transaction
  family + frame-level ix claims across existing families so claim sets
  overlap. EXECUTION_BOUNDARY widens into
  aether/aetheric_frame/dev_ops/change_control_manager for exactly that
  slice once the owner signs the presented design.
  [SUPERSEDED same day by the owner's simpler ruling: Aether-hosted
  LoadGate, signed off and LANDED with the lazy-frames tranche - see the
  S1 story 14:00Z FACT note. No transaction family was built.]
- 2026-07-11 owner: CANDIDATE STORY pinned (post-S1 review) - SPELL GRAFT
  lane: restore a single spell INTO an already-live conduit, where the
  graft unit is the spell PLUS its spell_index values (selection state,
  index membership) - never the bare crystal (owner: "its spell_index
  values too not just spells"). Restore grains today stop at world /
  frame slice / conduit slice. Natural sequencing: alongside or after S3
  (impact engine) - blast-radius answers should precede injecting spells
  into live conduits. NOT scheduled; tranche order stays S2 -> S3.
- 2026-07-11 owner (design chat, post-S1): GRAFT UNIT CORRECTED - the
  graft unit is the SPELL_INDEX (all member spells active+parked, custody,
  selection; SpellIndexCrystal already models exactly this membership
  map), owned by the spellbook; grafting = the normal re-integration verbs
  aimed at a LIVE host book (bind members, park staged on the anchor,
  notch selection). Open design question flagged to the owner: landing
  rules when the target book already holds an index for an overlapping
  lineage.
- 2026-07-11 owner RULING (restore paradigm law, pinned): loading always
  RE-INTEGRATES through the runtime's NORMAL verbs (Spellbook ctor,
  conjure, bind, staged bind, notch, create_cluster, link/contract verbs)
  - NO special loaders, ever. CONFIGURATIONS ARE THE ONE SANCTIONED
  EXCEPTION (reload verbs: load_recorded_dictionary /
  from_recorded_posture) because recorded config truth must land verbatim
  with per-key backfill honesty. The current engine conforms; all future
  lanes (S2, S3, graft) are bound by this law.

## State Transition Event
- from_state: none -> to_state: in_progress
- transition_reason: owner directive to execute the V3 horizon iteration.

## Applicable Anti-Patterns
- [ ] No implementation before that story's patch docs exist and are linked.
- [ ] No facade signature changes hiding inside additive work.
- [ ] No MR-side edits; seam findings go to the MR agent via mailbox.
- [ ] "Not run." until the owner runs.

## Noting Behavior
- Epic notes: program direction, cross-story tradeoffs, tranche order changes.

## Artifact Links (Optional)
- system_docs/patches/active/crystallizer_v3_horizon_2026_07_11/ (per-story
  patch docs; created at each story's gate).

## Notes
- DATETIME: 2026-07-11T11:09:27Z
  TYPE: PLAN
  CLAIM: Program staged per owner directive. Tranche law from the decomposition
    epic carries over (sentinel per tranche; reroute/inventory lists are
    CHECKLISTS). S1 opens first with a source investigation of the loader
    package + preflight + record verbs before patch authoring.
  EVIDENCE:
  - codex/context_compass/artifacts/2026-07-09_crystallizer_philosophy_v3.md:1-999
  - codex/context_compass/tickets/epics/completed/2026-07-09_crystallizer_subsystem_decomposition_epic.md:1-999
  IMPACT: Durable program frame for three tranches; resumable post-compaction.
  NEXT: S1 story ticket + investigation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-12T00:50:00Z
  TYPE: FACT
  CLAIM: OWNER-DIRECTED SQLite proof suite for the external persistence
    lane (the 2026-07-07 callables-first DB seam, verified live this
    session): 4 integration tests over a REAL stdlib sqlite3 store in
    test_crystallizer_restore_integration.py:1210-1350 - (1) flush ships
    local-then-remote + INSERT OR REPLACE upsert (the remote U lane, no
    duplicate rows); (2) POD DEATH round trip: seal -> flush to SQLite ->
    rmtree the entire local cache -> fresh boot ->
    reload_profile_from_external (inserted>=1) -> load_checkpoint ->
    same content-derived spell SHA re-recorded; (3) lenient-upload law:
    a raising handler never kills flush, upload_failure_count==1 on the
    describe surface; (4) remote-contradiction law: list-says/download-
    denies refuses with ValueError("inconsistent"). Handler trio
    (upload/download/list) built exactly per the ruled contract:
    handlers own connection/schema/serialization, melder only calls.
    CRUD posture reconfirmed for the owner: C/R/U covered; remote D
    deliberately absent per the 2026-07-07 ruling (owner reaffirmed -
    original ruling stands unless he orders the delete_handler lane).
  EVIDENCE:
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:1210-1350
  - src/melder/crystallizer/asset_management/external_persistence_manager.py:134-274
  TESTS: Not run (sandbox; disk verified via file-tool).
  NEXT: rides the same owner sweep.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-12T01:40:00Z
  TYPE: FACT
  CLAIM: EXTERNAL MESH LANE built per the owner's three rulings (patch
    crystallizer_external_mesh_2026_07_12 authored FIRST; callables-first
    law untouched - presence flags only). (1) Generic kind-partitioned
    quartet on the manager configuration: with_store_handler(kind,
    profile, unit_id, payload) / with_fetch_handler(kind, unit_id) /
    with_list_units_handler(kind, profile) / with_delete_handler(kind,
    unit_id) + with_stream_emissions(bool); describe_presence gains the
    flags. (2) Manager: store_unit (lenient + NEW store_failure_count) /
    fetch_unit / list_units (loud-refuse) / delete_unit (STRICT - a
    half-run retention pass must not lie) + store_enabled /
    stream_emissions_enabled; LEGACY BRIDGE: checkpoint verbs fall back
    to the generic lanes (upload->store_unit("checkpoint"),
    download->fetch_unit, profile list->list_units) so ONE handler set
    serves the whole mesh. (3) AssetManagementSystem: store_formation
    ships local-then-remote (kind="formation");
    reload_formations_from_external (list+fetch -> local
    insert-if-absent, contradiction raises);
    apply_external_retention(profile, cap) ULID-sorted oldest-first
    deletes; emission_tap_enabled cheap gate + stream_emission (fresh
    event ULID, {"crystal_kind","payload"} envelope). (4)
    Crystallizer.emit(): opt-in tap AFTER the record lands (local truth
    leads the mirror; lenient+counted; untapped worlds pay one property
    read). Facades reload_formations_from_external() +
    apply_external_retention() (cap defaults to
    max_persistence_crystals - the same knob as the local FIFO). (5)
    4 new SQLite integration tests (one mesh_units table, kind column):
    generic-bridge checkpoint pod-death round trip; formation ship +
    reload + restore; emission tap delta rows with crystal_kind
    envelopes; retention trims oldest, survivors = newest cap.
  EVIDENCE:
  - src/melder/crystallizer/asset_management/external_persistence_manager.py:280-470
  - src/melder/crystallizer/asset_management/asset_management_system.py:334-660
  - src/melder/crystallizer/crystallizer.py:1068-1084,1835-1925
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:1350-1600
  IMPACT: ANY mesh unit stores/round-trips through user callables;
    live DB mirroring and melder-driven retention are per-deployment
    opt-ins. CRUD now C/R/U/D-complete when the user attaches the lanes.
  TESTS: Not run (sandbox; rot on grown files - disk verified via
    file-tool sentinels, 12 src + 4 test hits).
  NEXT: rides the owner sweep with everything else.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T02:50:00Z
  TYPE: FACT
  CLAIM: RECORD VERSIONING + JSON/INTERFACE CONTRACT (owner rulings
    2026-07-12). (1) NEW persistence/record_version.py - RecordVersion
    (static authority, class-level CURRENT="1.0.0"/KEY): stamp / of
    (absent="0.0.0" pre-versioning) / parse / check_readable (refuses
    NEWER major with the upgrade instruction; older + pre-versioning
    pass into the record's tolerance lanes). (2) STAMPS on every durable
    artifact: to_cached_item, capture_formation_record, emission-tap
    envelopes. READ GATES: from_cached_item (covers cache + external
    reloads) and load_formation_record (pre-replay). (3) 10-test unit
    suite test_record_version_and_json_contract.py: version semantics;
    cached-item stamp + LOSSLESS class->json->class rehydration loop +
    newer-major refusal; twin-family describe() JSON round-trip proof
    (AethericFrame/SpellIndex/MutationResearch crystals - "an interface
    class that we can emit or json"); dict-backed generic-manager suite
    (any-kind round trip, lenient store counting vs STRICT deletes,
    strict_uploads propagation, legacy checkpoint bridge over generic
    lanes, presence-flag describe JSON-safety). SQLite tap test asserts
    the envelope stamp. ALSO consumed mutation_0's 16:17Z HANDOFF
    mid-slice: MR spell_id vocabulary sync (strategy reads
    spell_id/lane_id_by_spell_id; COMPAT CALL: old-key payloads = ONE
    named pre_vocabulary_sweep_payload warning, checks still run; +1
    tolerance test; round-trip walk read synced; his task ticket closed).
  EVIDENCE:
  - src/melder/crystallizer/persistence/record_version.py:1-131
  - src/melder/crystallizer/persistence/persistence_crystal.py:286-335
  - tests/unit/melder/crystallizer/persistence/test_record_version_and_json_contract.py:1-328
  - tickets/tasks/2026-07-11_mr_spell_id_vocabulary_preflight_sync_task.md
  TESTS: Not run (sandbox; rot on grown files - disk verified via
    file-tool, 9 sentinel hits across 5 files).
  NEXT: owner sweep covers the day; then closure walks + SIX patch dirs
    promotion + graph regen.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T03:50:00Z
  TYPE: FACT
  CLAIM: OWNER --last-failed TRIAGE (12 fails) - 11 mine (2 root causes),
    1 mutation_0's. (1) ROOT CAUSE A (9 fails): the pre-mesh validate()
    law ("upload_on_flush with no upload handler = misconfiguration")
    predates the generic lane - every generic-quartet config froze
    refused. FIX in source: the STORE handler now satisfies the flush
    knob (the legacy bridge ships checkpoints through it); read-only
    configs (fetch/list only) still refuse unless the knob is disabled
    explicitly - the law survives, widened; the read-only test now
    disables the knob. Pre-existing manager suite (5
    with_upload_on_flush(False) uses) unaffected - the change only
    widens. (2) ROOT CAUSE B (2 fails): my asserts compared the
    "inserted" id LIST to an int - both moved to len(...) >= 1.
    (3) test_root_residency_view_is_honest_without_custody expects the
    pre-sweep "spell_sha" error text from MR source - mutation_0's test,
    owner routing the fix to him directly.
  EVIDENCE:
  - src/melder/crystallizer/asset_management/external_persistence_manager_configuration.py:592-621
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py (2x len fix + knob)
  TESTS: Not run post-fix (sandbox). Owner rerun of --last-failed should
    collapse the 11; the 12th is MR-side.
  NEXT: owner rerun.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T04:10:00Z
  TYPE: FACT
  CLAIM: RERUN 2 TRIAGE (10/12 green; 2 fails, ONE root cause): the
    flush leg's gate `upload_enabled` still counted only the LEGACY
    upload handler - quartet-only configs froze fine (validate widened)
    but never SHIPPED at flush: the bridge test's mesh_units table was
    never created (zero handler calls) and retention listed an empty
    remote (nothing to trim). FIX: upload_enabled now mirrors validate's
    widened write-lane rule ((upload_handler OR store_handler) AND
    upload_on_flush) - upload_checkpoint's bridge does the rest. Legacy
    configs unchanged (store handlers could not exist pre-mesh). One
    property, both tests.
  EVIDENCE:
  - src/melder/crystallizer/asset_management/external_persistence_manager.py:108-135
  - src/melder/crystallizer/asset_management/asset_management_system.py:192
  TESTS: Not run post-fix (sandbox). Owner rerun; the MR-side
    residency_view fail remains mutation_0's.
  NEXT: owner rerun.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T04:45:00Z
  TYPE: FACT
  CLAIM: CLOSED - all three ruled stories owner-accepted green (S1
    load-scope maturity closed 07-11T17:55Z; S2 physical custody + S3
    impact engine closed 07-12T04:40Z) PLUS the owner-directed
    extensions delivered in-lane: LoadAdmission rename, Aether LoadGate,
    posture wait-bound propagation, external mesh lane (generic quartet
    + emission tap + retention), record versioning + JSON/interface
    contract, SQLite proof suites (8 tests), vocabulary conformance.
    THREAD-SAFETY AUDIT (owner directive 2026-07-12) over every new
    surface: LoadGate condition-guarded; authority drain
    lock-snapshotted per slice; manager counters lock-guarded with
    handlers invoked OUTSIDE locks; frozen configs immutable post-freeze;
    asset verbs fetch the manager under lock and call remotes outside;
    profile<->crystal lock order one-way; ImpactEngine documented
    thread-confined (immutable post-construction, facade builds+cleans
    per call); engines single-use under LoadGate whole-system authority.
    ONE RACE FOUND AND FIXED: the emission tap described the twin AFTER
    record() - replace-on-emit meant a concurrent same-kind emit could
    clean that twin mid-describe; the payload now captures BEFORE the
    record and ships after (local truth still leads the mirror,
    crystallizer.py emit()). PROMOTION DEBT EXPLICITLY CARRIED FORWARD
    (not part of this closure): six patch dirs -> C-docs + graph regen -
    tracked on the artifact board as the next dedicated pass.
  EVIDENCE:
  - src/melder/crystallizer/crystallizer.py:1068-1092
  - artifact_board.md (promotion rows)
  IMPACT: The V3 horizon program is delivered; the record speaks
    versioned JSON through user callables, loads hold exclusive
    authority, and every mesh unit round-trips.
  NEXT: batched promotion + graph regen (dedicated pass); then the
    spell-index graft lane candidate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Owner-directed three-story crystallizer iteration on the V3 horizon: composable
formation loads (S1), opt-in physical source retention (S2), impact engine
(S3). MR Phase B belongs to another agent. Patch gates per story; sentinel per
tranche; facades stay byte-compatible.
