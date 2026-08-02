- Completed: 2026-07-12T21:00:00Z
- Summary: Closed COMPLETE under the 20:35Z scope adjudication
  (owner-delegated): the mesh contract + generic quartet + RecordVersion +
  the first-party SqliteMeshAdapter deliver this epic's storage seam under
  the callables-first ruling; MR persistence shipped via the twin lanes
  (both node-row families). Atomic-batch item superseded by seal-then-ship
  (owner mesh ruling). Closed on owner directive; pytest Not run by agent
  - reopen on red. Adapter promotion carried as debt.

# Epic: Crystallizer Persistence (CRUD adapter: protocol/JSON + MutationResearchCrystal)

## Metadata
- Epic ID: EPIC-2026-07-03-crystallizer-persistence
- Parent Epic: EPIC-2026-07-02-agent-object-persistence-loop
- Status: ready (REACTIVATED 2026-07-11T22:05:00Z, melder_0 - owner
  correction: "I never said close your stuff... focus on the
  crystallizer stuff you planned". Everything else is done, so the old
  "adapter LAST" ruling now reads adapter NOW: remaining scope = a
  first-party adapter slice PROVIDING the mesh callables (SQLite first;
  the 8 mesh-SQLite tests already prototype the shape; users register
  the adapter's handlers through the normal fluents; core imports no DB
  stack - callables-first law intact). Spec authority =
  MeshInterfaceContract.describe(): the emitted table IS the adapter's
  storage contract.)
- Park history: PARKED to backlog 2026-07-11T19:10:00Z (substance
  largely shipped via other lanes; the CRUD adapter design here
  predates the callables-first ruling - re-derive from source).
- Owner: cowork
- Agent Name: melder_0 (owner-directed transfer 2026-07-05; crystal_0 = backup)
- Priority: p3
- Created: 2026-07-03T15:21:55Z
- Updated: 2026-07-03T15:21:55Z
- Target Window: 2026-Q3

## Problem / Opportunity
Crystals (first cut) and snapshots (bootstrap epic) need a single, host-owned persistence layer:
one db-write entry point + one hydrate/load point. This epic defines that CRUD adapter contract and
makes MutationResearch persist through it (MutationResearchCrystal), so all git-style ops
reload/unload via one seam.

## MRP Alignment
The single storage seam every other layer (bootstrap, MR, restore) rides. Host owns storage;
crystallizer defines the shapes. Get the contract right and any backend (SQLite/JSON/DB) plugs in.

## Ticket Contract
- ENTRY_GATE: routed on attention_board.md; parent + first-cut epic; consumed by the bootstrap epic
  (EPIC-2026-07-03-crystallizer-bootstrap-checkpoint) and MR.
- EXECUTION_BOUNDARY: the persistence protocol (a callable satisfying a typed PROTOCOL form,
  canonical) OR a JSON codec; CRUD verbs over named datasets; transaction = ordered atomic CRUD
  batch; the single db-write entry + single hydrate/load point; MutationResearchCrystal +
  git-style reload/unload; reference adapters (SQLite mock + JSON file). EXCLUDES snapshot
  composition (bootstrap epic) and MR merge-model semantics (parked).
- DEPENDENCIES: first-cut custody (produces crystals to persist).
- EXIT_GATE: crystals + MR composition round-trip (create/read/update/delete); a transaction applies
  as an atomic ordered batch; SQLite-mock + JSON-file adapters pass; green on 3.14t.
- FAILURE_ESCALATION: DECISION_REQUEST for typed-protocol-vs-JSON default and the dataset/key schema.

## Goals (Outcomes)
- Persistence model = a callable the HOST implements satisfying a specific PROTOCOL (typed contract,
  canonical) OR a JSON codec (portability). CRUD verbs: create / read / update / delete over named
  datasets.
- A "transaction" = an ordered batch of CRUD ops applied atomically.
- One db-write entry point + one hydrate/load point (the single seam all layers ride).
- MutationResearchCrystal: MR's composition (research streams, version records, heads, index
  associations - the git-style structure) persists + reloads/unloads through this CRUD layer.
