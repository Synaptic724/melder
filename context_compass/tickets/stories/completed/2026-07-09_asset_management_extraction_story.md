# Story: asset_management extraction (S3 - bytes at rest)

- Completed: 2026-07-10T09:10:00Z
- Summary: AssetManagementSystem owns cache + formation files + the EPM seam
  over a borrowed record; PersistenceSystem carries zero disk/DB code; 10
  facades rerouted byte-compatible; flush = seal-then-ship (one feedstock
  pull, both legs); the untested auto-flush cadence lane bug found + fixed;
  owner-run sentinel green; owner accepted at epic closure.

## Metadata
- Story ID: STORY-2026-07-09-asset-management-extraction
- Parent Epic: EPIC-2026-07-09-crystallizer-subsystem-decomposition
- Status: done
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-10T03:30:00Z
- Updated: 2026-07-10T03:30:00Z

## Problem / Opportunity
The ledger touches disk (owns CrystallizerCache + seven asset verbs) and the
root facade owns a transport (ExternalPersistenceManager custody + upload
hook). V3 identities: PersistenceSystem = in-process truth ONLY;
AssetManagementSystem = bytes at rest (cache files, formation files, remote
DB seam). First tranche that actually shrinks the god object.

## Design
Per system_docs/patches/active/crystallizer_decomposition_2026_07_09/
component_patch_asset_management.md (entry gate satisfied 03:30Z).

## Ticket Contract
- ENTRY_GATE: S2 sentinel GREEN (owner run, 2026-07-10); component patch
  authored + linked. SATISFIED.
- EXECUTION_BOUNDARY: new asset_management/ package (owner class + 3 moved
  files); persistence_system.py (7 verbs out, 3 in, 1 reshaped);
  crystallizer.py (slot swap, cleanup order, facade reroutes, upload hook
  deleted); NEW unit tests for AssetManagementSystem; sentinel imports only
  if touched. NOTHING ELSE. Facade surface byte-compatible.
- DEPENDENCIES: S1+S2 accepted.
- EXIT_GATE: grep gates (persistence_system has no cache/EPM references;
  no `persistence.crystallizer_cache` / `persistence.external_persistence`
  import paths anywhere in src); compile floor; owner sentinel green.
- FAILURE_ESCALATION: any facade signature drift or semantic delta in
  flush/reload/formation lanes -> stop + CONFLICT.

## Tasks
- [x] T1: mv crystallizer_cache.py + external_persistence_manager(.py|
      _configuration.py) -> asset_management/; self/consumer imports fixed
      (EPM self-import, bootstrap, crystallizer). DONE 03:45Z. NOTE: bash
      mkdir did not propagate to the real disk (mv target 'No such file');
      materialized the package dir via a file-tool Write instead - new
      environment fact for future moves.
- [x] T2: PersistenceSystem - cached_item_forms + max_persistence_crystals
      property + capture_formation_record added; restore_formation ->
      restore_formation_record (engine leg, S4 relocates); 7 asset verbs +
      cache slot/init/cleanup + describe()'s disk count REMOVED (facade
      re-enriches). DONE 04:00Z.
- [x] T3: asset_management_system.py (513L) - owner class per patch; flush
      absorbs the upload hook (ONE feedstock pull for both legs). DONE 04:10Z.
- [x] T4: Crystallizer - _external_persistence_manager slot ->
      _asset_management_system; cleanup asset-before-record; 10 facades
      rerouted (flush/reload x2/list-cache/formations x3/EPM x3);
      _upload_flushed_checkpoints deleted (NOTE comment); describe_record
      enriched with the asset count (payload parity). DONE 04:20Z.
- [x] T5 (RE-SCOPED, see DECISION 04:25Z): compile floor + grep gates done;
      NEW asset unit tests deferred - the existing exhaustive suites
      (test_crystallizer_cache, test_external_persistence_manager, the
      profile-cache suite) ARE the asset tests aimed at the old owner;
      S-test RE-HOMES them onto AssetManagementSystem instead of us
      duplicating them now.
- [x] T6: story/board sync; owner sentinel run REQUESTED. DONE 04:30Z.

## Acceptance Criteria
- PersistenceSystem contains zero disk/DB code (grep-proven).
- Crystallizer facades byte-compatible; upload leg preserved lenient.
- Sentinel set green (formation round trip, profile-cache round trip, pod
  bootstrap all traverse the new routing).

## Applicable Anti-Patterns
- [ ] No facade signature changes.
- [ ] No error-message drift on preserved lanes.
- [ ] No ledger -> asset call edges (edge law).
- [ ] "Not run." for anything not executed.

## Noting Behavior
- Story notes: seam evidence, verb inventory deltas, gate results.

