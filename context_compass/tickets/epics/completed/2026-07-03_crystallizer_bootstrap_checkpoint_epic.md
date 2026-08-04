# Epic: Crystallizer Bootstrap + Checkpoint (crystal-twin snapshots + restore_aether)

- Completed: 2026-07-11T19:10:00Z
- Summary: The whole program this epic staged SHIPPED owner-green through
  the restore-engine story chain: twin family + emit model, checkpoint
  ledger/cache/chain-verify, RestoreEngine whole-system restore, reload
  lanes, M3 synthetic restore, formations + analyzer/preflight,
  CrystallizerBootstrap pod-restart lane, EPM. Both open child stories
  (formations+analyzer, loader-chain M3) closed with this epic. Closed
  on owner-directed self-cleanup; design deltas vs. the original
  restore_aether sketch are superseded by the promoted C-doc sections
  (the shipped model won).

## Metadata
- Epic ID: EPIC-2026-07-03-crystallizer-bootstrap-checkpoint
- Parent Epic: EPIC-2026-07-02-agent-object-persistence-loop
- Status: closed (owner-directed self-cleanup 2026-07-11; delivered
  owner-green via the restore program)
- Owner: cowork
- Agent Name: melder_0 (owner-directed transfer 2026-07-05; crystal_0 = backup)
- Priority: p3
- Created: 2026-07-03T15:21:55Z
- Updated: 2026-07-07T02:05:00Z
- Target Window: 2026-Q3

## Problem / Opportunity
Once crystallizer participates in bind and holds crystals (first cut,
EPIC-2026-07-03-wire-crystallizer-into-melder), we need to snapshot and restore a WHOLE running
Aether - frames, conduits, Nexus, bindings, links, configs - from a small manifest. This epic is
the north-star unfold: a container points at a snapshot and the checkpointed system is simply UP.

## MRP Alignment
The restore layer that makes "checkpoint a live object world, unfold it from a small bootstrap"
real. Structure-first: rebuild the registration graph; re-meld instances lazily.

## Ticket Contract
- ENTRY_GATE: routed on attention_board.md; parent + first-cut epic; persistence epic
  (EPIC-2026-07-03-crystallizer-persistence) provides store/load.
- EXECUTION_BOUNDARY: the crystal-twin family (Aetheric / AethericFrame / Conduit / Spell crystals),
  the `snapshot_aether` / `restore_aether` pair, content-addressed snapshot versioning, synth +
  non-synth leaf handling, and the two capture modes (live-push vs method-walk). EXCLUDES the CRUD
  adapter internals (persistence epic), MR semantics, first-cut wiring.
- DEPENDENCIES: first-cut custody (produces SpellCrystals); persistence epic (store/load).
- EXIT_GATE: `snapshot_aether(name)` captures a running Aether into a composed crystal tree;
  `restore_aether(name)` rebuilds it (configs -> frames -> Nexus -> conduits -> bindings -> links);
  instances re-meld at runtime; synth + non-synth both restore; green on 3.14t.
- FAILURE_ESCALATION: DECISION_REQUEST for capture-mode default and restore atomicity.

## Goals (Outcomes)
- A crystal-twin per structural unit: AethericCrystal (root/system) composes AethericFrameCrystals
  compose ConduitCrystals compose SpellCrystals (+ module/synthetic crystals). Each twin is a
  PURE-DATA serializable mirror - no behavior, no instances, no locks.
- `snapshot_aether("name")`: walk the live tree, emit the composed twin, hand to persistence.
- `restore_aether("name")` / `restore_aether("name", version=<callsign>)`: rebuild the live tree
  top-down in dependency order; instances re-meld lazily.
- Snapshot-over-time: each AethericCrystal snapshot is content-addressed (callsign-style) ->
  immutable, versioned checkpoint history (dedup identical).
- Synth vs non-synth is a LEAF concern: module-crystals carry authority (physical / bytecode /
  synthetic); the upper tree is identical either way.
- Two capture modes: (a) live objects push their twin into an active snapshot as they change
  (incremental), or (b) a method-walk captures at a point in time.

## Non-Goals
- The CRUD / persistence adapter internals -> EPIC-2026-07-03-crystallizer-persistence.
- MR merge-model / impact-engine semantics.
- The first-cut wiring (separate epic).
- Live object-INSTANCE serialization (twins are structure/state only; instances re-meld).

## Scope Boundaries
- In scope: crystallizer crystal-twin types + the snapshot/restore engine.
- Out of scope: the storage adapter (persistence epic), MR internals, first-cut wiring.