- Reference adapters: a SQLite mock (tests) + a plain JSON-file adapter (emit + read-back).

## Non-Goals
- Snapshot composition / the crystal-twin family -> bootstrap epic.
- MR merge/lane/head model semantics (parked) - persistence only CONVEYS the data.
- Becoming a DB framework / owning table schemas (the HOST owns storage shape).

## Scope Boundaries
- In scope: the adapter contract + codecs + CRUD/transaction semantics + MutationResearchCrystal
  persistence + reference adapters.
- Out of scope: the snapshot walk (bootstrap epic), MR runtime semantics, first-cut wiring.

## Milestones (Track Progress)
- [ ] P1: the persistence PROTOCOL (typed contract, canonical) + JSON codec (portability option).
- [ ] P2: CRUD verbs (create/read/update/delete) over named datasets.
- [ ] P3: transaction = ordered CRUD batch, applied atomically.
- [ ] P4: the single db-write entry point + single hydrate/load point.
- [ ] P5: MutationResearchCrystal + git-style reload/unload through the CRUD layer.
- [ ] P6: reference adapters - SQLite mock + JSON-file.

## Stories (Required to Complete)
- [ ] Story: <TBD> - P1 protocol + JSON codec
- [ ] Story: <TBD> - P2 CRUD over named datasets
- [ ] Story: <TBD> - P3 transaction batch
- [ ] Story: <TBD> - P4 single entry/load seam
- [ ] Story: <TBD> - P5 MutationResearchCrystal
- [ ] Story: <TBD> - P6 reference adapters

## Acceptance Criteria (Epic Done)
- Crystals + MR composition CRUD round-trip through the adapter; transactions apply atomically;
  SQLite-mock + JSON-file adapters pass; green on 3.14t; owner accepts.

## Risks / Mitigations
- Risk: protocol-vs-JSON split confuses -> Mitigation: typed protocol canonical, JSON as codec/option.
- Risk: leaking storage concerns into crystallizer -> Mitigation: host owns storage; strict adapter boundary.
- Risk: mount write-fault -> verify writes.

## Open Questions
- Typed-protocol vs JSON default per dataset.
- Dataset + key schema (soft assignment + keys for DB-loaded systems).
- Whether MutationResearchCrystal is one dataset or several (streams / versions / heads).

## Decision Log
- 2026-07-03T15:21:55Z: Created as phase-3 of EPIC-2026-07-02. Persistence = a host callable satisfying a typed
  protocol OR JSON, CRUD over named datasets, transaction = ordered atomic batch; one db-write + one
  load seam. MR persists as MutationResearchCrystal through this layer (git-style reload/unload).
  Reference adapters SQLite-mock + JSON-file. Host owns storage; crystallizer defines shapes.
- 2026-07-06T15:45:00Z (melder_0, owner roadmap "local cache before adapter, adapter LAST"):
  the LOCAL CACHE lane landed in the wire-epic story (CrystallizerCache real: atomic JSON per
  checkpoint ULID under __crystallizer_cache__; flush_checkpoint_to_cache /
  reload_checkpoint_from_cache insert-if-absent / list_cached_checkpoint_ids at system +
  crystallizer facades). This REALIZES the single write+load seam's built-in filesystem lane
  (a P4-lite + JSON-reference slice); the ADAPTER CONTRACT (P1 typed protocol, P2 CRUD over
  named datasets, P3 atomic transaction batches, host-owned backends, SQLite mock) remains
  THIS epic's scope and comes LAST per owner. MutationResearchCrystal (P5) stays parked:
  owner directive 2026-07-06 - MR is all placeholders, owned by a separate agent.

## Context / Handoff Summary
Phase-3 storage seam: the CRUD adapter (typed protocol / JSON) all layers ride, plus
MutationResearchCrystal so MR's git-style ops persist + reload/unload through one seam. Consumed by
the bootstrap epic and MR; produces/consumes first-cut crystals.

