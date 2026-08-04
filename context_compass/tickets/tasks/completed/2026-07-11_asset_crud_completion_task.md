- Completed: 2026-07-12T21:00:00Z
- Summary: All five deltas delivered (MeshInterfaceContract self-describing
  table, cache deletes, system verbs incl. graft lanes +
  describe_external_interface, facades, mesh-aware bootstrap) + 21-test
  suite; three owner-run triages resolved in-lane plus the same-ms ULID
  retention re-order (checkpoint_number-ordered eviction + 2 regression
  rows). Closed on owner directive ("turn in all"); pytest Not run by
  agent - reopen on red. C-doc/graph promotion carried as debt.

# Task: asset-management CRUD completion + self-describing mesh interface

## Metadata
- Task ID: TASK-2026-07-11-asset-crud-completion
- Parent: successor of the closed external-mesh lane (horizon epic) +
  the CRUD audit answered for the owner 2026-07-11
- Status: in_progress
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-11T19:45:00Z
- Updated: 2026-07-11T19:45:00Z

## Problem / Opportunity
The mesh audit (owner Q&A, source-verified) found the external quartet
complete but three asymmetries: no melder-driven formation delete
anywhere, no single-item cache evict, and graft records ride no
first-class kind. Owner directive additionally wants the interface
layer SELF-DESCRIBING: "emit the table as well the shape ... form the
calls so the user can register these directly and then we can emit
them or just emit and retrieve the json from calls."

## Ticket Contract
- ENTRY_GATE: patch asset_crud_completion_2026_07_11 exists + linked.
- EXECUTION_BOUNDARY: asset_management/ package + Crystallizer facades
  + unit tests; nothing in persistence/ or the loader changes behavior.
- DEPENDENCIES: RecordVersion (stamping), generic mesh quartet (lanes).
- EXIT_GATE: all four deltas landed + tests authored; owner-run 3.14t.
- FAILURE_ESCALATION: BLOCKER note + stop if any existing verb's
  behavior would have to change (additive-only law).

## Acceptance Criteria
- MeshInterfaceContract.describe() emits the full kind/shape/signature
  table as one RecordVersion-stamped dict (the user can build storage
  from it without reading melder source).
- Formation delete works local-only and local+remote (strict remote).
- One cached checkpoint can be evicted by id.
- A graft record round-trips store->fetch (version-gated) ->list over
  the generic lanes without the user naming the kind.
- describe_external_interface facade joins contract + live presence.

## Applicable Anti-Patterns
- No module-level constants (class-level only); no behavior change to
  existing verbs; no SQL generation; docstring/comment preservation.

## Artifact Links
- system_docs/patches/active/asset_crud_completion_2026_07_11/architecture_patch.md

## Noting Behavior
- Task: tactical findings, immediate impacts, one-step continuation.

