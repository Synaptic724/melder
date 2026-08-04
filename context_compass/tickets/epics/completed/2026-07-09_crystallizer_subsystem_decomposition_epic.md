# Epic: Crystallizer subsystem decomposition (record / loader / assets / analysis)

- Completed: 2026-07-10T09:10:00Z
- Summary: the persistence god object decomposed into the V3 subsystem model
  (PersistenceSystem = ledger | AssetManagementSystem = bytes at rest |
  CrystalLoaderSystem = mediated unfold, + package-level crystals/ vocabulary
  + the crystal_analysis service). Six stories, all owner-validated (614/614
  full tree); facade surface byte-compatible (additive keys only); verdict
  law live (blockers refuse pre-replay - proven by the SHA-refusal); physical
  fingerprints + export surfaces + load order recorded per analysis; docs +
  graph current; patch lane retired. Owner accepted 2026-07-10 ("I see its
  all fixed up... close the epic").

## Metadata
- Epic ID: EPIC-2026-07-09-crystallizer-subsystem-decomposition
- Status: done
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-09T23:25:00Z
- Updated: 2026-07-09T23:25:00Z
- Target Window: 2026-Q3
- Related Program/Initiative: crystallizer persistence & restore program
  (successor to EPIC-2026-07-03-crystallizer-bootstrap-checkpoint)

## Problem / Opportunity
The persistence program (2026-07-03 through 2026-07-08) built the right ENGINE inside the
wrong TOPOLOGY. `PersistenceSystem` accreted into a god object carrying four separable
concerns behind ~45 public verbs:

1. RECORD (its true job): profiles, twins, journal, tombstones, state switches,
   checkpoint minting, ledger retention, chain verification.
2. ASSETS: `CrystallizerCache` ownership, flush/reload traffic, formation file storage,
   and the `ExternalPersistenceManager` upload hooks threaded through flush paths.
3. LOADING: `load_checkpoint`, `restore_formation`, `load_formation_record`,
   `checkpoint_replay_data` — with no durable owner of load state anywhere.
4. PACKAGING: formations save/list.

Simultaneously `SpellCrystal` owns ~500 lines of embedded analysis (classification,
source resolution, transitive AST walk, synthetic harvest) welded into its constructor,
so analysis can only run against a LIVE spell — structurally unusable for the
MutationResearch impact engine, which must re-analyze RETAINED historical versions.

The April philosophy planned this separation (`crystal_analysis/`, `crystal_loader/`,
`asset_management/` package shape); V2 re-blessed it; the build inhabited none of it.
Owner verdict 2026-07-09: the old design's boundaries were right, the new engine's
semantics are right — migrate to the boundaries without losing the semantics. Owner
explicitly framed the driver: bite-sized subsystems are what future AI agents can hold
in bounded context; the god object is not maintainable.

Confirmed coverage gaps riding along (evidence in the gap-map artifact):
- Physical (file-backed) modules: analyzed but NOT custodied — no retained source text,
  no module-text SHA256, so on-disk drift since a checkpoint is UNDETECTABLE.
- Export surface: captured for nobody (MR impact engine blocker).
- Load order: direct edges only; restore fakes ordering with dot-depth heuristics.
- Site-package provenance: path classification only, no distribution name/version.

## MRP Alignment (Most Reasonable Product)
The record/emit model (twins, journal, fold, all-or-nothing restore, R-A covenant) is
proven and survives unchanged. What is NOT durable is the topology: every new lane
(MR Phase B is queued next) would deepen the god object and double future migration
cost. Decomposing now, before MR lands on these seams, is the smallest change that
makes the core safe to build on. MRP, not MVP: facades stay stable, semantics stay
identical, every tranche independently green.

## Ticket Contract
- ENTRY_GATE: this epic routed on `attention_board.md`; per-story patch docs
  (architecture patch + component patches) exist and are ticket-linked BEFORE that
  story's implementation begins (patch_framework_gating.md applies — component
  boundaries move).
- EXECUTION_BOUNDARY: `src/melder/crystallizer/**` plus the import sites of moved
  modules (11 src + 12 test files for `persistence.crystals`; test tree re-points per
  tranche). NO public facade signature changes on `Crystallizer`. NO semantic changes
  to record/fold/replay except where a story explicitly names one (admission gate,
  physical SHA).