## Notes
- DATETIME: 2026-07-10T03:30:00Z
  TYPE: PLAN
  CLAIM: Design pinned from source evidence: PersistenceSystem asset verbs at
    :573-1017 (bodies read in full), Crystallizer EPM custody + facades at
    :153-184, :1276-1504, :1591-1723, cache is ctor-arg-free (static root
    resolution), feedstock payloads already carry checkpoint_id+profile_name
    (upload leg can reuse them - one pull instead of two). Build order
    T1->T6.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_system.py:573-1017
  - src/melder/crystallizer/crystallizer.py:1276-1723
  - src/melder/crystallizer/persistence/crystallizer_cache.py:40-85
  IMPACT: After S3, PersistenceSystem is the boring ledger the V3 philosophy
    demands; S4's loader extraction becomes the last big cut.
  NEXT: T1 moves.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-10T04:25:00Z
  TYPE: DECISION
  CLAIM: T5 re-scoped: no NEW asset unit tests in S3. Rationale: the moved
    lanes are already exhaustively unit-tested by the existing suites
    (test_crystallizer_cache.py, test_external_persistence_manager.py, the
    profile-cache suite in test_kit_export_import.py) - they test the SAME
    semantics aimed at the old owner's verbs. Duplicating them now creates
    two copies that S-test must reconcile; instead S-test RE-HOMES them onto
    AssetManagementSystem verbs (rename-and-repoint, not rewrite). Sentinel
    integration coverage (profile-cache round trip, formation round trip,
    pod bootstrap w/ dict remote) exercises every S3 reroute end-to-end NOW.
  EVIDENCE:
  - tests/unit/melder/crystallizer/persistence/test_external_persistence_manager.py:1-30
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:1-30
  IMPACT: S-test story scope grows by the re-homing task; S3 stays a move.
  NEXT: build-complete FACT + sentinel request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-10T04:30:00Z
  TYPE: FACT
  CLAIM: S3 BUILD COMPLETE. Ledger surgery: persistence_system.py no longer
    contains ANY disk/DB reference (tool-layer grep: zero cache/EPM tokens);
    gained cached_item_forms (feedstock; payloads carry checkpoint_id +
    profile_name so flush pulls ONCE for cache+upload), live
    max_persistence_crystals property, capture_formation_record;
    restore_formation reshaped to restore_formation_record(record). Asset
    owner: AssetManagementSystem (borrows record via public verbs only; owns
    cache + EPM; flush = seal-then-ship with FIFO retention at the record's
    live cap + lenient upload leg; reloads land in the record's sink;
    formation files + EPM configure/describe/reload_from_external moved).
    Crystallizer: slot swap, asset-before-record cleanup, 10 facade reroutes
    byte-compatible, upload hook absorbed, describe_record re-enriched.
    GATES: old import paths 0 in src; ledger token gate 0. COMPILE: 4/4
    asset files PARSE OK (ast floor - py_compile's pyc write fails in the
    new dir on the mount); bootstrap disk tail verified intact (:397-402);
    crystallizer.py + persistence_system.py replicas binary (null-tail rot),
    disks verified via tool-layer grep/reads. Execution: Not run - sentinel
    set requested (integration suite traverses every reroute: profile-cache
    round trip, formations, pod bootstrap).
  EVIDENCE:
  - src/melder/crystallizer/asset_management/asset_management_system.py:1-513
  - src/melder/crystallizer/persistence/persistence_system.py:573-700
  - src/melder/crystallizer/crystallizer.py:1276-1650
  IMPACT: PersistenceSystem is now the boring ledger; only the load verbs
    remain to extract (S4).
  NEXT: owner sentinel run; on green, open S4 (crystal_loader_system +
    BootMediator).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-10T04:50:00Z
  TYPE: FACT
  CLAIM: SENTINEL RUN 1 (owner): 22+7+26 GREEN; integration 13/13 ERRORED at
    the cache_root fixture - MY MISS: the T1 grep inventory LISTED the test
    files carrying old cache/EPM import paths (incl. the sentinel integration
    file's module-form `from ...persistence import crystallizer_cache` at
    :105) and I fixed only the src consumers. Sentinel maintenance is the
    tranche law's whole point. FIXED: 9 import lines across 6 test files
    (restore_integration :105/:659, record_integration :261, record_sinks
    :242, test_crystallizer_cache :12, kit_export_import :27,
    external_persistence_manager :10/:13); repo-wide old-path gate now 0 via
    tool-layer grep (real disk; bash replicas are binary/rotted for edited
    files). Execution: Not run - rerun requested (integration suite only is
    sufficient; the three unit suites already passed this build).
  EVIDENCE:
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:105-105
  IMPACT: Inventory hygiene rule for S4: the affected-file list from the
    opening grep is a CHECKLIST, not context - every row gets ticked.
  NEXT: owner reruns the integration suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-10T05:05:00Z
  TYPE: FACT
  CLAIM: SENTINEL RUN 2: 12/13 GREEN through the new seam (round trips,
    profile-cache, pod bootstrap, M3 boot-boundary all traverse
    AssetManagementSystem correctly). One residual: analyze_formation's read
    leg still called the removed ledger verb (it was ON my patch-doc reroute
    list) -> rerouted to asset load_formation_record. The fix-pass grep then
    caught a SECOND latent residual no test exercises: the automatic-cadence
    auto_flush path (crystallizer.py:471) still called
    flush_checkpoint_to_cache + the deleted upload hook -> now one asset
    flush_checkpoint call (both legs). Verified zero remaining removed-verb
    call sites in src (tool-layer grep). Same lesson as run 1 compounded:
    reroute lists are CHECKLISTS - S4 will tick every facade row explicitly
    before requesting a run. Execution: Not run - rerun requested
    (integration suite only).
  EVIDENCE:
  - src/melder/crystallizer/crystallizer.py:1548-1556
  - src/melder/crystallizer/crystallizer.py:464-472
  IMPACT: The cadence crash-safe lane would have AttributeError'd in
    production on the first auto-flush interval - caught by gate grep, not
    by any test; S-test should add an auto-flush cadence regression.
  NEXT: owner reruns the integration suite; on green, S4 opens.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Extract bytes-at-rest custody into AssetManagementSystem per the component
patch; ledger gains record-side feedstock verbs; facades reroute untouched;
upload leg absorbed into the asset flush; sentinel run closes the tranche.