## Notes
- DATETIME: 2026-07-11T19:45:00Z
  TYPE: PLAN
  CLAIM: Land order per patch: (1) mesh_interface_contract.py (pure,
    new file); (2) cache delete verbs; (3) system verbs (formation
    delete w/ optional strict remote leg, graft kind lanes,
    describe_external_interface); (4) facades; (5) unit tests
    (dict-backed handlers, mirroring test_record_version_and_json
    contract patterns). Payload-shape inventory sources: cached_item
    form (persistence_system.cached_item_form), formation record
    (capture_formation_record), graft record (capture_index_graft),
    tap envelope (stream_emission).
  EVIDENCE:
  - src/melder/crystallizer/asset_management/asset_management_system.py:136-680
  - src/melder/crystallizer/asset_management/crystallizer_cache.py:83-381
  - src/melder/crystallizer/asset_management/external_persistence_manager.py:335-483
  IMPACT: closes the CRUD symmetry question the owner raised; the mesh
    becomes registration-ready from its own emitted contract.
  NEXT: write mesh_interface_contract.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T19:55:00Z
  TYPE: FACT
  CLAIM: DELTA 1 LANDED - asset_management/mesh_interface_contract.py
    (184 lines, ast-parse clean): MeshInterfaceContract static
    authority. Four UNIT_KIND_* class constants (checkpoint/formation/
    index_graft/emission - the first three kind strings source-verified
    against live store_unit/list_units call sites at
    asset_management_system.py:348/:577/:653/:722), IDENTITY_COLUMNS
    (kind/profile_name/unit_id/payload), HANDLER_SIGNATURES (the four
    lanes + stream knob, each with its registration fluent name), and
    PAYLOAD_SHAPES mirroring the REAL producers key-for-key
    (to_cached_item persistence_crystal.py:291-302,
    capture_formation_record persistence_system.py:749-760,
    capture_index_graft record, stream_emission envelope
    asset_management_system.py:725-728). describe() emits the whole
    table RecordVersion-stamped with detached copies.
  EVIDENCE:
  - src/melder/crystallizer/asset_management/mesh_interface_contract.py:1-184
  - src/melder/crystallizer/persistence/persistence_crystal.py:291-302
  - src/melder/crystallizer/persistence/persistence_system.py:749-760
  - src/melder/crystallizer/asset_management/asset_management_system.py:721-729
  IMPACT: the owner's "emit the table + shape / form the calls" verb
    exists; deltas 2-4 consume its kind constants.
  NEXT: delta 2 - CrystallizerCache.delete_cached_item(id) +
    delete_formation(profile, name) (atomic unlink, teach-grade
    KeyError on miss; insertion points after load_cached_item :186 and
    load_formation :316); then delta 3 system verbs (formation delete
    w/ optional strict remote leg via delete_unit("formation", name),
    graft store/fetch/list on the generic lanes w/ check_readable at
    fetch, describe_external_interface = contract describe +
    manager.describe presence join); then delta 4 facades; then the
    unit suite (dict-backed handlers per the JSON-contract test
    precedent). Tests: Not run (sandbox; ast floor only).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T20:05:00Z
  TYPE: FACT
  CLAIM: DELTA 2 LANDED - CrystallizerCache gains delete_cached_item
    (:223 region, mirrors load_cached_item's profile-glob + legacy-path
    resolution exactly, unlink + teach-grade KeyError miss, returns the
    deleted path) and delete_formation (:401 region, exact
    store/load path form, local-only by contract - the remote leg is
    delta 3's). File now 508 lines; insertion regions + tail verified
    whole via file-tool Read. AST: Not run for this file - the bash
    replica ROTTED mid-verify (reads the pre-edit length, cutting
    inside load_formation's raise at :393; two attempts, same stale
    cut; disk verified intact via file-tool :385-:398 + :452-:508).
    mesh_interface_contract.py passed ast BEFORE the rot set in.
  EVIDENCE:
  - src/melder/crystallizer/asset_management/crystallizer_cache.py:223-268
  - src/melder/crystallizer/asset_management/crystallizer_cache.py:401-450
  IMPACT: local cache CRUD is now symmetric for both kinds; delta 3
    builds the system verbs on top.
  NEXT: delta 3 in asset_management_system.py -
    delete_cached_checkpoint(id) (cache passthrough),
    delete_formation(profile, name, include_remote=False) (cache delete
    + optional STRICT delete_unit("formation", name) leg),
    store_index_graft/fetch_index_graft/list_index_grafts (generic
    lanes, kind=MeshInterfaceContract.UNIT_KIND_INDEX_GRAFT,
    check_readable at fetch), describe_external_interface()
    (MeshInterfaceContract.describe() + manager presence join); then
    delta 4 Crystallizer facades; then the unit suite (dict-backed
    handlers). Re-verify replica freshness before any bash parse.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T20:15:00Z
  TYPE: FACT
  CLAIM: TESTS AUTHORED for deltas 1+2 - NEW tests/unit/melder/
    crystallizer/asset_management/test_asset_crud_completion.py (158
    lines, ast OK, 8 tests): contract describe stamped + complete
    (kinds order, identity columns, one shape row per kind), shape rows
    mirror the real producers (checkpoint/formation/emission key
    spot-checks + record_version first everywhere), handler signatures
    carry registration fluents + arg order, describe() detachment
    (mutation never leaks), cache delete hit (neighbour survives, both
    kinds) + teach-grade KeyError miss (both kinds, non-destructive).
    Harness mirrors test_crystallizer_cache.py's cache_root monkeypatch
    fixture exactly. crystallizer_cache.py bash-replica rot PERSISTS
    (same :393 stale cut across three attempts; disk whole via
    file-tool) - its parse verdict rides the owner run. INCIDENT in the
    20:05Z note edit: it consumed this ticket's "## Context / Handoff
    Summary" header - restored below in this same pass.
  EVIDENCE:
  - tests/unit/melder/crystallizer/asset_management/test_asset_crud_completion.py:1-158
  IMPACT: deltas 1+2 are test-covered before delta 3 builds on them.
  NEXT: delta 3 (system verbs; instructions in the 20:05Z note), then
    delta 4 facades, then extend this suite (formation remote-leg
    strict delete, graft round trip over dict handlers,
    describe_external_interface presence join).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T20:30:00Z
  TYPE: FACT
  CLAIM: DELTAS 3+4 LANDED. System verbs (asset_management_system.py,
    inserted between apply_external_retention and the tap property +
    MeshInterfaceContract import added): delete_cached_checkpoint
    (cache passthrough), delete_formation (local always; remote leg
    opt-in STRICT via delete_unit("formation")), store_index_graft
    (kind=UNIT_KIND_INDEX_GRAFT keyed by the record's own index_id;
    ValueError without one; requires store_enabled), fetch_index_graft
    (loud-refuse lanes, teach-grade KeyError miss,
    RecordVersion.check_readable gate), list_index_grafts,
    describe_external_interface (contract + live_manager presence
    join). Facades (crystallizer.py:2008-2183, activation-gated,
    active-profile defaulting mirrors apply_external_retention):
    delete_cached_checkpoint / delete_formation /
    store_index_graft_external / fetch_index_graft_external /
    list_index_grafts_external / describe_external_interface.
    AST: Not run for both edited files (bash replica rot persists -
    system file cut mid-docstring at stale :505; disk verified whole
    via file-tool: all six system verbs at :670-:911 seaming cleanly
    into the tap property :913, all six facades grep-hit
    :2008-:2160).
  EVIDENCE:
  - src/melder/crystallizer/asset_management/asset_management_system.py:663-911
  - src/melder/crystallizer/crystallizer.py:2008-2183
  IMPACT: CRUD symmetric across cache + external for every kind; the
    interface layer is fully self-describing at the facade.
  NEXT: extend the test suite (system verbs over dict-backed handlers:
    formation remote-leg strict + refusal, graft store/fetch/list round
    trip + version-gate refusal + index_id ValueError,
    describe_external_interface live_manager join both states); then
    closure walk + C-doc/graph promotion of this lane; owner runs 3.14t.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T20:40:00Z
  TYPE: FACT
  CLAIM: TEST EXTENSION LANDED - the suite grows 8 -> 15 tests
    (338 lines, file-tool verified; the bash replica still serves the
    stale 158-line pre-extension copy, so the extension's parse verdict
    rides the owner run). New coverage over a dict-backed mesh +
    AssetManagementSystem(PersistenceSystem()) fixture (the
    _dict_backed_configuration helper mirrors the JSON-contract test's
    quartet pattern): graft store/fetch/list round trip (kind +
    index_id keying + payload equality through the gate), missing
    index_id ValueError (nothing ships), newer-MAJOR fetch refusal
    (reader gate law), fetch-miss KeyError, delete_formation local-only
    vs STRICT remote leg (remote_deleted flag + row gone), cache
    checkpoint evict passthrough, describe_external_interface
    live_manager join (manager attached vs bare None).
  EVIDENCE:
  - tests/unit/melder/crystallizer/asset_management/test_asset_crud_completion.py:161-338
  IMPACT: all four deltas are test-covered; the lane's build phase is
    COMPLETE.
  NEXT: owner-run 3.14t -> triage or closure walk; then promote the
    patch dir into the C-docs (three-lane-tail sibling section) + graph
    (MeshInterfaceContract node; NOTE: mutation_0 has since regenerated
    to 530/992 - re-verify counts before editing).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T20:50:00Z
  TYPE: FACT
  CLAIM: SECOND TEST EXTENSION - suite now 20 tests / 431 lines
    (file-tool verified count + tail; replica still stale). Five new
    error-path/partition contracts: formation remote-leg refusal
    without a manager (AND documents the ordering truth: the local
    delete runs BEFORE the refusal), strict remote propagation via a
    PUBLIC-surface broken-delete configuration (first draft poked
    manager._delete_handler - caught + reworked to the registration
    fluents before landing), graft store refusal naming
    with_store_handler, list_index_grafts profile partition (the
    profile_name identity column is real), and legacy flat-layout
    cache evict (the pre-layout tolerance branch).
  EVIDENCE:
  - tests/unit/melder/crystallizer/asset_management/test_asset_crud_completion.py:341-431
  IMPACT: every refusal lane and both cache layouts are covered; test
    density for the new surface is well above the 10/100 floor.
  NEXT: owner-run 3.14t -> triage or closure walk + promotion
    (re-verify graph counts vs mutation_0's 530/992 first). One
    OPTIONAL polish row: facade-rank gating tests (unactivated
    Crystallizer refusal) - the existing facade suites already prove
    that gate pattern, so only add on owner request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-12T15:10:00Z
  TYPE: FACT
  CLAIM: MAILBOX NOTICE consumed (mutation_0, 2026-07-12T02:30:00Z,
    owner-ruled additive shape change): MutationResearchCrystal
    .describe() now carries TWO new keys beside composition_payload -
    "research_nodes" and "grouped_research_nodes" (flat value-typed
    DB-storable rows derived from the composition at construction;
    JSON round-trip asserted in his tests; hydration still reads the
    composition). ACTION FOR THIS LANE + the SQLite adapter epic: IF
    MeshInterfaceContract's PAYLOAD_SHAPES enumerates per-kind payload
    keys for the mutation_research twin kind, that row needs the two
    additions when the lane resumes; verify against the live
    describe() before editing (payload-shapes mirror real producers).
  EVIDENCE:
  - src/melder/crystallizer/crystals/mutation_research_crystal.py
  IMPACT: keeps the self-describing table truthful against mutation_0's
    shipped twin change; nothing breaks today (additive keys), but the
    contract table must not lag once promoted.
  NEXT: on lane resume (post owner-run green), re-verify
    MeshInterfaceContract's mutation_research row vs live describe()
    and add the two keys if enumerated.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-12T19:00:00Z
  TYPE: FACT
  CLAIM: OWNER-RUN FLAKE FIXED (cache retention same-ms ULID tie):
    test_cache_files_follow_the_checkpoint_limit intermittently kept
    the FIRST flushed checkpoint - root cause: enforce_cache_retention
    sorted by ULID filename, but two checkpoints sealed within one
    millisecond share the ULID time component and order by RANDOM
    tails, so name order can invert creation order and evict the newer
    file ("passes alone" = timing crosses the ms boundary). FIX:
    retention now sorts by the recorded checkpoint_number carried in
    each cached payload (monotonic per profile - the record's own
    truth); filename only breaks ties; unreadable payloads sort OLDEST
    and reclaim first (dead cache weight). Docstring truth-synced (the
    "ULID name order = creation order" line was the lie). Cost: k
    small JSON reads per flush over a capped directory - flush-lane
    IO, not hot path. TWO regression rows added: deterministic
    name/number inversion pair (retention must evict by number) +
    unreadable-junk-reclaims-first. NOT test pollution: the per-test
    cache_root already isolates; no cache-off switch needed. AST: Not
    run (replica rot; disk verified via file-tool). pytest: Not run.
  EVIDENCE:
  - src/melder/crystallizer/asset_management/crystallizer_cache.py:139-215
  - tests/unit/melder/crystallizer/persistence/test_kit_export_import.py:123-186
  IMPACT: FIFO retention now evicts true-oldest under same-ms sealing
    in production too, not just in tests.
  NEXT: owner re-run of test_kit_export_import.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T21:00:00Z
  TYPE: FACT
  CLAIM: OWNER-RUN TRIAGE #1 - test_delete_cached_item_removes_only_
    the_target failed TypeError: store_cached_item takes (checkpoint_id,
    cached_item) - the profile rides IN the payload ("profile_name"
    key, default "default"; source-verified crystallizer_cache.py:83-
    131). My three test call sites passed a positional profile arg
    (signature assumed, not read - the exact miss the source-first law
    exists for). FIXED: all three store_cached_item calls now pass
    (id, payload-with-profile_name). Swept the file for other assumed
    signatures: store_formation/load/list verbs were all read-verified
    this session; no other call-shape assumptions remain.
  EVIDENCE:
  - tests/unit/melder/crystallizer/asset_management/test_asset_crud_completion.py:110-117
  - src/melder/crystallizer/asset_management/crystallizer_cache.py:83-131
  IMPACT: the two cache-store-dependent tests (delete target +
    checkpoint passthrough) should now construct their fixtures
    correctly; other 18 tests untouched.
  NEXT: owner re-runs the suite; on green -> closure walk + promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T21:10:00Z
  TYPE: FACT
  CLAIM: OWNER-RUN TRIAGE #2 (full-run fails / rerun passes - owner
    flagged as flaky; investigation splits them). (a) The two
    store_cached_item TypeErrors are NOT flaky tests: the traceback is
    self-contradicting - displayed source passes 2 args (self+2=3,
    the verb's exact arity) while the error says "4 were given" - the
    executed bytecode was the PRE-FIX 3-arg call; pytest re-reads the
    file for display. The full run COLLECTED the module before triage
    #1's fix landed mid-run; fresh collection (the rerun) passes. No
    test change; expect green on the next full run. (b)
    test_fetch_index_graft_gates_newer_major was a REAL double-sided
    bug: RecordVersion.check_readable raises ValueError (reader-gate
    law, record_version.py:125) but my fetch_index_graft docstring
    claimed RuntimeError for the version case and the test asserted
    per that wrong docstring. FIXED all three surfaces: test now
    pytest.raises(ValueError, match="99.0.0") with a comment recording
    the correction; the system verb + facade Raises sections now split
    RuntimeError (cleaned/lane) from ValueError (version gate).
  EVIDENCE:
  - src/melder/crystallizer/persistence/record_version.py:125
  - tests/unit/melder/crystallizer/asset_management/test_asset_crud_completion.py:262-275
  - src/melder/crystallizer/asset_management/asset_management_system.py (fetch Raises)
  - src/melder/crystallizer/crystallizer.py (facade Raises)
  IMPACT: docstrings no longer lie about the version gate's exception
    type; the suite matches the real contract.
  NEXT: owner re-runs the FULL tree (not just --last-failed) so all
    20 collect fresh; on green -> closure walk + promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T21:25:00Z
  TYPE: DECISION
  CLAIM: SCOPE EXPANSION (owner: "implement all the final things") -
    DELTA 5, mesh-aware bootstrap, recorded in the patch doc before
    code: CrystallizerBootstrap.with_formation_reload(bool) fluent
    (:227; default True mirroring with_pull_remote; TypeError non-bool,
    consumed/cleaned guards) + formation-pull step between the remote
    checkpoint pull and chain verify (:372, gated manager-attached AND
    flag; reload_formations_from_external) + report key
    "formation_reload" (:405) + contract docstring order renumbered
    (steps 5-7). Slots/init/cleanup carry _reload_formations
    (children-first del posture). Suite +1 -> 21 tests: fluent contract
    (self-return, TypeError, post-cleanup refusal); the report-key
    behavior rides the pod-death integration lane on the owner run.
    All disk-verified via file-tool grep (:227/:372/:405); AST Not run
    (replica rot standing).
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/bootstrap_loader.py:227-268
  - src/melder/crystallizer/crystal_loader_system/bootstrap_loader.py:365-410
  - tests/unit/melder/crystallizer/asset_management/test_asset_crud_completion.py (tail test)
  IMPACT: the last recorded implementable crystallizer gap is closed -
    a rebuilt pod gets its formation slices back at boot; slice
    restores work immediately.
  NEXT: owner FULL re-run (fresh collection) -> closure walk +
    promotion (C-docs three-lane-tail sibling + graph
    MeshInterfaceContract node; re-verify counts vs 530/992).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T22:20:00Z
  TYPE: FACT
  CLAIM: OWNER-RUN TRIAGE #3 - REAL delta-5 regression, mine:
    test_pod_bootstrap_rebuilds_the_world_from_the_remote failed
    because the formation-reload step gated only on "manager attached"
    and called reload_formations_from_external against a LEGACY-ONLY
    manager (upload/download/list trio, no generic quartet - legal, the
    legacy bridge exists for it), tripping list_units' deliberate
    loud-refusal. FIX: capability gate in bootstrap (facade-only law
    kept - the builder reads its OWN configuration's presence flags:
    list_units_handler AND fetch_handler must both be present, source-
    verified property names at configuration :206/:217); legacy-only
    managers now SKIP the step silently (report key None). The verb's
    loud-refusal contract is untouched (deliberate). Both docstrings
    (fluent contract + step list) corrected to the gated truth. The
    pod-death integration test itself now COVERS the legacy-only skip
    path - no new test needed.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/bootstrap_loader.py (gate + docstrings)
  - src/melder/crystallizer/asset_management/external_persistence_manager_configuration.py:206-227
  IMPACT: legacy-only worlds boot exactly as before delta 5;
    quartet-wired worlds get formations back.
  NEXT: owner re-runs; on green -> closure walk + promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Additive interface-layer completion: self-describing mesh contract +
formation delete + cache evict + first-class graft kind + facades +
mesh-aware bootstrap (delta 5, owner-directed expansion). ALL FIVE
DELTAS LANDED + 21-test suite. Triage #1 (assumed signature), #2
(version-gate exception type + stale collection), #3 (delta-5
legacy-only capability gate) resolved. Remaining: owner FULL re-run ->
closure walk + C-doc/graph promotion (re-verify vs 530/992). Owner
runs tests; agent reports Not run.