- DEPENDENCIES: canonical philosophy artifacts (below); gap-map artifact; current
  C-docs sections "Crystallizer Persistence & Restore" / "Persistence & Restore
  Architecture"; owner rulings in Decision Log.
- EXIT_GATE: all five stories accepted by owner-run 3.14t green + acceptance walks;
  C-docs and src_graph promoted; board/artifact closure sync complete.
- FAILURE_ESCALATION: any lock-order ambiguity across new seams, any facade signature
  break, any fold/replay behavior delta discovered mid-move -> CONFLICT/BLOCKER note +
  stop; scope growth beyond the boundary -> DECISION_REQUEST before continuing.

## Goals (Outcomes)
- `PersistenceSystem` = ledger only: profiles, twins, journal, checkpoint minting,
  retention, chain verify, insert sink. No disk, no DB, no engines, no formations
  storage.
- `AssetManagementSystem` (new, `asset_management/`): all bytes-at-rest — cache files,
  formation files, ExternalPersistenceManager custody, flush local-then-upload, reload
  cache/external feeding the record's insert sink, cache-file retention.
- `CrystalLoaderSystem` (new, `crystal_loader_system/`): the unfold owner — durable
  load state (last report, shortfalls, identity map), `BootMediator` admission
  (LoadPlan -> strategy verdicts -> refuse/proceed), `RestoreEngine` as dumb executor,
  `CrystallizerBootstrap` thinned to a fluent wrapper over mediator verbs.
- `crystal_analysis/` (inhabited): standalone `CrystalAnalyzer` + `CrystalAnalysisResult`
  running against a live Spell OR a retained payload; custody strategies per authority
  class; fact strategies (imports/from-imports moved; export_surface and
  dependency_view/load-order NEW); preflight strategies relocated here.
- `crystals/` moved to crystallizer level: the twin vocabulary is package-level, not
  record-internal (8 of 11 src importers are runtime units outside crystallizer).
- SpellCrystal (and every crystal) = pure data CARRIER holding one analysis result;
  crystals never own analyzers, maps, or strategies.
- Physical modules gain bind-time module-text SHA256 fingerprints (drift detection).

## Non-Goals (Explicit Exclusions)
- MR Phase B (composition persistence/hydration) — separate successor lane.
- Full physical source-text RETENTION — deferred owner decision (fingerprint only now).
- Environment/asset layer (uv.lock capture/validation, env gate) — open scope decision
  (gap map section 3); NOT built here.
- Facade vocabulary renames on `Crystallizer` public surface.
- Any change to emission factors, twin shapes, journal semantics, or checkpoint sealing.

## Scope Boundaries
- In scope: `src/melder/crystallizer/**`; import-site sweeps for moved modules;
  `tests/unit/melder/crystallizer/**` + crystallizer integration tests re-pointing;
  patch docs; C-doc/graph promotion at close.
- Out of scope: all other `src/melder` subsystems (their twin-import lines change
  mechanically in S2, nothing else); MR runtime; Nexus/AR behavior.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner approved the target architecture and ordered the epic
  ("its the right move to make", 2026-07-09); tranche A opens next.

## Success Metrics
- PersistenceSystem public verb count drops from ~45 to the ledger set (~28).
- `spell_crystal.py` loses the embedded analysis (~500 lines relocate).
- Zero `persistence.crystals` import paths remain (all `crystallizer.crystals`).
- Every load path (checkpoint, formation, bootstrap) passes through BootMediator
  admission; `with_preflight_gate` is absorbed, not duplicated.
- Owner-run 3.14t full tree green after each tranche.

## Requirements (Functional + Non-Functional)
- Edge law (acyclic): anything may import `crystals/`; crystal_analysis reads crystals;
  loader reads record + invokes analysis; assets read record + call its insert sink;
  the record calls NOBODY.
- Lock law: preserve the one-way order (emitters -> crystallizer -> subsystem ->
  profile); no subsystem-to-subsystem lock nesting; document per-seam ordering in
  docstrings (Threading sections).
- Flush contract: seal (ledger) then ship (assets); cache-write failure semantics and
  lenient-upload accounting documented as the cross-subsystem transaction law.
- Admission verdict policy: blockers REFUSE with teach-grade errors; warnings PROCEED
  and ride the report (owner may add a strictness knob later — not in first cut).
