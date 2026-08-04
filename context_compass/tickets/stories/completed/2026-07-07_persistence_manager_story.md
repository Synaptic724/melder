# Story: PersistenceManager (DB upload/download seam via user callables)

## Metadata
- Story ID: STORY-2026-07-07-persistence-manager
- Parent Epic: EPIC-2026-07-03-crystallizer-bootstrap-checkpoint
- Status: closed
- Owner: cowork
- Agent Name: melder_0
- Priority: p2
- Created: 2026-07-07T18:40:00Z
- Updated: 2026-07-07T18:40:00Z

## Problem / Opportunity
Owner ruling: the local cache caps at the checkpoint limit; durability
beyond it is the user's DB opt-in. That opt-in needs its seam: a
`persistence_manager` module inline with persistence_system whose object
OWNS uploading and downloading of cached checkpoint items, configured by
USER-ATTACHED CALLABLES in a SEPARATE configuration at the crystallizer
configuration step (the user must attach their own DB calls until a
first-party adapter lane exists).

## Owner Decision (this ticket's charter)
- New class PersistenceManager, module
  src/melder/crystallizer/persistence/persistence_manager.py (inline
  with persistence_system; OWNED by PersistenceSystem - it owns all
  caches/transports).
- Separate configuration: PersistenceManagerConfiguration - callables
  loaded at the crystallizer configuration step.
- AGENT TAKE ADOPTED PENDING OWNER VETO: callables-first; NO SQLAlchemy
  dependency in core (3.14t nogil risk on drivers/C-extensions; schema/
  migration/dialect ownership is beyond MRP; a first-party adapter
  package can PROVIDE the callables later - seam now, product later).
  Keyring only solves credentials, not the ownership surface.

## Design
- PersistenceManagerConfiguration (Cleanable, fluent + freeze):
  - with_upload_handler(callable(profile_name, checkpoint_id,
    cached_item) -> None)
  - with_download_handler(callable(checkpoint_id) -> Optional[dict])
  - with_list_handler(callable(profile_name) -> List[str])
  - with_upload_on_flush(bool, default True) - flush path also uploads.
  - with_strict_uploads(bool, default False) - False: upload failures
    LOG and continue (the local seal/cache lane must never die on a
    remote); True: raise.
  - validate(): handlers callable-or-None; freeze() seals; RECORD LAW:
    callables record as presence flags only (logger-resolver precedent);
    reload lane reports code_participation.
- PersistenceManager (Cleanable):
  - Constructed from a FROZEN configuration; owned by PersistenceSystem
    (slot _persistence_manager, Optional).
  - upload_checkpoint(profile_name, checkpoint_id, cached_item):
    handler-gated NO-OP when no upload handler; strictness per config.
  - download_checkpoint(checkpoint_id) -> Optional[dict].
  - download_profile(profile_name) -> List[dict] (list handler + per-id
    download; missing handlers -> expressive RuntimeError).
  - Handlers execute OUTSIDE PersistenceSystem's lock (user code must
    never run under the record lock); document threading contract.
- Wiring:
  - Crystallizer.configure_persistence_manager(pm_configuration) BEFORE
    activate (the crystallizer configuration step per owner); activate
    constructs the manager into the PersistenceSystem.
  - flush_checkpoint_to_cache: after cache store + retention, upload
    each flushed item when upload_on_flush.
  - NEW PersistenceSystem.reload_profile_from_manager(profile_name):
    download_profile -> from_cached_item insert-if-absent (mirrors
    reload_profile_from_cache); facade on Crystallizer.
- Tests: unit (config validate/freeze/presence-flags; manager no-op
  gates; strict vs lenient upload failure; download insert lane with
  stub callables) + integration (flush uploads via recording stub dict;
  fresh system reload_profile_from_manager -> verify chain intact).

## Acceptance Criteria
- Flush uploads through the attached callable (when enabled) without
  ever breaking the local seal/cache lane in lenient mode.
- A fresh system rebuilds a profile purely from manager downloads.
- No new third-party dependency.
- Callables never enter the record; presence flags only.

## Notes

