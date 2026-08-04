# Task: Investigate crystallizer implementation to prepare MutationResearch build

- Completed: 2026-07-11T19:20:00Z
- Summary: Crystallizer mechanics captured with evidence and the MR
  persistence/hydration seam identified (Phase A->B on MutationResearchCrystal)
  - the seam this task named became the shipped MR program (Phase B twin,
  build stage, preflight row, all owner-run green). Open DECISION_REQUEST and
  BLOCKER resolved/mooted by the V3 decomposition. Final owner-directed
  verification read confirms the loop coherent end to end. Closed by mutation_0
  on lane inheritance (same MR lineage) under owner directive.

## Metadata
- Task ID: TASK-2026-07-08-investigate-crystallizer-implementation
- Story: none (standalone; seeded the MR build program - see
  tickets/stories/completed/2026-07-11_build_mr_research_set_core_story.md)
- Status: done
- Owner: cowork
- Agent Name: mutation_research_0, mutation_0 (inheritor)
- Priority: p1
- Created: 2026-07-08T22:07:12Z
- Updated: 2026-07-11T19:20:00Z

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: owner closure directive 2026-07-11; deliverables served
  their purpose (the MR program built on this task's findings is complete and
  closed); final verification read executed on owner direction.

## Objective
Understand how the crystallizer subsystem (`src/melder/crystallizer/**`, ~14k LOC)
actually works end to end, ground the V2 "Custody + Unfold" philosophy against the
real code, flag doc drift, and identify the crystallizer<->MutationResearch persistence
and hydration seam so MutationResearch build work can start from evidence.

## Ticket Contract
- ENTRY_GATE: this ticket active + a routing row on `attention_board.md`; read-only.
- EXECUTION_BOUNDARY: read-only investigation across `src/melder/crystallizer/**`;
  cross-reference `system_docs/src_architecture.md`, `system_docs/src_components.md`,
  and the crystallizer/MR V2 philosophy artifacts. NO source edits under this task.
- DEPENDENCIES: `artifacts/2026-07-01_crystallizer_philosophy_v2.md`,
  `artifacts/2026-07-01_mutation_research_philosophy_v2.md`.
- EXIT_GATE: crystallizer mechanics (root API, SpellCrystal unit, persistence system,
  restore/unfold engine, synthetic-module activation, MR persistence seam) captured in
  `## Notes` with `path:start-end` evidence; open questions listed.
- FAILURE_ESCALATION: record `DECISION_REQUEST`/`CONFLICT`/`BLOCKER` on any code<->doc
  conflict material to MR design, or if a claimed mechanic cannot be evidenced.

## Scope Boundaries
- In scope: reading and understanding crystallizer source; mapping code to V2 philosophy;
  identifying the MR persistence/hydration seam and crystal-at-bind custody path.
- Out of scope: any code edits; MutationResearch implementation; crystallizer refactors.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user directed reading the crystallizer to prep MR work; investigation started.

## Steps / Checklist
- [ ] Read crystallizer root (`crystallizer.py`, `crystallizer_bootstrap.py`) - API + lifecycle.
- [ ] Read `persistence/crystals/spell_crystal.py` - the SpellCrystal unit.
- [ ] Read persistence engine (`persistence_system.py`, `restore_engine.py`, `persistence_profile.py`).
- [ ] Read `synthetic_module.py` - live module embodiment / unfold target.
- [ ] Read MR seam (`persistence/crystals/mutation_research_crystal.py`, `external_persistence_manager.py`).
- [ ] Read configuration + cache + per-type crystals + analysis strategies (lighter).
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Evidence-backed understanding of crystallizer mechanics in `## Notes`.
- Identified crystallizer<->MutationResearch seam for MR build planning.

## Files / Paths Impacted
- None (read-only investigation).

## Validation
- Not run.
- Recommended commands:
  - (user, 3.14t) targeted crystallizer unit/component/integration suites once MR build starts.