- R-A covenant preserved: crystallizer-off worlds stay byte-identical.
- Restore engine all-or-nothing + shortfall honesty semantics unchanged.
- Synaptic code law throughout: rich contract docstrings, cleanup-after-__init__
  children-first del posture, Optional/Union typing, TYPE_CHECKING-first, no module
  constants, no print, methods ~50-60 LOC.

## Constraints / Assumptions
- Sandbox is Py3.10; melder imports only run on user 3.14t. Compile floor = py_compile
  on fresh replicas (replica-rot verification via file-tool Read where needed).
  Execution reports are "Not run." until owner runs.
- All writes to existing files are FILE-TOOL-ONLY; bash mv allowed for file moves.
- One-shot file writes stay under 900 LOC; big files grow iteratively.
- Each story sized to be completable (and green) inside one agent session.

## Dependencies / External References (the reading set behind this epic)
Philosophy / design canon (read in full 2026-07-09):
- `artifacts/2026-04-26_crystallizer_philosophy.md` — origin of the package shape
  (crystal_analysis / asset_management / crystal_loader), bootstrap-manifest restore
  order, asset model + authority classes, adapter-driven persistence, env-vs-world
  truth split.
- `artifacts/2026-07-01_crystallizer_philosophy_v2.md` — three sharpened duties
  (custody at bind; save-time facts + unfold order; MR hydration), loader-chain build
  order; names `crystal_analysis/strategies/` as exactly the facts service.
- `artifacts/2026-07-01_mutation_research_philosophy_v2.md` — MR as consumer: impact
  engine reads crystal-custodied source for ANY version (file-born included), needs
  export surface + standalone re-analysis; kill list; build order.
- `artifacts/2026-07-08_crystallizer_persistence_gaps_and_remaining_work.md`
  (mutation_research_0) — evidence-backed gap map: SpellCrystal analyzer gaps (1.1
  export surface, 1.2 load order, 1.3 provenance, 1.6 no standalone analyzer), MR
  Phase B seam, asset/env scope question, engine first-cut tolerances, dead-dir
  verdict.
System docs (chunk-read in full 2026-07-09):
- `system_docs/src_architecture.md` — canonical boot order + "Persistence & Restore
  Architecture" (EMIT/restore invariants, durability layering).
- `system_docs/src_components.md` — "Crystallizer Persistence & Restore" (ownership
  hierarchy, record model, reload lanes, EPM, bootstrap).
Source evidence (verb inventory + analysis regions):
- `src/melder/crystallizer/persistence/persistence_system.py:171-1471` (4-concern verb
  inventory: record 195-557/1019-1127, assets 573-662/887-1018, loading 750-861/
  1181-1298, chain 1299)
- `src/melder/crystallizer/persistence/crystals/spell_crystal.py:1150-1620` (embedded
  analysis: classify 1150, source resolution 1212-1261, AST extraction 1288, walk
  1473-1576, synthetic harvest 1578)
- `src/melder/crystallizer/persistence/restore_engine.py` (stage machine, fold,
  preflight seam), `crystallizer_bootstrap.py` (verify gate + preflight knob to be
  absorbed), `crystallizer_cache.py`, `external_persistence_manager*.py`,
  `persistence/analysis/*` (7 strategies + analyzer to relocate).
Prior program tickets (context trail):
- `tickets/stories/completed/2026-07-07_restore_engine_load_checkpoint_story.md`
- `tickets/stories/2026-07-07_formations_and_persistence_analyzer_story.md`
- `tickets/stories/2026-07-07_loader_chain_m3_synthetic_restore_story.md`
- `tickets/stories/2026-07-07_persistence_manager_story.md`
- `tickets/epics/2026-07-03_crystallizer_bootstrap_checkpoint_epic.md`

## Milestones (Track Progress)
- [x] M-A: crystal_analysis live — analyzer + result + custody/fact strategies,
      SpellCrystal slimmed to carrier, physical SHA landing, suite green.
      (S1 sentinel green 2026-07-10.)
- [x] M-B: crystals/ at crystallizer level + asset_management extracted —
      PersistenceSystem free of disk/DB, suite green. (S2+S3 green.)
- [x] M-C: crystal_loader_system live — mediator admission on every load path,
      bootstrap thinned, durable load state, suite green. (S4 green; verdict
      law proven live by the SHA-refusal.)