## Milestones (Track Progress)
- [ ] B1: crystal-twin family (Aetheric / AethericFrame / Conduit / Spell) with symmetric
      to_crystal (emit) + restore (rebuild) per type.
- [ ] B2: `snapshot_aether` - walk the live tree, compose the twin, store via persistence.
- [ ] B3: `restore_aether` - rebuild top-down in dependency order; instances re-meld.
- [ ] B4: content-addressed snapshot versioning (checkpoint history; latest + pinned).
- [ ] B5: synth vs non-synth leaf handling (physical/bytecode import-exec vs loader seed).
- [ ] B6: capture modes - live-push into an active snapshot vs method-walk.

## Stories (Required to Complete)
- [ ] Story: <TBD> - B1 crystal-twin family
- [ ] Story: <TBD> - B2 snapshot_aether
- [ ] Story: <TBD> - B3 restore_aether
- [ ] Story: <TBD> - B4 snapshot versioning
- [ ] Story: <TBD> - B5 synth/non-synth leaf
- [ ] Story: <TBD> - B6 capture modes

## Acceptance Criteria (Epic Done)
- snapshot_aether -> restore_aether round-trips a running Aether (structure) on 3.14t; instances
  re-meld; versioned snapshots restore exactly; synth + non-synth both work; owner accepts.

## Risks / Mitigations
- Risk: twin drift from the live object -> Mitigation: symmetric emit/restore + round-trip tests.
- Risk: restore ordering wrong -> Mitigation: fixed dependency order + tests.
- Risk: mount write-fault -> verify writes.

## Open Questions
- Capture-mode default (live-push vs method-walk).
- Restore atomicity (all-or-nothing vs partial/resumable).
- Where twin-emit lives (`to_crystal()` on each live type vs a visitor in crystallizer).

## Decision Log
- 2026-07-03T15:21:55Z: Created as phase-2 of EPIC-2026-07-02. Crystal-twin family mirrors the ownership tree;
  snapshot_aether/restore_aether are the symmetric pair; twins are pure-data; snapshots are
  content-addressed for a checkpoint history; synth/non-synth is a leaf concern. Rides the
  persistence epic for store/load.

## Context / Handoff Summary
Phase-2 restore layer: compose a running Aether into a tree of crystal-twins (Aetheric /
AethericFrame / Conduit / Spell), snapshot + restore via restore_aether, versioned over time.
Structure-first; instances re-meld. Storage rides the persistence epic.

## Restore-Engine Design Note (2026-07-06, melder_0 - grounded in the landed record)
The record this engine consumes NOW EXISTS in full (wire-epic Phase A + relationship +
durability lanes; trail: tickets/stories/2026-07-05_persistence_crystal_profile_and_
twin_family_scaffold_story.md). What restore has to work with:

- INPUTS: the active profile's CURRENT twins (live mirror) OR a checkpoint replay
  (PersistenceCrystal journal segment + captured payloads, reloadable from the local
  cache via reload_cached_checkpoint - history survives the process).
- TWIN COVERAGE: AetherCrystal (root config), AethericFrameCrystal (posture+devops),
  SpellbookCrystal (config payload + hook markers + bind_order), ConduitCrystal
  (+ link_targets = OUTBOUND edges), SpellCrystal (bind facts: spell/binding/
  spellframe/existence/permissions names + spellbook edge + rebindability),
  SpellIndexCrystal (owner edge, selection, member SHAs), ContractCrystal (endpoints +
  per-side details/subscriptions), RecordedUnitState switches (nexus/MR), tombstones
  (spell/spellbook/spell_index/contract/frame _removed) + activity payloads.
- REPLAY ORDER (canon, refined): aether config -> frame postures -> spellbook configs
  -> conjure (conduits) -> binds from spell custody in SpellbookCrystal.bind_order
  (active=bind; staged=bind_inactive onto the index anchored by SpellIndexCrystal
  selection) -> notch to recorded selections -> LINK EDGES from link_targets
  (initiator side re-links) -> CONTRACTS last (details/subscriptions re-granted from
  ContractCrystal projections).
- IDENTITY: recorded ULIDs (conduit/index/contract ids) are record-local - restore
  mints fresh and walks an old->new translation map (parent-epic 2026-07-05 decision);
  spell SHAs / frame names / profile names are the stable coordinates.