## Risks / Rollback Notes
- Docs (`src_architecture.md` / `src_components.md`) are stale on crystallizer structure;
  treat code as truth and flag drift rather than trusting the docs.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= minimum_note_score)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-07-08_crystallizer_persistence_gaps_and_remaining_work.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retained as the crystallizer/persistence gap map + MR build roadmap.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-07-08T22:07:12Z
  TYPE: PLAN
  CLAIM: Read crystallizer source in priority order (root -> SpellCrystal -> persistence
    system -> restore engine -> synthetic module -> MR seam -> config/cache/per-type
    crystals) to understand mechanics and locate the MR persistence/hydration seam.
  EVIDENCE:
  - src/melder/crystallizer/crystallizer.py:1-1783
  - src/melder/crystallizer/persistence/persistence_system.py:1-1527
  IMPACT: Establishes the read plan for grounding MR V2 build work in real code.
  NEXT: Read crystallizer.py root API + lifecycle.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-07-08T22:07:12Z
  TYPE: FACT
  CLAIM: Crystallizer is ~14k LOC and the canonical docs are STRUCTURALLY STALE: the
    `crystal_loader/`, `crystal_analysis/`, and `asset_management/` packages named in
    src_architecture/src_components are still 0-line scaffold, while a large undocumented
    `persistence/` subtree is the real engine (persistence_system 1527, restore_engine
    1618, persistence_profile 1323, crystals/spell_crystal 1683). SpellCrystal now lives at
    `persistence/crystals/spell_crystal.py`, not the top-level `spell_crystal.py` the docs cite.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader/crystal_loader.py:1-1
  - src/melder/crystallizer/persistence/persistence_system.py:1-1527
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:1-1683
  IMPACT: MR build planning must read the code, not the stale docs; the persistence subtree
    is where the crystallizer<->MR seam actually lives.
  NEXT: Read crystallizer.py to confirm the root API and how bind/crystal creation is wired.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-08T22:10:56Z
  TYPE: FACT
  CLAIM: Crystallizer already implements the V2 "Custody + Unfold" model as a live
    EMIT -> record -> checkpoint -> restore engine (NOT future work). Structural units push
    typed twins into the active PersistenceProfile via `emit(...)` / `emit_spell_crystal(active|
    inactive)` (NO-OP until activated); PersistenceSystem seals delta windows into
    PersistenceCrystal checkpoints (ordered journal window + full-object-per-twin payloads;
    a world at checkpoint K = fold chain 1..K, later wins per (kind,key)); flush to a local
    cache (atomic JSON) + optional ExternalPersistenceManager upload via user callables;
    `load_checkpoint` unfolds by replaying public runtime verbs (restore_engine). SpellCrystal
    is the built per-spell source-custody manifest (root module + dep walk + synthetic/
    user_source/site_package/unknown classification), minted at bind via create_spell_crystal.
  EVIDENCE:
  - src/melder/crystallizer/crystallizer.py:933-996
  - src/melder/crystallizer/crystallizer.py:1725-1753
  - src/melder/crystallizer/persistence/persistence_crystal.py:9-38
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:20-57
  IMPACT: MR build does not need to build persistence/custody/unfold from scratch; it plugs
    into an existing substrate. Crystallizer V2 philosophy is BEHIND the code here.
  NEXT: Read persistence_system.py + restore_engine.py for exact record/fold/replay mechanics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-08T22:10:56Z
  TYPE: FACT
  CLAIM: The crystallizer<->MR seam is staged and the gap is NAMED in code:
    MutationResearchCrystal records "Phase A" (config/activation state only); the git-style
    composition (research streams, version records, heads, index associations) is "Phase B /
    persistence epic P5" and deliberately absent. `emit_mutation_research_state` records
    lifecycle flips (RecordedUnitState); MR is codegen/dynamic-lane-only so its twin only
    appears in dynamic-lane profiles. `get_spell_crystal(spell_id)` is the custody lookup MR
    (and loaders) use.
  EVIDENCE:
  - src/melder/crystallizer/persistence/crystals/mutation_research_crystal.py:8-33
  - src/melder/crystallizer/persistence/crystals/mutation_research_crystal.py:40-62
  - src/melder/crystallizer/crystallizer.py:850-874
  - src/melder/crystallizer/crystallizer.py:486-514
  IMPACT: The first MR build increment is bounded: build MR's in-memory composition
    (ResearchStream / VersionRecord / heads / index associations) and extend
    MutationResearchCrystal Phase A -> Phase B (P5) as a hydrate/emit seam - matching MR V2
    build-order steps 1-2. No new crystal object needed; extend the existing twin.
  NEXT: Read src/melder/mutation_research/** to map current MR runtime vs the V2 target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-08T22:10:56Z
  TYPE: PLAN
  CLAIM: Before designing the first MR build story, read melder_0's directly-overlapping
    `agent_object_persistence_loop` epic (2026-07-02) and the actual `src/melder/mutation_research/**`
    to ground current MR runtime state; then scope story 1 with the user.
  EVIDENCE:
  - tickets/epics/2026-07-02_agent_object_persistence_loop_epic.md:1-1
  - src/melder/mutation_research/mutation_research.py:1-1
  IMPACT: Avoids re-deriving what melder_0 already mapped and prevents wiring MR to the wrong seam.
  NEXT: Await user direction on scope, then read melder_0 epic + mutation_research/ source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-08T22:37:02Z
  TYPE: CONFLICT
  CLAIM: CORRECTION to the 22:10:56Z "implements V2 Custody+Unfold" note - it wrongly
    reconciled code with philosophy. The built crystallizer STRUCTURALLY FORKED from the
    philosophy. The philosophy's structure (crystal_loader unfold chain: bootstrap_manifest ->
    crystal_loader -> synthetic_module_loader -> bootstrap_loader; crystal_analysis save-time
    facts; asset_management) is DEAD SCAFFOLD: whole-tree grep of src/melder for
    crystal_analysis|crystal_loader|asset_management|crystal_management = 0 importers;
    crystal_management/ and crystallizer/mutation_research/ are entirely empty; the rest are
    0-line stubs. The real, WIRED engine is the persistence/ subtree (EMIT twin -> profile ->
    checkpoint -> restore), landed Jul 5-7 (AFTER the Jul 1 V2 philosophy). It is genuinely
    live: Aether constructs it; Conduit/Frame/Ward/Cluster/Spellbook/Transfer emit typed twins
    into it, gated on _crystallizer.activated.
  EVIDENCE:
  - src/melder/aether/aether.py:109
  - src/melder/aether/conduit/conduit.py:393-396
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:400-416
  - src/melder/crystallizer/crystal_loader/crystal_loader.py:1-1
  IMPACT: The crystallizer philosophy docs describe an abandoned structure. Any MR plug-in must
    target the persistence/ EMIT model, not the dead loader chain. The philosophy<->code
    divergence must be reconciled before MR is built on top of it.
  NEXT: Read melder_0 Jul 2-3 design artifacts to determine if persistence/ was a sanctioned pivot.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-08T22:37:02Z
  TYPE: DECISION_REQUEST
  CLAIM: User must decide whether the persistence/ EMIT model is the ACCEPTED crystallizer
    direction (=> reconcile/retire the philosophy's dead loader-chain structure + dead dirs and
    plug MR persistence into persistence/), or whether the fork should be reconsidered before MR
    work proceeds. Not answerable from code alone; whether persistence/ was a sanctioned pivot
    likely lives in melder_0's 2026-07-02 agent_object_persistence_loop philosophy (25KB) +
    2026-07-03 persistence_design_detail artifacts.
  EVIDENCE:
  - codex/context_compass/artifacts/2026-07-02_agent_object_persistence_loop_philosophy.md:1-1
  - codex/context_compass/artifacts/2026-07-03_persistence_design_detail.md:1-1
  IMPACT: Building MR on a crystallizer whose structure diverged from intent, without confirming
    the divergence is accepted, risks wiring MR to a seam that may itself be reconsidered.
  NEXT: Read the two melder_0 design artifacts, then bring the divergence + MR plug-in options to the user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-08T22:42:17Z
  TYPE: FACT
  CLAIM: Persistence engine spine read end-to-end (record -> checkpoint -> restore).
    PersistenceSystem owns profiles (one active; "default" guaranteed) + a checkpoint ledger
    (PersistenceCrystal, ULID, FIFO cap) + disk cache + external manager. PersistenceProfile is a
    FLAT level-mapped twin store mirroring the runtime hierarchy (AetherCrystal -> {MR, Nexus,
    Frame} -> Spellbook -> {SpellCrystal, Conduit} + index/contract/cluster), replace-on-emit,
    journaled (sequence,kind,key); capture_segment_since(mark) detaches current-state describe()
    payloads = the checkpoint delta window. RestoreEngine folds the profile's crystal chain
    (later-wins + tombstone sweeps) then replays through the PUBLIC runtime verbs in canon order:
    aether_config -> crystallizer(reported) -> MR(reported) -> nexus -> frames(posture first) ->
    books_and_binds(configure+freeze, active binds PRE-conjure, conjure, staged bind_inactive
    POST-conjure onto live index anchors, notch divergent selections) -> links -> clusters ->
    contracts LAST. Identity: spell SHAs are content-stable (kept); index/conduit/contract/cluster
    ULIDs translate to fresh ids (never-rehydrate-ULIDs). Synthetic-module roots are rebuilt
    IN-ENGINE by _rebuild_synthetic_world (construct/register/publish/execute, parents-first).
    All-or-nothing with reverse teardown; shortfalls reported, never silent.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_profile.py:29-67
  - src/melder/crystallizer/persistence/persistence_system.py:1226-1297
  - src/melder/crystallizer/persistence/restore_engine.py:397-455
  - src/melder/crystallizer/persistence/restore_engine.py:1461-1594
  IMPACT: The engine is a coherent snapshot-twin + journal + checkpoint-fold + public-verb-replay
    system, well beyond scaffold (multiple Jul-7 hardening fixes present), NOT a half-built drift.
  NEXT: Read spell_crystal custody internals + synthetic_module + adapters for full depth.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-08T22:42:17Z
  TYPE: FACT
  CLAIM: Philosophy<->code comparison verdict. The persistence/ code MEETS the philosophy's GOALS
    (custody-at-bind, JSON-adapter persistence, conduit-snapshot reload, hydrate/unfold) via a
    DIFFERENT mechanism than the philosophy's named STRUCTURE. Philosophy = event/transaction-
    sourced (MR emits stream/version/head transactions) + loader chain (bootstrap_manifest ->
    crystal_loader -> synthetic_module_loader -> bootstrap_loader) + crystal_analysis save-time
    facts. Code = snapshot digital-twins + replace-on-emit + journal + checkpoint-delta-fold +
    RestoreEngine public-verb replay. The loader chain is ABSORBED into
    restore_engine._rebuild_synthetic_world; crystal_analysis facts are ABSORBED into SpellCrystal's
    own dependency walk; conduit snapshots = formations. So the five dead dirs are the philosophy's
    abandoned skeleton, not missing features. MR is the one genuine gap, stubbed on BOTH ends:
    record = MutationResearchCrystal Phase A (config/activation only; composition = Phase B/P5
    deliberately absent); restore = MR "reported not restored, too new".
  EVIDENCE:
  - src/melder/crystallizer/persistence/crystals/mutation_research_crystal.py:13-24
  - src/melder/crystallizer/persistence/restore_engine.py:747-767
  - src/melder/crystallizer/persistence/crystals/mutation_research_crystal.py:40-62
  IMPACT: MR persistence should follow the CODE's twin model, NOT the philosophy's
    transaction/loader model: build MR composition objects -> extend MutationResearchCrystal Phase
    A->B to carry them -> MR emits its twin (the profile already holds the singleton MR slot) ->
    add a real _replay_mutation_research restore stage (today it only reports). That is the
    evidenced plug-in seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-09T23:06:39Z
  TYPE: FACT
  CLAIM: SpellCrystal read in FULL. It covers the import/dependency-edge/classification/custody
    + bind-signature part of crystal_analysis (transitive AST import walk with cycle protection,
    relative-import resolution, synthetic-source harvest) but genuinely does NOT cover: EXPORT
    SURFACE (imports only, no exports/__all__), an explicit LOAD-ORDER / dependency-view artifact
    (direct edges only; order deferred to restore heuristics), SITE-PACKAGE distribution
    name/version provenance, binary/non-source dependency depth, and dynamic/runtime imports.
    User's doubt was correct. Full gap map (this + MR Phase B + asset/env unbuilt + engine stubs)
    captured in the new artifact.
  EVIDENCE:
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:1288-1405
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:1150-1210
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:1620-1681
  - artifacts/2026-07-08_crystallizer_persistence_gaps_and_remaining_work.md:1-1
  IMPACT: The MR impact engine (blast-radius) needs export-surface capture, which is unbuilt -
    that gap is on the MR critical path, not cosmetic.
  NEXT: On user go, start MR Phase B (composition objects + MutationResearchCrystal A->B seam).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-09T23:06:39Z
  TYPE: BLOCKER
  CLAIM: 5 dead-dir removal is BLOCKED from the agent sandbox: bash `rm` returns "Operation not
    permitted" on the mount (touch succeeds, rm does not) and the file tools expose no delete
    primitive. Nothing was deleted; real src/melder/mutation_research is intact. User must run
    the `git rm -r` (gap-doc section 5) on the host.
  EVIDENCE:
  - artifacts/2026-07-08_crystallizer_persistence_gaps_and_remaining_work.md:100-115
  IMPACT: Directory cleanup is user-side; the agent cannot complete it in this environment.
  NEXT: User runs the git rm; then the cleanup item closes.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-11T19:20:00Z
  TYPE: FACT
  CLAIM: FINAL VERIFICATION READ (owner-directed: "go read the mutation research
    stuff in crystallizer"; lane inherited by mutation_0 - same MR lineage,
    mutation_research_0's session ended). The crystallizer<->MR loop this task
    set out to LOCATE is now BUILT and verified coherent end to end:
    (1) MutationResearchCrystal Phase B rides composition_payload exactly as
    emitted by describe_research_composition (crystal contract read in full);
    (2) MRCompositionStrategy (preflight row 9) validates the EXACT
    describe_composition shape - {organization{lanes,residence},journal,
    network_snapshot_shas,network_versioner} keys cross-checked against
    research_set.py:1294-1300 + :265-269 + from_payload :1347-1358 - blockers
    on unparseable shapes only, warnings on lane/residence disagreement,
    legacy spell_sha keys tolerated with the named pre_vocabulary_sweep_payload
    warning; (3) _replay_mutation_research is a REAL build stage (restore_
    engine.py:887-978): reload verb w/ per-key shortfalls -> hosted accessor
    (never free-constructed) -> deactivate-if-active (truthful recorded act) ->
    activate(hydrate_from_record=False; engine owns folded truth) ->
    load_recorded_composition wholesale + re-emit -> disabled later-wins
    replays activate-then-deactivate; cleaned/pre-Phase-B lanes stay honest
    shortfalls. EVERY open item in this task is resolved: the 22:37Z
    DECISION_REQUEST (EMIT-model sanction) was answered by the owner-accepted
    program built ON it + the V3 decomposition reconciling philosophy<->code;
    the 23:06Z BLOCKER (dead-dir removal) is MOOT - those dirs became the REAL
    V3 subsystems (crystal_loader_system/crystal_analysis/asset_management);
    the export-surface gap landed as ExportSurfaceStrategy (melder_0 S1);
    MR Phase B + the build stage are owner-run green and closed. MAILBOX
    CONSUMED on inheritance (melder_0 -> mutation_research_0, 12:05Z NOTICE):
    BootMediator->LoadAdmission rename is informational only - this ticket's
    notes describe the same seams under the old name; the S1 formation-load
    additions left the MR analyze_payload seam untouched (verified: my program
    never depended on the renamed surface).
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:887-978
  - src/melder/crystallizer/crystal_analysis/preflight/mutation_research_composition_strategy.py:108-165
  - src/melder/mutation_research/research_set/research_set.py:1294-1300
  IMPACT: The task's deliverable (evidence-backed mechanics + the MR seam) not
    only stands - the seam it identified became the shipped, closed MR
    program. Nothing remains open in this lane.
  NEXT: closure walk (owner directive).
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Closure Walk (acceptance criteria vs delivered)
- Crystallizer mechanics captured with evidence: DONE (root API, custody,
  persistence spine, restore engine, synthetic modules - notes 22:10Z-23:06Z;
  final verification 19:20Z against the post-decomposition V3 tree).
- MR persistence/hydration seam identified: DONE - and consumed: the Phase A->B
  seam this task named became MutationResearchCrystal.composition_payload +
  load_recorded_composition + the real build stage, all owner-run green.
- Doc drift flagged: DONE (drove the doc-residue surgery + V3 promotion lanes).
- Escalations resolved: DECISION_REQUEST answered by the sanctioned V3
  program; BLOCKER mooted by the decomposition making the dirs real.
- Artifact retained: artifacts/2026-07-08_crystallizer_persistence_gaps_and_
  remaining_work.md (retain_as_reference; its gap map is now a historical
  record of what got built).
- Owner acceptance: closure directive 2026-07-11 ("close any epics you
  finished" / earlier "close any tickets you properly managed").

## Context / Handoff Summary
Investigation lane (mutation_research_0) to understand the crystallizer before MR build work.
FINDINGS: crystallizer.py (root, 1783 LOC) read in full - it is a mature EMIT/record/
checkpoint/cache/external-upload/restore engine that already implements V2 "Custody + Unfold"
(SpellCrystal custody at bind; profiles; PersistenceCrystal chain-fold; restore_engine unfold
via public-verb replay; ExternalPersistenceManager adapter; formations; PersistenceAnalyzer).
The crystallizer<->MR seam is explicit and staged: MutationResearchCrystal is "Phase A"
(config/activation only); MR git-composition persistence is "Phase B / persistence epic P5"
and unbuilt - that is the MR entry point. Docs (src_architecture/components) are structurally
stale (crystal_loader/analysis/asset_management empty; persistence/ subtree is the real
engine). Directly overlapping active lane: melder_0 `agent_object_persistence_loop` epic
(codegen->synthmodule->bind->crystal loop, M1-M7). NEXT: read that epic + `src/melder/
mutation_research/**`, then scope MR build story 1 with the user. Not yet read: persistence_
system.py, restore_engine.py, synthetic_module.py, persistence_profile.py, external_
persistence_manager.py, per-type crystals, analysis strategies.