- [x] M-D: docs/graph promoted (both C-docs current; graph 520 nodes/965
      edges, zero stale paths, readable regenerated + validated); patch lane
      -> completed/; philosophy drift note in the S5 story. Epic closure walk
      PREPARED — awaiting owner acceptance (614/614 full tree).

## Stories (Required to Complete)
- [ ] Story: STORY-2026-07-09-crystal-analysis-extraction — stand up
      `crystal_analysis/` for real: `CrystalAnalyzer` + `CrystalAnalysisResult`;
      custody strategies (synthetic / user_source / site_package / binary+unknown);
      fact strategies (import_statement + from_import_statement = moved logic;
      export_surface + dependency_view/load-order = NEW); SpellCrystal delegates and
      stores the result (analysis logic leaves the constructor); physical module-text
      SHA256 fingerprint captured at bind via the user_source custody strategy;
      analyzer runs from a live Spell OR a retained payload. Tests: strategy units +
      SpellCrystal contract updates + fingerprint drift regression.
- [ ] Story: STORY-2026-07-09-crystals-vocabulary-move-up — `git mv`
      `persistence/crystals/` -> `crystallizer/crystals/` (+ `recorded_unit_state.py`);
      mechanical import sweep (11 src + 12 test files); zero behavior change;
      grep gate proves no `persistence.crystals` path survives.
- [ ] Story: STORY-2026-07-09-asset-management-extraction — `asset_management/` with
      `AssetManagementSystem`; move `crystallizer_cache.py` + EPM (+configuration);
      extract flush/reload/upload/formation-file verbs from PersistenceSystem;
      Crystallizer facades reroute; flush contract documented; ledger exposes
      cached-item forms + insert sink only.
- [ ] Story: STORY-2026-07-09-crystal-loader-system-boot-mediator —
      `crystal_loader_system/` with `CrystalLoaderSystem` (durable load state),
      `BootMediator` (plan -> strategies -> verdict -> engine), `LoadPlan` (declarative
      needs + world/frame/conduit scope), move `restore_engine.py` +
      `crystallizer_bootstrap.py` (thinned to `bootstrap_loader.py`); preflight
      strategies relocate to `crystal_analysis/preflight/`; `with_preflight_gate`
      absorbed into standard admission; extract load verbs from PersistenceSystem.
- [ ] Story: STORY-2026-07-09-test-repoint-sweep — after S4: one mechanical import
      re-point sweep across the broken bulk test tree against the FINAL module layout;
      owner-run full 3.14t tree green gates S5. (Sentinel set stays green per tranche
      throughout: whole-system restore, profile-cache round trip, formation round
      trip, pod bootstrap, analyzer units.)
- [ ] Story: STORY-2026-07-09-decomposition-doc-graph-promotion — merge patch docs
      into `src_components.md` / `src_architecture.md`; regenerate `src_graph.json`
      + readable per canonical recipe; record philosophy-drift closure note (which
      April/V2 intents are now inhabited, which remain open: env layer, text
      retention, MR Phase B).

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: author per-story patch docs under
      `system_docs/patches/active/crystallizer_decomposition_2026_07_09/` before each
      story's implementation (entry gate).
- [ ] Task: maintain a running facade-parity grep gate (no `Crystallizer` public
      signature changes) across all tranches.
- [ ] Task: per-tranche owner-run 3.14t validation checkpoint before the next tranche
      opens.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Crystallizer owns three same-rank children (PersistenceSystem | CrystalLoaderSystem |
  AssetManagementSystem) + the crystal_analysis service + package-level crystals/.
- PersistenceSystem contains zero disk/DB/engine/formation-storage code.
- No crystal class contains analysis logic; all analysis flows through
  CrystalAnalyzer; results are carried as detached payloads.
- Every load path passes BootMediator admission; blockers refuse with teach-grade
  errors; reports land in durable load state.
- Physical modules carry bind-time SHA256 fingerprints; preflight can flag on-disk
  drift.
- Public facade surface byte-compatible for callers; full owner-run 3.14t tree green;
  C-docs + graph current.

## Risks / Mitigations
- Import-sweep breakage across 23+ files -> per-tranche compile floor + grep gates +
  owner-run tree before next tranche.