- DATETIME: 2026-07-07T18:40:00Z
  TYPE: PLAN
  CLAIM: Lane opened on owner directive ("do all those" + PM spec +
    take requested). Also queued this burst-series per owner: patch-doc
    promotion into C-docs (+ tail repairs), graph regen, loader-chain M3,
    public-accessor follow-ups. Implementation order: PM config -> PM ->
    system wiring -> facades -> tests -> then patch promotion lane.
  EVIDENCE:
  - owner message 2026-07-07 (PM spec + SQLAlchemy question)
  IMPACT: The DB opt-in becomes real without dependency pressure.
  NEXT: Implement PersistenceManagerConfiguration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T19:40:00Z
  TYPE: FACT
  CLAIM: LANE LANDED with two owner corrections absorbed mid-build:
    (1) NAME/RANK: class is ExternalPersistenceManager (module
    external_persistence_manager.py inline with persistence_system.py);
    it goes INTO the Crystallizer at the same ownership rank as
    PersistenceSystem (crystallizer -> persistence_system |
    external_persistence_manager); the interim PersistenceSystem
    ownership wiring was REVERTED. (2) SQLAlchemy question settled:
    callables-first adopted ("we'll sidestep it... user will always need
    a sqlbootstrap and to manage their own secrets thats on them").
    LANDED: ExternalPersistenceManagerConfiguration (fluent handler
    loaders upload/download/list + upload_on_flush/strict_uploads knobs;
    validate refuses upload_on_flush-without-handler; freeze seals;
    describe_presence = flags only per record law).
    ExternalPersistenceManager (upload gate NO-OP without handler;
    lenient-default failure posture with upload_failure_count
    diagnostics, strict re-raises - the documented best-effort
    broad-except; download_checkpoint/download_profile with loud
    missing-handler + remote-inconsistency refusals; describe =
    presence + diagnostics). SYSTEM support verbs: cached_item_form +
    insert_cached_items (generic insert-if-absent import sink).
    CRYSTALLIZER facades (owner: "facade all the important things"):
    configure_external_persistence_manager (freezes-if-needed, replaces
    + cleans previous), describe_external_persistence_manager,
    reload_profile_from_external (manager download -> system insert),
    _upload_flushed_checkpoints hooked into BOTH flush paths (manual
    facade + auto cadence ticker; manual flush_checkpoint now returns
    the flushed ids it always documented). Cleanup order: manager first,
    then system. 4 unit tests (config contract/presence-only, upload
    gates + both failure postures, download refusals + inconsistency,
    full remote round trip rebuilding a fresh ledger via dict-backed
    handlers). Compile: manager/system/crystallizer/tests clean
    in-sandbox; configuration file Not run (replica rot; disk verified).
    Execution: Not run.
  EVIDENCE:
  - src/melder/crystallizer/persistence/external_persistence_manager_configuration.py
  - src/melder/crystallizer/persistence/external_persistence_manager.py
  - src/melder/crystallizer/persistence/persistence_system.py
    (cached_item_form / insert_cached_items)
  - src/melder/crystallizer/crystallizer.py (slot/cleanup/facades/hooks)
  - tests/unit/melder/crystallizer/persistence/test_external_persistence_manager.py
  IMPACT: Flush now ships local-then-remote; a fresh process rebuilds a
    profile purely from the user's DB callables; zero new dependencies.
  NEXT: Owner sweep; then the queued lanes (patch-doc promotion into
    C-docs + tail repairs, graph regen, loader-chain M3).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T20:00:00Z
  TYPE: PLAN
  CLAIM: OWNER EXTENSION - fluent POD BOOTSTRAP API (kube scenario): a
    restarted pod always needs to (1) set up the crystallizer +
    persistence system, (2) attach their external manager, (3) pull
    history (local cache, then their DB), storing downloaded items
    locally "if it needs to be done", (4) pick the MOST RECENT
    checkpoint, (5) load it -> whole system bootstraps. DESIGN: new
    CrystallizerBootstrap(Cleanable), single-use fluent builder at
    src/melder/crystallizer/crystallizer_bootstrap.py (builder-module
    precedent: crystallizer_configuration_builder):
    .with_crystallizer_configuration(cfg) [default: with_defaults()]
    .with_external_persistence_manager(pm_cfg) [optional]
    .with_profile(name) [default "default"]
    .with_pull_remote(bool) [default True when a manager is attached]
    .bootstrap() -> report dict {activated, cache_reload{inserted,...}|
    None, remote_reload{...}|None, restored_checkpoint_id|None,
    restore_report|None, chain_report}. Semantics: composes ONLY
    Crystallizer facades; cache reload tolerates empty (fresh-ever pod
    boots an empty world legally - restored=None, no error); remote-
    inserted ids re-flush through the facade so the local cache holds
    them (documented consequence: the upload hook re-upserts them -
    user handlers must be upsert-safe); chain verify gates the load
    (broken -> expressive RuntimeError; truncated rides the report);
    newest = last ULID among the profile's ledger ids.
  EVIDENCE:
  - owner message 2026-07-07 (kube bootstrap flow)
  IMPACT: One fluent call chain = pod restart to rebuilt world.
  NEXT: Implement + tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-07T20:30:00Z
  TYPE: FACT
  CLAIM: POD BOOTSTRAP LANDED. NEW
    src/melder/crystallizer/crystallizer_bootstrap.py -
    CrystallizerBootstrap(Cleanable), single-use fluent builder
    composing ONLY Crystallizer facades: with_crystallizer_configuration
    (defaults-lane when omitted; docstring routes recorded-policy boots
    through load_recorded_dictionary) / with_external_persistence_manager
    / with_profile / with_pull_remote -> bootstrap() runs the owner
    order: activate -> attach manager -> local cache reload (empty
    TOLERATED: fresh-ever pods legally boot empty worlds) -> remote pull
    + re-flush pulled ids into the local cache (documented upsert-safe
    handler expectation) -> chain verify GATES the load (broken refuses
    with an expressive RuntimeError) -> load_checkpoint on the newest
    profile ULID -> full report dict. Unconsumed configurations clean
    with the builder; consumed ones pass ownership downstream.
    INTEGRATION TEST landed
    (test_pod_bootstrap_rebuilds_the_world_from_the_remote): pod 1
    records/flushes/uploads to a dict remote; pod death = singleton
    reset + rmtree'd local cache; pod 2 = ONE fluent chain -> world
    rebuilt (remote pull, newest picked, restore complete, same spell
    SHA re-emitted, local cache re-populated). Compile: bootstrap +
    integration file clean in-sandbox. Execution: Not run.
  EVIDENCE:
  - src/melder/crystallizer/crystallizer_bootstrap.py
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py
    (tail test)
  IMPACT: The kube story is one fluent chain: pod restart -> attach DB
    callables -> whole system bootstraps.
  NEXT: Owner sweep; then patch-doc promotion / graph regen /
    loader-chain M3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T21:10:00Z
  TYPE: FACT
  CLAIM: CLOSED - acceptance walk on owner confirmation ("ok cool this
    works"). Criteria: (1) flush uploads through user callables without
    breaking the local lane (lenient posture + failure diagnostics) -
    PROVEN (unit postures test + integration upload assertion);
    (2) a fresh system rebuilds a profile purely from manager downloads -
    PROVEN (unit remote round trip + pod-death integration test);
    (3) no new third-party dependency - HELD (callables-first, owner
    settled: user owns SQL bootstrap + secrets); (4) callables never
    enter the record - HELD (presence-flags law, asserted in unit).
    PLUS the fluent pod-boot lane (CrystallizerBootstrap) proven by the
    full pod-death round trip. Facade-complete per owner ruling
    (configure/describe/reload_from_external + upload hooks on both
    flush paths).
  EVIDENCE:
  - owner confirmation 2026-07-07 + green sweeps
  IMPACT: The DB opt-in and the kube restart story are both real, owner-
    proven, dependency-free.
  NEXT: none (closed). Follow-up lanes queued: patch-doc promotion,
    graph regen, loader-chain M3, first-party adapter package (provides
    callables; future).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
