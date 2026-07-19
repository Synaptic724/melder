# Import & Module Lifecycle — Tested Findings (2026-07-02 session)

## Metadata
- Artifact ID: ART-2026-07-02-import-module-lifecycle-findings
- Parent Epic: EPIC-2026-07-02-agent-object-persistence-loop
- Status: active
- Agent Name: crystal_0
- Created: 2026-07-03T12:33:03Z
- Updated: 2026-07-03T12:33:03Z
- Companion to `2026-07-02_agent_object_persistence_loop_philosophy.md` (the loop +
  frame) and the epic (execution plan). THIS doc is the evidence-backed findings
  layer: every claim below was proven by a probe this session; each carries its
  evidence and its actionable implication. Actions are rolled up into the epic.

## How to read this
Each finding = CLAIM + EVIDENCE (probe/scenario; sandbox CPython 3.10 unless noted —
the external-lib probe was ALSO confirmed on user-run 3.14t / `.venv_new`) + ACTION
(what the build must do). Import semantics match across versions; the runtime target
is 3.14t no-GIL.

## 0. Frame (non-negotiable)
The machine is the `SyntheticModule` registry of live, pre-existing world objects.
The import protocol (a finder at the FRONT of `sys.meta_path` + a `Loader`) is only
the DOORWAY: our loader RETURNS the pre-existing object and delegates execution back
to it. We own our registered names; importlib owns everything else. World-first — do
not reason by analogy to normal Python.
- EVIDENCE: numpy imported inside a synthetic module had `__loader__ = SourceFileLoader`
  (importlib's) while synthetics had `__loader__ = OurLoader`.
- ACTION: keep the finder global + first; never claim names we do not own.

## 1. Dependency edge taxonomy — world-internal (manage) vs world-external (delegate)
Classify every import edge; that classification IS the manage-vs-delegate line.
- WORLD-INTERNAL (we manage: resolve + order + custody + seed/unseed):
  - synthetic -> synthetic
  - synthetic -> owned-physical (user source we custody)
  - physical -> synthetic (the reverse edge)
- WORLD-EXTERNAL (importlib manages loading; we only validate presence):
  - synthetic/physical -> site-package
  - synthetic/physical -> stdlib
- EVIDENCE: classify probe -> {synthetic, stdlib, site_package, missing}; numpy served
  by importlib; synthetics + owned-physical served by our loader.
- ACTION: `crystal_analysis` classifies each edge by AUTHORITY (synthetic_module /
  user_source / site_package / stdlib / missing). Internal edges -> dependency graph +
  load order. External edges -> env-validation manifest only.

## 2. Two dependency tiers — load-time vs deferred
- LOAD-TIME (top-level imports): fire at module exec; set topological load order +
  cycle handling; must be seeded before exec.
- DEFERRED (in-method imports): fire at CALL time; do NOT gate load; gate call-time
  availability + unseed safety. A module loads even if a deferred dep is absent.
- Deferred imports are the LAZY side of the hot-swap boundary: they re-resolve each
  call and see the world AS IT IS AT CALL TIME (they pick up hot-swaps; they can also
  watch a dep get unseeded out from under them).
- EVIDENCE: deferred probe 5/5 — AST split load-time vs deferred; a module with an
  in-method import of an ABSENT synthetic still loaded; the call resolved once the dep
  was seeded; a missing dep failed at CALL time (not load); unseeding broke a later call.
- ACTION: `crystal_analysis` tags each edge with SCOPE (load-time | deferred). Loader
  orders only load-time edges; deferred edges are a call-time-availability contract.

## 3. External libraries — track edges, never manage their code
- Site-packages/stdlib imported by our modules resolve FREE via the standard finders
  BEHIND our finder, and share the same `sys.modules` object (no duplication).
- A MISSING external dep fails at exec, and because we publish-before-exec it leaves a
  HALF-PUBLISHED broken module in `sys.modules`.
- EVIDENCE: external-lib probe 5/5 on user 3.14t (json + pytest shared objects; classify
  correct; missing -> ModuleNotFoundError with half-published=True; unseed left the
  external loaded). Who-owns proof: numpy.__loader__ = SourceFileLoader.
- ACTION: record external edges (name + `site_package` authority + best-effort version)
  for RESTORE-TIME env validation; do NOT capture external code. Loader:
  VALIDATE-BEFORE-ACTIVATE (load-time external deps present via find_spec / uv.lock;
  throw if missing) + ROLLBACK-ON-EXEC-FAILURE (unpublish + unregister a module whose
  exec raised — no half-published modules).

## 4. Owned physical modules run under OUR loader
- A "managed module" is our `ModuleType`; it can be CODEGEN-backed (`__file__ =
  "<synthetic:...>"`) OR PHYSICAL-backed (`__file__` = the real path). Serving owned
  physical source through our loader gives uniform custody, restore-from-memory (files
  become optional projections), and FREE introspection (real `__file__` on disk ->
  `inspect.getsource` works with no linecache workaround). Only SITE-PACKAGES stay
  importlib-owned.
- EVIDENCE: owned-physical probe 6/6 — physical served by OurLoader (authority=physical,
  real __file__); imported a synthetic dep (internal) and a site-package (external,
  importlib); reverse edge (a synthetic imported the owned-physical); getsource worked.
- ACTION: support authority `physical` in the managed-module/crystal path; COMPILE
  physical-backed source with the real filename so introspection/tracebacks work.

## 5. Physical -> synthetic is the HARDEST edge to manage
- Resolution is free (the global finder resolves a physical's import of a synthetic).
- Burden: (a) SEED-BEFORE-IMPORT — the finder must be installed and the synthetic at
  least REGISTERED before the physical's import fires; registered-only resolves lazily.
  We do NOT control when importlib fires a physical import, so synthetic deps physical
  modules reach must be EAGER-SEEDED at world-activation. (b) We CANNOT enumerate
  physical importers from our registry (importlib owns them), and a physical dep may be
  DEFERRED (in a method, on any thread) -> physical->synthetic edges must be recorded
  EXPLICITLY at analysis time (AST-scan physical sources for our synthetic names).
  (c) A synthetic that physical entry points reach must stay RESIDENT while those
  physicals are live.
- EVIDENCE: physical->synthetic probe 4/4 (unseeded fails; seeded-first works;
  registered-only lazy-resolves; unseed strands the physical's captured symbol);
  physical-method->synthetic probe 4/4 (works at call time; reached OUR loader; unseed
  broke the next call; a captured reference SURVIVED unseed).
- ACTION: record physical->synthetic edges explicitly; eager-seed on activate;
  keep-resident while physical dependents are live; reverse-edge-aware unseed.

## 6. `from b import a` — name-level edges + a failure taxonomy
- `from` reaches INTO b: b must be exec'd (registered-only execs on demand) and `a` must
  resolve as an ATTRIBUTE of b OR a SUBMODULE `b.a` (triggers a second import; b must be
  a package). Imports inside ANY exec'd block route through our global finder
  automatically — no per-exec interception.
- Two DISTINCT failures: b absent -> `ModuleNotFoundError` (a SEEDING problem);
  `a` not in b -> `ImportError: cannot import name` (a CONTRACT problem).
- Relative `from . import a` needs `__package__`/`__name__` in the exec namespace; a
  bare codegen dict fails.
- EVIDENCE: from-import probe 5/5 (attr pulled lazily; submodule triggered; missing-name
  ImportError; absent-module ModuleNotFoundError; bare relative failed).
- ACTION: `crystal_analysis` records from-imports as (module edge + imported NAME(s)) —
  name-level edges feed MR's impact engine (name-precise blast radius) and separate
  contract failures (missing name) from seeding failures (missing module). To allow
  relative imports in codegen, exec AS a synthetic module with package context, not a
  bare dict. (Production `_extract_import_targets_from_ast` already returns the
  from-import map — flow it into the crystal.)

## 7. Circular dependencies — we inherit cycle-safety via publish-before-exec
- importlib has no cycle "check"; it publishes the module into `sys.modules` BEFORE
  executing its body, so a circular import finds the PARTIALLY-initialized module and
  binds it (the cycle terminates). `import A` is cycle-robust (bind the module object,
  read names later); `from A import X` is FRAGILE (fails if A is still partial). Deferring
  the back-edge into a method breaks the cycle.
- Our loader does the SAME publish-before-exec, so synthetic and synthetic<->physical
  cycles are safe for free — no cycle detection to build.
- EVIDENCE: circular-dep probe 4/4 (B saw partial A mid-cycle; mutual `__dict__` refs;
  `from A import X` partial-init ImportError; deferred back-edge fixed it).
- ACTION: keep publish-before-exec in materialize + the loader/restore chain; document
  the `import` vs `from`-in-cycle guidance in the codegen guardrails.

## 8. Removal depth + cleanup / memory model
- THREE depths: PUBLISHED -> UNPUBLISHED (drop the `sys.modules` ref; new imports fail
  but captured references still work — a ghost object) -> CLEANED (clear the module
  namespace; even captured references break).
- Cycles leave MUTUAL `__dict__` references, so unpublish alone does NOT free memory; a
  module is kept alive by INCOMING references from its dependents. Cleanup must clear the
  module's OWN namespace (break outgoing refs); full reclaim needs dependents released
  too (another reason reverse edges matter). Under no-GIL 3.14t, clear namespaces for
  DETERMINISTIC teardown rather than leaning on the cyclic GC.
- EVIDENCE: removal-depth scenarios (captured reference survived unpublish; deferred
  import broke on unpublish) + circular-dep mutual-refs.
- ACTION: notch/inactive = UNPUBLISH (reversible; retain the crystal; do not strand
  mid-flight holders); hard teardown = CLEANUP (clear namespace, del owned refs, logger
  last — matches the repo cleanup discipline). ALSO clear the linecache entry on
  unpublish/cleanup (flip side of the introspection fix).

## 9. Introspection (getsource / tracebacks / pdb)
- Codegen-backed synthetics use `__file__ = "<synthetic:...>"`, which trips linecache's
  angle-bracket guard -> `inspect.getsource` fails. FIX B: a normal-looking `__file__` +
  a loader `get_source` (InspectLoader). FIX C: seed `linecache.cache[__file__]`.
  Physical-backed managed modules get introspection FREE (real `__file__`, real file).
- ACTION: implement FIX B (loader `get_source` + non-`<>` `__file__` where possible) for
  codegen-backed modules; FIX C as fallback; clear linecache on unseed.

## 10. Experiment index (runnable evidence)
Persisted under `tests/experimentation/`:
- `synthetic_module_external_library_probe.py` — external libs; 5/5, confirmed on 3.14t.
- `owned_physical_synthetic_relationship_probe.py` — owned physical under our loader; 6/6.
- `import_lifecycle_management_suite.py` — physical->synthetic mgmt, deferred imports,
  from-import-in-exec, physical-method->synthetic, circular-dep, removal-depth (new).
Also pre-existing: `physical_imports_synthetic_limits_probe.py`,
`pytest_synthetic_module_testbench.py`, `importlib_synthetic_circular_dependency_testbench.py`.

## 11. Actionable rollup
Every ACTION above is consolidated into the epic's Findings-Derived Requirements +
milestones (crystal_analysis edge model, loader chain, lifecycle/removal-depth,
physical<->synthetic tracking, introspection). See
`tickets/epics/2026-07-02_agent_object_persistence_loop_epic.md`.

## Addendum 2026-07-03 — Version Store, Removal-as-Feature, Concurrency Surface, importlib-Mirror

### 12. Removal is a NEW feature (importlib never removes)
importlib CACHES modules in `sys.modules` forever; it has no removal. Our unseed/unpublish
is a NOVEL extension importlib does not provide - and it is exactly where every hazard we
mapped lives (stale refs, re-import failure, deferred/cross-boundary breakage). Treat
removal as the one genuinely new, hazardous surface and MINIMIZE it (see 13).
- ACTION: model removal as a deliberate, bounded operation gated to safe boundaries - never
  a careless "importlib with delete bolted on".

### 13. Content-addressed version store + callsign (the removal-minimizer)
Name each module version by an identifier-safe content SHA256 callsign `<canonical>__<hex12>`.
The append-only store keys modules by callsign; versions COEXIST in `sys.modules`, identical
content DEDUPS to one object, and nothing collides - so there is no collision-driven NEED to
remove.
- Canonical imports stay normal: `import svc` / `from svc import a` resolve via the finder
  through a canonical->active-callsign ALIAS; the SHA never appears in code. Version-pin (MR
  checkout) via `import <callsign>` (identifier-safe) or `importlib.import_module(callsign)`.
- EVIDENCE: content-addressed probe (coexist + dedup + repoint-without-removal, 3/3) and
  callsign-invisible probe (import svc / from svc import a / repoint picks up new version /
  pin both ways, 4/4).
- MAPPING onto the existing model (no new concepts - a concrete implementation of them):
  - callsign (content SHA256) = module-version identity = the crystal's module-version SHA
  - append-only callsign store = the version store (materialized crystals)
  - canonical->callsign ALIAS = SpellIndex (one active selected version)
  - repoint the alias = notch (switch active). The ONE remaining removal is invalidating the
    canonical alias entry in `sys.modules` (bounded, safe, at the notch/hot-swap boundary)
  - evict cold callsigns = optional memory GC, ONLY versions with no live references
- CAVEATS: identifier-safe separator is required for a literal `import <callsign>` (`@` breaks
  the statement; use `__`). eager-capture/hot-swap staleness is orthogonal (unchanged).
- ACTION (reshapes M6): removal RELOCATED from correctness-necessity to (a) alias repoint on
  version switch + (b) cold-version eviction for memory. The scary "unseed strands dependents"
  cases largely evaporate for the version store (versions never vanish). Standardize the
  callsign on `<canonical>__<hex>`.

### 14. Concurrency surface - narrowed (already-safe vs what we own)
importlib + module `__dict__` are ALREADY no-GIL-safe on 3.14t; the import-driven path is
covered by importlib's per-module import lock. So the surface WE must make thread-safe is
narrower than "all imports":
- our REGISTRY mutations (register/unregister/store)
- the MANUAL materialize path (the publish-before-exec sequence we replicate)
- the ALIAS repoint (notch) and any EVICTION
- NOT the module `__dict__` or the import-driven path themselves.
- ACTION: guard registry + alias + materialize with the existing RLock discipline; add a
  no-GIL STRESS TEST (concurrent import of one callsign; repoint racing an in-flight import;
  store racing importlib's `_ModuleLock`). Content-addressing helps: append-only + dedup
  means concurrent stores of identical content CONVERGE, not collide.

### 15. Our machinery is importlib PLUGGED-IN, not reimplemented
We are two hooks (finder + loader) INSIDE importlib's machinery, not a parallel import
system. So circular-dep handling, ImportError/ModuleNotFoundError, `sys.modules` semantics,
fromlist, and relative imports are ALL importlib's - identical for synthetic and physical.
- EVIDENCE: importlib published our module to `sys.modules` BEFORE calling our `exec_module`
  (importlib drives publish-before-exec); a synthetic circular import raised the IDENTICAL
  `ImportError: cannot import name 'X'` as a physical one.
- CAVEAT: the MANUAL materialize path replicates importlib's sequence ourselves -> it is a
  mirror we MAINTAIN. Anything through a real `import` / `importlib.import_module` is importlib
  driving (guaranteed identical).
- ACTION: prefer routing through importlib (`import_registered_module`) where possible; add an
  EQUIVALENCE regression test asserting manual-materialize state == import-driven state.

### 16. Hybrid: eager-init module with a method built ONLY to break a cycle
A module can eager-load at init AND carry a method whose import exists solely to break a cycle
(a deferred back-edge). We manage this correctly BECAUSE scope-tagging keeps the deferred
cycle-breaker OUT of the load-order graph (so we do not recreate the cycle) while keeping it
IN the reverse/availability graph (so unseed still knows).
- EVIDENCE: hybrid probe 5/5 (load-order excludes the deferred back-edge; both load; the
  method works; forcing the back-edge load-time reintroduces the partial-init cycle).
- ACTION: confirms R2 (scope tag) + R11 (reverse-edge unseed) are load-bearing, not cosmetic.

### 17. Experiment index (addendum)
- inline, reproducible this session: hybrid + importlib-mirror (5/5), content-addressed
  callsign (3/3), callsign-invisible-to-import-site (4/4). Fold into
  `import_lifecycle_management_suite.py` as G9 (version-store/callsign) + G10 (importlib-mirror)
  when persisting (task T-F8).