- Lock-order regressions across new seams -> document per-seam order; no
  subsystem-to-subsystem locking; review at story exit gates.
- Cross-subsystem flush semantics (seal ok / ship fails) -> explicit contract in the
  asset story's patch doc; lenient-upload accounting preserved.
- Write-fault history (truncations on big files) -> file-tool-only writes, iterative
  growth, line-count verification after moves.
- Hidden coupling: fold/stage branches reference twin kinds — the twin-kind change
  axis stays cross-boundary by nature; document the "adding a twin kind" checklist in
  C-docs instead of pretending topology removes it.
- Context exhaustion mid-tranche -> stories sized for one session; notes + board
  updated before any compaction risk.

## Validation / Test Approach
- Per story: unit suites move/extend with the code; py_compile floor in-sandbox
  (replica-rot-verified); execution truthfully reported "Not run." until the owner
  runs 3.14t; owner-run green gates tranche progression.
- Regression tests named for symptoms: physical-drift fingerprint mismatch; admission
  refusal on blocker verdict; facade-parity for rerouted verbs; reload-through-assets
  round trip; formation restore through mediator.
- Integration: existing restore/bootstrap/formation round-trip suites re-pointed and
  kept green; one new pod-boot test proving bootstrap-through-mediator parity.

## Rollout / Adoption Plan
- Tranche-ordered (S1 analysis -> S2 vocabulary/assets -> S4 loader -> S5 docs), each
  independently shippable and owner-validated; no dual-write or compatibility shims —
  internal reroutes land atomically per tranche behind the stable facade.

## Open Questions
- Full physical source-text retention (custody beyond fingerprint): owner decision,
  affects MR checkout of file-born versions. Deferred; fingerprint ships now.
- Environment/asset layer (uv.lock validation, env gate at admission): in or out of
  scope for asset_management, ever? (gap map section 3.)
- Mediator strictness knob (treat warnings as refusals): deferred until a real
  consumer asks.

## Decision Log
- 2026-07-09 owner: old design's boundaries right, engine semantics right — migrate;
  "bite sizes" for future agents is the driver; "it won't be simple but its the right
  move to make".
- 2026-07-09 owner: PersistenceSystem name stays; DB ops and loader ops move OUT.
- 2026-07-09 owner: small BootMediator manages bootloader transactions and "maps if
  the strategies will work" (admission = strategy verdicts).
- 2026-07-09 owner: crystals never own analyzer maps/strategies; crystal_analysis dir
  (kept on disk) hosts all crystal analysis; other crystal kinds use the same service.
- 2026-07-09 owner: dir names `crystal_loader_system/` + `asset_management/`;
  dead scaffold dirs deleted by owner (crystal_analysis retained).
- 2026-07-09 melder_0 (owner accepted): crystals/ moves to crystallizer level —
  8/11 src importers are external runtime units; vocabulary is package-level.