- REBINDABILITY: "hydratable" (class/function root targets) rebuild by re-import/
  materialize; "replay_required" (method/lambda/object spells, hooks) are REPORTED as
  shortfalls, never under-built silently.
- CHECKPOINT REPLAY SEMANTICS: apply journal events in sequence per capture window;
  removal tombstones apply the same match rules the live evictions used (spellbook_id
  parent-edge subtree, either-endpoint contract sweep); "hydration is checkpoint-shaped
  replay, never raw map-merge".
- ENTRY POINT: PersistenceSystem.load_checkpoint's NotImplementedError body is the
  seat; the guard canon (activate crystallizer before building) applies to the
  restore-target world too.
- CLUSTERS (added 2026-07-06T16:40:00Z): ClusterCrystal records cluster/frame
  identities, member conduit ids, elected leader, and shared lineage entries -
  restore regroups clusters AFTER conduits exist and BEFORE/alongside contracts
  (shares re-granted through cluster verbs; leader re-elected last).
- KNOWN NON-COVERAGE (by design): instances (re-meld lazily), spellspaces, hook
  callables (markers only), MR internals (placeholders; other agent).

## EMIT model (DECISION, 2026-07-04T14:15:20Z)
Structural units EMIT to crystallizer (push); crystallizer is a passive observer/sink (no pull).
Enable crystallizer (store + policy only); frames/conduits/spellbooks/spells/links emit their twin +
lifecycle at create/configure/change; crystallizer records + persists -> it 'just knows what's
configured'. Dissolves the onion (no ordering/reach-in). Bootstrap OPEN-ENDED: restore_conduit/
restore_frame/restore_aether = same op at different subtrees. bind EMITS (no-op when crystallizer off
-> byte-identical). Emit-points: frame finalize, conjure, bind, link (+ MR's existing emit). Detail:
artifacts/2026-07-03_bootstrap_design_detail.md (EMIT/OBSERVER MODEL).

## Decision Log (append, 2026-07-06T20:45:00Z, melder_0)
- Wire epic CLOSED (owner-accepted) - this epic is now the ACTIVE successor lane.
- B1 (twin family) is SATISFIED by the wire epic's landed record (9 twin kinds,
  pure-data, describe-detached) - richer than drafted (index/contract/cluster twins
  were not in the original B1 list). B2 is SUPERSEDED: no method-walk snapshot_aether;
  the EMIT model + checkpoint seals ARE the capture (owner canon: no catch-up walk).
- Remaining real work: B3 restore (load_checkpoint seat, per the Design Note above),
  B4 largely covered by checkpoint ledger + local cache (chain-integrity verb still
  open), B5 rebindability shortfall reporting, B6 resolved (live-push won; owner).
- Status: draft -> ready.

## Kit Export/Import Design Note (2026-07-07, melder_0 - prep for the next lane)
Grounded in the landed surfaces; NO code until the owner opens the lane.
- A KIT = one profile's foldable history as a portable file set: manifest
  (kit name, profile name, chain checkpoint ids + numbers, seal stamps,
  format version) + the chain's cached-item payloads (exactly
  PersistenceCrystal.to_cached_item - the codec already round-trips).
- EXPORT = verify_checkpoint_chain gate (refuse "broken"; warn-annotate
  "truncated_prefix" into the manifest) -> write manifest + items into one
  directory / archive. IMPORT = read manifest -> from_cached_item each ->
  insert-if-absent into the ledger (reload semantics; no retention dropout)
  -> the restore engine folds it like any chain.
- Activation Rules carry over: synthetic-containing kits only unfold into
  dynamic frames; rebindability shortfalls report at unfold, same as any
  restore (kits change TRANSPORT, not honesty).
- OPEN (owner taste): archive format (.zip vs directory), kit naming,
  whether import auto-creates a named profile matching the kit name,
  sealer trust/signing (already deferred to a kit-distribution epic).

## Notes

