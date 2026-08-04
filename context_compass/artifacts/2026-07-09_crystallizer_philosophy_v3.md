# Crystallizer Philosophy V3 (The Subsystem Model)

## Metadata
- Artifact ID: ART-2026-07-09-crystallizer-philosophy-v3
- Parent Ticket: EPIC-2026-07-09-crystallizer-subsystem-decomposition
- Status: active
- Supersedes: ART-2026-07-01-crystallizer-philosophy-v2 (where conflicting; duties
  intact), ART-2026-04-26-crystallizer-philosophy (where conflicting; thesis intact)
- Created: 2026-07-09T23:30:00Z
- Updated: 2026-07-09T23:30:00Z

## Purpose
Define the future of the crystallizer after the 2026-07 persistence program proved the
engine and the 2026-07-09 owner review rejected its topology. V2's three duties stand.
April's thesis stands. What changes is the SHAPE: the crystallizer becomes a thin root
over four bounded subsystems and one shared vocabulary, sized so that a future agent can
hold any one subsystem's whole contract in bounded context. Where earlier documents
disagree with this one, THIS document wins.

## North Star (Unchanged Destination, Sharper Road)
A kube container holds a project and a small bootstrap. On start, the bootstrap asks the
loader for the world: the mediator builds a plan, the strategies vouch for it or refuse
with reasons, and the engine unfolds crystals into synthetic modules, worlds, frames, and
configuration - the checkpointed application is simply UP. From there agents build at
Nexus workstations; every bound object is custodied, every version is analyzable, every
change is mappable before it commits (MR's impact engine reading crystal custody).
Crystallizer's contribution is custody and unfold - retained truth in, living worlds out.

## Core Thesis
Crystallizer is the source-truth, persistence, and recovery ROOT for managed software
artifacts - the saving tool and the regeneration system. It is not a second runtime, not
a package manager, not a DB framework, not an analyzer of change (MR judges change;
Sentinel judges behavior), and not the owner of MutationResearch graph semantics.

The 2026-07 lesson, stated as law: the FACADE may be wide, but it must be thin. No member
object may be wide AND deep. `PersistenceSystem` accreting record + disk + DB + loading
behind ~45 verbs was the failure mode; the subsystem model below is the correction.

## The Five Identities

### 1. `crystals/` - the vocabulary (package level)
Pure-data twin carriers: aether, crystallizer, nexus, mutation_research, frame,
spellbook, conduit, spell_index, contract, cluster, spell custody, recorded unit state.
- CARRIER LAW: crystals carry recorded truth and analysis RESULTS. They never own
  analyzers, strategy maps, or walk logic. A crystal is something you read.
- They live at crystallizer level because they are the language every emitter in melder
  speaks; runtime units import the vocabulary without touching any subsystem's insides.

### 2. `persistence/` - the record (PersistenceSystem, the ledger)
The event-sourced spine, kept exactly as proven: structural units PUSH twins at their
own confirmation points; profiles journal insertion order; replace-on-emit custody;
checkpoint windows seal deltas into PersistenceCrystals; FIFO ledger retention; chain
verification; one insert sink for reloads; every snapshot self-describing (the policy
twin rides every seal).
- LEDGER LAW: the record is boring. It owns in-process truth ONLY - no disk, no DB, no
  engines, no formations storage. It calls nobody; everything calls it.
- R-A covenant stands: recording off means byte-identical runtime behavior.
- Records carry plain values; callables appear as presence flags and reload as
  code-participation reports.

### 3. `asset_management/` - bytes at rest (AssetManagementSystem)
Everything durable that is not in-process truth: local cache files
(`__crystallizer_cache__/{profile}/...`), formation files, cache-file retention, and the
ExternalPersistenceManager seam (user-supplied upload/download/list callables - users
own their SQL bootstrap and their secrets; a first-party adapter package may PROVIDE
callables later without entering the core).
- FLUSH CONTRACT: seal (ledger) then ship (assets) - local cache first, then lenient
  uploads that count failures without breaking the seal lane.
- Reloads (cache or external) produce cached items and feed the record's insert sink.
- Durability layering is explicit: ledger (bounded FIFO) -> cache (bounded FIFO) ->
  user DB (unbounded, explicitly the user's opt-in and operational responsibility).

### 4. `crystal_loader_system/` - the unfold (CrystalLoaderSystem + BootMediator)
Every load is a mediated boot transaction. The mediator is deliberately small - an
admission pipeline, not a lock plane:
- PLAN: a declarative LoadPlan of what this restore needs (crystals, books, frames,
  synthetic modules) and at what SCOPE (world | frame | conduit). Plans are inspectable
  before anything activates.
- MAP: the strategy set runs against the plan - "will this load work?" answered before
  execution. World loads run the full set; scoped loads run scope-appropriate subsets;
  host-precondition strategies (is the target frame live and dynamic, do binding keys
  collide) join the same registry as they land.
- VERDICT LAW: blockers REFUSE with teach-grade errors naming what is unbuildable;
  warnings PROCEED and ride the report. Admission is the standard path, not an opt-in.
- EXECUTE: the RestoreEngine stays the dumb executor - canonical stage order
  (Aether|Utility -> Crystallizer -> MR -> Nexus -> Frame -> Spellbook -> Conduit|Ward),
  all-or-nothing reverse teardown, fresh ULIDs always (spell SHAs never translate),
  re-emission into the fresh active profile intended, honesty shortfalls never silent.
- REMEMBER: the loader owns durable load state - last report, identity map, shortfalls.
  "What did we last load" has an owner.
- The bootstrap is a thin fluent wrapper over mediator verbs for pod restarts.

### 5. `crystal_analysis/` - the shared analysis service
One standalone CrystalAnalyzer producing detached CrystalAnalysisResult payloads,
runnable against a LIVE spell or a RETAINED payload (historical versions analyze without
a living object). Three strategy families:
- CUSTODY (per authority class): synthetic = full text + SHA custody, rebuildable;
  user_source = module-text SHA fingerprint at bind (drift detection), text retention a
  deliberate future decision; site_package = distribution name + version provenance;
  binary/unknown = honest leaf law (recorded, never walked).
- FACTS (per pass): import/from-import walks, export surface (what a module exposes -
  MR's blast-radius prerequisite), dependency view / topological load order (the crystal
  says its unfold order; restore stops guessing with heuristics).
- PREFLIGHT (restore admission): the bundle-consistency strategies the mediator runs.
Two consumers, one service: loader admission and MR's impact engine. Neither reimplements
the other's analysis.

## The Laws (Cross-Subsystem)
- EDGE LAW (acyclic): anything may import `crystals/`; analysis reads crystals; loader
  reads record + invokes analysis; assets read record + call its sink; the record calls
  nobody.
- LOCK LAW: one-way ordering only (emitters -> crystallizer -> subsystem -> profile);
  no subsystem-to-subsystem lock nesting, ever.
- FACADE LAW: users and agents talk to `Crystallizer` facades; the facade routes and
  never implements.
- BITE-SIZE LAW (the owner's driver, promoted to design force): every subsystem's
  public contract must be holdable by a bounded-context agent in one read. When a
  subsystem's surface outgrows that, it is re-decomposed - the god object is a standing
  failure mode, not a one-time accident.
- TWIN-KIND HONESTY: adding a twin kind legitimately touches record AND loader (record/
  replay are duals). The cost is inherent; it is paid via a documented checklist, not
  hidden by topology claims.

## What Stays True From April / V2
- Bind is the promotion boundary from local construction into durable world truth;
  `sys.modules` publication is never persistence.
- A crystal for every bound object: custody is mandatory at bind, and the impact engine
  must be able to read ANY version's source - codegen-born, file-born, synthetic, mixed.
- Conduit/frame world slices are the honest scoped reload units (formations are that
  promise kept); single spells are not.
- Synthetic modules are first-class: live embodiment, canonical-name activation,
  copy-mode only at bootstrap/rebuild boundaries.
- Persistence stays adapter-driven: crystallizer defines payload shapes; hosts own
  storage and update semantics.
- Environment/package truth stays separate from world/module truth; the loader
  validates, it never becomes a package manager.
- Files are optional projections, never primary truth.

## The Future (Build Horizon, In Order)
1. THE DECOMPOSITION ITSELF (EPIC-2026-07-09): analysis extraction -> vocabulary
   move-up -> assets extraction -> loader + mediator -> doc/graph promotion. Everything
   below assumes these seams exist.
2. MR PHASE B: MutationResearchCrystal grows the composition payload (streams, version
   records, heads, index associations); MR emits at mutation acts; the loader hydrates
   MR's in-memory composition at activation; lifecycle states replay instead of report.
3. THE IMPACT ENGINE (MR-owned, crystallizer-fed): consumes custody + export surface +
   usage-map facts from crystal_analysis and dependency truth from melder's compiler;
   crystallizer never judges the change.
4. PHYSICAL CUSTODY MATURITY: fingerprints (now) -> optional full-text retention
   (dedup by SHA across the record; retained text serves analysis and checkout, restore
   still re-imports) -> checkout of file-born historical versions.
5. LOAD-SCOPE MATURITY: host-precondition strategies, retarget-on-restore (recorded
   frame -> different frame), collision policies (refuse now; skip_existing later),
   cross-profile composition.
6. ENV/ASSET LAYER (open owner decision): if ever built, it grows inside
   asset_management (uv.lock reference capture, admission-time environment gate in the
   mediator) and stops at validation - recovery paths remain user-owned.
7. FIRST-PARTY ADAPTER PACKAGE: shippable EPM callables (SQLite/Postgres reference
   implementations) outside the core, proving the callable contract without absorbing
   SQL ownership.

## What Crystallizer Will Never Be
A second runtime. A package manager. A DB framework. MR's graph semantics. A change
judge. A behavior analyzer (Sentinel's seam). An orchestration engine. If a future lane
needs one of these, it is a different system reading crystallizer's surfaces.

## Summary
Crystallizer keeps its identity - the saving tool and regeneration system - and gains its
final shape: a thin root over a boring ledger, an asset custodian, a mediated loader, and
one shared analyzer, speaking a package-level crystal vocabulary, governed by acyclic
edges and the bite-size law, so that worlds unfold on demand, every version stays
readable forever, and every subsystem stays small enough for the next intelligence that
shows up to hold it whole.