- 2026-07-09 melder_0 rec (unopposed): verdict policy blockers-refuse /
  warnings-proceed+report; physical SHA now, text retention deferred; export_surface
  + load_order ride S1 as the only new capability in the migration.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-07-09_crystallizer_philosophy_v3.md (CANONICAL design anchor for
    this epic; retain_as_reference)
  - system_docs/patches/completed/crystallizer_decomposition_2026_07_09/ (all 5
    patch docs; promoted into the C-docs and retired 2026-07-10)
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: story closures merge durable deltas into C-docs; patch lane moves
  to completed/ at epic close; the V3 philosophy artifact is retained as reference.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-07-09T23:25:00Z
  TYPE: PLAN
  CLAIM: Epic opened on owner approval after a multi-turn design debate. Verdict
    reached: the persistence program built correct semantics (EMIT/fold/all-or-nothing)
    inside an accreted god object; the April/V2 philosophy boundaries are correct and
    get inhabited via 5 stories (analysis extraction -> crystals move-up -> assets
    extraction -> loader+mediator -> doc/graph promotion). Coverage verdict recorded:
    synthetic custody complete; physical analyzed-not-custodied (no SHA — drift
    undetectable); export surface + load order missing (MR blockers). Owner deleted 4
    dead scaffold dirs; crystal_analysis kept as the analysis home.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_system.py:573-1298
  - src/melder/crystallizer/persistence/crystals/spell_crystal.py:1150-1620
  - codex/context_compass/artifacts/2026-07-08_crystallizer_persistence_gaps_and_remaining_work.md:28-76
  - codex/context_compass/artifacts/2026-07-01_crystallizer_philosophy_v2.md:52-64
  IMPACT: MR Phase B lands on clean seams instead of the god object; future agents
    onboard subsystem-sized surfaces.
  NEXT: author the S1 patch docs (architecture patch + component patch for
    crystal_analysis/SpellCrystal), then open the S1 story ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-09T23:30:00Z
  TYPE: FACT
  CLAIM: Crystallizer Philosophy V3 authored at owner direction as the CANONICAL modern
    philosophy (supersedes V2/April where conflicting; duties and thesis intact). It
    codifies the subsystem model this epic builds: five identities (crystals vocabulary,
    ledger, asset_management, crystal_loader_system + BootMediator, crystal_analysis),
    the cross-subsystem laws (edge/lock/facade/bite-size/twin-kind honesty, flush
    contract, verdict law), what stays true from April/V2, and a 7-step build horizon
    (this epic -> MR Phase B -> impact engine -> physical custody maturity -> load-scope
    maturity -> env-layer decision -> first-party adapter package). Artifact-board row
    added; artifact linked from this epic.
  EVIDENCE:
  - codex/context_compass/artifacts/2026-07-09_crystallizer_philosophy_v3.md:1-186
  - codex/context_compass/artifact_board.md:40-41
  IMPACT: Future lanes (S1-S5, MR Phase B, impact engine) design against ONE current
    document instead of reconciling April/V2/code drift; the bite-size law is now a
    named, permanent design force.
  NEXT: author the S1 patch docs under
    system_docs/patches/active/crystallizer_decomposition_2026_07_09/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-10T00:10:00Z
  TYPE: DECISION
  CLAIM: Test strategy ruled (owner accepted melder_0's sentinel proposal after
    proposing full breakage): bulk test breakage is ACCEPTED for the whole epic - no
    per-tranche re-pointing of the ~100+ unit files; ONE mechanical re-point sweep
    story (S-test, added to the story list) runs after S4 against the final layout.
    GUARDRAIL: a sentinel set stays green per tranche to catch SEMANTIC drift early -
    whole-system restore integration, profile-cache round trip, formation round trip,
    pod bootstrap, analyzer units. Owner per-tranche runs shrink to the sentinel set;
    one full-tree run gates S5. ALSO: patch gate satisfied for S1 - architecture
    patch + component patches (crystal_analysis, spell_crystal) authored; S1 story
    opened (STORY-2026-07-09-crystal-analysis-extraction) with build order T1-T9.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/crystallizer_decomposition_2026_07_09/architecture_patch.md:1-999
  - codex/context_compass/tickets/stories/2026-07-09_crystal_analysis_extraction_story.md:1-999
  IMPACT: Semantic regressions surface per tranche instead of five stories deep;
    import churn is paid once.
  NEXT: implement S1 T1 (crystal_analysis_result.py).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work walkthrough shared with user (closure walk: all 6 stories vs
      acceptance criteria + live end-state tree proof, 2026-07-10).
- [x] Acceptance criteria confirmed by user (owner: "ok cool yeah I see its
      all fixed up... close the epic and lets move on", 2026-07-10; full
      tree 614/614 owner-run).
- [x] Applicable anti-pattern checks are clear or escalated with evidence
      (facade surface byte-compatible additive-only; every story closed on
      story-level evidence; patch docs preceded every tranche).

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.
- [ ] No implementation before that story's patch docs exist and are linked.
- [ ] No facade signature changes hiding inside "mechanical" moves.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Owner-approved decomposition of the crystallizer persistence god object into:
PersistenceSystem (ledger only) | AssetManagementSystem (bytes at rest) |
CrystalLoaderSystem (BootMediator admission + LoadPlan + RestoreEngine + thinned
bootstrap) + crystal_analysis (standalone analyzer, custody/fact/preflight strategy
families) + crystals/ promoted to package level. Five stories, tranche-ordered, patch
gates per story, facade surface frozen, owner-run 3.14t green gates each tranche.
Physical SHA fingerprinting is the one new capability riding tranche A alongside
export_surface + load_order fact strategies. Next action: S1 patch docs, then the S1
story ticket.