## Decision Log (append, 2026-07-06T20:45:00Z, melder_0)
- Wire epic CLOSED. Local-cache slice (P4-lite) SHIPPED there: atomic JSON per
  checkpoint ULID under __melder_cache__/__crystallizer_cache__, flush/reload/list
  facades, cross-instance recovery proven in tests ("Not run." - user runs 3.14t).

## Notes
- DATETIME: 2026-07-12T20:35:00Z
  TYPE: DECISION
  CLAIM: SCOPE ADJUDICATION (owner-delegated: "adapter is done too
    right? go ahead and take ownership"): the SQLite adapter slice
    COMPLETES this epic's real scope. Rationale: the original P1-P3
    items (typed CRUD protocol, named datasets, atomic transaction
    batches) described a storage seam that the shipped reality
    delivers differently and better under the owner's callables-first
    ruling - MeshInterfaceContract (the self-describing contract),
    the generic kind-partitioned quartet (CRUD over kinds = the
    dataset model), RecordVersion stamps (the shape contract), and
    the first-party adapter (the reference backend, superseding the
    planned "SQLite mock"). P5 (MutationResearchCrystal persistence)
    shipped long ago via the twin + emit + checkpoint lanes and now
    carries both node-row families. "Transaction = ordered atomic
    batch" is intentionally NOT built: flush is seal-then-ship with
    lenient uploads by explicit owner ruling (2026-07-12 mesh lane) -
    recorded as superseded, not missing. CLOSURE rides the owner-run
    green (exit gate unchanged); on green this epic closes complete.
  EVIDENCE:
  - src/melder/crystallizer/asset_management/mesh_interface_contract.py
  - src/melder/crystallizer/asset_management/adapters/sqlite_mesh_adapter.py
  IMPACT: no further build slices belong to this epic; the run is the
    last gate.
  NEXT: owner-run green -> closure walk + promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T18:30:00Z
  TYPE: FACT
  CLAIM: OWNER-DIRECTED SEAM VERIFICATION - the two-node-kind MR model
    (ResearchNode + GroupedResearchNode) is coherent END TO END across
    the crystallizer, verified from source at all five stations:
    (1) RECORD - MutationResearchCrystal derives BOTH flat row families
    (research_nodes/grouped_research_nodes w/ set/lane context) from the
    composition AT CONSTRUCTION, so blob and rows cannot disagree
    (mutation_research_crystal.py:87-170); best-effort shape guards
    uphold the record-what-was-handed twin law. (2) SEAL/SHIP -
    describe() carries composition + both row lists (:266-277);
    JSON-safe (mutation_0's round-trip rows); the mesh ships it
    opaquely - PAYLOAD_SHAPES enumerates unit-kind keys only, so NO
    contract/adapter change (re-confirmed). (3) PREFLIGHT -
    MRCompositionStrategy dispatches node_type=="group": group_id joins
    the residence-agreement checks like any identity; pinned members
    absent from residence = drift WARNINGS (informational rebuild
    proceeds); legacy spell_sha tolerance intact
    (mutation_research_composition_strategy.py:129-217). (4) RESTORE -
    engine reads the COMPOSITION only (rows = queryable face, never the
    hydration carrier); ResearchLane.from_payload dispatches on
    NODE_TYPE and rebuilds the correct class per node
    (research_lane.py:676-682); node_identity() carries both families
    through lanes/journal/residence. (5) ADAPTER - the SQLite mesh
    adapter stores the whole stamped payload opaquely; users wanting
    per-node tables map the two row lists directly (the twin's stated
    design). ZERO defects found; zero residue beyond the already-
    adjudicated no-change contract ruling.
  EVIDENCE:
  - src/melder/crystallizer/crystals/mutation_research_crystal.py:29-277
  - src/melder/crystallizer/crystal_analysis/preflight/mutation_research_composition_strategy.py:100-218
  - src/melder/mutation_research/research_set/research_lane.py:626-690
  IMPACT: the crystallizer fully digests mutation_0's GroupedResearchNode
    program; the adapter epic's storage story covers both node kinds.
  NEXT: none for this seam; the epic still awaits the owner run +
    closure adjudication.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-12T16:20:00Z
  TYPE: FACT
  CLAIM: SQLITE ADAPTER SLICE IMPLEMENTED (owner: "You got an epic to
    do after"; patch sqlite_mesh_adapter_2026_07_12 authored first).
    Pre-build verifications: (a) the board's "8 mesh-SQLite tests"
    claim was STALE NAMING - the prototypes are the DICT-backED manager
    contract tests (test_record_version_and_json_contract.py:186-328;
    zero sqlite anywhere in the tree before this slice); (b)
    mutation_0's twin additive-keys NOTICE resolves NO-CHANGE for the
    contract table: PAYLOAD_SHAPES enumerates UNIT-kind top-level keys
    only (mesh_interface_contract.py:91-126) - twin-internal keys ride
    the payload column opaquely, so research_nodes/
    grouped_research_nodes need no mesh/adapter edit. LANDED: NEW leaf
    module asset_management/adapters/sqlite_mesh_adapter.py -
    SqliteMeshAdapter (Cleanable, guard-sentineled, namespace pkg = no
    __init__): one contract-shaped table (kind/profile_name/unit_id/
    payload JSON; PK (kind, unit_id); kind+profile listing index;
    idempotent schema at ctor; identifier-pattern gate on table_name =
    the injection guard; parent dirs created for pod boots); the four
    HANDLER_SIGNATURES verbs (store = INSERT OR REPLACE replace-on-emit;
    fetch = dict|None; list = kind+profile partition in ULID order;
    delete = STRICT KeyError on miss, mirroring the dict prototype);
    register_with(configuration) = sugar over the four PUBLIC fluents;
    describe() RecordVersion-stamped; connection-per-operation with
    contextlib.closing (deterministic close, no-GIL safe, no shared
    connection) + inner connection context for write transactions.
    CALLABLES-FIRST INTACT: core never imports the adapter or sqlite3;
    the user imports and registers. TESTS: 9-row suite
    (test_sqlite_mesh_adapter.py) driven THROUGH the real
    ExternalPersistenceManager: all four contract kinds round-trip,
    pod-restart durability across adapter instances, replace semantics,
    kind+profile partitioning + ULID ordering, fetch-None vs
    delete-strict asymmetry, JSON fidelity verified down to the raw
    stored column, ctor refusals, cleanup contract (file survives -
    user's asset), register_with wiring end to end. AST floor: both
    files parse OK (sandbox py3); pytest: Not run (owner-run 3.14t).
  EVIDENCE:
  - src/melder/crystallizer/asset_management/adapters/sqlite_mesh_adapter.py:1-420
  - tests/unit/melder/crystallizer/asset_management/test_sqlite_mesh_adapter.py:1-247
  - system_docs/patches/active/sqlite_mesh_adapter_2026_07_12/architecture_patch.md
  - src/melder/crystallizer/asset_management/mesh_interface_contract.py:91-126
  IMPACT: a user constructs the adapter, registers it through the
    normal fluents, and the whole mesh persists to SQLite with zero
    storage code - the epic's remaining scope under the callables-first
    ruling is delivered as its first concrete slice.
  NEXT: owner-run 3.14t (new suite + asset_management + persistence
    trees); on green: closure walk vs the epic's re-derived scope
    (the old P1-P3 typed-protocol/batch items predate callables-first -
    owner adjudicates whether the adapter slice completes the epic) +
    C-doc/graph promotion of the adapter component.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- Remaining scope = the adapter contract (P1-P6) - owner-sequenced LAST, after the
  restore engine (bootstrap epic). P5 MR crystal remains parked (other agent).
- 2026-07-07T02:20:00Z (melder_0): repaired the truncated 15:45 decision tail +
  Context/Handoff Summary from git 32e751d4f (write-fault incident; details in the
  parent epic's Phase-A Closure). Ticket writes FILE-TOOL-ONLY from here.