- DATETIME: 2026-07-07T23:10:00Z
  TYPE: FACT
  CLAIM: GRAPH REGEN COMPLETE (last queued doc lane). src_graph.json:
    +9 authored nodes (PersistenceSystem, PersistenceProfile,
    PersistenceCrystal, CrystallizerCache, RestoreEngine,
    ExternalPersistenceManager + its Configuration,
    CrystallizerBootstrap, persistence.crystals package node) and +10
    edges (ownership hierarchy incl. the crystallizer's dual-rank
    children, ledger/cache/profile ownership, engine creation, the M3
    engine->SyntheticModule creates edge, bootstrap->facades uses edge);
    STALE FIX: the pre-move melder.crystallizer.spell_crystal.SpellCrystal
    node relocated to persistence.crystals with updated file/role (M3
    sources noted) and all referencing edges remapped. 516->525 nodes,
    943->953 edges. readable_src_graph.json regenerated per the
    canonical Markdown recipe (safe-delimiter breaks, width 220,
    validity-checked; python equivalent of the inline PowerShell block -
    the recipe mandates inline execution, no repo script added). Both
    files JSON-valid; readable verified on user disk via file-tool read.
  EVIDENCE:
  - system_docs/src_graph.json (525 nodes / 953 edges)
  - system_docs/readable_src_graph.json (4086 lines)
  IMPACT: Onboarding graph truth now covers the entire persistence
    program. The epic's queued work is now: owner sweep of M3 (last
    unproven lane) + the future first-party adapter package only.
  NEXT: Owner sweep.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T21:40:00Z
  TYPE: FACT
  CLAIM: PATCH-DOC PROMOTION COMPLETE. Both restore_engine_2026_07_07
    patch docs merged into the C-docs as current-state sections:
    src_components.md gained "Crystallizer Persistence & Restore"
    (ownership hierarchy, EMIT model + emission seams, checkpoints/cache/
    retention, restore stages in canonical order, reload lanes,
    ExternalPersistenceManager, CrystallizerBootstrap); src_architecture.md
    gained "Persistence & Restore Architecture" (canonical boot order,
    EMIT invariants incl. the sanctioned aether root catch-up, restore
    invariants, durability layering ledger->cache->user DB). BOTH C-doc
    truncated tails repaired with honest closure markers (loss predates
    recoverable git history - verified back 8 commits; nothing guessed).
    Patch dir moved active/ -> completed/. Remaining doc debt: readable
    graph regen (needs src_graph.json authorship); loader-chain M3 is the
    next feature lane.
  EVIDENCE:
  - system_docs/src_components.md (tail + new section)
  - system_docs/src_architecture.md (tail + new section)
  - system_docs/patches/completed/restore_engine_2026_07_07/
  IMPACT: Every future agent onboards on current persistence truth; the
    patch lane is closed per protocol.
  NEXT: none for this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T13:40:00Z
  TYPE: FACT
  CLAIM: AETHER UTILITY SYSTEM AUDIT complete (owner-ordered follow-up,
    post story closure). VERDICT: the utility system holds exactly THREE
    configured fields (activation knob, channel resolver, default logger)
    - all applied from AetherConfiguration at Aether.activate via
    _apply_configuration_to_utility_system (clear-then-register full
    overwrite), so config restore already covered the activation-time
    surface. REAL GAP FOUND AND FIXED: the mutation verbs are PUBLIC and
    post-activation flips bypassed the configuration - the record drifted
    silently. NEW emission seam AetherUtilitySystem.
    emit_root_twin_when_recording (payload from LIVE fields; lazy
    crystallizer import; presence flags for callables) called by all five
    mutating verbs (set knob, register/clear resolver, register/clear
    default logger). Redundant re-emissions during activation are
    harmless replace-on-emit last-wins. Regression test:
    tests/unit/melder/aether/test_aether_utility_system_record.py (flip +
    register post-activation -> twin payload follows; clear -> presence
    False). Compile: test OK in-sandbox; aether_utility_system.py Not run
    (replica rot; disk verified). Follow-up noted in-test: no public
    facade exists yet for reading the recorded root twin payload.
  EVIDENCE:
  - src/melder/aether/aether_utility_system.py (seam + 5 call sites)
  - tests/unit/melder/aether/test_aether_utility_system_record.py
  IMPACT: The root twin now mirrors live truth at every mutation point -
    the last silent-drift surface on the aether root is closed. NEXT
    LANES: kit export/import (design note above), patch-doc promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-07T02:05:00Z
  TYPE: FACT
  CLAIM: TRUNCATION REPAIR + code verification. (a) INCIDENT: melder_0's 2026-07-06
    bash append (read-whole/rewrite-whole) baked a stale replica into this file,
    cutting the Design Note body mid-line and the whole EMIT model section; restored
    VERBATIM from melder_0's in-session read of the intact file. Epic writes are
    FILE-TOOL-ONLY from here (mailbox/board precedent extended to tickets).
    (b) VERIFICATION: the restore seat matches the Design Note exactly.
    `PersistenceSystem.load_checkpoint` validates the id under lock THEN raises
    NotImplementedError (restart-lane by contract). `PersistenceCrystal.replay_data()`
    returns {"journal": [[seq, kind, key]...] window-ordered, "payloads":
    {kind: {key: payload}}} fully detached; fold contract on the class (world at
    checkpoint K = fold chain 1..K, later payloads win per (kind, key)).
    `capture_segment_since` carries all 18 capture branches (9 live kinds via
    _resolve_twin, spell_crystal dual-location, spell_activity current-truth,
    nexus/MR state + twin_present, 6 tombstones incl. spellbook subtree). Twin
    payloads carry the restore inputs: SpellbookCrystal bind_order/config/hooks;
    SpellIndexCrystal owner+selection+members; ConduitCrystal link_targets+config;
    SpellCrystal full bind signature + rebindability.
    STALENESS (separate): readable_src_graph.json predates Phase A for the
    crystallizer subtree (old spell_crystal path, zero persistence/** nodes); both
    src_architecture.md and src_components.md have truncated tails.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_system.py:874-905
  - src/melder/crystallizer/persistence/persistence_crystal.py:242-271
  - src/melder/crystallizer/persistence/persistence_profile.py:863-981
  - src/melder/crystallizer/persistence/persistence_profile.py:1011-1051
  - src/melder/crystallizer/persistence/crystals/spellbook_crystal.py:178-194
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:1516-1560
  IMPACT: No drift between the record and the Design Note - B3 can be planned
    directly on the shipped surfaces; the epic's canonical design content is whole
    again on disk.
  NEXT: Owner approves the B3 restore-engine plan (patch docs + story + implementation
    boundary proposed in chat); patch artifacts land BEFORE code per
    patch_framework_gating.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-07T02:45:00Z
  TYPE: FACT
  CLAIM: Rebuild-side survey - EVERY replay stage has a live public driver; the missing
    piece is ONLY the engine. (1) Aether config: create_configuration/configure/activate.
    (2) Spellbook.bind is keyword-only (spell, existence, permissions, spellframe,
    binding_name, disposal_method_names, profile); staged lane = Conduit.bind_inactive
    + Conduit.notch_spell (public surfaces moved to Conduit; spellbook holds _bind_inactive
    /_notch_spell internals). (3) SPELLFRAME RESTORE IS NAME-SAFE:
    normalize_frame_key(cls) == normalize_frame_key(cls.__name__) (lowercased __name__),
    so binding with the recorded spellframe_name STRING reproduces the identical
    (frame_key, binding_key) - no spellframe import needed. (4) Hydratable spells rebuild
    from root_module_name + root_target_qualname (import + attr walk), gated by the
    recorded rebindability field. (5) Conjure/link/contract/cluster drivers all public:
    Spellbook.conjure, Conduit.link, the 8 contract verbs (+ Conduit.transaction windows
    for removal-family ops), ConduitCloud.create_cluster/add_conduit_to_cluster +
    ClusterCrystal members/leader/shares.
    GAPS (= the work): G1 the engine itself (fold chain 1..K + replay orchestration +
    old->new ULID translation + shortfall report) in load_checkpoint's body + a new
    persistence module. G2 spellbook config payload coerces non-plain property values to
    str at capture (spellbook.py ~:284 region) - restore must classify round-trippable
    properties; the rest are shortfall entries. G3 synthetic-rooted spells cannot
    re-import until parent M3/M5 land - first cut REPORTS them (root_module_kind ==
    "synthetic") as shortfalls. G4 rebuilding through public verbs re-emits into the
    ACTIVE profile: the restored world re-records itself under fresh ULIDs - coherent
    with the never-rehydrate-ULIDs policy; adopt as intended behavior. G5 atomicity =
    owner decision (recommend all-or-nothing first cut). G6 chain-integrity verb stays a
    separate small lane (B4 residue).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4338-4400
  - src/melder/aether/conduit/conduit.py:2785-2785
  - src/melder/aether/conduit/conduit.py:3972-3972
  - src/melder/utilities/helpers/general_helpers.py:129-153
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:203-216
  - src/melder/aether/conduit/conduit.py:4723-5278
  - src/melder/aether/aetheric_frame/conduit_cloud.py:394-519
  IMPACT: B3 scope is confirmed narrow - one engine module + the load_checkpoint body;
    no changes needed on capture or runtime surfaces for the first slice.
  NEXT: Owner picks atomicity (G5) and approves the story + patch docs; then patch
    artifacts land BEFORE engine code per patch_framework_gating.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
